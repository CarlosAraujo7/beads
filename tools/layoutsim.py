"""Comparação TOLERANTE entre dois moldes (independe de nome, de tamanho e de pequenas diferenças de desenho).

Cada molde vira uma miniatura 24x24 (a caixa do desenho, com a proporção preservada) e as miniaturas são comparadas
célula a célula por forma (vazio x conta) e por cor. Serve para saber "este desenho já está no catálogo, mesmo com outro nome,
outro tamanho ou sem o contorno?".

uso em Python:  import layoutsim as L;  L.score(rowsA, rowsB)  -> 0..1   (>= 0.80 costuma ser o mesmo desenho)
                L.best(rows, catalogo_items, n=3) -> [(score, nome), ...]
"""
import os, sys
import numpy as np
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)

_HEX = {'k': '2E2E32', 'w': 'FFFFFF', 'i': 'E4E7EA', 'd': '5F6065', 'm': '8A8D93', 'l': 'B5B8BE', 'r': 'BD3A4B', 'p': 'EA9BB8', 'q': 'F1C4D1',
        'o': 'EC8546', 'a': 'E9A23B', 'y': 'EBC22F', 's': 'E4C7B5', 't': 'D99479', 'n': '8F5E50', 'b': '6B98D3', 'c': '55BEDB', 'e': 'C3E5F3',
        'u': '75609A', 'v': 'A89BC6', 'x': 'C8C4E4', 'g': '7FC79C', 'f': '5FA66E', 'h': '3F8761'}
RGB = {k: np.array([int(v[i:i + 2], 16) for i in (0, 2, 4)], float) for k, v in _HEX.items()}
N = 24


def thumb(rows):
    H, W = len(rows), max(len(r) for r in rows)
    ys = [y for y, r in enumerate(rows) if any(c != '.' for c in r)]
    xs = [x for r in rows for x, c in enumerate(r) if c != '.']
    if not ys: return np.zeros((N, N)), np.zeros((N, N, 3))
    y0, y1, x0, x1 = min(ys), max(ys) + 1, min(xs), max(xs) + 1
    h, w = y1 - y0, x1 - x0
    side = max(h, w)
    sh = np.zeros((N, N)); col = np.zeros((N, N, 3))
    cnt = np.zeros((N, N))
    # cada conta cai numa célula da miniatura (centralizado)
    oy = (side - h) / 2; ox = (side - w) / 2
    for y in range(h):
        for x in range(w):
            c = rows[y0 + y][x0 + x] if x0 + x < len(rows[y0 + y]) else '.'
            if c == '.' or c not in RGB: continue
            ty = min(N - 1, int((y + oy) * N / side)); tx = min(N - 1, int((x + ox) * N / side))
            sh[ty, tx] += 1; col[ty, tx] += RGB[c]
    cell = (side / N) ** 2
    filled = sh > max(0.25, 0.3 * cell)   # a célula conta como preenchida se mais de ~30% dela tem contas
    out = np.zeros((N, N, 3))
    out[filled] = col[filled] / sh[filled][:, None]
    return filled.astype(float), out


def score(a, b):
    sa, ca = thumb(a); sb, cb = thumb(b)
    both = (sa > 0) & (sb > 0)
    union = (sa > 0) | (sb > 0)
    if union.sum() == 0: return 0.0
    shape = both.sum() / union.sum()                       # IoU da forma
    if both.sum() == 0: return 0.0
    cd = np.linalg.norm(ca[both] - cb[both], axis=1) / 441.7  # 0..1
    colr = 1 - float(np.clip(cd.mean() * 2.2, 0, 1))        # cor parecida
    return float(0.65 * shape + 0.35 * colr)


def best(rows, items, n=3):
    sc = sorted(((score(rows, t['rows']), t['name']) for t in items), reverse=True)
    return sc[:n]
