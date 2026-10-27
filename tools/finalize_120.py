"""POLÍTICA DO CATÁLOGO (pedido do usuário, 2026-10-27): só ficam moldes de **120 cores** e de **1 placa (<= 50x50)**. Nada de cópias.

Este script reconstrói o catálogo nesse formato EM CIMA do templates.js ATUAL (o que o usuário gravou pelo app vale: exclusões, categorias, ajustes de
desenho e a posição de cada molde ficam como estão). Cada "molde" (desenho) do catálogo atual é:
  * o molde base (sem sufixo) se ainda existe; ou, se o usuário excluiu o base e deixou a cópia "(120 cores)", essa cópia (que passa a ter o nome/id do base);
  * as cópias "(1 placa)" e as "(120 cores)" que sobram são descartadas (a de 1 placa é refeita).
As linhas do desenho final vêm da conversão de 120 cores MAIS RECENTE (finalN_120.json / final_outros_120.json pelo nome, só se o molde base do instantâneo
`backups/pre-finalize-120.js` era igual à conversão original de 24 cores; old120.json por id; manual120.json = trocas conferidas a olho). Se não há
conversão de 120 cores (desenho refeito à mão, foto, criação do Claude), o desenho atual fica (as 24 cores antigas são letras válidas das 120).
AJUSTES DO USUÁRIO são preservados: se o desenho atual difere do instantâneo (ele editou no app), as contas que ele mudou são aplicadas em cima da
conversão de 120 cores (mesmas dimensões) ou, se as dimensões mudaram, fica o desenho dele.
Moldes com mais de 50 em algum lado são reduzidos para 1 placa (shrink.py, método 'bias').

uso:  python tools/finalize_120.py [--dry]        (grava com cópia de segurança em tools/backups/)
"""
import os, sys, json
SP = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(SP)
sys.path.insert(0, SP)
import tplfile, shrink
from palette import LETTERS24

PLATE = 50
cat_path = os.path.join(ROOT, 'templates.js')
C = tplfile.parse(cat_path)
B = tplfile.parse(os.path.join(SP, 'backups', 'pre-finalize-120.js'))
is_copy = lambda n: n.endswith('(120 cores)') or n.endswith('(1 placa)')
only24 = lambda rows: all(c in LETTERS24 + '.' for r in rows for c in r)

# --- conversões de 120 cores mais recentes
src24, src120 = {}, {}
for k in [7, 8, 9, 10, 11, 12, 13, 14]:
    for n, g, r in json.load(open(os.path.join(SP, 'data', f'final{k}.json'), encoding='utf-8')): src24[n] = r
    for n, g, r in json.load(open(os.path.join(SP, 'data', f'final{k}_120.json'), encoding='utf-8')): src120[n] = r
for n, g, r in json.load(open(os.path.join(SP, 'data', 'final_outros.json'), encoding='utf-8')): src24.setdefault(n, r)
for n, g, r in json.load(open(os.path.join(SP, 'data', 'final_outros_120.json'), encoding='utf-8')): src120.setdefault(n, r)
r13 = {n: r for n, g, r in json.load(open(os.path.join(SP, 'data', 'final15_120.json'), encoding='utf-8'))}
old = json.load(open(os.path.join(SP, 'data', 'old120.json'), encoding='utf-8'))
manual = json.load(open(os.path.join(SP, 'data', 'manual120.json'), encoding='utf-8')) if os.path.exists(os.path.join(SP, 'data', 'manual120.json')) else {}

# --- nomes das cópias "(120 cores)" feitas por make_120.py: base (id do instantâneo) <-> nome da cópia
Bbase = [t for t in B['items'] if not is_copy(t['name'])]
Bbyid = {t['id']: t for t in B['items']}
copy_name, base_of_copy, seen = {}, {}, {}
for t in Bbase:
    n = t['name']; seen[n] = seen.get(n, 0) + 1
    cn = f'{n} (120 cores)' if seen[n] == 1 else f'{n} (versão {seen[n]}) (120 cores)'
    copy_name[t['id']] = cn; base_of_copy[cn] = t['id']
Bname = {t['name']: t for t in B['items']}
Cname = {t['name']: t for t in C['items']}
Cid = {t['id']: t for t in C['items']}


def fresh_for(bid):
    """linhas de 120 cores mais recentes do molde base `bid` (do instantâneo), ou None"""
    b = Bbyid.get(bid)
    if not b: return None
    n = b['name']
    if n in manual: return manual[n]
    if n in r13 and not only24(b['rows']): return r13[n]
    if only24(b['rows']):
        if n in src120 and src24.get(n) == b['rows'] and bid == next(t['id'] for t in Bbase if t['name'] == n): return src120[n]
        if bid in old: return old[bid]
    return None


