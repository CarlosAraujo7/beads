"""Revisão da remessa 20 pedida pelo usuário (2026-10-30): Cavaleiros ILUSTRADOS (chibis, folhas, armaduras, capacetes; 1 placa e grandes) com menos ruído nas bordas,
sem fundo virando branco entre pernas/asas (seal 0 + holes_bg + beadclean.clean), o Patinho no passo real do desenho e o Shiryu (pixel, corpo inteiro) com pele e armadura mais claras.
  python tools/r20_revisao.py --snapshot   guarda as linhas ATUAIS desses moldes no catálogo (tools/data/r20_rev_orig.json)
  python tools/r20_revisao.py --apply      troca pelo que está em data/final22*_120.json, só se o molde do catálogo ainda é igual ao instantâneo (senão pula e avisa)"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
os.environ.setdefault('BEADPAL', '120'); os.environ['REMNUM'] = '20'
import tplfile, loose
TPL = os.path.join(ROOT, 'templates.js'); SNAP = os.path.join(HERE, 'data', 'r20_rev_orig.json')


def targets():
    import r20_exfinal as R
    names = []
    for n, g, idx, kw, pl, box, clr in R.ILLCFG:
        names.append(n)
        if pl: names.append(n + ' (grande)')
    return names + ['Patinho de guarda-chuva (pixel)', 'Shiryu de Dragão (pixel, corpo inteiro)']


if __name__ == '__main__':
    d = tplfile.parse(TPL); by = {t['name']: t for t in d['items']}
    if '--snapshot' in sys.argv:
        snap = {n: by[n]['rows'] for n in targets() if n in by}
        json.dump(snap, open(SNAP, 'w', encoding='utf-8'), ensure_ascii=False)
        print(len(snap), 'moldes no instantâneo; fora do catálogo (excluídos):', [n for n in targets() if n not in by]); sys.exit()
    if '--apply' in sys.argv:
        snap = json.load(open(SNAP, encoding='utf-8'))
        APP = os.path.join(HERE, 'data', 'r20_rev_applied.json')
        applied = json.load(open(APP, encoding='utf-8')) if os.path.exists(APP) else {}
        new = {}
        for f in ('final22_120.json', 'final22_multi_120.json'):
            for it in json.load(open(os.path.join(HERE, 'data', f), encoding='utf-8')): new[it[0]] = it[2]
        import shutil; shutil.copy(TPL, os.path.join(HERE, 'backups', 'pre-r20-revisao.js'))
        n_ok = 0
        for n, old in snap.items():
            if n not in by: print('  NÃO ESTÁ MAIS NO CATÁLOGO, pulei:', n); continue
            if n.startswith('Armadura') and not n.endswith('(grande)'): continue          # o usuário excluiu as armaduras de 1 placa (2026-10-30): não mexo nelas
            if by[n]['rows'] != old and by[n]['rows'] != applied.get(n): print('  PULEI (você ajustou no app depois):', n); continue
            r = new[n]
            if loose.loose_count(r): r = loose.fix_loose(r)
            if max(len(r[0]), len(r)) > 50 and not n.endswith('(grande)'):
                import shrink; r = loose.fix_loose(shrink.shrink(r, 50, 'bias', empty_at=0.6))
            if r != by[n]['rows']: by[n]['rows'] = r; n_ok += 1
            applied[n] = r
        tplfile.write(TPL, d['legend'], d['cfg'], d['items'], d.get('removed')); print('trocados', n_ok, '| gravado')
        json.dump(applied, open(APP, 'w', encoding='utf-8'), ensure_ascii=False)
