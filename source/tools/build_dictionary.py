# -*- coding: utf-8 -*-
"""
从游戏数据文件中精确匹配英文原文，生成 XUnity.AutoTranslator 词典与字体字符集。

用法：
    python build_dictionary.py

输出：
    1. build/BABBDI_zh-CN.txt   -> 放到 <游戏目录>/BepInEx/Translation/zh-CN/Text/
    2. build/charset.txt        -> 放到插件的 charset.txt（用于预热字形）
    3. 控制台报告未匹配的词典条目（拼写错误）与可疑的未翻译游戏文本
"""
import os
import re
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations import TRANSLATIONS, EXTRA, REGEX_ENTRIES, EXCLUDE_EXACT

GAME_DATA = r'D:\Steam\Steam\steamapps\common\BABBDI\Babbdi_Data'
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build')

# 与游戏数据文件中的字符串提取保持一致（UTF-8 感知）
RUN = re.compile(
    rb'(?:[\x20-\x7e]|[\xc2-\xdf][\x80-\xbf]|[\xe0-\xef][\x80-\xbf]{2}|[\xf0-\xf4][\x80-\xbf]{3})+'
)

FILES = [
    'level0',
    'level1',
    'sharedassets0.assets',
    'sharedassets1.assets',
    'resources.assets',
    'globalgamemanagers',
]

# 明显不是面向玩家的文本：Unity 资源名、着色器、字体版权等
NOISE = re.compile(
    r'^(Library/|Resources/|Hidden/|Nature/|Mobile/|Legacy Shaders|Combined Mesh|'
    r'Light Probe|Audio Reverb|Chain Simple|Point Light|Particle System|Spot Light|'
    r'Reflection Probe|Directional Light|Main Camera|Text \(TMP\)|Panel|Toggle|'
    r'Scrollbar|Viewport|Handle|Fill|Item|Template|Content|Canvas|EventSystem|'
    r'ArrowInitPosition|SoundSource|PostProcessResources|ColorGrading|Vignette|'
    r'AmbientOcclusion|LensDistortion|Grain|Bloom|Bokeh Filter|CoC |Camera Far Fade|'
    r'Camera Near Fade|Downsample|Debug Overlay|New Lighting|TMP Settings|'
    r'style sheets|linebreaking|sprite assets|fonts & materials|Font |Outline |Face |'
    r'Bevel |Bump |Gradient |Mask |Vertex |Scale Ratio|Texture |Height |Normal |'
    r'Rim |Water |Foam |Detail |Specular |Smoothness|Tint |Main Color|Alpha Cutoff|'
    r'Soft Particles|Max Tessellation|UV Set|Toon Ramp|Base Layer|New State|'
    r'Copyright|Licensed|Digitized|Based on Arimo|Ascender|Liberation|Monofonto|'
    r'Arial|Arimo|FuturaHandwritten|MajorMonoDisplay|Major Mono|monofonto|'
    r'Not Walkable|Ignore Raycast|Autodesk|Skybox|Standard \(|Particles/|UI/)',
    re.IGNORECASE
)

# 已确认不是面向玩家的短标识符（UnityEvent 方法名、UI 动画状态名、对象名等）
KNOWN_NON_TEXT = {
    'normal', 'highlighted', 'pressed', 'selected', 'disabled', 'onclickdown',
    'valuechange', 'onclick', 'onpointerenter', 'onpress', 'setactive', 'setbool',
    'setqualityleveldropdown', 'changescene', 'changebutton', 'save', 'load',
    'parameters', 'informations', 'version', 'tip', 'background', 'foreground',
    'loader', 'loadertext', 'progress', 'template', 'item', 'content', 'fill',
    'handle', 'viewport', 'arrow', 'music', 'mastervolume', 'volumeambient',
    'volumesfx', 'volumemusic', 'savingoptions', 'qualitysettings', 'musicsource',
    'soundeffectsource', 'ambientsource', 'outdoorwindsound', 'indoorwindsound',
    'steamintegration', 'levelmanager', 'gamemanager', 'mainmenu', 'options',
    'optionsmenu', 'playgame', 'quitgame', 'backbutton', 'crosshair', 'mapbutton',
    'new text', 'option a', 'volume(text)', 'acknowledgments',
}


def norm(s):
    return ' '.join(s.split()).upper()


