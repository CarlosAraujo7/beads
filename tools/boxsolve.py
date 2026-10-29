"""Confere (e resolve) a montagem de uma CAIXA de encaixe: 6 peças planas com dentes que se intercalam.
Dada a lista de peças lidas da foto e o tamanho da caixa (W largura, H altura, D profundidade, em contas), procura em qual face cada peça entra
e com que giro/espelho, de modo que TODA conta da casca da caixa seja coberta EXATAMENTE uma vez (dente de uma peça = vão da vizinha).
Se achar uma solução, a leitura da foto está consistente; se não achar, alguma conta foi lida errada (o programa mostra onde mais bateu).

Mapeamento das faces = o do app (cellWorld em index.html), com Z para a frente do objeto, Y para baixo:
  front (Z=D-1): x=cx, y=cy · back (Z=0): x=W-1-cx, y=cy · left (x=0): z=cx · right (x=W-1): z=D-1-cx · top (y=0): x=cx, z=cy · bottom (y=H-1): x=cx, z=D-1-cy
uso (em Python):  from boxsolve import solve;  solve({'a': rows, ...}, W, H, D)  -> lista de soluções [{peça: (face, rot, espelho)}]
"""
import itertools


def rotate(rows, k):
    for _ in range(k % 4):
        h = len(rows); w = max(len(r) for r in rows); pad = [r.ljust(w, '.') for r in rows]
        rows = [''.join(pad[h - 1 - x][y] for x in range(h)) for y in range(w)]
    return rows


def mirror(rows):
    return [r[::-1] for r in rows]


def face_cells(face, rows, W, H, D):
    out = {}
    for cy, r in enumerate(rows):
        for cx, ch in enumerate(r):
            if ch == '.': continue
            if face == 'front': c = (cx, cy, D - 1)
            elif face == 'back': c = (W - 1 - cx, cy, 0)
            elif face == 'left': c = (0, cy, cx)
            elif face == 'right': c = (W - 1, cy, D - 1 - cx)
            elif face == 'top': c = (cx, 0, cy)
            else: c = (cx, H - 1, D - 1 - cy)
            out[c] = ch
    return out


def dims(face, W, H, D):
    return {'front': (W, H), 'back': (W, H), 'left': (D, H), 'right': (D, H), 'top': (W, D), 'bottom': (W, D)}[face]


def shell(W, H, D):
    return {(x, y, z) for x in range(W) for y in range(H) for z in range(D) if x in (0, W - 1) or y in (0, H - 1) or z in (0, D - 1)}


def solve(pieces, W, H, D, allow_mirror=False, limit=20):
    S = shell(W, H, D); names = list(pieces); faces = ['front', 'back', 'left', 'right', 'top', 'bottom']
    tot = sum(sum(1 for r in rows for ch in r if ch != '.') for rows in pieces.values())
    print(f'contas lidas: {tot} · casca da caixa {W}×{H}×{D}: {len(S)}')
    opts = {}   # (peça, face) -> [(rot, esp, células)]
    for n in names:
        for f in faces:
            fw, fh = dims(f, W, H, D); L = []
            for k in range(4):
                for m in ((0, 1) if allow_mirror else (0,)):
                    rows = rotate(pieces[n], k)
                    if m: rows = mirror(rows)
                    if len(rows) != fh or max(len(r) for r in rows) != fw: continue
                    cells = face_cells(f, rows, W, H, D)
                    if all(c in S for c in cells): L.append((k, m, cells))
            if L: opts[(n, f)] = L
    sols = []

    def rec(i, used, cur, taken):
        if len(sols) >= limit: return
        if i == len(faces):
            if len(used) == len(S): sols.append(dict(cur))
            return
        f = faces[i]
        for n in names:
            if n in taken or (n, f) not in opts: continue
            for k, m, cells in opts[(n, f)]:
                if any(c in used for c in cells): continue
                cur[n] = (f, k, m); rec(i + 1, used | set(cells), cur, taken | {n}); del cur[n]
    rec(0, frozenset(), {}, frozenset())
    print(f'{len(sols)} solução(ões)')
    for s in sols[:limit]: print('  ', s)
    return sols
