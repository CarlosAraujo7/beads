"""Folhas de conferência de COR: imagem original | molde (como está em data/finalN_120.json), lado a lado, para revisar rostos/peles/cores de uma remessa.

uso:  python tools/cmp_src.py N [--big] [filtro...]     (N = nº da remessa; usa rN_exfinal.CFG e data/final{N+2}_120.json ou final{N+2}_multi_120.json com --big)
saída: tools/out/cmp_N_k.png (12 pares por folha)
"""
import os, sys, json, importlib, tempfile
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
os.environ.setdefault('BEADPAL', '120')
from PIL import Image, ImageDraw
from flat import render_flat
from palette import sfx

args = [a for a in sys.argv[1:]]
N = int(args.pop(0)); big = '--big' in args; flt = [a for a in args if not a.startswith('--')]
mod = importlib.import_module(f'r{N}_exfinal')
dat = json.load(open(os.path.join(SP, 'data', f'final{N + 2}' + ('_multi' if big else '') + sfx() + '.json'), encoding='utf-8'))
rows_by = {it[0]: it[2] for it in dat}
H = 230
pairs = []
for n, g, idx, kw, pl, *_ in mod.CFG:
    nn = n + (' (grande)' if big else '')
    if nn not in rows_by or (flt and not any(f in nn for f in flt)): continue
    im = Image.open(mod.FILES[idx]).convert('RGBA'); bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg.convert('RGB')
    if kw.get('box'): im = im.crop(kw['box'])
    im = im.resize((max(1, round(im.width * H / im.height)), H))
    rows = rows_by[nn]; sc = max(1, round(H / (len(rows) + 3)))
    tmp = os.path.join(tempfile.gettempdir(), 'cmp_tmp.png'); render_flat([('', rows)], tmp, scale=sc, W=len(rows[0]) * sc + 48)
    br = Image.open(tmp).convert('RGB'); br = br.crop((24, 40, 24 + len(rows[0]) * sc, 40 + len(rows) * sc))
    br = br.resize((max(1, round(br.width * H / br.height)), H), Image.NEAREST)
    pairs.append((nn, idx, im, br))
W = 1900; pad = 12; per = 12
for k in range(0, len(pairs), per):
    chunk = pairs[k:k + per]
    x = pad; y = pad; rowh = 0; pos = []
    for nn, idx, im, br in chunk:
        w = im.width + br.width + 6
        if x + w + pad > W: x = pad; y += rowh + 26; rowh = 0
        pos.append((x, y)); x += w + pad; rowh = max(rowh, H + 14)
    sheet = Image.new('RGB', (W, y + rowh + 26), (60, 60, 66)); d = ImageDraw.Draw(sheet)
    for (nn, idx, im, br), (x, y) in zip(chunk, pos):
        d.text((x, y), f'{idx}: {nn}'[:60].encode('ascii', 'replace').decode(), fill=(255, 255, 0))
        sheet.paste(im, (x, y + 14)); sheet.paste(br, (x + im.width + 6, y + 14))
    out = os.path.join(SP, 'out', f'cmp_{N}{"b" if big else ""}_{k // per}.png'); sheet.save(out); print(out)
