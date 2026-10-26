"""Lista as cores mais comuns das celulas de uma imagem da remessa e a letra da paleta que cada uma vira.

uso (na raiz do projeto):  REMNUM=9 python tools/colors.py <indice> [px=22.0] [crop_img="(x0,y0,x1,y1)"] [crop="(y0,y1,x0,x1)"] [mode=True] [dist=16] [n=14]
Serve para decidir overrides de cor (colmap) antes de rodar a conversao.
"""
import os, sys, colorsys
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from collections import Counter
import r6

def main(i, n=14, dist=16, **kw):
    arr = r6.load_cells(i, **kw); sn = r6.snap(arr, dist); H, W, _ = sn.shape
    c = Counter(tuple(int(v) for v in sn[y, x]) for y in range(H) for x in range(W))
    print('imagem', i, 'celulas', W, 'x', H)
    for k, v in c.most_common(n):
        h, s, vv = colorsys.rgb_to_hsv(*[x / 255 for x in k])
        print('  ', k, v, '->', r6.mapc(k), 'h%d s%.2f v%.2f' % (h * 360, s, vv))

if __name__ == '__main__':
    a = sys.argv[1:]
    kw = {}
    for t in a[1:]:
        k, v = t.split('=', 1); kw[k] = eval(v)
    main(int(a[0]), **kw)
