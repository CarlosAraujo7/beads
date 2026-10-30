"""Simetria de moldes de FRENTE (pedido do usuário, 2026-10-30, Cavaleiros do Zodíaco: olhos diferentes de um lado e do outro, marcas e chifres da armadura que mudam).
mirror(rows, a2, side)   espelha em torno do eixo a2/2 (a2 par = o eixo cai EM CIMA de uma coluna de contas; a2 ímpar = ENTRE duas colunas):
    side='L' mantém o lado esquerdo e copia (espelhado) para a direita; side='R' mantém o direito e copia para a esquerda.
    A coluna do eixo (a2 par) fica como está. O molde é refeito na largura que couber o lado mantido + o espelho, e depois cortado (O.trim).
best_axis(rows)          eixo (em meias-colunas) de maior coincidência com o espelho;
noise(rows, x0, x1)      conta "ruído" (contas cuja letra não aparece em nenhum dos 4 vizinhos) em um intervalo de colunas — serve para escolher a metade mais limpa.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import outline as O


def best_axis(rows, span=8):
    H, W = len(rows), len(rows[0]); best = None
    for a2 in range(W - span, W + span + 1):
        ok = tot = 0
        for y in range(H):
            for x in range(W):
                c = rows[y][x]
                if c == '.': continue
                tot += 1; xm = a2 - x
                if 0 <= xm < W and rows[y][xm] == c: ok += 1
        sc = ok / max(tot, 1)
        if best is None or sc > best[0]: best = (sc, a2)
    return best[1], best[0]


def mirror(rows, a2, side='L'):
    H, W = len(rows), len(rows[0])
    c2 = a2                                                # x -> a2 - x
    keep = [x for x in range(W) if (2 * x <= a2 if side == 'L' else 2 * x >= a2)]
    xs = set(keep) | {a2 - x for x in keep}
    x0, x1 = min(xs), max(xs)
    off = -x0 if x0 < 0 else 0
    out = []
    for y in range(H):
        row = ['.'] * (x1 - min(x0, 0) + 1)
        for x in keep:
            ch = rows[y][x]
            if ch == '.': continue
            row[x + off] = ch
            xm = a2 - x
            if xm != x: row[xm + off] = ch
        out.append(''.join(row))
    return O.trim(out)


def noise(rows, x0, x1):
    H, W = len(rows), len(rows[0]); n = 0
    for y in range(H):
        for x in range(max(x0, 0), min(x1, W)):
            c = rows[y][x]
            if c == '.': continue
            nb = [rows[yy][xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if 0 <= yy < H and 0 <= xx < W]
            if c not in nb: n += 1
    return n
