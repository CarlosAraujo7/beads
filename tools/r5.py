import sys, os, glob, json
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import numpy as np
from PIL import Image
import cellread as C, outline as O, polish as PL, grid2 as G2, img2tpl as T
REM = os.path.join(os.path.dirname(SP), 'remessa 5')

def pat(idx, tol=26, px=None, mp=None, drop='', crop=None, mode='recolor', keep=(), clear=(), despeckle=True, crop_img=None, post=None, colors=False):
    """padrao com grade (remessa 5): le as celulas, tira o fundo, ajusta o contorno e apara"""
    f = sorted(glob.glob(os.path.join(REM, '*.*')))[idx]
    im = Image.open(f).convert('RGBA')
    if crop_img: im = im.crop(crop_img)
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); rgba = np.array(bg).astype(np.uint8)
    g = G2.detect(rgba, px)
    arr = G2.sample(rgba, g, mode=False)[..., :3]
    if crop: arr = arr[crop[0]:crop[1], crop[2]:crop[3]]
    rows = C.letters_bg(arr, tol=tol)
    rows = [''.join('.' if c in drop else (mp or {}).get(c, c) for c in r) for r in rows]
    for (y0, y1, x0, x1) in clear:
        rows = [''.join('.' if (y0 <= y <= y1 and x0 <= x <= x1) else c for x, c in enumerate(r)) for y, r in enumerate(rows)]
    if despeckle: rows = O.drop_specks(O.trim(rows), maxsize=2)
    if colors: rows = O.despeckle_colors(rows)
    if post: rows = post(rows)
    if mode == 'recolor': rows = O.recolor_outline(rows)
    elif mode == 'clean': rows = O.clean_k(rows, keep=list(keep))
    return O.trim(rows)


def sprite(idx, mp=None, mode='recolor'):
    """sprite pequeno (1 pixel = 1 conta), fundo transparente"""
    f = sorted(glob.glob(os.path.join(REM, '*.*')))[idx]
    im = Image.open(f).convert('RGBA'); a = np.array(im)
    rows = []
    for y in range(a.shape[0]):
        rows.append(''.join('.' if a[y, x, 3] < 128 else (mp or {}).get(C.nearest(a[y, x, :3]), C.nearest(a[y, x, :3])) for x in range(a.shape[1])))
    rows = O.trim(rows)
    return O.recolor_outline(rows) if mode == 'recolor' else rows

def pat_flood(idx, thr=215, px=None, mp=None, drop='', clear=(), crop=None, mode='recolor', keep=(), crop_img=None, despeckle=True, colors=False, post=None):
    """igual a pat(), mas o fundo e 'claro ligado a borda' (fundos com ruido)"""
    f = sorted(glob.glob(os.path.join(REM, '*.*')))[idx]
    im = Image.open(f).convert('RGBA')
    if crop_img: im = im.crop(crop_img)
    bgc = Image.new('RGBA', im.size, (255, 255, 255, 255)); bgc.alpha_composite(im); rgba = np.array(bgc).astype(np.uint8)
    g = G2.detect(rgba, px)
    arr = G2.sample(rgba, g, mode=False)[..., :3]
    if crop: arr = arr[crop[0]:crop[1], crop[2]:crop[3]]
    rows = C.letters_flood(arr, thr=thr)
    rows = [''.join('.' if c in drop else (mp or {}).get(c, c) for c in r) for r in rows]
    for (y0, y1, x0, x1) in clear:
        rows = [''.join('.' if (y0 <= y <= y1 and x0 <= x <= x1) else c for x, c in enumerate(r)) for y, r in enumerate(rows)]
    if despeckle: rows = O.drop_specks(O.trim(rows), maxsize=2)
    if colors: rows = O.despeckle_colors(rows)
    if post: rows = post(rows)
    if mode == 'recolor': rows = O.recolor_outline(rows)
    elif mode == 'clean': rows = O.clean_k(rows, keep=list(keep))
    return O.trim(rows)


