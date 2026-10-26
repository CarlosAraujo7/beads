import sys, os
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)

NB8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
NB4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def trim(rows):
    ys = [y for y, r in enumerate(rows) if any(c != '.' for c in r)]; xs = [x for x in range(len(rows[0])) if any(r[x] != '.' for r in rows)]
    return [r[min(xs):max(xs) + 1] for r in rows[min(ys):max(ys) + 1]]

def pad(rows, n=1):
    w = len(rows[0]); e = '.' * (w + 2 * n)
    return [e] * n + ['.' * n + r + '.' * n for r in rows] + [e] * n

def strip_outline(rows, black='k', passes=1):
    g = [list(r) for r in pad(rows)]
    h, w = len(g), len(g[0])
    occ = lambda y, x: 0 <= y < h and 0 <= x < w and g[y][x] != '.'
    for _ in range(passes):
        remove = []
        for y in range(h):
            for x in range(w):
                if g[y][x] != black: continue
                # celula de borda: algum vizinho (8) vazio / fora da placa
                if all(occ(y + dy, x + dx) for dy, dx in NB8): continue
                inner = [(y + dy, x + dx) for dy, dx in NB8 if occ(y + dy, x + dx) and not all(occ(y + dy + a, x + dx + b) for a, b in NB8)]
                inner_all = [(y + dy, x + dx) for dy, dx in NB8 if occ(y + dy, x + dx)]
                inside = [p for p in inner_all if any(not occ(p[0] + a, p[1] + b) for a, b in NB8) is False]   # vizinhos que NAO sao de borda
                # contorno puro: tem vizinho interno (nao-borda) colorido e nenhum vizinho interno preto
                if inside and all(g[p[0]][p[1]] != black for p in inside): remove.append((y, x))
        for y, x in remove: g[y][x] = '.'
    return trim([''.join(r) for r in g])

def components(rows, n8=False):
    h, w = len(rows), len(rows[0]); seen = set(); comps = []
    nb = NB4 + (NB8 if n8 else [])
    for y in range(h):
        for x in range(w):
            if rows[y][x] != '.' and (y, x) not in seen:
                st = [(y, x)]; seen.add((y, x)); c = []
                while st:
                    a, b = st.pop(); c.append((a, b))
                    for dy, dx in nb:
                        p, q = a + dy, b + dx
                        if 0 <= p < h and 0 <= q < w and rows[p][q] != '.' and (p, q) not in seen: seen.add((p, q)); st.append((p, q))
                comps.append(c)
    return sorted(comps, key=len, reverse=True)

def drop_specks(rows, maxsize=3):
    comps = components(rows)
    if len(comps) < 2: return rows
    g = [list(r) for r in rows]
    for c in comps[1:]:
        if len(c) <= maxsize:
            for y, x in c: g[y][x] = '.'
    return trim([''.join(r) for r in g])

def connect_components(rows, maxdrop=6, max_iter=6):
    """garante que o desenho seja uma peca so (contas se prendem pelos lados): pontes de 1 conta nos encostos diagonais, descarta migalhas"""
    rows = list(rows)
    for _ in range(max_iter):
        comps = components(rows)
        if len(comps) < 2: break
        h, w = len(rows), len(rows[0]); g = [list(r) for r in rows]
        main = set(comps[0]); changed = False
        for c in comps[1:]:
            cs = set(c); best = None
            for (y, x) in c:
                for (a, b) in main:
                    d = max(abs(a - y), abs(b - x))
                    if best is None or d < best[0]: best = (d, (y, x), (a, b))
                    if d == 1: break
                if best and best[0] == 1: break
            d, p, q = best
            if d == 1:          # encosto diagonal: uma conta na quina
                for cy, cx in ((p[0], q[1]), (q[0], p[1])):
                    if 0 <= cy < h and 0 <= cx < w and g[cy][cx] == '.':
                        g[cy][cx] = rows[p[0]][p[1]]; changed = True; break
            elif d == 2 and len(c) > maxdrop:   # um vazio no meio: liga com a cor da peca solta
                my, mx = (p[0] + q[0]) // 2, (p[1] + q[1]) // 2
                if g[my][mx] == '.': g[my][mx] = rows[p[0]][p[1]]; changed = True
            elif len(c) <= maxdrop:
                for (y, x) in c: g[y][x] = '.'; changed = True
        rows = [''.join(r) for r in g]
        if not changed: break
    return trim(rows)


