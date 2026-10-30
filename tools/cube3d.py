"""Gera PROJETOS 3D DE ENCAIXE (caixas de 6 peças planas com dentes alternados) a partir de moldes do catálogo: o rosto do molde vira a frente do cubo.

A junta é a mesma dos cubos lidos das fotos (Abelha 7×7×10, Presente 7×7×7): em cada aresta as contas alternam entre as duas peças vizinhas, então toda posição
da casca da caixa é de UMA peça só (confere com make_3d.check_box e tools/boxsolve.py):
  * aresta entre tampa (cima/baixo) e parede: a PAREDE fica com as posições ímpares (1,3,5…) e a tampa com as pares;
  * aresta vertical entre frente/trás e lateral: frente/trás ficam com as posições pares (0,2,4…, inclusive as pontas) e a lateral com as ímpares;
  * cantos (3 peças): da frente/trás (a conta do canto fica ligada à fileira de dentes de cima/baixo da frente).
Mapeamento das faces = o do app (cellWorld em index.html): front z=D-1 · back z=0 · left x=0 · right x=W-1 · top y=0 · bottom y=H-1, Y para baixo, peça vista DE FORA.

uso:  from cube3d import cube_project ;  p = cube_project(spec)   (veja tools/make_cubes.py para as especificações)
"""
import os, sys
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)

FACES = ['front', 'back', 'left', 'right', 'top', 'bottom']
PRIO = ['front', 'back', 'top', 'bottom', 'left', 'right']        # de qual face vem a COR de uma conta que fica em mais de uma face


def face_dims(f, W, H, D):
    return {'front': (W, H), 'back': (W, H), 'left': (D, H), 'right': (D, H), 'top': (W, D), 'bottom': (W, D)}[f]


def cell_voxel(f, cx, cy, W, H, D):
    return {'front': (cx, cy, D - 1), 'back': (W - 1 - cx, cy, 0), 'left': (0, cy, cx), 'right': (W - 1, cy, D - 1 - cx),
            'top': (cx, 0, cy), 'bottom': (cx, H - 1, D - 1 - cy)}[f]


def faces_of(v, W, H, D):
    x, y, z = v; out = []
    if z == D - 1: out.append('front')
    if z == 0: out.append('back')
    if x == 0: out.append('left')
    if x == W - 1: out.append('right')
    if y == 0: out.append('top')
    if y == H - 1: out.append('bottom')
    return out


def owner(v, W, H, D):
    fs = faces_of(v, W, H, D)
    if len(fs) == 1: return fs[0]
    if len(fs) >= 3: return 'front' if 'front' in fs else 'back'
    a, b = fs; x, y, z = v; S = {a, b}
    caps = S & {'top', 'bottom'}; fb = S & {'front', 'back'}; lr = S & {'left', 'right'}
    if caps:                                             # tampa × parede: a parede fica com os ímpares
        wall = (fb or lr).copy().pop(); cap = caps.copy().pop()
        t = x if fb else z
        return wall if t % 2 == 1 else cap
    t = y                                                # frente/trás × lateral: frente/trás com os pares
    return next(iter(fb)) if t % 2 == 0 else next(iter(lr))


def _cell_of(f, v, W, H, D):
    x, y, z = v
    return {'front': (x, y), 'back': (W - 1 - x, y), 'left': (z, y), 'right': (D - 1 - z, y), 'top': (x, z), 'bottom': (x, D - 1 - z)}[f]


def paint(v, tex, fill, W, H, D):
    for f in PRIO:
        if f not in faces_of(v, W, H, D): continue
        t = tex.get(f)
        if t:
            cx, cy = _cell_of(f, v, W, H, D)
            ch = t[cy][cx] if cy < len(t) and cx < len(t[cy]) else '.'
            if ch != '.': return ch
        return fill[f]
    raise ValueError(v)


