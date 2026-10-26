"""Detecção de grade com tamanho de quadradinho fracionário (espectro das bordas + refino em subpixel)."""
import numpy as np

def edge_profiles(rgba):
    a = rgba.astype(float)
    ex = np.abs(np.diff(a, axis=1)).sum(2).sum(0)
    ey = np.abs(np.diff(a, axis=0)).sum(2).sum(1)
    return np.concatenate([[0], ex]), np.concatenate([[0], ey])

def spectral_period(e, pmin=3.0, pmax=70.0):
    n = len(e)
    a = (e - e.mean()) * np.hanning(n)
    N = 1 << int(np.ceil(np.log2(n * 16)))
    F = np.abs(np.fft.rfft(a, N)) ** 2
    fr = np.fft.rfftfreq(N)
    sel = (fr >= 1 / pmax) & (fr <= 1 / pmin)
    Fs = np.where(sel, F, 0)
    k = int(Fs.argmax())
    # procura sub-harmônico: se existe pico forte em metade da frequência, o período real é o dobro
    p = 1 / fr[k]
    return p, Fs[k] / (F[sel].sum() + 1e-9)

def refine(e, p0, span=0.06, step=0.01):
    """acha (passo, offset) fracionários que maximizam a energia de borda nas posições da grade"""
    n = len(e)
    best = (-1, p0, 0.0)
    cs = np.cumsum(np.concatenate([[0], e]))
    ee = e + np.roll(e, -1)           # une a borda antialiased em 2 pixels
    for p in np.arange(p0 * (1 - span), p0 * (1 + span) + 1e-9, p0 * step):
        for o in np.arange(0, p, 0.25):
            j = np.arange(0, int((n - 1 - o) / p) + 1)
            pos = np.floor(o + j * p).astype(int)
            pos = pos[pos < n - 1]
            sc = ee[pos].mean() if len(pos) else 0
            if sc > best[0]: best = (sc, p, o)
    return best[1], best[2]

def detect(rgba, force=None):
    ex, ey = edge_profiles(rgba)
    px_, qx = spectral_period(ex); py_, qy = spectral_period(ey)
    if force: px_ = py_ = float(force)
    # se x e y discordam muito, usa o de maior energia nos dois
    if abs(px_ - py_) / max(px_, py_) > 0.1:
        if qx >= qy: py_ = px_
        else: px_ = py_
    px, ox = refine(ex, px_); py, oy = refine(ey, py_)
    h, w, _ = rgba.shape
    # inclui células parciais nas bordas (se tiverem >= 40% do tamanho)
    j0 = -1 if ox > 0.4 * px else 0
    i0 = -1 if oy > 0.4 * py else 0
    W = int(np.floor((w - ox) / px + 0.6)) - j0
    H = int(np.floor((h - oy) / py + 0.6)) - i0
    return dict(px=px, py=py, ox=ox + j0 * px, oy=oy + i0 * py, W=W, H=H, q=min(qx, qy))

def sample(rgba, g, mode=False, inset=0.15, ring=None):
    px, py, ox, oy, W, H = g['px'], g['py'], g['ox'], g['oy'], g['W'], g['H']
    hh, ww, _ = rgba.shape
    out = np.zeros((H, W, 4))
    for by in range(H):
        y0 = oy + by * py; ya = int(round(y0 + py * .3)); yb = max(ya + 1, int(round(y0 + py * .7)))
        ya = max(0, ya); yb = min(hh, yb)
        for bx in range(W):
            x0 = ox + bx * px; xa = int(round(x0 + px * .3)); xb = max(xa + 1, int(round(x0 + px * .7)))
            xa = max(0, xa); xb = min(ww, xb)
            if ya >= yb or xa >= xb:
                out[by, bx] = (255, 255, 255, 0); continue
            if ring:   # anel da conta (ignora o buraco do centro e o reflexo)
                cx_, cy_ = x0 + px / 2, y0 + py / 2
                r0, r1 = ring
                xa2 = max(0, int(cx_ - r1 * px)); xb2 = min(ww, int(cx_ + r1 * px) + 1)
                ya2 = max(0, int(cy_ - r1 * py)); yb2 = min(hh, int(cy_ + r1 * py) + 1)
                if xa2 >= xb2 or ya2 >= yb2: out[by, bx] = (255, 255, 255, 0); continue
                yy, xx = np.mgrid[ya2:yb2, xa2:xb2]
                dd = np.hypot((xx - cx_) / px, (yy - cy_) / py)
                sel = (dd >= r0) & (dd <= r1)
                blk = rgba[ya2:yb2, xa2:xb2][sel]
                out[by, bx] = np.median(blk, axis=0) if len(blk) else (255, 255, 255, 0)
            elif mode:   # cor dominante da célula (ignora texto/códigos desenhados dentro dela)
                x0i = int(round(x0 + px * inset)); x1i = int(round(x0 + px * (1 - inset)))
                y0i = int(round(y0 + py * inset)); y1i = int(round(y0 + py * (1 - inset)))
                x0i = max(0, x0i); y0i = max(0, y0i); x1i = min(ww, max(x1i, x0i + 1)); y1i = min(hh, max(y1i, y0i + 1))
                blk = rgba[y0i:y1i, x0i:x1i].reshape(-1, 4)
                key = (blk[:, :3] // 24).astype(int)
                kk = key[:, 0] * 100 + key[:, 1] * 10 + key[:, 2]
                vals, inv, cnt = np.unique(kk, return_inverse=True, return_counts=True)
                best = cnt.argmax()
                out[by, bx] = blk[inv.reshape(-1) == best].mean(axis=0)
            else:
                blk = rgba[ya:yb, xa:xb].reshape(-1, 4)
                out[by, bx] = np.median(blk, axis=0)
    return out
