import re, sys, os, json

# UTF-8 aware printable-run extractor: allows ASCII printable plus valid UTF-8 multibyte
RUN = re.compile(rb'(?:[\x20-\x7e]|[\xc2-\xdf][\x80-\xbf]|[\xe0-\xef][\x80-\xbf]{2}|[\xf0-\xf4][\x80-\xbf]{3})+')

def runs_utf8(path, minchars=2):
    with open(path, 'rb') as f:
        data = f.read()
    out = []
    for m in RUN.finditer(data):
        b = m.group()
        try:
            s = b.decode('utf-8')
        except Exception:
            continue
        if len(s) < minchars:
            continue
        if not any(c.isalpha() for c in s):
            continue
        out.append((m.start(), s))
    return out, len(data)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'region':
        path, outpath = sys.argv[2], sys.argv[3]
        anchors = sys.argv[4:]
        rs, size = runs_utf8(path)
        offs = [off for off, s in rs if any(a in s for a in anchors)]
        if not offs:
            print('no anchors'); sys.exit(1)
        lo, hi = max(0, min(offs) - 80000), min(size, max(offs) + 80000)
        sel = [s for off, s in rs if lo <= off <= hi]
        seen, res = set(), []
        for s in sel:
            if s in seen: continue
            seen.add(s); res.append(s)
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(res))
        print(f'{os.path.basename(path)}: anchors={len(offs)} region=[{lo},{hi}] strings={len(res)} -> {outpath}')