def extract_strings(path):
    with open(path, 'rb') as f:
        data = f.read()
    out = []
    seen = set()
    for m in RUN.finditer(data):
        try:
            s = m.group().decode('utf-8')
        except Exception:
            continue
        if len(s) < 2 or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    table = {}
    dupes = []
    for en, zh in TRANSLATIONS:
        k = norm(en)
        if k in table and table[k] != zh:
            dupes.append((k, table[k], zh))
        table[k] = zh

    # 检查"部分翻译"前缀冲突：某条键是另一条键的前缀时，短文本可能被误伤
    collisions = []
    keys = sorted(table.keys())
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if b.startswith(a) and a != b and len(a) >= 4:
                collisions.append((a, b))

    if collisions:
        print('!! 注意：以下键存在前缀冲突（XUnity 的"部分翻译"可能误伤短文本）：')
        for a, b in collisions:
            print(f'   短 "{a}"  <-  长 "{b}"')
        print('   （若该短文本确实会单独显示，请改用 REGEX_ENTRIES）')
        print()

    excluded = set(norm(e) for e in EXCLUDE_EXACT)
    for k in excluded:
        table.pop(k, None)

    if dupes:
        print('!! 词典中存在规范化后重复的键（后者覆盖前者）：')
        for k, a, b in dupes:
            print(f'   {k}: {a} / {b}')

    # 收集游戏中的全部字符串
    corpus = []
    for name in FILES:
        p = os.path.join(GAME_DATA, name)
        if not os.path.exists(p):
            print(f'   (跳过不存在的文件 {name})')
            continue
        ss = extract_strings(p)
        corpus.extend(ss)
        print(f'   {name}: {len(ss)} 条字符串')

    corpus = list(dict.fromkeys(corpus))
    print(f'\n游戏字符串总数（去重）：{len(corpus)}')

    # 精确匹配
    entries = []
    hits = {}
    for s in corpus:
        k = norm(s)
        if k in table:
            entries.append((s, table[k]))
            hits.setdefault(k, 0)
            hits[k] += 1

    for en, zh in EXTRA:
        entries.append((en, zh))

    # 完全没匹配上的词典条目 = 拼写错误或该文本不在本版本游戏中
    unmatched = [en for en, _ in TRANSLATIONS if norm(en) not in hits]

    # 去重（同一原文只保留一条）
    dedup = {}
    for s, zh in entries:
        if s not in dedup:
            dedup[s] = zh
    entries = list(dedup.items())

    out_path = os.path.join(OUT_DIR, 'BABBDI_zh-CN.txt')
    with io.open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# BABBDI 简体中文汉化词典（人工翻译）\n')
        f.write('# 格式：英文原文=简体中文译文\n')
        f.write('# 放置位置：<游戏目录>/BepInEx/Translation/zh-CN/Text/\n\n')
        for s, zh in sorted(entries, key=lambda x: x[0]):
            f.write(f'{s}={zh}\n')
        if REGEX_ENTRIES:
            f.write('\n# --- 正则条目（仅在精确匹配失败后生效）---\n')
            for pattern, zh in REGEX_ENTRIES:
                f.write(f'r:"{pattern}"={zh}\n')

    # 字符集（供字体插件预热字形）
    # 注意：必须包含全部非 ASCII 字符，不只是汉字——否则全角标点（：，。“”）和省略号
    # 会因为没被预热而拿不到字形，显示成方框。
    chars = set()
    for _, zh in entries:
        for c in zh:
            if ord(c) > 127 and not c.isspace():
                chars.add(c)
    for _, zh in REGEX_ENTRIES:
        for c in zh:
            if ord(c) > 127 and not c.isspace():
                chars.add(c)
    charset_path = os.path.join(OUT_DIR, 'charset.txt')
    with io.open(charset_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(''.join(sorted(chars)))

    print(f'\n生成词典条目：{len(entries)} 条 -> {out_path}')
    print(f'生成字符集：{len(chars)} 个汉字 -> {charset_path}')

    if unmatched:
        print(f'\n!! 以下 {len(unmatched)} 个词典条目在游戏文件中没有找到对应原文（请检查拼写）：')
        for en in unmatched:
            print(f'   {en}')

    # 提示可能遗漏的、看起来像玩家可见文本的字符串
    print('\n--- 疑似玩家可见但未纳入词典的字符串（人工复核用）---')
    suspicious = []
    for s in corpus:
        if norm(s) in table:
            continue
        if len(s) < 4 or ' ' not in s:
            continue
        if NOISE.match(s) or norm(s) in KNOWN_NON_TEXT:
            continue
        words = [w for w in re.split(r'\s+', s) if re.match(r'^[A-Za-z]{2,}$', w)]
        if len(words) >= 2 and re.match(r'^[A-Za-z0-9 ,\.!\'"?\-\(\)&:;/\[\]%\+¿¡ÉÑÓÁÍÚ]+$', s):
            suspicious.append(s)
    for s in sorted(set(suspicious)):
        print(f'   {s}')
    print(f'（共 {len(set(suspicious))} 条）')


if __name__ == '__main__':
    main()
