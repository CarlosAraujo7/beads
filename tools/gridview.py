"""Desenha uma grade (passo px, py, origem ox, oy) sobre um recorte ampliado de uma foto para LER contas à mão: cada célula numerada nas bordas.
uso: python tools/gridview.py foto x0,y0,x1,y1 ox,oy px[,py] [escala] [saida.png]"""
import sys, os
import numpy as np, cv2
from PIL import Image
SP = os.path.dirname(os.path.abspath(__file__))
path = sys.argv[1]; x0, y0, x1, y1 = (int(v) for v in sys.argv[2].split(','))
ox, oy = (float(v) for v in sys.argv[3].split(',')); pp = [float(v) for v in sys.argv[4].split(',')]; px = pp[0]; py = pp[1] if len(pp) > 1 else pp[0]
sc = float(sys.argv[5]) if len(sys.argv) > 5 else 5.0
out = sys.argv[6] if len(sys.argv) > 6 else os.path.join(SP, 'out', 'gridview.png')
im = np.array(Image.open(path).convert('RGB'))
v = cv2.resize(im[y0:y1, x0:x1], None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC)
i = 0
x = ox
while x < x1:
    if x >= x0:
        X = int((x - x0) * sc); cv2.line(v, (X, 0), (X, v.shape[0]), (255, 0, 255), 1)
        if i % 5 == 0: cv2.putText(v, str(int((x - ox) / px + .5)), (X + 2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1)
    x += px; i += 1
j = 0
y = oy
while y < y1:
    if y >= y0:
        Y = int((y - y0) * sc); cv2.line(v, (0, Y), (v.shape[1], Y), (255, 0, 255), 1)
        if j % 5 == 0: cv2.putText(v, str(int((y - oy) / py + .5)), (2, Y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 0), 1)
    y += py; j += 1
Image.fromarray(v).save(out); print(out, v.shape)
