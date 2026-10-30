"""Melhoria de ROSTOS de moldes do catálogo, a pedido do usuário (2026-10-30; veja CLAUDE.md §7.16). Os consertos moram em tools/faces_fix.py (um dicionário FIX por id de molde).
  python tools/faces_apply.py [filtro de id...]            monta o molde novo de cada conserto e grava a comparação em tools/out/faces_<id>.png (fonte | atual | novo); NÃO mexe no catálogo
  python tools/faces_apply.py [filtro...] --apply          grava no templates.js (cópia em tools/backups/pre-faces.js na 1ª vez); só troca se o molde do catálogo ainda é o que eu tinha visto
Cada FIX: src=(remessa, índice[, box]) · conv={kwargs do illus.convert4} (reconverte a imagem; sem conv usa as linhas do catálogo) · skin=bool (trava de pele do near120) · legend/blocks/cells/sym (facetools.apply_fix)
"""
import os, sys, json, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
os.environ.setdefault('BEADPAL', '120')
import tplfile, loose, facetools as F, illus, r5, illus5
from flat import render_flat
from PIL import Image
import numpy as np
from faces_fix import FIX

APPLIED = os.path.join(HERE, 'data', 'faces_applied.json')       # o que EU gravei por último em cada molde (para poder refazer sem pular)
SNAP = os.path.join(HERE, 'data', 'faces_orig.json')       # o molde do catálogo ANTES do meu conserto (para só trocar o que ainda é igual e para desfazer)


def build(i, it, ap=True):
    f = FIX[i]; cur = it['rows']
    src = f.get('src'); rem, idx = (src[0], src[1]) if src else (None, None); box = src[2] if src and len(src) > 2 else None
    if 'base_fn' in f: base = f['base_fn']()                # molde-base calculado por uma função (ex.: cav_chibis_fix.fix_shun)
    elif 'base_rows' in f:                        # molde dado por extenso (letras apelidadas pela `legend`), p.ex. reconversões feitas à parte
        base = [''.join('.' if c == '.' else F.letter_of(c, f['legend']) for c in r) for r in f['base_rows']]
    elif 'conv' in f:
        r5.SKIN_ON = f.get('skin', True)
        kw = dict(f['conv'])
        if box and 'box' not in kw: kw['box'] = box
        base = illus.convert4(F.src_path(rem, idx), **kw)
        if f.get('post'): base = f['post'](base)
    elif 'conv5' in f:
        r5.SKIN_ON = f.get('skin', True)
        from faces_src import S as SRC
        kw0 = SRC[i][2] if i in SRC else {}
        kw = {k: v for k, v in kw0.items() if k in ('thr', 'bg', 'tol', 'pale_skin', 'peel', 'dark_frac', 'box', 'white_outside', 'refs', 'seal')}; kw.update(f['conv5'])
        if box and 'box' not in kw: kw['box'] = box
        base = illus5.convert5(F.src_path(rem, idx), **kw)
        if f.get('post'): base = f['post'](base)
    else: base = cur
    new = F.apply_fix(base, f) if ap else base
    if f.get('final'): new = f['final'](new)         # limpeza DEPOIS do desenho (pode cortar linhas/colunas vazias das bordas)
    if f.get('loose', True) and loose.loose_count(new): new = loose.fix_loose(new)
    return new


def compare(i, it, new, path):
    f = FIX[i]; src = f.get('src'); sc = f.get('scale', 10); h = len(it['rows']) * sc + 18
    if src:
        rem, idx = src[0], src[1]; box = src[2] if len(src) > 2 else None
        raw = F.src_raw(rem, idx, box); fg = F.fg_mask(raw); ys, xs = np.nonzero(fg)
        sm = Image.fromarray(raw).crop((max(0, xs.min() - 4), max(0, ys.min() - 4), min(raw.shape[1], xs.max() + 5), min(raw.shape[0], ys.max() + 5)))
        sm = sm.resize((max(1, int(sm.width * h / sm.height)), h), Image.LANCZOS)
    else: sm = Image.new('RGB', (4, h), (60, 60, 66))
    tmp = path + '.tmp.png'
    render_flat([('ATUAL', it['rows']), ('NOVO', new)], tmp, scale=sc, W=2 * (len(new[0]) * sc + 24) + 24)
    im = Image.open(tmp)
    comp = Image.new('RGB', (sm.width + im.width + 8, max(im.height, h + 24)), (60, 60, 66)); comp.paste(sm, (4, 24)); comp.paste(im, (sm.width + 8, 0)); comp.save(path); os.remove(tmp)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--') and not a.endswith('.js')]
    apply_ = '--apply' in sys.argv
    TPL = os.path.join(ROOT, 'templates.js'); d = tplfile.parse(TPL); by = {it['id']: it for it in d['items']}
    snap = json.load(open(SNAP, encoding='utf-8')) if os.path.exists(SNAP) else {}
    applied = json.load(open(APPLIED, encoding='utf-8')) if os.path.exists(APPLIED) else {}
    if '--prev' in sys.argv:        # --prev ARQUIVO.js: tratar o desenho desse backup como "versão que EU tinha gravado" (para refazer moldes cuja 1ª rodada foi gravada antes de existir faces_applied.json)
        pv = {x['id']: x['rows'] for x in tplfile.parse(sys.argv[sys.argv.index('--prev') + 1])['items']}
        for k, v in pv.items():
            if k in FIX: applied.setdefault(k, v)
    gone = [i for i in FIX if i not in by]
    if gone: print('NÃO ESTÃO MAIS NO CATÁLOGO (o usuário excluiu; pulados):', ', '.join(gone))
    ids = [i for i in FIX if i in by and (not args or any(a in i for a in args))]
    res = {}
    for i in ids:
        it = by[i]
        if i not in snap: snap[i] = it['rows']             # 1ª vez: guarda o original
        new = build(i, {'rows': snap[i], **{k: v for k, v in it.items() if k != 'rows'}}) if False else build(i, {'rows': snap[i]})
        res[i] = new
        compare(i, {'rows': snap[i]}, new, os.path.join(HERE, 'out', 'faces_%s.png' % i))
        print('%-52s %dx%d -> %dx%d  contas %d -> %d  soltas %d' % (i[:52], len(snap[i][0]), len(snap[i]), len(new[0]), len(new), sum(c != '.' for r in snap[i] for c in r), sum(c != '.' for r in new for c in r), loose.loose_count(new)))
    json.dump(snap, open(SNAP, 'w', encoding='utf-8'), ensure_ascii=False)
    if apply_:
        bk = os.path.join(HERE, 'backups', 'pre-faces.js')
        if not os.path.exists(bk): shutil.copy(TPL, bk)
        for i, new in res.items():
            cur = by[i]['rows']
            if cur != snap[i] and cur != new and cur != applied.get(i): print('  PULEI', i, '(o catálogo não é o que eu tinha visto: você ajustou no app?)'); continue
            by[i]['rows'] = new; applied[i] = new; print('  trocado', i)
        tplfile.write(TPL, d['legend'], d['cfg'], d['items'], d.get('removed')); print('gravado')
        json.dump(applied, open(APPLIED, 'w', encoding='utf-8'), ensure_ascii=False)
