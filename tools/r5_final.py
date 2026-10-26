import sys, os, json, colorsys
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import numpy as np
import r5, r5_build, outline as O
from flat import render_flat

def grayish(c):
    h, s, v = colorsys.rgb_to_hsv(*(np.array(c) / 255.0)); return s < 0.07 and v > 0.72

def pokeball_post(rows):
    r1 = [''.join(('w' if c in 'il' else c) if y >= 22 else c for c in r) for y, r in enumerate(rows)]
    return O.despeckle_colors(O.despeckle_colors(r1))

EXTRA = [
 ('Haku (Viagem de Chihiro)', 'Studio Ghibli', lambda: r5.pat_flood(0, thr=232, drop='x', post=r5.largest)),
 ('Haku (versão pastel)', 'Studio Ghibli', lambda: r5.pat_flood(19, thr=215, drop='x', post=r5.largest)),
 ('Charmander esqueleto', 'Pokémon', lambda: r5.photo(24, 24)[0]),
 ('Pikachu de Mewtwo', 'Pokémon', lambda: r5.photo(37, 28, mp={'q': 'i', 's': 'i'})[0]),
 ('Poké Ball (peça)', 'Pokémon', lambda: r5.photo(40, 28, post=pokeball_post)[0]),
 ('Dragonite', 'Pokémon', lambda: r5.photo(28, 17, bgfn=grayish, mp={'q': 's'}, spread=0.12)[0]),
 ('Mario (peça)', 'Mario', lambda: r5.photo(36, 28)[0]),
 ('Moeda do Mario', 'Mario', lambda: r5.photo(25, 38)[0]),
]
if __name__ == '__main__':
    out = []; items = []
    for n, g, fn in r5_build.CFG + EXTRA:
        try:
            r = fn(); out.append((n, g, r)); items.append((f'{n[:24]} {len(r[0])}x{len(r)} p{len(O.components(r))}'.encode('ascii', 'replace').decode(), r))
        except Exception as e:
            print('ERRO', n, repr(e))
    json.dump(out, open(os.path.join(OUT, 'final7_firstpass.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(out), 'templates')
    for k in range(0, len(items), 10):
        render_flat(items[k:k + 10], os.path.join(OUT, f'r5_f_{k // 10}.png'), scale=8, W=1900)
