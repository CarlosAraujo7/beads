"""Compara o molde que está NO CATÁLOGO (antigo) com a conversão nova (data/finalN_120.json) lado a lado e monta o arquivo `finalN_replace_120.json`
só com os moldes que (a) estão no catálogo, (b) NÃO foram editados pelo usuário (catálogo == `tools/out/old_rows/...json`, a versão que eu gravei) e (c) mudaram.

uso:  python tools/cmp_old_new.py N [--big] [--min 0.03]     N = remessa (14..18 -> final{N+2})
saída: tools/out/on_N[b]_k.png (antigo | novo, 10 pares por folha) e data/final{N+2}[_multi]_replace_120.json
"""
import os, sys, json
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
os.environ.setdefault('BEADPAL', '120')
import tplfile
from flat import render_flat

args = sys.argv[1:]; N = int(args.pop(0)); big = '--big' in args
mn = float(args[args.index('--min') + 1]) if '--min' in args else 0.03
suf = '_multi' if big else ''
new = json.load(open(os.path.join(SP, 'data', f'final{N + 2}{suf}_120.json'), encoding='utf-8'))
oldf = os.path.join(SP, 'out', 'old_rows', f'final{N + 2}{suf}_120.json')
old = {it[0]: it[2] for it in json.load(open(oldf, encoding='utf-8'))} if os.path.exists(oldf) else {}
cat = {t['name']: t for t in tplfile.parse(os.path.join(os.path.dirname(SP), 'templates.js'))['items']}


def diff(a, b):
    if len(a) != len(b) or len(a[0]) != len(b[0]): return 1.0
    tot = sum(1 for r in a for c in r if c != '.'); ch = sum(1 for ra, rb in zip(a, b) for x, y in zip(ra, rb) if x != y)
    return ch / max(tot, 1)


rep = []; items = []; ed = []; gone = []
for it in new:
    n, g, rows = it[0], it[1], it[2]
    if n not in cat: gone.append(n); continue
    cur = cat[n]['rows']
    if n in old and cur != old[n]: ed.append(n); continue          # o usuário mexeu: não troca
    d = diff(cur, rows)
    if d >= mn: rep.append((d, it))
rep.sort(key=lambda x: -x[0])
print(f'{len(new)} convertidos | {len(gone)} fora do catálogo (excluídos) | {len(ed)} editados pelo usuário (mantidos) | {len(rep)} mudaram >= {mn:.0%}')
if gone: print('  excluídos:', gone)
if ed: print('  editados:', ed)
for d, it in rep:
    t = it[0][:22].encode('ascii', 'replace').decode()
    items += [('A ' + t, cat[it[0]]['rows']), ('N ' + t, it[2])]
per = 10
for k in range(0, len(items), per * 2):
    render_flat(items[k:k + per * 2], os.path.join(SP, 'out', f'on_{N}{"b" if big else ""}_{k // (per * 2)}.png'), scale=3 if big else 4, W=1900)
json.dump([it for d, it in rep], open(os.path.join(SP, 'data', f'final{N + 2}{suf}_replace_120.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('lista:', ', '.join(f'{it[0][:28]} {d:.0%}' for d, it in rep[:60]))
