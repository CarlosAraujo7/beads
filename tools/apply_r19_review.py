"""Aplica a REVISÃO da remessa 19 (ver r19_exfinal.py, bloco "REVISÃO") no templates.js, SEM tocar em mais nada do catálogo definitivo do usuário (2026-10-30).
  * troca as linhas de data/final21_revisao_120.json (Eeveelutions + 5 moldes sem a trava de pele) SÓ se o molde do catálogo ainda é igual ao que eu tinha gravado
    (data/final21_120.json + `loose.fix_loose`): se o usuário ajustou o desenho no app, não mexe e avisa;
  * tira o ícone de lupa (marca d'água) do Tricerátops;
  * cópia de segurança em tools/backups/pre-r19-review.js; aplica `loose.fix_loose` nas linhas novas (regra: nunca contas soltas).
uso:  python tools/apply_r19_review.py [--dry]
"""
import os, sys, json, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import tplfile, loose, outline as O

TPL = os.path.join(ROOT, 'templates.js'); dry = '--dry' in sys.argv
d = tplfile.parse(TPL)
by = {it['name']: it for it in d['items']}
orig = {n: rows for n, g, rows in json.load(open(os.path.join(HERE, 'data', 'final21_120.json'), encoding='utf-8'))}
rev = json.load(open(os.path.join(HERE, 'data', 'final21_revisao_120.json'), encoding='utf-8'))


def same_as_mine(n):
    r = orig[n]
    r = loose.fix_loose(r) if loose.loose_count(r) else r
    rv = next((x for m, g, x in rev if m == n), None)
    rv = (loose.fix_loose(rv) if loose.loose_count(rv) else rv) if rv else None
    return by[n]['rows'] == r or by[n]['rows'] == rv or (n in TOUCH_NAMES)


TOUCH_NAMES = ()
done = []; skipped = []; ok_names = set()
for n, g, rows in rev:
    if n not in by: skipped.append((n, 'não está mais no catálogo')); continue
    if not same_as_mine(n): skipped.append((n, 'você ajustou o desenho no app')); continue
    ok_names.add(n)
    new = loose.fix_loose(rows) if loose.loose_count(rows) else rows
    if new != by[n]['rows']: by[n]['rows'] = new; done.append(n)

# retoques célula a célula (artefatos de JPEG que a conversão fiel deixou; conferidos com as cores brutas da fonte): (linha, coluna, letra certa)
#  Jolteon: 2 amarelos A3 quase idênticos ao corpo (229,222,120 × 234,221,138) -> A1 'j';  Espeon: 2 células azul-acinzentadas (120,144,163) no meio das orelhas cinza (sangramento de cor do JPEG) viravam turquesa C15 -> cinza H4 'm'
TOUCH = {'Jolteon (sentado)': [(2, 4, 'j'), (8, 13, 'j')], 'Espeon (sentado)': [(4, 1, 'm'), (4, 19, 'm')]}
for n, cells in TOUCH.items():
    if n in ok_names:
        rows = [list(r) for r in by[n]['rows']]
        for y, x, ch in cells: rows[y][x] = ch
        by[n]['rows'] = [''.join(r) for r in rows]; print('  retoque', n.encode('ascii', 'replace').decode(), cells)

# Tricerátops: ícone de lupa do canto (marca d'água do site), 21 contas soltas lá embaixo à esquerda
t = by.get('Tricerátops azul (pixel)')
if t:
    comps = O.components(t['rows'])
    if len(comps) == 2 and min(len(c) for c in comps) <= 30:
        small = min(comps, key=len); keep = set(small)
        t['rows'] = O.trim([''.join('.' if (y, x) in keep else c for x, c in enumerate(r)) for y, r in enumerate(t['rows'])])
        done.append('Tricerátops azul (pixel) [ícone de lupa tirado]')

print('trocados:', len(done)); [print('  +', n.encode('ascii', 'replace').decode()) for n in done]
print('pulados:', len(skipped)); [print('  -', n.encode('ascii', 'replace').decode(), '|', why) for n, why in skipped]
if dry: print('(--dry: nada gravado)'); sys.exit(0)
shutil.copy(TPL, os.path.join(HERE, 'backups', 'pre-r19-review.js'))
tplfile.write(TPL, d['legend'], d['cfg'], d['items'], d.get('removed'))
print('gravado (cópia em tools/backups/pre-r19-review.js)')
