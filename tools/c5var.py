"""variantes de illus5.convert5 lado a lado: python tools/c5var.py nome remessa idx 'rótulo:k=v,k=v' ... [--cur id]  -> out/c5_<nome>.png (fonte | atual | variantes)"""
import os, sys, ast
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.environ.setdefault('BEADPAL', '120')
import numpy as np, tplfile, facetools as F, illus5, r5
from flat import render_flat
from PIL import Image
args = sys.argv[1:]; cur = None
if '--cur' in args: k = args.index('--cur'); cur = args[k + 1]; del args[k:k + 2]
name, rem, idx = args[0], int(args[1]), int(args[2]); specs = args[3:]
skin = True
items = []
if cur:
    by = {i['id']: i['rows'] for i in tplfile.parse(os.path.join(os.path.dirname(HERE), 'templates.js'))['items']}; items.append(('ATUAL', by[cur]))
for sp in specs:
    lab, _, kv = sp.partition(':'); kw = {}
    for p in [x for x in kv.split(',') if x]:
        a, b = p.split('='); kw[a] = ast.literal_eval(b)
    r5.SKIN_ON = kw.pop('skin', True)
    items.append((lab, illus5.convert5(F.src_path(rem, idx), **kw)))
sc = int(os.environ.get('SC', '8'))
tmp = os.path.join(HERE, 'out', '_c5.png'); render_flat(items, tmp, scale=sc, W=sum(len(r[1][0]) * sc + 26 for r in items) + 30)
raw = F.src_raw(rem, idx); fg = F.fg_mask(raw); ys, xs = np.nonzero(fg)
sm = Image.fromarray(raw).crop((max(0, xs.min() - 4), max(0, ys.min() - 4), min(raw.shape[1], xs.max() + 5), min(raw.shape[0], ys.max() + 5)))
h = max(len(r[1]) for r in items) * sc + 18; sm = sm.resize((max(1, int(sm.width * h / sm.height)), h), Image.LANCZOS)
im = Image.open(tmp); c = Image.new('RGB', (sm.width + im.width + 8, max(h + 24, im.height)), (60, 60, 66)); c.paste(sm, (2, 24)); c.paste(im, (sm.width + 8, 0))
c.save(os.path.join(HERE, 'out', 'c5_%s.png' % name)); print(c.size)
