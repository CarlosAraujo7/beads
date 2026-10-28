"""Conta BURACOS nos moldes: contas vazias dentro da figura (não ligadas por vazias à borda do molde) e 'vazamentos' (vazias cercadas por figura em 3 lados).
uso: python tools/holes.py [filtro...]   -> lista os moldes do catálogo com mais buracos (só 1 placa; use --all para incluir os grandes)"""
import os, sys
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import numpy as np, cv2, tplfile
ROOT = os.path.dirname(SP)
def holes(rows):
    g = np.array([[c != '.' for c in r] for r in rows], np.uint8); h, w = g.shape
    pad = np.pad(1 - g, 1, constant_values=1)                      # vazias + moldura de "fora"
    n, lab = cv2.connectedComponents(pad.astype(np.uint8), connectivity=4)
    out = lab[0, 0]; enclosed = int(((pad == 1) & (lab != out)).sum())
    # vazamento: vazia com figura em 3 dos 4 lados (canal de 1 conta que entra na figura)
    leak = 0
    for y in range(h):
        for x in range(w):
            if g[y, x]: continue
            nb = [g[y + dy, x + dx] if 0 <= y + dy < h and 0 <= x + dx < w else 0 for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if sum(nb) >= 3: leak += 1
    return enclosed, leak, int(g.sum())
if __name__ == '__main__':
    allf = '--all' in sys.argv; flt = [a for a in sys.argv[1:] if not a.startswith('--')]
    d = tplfile.parse(os.path.join(ROOT, 'templates.js')); res = []
    for t in d['items']:
        if flt and not any(f in t['name'] for f in flt): continue
        if not allf and (len(t['rows'][0]) > 50 or len(t['rows']) > 50): continue
        e, l, a = holes(t['rows']); res.append(((e + l) / max(a, 1), e, l, a, t['name']))
    res.sort(reverse=True)
    for sc, e, l, a, n in res[:int(os.environ.get('TOP', 40))]: print(f'{sc*100:5.1f}%  enclosed={e:3d} leak={l:3d} area={a:4d}  {n}')