def transplant(ref, cur, fresh):
    """aplica sobre `fresh` as contas que o usuário mudou (cur != ref). None se as dimensões não batem"""
    dims = lambda r: (len(r), max(len(x) for x in r))
    if not (dims(ref) == dims(cur) == dims(fresh)): return None
    out = [list(r) for r in fresh]
    for y, (a, b) in enumerate(zip(ref, cur)):
        for x, (ca, cb) in enumerate(zip(a, b)):
            if ca != cb: out[y][x] = cb
    return [''.join(r) for r in out]


stat = dict(base=0, so_copia=0, trocado=0, igual=0, editado_transplantado=0, editado_mantido=0, sem_120=0, reduzido=0)
notes = {'editado_transplantado': [], 'editado_mantido': [], 'sem_120': [], 'so_copia': []}
out = []
for t in C['items']:
    n = t['name']
    if n.endswith('(1 placa)'): continue
    bid = None
    if n.endswith('(120 cores)'):
        bid = base_of_copy.get(n)
        if bid and bid in Cid: continue                      # o base ainda existe: é ele que representa o desenho
        if not bid: print('AVISO: cópia sem base conhecida, mantida como está:', n)
    else:
        bid = t['id']
    rep_is_copy = n.endswith('(120 cores)')
    ref = (Bbyid.get(t['id']) or Bname.get(n) or {}).get('rows')      # desenho do instantâneo desse mesmo item
    cur = t['rows']
    edited = ref is not None and ref != cur
    fresh = fresh_for(bid) if bid else None
    rows = cur
    if fresh is not None:
        if edited:
            tp = transplant(ref, cur, fresh) if not rep_is_copy or True else None
            if tp is not None: rows = tp; stat['editado_transplantado'] += 1; notes['editado_transplantado'].append(n)
            else: rows = cur; stat['editado_mantido'] += 1; notes['editado_mantido'].append(n)
        else:
            base_rows = Bbyid[bid]['rows'] if bid in Bbyid else cur
            diff = None
            if len(fresh) == len(base_rows) and all(len(x) == len(y) for x, y in zip(fresh, base_rows)):
                diff = sum(1 for x, y in zip(base_rows, fresh) for c, e in zip(x, y) if c != e) / max(1, sum(c != '.' for x in base_rows for c in x))
            if diff is not None and diff <= 0.03 and not rep_is_copy: rows = cur; stat['igual'] += 1
            else: rows = fresh; stat['trocado'] += 1
    else:
        stat['sem_120'] += 1; notes['sem_120'].append(n)
    if rep_is_copy and bid:
        stat['so_copia'] += 1; notes['so_copia'].append(n)
    stat['base'] += 1
    h = len(rows); w = max(len(r) for r in rows)
    if w > PLATE or h > PLATE:
        rows = shrink.shrink(rows, PLATE, 'bias', empty_at=0.6); stat['reduzido'] += 1
    if rep_is_copy and bid in Bbyid:                          # o usuário excluiu o base e ficou a cópia: ela volta a ter o nome/id do base
        b = Bbyid[bid]; item = dict(t, id=bid, name=b['name'], rows=rows)
    else:
        item = dict(t, rows=rows)
    out.append(item)

removed = [r for r in (C.get('removed') or []) if r not in {t['name'] for t in out}]
print('moldes no catálogo atual:', len(C['items']), '-> final:', len(out), '|', stat)
print('editados pelo usuário e mantidos (dimensões mudaram):', notes['editado_mantido'])
print('editados pelo usuário (ajustes aplicados sobre a versão de 120 cores):', notes['editado_transplantado'])
print('sem conversão de 120 cores (ficam como estão):', len(notes['sem_120']))
big = [t['name'] for t in out if len(t['rows']) > PLATE or max(len(r) for r in t['rows']) > PLATE]
assert not big, big
assert len({t['id'] for t in out}) == len(out), 'ids repetidos'
if '--dry' not in sys.argv:
    tplfile.write(cat_path, C['legend'], C['cfg'], out, removed)
    print('gravado:', cat_path, '(cópia de segurança em tools/backups/)')
else:
    print('(--dry: nada foi gravado)')
json.dump(out, open(os.path.join(SP, 'out', 'finalize_preview.json'), 'w', encoding='utf-8'), ensure_ascii=False)