def strip2(rows, black='k', small=5, core=4):
    """tira o contorno preto: fio fino de borda some, fio fino interno vira a cor vizinha, pretos grossos (cabelo, roupa) e detalhes pequenos (olhos) ficam"""
    g = [list(r) for r in pad(rows)]
    h, w = len(g), len(g[0])
    occ = lambda y, x: 0 <= y < h and 0 <= x < w and g[y][x] != '.'
    isb = lambda y, x: 0 <= y < h and 0 <= x < w and g[y][x] == black
    border = lambda y, x: any(not occ(y + a, x + b) for a, b in NB8)
    blk = {(y, x) for y in range(h) for x in range(w) if g[y][x] == black}
    thick = set()
    for (y, x) in blk:
        if isb(y, x + 1) and isb(y + 1, x) and isb(y + 1, x + 1):
            thick |= {(y, x), (y, x + 1), (y + 1, x), (y + 1, x + 1)}
    # componentes pretos (8-vizinhos)
    seen = set(); comps = []
    for p in sorted(blk):
        if p in seen: continue
        st = [p]; seen.add(p); c = []
        while st:
            a, b = st.pop(); c.append((a, b))
            for dy, dx in NB8:
                q = (a + dy, b + dx)
                if q in blk and q not in seen: seen.add(q); st.append(q)
        comps.append(set(c))
    keep = set()
    for c in comps:
        if len(c) <= small:
            if not any(border(y, x) for y, x in c): keep |= c
            continue
        t = c & thick
        # pedacos grossos pequenos (juncoes do contorno) nao contam
        seen2 = set()
        for p in sorted(t):
            if p in seen2: continue
            st = [p]; seen2.add(p); part = []
            while st:
                a, b = st.pop(); part.append((a, b))
                for dy, dx in NB8:
                    q = (a + dy, b + dx)
                    if q in t and q not in seen2: seen2.add(q); st.append(q)
            if len(part) >= core + (4 if any(border(y, x) for y, x in part) else 0): keep |= set(part)
    out = [row[:] for row in g]
    for (y, x) in blk:
        if (y, x) in keep: continue
        if border(y, x): out[y][x] = '.'; continue
        votes = {}
        for dy, dx in NB8:
            q = (y + dy, x + dx)
            if occ(*q) and g[q[0]][q[1]] != black:
                wgt = 2 if dy == 0 or dx == 0 else 1
                votes[g[q[0]][q[1]]] = votes.get(g[q[0]][q[1]], 0) + wgt
        if votes: out[y][x] = max(sorted(votes), key=lambda k: votes[k])
    return trim([''.join(r) for r in out])


def bridge(rows, maxlen=12):
    """liga cada pedaco solto ao maior por um caminho curto de contas (cor do pedaco solto), pelos lados"""
    from collections import deque, Counter
    rows = [list(r) for r in rows]
    h, w = len(rows), len(rows[0])
    for _ in range(40):
        comps = components([''.join(r) for r in rows])
        if len(comps) < 2: break
        main = set(comps[0]); done = False
        for c in sorted(comps[1:], key=len):
            col = Counter(rows[y][x] for y, x in c).most_common(1)[0][0]
            cs = set(c); prev = {}; dq = deque()
            for p in c: prev[p] = None; dq.append(p)
            hit = None
            while dq and hit is None:
                p = dq.popleft()
                for dy, dx in NB4:
                    q = (p[0] + dy, p[1] + dx)
                    if not (0 <= q[0] < h and 0 <= q[1] < w) or q in prev: continue
                    if q in main: hit = p; break
                    if rows[q[0]][q[1]] == '.': prev[q] = p; dq.append(q)
            if hit is None: continue
            path = []; p = hit
            while p is not None and p not in cs: path.append(p); p = prev[p]
            if len(path) <= maxlen:
                for (y, x) in path: rows[y][x] = col
                done = True; break
        if not done: break
    return [''.join(r) for r in rows]


def strip3(rows, black='k', max_iter=4):
    """tira o contorno preto externo, inclusive as pontas dos cabelos: celula preta de borda, com vizinho colorido
    (nao preto) e no maximo 2 vizinhos pretos (4-vizinhos) e removida; pretos grossos (cabelo, roupa) ficam"""
    g = [list(r) for r in pad(rows)]
    h, w = len(g), len(g[0])
    occ = lambda y, x: 0 <= y < h and 0 <= x < w and g[y][x] != '.'
    border0 = {(y, x) for y in range(h) for x in range(w) if g[y][x] != '.' and any(not occ(y + a, x + b) for a, b in NB8)}
    for _ in range(max_iter):
        kill = []
        for (y, x) in border0:
            if g[y][x] != black: continue
            nb = [(y + a, x + b) for a, b in NB4]
            blk = sum(1 for p in nb if 0 <= p[0] < h and 0 <= p[1] < w and g[p[0]][p[1]] == black)
            col = sum(1 for p in nb if 0 <= p[0] < h and 0 <= p[1] < w and g[p[0]][p[1]] not in ('.', black))
            if col >= 1 and blk <= 2: kill.append((y, x))
        if not kill: break
        for (y, x) in kill: g[y][x] = '.'
    return trim([''.join(r) for r in g])


