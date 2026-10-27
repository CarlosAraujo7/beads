"""Compara cada molde de 24 cores do catálogo com a sua versão de 120 cores (mesmas dimensões), conta a conta, e lista os que mudaram de forma
suspeita: contas que ficaram bem mais ESCURAS, ou de tom bem diferente (matiz), ou que viraram cinza/oliva sendo que antes eram pele/bege.
Serve para achar "pele que virou marrom escuro ou cinza" sem olhar 300 imagens; depois se olha só os apontados.

uso:  python tools/audit120.py [limite=0.12]      (lê tools/data/final*_120.json, final_outros_120.json e old120.json)
"""
import os, sys, json, glob, colorsys
import numpy as np
SP = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(SP)
sys.path.insert(0, SP)
import tplfile, r5
from palette import ALL
from make_palette import rgb2lab, h2rgb

LAB = {c['letter']: rgb2lab(h2rgb(c['hex'])) for c in ALL}
CODE = {c['letter']: c['code'] for c in ALL}
HSV = {c['letter']: colorsys.rgb_to_hsv(*(np.array(h2rgb(c['hex'])) / 255)) for c in ALL}
limit = float(sys.argv[1]) if len(sys.argv) > 1 else 0.12
cat = tplfile.parse(os.path.join(SP, 'backups', 'pre-finalize-120.js'))['items']
by_name = {t['name']: t for t in cat}; by_id = {t['id']: t for t in cat}
new = {}
for f in sorted(glob.glob(os.path.join(SP, 'data', 'final*_120.json'))):
    for n, g, r in json.load(open(f, encoding='utf-8')): new.setdefault(n, r)
old = json.load(open(os.path.join(SP, 'data', 'old120.json'), encoding='utf-8')) if os.path.exists(os.path.join(SP, 'data', 'old120.json')) else {}
pairs = [(n, by_name[n]['rows'], r) for n, r in new.items() if n in by_name]
pairs += [(by_id[i]['name'], by_id[i]['rows'], r) for i, r in old.items() if i in by_id]
out = []
for n, a, b in pairs:
    if len(a) != len(b) or any(len(x) != len(y) for x, y in zip(a, b)): continue
    tot = 0; dark = 0; hue = 0; gray = 0
    for ra, rb in zip(a, b):
        for ca, cb in zip(ra, rb):
            if ca == '.' or cb == '.' or ca == cb: continue
            tot += 1
            la, lb = LAB[ca], LAB[cb]
            ha, sa, va = HSV[ca]; hb, sb, vb = HSV[cb]
            if lb[0] < la[0] - 14: dark += 1
            dh = abs(ha - hb) * 360; dh = min(dh, 360 - dh)
            if sa > 0.12 and sb > 0.12 and dh > 25: hue += 1
            if sa > 0.14 and sb < 0.10 and abs(lb[0] - la[0]) > 4: gray += 1
    n_all = sum(c != '.' for r in a for c in r)
    bad = (dark + hue + gray) / max(1, n_all)
    if bad >= limit: out.append((bad, n, n_all, dark, hue, gray))
out.sort(reverse=True)
for b, n, t, d, h, g in out: print(f'{b:.2f} {n[:46]:48s} contas={t:4d} escureceu={d:4d} matiz={h:4d} cinza={g:4d}')
print(len(out), 'suspeitos de', len(pairs))
