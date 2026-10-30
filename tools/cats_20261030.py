"""Pedido do usuário (2026-10-30): categorias Ryukendo, Paisagens, Horizon e The Ancient Magus' Bride, com os moldes que estavam em "Outros". Só muda categoria (e o nome do Elias); não mexe em desenho.
Pode rodar de novo sem efeito. Usa o templates.js ATUAL; id que não estiver mais lá é avisado e pulado.  python tools/cats_20261030.py [--dry]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tplfile

TPL = os.path.join(os.path.dirname(HERE), 'templates.js')
CATS = {
    'ryukendo': ('Ryukendo', 'cHeroes'),
    'paisagens': ('Paisagens', 'cSun'),
    'horizon': ('Horizon', 'cGames'),
    'the-ancient-magus-bride': ("The Ancient Magus' Bride", 'cBook'),
}
MOVES = {
    'heroi-de-armadura-vermelha-e-dourada-chibi': 'ryukendo', 'heroi-de-armadura-vermelha-e-branca-chibi': 'ryukendo',
    'heroi-de-armadura-azul-e-dourada-chibi': 'ryukendo', 'heroi-de-armadura-azul-e-dourada-com-espada-chibi': 'ryukendo',
    'heroi-de-armadura-vermelha-e-dourada-chibi-grande': 'ryukendo', 'heroi-de-armadura-vermelha-e-branca-chibi-grande': 'ryukendo',
    'heroi-de-armadura-azul-e-dourada-chibi-grande': 'ryukendo', 'heroi-de-armadura-azul-e-dourada-com-espada-chibi-grande': 'ryukendo',
    'heroi-de-armadura-azul-e-dourada-com-bola-grande': 'ryukendo',
    'praia-com-tartaruga-pixel': 'paisagens', 'ceu-dividido-noite-e-dia-pixel': 'paisagens',
    'criatura-robotica-com-coracao-pixel': 'horizon',
    'esqueleto-de-manto-azul-pixel': 'the-ancient-magus-bride',
}
RENAME = {'esqueleto-de-manto-azul-pixel': 'Elias Ainsworth (pixel)'}

d = tplfile.parse(TPL); cfg = d['cfg']; by = {t['id']: t for t in d['items']}
names = {t['name'] for t in d['items']}
for cid, (name, icon) in CATS.items():
    if any(c['id'] == cid for c in cfg['custom']): continue
    cfg['custom'].append({'id': cid, 'name': name, 'icon': icon})
    order = [x for x in cfg.get('order', []) if x not in (cid, 'other')]
    at = order.index('earrings') if 'earrings' in order else len(order)
    cfg['order'] = order[:at] + [cid] + order[at:] + ['other']
    print('categoria criada:', name)
for i, cid in MOVES.items():
    if i not in by: print('NÃO ESTÁ NO CATÁLOGO, pulei:', i); continue
    t = by[i]; t['cat'] = cid; t['group'] = CATS[cid][0]
    print('%-60s -> %s' % (t['name'], CATS[cid][0]))
for i, n in RENAME.items():
    if i in by and by[i]['name'] != n:
        assert n not in names, n
        print('renomeado:', by[i]['name'], '->', n); by[i]['name'] = n
print('moldes:', len(d['items']), '| ainda em Outros:', [t['name'] for t in d['items'] if t['cat'] == 'other'])
if '--dry' in sys.argv: print('(--dry: nada foi gravado)')
else: tplfile.write(TPL, d['legend'], cfg, d['items'], d.get('removed')); print('gravado')
