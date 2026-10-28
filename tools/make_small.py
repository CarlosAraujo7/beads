"""Versões PEQUENAS (~600 contas) dos moldes do catálogo: "<nome> (pequeno)".

Pedido do usuário (2026-10-28): o molde de 394 contas (Okarun) ficou perfeito na placa; a tela engana e 2000+ contas não são necessárias. Moldes de até ~600 contas são
rápidos de montar e ficam bonitos. A galeria ganhou a aba "Até ~600 contas", que mostra SÓ os moldes com "(pequeno" no nome (nada sai das outras abas); cada molde com mais de 650 contas (SMALL_MAX) ganha um irmão pequeno.

Método: shrink.py ('bias': o contorno escuro pesa mais, o traço de 1 conta sobrevive) a partir da MAIOR versão do mesmo desenho ("<nome> (grande)" se existir,
senão o próprio molde), com o tamanho escolhido para dar ~550 contas (nunca mais que 620). Não mexe em nenhum molde existente.

uso:  python tools/make_small.py            -> data/final_small_120.json + prévias tools/out/small_k.png (nada é gravado no catálogo)
      python tools/make_small.py --apply    -> grava no templates.js, cada "(pequeno)" logo DEPOIS do molde de origem (o de 1 placa) (cópia de segurança em tools/backups/)
      --skip "nome1|nome2"  (nomes de base a pular);  --target 550
"""
import os, sys, json, shutil, datetime
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
ROOT = os.path.dirname(SP)
import tplfile, shrink, loose
from flat import render_flat

SMALL_MAX = 650            # igual ao do index.html: até aqui o molde cai na aba "Até ~600 contas"
args = sys.argv[1:]
target = int(args[args.index('--target') + 1]) if '--target' in args else 550
skip = set((args[args.index('--skip') + 1] if '--skip' in args else '').split('|')) - {''}
TPL = os.path.join(ROOT, 'templates.js')


def beads(r): return sum(1 for row in r for c in row if c != '.')


def to_target(rows):
    best = None
    for size in range(10, 61):
        s = shrink.shrink(rows, size, 'bias', empty_at=0.5)
        b = beads(s)
        if b <= 620 and (best is None or abs(b - target) < abs(best[0] - target)): best = (b, s)
        if b > target * 1.4: break
    if not best: return None
    return loose.fill_pinholes(loose.fix_loose(best[1]))[0]      # a redução cria contas soltas e buraquinhos: sem eles (regra do usuário)


d = tplfile.parse(TPL); items = d['items']; byname = {t['name']: t for t in items}; removed = set(d.get('removed') or [])
out = []; skipped = []
for t in items:
    n = t['name']
    if n.endswith('(grande)') or n.endswith('(pequeno)') or n in skip: continue
    if beads(t['rows']) <= SMALL_MAX: continue
    nn = n + ' (pequeno)'
    if nn in byname or nn in removed: continue
    big = byname.get(n + ' (grande)')
    src = big['rows'] if big else t['rows']
    rows = to_target(src)
    if not rows or min(len(rows[0]), len(rows)) < 8 or beads(rows) < 250: skipped.append(n); continue
    out.append((nn, t['group'], rows, {'plates': 1}, n))
print(len(out), 'versões pequenas;', len(skipped), 'puladas:', skipped[:20])
bs = [beads(o[2]) for o in out]
if bs: print('contas: mín %d  média %d  máx %d' % (min(bs), sum(bs) / len(bs), max(bs)))
json.dump(out, open(os.path.join(SP, 'data', 'final_small_120.json'), 'w', encoding='utf-8'), ensure_ascii=False)
if '--apply' not in args:
    its = [(f'{o[0][:22]} {beads(o[2])}'.encode('ascii', 'replace').decode(), o[2]) for o in out]
    for k in range(0, len(its), 60):
        render_flat(its[k:k + 60], os.path.join(SP, 'out', f'small_{k // 60}.png'), scale=3, W=1900)
    sys.exit(0)
# --apply: cada pequeno entra logo DEPOIS do molde de origem (a versão de 1 placa)
ids = {t['id'] for t in items}; names = set(byname)
bk = os.path.join(SP, 'backups'); os.makedirs(bk, exist_ok=True)
shutil.copy(TPL, os.path.join(bk, 'templates-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.js'))
new_items = []; placed = 0
after = {}
for nn, g, rows, o, base in out: after.setdefault(base, []).append((nn, rows))
for t in items:
    new_items.append(t)
    key = t['name']
    if key in after:
        for nn, rows in after.pop(key):
            base_id = tplfile.slug(nn); i = base_id; k = 2
            while i in ids: i = '%s-%d' % (base_id, k); k += 1
            ids.add(i); names.add(nn)
            new_items.append({'id': i, 'cat': byname[key]['cat'], 'group': byname[key]['group'], 'name': nn, 'rows': rows}); placed += 1
tplfile.write(TPL, d['legend'], d['cfg'], new_items, d.get('removed'))
print('gravados', placed, 'moldes pequenos;', 'sem lugar:', list(after)[:5], '| total', len(new_items))
