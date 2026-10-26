import sys, os
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import numpy as np, cv2
import lattice as L

def fit(path, bbox, p0, spread=0.08, angles=np.arange(-4, 4.1, 0.5), mask=None, ring=(0.27, 0.45), step=0.5):
    """acha angulo, passo e deslocamento da grade de contas dentro de bbox=(x0,y0,x1,y1) e amostra o centro de cada conta"""
    img = cv2.imread(path); h, w = img.shape[:2]
    x0, y0, x1, y1 = bbox
    gray0 = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (3, 3), 0).astype(float)
    bm0 = np.zeros((h, w), np.uint8); bm0[y0:y1, x0:x1] = 1
    def search(prof, lo, hi):
        n = len(prof); v = prof - prof.mean(); k = np.arange(n); best = (0, lo)
        for p in np.arange(lo, hi, 0.02):
            s = abs((v * np.exp(-2j * np.pi * k / p)).sum())
            if s > best[0]: best = (s, p)
        return best
    best = None
    for ang in angles:
        M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
        gr = cv2.warpAffine(gray0, M, (w, h)); bm = cv2.warpAffine(bm0, M, (w, h)) > 0
        gx = np.abs(np.diff(gr, axis=1)) * bm[:, 1:]; gy = np.abs(np.diff(gr, axis=0)) * bm[1:, :]
        sx = search(gx.sum(0), p0 * (1 - spread), p0 * (1 + spread)); sy = search(gy.sum(1), p0 * (1 - spread), p0 * (1 + spread))
        sc = sx[0] / max(1, gx.sum()) + sy[0] / max(1, gy.sum())
        if best is None or sc > best[0]: best = (sc, ang, sx[1], sy[1])
    _, ang, px, py = best
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    rot = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    bm = cv2.warpAffine(bm0, M, (w, h)) > 0
    if mask is not None: bm = bm & mask(rot)
    g = cv2.cvtColor(rot, cv2.COLOR_BGR2GRAY).astype(float)
    D = cv2.GaussianBlur(np.abs(g - cv2.GaussianBlur(g, (0, 0), px * 0.35)), (0, 0), 1.2)
    nx = int(w / px) + 2; ny = int(h / py) + 2; bs = None
    for oy in np.arange(0, py, step):
        ys = (oy + np.arange(ny) * py).astype(int).clip(0, h - 1)
        for ox in np.arange(0, px, step):
            xs = (ox + np.arange(nx) * px).astype(int).clip(0, w - 1)
            X, Y = np.meshgrid(xs, ys); m = bm[Y, X]
            s = D[Y, X][m].mean() if m.any() else 0
            if bs is None or s > bs[0]: bs = (s, ox, oy)
    cx = bs[1] + np.arange(nx) * px; cy = bs[2] + np.arange(ny) * py
    cx = cx[cx < w - px * .5]; cy = cy[cy < h - py * .5]
    # recorta para a caixa (com 1 conta de folga)
    cx = cx[(cx > x0 - px) & (cx < x1 + px)]; cy = cy[(cy > y0 - py) & (cy < y1 + py)]
    arr = L.sample(rot, cx, cy, (px + py) / 2, ring)
    return rot, cx, cy, (px, py), ang, arr

def check(rot, cx, cy, out, bbox, scale=1.6):
    v = rot.copy(); h, w = v.shape[:2]
    for x in cx: cv2.line(v, (int(x), 0), (int(x), h), (255, 0, 255), 1)
    for y in cy: cv2.line(v, (0, int(y)), (w, int(y)), (255, 0, 255), 1)
    x0, y0, x1, y1 = bbox
    v = cv2.resize(v[max(0, y0 - 20):y1 + 20, max(0, x0 - 20):x1 + 20], None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(out, v)

def labeled(rot, cx, cy, out, bbox, scale=1.6, rows=None):
    v = rot.copy()
    for j, y in enumerate(cy):
        for i, x in enumerate(cx):
            cv2.putText(v, f'{i},{j}', (int(x) - 11, int(y) + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 0, 255), 1)
    x0, y0, x1, y1 = bbox
    y0c, y1c = (y0, y1) if rows is None else (int(cy[rows[0]] - 20), int(cy[rows[1]] + 20))
    v = cv2.resize(v[max(0, y0c - 20):y1c + 20, max(0, x0 - 20):x1 + 20], None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(out, v); return v.shape
