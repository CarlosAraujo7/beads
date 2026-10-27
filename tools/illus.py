"""Ilustração (desenho SEM grade de contas, ex.: adesivo/sticker com fundo branco) -> molde de até N contas, com a paleta ativa (BEADPAL=120).

    import illus
    rows = illus.convert(path, size=50)                    # molde cabendo em 50x50
    parts = illus.split(path, n=10, size=50)               # várias figuras numa imagem: devolve [rows, ...] em ordem de leitura

Método: tira o fundo (claro ligado à borda; a borda branca do adesivo some junto), recorta a figura e, para cada conta, olha a janela
correspondente da imagem grande: se boa parte é contorno escuro a conta é do contorno; senão recebe a letra mais próxima (ΔE2000, 120 cores)
da cor MÉDIA dos pontos claros. Não é cópia exata: é uma redução do desenho, então confira olhando.
"""
import os, sys
import numpy as np
import cv2
from PIL import Image
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import r5, shrink, outline as O


def _load(path, box=None):
    im = Image.open(path).convert('RGBA')
    if box: im = im.crop(box)
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    return np.array(bg.convert('RGB'))


def background(rgb, thr=205):
    """True onde é fundo: claro (mín. dos canais >= thr) e ligado à borda. thr baixo (205) atravessa a linha cinza fina do adesivo
    e leva junto a borda branca dele; o miolo claro do desenho fica, porque o contorno escuro do desenho o isola"""
    H, W, _ = rgb.shape
    light = (rgb.min(axis=2) >= thr).astype(np.uint8)
    n, lab = cv2.connectedComponents(light, connectivity=4)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])).tolist()) - {0}
    return np.isin(lab, list(edge)) & (light > 0)


def peel_sticker(rgb, bg):
    """adesivo com contorno externo PRETO + faixa branca + contorno do desenho (Echidna): depois de tirar o fundo, descasca de fora para dentro
    a primeira camada escura fina e a faixa branca seguinte. Só age se achar exatamente esse padrão (escuro nos primeiros pixels, depois >= 75% de branco)."""
    fg = (~bg).astype(np.uint8)
    dist = cv2.distanceTransform(fg, cv2.DIST_L2, 3)
    H, W = fg.shape; dmax = int(0.07 * max(H, W))
    white = rgb.min(axis=2) >= 225; dark = rgb.max(axis=2) < 90
    frac_w = []; frac_d = []
    for d in range(0, dmax):
        m = (dist > d) & (dist <= d + 1)
        n = m.sum()
        frac_w.append(white[m].mean() if n else 0); frac_d.append(dark[m].mean() if n else 0)
    if not frac_d or max(frac_d[:4]) < 0.5: return bg
    d0 = int(np.argmax(frac_d[:4]))
    run = None
    for d in range(d0 + 1, dmax - 2):
        if all(frac_w[d + k] > 0.75 for k in range(3)):
            e = d + 3
            while e < dmax and frac_w[e] > 0.75: e += 1
            run = (d, e); break
    if run is None: return bg
    return bg | (dist <= run[1] + 1)


