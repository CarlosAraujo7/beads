"""Lê PEÇAS de projetos 3D de beads a partir de FOTOS (placa ou superfície): acha a grade de contas (fitgrid), amostra o anel de cada conta e classifica pela paleta
explícita `pal` (lista de ((r,g,b), letra); a letra '.' = fundo). Devolve linhas de letras (como um molde) e grava uma imagem de conferência
(foto recortada com a letra lida em cima de cada conta) em tools/out/peg3d_<tag>.png — OLHE a conferência: foto de baixa resolução engana.

uso em Python:  import peg3d;  rows = peg3d.read(path, bbox, p0, pal, tag='maca1', ang=None)
"""
import os, sys
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import numpy as np, cv2
from PIL import Image
import fitgrid as F
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)


def read(path, bbox, p0, pal, tag='x', spread=0.12, angles=np.arange(-4, 4.1, 0.5), ring=(0.15, 0.42), minfrac=0.0, scale=3.0, trim=True):
    im = Image.open(path).convert('RGB'); tmp = os.path.join(OUT, f'peg3d_tmp_{tag}.png'); im.save(tmp)
    rot, cx, cy, p, ang, arr = F.fit(tmp, bbox, p0, spread=spread, angles=angles, step=0.5, ring=ring)
    a = np.array(arr)[..., :3].astype(float)
    cen = np.array([c for c, _ in pal], float); let = [l for _, l in pal]
    idx = np.argmin(((a[:, :, None, :] - cen[None, None, :, :]) ** 2).sum(axis=3), axis=2)
    grid = [[let[idx[y, x]] for x in range(a.shape[1])] for y in range(a.shape[0])]
    # recorta para as contas dentro de bbox (a grade tem 1 conta de folga)
    x0, y0, x1, y1 = bbox
    xs = [i for i, x in enumerate(cx) if x0 - p[0] / 2 <= x <= x1 + p[0] / 2]; ys = [j for j, y in enumerate(cy) if y0 - p[1] / 2 <= y <= y1 + p[1] / 2]
    sub = [[grid[j][i] for i in xs] for j in ys]
    rows = [''.join(r) for r in sub]
    # conferência: letras sobre a foto
    v = rot.copy()
    for j in ys:
        for i in xs:
            c = grid[j][i]
            if c != '.': cv2.putText(v, c, (int(cx[i]) - 4, int(cy[j]) + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 0, 255), 1)
    v = v[max(0, y0 - 6):y1 + 6, max(0, x0 - 6):x1 + 6]
    cv2.imwrite(os.path.join(OUT, f'peg3d_{tag}.png'), cv2.resize(v, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC))
    if trim:
        while rows and set(rows[0]) <= {'.'}: rows.pop(0)
        while rows and set(rows[-1]) <= {'.'}: rows.pop()
        if rows:
            xs2 = [x for r in rows for x, c in enumerate(r) if c != '.']; a0, a1 = min(xs2), max(xs2) + 1
            rows = [r[a0:a1] for r in rows]
    return rows, dict(p=p, ang=ang)


def show(rows):
    print(f'{len(rows[0])}x{len(rows)}')
    for r in rows: print(r)


