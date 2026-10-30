"""folha de visão geral: para cada id (fonte | atual | reconversão com dark_L/dark_frac mais exigentes), 3-4 moldes por imagem. python tools/faces_overview.py nome_da_folha id1 id2 ..."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.environ.setdefault('BEADPAL', '120')
import numpy as np, tplfile, facetools as F, illus, r5, illus5
from faces_src import S
from flat import render_flat
from PIL import Image
name, ids = sys.argv[1], sys.argv[2:]
d = tplfile.parse(os.path.join(os.path.dirname(HERE), 'templates.js')); by = {i['id']: i for i in d['items']}
cols = []
for i in ids:
    rem, idx, kw = S[i]; cur = by[i]['rows']
    r5.SKIN_ON = True
    a = dict(K=18); a.update({k: v for k, v in kw.items() if k in ('thr', 'bg', 'tol', 'pale_skin', 'peel', 'dark_frac', 'box', 'white_outside', 'refs', 'seal')})
    new = illus5.convert5(F.src_path(rem, idx), **a)
    raw = F.src_raw(rem, idx); fg = F.fg_mask(raw, thr=a.get('thr', 205)); ys, xs = np.nonzero(fg)
    sm = Image.fromarray(raw).crop((max(0, xs.min() - 4), max(0, ys.min() - 4), min(raw.shape[1], xs.max() + 5), min(raw.shape[0], ys.max() + 5)))
    sc = 7; h = max(len(cur), len(new)) * sc + 18
    sm = sm.resize((max(1, int(sm.width * h / sm.height)), h), Image.LANCZOS)
    tmp = os.path.join(HERE, 'out', '_ov.png'); render_flat([('ATUAL ' + i[:20], cur), ('NOVO', new)], tmp, scale=sc, W=(len(cur[0]) + len(new[0])) * sc + 90)
    im = Image.open(tmp); c = Image.new('RGB', (sm.width + im.width + 10, max(h, im.height)), (60, 60, 66)); c.paste(sm, (2, 18)); c.paste(im, (sm.width + 8, 0)); cols.append(c)
W = max(c.width for c in cols); out = Image.new('RGB', (W * 2 + 10, sum(c.height for c in cols[0::2]) if False else 10), (60, 60, 66))
# empilha 2 por linha
rowsimg = []
for k in range(0, len(cols), 2):
    pair = cols[k:k + 2]; w = sum(p.width for p in pair) + 10; hh = max(p.height for p in pair)
    r = Image.new('RGB', (w, hh), (60, 60, 66)); x = 0
    for p in pair: r.paste(p, (x, 0)); x += p.width + 10
    rowsimg.append(r)
Wd = max(r.width for r in rowsimg); Hd = sum(r.height for r in rowsimg) + 6 * len(rowsimg)
img = Image.new('RGB', (Wd, Hd), (60, 60, 66)); y = 0
for r in rowsimg: img.paste(r, (0, y)); y += r.height + 6
img.save(os.path.join(HERE, 'out', 'ov_%s.png' % name)); print(img.size)
