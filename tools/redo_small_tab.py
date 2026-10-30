"""Refaz a aba "Até ~600 contas" (pedido do usuário, 2026-10-29):
  1. APAGA todos os moldes "(pequeno)" (as reduções de ~550 contas feitas por make_small.py); os nomes vão para TPL_REMOVED (o make_small não recria);
  2. DEVOLVE ao catálogo moldes que o usuário tinha tirado, que são NATURALMENTE pequenos (< 600 contas, ≤ 50 de lado) e que valem a pena (lista curada à mão olhando as folhas de
     contato: personagens e séries que já temos; ficaram de fora formas genéricas feitas pelo Claude, fotos borradas, tatuagens, duplicatas);
  3. tira os devolvidos de TPL_REMOVED.
A aba em si passou a ser por CONTAGEM (index.html: isSmall = t.beads < 600), então nenhum molde é renomeado nem sai da aba "1 placa".
uso:  python tools/redo_small_tab.py [--dry]
"""
import os, sys, json, glob, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import tplfile

TPL = os.path.join(ROOT, 'templates.js')
dry = '--dry' in sys.argv

# índices em tools/out/removed_small_names.json (ordem alfabética dos removidos < 600 com fonte em tools/data)
KEEP_IDX = [0, 3, 4, 6, 7, 8, 9, 10, 13, 14, 15, 18, 19, 20, 21, 22, 25, 26, 27, 28, 29, 31, 33, 34, 35, 36, 41, 43, 44, 47, 48, 50, 52, 54, 56, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 69, 70, 71, 72, 73,
            76, 77, 78, 79, 81, 85, 86, 87, 91, 93, 96, 97, 98, 99, 101, 102, 104, 108, 109, 111, 115, 116, 117, 120, 121, 122, 123, 125, 128]
FROM_BACKUP = ['Chiquinha', 'Eren Jaeger (chibi)', 'Frieren (chibi)', 'Okarun']      # sem arquivo em tools/data: vêm de cópias antigas do templates.js


def beads(rows): return sum(1 for r in rows for c in r if c != '.')


d = tplfile.parse(TPL)
names_all = json.load(open(os.path.join(HERE, 'out', 'removed_small_names.json'), encoding='utf-8'))
keep = [names_all[i] for i in KEEP_IDX]

# --- fontes (rows, série) por nome: o arquivo mais novo e de 120 cores vence; remessas 1-4 usam data/old120.json (recolorido) quando existe
src = {}
files = sorted(glob.glob(os.path.join(HERE, 'data', 'final*.json')) + glob.glob(os.path.join(HERE, 'data', 'outros_pool.json')), key=lambda p: (('_120' in p), p))
for p in files:
    try: dd = json.load(open(p, encoding='utf-8'))
    except Exception: continue
    if not isinstance(dd, list): continue
    for it in dd:
        if isinstance(it, list) and len(it) >= 3 and isinstance(it[0], str) and isinstance(it[2], list): src[it[0]] = (it[2], it[1], os.path.basename(p))
old120 = json.load(open(os.path.join(HERE, 'data', 'old120.json'), encoding='utf-8'))
back = {}
for p in sorted(glob.glob(os.path.join(HERE, 'backups', '*.js'))):
    try: bd = tplfile.parse(p)
    except Exception: continue
    for it in bd['items']:
        if it['name'] in FROM_BACKUP: back[it['name']] = (it['rows'], it['group'])

readd = []
for n in keep:
    rows, series, p = src[n]
    sid = tplfile.slug(n)
    if sid in old120 and not ('_120' in p): rows = old120[sid]
    assert beads(rows) < 600 and max(len(rows[0]), len(rows)) <= 50, (n, beads(rows))
    readd.append([n, series, rows])
for n in FROM_BACKUP:
    rows, group = back[n]; assert beads(rows) < 600; readd.append([n, group, rows])
print('a devolver:', len(readd))

# --- 1. apaga os "(pequeno)"
pequenos = [it for it in d['items'] if '(pequeno' in it['name']]
removed = list(d.get('removed') or [])
for it in pequenos:
    if it['name'] not in removed: removed.append(it['name'])
items = [it for it in d['items'] if '(pequeno' not in it['name']]
print('apagados "(pequeno)":', len(pequenos), '· catálogo:', len(d['items']), '->', len(items))
if dry:
    for n, s, r in readd: print('  +', ascii(n), beads(r))
    sys.exit(0)
tplfile.write(TPL, d['legend'], d['cfg'], items, removed)

# --- 2. devolve (add_templates cuida de categoria, id, contas soltas e cópia de segurança)
tmp = os.path.join(HERE, 'out', 'readd_small.json')
json.dump(readd, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
r = subprocess.run([sys.executable, os.path.join(HERE, 'add_templates.py'), tmp, '--readd'], capture_output=True)
print((r.stdout or b'').decode('cp1252', 'replace')[-1500:])

# --- 3. tira os devolvidos da lista de excluídos
d2 = tplfile.parse(TPL)
back_names = {n for n, s, r in readd}
rem2 = [n for n in (d2.get('removed') or []) if n not in back_names]
tplfile.write(TPL, d2['legend'], d2['cfg'], d2['items'], rem2)
print('moldes agora:', len(d2['items']), '· excluídos:', len(d2.get('removed') or []), '->', len(rem2))
