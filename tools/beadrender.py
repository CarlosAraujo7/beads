"""Lê RENDERS de peças de contas montadas sobre placa (remessa 21: imagens geradas, com a grade das contas diferente da grade de pinos da placa e às vezes não quadrada).
  lattice(img, box, p0)            -> (ox, oy, px, py): centro da conta (0,0) e passos x/y, ajustados pelos FUROS das contas (centro mais escuro que o anel)
  cells(img, lat, box)             -> grade de medidas por célula: cor do anel (mediana), contraste anel-centro, se parece conta
  overlay(img, lat, box, path)     -> recorte ampliado com a grade desenhada (para conferir olhando)
"""
import numpy as np, cv2
from PIL import Image

ANG = np.linspace(0, 2 * np.pi, 12, endpoint=False)


def load(path):
    return np.array(Image.open(path).convert('RGB'))


def _score(g, x0, y0, x1, y1, ox, oy, px, py, r=0.30):
    xs = np.arange(ox + np.ceil((x0 - ox) / px) * px, x1, px); ys = np.arange(oy + np.ceil((y0 - oy) / py) * py, y1, py)
    if len(xs) < 3 or len(ys) < 3: return -1e9
    X, Y = np.meshgrid(xs, ys); H, W = g.shape
    rx = np.clip((X[..., None] + px * r * np.cos(ANG)).round().astype(int), 0, W - 1)
    ry = np.clip((Y[..., None] + py * r * np.sin(ANG)).round().astype(int), 0, H - 1)
    ring = g[ry, rx].mean(axis=-1)
    cen = g[np.clip(Y.round().astype(int), 0, H - 1), np.clip(X.round().astype(int), 0, W - 1)]
    # entre contas (canto da célula) a imagem também é mais escura: penaliza a fase "meio passo" pela diferença canto x anel
    cx = np.clip((X + px / 2).round().astype(int), 0, W - 1); cy = np.clip((Y + py / 2).round().astype(int), 0, H - 1)
    corner = g[cy, cx]
    return float(((ring - cen) + 0.5 * (ring - corner)).mean())


def lattice(img, box, p0, spread=0.12, verbose=True):
    """p0 = passo aproximado (ou (px, py)); procura passo quadrado, depois refina px e py separados e a fase"""
    g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(float), (3, 3), 0)
    x0, y0, x1, y1 = box
    p0x, p0y = (p0, p0) if np.isscalar(p0) else p0
    best = None
    for px in np.arange(p0x * (1 - spread), p0x * (1 + spread), 0.1):
        py = px * p0y / p0x
        for ox in np.arange(0, px, 1.0):
            for oy in np.arange(0, py, 1.0):
                s = _score(g, x0, y0, x1, y1, x0 + ox, y0 + oy, px, py)
                if best is None or s > best[0]: best = (s, x0 + ox, y0 + oy, px, py)
    s, ox, oy, px, py = best
    for _ in range(2):                                            # refino fino: px, py e fase separados
        cand = []
        for dpx in np.arange(-0.5, 0.51, 0.05):
            for dpy in np.arange(-0.5, 0.51, 0.05):
                for dox in np.arange(-1.5, 1.51, 0.5):
                    for doy in np.arange(-1.5, 1.51, 0.5):
                        cand.append((_score(g, x0, y0, x1, y1, ox + dox, oy + doy, px + dpx, py + dpy), ox + dox, oy + doy, px + dpx, py + dpy))
        best = max(cand); s, ox, oy, px, py = best
    if verbose: print('grade: ox %.2f oy %.2f px %.3f py %.3f (nota %.2f)' % (ox, oy, px, py, s))
    return ox, oy, px, py


def cells(img, lat, box, r=0.30):
    """devolve (cols, rows, c0, r0, rgb[rows,cols,3], contraste[rows,cols]) para as células cujo centro está dentro de `box`"""
    ox, oy, px, py = lat; x0, y0, x1, y1 = box
    c0 = int(np.ceil((x0 - ox) / px)); c1 = int(np.floor((x1 - ox) / px)); r0 = int(np.ceil((y0 - oy) / py)); r1 = int(np.floor((y1 - oy) / py))
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(float); H, W = g.shape
    rows = r1 - r0 + 1; cols = c1 - c0 + 1
    rgb = np.zeros((rows, cols, 3)); con = np.zeros((rows, cols))
    for j in range(rows):
        for i in range(cols):
            cx = ox + (c0 + i) * px; cy = oy + (r0 + j) * py
            rx = np.clip((cx + px * r * np.cos(ANG)).round().astype(int), 0, W - 1); ry = np.clip((cy + py * r * np.sin(ANG)).round().astype(int), 0, H - 1)
            rgb[j, i] = np.median(img[ry, rx].astype(float), axis=0)
            con[j, i] = g[ry, rx].mean() - g[int(np.clip(round(cy), 0, H - 1)), int(np.clip(round(cx), 0, W - 1))]
    return cols, rows, c0, r0, rgb, con


