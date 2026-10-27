"""Converte uma imagem (pixel art/padrão pronto ou desenho) em template do Bead Studio.

uso: python img2tpl.py <imagem> "<Nome>" "<Grupo>" [--px N] [--size W H] [--no-bg] [--maxcolors N] [--dry]
  --px N        tamanho de cada quadradinho na imagem (se omitido, detecta sozinho)
  --size W H    força modo "foto": reduz a imagem para W x H contas (sem detectar grade)
  --no-bg       não remove o fundo ligado às bordas
  --maxcolors N usa só as N cores mais frequentes
  --dry         só mostra o resultado, não grava em templates.js
"""
import sys, os, re, json, math
import numpy as np
from PIL import Image

TPL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates.js')
# a paleta vem de data/palette.json (palette.py): BEADPAL=24 (padrão, 24 cores do kit antigo) ou BEADPAL=120
from palette import PAL, LETTER
RGB = np.array([[int(h[i:i+2], 16) for i in (1, 3, 5)] for _, h in PAL], float)

def rgb2lab(a):
    a = a / 255.0
    a = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = a @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
LAB = rgb2lab(RGB)

def detect_grid(rgba, forced=None):
    h, w, _ = rgba.shape
    a = rgba.astype(float)
    ex = np.abs(np.diff(a, axis=1)).sum(2).sum(0)   # bordas entre colunas x-1|x -> índice x-1
    ey = np.abs(np.diff(a, axis=0)).sum(2).sum(1)
    ex = np.concatenate([[0], ex]); ey = np.concatenate([[0], ey])
    def prep(e): return e - e.mean()
    ax, ay = prep(ex), prep(ey)
    nmax = min(90, min(len(ax), len(ay)) // 3)
    r = np.zeros(nmax + 2); v0 = 0
    for x in (ax, ay):
        v0 += (x * x).mean()
        for k in range(1, nmax + 2): r[k] += (x[:-k] * x[k:]).mean()
    p = forced; q = 1.0
    if not p:
        mx = r[2:nmax + 1].max()
        for k in range(2, nmax + 1):
            if r[k] >= 0.6 * mx and r[k] >= r[k - 1] and r[k] >= r[k + 1]: p = k; q = mx / v0; break
    if not p: return None
    def off(e):
        best, bo = -1, 0
        for o in range(p):
            s = e[o::p].mean()
            if s > best: best, bo = s, o
        return bo
    ox, oy = off(ex), off(ey)
    return dict(p=p, ox=ox, oy=oy, q=q, W=(w - ox) // p, H=(h - oy) // p)

def sample_blocks(rgba, g):
    p, ox, oy, W, H = g['p'], g['ox'], g['oy'], g['W'], g['H']
    lo, hi = int(p * .3), max(int(p * .3) + 1, int(math.ceil(p * .7)))
    out = np.zeros((H, W, 4))
    for by in range(H):
        for bx in range(W):
            blk = rgba[oy + by * p + lo: oy + by * p + hi, ox + bx * p + lo: ox + bx * p + hi].reshape(-1, 4)
            out[by, bx] = np.median(blk, axis=0)
    return out

def remove_bg(px, tol=40):
    H, W, _ = px.shape
    empty = px[..., 3] < 128
    corners = [px[0, 0], px[0, W - 1], px[H - 1, 0], px[H - 1, W - 1]]
    corners = [c for c in corners if c[3] >= 128]
    if len(corners) >= 2:
        bg = np.mean([c[:3] for c in corners], axis=0)
        near = (np.linalg.norm(px[..., :3] - bg, axis=2) <= tol) & ~empty
        stack = [(y, x) for y in range(H) for x in range(W) if (y in (0, H - 1) or x in (0, W - 1)) and near[y, x]]
        seen = set(stack)
        while stack:
            y, x = stack.pop(); empty[y, x] = True
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and near[yy, xx] and (yy, xx) not in seen:
                    seen.add((yy, xx)); stack.append((yy, xx))
    return empty

def quantize(px, empty, maxcolors=24):
    lab = rgb2lab(px[..., :3])
    d = ((lab[:, :, None, :] - LAB[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1); idx[empty] = -1
    if maxcolors < 24:
        cnt = np.bincount(idx[idx >= 0], minlength=24)
        keep = np.argsort(-cnt)[:maxcolors]
        mask = np.full(24, np.inf); mask[keep] = 0
        idx = (d + mask[None, None]).argmin(-1); idx[empty] = -1
    return idx

def to_rows(idx):
    ys, xs = np.where(idx >= 0)
    idx = idx[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return [''.join('.' if v < 0 else LETTER[PAL[v][0]] for v in row) for row in idx]

def convert(path, px=None, size=None, bg=True, maxcolors=24):
    im = Image.open(path).convert('RGBA')
    info = ''
    if size:
        im2 = im.resize(tuple(size), Image.BOX)
        arr = np.array(im2).astype(float); info = f'modo foto {size[0]}x{size[1]}'
    else:
        rgba = np.array(im).astype(np.uint8)
        g = detect_grid(rgba, px)
        if not g or g['W'] < 4 or g['H'] < 4: raise SystemExit('não detectei a grade; use --px N ou --size W H')
        arr = sample_blocks(rgba, g); info = f"grade {g['p']} px (q={g['q']:.2f}) -> {g['W']}x{g['H']}"
    empty = remove_bg(arr) if bg else arr[..., 3] < 128
    idx = quantize(arr, empty, maxcolors)
    return to_rows(idx), info

def add_to_templates(name, group, rows):
    src = open(TPL, encoding='utf-8').read()
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower().encode('ascii', 'ignore').decode() or 'item').strip('-') or 'item'
    ids = set(re.findall(r'\{id:"([^"]+)"', src))
    base, n = slug, 2
    while slug in ids: slug = f'{base}-{n}'; n += 1
    entry = '{id:%s,group:%s,name:%s,rows:[\n%s\n]},\n' % (json.dumps(slug), json.dumps(group, ensure_ascii=False), json.dumps(name, ensure_ascii=False), ',\n'.join(json.dumps(r) for r in rows))
    src = src.replace('window.TEMPLATES = [\n', 'window.TEMPLATES = [\n' + entry, 1)
    open(TPL, 'w', encoding='utf-8').write(src)
    return slug

if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 3: raise SystemExit(__doc__)
    path, name, group = a[0], a[1], a[2]
    opt = a[3:]
    px = int(opt[opt.index('--px') + 1]) if '--px' in opt else None
    size = (int(opt[opt.index('--size') + 1]), int(opt[opt.index('--size') + 2])) if '--size' in opt else None
    mc = int(opt[opt.index('--maxcolors') + 1]) if '--maxcolors' in opt else 24
    rows, info = convert(path, px, size, '--no-bg' not in opt, mc)
    print(info, '|', len(rows[0]), 'x', len(rows), '|', sum(ch != '.' for r in rows for ch in r), 'contas')
    for r in rows: print(r)
    if '--dry' not in opt:
        print('gravado como', add_to_templates(name, group, rows))
