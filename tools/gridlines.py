"""Acha as posições das linhas da grade de uma imagem (para forçar o passo em gráficos numerados).

uso (na raiz do projeto):  python tools/gridlines.py "remessa N/arquivo.png" x0 y0 x1 y1
Escolha uma faixa (x0,y0,x1,y1, em pixels da imagem) onde as células estão VAZIAS (só fundo e linhas da grade),
por exemplo o canto de cima de um gráfico. O script imprime as posições das linhas verticais e horizontais e o passo mediano.
Rode em duas faixas (início e fim da imagem) para calcular passo e deslocamento:  px = (última - primeira) / nº de células,  ox = primeira linha - k*px.
Depois use  px=dict(px=..., py=..., ox=..., oy=..., W=colunas, H=linhas)  com  mode=True  em r6.exact6 / r6_dump.py / colors.py.
"""
import sys
import numpy as np
from PIL import Image

p = sys.argv[1]
im = np.asarray(Image.open(p).convert('RGB')).astype(float)
x0, y0, x1, y1 = map(int, sys.argv[2:6])
reg = im[y0:y1, x0:x1].mean(axis=2)
colp = reg.mean(axis=0); rowp = reg.mean(axis=1)


def peaks(prof, off):
    m = prof.mean(); s = prof.std()
    idx = [i for i in range(1, len(prof) - 1) if prof[i] < m - 0.6 * s and prof[i] <= prof[i - 1] and prof[i] <= prof[i + 1]]
    return [i + off for i in idx]


px = peaks(colp, x0); py = peaks(rowp, y0)
print('verticais x:', px[:60])
print('horizontais y:', py[:80])
if len(px) > 3:
    d = np.diff(px); print('passo x mediano', np.median(d), 'min', d.min(), 'max', d.max())
if len(py) > 3:
    d = np.diff(py); print('passo y mediano', np.median(d), 'min', d.min(), 'max', d.max())