def quantize(img, box, K=14, seed=3):
    """k-means em Lab dos pixels da caixa: devolve (rótulos HxW da caixa, centros RGB)"""
    x0, y0, x1, y1 = box
    sub = img[y0:y1, x0:x1]
    lab = cv2.cvtColor(sub, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
    rs = np.random.RandomState(seed); pts = lab if len(lab) < 150000 else lab[rs.choice(len(lab), 150000, replace=False)]
    cv2.setRNGSeed(seed)
    _, _, cen = cv2.kmeans(pts, K, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.5), 3, cv2.KMEANS_PP_CENTERS)
    d = ((lab[:, None, :] - cen[None]) ** 2).sum(-1); lbl = d.argmin(1).reshape(sub.shape[:2])
    rgb = [sub.reshape(-1, 3)[lbl.ravel() == k].mean(axis=0) if (lbl == k).any() else np.zeros(3) for k in range(K)]
    return lbl, np.array(rgb)


_RING = [(r, a) for r in (0.24, 0.36) for a in np.linspace(0, 2 * np.pi, 10, endpoint=False)]


def _samples(lbl, box, ox, oy, px, py):
    x0, y0, x1, y1 = box; H, W = lbl.shape
    c0 = int(np.ceil((x0 - ox) / px)); c1 = int(np.floor((x1 - 1 - ox) / px)); r0 = int(np.ceil((y0 - oy) / py)); r1 = int(np.floor((y1 - 1 - oy) / py))
    cx = ox + np.arange(c0, c1 + 1) * px - x0; cy = oy + np.arange(r0, r1 + 1) * py - y0
    X, Y = np.meshgrid(cx, cy)
    sx = np.clip((X[..., None] + np.array([r * px * np.cos(a) for r, a in _RING])).round().astype(int), 0, W - 1)
    sy = np.clip((Y[..., None] + np.array([r * py * np.sin(a) for r, a in _RING])).round().astype(int), 0, H - 1)
    return lbl[sy, sx], c0, r0


def purity(lbl, box, lat, K):
    s, _, _ = _samples(lbl, box, *lat)
    cnt = (s[..., None] == np.arange(K)).sum(axis=2)
    return float((cnt.max(-1) / s.shape[-1]).mean())


def lattice_purity(img, box, p0, K=14, spread=0.04, verbose=True):
    """grade que deixa cada célula mais 'pura' (o anel de amostras cai numa conta só): passo inicial p0=(px, py) da autocorrelação"""
    lbl, _ = quantize(img, box, K)
    p0x, p0y = (p0, p0) if np.isscalar(p0) else p0
    x0, y0 = box[0], box[1]
    best = None
    for k in np.arange(1 - spread, 1 + spread + 1e-9, 0.005):
        px, py = p0x * k, p0y * k
        for ox in np.arange(0, px, 1.0):
            for oy in np.arange(0, py, 1.0):
                sc = purity(lbl, box, (x0 + ox, y0 + oy, px, py), K)
                if best is None or sc > best[0]: best = (sc, x0 + ox, y0 + oy, px, py)
    sc, ox, oy, px, py = best
    for _ in range(2):
        cand = [best]
        for dpx in np.arange(-0.3, 0.31, 0.05):
            for dpy in np.arange(-0.3, 0.31, 0.05):
                for dox in (-0.5, 0, 0.5):
                    for doy in (-0.5, 0, 0.5):
                        lat = (ox + dox, oy + doy, px + dpx, py + dpy)
                        cand.append((purity(lbl, box, lat, K),) + lat)
        best = max(cand); sc, ox, oy, px, py = best
    if verbose: print('grade (pureza %.3f): ox %.2f oy %.2f px %.3f py %.3f' % (sc, ox, oy, px, py))
    return (ox, oy, px, py), lbl


