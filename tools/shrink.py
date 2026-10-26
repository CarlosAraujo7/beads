"""Reduz um molde grande para caber em UMA placa (padrão 50x50), mantendo as cores da paleta e os contornos.

uso em Python:  import shrink;  shrink.shrink(rows, size=50, method='bias') -> novas linhas
métodos:
  'mode'  = cada conta nova recebe a cor que mais cobre a região (contornos finos somem)
  'bias'  = igual, mas as cores escuras (contorno) pesam mais, para o traço de 1 conta sobreviver   <- padrão
  'lab'   = média das cores em Lab e depois a cor mais próxima da paleta (suaviza, mas "lava" o contorno)
"""
import math, os, sys
import numpy as np
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from layoutsim import RGB


def _lab(rgb):
    c = np.asarray(rgb, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    x, y, z = (M @ c) / np.array([0.95047, 1.0, 1.08883])
    f = lambda t: np.cbrt(t) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return np.array([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)])


LAB = {k: _lab(v) for k, v in RGB.items()}
# peso extra das cores escuras: o contorno de 1 conta é o que mais se perde numa redução
BIAS = {'k': 1.9, 'd': 1.5, 'm': 1.15}


def target_size(w, h, size=50):
    s = max(w, h) / size
    if s <= 1: return w, h
    return max(1, min(size, round(w / s))), max(1, min(size, round(h / s)))


def shrink(rows, size=50, method='bias', empty_at=0.5):
    H = len(rows); W = max(len(r) for r in rows)
    nw, nh = target_size(W, H, size)
    if (nw, nh) == (W, H): return list(rows)
    out = []
    for j in range(nh):
        y0, y1 = j * H / nh, (j + 1) * H / nh
        row = ''
        for i in range(nw):
            x0, x1 = i * W / nw, (i + 1) * W / nw
            wt = {}
            for y in range(int(math.floor(y0)), min(H, int(math.ceil(y1)))):
                wy = min(y + 1, y1) - max(y, y0)
                if wy <= 0: continue
                r = rows[y]
                for x in range(int(math.floor(x0)), min(W, int(math.ceil(x1)))):
                    wx = min(x + 1, x1) - max(x, x0)
                    if wx <= 0: continue
                    c = r[x] if x < len(r) else '.'
                    wt[c] = wt.get(c, 0) + wx * wy
            total = (x1 - x0) * (y1 - y0)
            if wt.get('.', 0) >= empty_at * total: row += '.'; continue
            cols = {c: a for c, a in wt.items() if c != '.'}
            if not cols: row += '.'; continue
            if method == 'lab':
                s = sum(cols.values())
                m = sum(LAB[c] * a for c, a in cols.items()) / s
                row += min(LAB, key=lambda k: float(np.linalg.norm(LAB[k] - m)))
            else:
                b = BIAS if method == 'bias' else {}
                row += max(cols, key=lambda c: cols[c] * b.get(c, 1.0))
        out.append(row)
    # tira linhas/colunas vazias que sobraram nas bordas
    while out and not any(c != '.' for c in out[0]): out.pop(0)
    while out and not any(c != '.' for c in out[-1]): out.pop()
    if out:
        xs = [x for r in out for x, c in enumerate(r) if c != '.']
        x0, x1 = min(xs), max(xs) + 1
        out = [r[x0:x1] for r in out]
    return out
