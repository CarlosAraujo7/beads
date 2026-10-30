"""folhas de rosto (fonte | convert5) para desenhar os olhos: python tools/faces_sheets.py id r0 r1 c0 c1 [cell]  (usa tools/faces_src.py e os kwargs de FIX[id]['conv5'] se existir)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.environ.setdefault('BEADPAL', '120')
import tplfile, facetools as F, illus5, r5
from faces_src import S
i = sys.argv[1]; r0, r1, c0, c1 = map(int, sys.argv[2:6]); cell = int(sys.argv[6]) if len(sys.argv) > 6 else 30
try:
    from faces_fix import FIX
    kw = dict(FIX.get(i, {}).get('conv5', {}))
except Exception: kw = {}
rem, idx, kw0 = S[i]
a = dict(K=18); a.update({k: v for k, v in kw0.items() if k in ('thr', 'bg', 'tol', 'pale_skin', 'peel', 'dark_frac', 'box', 'white_outside', 'refs', 'seal')}); a.update(kw)
r5.SKIN_ON = True
rows = illus5.convert5(F.src_path(rem, idx, ) if False else F.src_path(rem, idx), **a)
raw = F.src_raw(rem, idx, a.get('box'))
g = F.align(raw, rows, thr=a.get('thr', 205), bg=a.get('bg', 'auto'), tol=a.get('tol', 45), verbose=False)
F.sheet(raw, rows, g, (r0, min(r1, len(rows)), c0, min(c1, len(rows[0]))), os.path.join(HERE, 'out', 'ft_%s.png' % i[:18]), cell=cell, title='%s %dx%d' % (i, len(rows[0]), len(rows)))
print(len(rows[0]), len(rows))