def read_mode(img, box, lat, K=14, lbl_cen=None):
    """cada célula = classe (k-means) mais comum no anel da conta; devolve (classes[rows, cols], centros RGB, c0, r0)"""
    lbl, cen = lbl_cen if lbl_cen else quantize(img, box, K)
    s, c0, r0 = _samples(lbl, box, *lat)
    cnt = (s[..., None] == np.arange(len(cen))).sum(axis=2)
    return cnt.argmax(-1), cen, c0, r0


def detect_beads(img, box, p, min_con=10.0):
    """acha cada conta pelo FURO: mínimo local do cinza (borrado) numa vizinhança de ~0,6 passo, com o anel (raio 0,3 passo) mais claro que o centro em >= min_con.
    devolve lista de (x, y, contraste, rgb do anel)"""
    x0, y0, x1, y1 = box
    g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32), (0, 0), max(1.0, p * 0.08))
    k = max(3, int(p * 0.6) | 1)
    mn = cv2.erode(g, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    ys, xs = np.nonzero((g <= mn + 0.01))
    out = []
    H, W = g.shape
    for x, y in zip(xs, ys):
        if not (x0 <= x < x1 and y0 <= y < y1): continue
        rx = np.clip((x + p * 0.30 * np.cos(ANG)).round().astype(int), 0, W - 1); ry = np.clip((y + p * 0.30 * np.sin(ANG)).round().astype(int), 0, H - 1)
        con = g[ry, rx].mean() - g[y, x]
        if con < min_con: continue
        rx2 = np.clip((x + p * 0.32 * np.cos(ANG)).round().astype(int), 0, W - 1); ry2 = np.clip((y + p * 0.32 * np.sin(ANG)).round().astype(int), 0, H - 1)
        out.append((float(x), float(y), float(con), np.median(img[ry2, rx2].astype(float), axis=0)))
    # junta mínimos duplicados (platô) a menos de 0,35 passo
    out.sort(key=lambda t: -t[2]); kept = []
    for b in out:
        if all((b[0] - c[0]) ** 2 + (b[1] - c[1]) ** 2 > (p * 0.45) ** 2 for c in kept): kept.append(b)
    return kept


def snap_beads(beads, p0):
    """encaixa as contas detectadas numa grade: passo = mediana das distâncias aos vizinhos de lado; fase = a que minimiza o resíduo; devolve dict (col, lin) -> conta"""
    P = np.array([(b[0], b[1]) for b in beads])
    dx = []; dy = []
    for i, (x, y) in enumerate(P):
        d = P - (x, y)
        hor = d[(np.abs(d[:, 1]) < p0 * 0.4) & (d[:, 0] > p0 * 0.6) & (d[:, 0] < p0 * 1.5)]
        ver = d[(np.abs(d[:, 0]) < p0 * 0.4) & (d[:, 1] > p0 * 0.6) & (d[:, 1] < p0 * 1.5)]
        if len(hor): dx.append(hor[:, 0].min())
        if len(ver): dy.append(ver[:, 1].min())
    px, py = float(np.median(dx)), float(np.median(dy))
    best = None
    for fx in np.linspace(0, 1, 20, endpoint=False):
        for fy in np.linspace(0, 1, 20, endpoint=False):
            u = (P[:, 0] / px - fx); v = (P[:, 1] / py - fy)
            res = (np.abs(u - u.round()) + np.abs(v - v.round())).mean()
            if best is None or res < best[0]: best = (res, fx, fy)
    _, fx, fy = best
    grid = {}
    for b in beads:
        c = int(round(b[0] / px - fx)); r = int(round(b[1] / py - fy))
        if (c, r) not in grid or b[2] > grid[(c, r)][2]: grid[(c, r)] = b
    return grid, (px, py, fx, fy, best[0])


def overlay(img, lat, box, path, rows=None, c0=0, r0=0, sc=2.5):
    x0, y0, x1, y1 = [int(v) for v in box]
    ox, oy, px, py = lat
    v = cv2.resize(img[y0:y1, x0:x1], None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC).copy()
    nx = int((x1 - ox) / px) + 2; ny = int((y1 - oy) / py) + 2
    for i in range(-2, nx):
        x = (ox + (i - 0.5) * px - x0) * sc
        if 0 <= x < v.shape[1]: cv2.line(v, (int(x), 0), (int(x), v.shape[0] - 1), (255, 0, 255), 1)
    for j in range(-2, ny):
        y = (oy + (j - 0.5) * py - y0) * sc
        if 0 <= y < v.shape[0]: cv2.line(v, (0, int(y)), (v.shape[1] - 1, int(y)), (255, 0, 255), 1)
    Image.fromarray(v).save(path)
