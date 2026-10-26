import sys, os, json
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import r6, outline as O
from flat import render_flat
idxs = [int(a) for a in sys.argv[2:]]; tag = sys.argv[1]
items = []
for i in idxs:
    try:
        r = r6.exact6(i); items.append((f'{i} {len(r[0])}x{len(r)} p{len(O.components(r))}', r)); print(i, len(r[0]), len(r))
    except Exception as e: print(i, 'ERRO', repr(e))
render_flat(items, os.path.join(OUT, f'r6_try_{tag}.png'), scale=6, W=1900)
