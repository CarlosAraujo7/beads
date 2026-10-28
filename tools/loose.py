"""CONTAS SOLTAS: regra do usuário (2026-10-28) — "nunca ter contas soltas". Conta solta = conta (ou grupinho) que não encosta de lado (4 vizinhos) na peça principal:
na placa ela não gruda no resto. Contato só na diagonal NÃO gruda.

fix_loose(rows) -> linhas sem contas soltas:
  1. componente de 1-2 contas separado da peça: some (ruído, respingo, brilho solto);
  2. componente de 3 a SMALL contas (12): se encosta em outro só na DIAGONAL, ou está a UMA célula vazia de distância, entra uma conta de ligação (a célula
     que fecha o canto/o vão) — assim o pedacinho vira parte da peça (a cauda do logo do Skyrim); se não chega perto de nada, some;
  3. componente com mais de SMALL contas é uma peça de verdade (moldes com 2 figuras, trio, emblema em partes): fica, mas se encosta em outra só na diagonal ganha a conta de ligação;
  4. tira as linhas/colunas vazias que sobrarem nas bordas.

uso:  python tools/loose.py              -> relatório do catálogo (moldes com contas soltas) sem gravar nada
      python tools/loose.py --apply      -> corrige o templates.js (cópia de segurança em tools/backups/)
      python tools/loose.py nome ...     -> só moldes cujo nome contém um dos filtros
"""
import os, sys, shutil, datetime
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import numpy as np, cv2
SMALL = 12


def components(rows):
    g = np.array([[c != '.' for c in r] for r in rows], np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(g, connectivity=4)
    return n, lab, st


def loose_count(rows):
    """nº de contas fora da peça principal e de peças pequenas (<= SMALL) — o que fix_loose mexe"""
    n, lab, st = components(rows)
    if n <= 2: return 0
    areas = sorted((int(st[i][4]) for i in range(1, n)), reverse=True)
    return sum(a for a in areas[1:] if a <= SMALL)


def fix_loose(rows, small=SMALL, stats=None):
    g = [list(r) for r in rows]
    H, W = len(g), len(g[0])
    removed = bridged = 0
    for _ in range(8):
        n, lab, st = components([''.join(r) for r in g])
        if n <= 2: break
        main = 1 + int(np.argmax([st[i][4] for i in range(1, n)]))
        changed = False
        order = sorted((i for i in range(1, n) if i != main), key=lambda i: st[i][4])
        for i in order:
            area = int(st[i][4])
            big = area > small                             # peça de verdade: só ganha a ligação se encosta em outra na diagonal (não gruda sem ela)
            ys, xs = np.nonzero(lab == i)
            if area <= 2:
                for y, x in zip(ys, xs): g[y][x] = '.'
                removed += area; changed = True; continue
            cand = None
            for y, x in zip(ys, xs):                       # contato na diagonal com outro componente? -> célula de ligação
                for dy, dx in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < H and 0 <= xx < W and lab[yy, xx] != 0 and lab[yy, xx] != i:
                        for by, bx, src in ((y, xx, (yy, xx)), (yy, x, (yy, xx))):
                            if g[by][bx] == '.': cand = (by, bx, g[src[0]][src[1]]); break
                    if cand: break
                if cand: break
            if not cand and not big:                       # separado por UMA célula vazia de outro componente? -> a célula do meio liga os dois
                for y, x in zip(ys, xs):
                    for dy, dx in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                        yy, xx = y + dy, x + dx; my, mx = y + dy // 2, x + dx // 2
                        if 0 <= yy < H and 0 <= xx < W and lab[yy, xx] != 0 and lab[yy, xx] != i and g[my][mx] == '.':
                            cand = (my, mx, g[y][x]); break
                    if cand: break
            if cand:
                g[cand[0]][cand[1]] = cand[2]; bridged += 1; changed = True
            elif not big:
                for y, x in zip(ys, xs): g[y][x] = '.'
                removed += area; changed = True
        if not changed: break
        # um passo por rodada: os rótulos mudam depois de cada ligação/remoção
    out = [''.join(r) for r in g]
    while out and not any(c != '.' for c in out[0]): out.pop(0)
    while out and not any(c != '.' for c in out[-1]): out.pop()
    if out:
        xs = [x for r in out for x, c in enumerate(r) if c != '.']
        x0, x1 = min(xs), max(xs) + 1
        out = [r[x0:x1] for r in out]
    if stats is not None: stats['removed'] = removed; stats['bridged'] = bridged
    return out


def fill_pinholes(rows, maxsize=3):
    """BURAQUINHOS: vazios de até `maxsize` células cercados por contas (não ligados ao lado de fora) — parece conta esquecida no meio do desenho.
    Cada célula vira a cor mais comum entre as contas vizinhas (8 vizinhos). Vazios maiores (olho vazado, anel, janela) ficam."""
    g = np.array([[c != '.' for c in r] for r in rows], np.uint8)
    pad = np.pad(1 - g, 1, constant_values=1)
    n, lab, st, _ = cv2.connectedComponentsWithStats(pad.astype(np.uint8), connectivity=4)
    out = lab[0, 0]; H, W = g.shape; res = [list(r) for r in rows]; filled = 0
    for i in range(1, n):
        if i == out or st[i][4] > maxsize: continue
        ys, xs = np.nonzero(lab == i)
        for y, x in zip(ys - 1, xs - 1):
            cnt = {}
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if (dy or dx) and 0 <= yy < H and 0 <= xx < W and rows[yy][xx] != '.': cnt[rows[yy][xx]] = cnt.get(rows[yy][xx], 0) + 1
            if cnt: res[y][x] = max(cnt, key=cnt.get); filled += 1
    return [''.join(r) for r in res], filled


if __name__ == '__main__':
    import tplfile
    ROOT = os.path.dirname(SP); TPL = os.path.join(ROOT, 'templates.js')
    args = sys.argv[1:]; apply = '--apply' in args; flt = [a for a in args if not a.startswith('--')]
    d = tplfile.parse(TPL); items = d['items']; rep = []
    for t in items:
        if flt and not any(f in t['name'] for f in flt): continue
        lc = loose_count(t['rows'])
        st = {}; new = fix_loose(t['rows'], stats=st)
        if new == t['rows']: continue
        assert loose_count(new) == 0, t['name']
        rep.append((lc, t['name'], st['removed'], st['bridged'], (len(t['rows'][0]), len(t['rows'])), (len(new[0]), len(new))))
        if apply: t['rows'] = new
    rep.sort(reverse=True)
    print(f'{len(rep)} moldes corrigidos de {len(items)}; contas soltas no total: {sum(r[0] for r in rep)}; removidas: {sum(r[2] for r in rep)}; ligações: {sum(r[3] for r in rep)}')
    for lc, n, rm, br, a, b in rep[:int(os.environ.get("TOP", 25))]: print(f'  {lc:3d} soltas  -{rm} +{br}  {a[0]}x{a[1]} -> {b[0]}x{b[1]}  {n}')
    if apply and rep:
        bk = os.path.join(SP, 'backups'); os.makedirs(bk, exist_ok=True)
        shutil.copy(TPL, os.path.join(bk, 'templates-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.js'))
        tplfile.write(TPL, d['legend'], d['cfg'], items, d.get('removed'))
        print('gravado em', TPL)
    elif not apply: print('(relatório: nada foi gravado; use --apply)')