def _lab(rgb):
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def _cells(rgb, mask_bg, size, over=8, dark_L=32.0, dark_frac=0.30, cover=0.5):
    """reduz a figura (sem o fundo) para até size x size contas: cada conta olha uma janela over x over da imagem grande.
    - conta vazia se menos de `cover` da janela é figura;
    - 'contorno': se >= dark_frac dos pontos são escuros (L < dark_L) a conta é do contorno (cor = média dos escuros -> letra mais próxima, com preferência pelo preto);
    - senão: cor média dos pontos NÃO escuros -> letra mais próxima (ΔE2000, 120 cores)."""
    ys, xs = np.nonzero(~mask_bg)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    rgb = rgb[y0:y1, x0:x1]; fg = (~mask_bg[y0:y1, x0:x1]).astype(np.float32)
    h, w = fg.shape
    s = min(1.0, size / max(w, h)); nw, nh = max(1, round(w * s)), max(1, round(h * s))
    bw, bh = nw * over, nh * over
    fgb = cv2.resize(fg, (bw, bh), interpolation=cv2.INTER_AREA)
    col = cv2.resize(rgb.astype(np.float32) * fg[..., None], (bw, bh), interpolation=cv2.INTER_AREA) / np.maximum(fgb[..., None], 1e-3)
    L = _lab(col)[..., 0]
    isfg = fgb > 0.5
    dark = isfg & (L < dark_L)
    def blocks(a): return a.reshape(nh, over, nw, over, *a.shape[2:])
    nfg = blocks(isfg.astype(np.float32)).sum(axis=(1, 3)); ndk = blocks(dark.astype(np.float32)).sum(axis=(1, 3))
    cb = blocks(col); fb = blocks((isfg & ~dark).astype(np.float32)); db = blocks(dark.astype(np.float32))
    mean_lit = (cb * fb[..., None]).sum(axis=(1, 3)) / np.maximum(fb.sum(axis=(1, 3))[..., None], 1)
    mean_dk = (cb * db[..., None]).sum(axis=(1, 3)) / np.maximum(db.sum(axis=(1, 3))[..., None], 1)
    rows = []
    for y in range(nh):
        r = ''
        for x in range(nw):
            if nfg[y, x] < cover * over * over: r += '.'; continue
            if ndk[y, x] >= dark_frac * nfg[y, x] or nfg[y, x] - ndk[y, x] < 1: r += r5.near120(tuple(float(v) for v in mean_dk[y, x]), dark=True)
            else: r += r5.near120(tuple(float(v) for v in mean_lit[y, x]))
        rows.append(r)
    return O.trim(rows)


def sticker_bg(rgb, thr=205, white_outside=None):
    """white_outside=(rx, ry): além do fundo, todo branco (>= 240) FORA da elipse central (raios rx, ry = fração da largura/altura) também é fundo
    — para adesivos cujo desenho tem furos brancos fechados (a fumaça do Subaru) que a inundação a partir da borda não alcança"""
    m = peel_sticker(rgb, background(rgb, thr))
    if white_outside:
        H, W = m.shape; yy, xx = np.mgrid[0:H, 0:W]
        out = ((xx - W / 2) / (white_outside[0] * W)) ** 2 + ((yy - H / 2) / (white_outside[1] * H)) ** 2 > 1
        m = m | ((rgb.min(axis=2) >= 240) & out)
    return m


def convert(path, size=50, box=None, thr=205, white_outside=None, **kw):
    rgb = _load(path, box)
    return _cells(rgb, sticker_bg(rgb, thr, white_outside), size, **kw)


def split(path, n, size=50, thr=205, join=14, min_area=0.004):
    """separa as figuras de uma imagem (adesivos soltos): junta pedaços a até `join` px, ordena em leitura (linhas de cima p/ baixo)"""
    rgb = _load(path)
    mask = background(rgb, thr); fg = (~mask).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * join + 1, 2 * join + 1))
    comp = cv2.dilate(fg, k)
    cnt, lab = cv2.connectedComponents(comp, connectivity=8)
    boxes = []
    for i in range(1, cnt):
        m = (lab == i) & (fg > 0)
        if m.sum() < min_area * fg.size: continue
        ys, xs = np.nonzero(m); boxes.append((ys.min(), ys.max() + 1, xs.min(), xs.max() + 1))
    if len(boxes) != n: raise SystemExit(f'esperava {n} figuras e achei {len(boxes)}: ajuste join/min_area')
    # ordem de leitura: agrupa por linha (centro vertical próximo) e ordena por x
    boxes.sort(key=lambda b: (b[0] + b[1]) / 2)
    rows_, cur = [], [boxes[0]]
    for b in boxes[1:]:
        if abs((b[0] + b[1]) / 2 - np.mean([(c[0] + c[1]) / 2 for c in cur])) < 0.5 * max(b[1] - b[0], cur[0][1] - cur[0][0]): cur.append(b)
        else: rows_.append(cur); cur = [b]
    rows_.append(cur)
    ordered = [b for r in rows_ for b in sorted(r, key=lambda b: b[2])]
    out = []
    for (y0, y1, x0, x1) in ordered:
        pad = 2
        sub = rgb[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad]
        out.append(_cells(sub, sticker_bg(sub, thr), size))
    return out