def connected(rows):
    cells = {(x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch != '.'}
    if not cells: return True
    seen = set(); st = [next(iter(cells))]
    while st:
        c = st.pop()
        if c in seen: continue
        seen.add(c); x, y = c
        for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if n in cells and n not in seen: st.append(n)
    return len(seen) == len(cells)


def build_pieces(W, H, D, tex, fill, ears=None):
    """-> {face: rows}. `ears`: {'rows': [...]} linhas EXTRAS acima da frente (orelhas/chifres), coladas nas contas da fileira de cima da frente."""
    out = {}
    for f in FACES:
        fw, fh = face_dims(f, W, H, D); rows = []
        for cy in range(fh):
            r = ''
            for cx in range(fw):
                v = cell_voxel(f, cx, cy, W, H, D)
                r += paint(v, tex, fill, W, H, D) if owner(v, W, H, D) == f else '.'
            rows.append(r)
        out[f] = rows
    if ears:
        extra = ears['front']
        out['front'] = list(extra) + out['front']
    for f, rows in out.items():
        assert connected(rows), ('peça desconexa', f)
    return out


FACE_NAMES = {'front': 'Frente', 'back': 'Traseira', 'left': 'Lateral esquerda', 'right': 'Lateral direita', 'top': 'Tampa de cima', 'bottom': 'Base'}


def cube_project(spec):
    """spec: id, name, desc (opcional), size=(W,H,D), tex={'front': rows, ...}, fill={'front':letra,...} (cor de cada face onde a textura é '.'), ears={'front': [...]}, view, level, steps"""
    W, H, D = spec['size']
    fill = {f: spec['fill'].get(f) or spec['fill']['*'] for f in FACES}
    ears = spec.get('ears'); k = len(ears['front']) if ears else 0
    pcs = build_pieces(W, H, D, spec.get('tex', {}), fill, ears)
    at = {'front': [0, -k, D - 1], 'back': [W - 1, 0, 0], 'left': [0, 0, 0], 'right': [W - 1, 0, D - 1], 'top': [0, 0, 0], 'bottom': [0, H - 1, D - 1]}
    pieces = []; parts = []; index = {}
    names = dict(FACE_NAMES); names.update(spec.get('names', {}))
    # junta peças iguais (ex.: duas laterais)
    for f in FACES:
        rows = tuple(pcs[f])
        key = rows if f not in ('front',) else None
        same = next((i for i, p in enumerate(pieces) if tuple(p['rows']) == rows and f != 'front' and p['_f'][0] != 'front'), None)
        if same is None:
            pieces.append({'name': names[f], 'qty': 1, 'rows': list(rows), '_f': [f]}); same = len(pieces) - 1
        else:
            pieces[same]['qty'] += 1; pieces[same]['_f'].append(f)
        a = list(at[f]); parts.append({'piece': same, 'face': f, 'at': a})
    for p in pieces:
        fs = p.pop('_f')
        if p['qty'] > 1:
            p['name'] = {'left': 'Lateral', 'top': 'Tampa', 'back': 'Traseira'}.get(fs[0], p['name']) + (' (cima e baixo)' if fs == ['top', 'bottom'] else ' (esquerda e direita)' if fs == ['left', 'right'] else '')
            p['note'] = f"{p['qty']} iguais"
    shell = W * H * D - (W - 2) * (H - 2) * (D - 2)
    return {'id': spec['id'], 'name': spec['name'], 'level': spec.get('level', 'Médio'), 'view': spec.get('view', [-28, -32]),
            'box': {'dims': [W, H, D], 'skip': []}, 'desc': spec['desc'], 'pieces': pieces, 'parts': parts, 'steps': spec['steps'],
            '_shell': shell}


def resample(rows, crop, nw, nh, bg='.', empty_at=0.55):
    """recorta `crop`=(x0,y0,x1,y1) (em contas do molde) e reduz/estica para nw×nh contas; as cores escuras (contorno) pesam mais para o traço sobreviver.
    contas vazias viram `bg`."""
    import math
    from shrink import BIAS
    x0, y0, x1, y1 = crop
    sub = [r[x0:x1].ljust(x1 - x0, '.') for r in rows[y0:y1]]
    H = len(sub); W = x1 - x0; out = []
    for j in range(nh):
        ya, yb = j * H / nh, (j + 1) * H / nh; row = ''
        for i in range(nw):
            xa, xb = i * W / nw, (i + 1) * W / nw; wt = {}
            for y in range(int(math.floor(ya)), min(H, int(math.ceil(yb)))):
                wy = min(y + 1, yb) - max(y, ya)
                for x in range(int(math.floor(xa)), min(W, int(math.ceil(xb)))):
                    wx = min(x + 1, xb) - max(x, xa)
                    if wy > 0 and wx > 0: c = sub[y][x]; wt[c] = wt.get(c, 0) + wx * wy
            tot = (xb - xa) * (yb - ya)
            cols = {c: a for c, a in wt.items() if c != '.'}
            if wt.get('.', 0) >= empty_at * tot or not cols: row += bg; continue
            row += max(cols, key=lambda c: cols[c] * BIAS.get(c, 1.0))
        out.append(row)
    return out


def dominant(rows, skip='k'):
    from collections import Counter
    c = Counter(ch for r in rows for ch in r if ch != '.' and ch not in skip)
    return c.most_common(1)[0][0] if c else 'k'