def largest(rows):
    """fica so a maior peca (4 vizinhos): tira legendas, marcas d'agua e enfeites soltos"""
    comps = O.components(rows)
    keep = set(comps[0]); h, w = len(rows), len(rows[0])
    return O.trim([''.join(rows[y][x] if (y, x) in keep else '.' for x in range(w)) for y in range(h)])


# ---------- fotos de pecas prontas (fundo branco): grade de contas + cor pela lab ----------
import fitgrid as F, cv2
_PAL = [(T.LETTER[c], np.array(T.rgb2lab(np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)))) for c, h in T.PAL]
def lab_letter(rgb, allowed=None, kL=1.0):
    l = np.array(T.rgb2lab(np.array(rgb, float)))
    best = None
    for k, pl in _PAL:
        if allowed and k not in allowed: continue
        d = (kL * (l[0] - pl[0])) ** 2 + (l[1] - pl[1]) ** 2 + (l[2] - pl[2]) ** 2
        if best is None or d < best[0]: best = (d, k)
    return best[1]

def photo(idx, p0, spread=0.25, mp=None, allowed=None, kL=1.0, bgmin=250, bgfn=None, ring=(0.2, 0.42), bbox=None, angles=np.arange(-3, 3.1, 0.5), post=None, minsize=4, tmp='r5_tmp.png', thr_dark=None):
    f = sorted(glob.glob(os.path.join(REM, '*.*')))[idx]
    im = Image.open(f).convert('RGBA'); bgc = Image.new('RGBA', im.size, (255, 255, 255, 255)); bgc.alpha_composite(im)
    path = os.path.join(OUT, tmp); bgc.convert('RGB').save(path)
    a = np.array(bgc.convert('RGB')).astype(int)
    if bbox is None:
        m = (a.min(axis=2) < 244); ys, xs = np.where(m)
        bbox = (max(0, xs.min() - 6), max(0, ys.min() - 6), min(a.shape[1], xs.max() + 6), min(a.shape[0], ys.max() + 6))
    rot, cx, cy, p, ang, arr = F.fit(path, bbox, p0, spread=spread, angles=angles, step=1.0, ring=ring)
    H, W, _ = arr.shape
    white = np.array([[(bgfn(arr[y, x]) if bgfn else arr[y, x].min() >= bgmin) for x in range(W)] for y in range(H)])
    out = np.zeros((H, W), bool); st = [(y, x) for y in range(H) for x in range(W) if (y in (0, H - 1) or x in (0, W - 1)) and white[y, x]]
    for q in st: out[q] = True
    while st:
        y, x = st.pop()
        for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (y + da, x + db)
            if 0 <= q[0] < H and 0 <= q[1] < W and white[q] and not out[q]: out[q] = True; st.append(q)
    rows = [''.join('.' if out[y, x] else lab_letter(arr[y, x], allowed, kL) for x in range(W)) for y in range(H)]
    if mp: rows = [''.join(mp.get(c, c) for c in r) for r in rows]
    rows = O.trim(rows)
    rows = O.drop_specks(rows, maxsize=minsize)
    if post: rows = post(rows)
    info = dict(p=p, ang=ang, shape=(W, H), bbox=bbox)
    return O.trim(rows), info


# ---------- versao "exata": as cores e o contorno do padrao ficam como estao ----------
_lab_cache = {}
def lab_letter_c(rgb):
    k = tuple(int(round(v / 3.0)) for v in rgb)
    if k not in _lab_cache: _lab_cache[k] = lab_letter(rgb)
    return _lab_cache[k]

