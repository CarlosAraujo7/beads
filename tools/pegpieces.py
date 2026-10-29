"""Lê as PEÇAS de um projeto 3D fotografado numa placa (pegboard): acha a grade de pinos/contas, amostra cada conta e imprime/desenha as peças.
uso:  python tools/pegpieces.py "remessa 3D 1/arq.jpg" x0,y0,x1,y1 passo0 [K]     -> imprime os grupos de cor (K) e salva tools/out/peg_check.png (grade desenhada sobre a foto)
"""
import os, sys
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import numpy as np, cv2
import fitgrid as F
from PIL import Image
if __name__ == '__main__':
    path = sys.argv[1]; bbox = tuple(int(v) for v in sys.argv[2].split(',')); p0 = float(sys.argv[3]); K = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    im = Image.open(path).convert('RGB'); tmp = os.path.join(SP, 'out', 'peg_tmp.png'); im.save(tmp)
    rot, cx, cy, p, ang, arr = F.fit(tmp, bbox, p0, spread=0.12, angles=np.arange(-3, 3.1, 0.5), step=0.5, ring=(0.18, 0.42))
    F.check(rot, cx, cy, os.path.join(SP, 'out', 'peg_check.png'), bbox, scale=2.2)
    a = np.array(arr)[..., :3].astype(float)
    print('passo %.2f x %.2f ang %.1f grade %dx%d' % (p[0], p[1], ang, a.shape[1], a.shape[0]))
    np.save(os.path.join(SP, 'out', 'peg_cells.npy'), a)
