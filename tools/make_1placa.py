"""Gera, para cada molde do catálogo que NÃO cabe numa placa (50x50), uma versão extra reduzida chamada "<nome> (1 placa)",
na mesma categoria do original. O original continua intacto.

uso (na raiz do projeto):  python tools/make_1placa.py [--placa 50] [--sheet]
     -> grava tools/data/final_1placa.json  (formato dos finalN.json)  e, com --sheet, folhas de conferência em tools/out/
depois:  python tools/add_templates.py tools/data/final_1placa.json --dry   (e sem --dry para gravar)

Pode rodar de novo quando entrarem moldes grandes novos: os que já têm "(1 placa)" no catálogo são ignorados pelo add_templates.
A redução é feita por shrink.py (método 'bias', limiar 0,6): contornos escuros pesam mais para o traço de 1 conta sobreviver.
"""
import os, sys, json, math
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import tplfile, shrink as S, layoutsim as L

ROOT = os.path.dirname(SP)
plate = 50
if '--placa' in sys.argv: plate = int(sys.argv[sys.argv.index('--placa') + 1])
cat = tplfile.parse(os.path.join(ROOT, 'templates.js'))
have = {t['name'] for t in cat['items']}
out = []; shown = []
for t in cat['items']:
    rows = t['rows']; h = len(rows); w = max(len(r) for r in rows)
    if w <= plate and h <= plate: continue
    if t['name'].endswith('(1 placa)'): continue
    sh = S.shrink(rows, plate, 'bias', empty_at=0.6)
    name = f"{t['name']} (1 placa)"
    out.append((name, t['group'], sh))
    shown.append((t['name'], rows, name, sh))
    print(f"{t['name'][:46]:48s} {w:3d}x{h:3d} -> {len(sh[0]):2d}x{len(sh):2d}  {sum(c != '.' for r in sh for c in r):4d} contas  [{t['group']}]" + ('  (já existe no catálogo)' if name in have else ''))
json.dump(out, open(os.path.join(SP, 'data', 'final_1placa.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(out), 'versões de uma placa')
if '--sheet' in sys.argv:
    from PIL import Image, ImageDraw
    HEX = {k: '#' + v for k, v in L._HEX.items()}
    BG = (201, 195, 182); T = 250
    def render(rows):
        img = Image.new('RGB', (T, T), BG); d = ImageDraw.Draw(img)
        hh, ww = len(rows), max(len(r) for r in rows); cs = max(1, T // max(hh, ww))
        ox = (T - ww * cs) // 2; oy = (T - hh * cs) // 2
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c in HEX: d.ellipse([ox + x * cs, oy + y * cs, ox + (x + 1) * cs - 1, oy + (y + 1) * cs - 1], fill=HEX[c]) if cs >= 4 else d.rectangle([ox + x * cs, oy + y * cs, ox + (x + 1) * cs - 1, oy + (y + 1) * cs - 1], fill=HEX[c])
        return img
    per = 8
    for k in range(0, len(shown), per):
        chunk = shown[k:k + per]
        sheet = Image.new('RGB', (4 * (2 * T + 14) + 6, ((len(chunk) + 3) // 4) * (T + 20) + 6), (30, 30, 34)); d = ImageDraw.Draw(sheet)
        for j, (n0, r0, n1, r1) in enumerate(chunk):
            x = 4 + (j % 4) * (2 * T + 14); y = 4 + (j // 4) * (T + 20)
            d.text((x, y), f'{n0[:34]}  {max(len(r) for r in r0)}x{len(r0)} -> {len(r1[0])}x{len(r1)}', fill=(255, 255, 0))
            sheet.paste(render(r0), (x, y + 16)); sheet.paste(render(r1), (x + T + 4, y + 16))
        sheet.save(os.path.join(SP, 'out', f'1placa_{k // per}.png'))