def exact(idx, tol=26, thr=None, px=None, crop=None, crop_img=None, clear=(), drop='', post=None, lab=True):
    """padrao com grade, igual ao enviado: so tira o fundo (cor do canto, ou 'claro' ligado a borda) e o que nao e desenho"""
    f = sorted(glob.glob(os.path.join(REM, '*.*')))[idx]
    im = Image.open(f).convert('RGBA')
    if crop_img: im = im.crop(crop_img)
    bgc = Image.new('RGBA', im.size, (255, 255, 255, 255)); bgc.alpha_composite(im); rgba = np.array(bgc).astype(np.uint8)
    g = G2.detect(rgba, px)
    arr = G2.sample(rgba, g, mode=False)[..., :3].astype(float)
    if crop: arr = arr[crop[0]:crop[1], crop[2]:crop[3]]
    H, W, _ = arr.shape
    if thr is None:
        ref = np.median(np.array([arr[0, 0], arr[0, W - 1], arr[H - 1, 0], arr[H - 1, W - 1]]), axis=0)
        same = np.array([[np.linalg.norm(arr[y, x] - ref) < tol for x in range(W)] for y in range(H)])
    else:
        same = np.array([[arr[y, x].min() > thr for x in range(W)] for y in range(H)])
    out = np.zeros((H, W), bool); st = [(y, x) for y in range(H) for x in range(W) if (y in (0, H - 1) or x in (0, W - 1)) and same[y, x]]
    for q in st: out[q] = True
    while st:
        y, x = st.pop()
        for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (y + da, x + db)
            if 0 <= q[0] < H and 0 <= q[1] < W and same[q] and not out[q]: out[q] = True; st.append(q)
    fn = hue_letter if lab else C.nearest
    rows = [''.join('.' if out[y, x] else fn(arr[y, x]) for x in range(W)) for y in range(H)]
    rows = [''.join('.' if c in drop else c for c in r) for r in rows]
    for (y0, y1, x0, x1) in clear:
        rows = [''.join('.' if (y0 <= y <= y1 and x0 <= x <= x1) else c for x, c in enumerate(r)) for y, r in enumerate(rows)]
    rows = O.trim(rows)
    if post: rows = post(rows)
    return O.trim(rows)

def sprite_exact(idx):
    f = sorted(glob.glob(os.path.join(REM, '*.*')))[idx]
    a = np.array(Image.open(f).convert('RGBA'))
    return O.trim([''.join('.' if a[y, x, 3] < 128 else hue_letter(a[y, x, :3]) for x in range(a.shape[1])) for y in range(a.shape[0])])


# ---------- cor: vizinho mais proximo na paleta, mas respeitando o matiz ----------
import colorsys
_PALH = []
for c, h in T.PAL:
    rgb = np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)
    hh, ss, vv = colorsys.rgb_to_hsv(*(rgb / 255)); _PALH.append((T.LETTER[c], hh * 360, ss, vv, np.array(T.rgb2lab(rgb))))
def _hd(a, b): d = abs(a - b) % 360; return min(d, 360 - d)
_hue_cache = {}
def hue_letter(rgb):
    """cor muito saturada: so vale paleta do mesmo matiz; o resto (cinzas, tons pasteis, pele): vizinho mais proximo em RGB"""
    k = tuple(int(round(v / 3.0)) for v in rgb)
    if k in _hue_cache: return _hue_cache[k]
    rgb = np.array(rgb, float); h, s, v = colorsys.rgb_to_hsv(*(rgb / 255)); h *= 360
    if s >= 0.45 and v >= 0.30:
        lab = np.array(T.rgb2lab(rgb)); cands = []
        if 62 <= h <= 110:           # verde-limao: a paleta nao tem; o verde de verdade fica mais perto que o amarelo
            cands = [p for p in _PALH if 100 <= p[1] <= 175 and p[2] >= 0.25]
        for tol in (22, 38, 60):
            if cands: break
            cands = [p for p in _PALH if p[2] >= 0.25 and _hd(h, p[1]) <= tol]
        out = min(cands or _PALH, key=lambda p: ((lab - p[4]) ** 2).sum())[0]
    else:
        out = C.nearest(rgb)
    _hue_cache[k] = out; return out
