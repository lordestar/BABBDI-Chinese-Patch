# -*- coding: utf-8 -*-
"""列出语料中"看起来像玩家可见文本"但未纳入词典的短字符串，用于查漏。"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translations import TRANSLATIONS, EXTRA

CORPUS_FILES = [
    r'D:\deepseek project\babbdi_strings\level0_region_utf8.txt',
    r'D:\deepseek project\babbdi_strings\level1_region_utf8.txt',
    r'D:\deepseek project\babbdi_strings\dialog_region_utf8.txt',
    r'D:\deepseek project\babbdi_strings\ALL_natural.txt',
]

def norm(s):
    return ' '.join(s.split()).upper()

table = set(norm(en) for en, _ in TRANSLATIONS)
table |= set(norm(en) for en, _ in EXTRA)

# 明显的非玩家文本/资源名
NOISE = re.compile(
    r'^(Combined Mesh|Light Probe|Audio Reverb|Chain Simple|Point Light|Particle System|'
    r'Spot Light|Reflection Probe|Directional Light|Main Camera|SM_|PostProcess|Vignette|'
    r'AmbientOcclusion|LensDistortion|Grain|Bloom|Bokeh|Camera |CoC |Downsample|Debug Overlay|'
    r'New Lighting|TMP |Font |Outline |Face |Bevel |Bump |Gradient |Mask |Vertex |Scale Ratio|'
    r'Texture |Height |Normal |Rim |Water |Foam |Detail |Specular |Smoothness|Tint |Main Color|'
    r'Alpha Cutoff|Soft Particles|Max Tessellation|UV Set|Toon Ramp|Base Layer|New State|'
    r'Library/|Resources/|Hidden/|Nature/|Mobile/|Legacy |Standard |Skybox|Autodesk|Particles/|UI/|'
    r'Copyright|Licensed|Digitized|Based on|Ascender|Liberation|Monofonto|Arial|Arimo|'
    r'FuturaHandwritten|MajorMono|Major Mono|monofonto|Card |Joystick|joystick|Mouse |mouse|'
    r'left shift|Ignore Raycast|Not Walkable|Sprite |Stencil |Cull Mode|Clip Rect|Color Mask|'
    r'Use Alpha|linebreaking|style sheets|sprite assets|fonts & materials|Weight |Default Style|'
    r'Arrow|SoundSource|SoundSource|Loader|Toggle|Scrollbar|Viewport|Handle|Fill|Item |Template|'
    r'Content|Canvas|EventSystem|Panel|Text \(TMP\)|MusicShotSource|IntroAudio|Progress|Background|'
    r'Foreground|Label|Tip|Checkmark|Slider|Volume|MasterVolume|AmbientSoundSlider|'
    r'Smiling face|Grinning face|Face with tears|Deep Color|Shalow Color|Glossy|Tiling|tiling|'
    r'QY |OBW |lV Vp|uKu |pBnCn|Db qH|HQ EQ|T 16\.0|babbdi scale|rhino scale|new york scale|'
    r'undergound scale|new scale|old gen car|snowy mountains|state man|sce$|xza|NVx|zMb|ooo$|qqq$|'
    r'OnClick|OnPointer|OnPress|SetActive|SetBool|SetQuality|ChangeButton|ChangeScene|ValueChange|'
    r'Normal$|Highlighted$|Pressed$|Selected$|Disabled$|Horizontal$|Vertical$|Submit$|Cancel$)',
    re.IGNORECASE)

seen = set()
out = []
for f in CORPUS_FILES:
    if not os.path.exists(f):
        continue
    for line in open(f, encoding='utf-8'):
        s = line.rstrip('\n')
        if not s or len(s) > 26:
            continue
        if norm(s) in table or norm(s) in seen:
            continue
        if NOISE.match(s):
            continue
        # 只保留"看起来像 UI 文本"的：字母开头，允许空格/数字/标点
        if not re.match(r"^[A-Za-z][A-Za-z0-9 ,\.!'\"\?\-\(\)&:;/\[\]]*$", s):
            continue
        # 排除明显是标识符/无空格的驼峰名
        if ' ' not in s and not s.isupper() and s not in ('back', 'bye', 'world', 'quit', 'play', 'save', 'map', 'ok'):
            continue
        seen.add(norm(s))
        out.append(s)

print('=== 未纳入词典的短字符串候选（人工复核）===')
for s in sorted(out):
    print(f'  {s!r}')
print(f'共 {len(out)} 条')
