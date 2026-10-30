"""empilha folhas de rosto de vários moldes numa imagem: python tools/faces_pair.py nome id:r0:r1:c0:c1 id:... [cell]"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
from PIL import Image
name = sys.argv[1]; specs = [a for a in sys.argv[2:] if ':' in a]; cell = next((a for a in sys.argv[2:] if a.isdigit()), '26')
ims = []
for sp in specs:
    i, r0, r1, c0, c1 = sp.split(':')
    subprocess.run([sys.executable, os.path.join(HERE, 'faces_sheets.py'), i, r0, r1, c0, c1, cell], check=True, stdout=subprocess.DEVNULL, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    ims.append(Image.open(os.path.join(HERE, 'out', 'ft_%s.png' % i[:18])).copy())
W = max(i.width for i in ims); H = sum(i.height for i in ims)
out = Image.new('RGB', (W, H), (40, 40, 44)); y = 0
for i in ims: out.paste(i, (0, y)); y += i.height
out.save(os.path.join(HERE, 'out', 'fp_%s.png' % name)); print(out.size)