def fit_lattice(img, bbox, p0, sig=(0.10, 0.28), thr=6.0):
    """grade pelos FUROS das contas (pontinhos escuros): DoG -> picos -> vetores entre vizinhos -> base (a, b) -> mínimos quadrados. Devolve (A, o): centro da conta (i, j) = o + i*a + j*b"""
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
    x0, y0, x1, y1 = bbox
    d = cv2.GaussianBlur(g, (0, 0), sig[1] * p0) - cv2.GaussianBlur(g, (0, 0), sig[0] * p0)       # furo = mais escuro que a volta -> positivo
    m = np.zeros_like(d, bool); m[y0:y1, x0:x1] = True
    pk = (d > thr) & (d == cv2.dilate(d, np.ones((int(p0 * 0.6) | 1, int(p0 * 0.6) | 1), np.uint8))) & m
    ys, xs = np.nonzero(pk); P = np.stack([xs, ys], 1).astype(float)
    if len(P) < 6: raise SystemExit('poucos furos achados (%d): ajuste p0/thr' % len(P))
    from scipy.spatial import cKDTree
    t = cKDTree(P); pairs = t.query_pairs(p0 * 1.35, output_type='ndarray'); V = P[pairs[:, 1]] - P[pairs[:, 0]]
    V[V[:, 0] < 0] *= -1; V[(V[:, 0] == 0) & (V[:, 1] < 0)] *= -1
    ln = np.hypot(V[:, 0], V[:, 1]); V = V[(ln > p0 * 0.7) & (ln < p0 * 1.3)]
    horiz = V[np.abs(V[:, 0]) > np.abs(V[:, 1])]; vert = V[np.abs(V[:, 1]) >= np.abs(V[:, 0])]
    a = np.median(horiz, axis=0); vert[vert[:, 1] < 0] *= -1; b = np.median(vert, axis=0)
    o = P[0].copy()
    for _ in range(4):
        M = np.array([a, b]).T; ij = np.round(np.linalg.solve(M, (P - o).T).T)
        X = np.c_[ij, np.ones(len(ij))]; sol, *_ = np.linalg.lstsq(X, P, rcond=None); a, b, o = sol[0], sol[1], sol[2]
    return a, b, o, len(P)


def read2(path, bbox, p0, pal, tag='x', rad=0.30, scale=3.0, bgmax=None, trim=True, margin=2, ij=None, **kw):
    """como read(), mas com a grade pelos furos. rad: raio (em passos) do círculo onde se amostra a cor da conta."""
    im = np.array(Image.open(path).convert('RGB')); h, w = im.shape[:2]
    a, b, o, n = fit_lattice(im, bbox, p0, **kw)
    x0, y0, x1, y1 = bbox
    # índices (i, j) que caem dentro do bbox
    corners = np.array([[x0, y0], [x1, y0], [x0, y1], [x1, y1]], float); M = np.array([a, b]).T
    cij = np.linalg.solve(M, (corners - o).T).T; i0, j0 = np.floor(cij.min(0)).astype(int) - margin, np.floor(cij.min(0)).astype(int)[1] - margin
    i0 = int(np.floor(cij[:, 0].min())) - margin; i1 = int(np.ceil(cij[:, 0].max())) + margin; j0 = int(np.floor(cij[:, 1].min())) - margin; j1 = int(np.ceil(cij[:, 1].max())) + margin
    cen = np.array([c for c, _ in pal], float); let = [l for _, l in pal]
    pr = max(2, int(round(rad * (np.hypot(*a) + np.hypot(*b)) / 2)))
    yy, xx = np.mgrid[-pr:pr + 1, -pr:pr + 1]; disc = (xx ** 2 + yy ** 2) <= pr * pr
    rows = []; pts = {}
    for j in range(j0, j1 + 1):
        r = ''
        for i in range(i0, i1 + 1):
            c = o + i * a + j * b; cx, cy = int(round(c[0])), int(round(c[1]))
            if not (x0 - 3 <= cx <= x1 + 3 and y0 - 3 <= cy <= y1 + 3 and pr <= cx < w - pr and pr <= cy < h - pr): r += '.'; continue
            patch = im[cy - pr:cy + pr + 1, cx - pr:cx + pr + 1][disc].astype(float)
            col = np.median(patch, axis=0)
            k = int(np.argmin(((cen - col) ** 2).sum(axis=1))); r += let[k]; pts[(i, j)] = (cx, cy, let[k])
        rows.append(r)
    v = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
    for (i, j), (cx, cy, l) in pts.items():
        if l != '.': cv2.putText(v, l, (cx - 4, cy + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 0, 255), 1)
    v = v[max(0, y0 - 6):y1 + 6, max(0, x0 - 6):x1 + 6]
    cv2.imwrite(os.path.join(OUT, f'peg3d_{tag}.png'), cv2.resize(v, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC))
    if trim:
        while rows and set(rows[0]) <= {'.'}: rows.pop(0)
        while rows and set(rows[-1]) <= {'.'}: rows.pop()
        if rows:
            xs2 = [x for r in rows for x, c in enumerate(r) if c != '.']; a0, a1 = min(xs2), max(xs2) + 1
            rows = [r[a0:a1] for r in rows]
    return rows, dict(a=a, b=b, o=o, furos=n)
