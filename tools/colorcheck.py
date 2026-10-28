"""Diagnóstico de COR de uma remessa de ilustrações (illus.convert4): para cada molde de 1 placa compara a cor MÉDIA ORIGINAL de cada conta com a cor da
letra escolhida (ΔE2000) e aponta
  - letras com desvio grande (cor errada),
  - contas de cor de PELE/clara-quente na imagem que viraram letra que não é de pele (branco, cinza, marrom...),
  - contas que ficaram mais saturadas/escuras que a imagem (efeito do realce).

uso:  python tools/colorcheck.py N [filtro...]     (N = remessa; usa rN_exfinal.CFG, só a versão de 1 placa)
"""
import os, sys, importlib, colorsys
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
os.environ.setdefault('BEADPAL', '120')
import numpy as np
import r5, illus, img2tpl as T
from palette import HEX_BY_LETTER, ALL

N = int(sys.argv[1]); flt = sys.argv[2:]
mod = importlib.import_module(f'r{N}_exfinal')
HEX = {l: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) if h.startswith('#') else tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for l, h in HEX_BY_LETTER.items()}
CODE = {c['letter']: c['code'] for c in ALL}
SKIN = {c['letter'] for c in ALL if c['code'] in r5._SKIN_CODES}


def lab(rgb): return np.array(T.rgb2lab(np.array(rgb, float)))
def de(a, b): return float(r5._de2000(lab(a), lab(b)[None, :])[0])


for n, g, idx, kw, pl, *_ in mod.CFG:
    if flt and not any(f in n for f in flt): continue
    r5.SKIN_ON = r5.skin_for(n, g)
    t = {}
    a = dict(mod.DK); a.update({k: v for k, v in kw.items() if k not in ('post', 'largest')})
    try: illus.convert4(mod.FILES[idx], plates=None, trace=t, **a)
    except Exception as e: print('ERRO', n, e); continue
    raw, m, size = t['raw'], t['mask'], t['size']
    t2 = {}
    illus._cells(raw, m, size, over=a.get('over', 8), dark_L=a.get('dark_L', 30.0), dark_frac=a.get('dark_frac', 0.22), cover=a.get('cover', 0.5), trace=t2)
    rows0 = t['rows0']; nfg, ndk = t['nfg'], t['ndk']; df = a.get('dark_frac', 0.22)
    per = {}; skin_bad = []; pale_w = 0; skin_cells = 0
    for y, row in enumerate(rows0):
        for x, ch in enumerate(row):
            if ch == '.': continue
            dark = ndk[y, x] >= df * nfg[y, x] or nfg[y, x] - ndk[y, x] < 1
            src = t2['dk'][y, x] if dark else t2['lit'][y, x]
            d = de(src, HEX[ch]); per.setdefault(ch, []).append((d, src))
            if dark: continue
            h_, s_, v_ = colorsys.rgb_to_hsv(*(np.array(src) / 255)); h_ *= 360
            if 14 <= h_ <= 58 and 0.06 <= s_ <= 0.5 and v_ >= 0.68:
                skin_cells += 1
                if ch not in SKIN: skin_bad.append((ch, tuple(int(v) for v in src)))
    tot = sum(len(v) for v in per.values())
    print(f'\n== {n}  ({tot} contas, pele/clara-quente na origem: {skin_cells}, fora das letras de pele: {len(skin_bad)})')
    if skin_bad:
        from collections import Counter
        cn = Counter(c for c, _ in skin_bad)
        ex = {c: [s for cc, s in skin_bad if cc == c][:1][0] for c in cn}
        print('   pele→ ' + ', '.join(f'{c}({CODE[c]} {HEX[c]}) x{k} ex.{ex[c]}' for c, k in cn.most_common(4)))
    bad = sorted(((np.mean([d for d, _ in v]), l, len(v), np.mean([s for _, s in v], axis=0)) for l, v in per.items() if len(v) >= 4), reverse=True)[:3]
    for dm, l, k, ms in bad:
        if dm >= 14: print(f'   desvio {dm:4.1f}  {l}({CODE[l]}) x{k}: origem média {tuple(int(v) for v in ms)} -> paleta {HEX[l]}')
