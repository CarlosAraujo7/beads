"""Gera as versões "<nome> (120 cores)" dos moldes de 24 cores do catálogo, refazendo a conversão da imagem de origem com as 120 cores.

Os moldes de 24 cores NÃO são alterados: cada um ganha uma cópia ao lado, na mesma categoria.

Fontes (todas convertidas com BEADPAL=120 pelos mesmos scripts de sempre):
  * remessas 5-12 e levantamento "Outros": data/finalN_120.json / final_outros_120.json (mesmo nome do molde);
  * remessas 1-4 (pipeline antigo, já retocadas à mão): data/old120.json, feito por tools/r_old120.py (imagem -> conversão exata em 120 cores).

Regras:
  * só entra se o molde de 24 cores do catálogo ainda é IGUAL à conversão original (se você ajustou o desenho no app, a versão 120 viria da
    imagem sem os seus ajustes: esses ficam de fora e saem listados);
  * não entra se a versão de 120 cores é praticamente igual (mudou 3% ou menos das contas);
  * as "(1 placa)" não ganham versão (a de 1 placa da versão 120 é gerada por make_1placa.py).

uso:  python tools/make_120.py [--dry]     -> grava tools/data/final_120cores.json; depois: python tools/add_templates.py tools/data/final_120cores.json
"""
import os, sys, json
SP = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(SP)
sys.path.insert(0, SP)
import tplfile
from palette import LETTERS24

cat = tplfile.parse(os.path.join(ROOT, 'templates.js'))['items']
have = {t['name'] for t in cat}
src24, src120 = {}, {}
for k in [7, 8, 9, 10, 11, 12, 13, 14]:
    for n, g, r in json.load(open(os.path.join(SP, 'data', f'final{k}.json'), encoding='utf-8')): src24[n] = r
    for n, g, r in json.load(open(os.path.join(SP, 'data', f'final{k}_120.json'), encoding='utf-8')): src120[n] = r
for n, g, r in json.load(open(os.path.join(SP, 'data', 'final_outros.json'), encoding='utf-8')): src24.setdefault(n, r)
for n, g, r in json.load(open(os.path.join(SP, 'data', 'final_outros_120.json'), encoding='utf-8')): src120.setdefault(n, r)
old = {}
p = os.path.join(SP, 'data', 'old120.json')
if os.path.exists(p): old = json.load(open(p, encoding='utf-8'))      # {id do molde: rows120} (r_old120.py: recolore o molde com a conversão de 120 cores da imagem)

used_names = set()
out = []; skipped = {'editado': [], 'igual': [], 'sem_fonte': []}; made = 0
for t in cat:
    n = t['name']
    if n.endswith('(1 placa)') or n.endswith('(120 cores)'): continue
    if any(c not in LETTERS24 + '.' for r in t['rows'] for c in r): continue        # já é de 120 cores (remessa 13)
    new_name = f'{n} (120 cores)'
    if new_name in have: continue
    if new_name in used_names:       # mesmo nome repetido no catálogo (ex.: 3 "Velha turbo")
        k = 2
        while f'{n} (versão {k}) (120 cores)' in used_names or f'{n} (versão {k}) (120 cores)' in have: k += 1
        new_name = f'{n} (versão {k}) (120 cores)'
    used_names.add(new_name)
    rows120 = None
    if n in src120:
        if src24.get(n) != t['rows']: skipped['editado'].append(n); continue
        rows120 = src120[n]
    elif t['id'] in old:
        rows120 = old[t['id']]
    else:
        skipped['sem_fonte'].append(n); continue
    a = t['rows']
    if len(a) == len(rows120) and all(len(x) == len(y) for x, y in zip(a, rows120)):
        diff = sum(1 for x, y in zip(a, rows120) for c, d in zip(x, y) if c != d); tot = sum(c != '.' for x in a for c in x)
        if diff <= 0.03 * max(1, tot): skipped['igual'].append(n); continue
    out.append((new_name, t['group'], rows120)); made += 1
print(made, 'versões de 120 cores')
for k, v in skipped.items(): print(f'{k}: {len(v)}', v if k != 'sem_fonte' else '')
if '--dry' not in sys.argv:
    json.dump(out, open(os.path.join(SP, 'data', 'final_120cores.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(skipped, open(os.path.join(SP, 'out', 'make120_skipped.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
