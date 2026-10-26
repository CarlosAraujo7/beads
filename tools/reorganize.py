"""Reorganiza o templates.js por franquia (uma vez; veja tools/franchises.py).

    python tools/reorganize.py --dry     # mostra como ficaria (contagem por categoria e o que vai para "Outros")
    python tools/reorganize.py           # grava (cópia de segurança automática em tools/backups/)

Regras: cada template vai para a categoria da franquia (NAME_MAP/GROUP_MAP); a série (group) passa a ser o nome da categoria;
o que não foi identificado vai para "Outros" mantendo a série antiga como subgrupo. As categorias genéricas do padrão
(Animes e mangás, Jogos, Super-heróis…) ficam escondidas (dá para restaurar em Organizar categorias). Desenhos, nomes e
exclusões NÃO mudam.
"""
import os, sys, json, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from collections import Counter, OrderedDict
import tplfile, franchises as F

ap = argparse.ArgumentParser()
ap.add_argument('--dry', action='store_true')
ap.add_argument('--templates', default=os.path.join(os.path.dirname(HERE), 'templates.js'))
a = ap.parse_args()

d = tplfile.parse(a.templates)
items = d['items']
before = {t['id']: (t['name'], t['rows']) for t in items}
cnt = Counter(); outros = OrderedDict()
for t in items:
    c = F.target(t['name'], t['group'])
    if c == 'other':
        outros.setdefault(t['group'], []).append(t['name'])
    else:
        t['group'] = F.NAME_BY_ID[c]
    t['cat'] = c; cnt[c] += 1

cfg = d['cfg'] or {'order': [], 'names': {}, 'icons': {}, 'custom': [], 'hidden': []}
used = [c for c, _, _ in F.CATEGORIES if cnt[c] or c == 'earrings']
custom = [{'id': i, 'name': n, 'icon': ic} for i, n, ic in F.CATEGORIES if i in used and i != 'earrings']
keep = [c for c in cfg.get('custom', []) if c['id'] not in {x['id'] for x in custom}]
cfg['custom'] = custom + keep
cfg['order'] = [c for c in used] + ['other']
cfg['names'] = {k: v for k, v in cfg.get('names', {}).items() if k in ('other', 'earrings')}
cfg['icons'] = {}
cfg['hidden'] = ['anime', 'games', 'heroes', 'cinema', 'toons', 'animals', 'symbols', 'claude']

print('categorias (ordem da galeria):')
for c in used + ['other']:
    print('  %-26s %3d' % (F.NAME_BY_ID.get(c, 'Outros'), cnt[c]))
print('\nficam em "Outros" (%d), por série antiga:' % cnt['other'])
for g, ns in outros.items(): print('  [%s] %s' % (g, ' | '.join(ns)))
assert {t['id']: (t['name'], t['rows']) for t in items} == before   # nada de nome/desenho mudou
if a.dry: print('\n(--dry: nada foi gravado)')
else:
    tplfile.write(a.templates, d['legend'], cfg, items, d.get('removed'))
    print('\ngravado:', a.templates, '(cópia de segurança em tools/backups/)')