def recolor_outline(rows, black='k', max_iter=3, interior=False):
    """o contorno preto vira a cor da peca vizinha (nao some): pontas de cabelo, maos e chapeu ficam com a cor deles.
    So mexe em preto fino (<=2 vizinhos pretos) encostado no vazio e em algo colorido; pretos grossos ficam."""
    g = [list(r) for r in pad(rows)]
    h, w = len(g), len(g[0])
    occ = lambda y, x: 0 <= y < h and 0 <= x < w and g[y][x] != '.'
    border0 = {(y, x) for y in range(h) for x in range(w) if g[y][x] != '.' and any(not occ(y + a, x + b) for a, b in NB8)}
    for it in range(max_iter):
        change = []
        for (y, x) in sorted(border0):
            if g[y][x] != black: continue
            blk = sum(1 for a, b in NB4 if g[y + a][x + b] == black) if 0 < y < h - 1 and 0 < x < w - 1 else 0
            votes = {}
            for a, b in NB8:
                q = (y + a, x + b)
                if 0 <= q[0] < h and 0 <= q[1] < w and g[q[0]][q[1]] not in ('.', black):
                    votes[g[q[0]][q[1]]] = votes.get(g[q[0]][q[1]], 0) + (2 if a == 0 or b == 0 else 1)
            if votes and blk <= 2:
                change.append(((y, x), max(sorted(votes), key=lambda k: votes[k])))
        if not change: break
        for (p, c) in change: g[p[0]][p[1]] = c
    return trim([''.join(r) for r in g])


def clean_k(rows, keep=(), black='k', thick_keep=True, erase_orphans=True, no_thick_rows=None, interior=None):
    """tira o preto fino (contorno e tracos de separacao) trocando pela cor da peca vizinha; ficam os pretos grossos
    (cabelo, roupa) e os que estiverem dentro das caixas `keep` = [(y0, y1, x0, x1)] (olhos, boca, detalhes)"""
    g = [list(r) for r in pad(rows)]
    h, w = len(g), len(g[0])
    occ = lambda y, x: 0 <= y < h and 0 <= x < w and g[y][x] != '.'
    isb = lambda y, x: 0 <= y < h and 0 <= x < w and g[y][x] == black
    thick = set()
    if thick_keep:
        for y in range(h):
            for x in range(w):
                if isb(y, x) and isb(y, x + 1) and isb(y + 1, x) and isb(y + 1, x + 1):
                    thick |= {(y, x), (y, x + 1), (y + 1, x), (y + 1, x + 1)}
    if no_thick_rows:
        thick = {p for p in thick if not (no_thick_rows[0] + 1 <= p[0] <= no_thick_rows[1] + 1)}
    protected = set()
    for (y0, y1, x0, x1) in keep:
        for y in range(y0 + 1, y1 + 2):
            for x in range(x0 + 1, x1 + 2): protected.add((y, x))       # +1: o pad
    out = [row[:] for row in g]
    for y in range(h):
        for x in range(w):
            if g[y][x] != black or (y, x) in thick or (y, x) in protected: continue
            votes = {}
            for a, b in NB8:
                q = (y + a, x + b)
                if 0 <= q[0] < h and 0 <= q[1] < w and g[q[0]][q[1]] not in ('.', black):
                    votes[g[q[0]][q[1]]] = votes.get(g[q[0]][q[1]], 0) + (2 if a == 0 or b == 0 else 1)
            inside = all(occ(y + a, x + b) for a, b in NB8)
            if interior and inside and votes: out[y][x] = interior
            elif votes: out[y][x] = max(sorted(votes), key=lambda k: votes[k])
            elif erase_orphans and any(not occ(y + a, x + b) for a, b in NB8): out[y][x] = '.'
    return trim([''.join(r) for r in out])


def despeckle_colors(rows, minsame=1):
    """celula solta de cor diferente (nenhum vizinho de 4 com a mesma cor) vira a cor mais comum em volta"""
    g = [list(r) for r in rows]
    h, w = len(g), len(g[0])
    out = [r[:] for r in g]
    for y in range(h):
        for x in range(w):
            c = g[y][x]
            if c == '.': continue
            same = sum(1 for a, b in NB4 if 0 <= y + a < h and 0 <= x + b < w and g[y + a][x + b] == c)
            if same >= minsame: continue
            votes = {}
            for a, b in NB8:
                p, q = y + a, x + b
                if 0 <= p < h and 0 <= q < w and g[p][q] not in ('.', c): votes[g[p][q]] = votes.get(g[p][q], 0) + 1
            if votes and sum(votes.values()) >= 5: out[y][x] = max(sorted(votes), key=lambda k: votes[k])
    return [''.join(r) for r in out]
