"""Lê um GRÁFICO limpo (grade de quadradinhos com cores chapadas, como os da remessa 3D 2) célula a célula.
uso em Python:  from gridread import cells, clusters
  g = cells(path, ox, oy, p, cols, rows)         -> lista de listas de (r,g,b): cor do CENTRO de cada célula (origem = canto da célula 0,0; passo p px)
  clusters(g, tol=18)                            -> [(cor, nº de células)] cores distintas (para escolher a paleta)
  letters(g, pal, bg)                            -> linhas de letras; pal=[((r,g,b),'letra'),...]; bg = cores que viram '.'
"""
import numpy as np
from PIL import Image


def cells(path, ox, oy, p, cols, rows, r=0.25):
    im = np.array(Image.open(path).convert('RGB')).astype(float)
    g = []
    for j in range(rows):
        row = []
        for i in range(cols):
            cx, cy = ox + (i + .5) * p, oy + (j + .5) * p
            a = int(max(0, cy - p * r)); b = int(cy + p * r) + 1; c = int(max(0, cx - p * r)); d = int(cx + p * r) + 1
            row.append(tuple(int(v) for v in np.median(im[a:b, c:d].reshape(-1, 3), axis=0)))
        g.append(row)
    return g


def clusters(g, tol=18):
    cs = []
    for row in g:
        for c in row:
            for k in cs:
                if sum((a - b) ** 2 for a, b in zip(k[0], c)) ** .5 <= tol: k[1] += 1; break
            else: cs.append([c, 1])
    return sorted(((tuple(k[0]), k[1]) for k in cs), key=lambda t: -t[1])


def letters(g, pal, bg=((255, 255, 255),), tol=30):
    refs = [(c, l) for c, l in pal] + [(c, '.') for c in bg]
    out = []
    for row in g:
        s = ''
        for c in row:
            d, l = min((sum((a - b) ** 2 for a, b in zip(rc, c)) ** .5, l) for rc, l in refs)
            s += l if d <= tol * 2 else '?'
        out.append(s)
    return out
