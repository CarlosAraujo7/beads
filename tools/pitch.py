"""Estima o passo (px por conta) e a fase da grade de contas/pinos numa região de uma foto, por autocorrelação do gradiente.
uso: python tools/pitch.py foto x0,y0,x1,y1 [min,max]     (passo procurado entre min e max px; padrão 6,30)
Imprime o passo em x e y e a fase (origem) que mais alinha as linhas de grade com os furos/pinos. Confira SEMPRE com tools/gridview.py:
a estimativa pode cair no dobro/metade do passo real."""
import sys
import numpy as np
from PIL import Image


def estimate(path, box, lo=6, hi=30):
    x0, y0, x1, y1 = box
    g = np.array(Image.open(path).convert('L'), dtype=float)[y0:y1, x0:x1]
    out = {}
    for ax, name in ((1, 'x'), (0, 'y')):
        d = np.abs(np.diff(g, axis=ax))
        prof = d.sum(axis=1 - ax)                      # perfil ao longo do eixo
        prof = prof - prof.mean()
        n = len(prof)
        best = None
        for p10 in range(int(lo * 20), int(hi * 20)):  # passo em passos de 0,05 px
            p = p10 / 20.0
            k = np.arange(n)
            c = (prof * np.cos(2 * np.pi * k / p)).sum(); s = (prof * np.sin(2 * np.pi * k / p)).sum()
            amp = np.hypot(c, s)
            if best is None or amp > best[0]:
                best = (amp, p, (np.arctan2(s, c) / (2 * np.pi)) * p % p)
        out[name] = best
    return out


if __name__ == '__main__':
    path = sys.argv[1]; box = tuple(int(v) for v in sys.argv[2].split(','))
    lo, hi = (float(v) for v in sys.argv[3].split(',')) if len(sys.argv) > 3 else (6, 30)
    r = estimate(path, box, lo, hi)
    for k in 'xy':
        amp, p, ph = r[k]
        print(f'{k}: passo {p:.2f}  fase {ph + (box[0] if k == "x" else box[1]):.1f}  (amp {amp:.0f})')
