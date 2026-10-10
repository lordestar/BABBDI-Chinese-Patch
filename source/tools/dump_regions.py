import re, sys, os

def runs(path, minlen=2):
    with open(path, 'rb') as f:
        data = f.read()
    out = []
    for m in re.finditer(rb'[\x20-\x7e]{%d,}' % minlen, data):
        out.append((m.start(), m.group().decode('ascii')))
    return out, len(data)

def dump_region(path, anchors, pad=60000, out=None):
    rs, size = runs(path)
    hits = []
    for a in anchors:
        for off, s in rs:
            if s == a or a in s:
                hits.append(off)
    if not hits:
        print(f'  !! no anchor found in {os.path.basename(path)}')
        return []
    lo, hi = max(0, min(hits) - pad), min(size, max(hits) + pad)
    sel = [s for off, s in rs if lo <= off <= hi]
    # dedupe preserving order
    seen = set(); res = []
    for s in sel:
        if s in seen: continue
        seen.add(s); res.append(s)
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            f.write('\n'.join(res))
    print(f'  {os.path.basename(path)}: anchors={len(hits)} region=[{lo},{hi}] strings={len(res)}')
    return res

if __name__ == '__main__':
    game = r'D:\Steam\Steam\steamapps\common\BABBDI\Babbdi_Data'
    outdir = r'D:\deepseek project\babbdi_strings'

    print('=== sharedassets1.assets (dialogue) ===')
    dump_region(os.path.join(game, 'sharedassets1.assets'),
                ["I'm so bored", 'No more tickets.', 'by train', 'you want to leave ?'],
                pad=80000, out=os.path.join(outdir, 'dialog_region.txt'))

    print('=== level1 (quests / library UI) ===')
    dump_region(os.path.join(game, 'level1'),
                ['WAY OF THE CLIMBER', 'SPEEDRUN MODE', 'press [tab] to open library'],
                pad=40000, out=os.path.join(outdir, 'level1_region.txt'))

    print('=== level0 (main menu) ===')
    dump_region(os.path.join(game, 'level0'),
                ['MASTER VOLUME', 'version 1.2.4'],
                pad=40000, out=os.path.join(outdir, 'level0_region.txt'))
