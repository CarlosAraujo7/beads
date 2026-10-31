"""Remessa 20 (138 imagens). Rode com a paleta de 120 cores:  BEADPAL=120 python tools/r20_exfinal.py [filtro...]   -> data/final22_120.json (1 placa) + data/final22_multi_120.json ("(grande)")
Gráficos: cópia exata. A maioria tem o CÓDIGO da cor ou um símbolo escrito dentro de cada célula, e o grid2.detect trava em 1/2, 1/3 ou 1/5 do passo: aqui o passo real vai forçado (medido por
autocorrelação + recorte ampliado) e a cor é a dominante da célula (mode=True). Ilustrações (quase todas Cavaleiros do Zodíaco): illus5.convert5, com irmão "(grande)" de 4 placas.
Puladas e por quê: veja SKIP no fim."""
import os, sys, json
os.environ['REMNUM'] = '20'
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import numpy as np, cv2
import r5, r6, outline as O, illus, illus5, beadclean
from flat import render_flat
from palette import sfx, ALL
E = r6.exact6
PALE = [((252, 239, 230), 16, next(p['letter'] for p in ALL if p['code'] == 'E14'))]      # pele creme dos gráficos chineses: o near120 mandava para o branco


def lg(rows): return r5.largest(rows)


def keep(n):
    """mantém só as peças com pelo menos n contas (legenda, título e moldura pontilhada são peças pequenas; raio do Percy e o Z do Stitch ficam)"""
    def f(rows):
        m = np.array([[c != '.' for c in r] for r in rows], np.uint8)
        k, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        return O.trim([''.join(c if c != '.' and st[lab[y, x]][4] >= n else '.' for x, c in enumerate(r)) for y, r in enumerate(rows)])
    return f


def cut(y0=None, y1=None, x0=None, x1=None, then=None):
    """recorta linhas/colunas DEPOIS da conversão (legenda colada embaixo, ícone na lateral)"""
    def f(rows):
        r = O.trim([s[x0:x1] for s in rows[y0:y1]])
        return then(r) if then else r
    return f


def drop_dull(rows):
    """foto de peça pronta (Shiryu, idx 24): o fundo de parede/madeira é cinza ou bege apagado; a peça é verde, preta, azul, amarela e pele. Apaga as letras apagadas e claras e fica com a maior peça"""
    import colorsys
    bad = set()
    for p in ALL:
        r, g, b = [int(p['hex'][i:i + 2], 16) / 255 for i in (1, 3, 5)]
        h, s_, v = colorsys.rgb_to_hsv(r, g, b)
        if s_ < 0.28 and v > 0.38: bad.add(p['letter'])
    return lg(O.trim([''.join('.' if c in bad else c for c in r) for r in rows]))


def big_block(rows):
    """fica com o maior bloco entre linhas vazias (a legenda de cores fica num bloco separado, embaixo do desenho)"""
    out, cur = [], []
    for r in rows + ['.' * len(rows[0])]:
        if set(r) == {'.'}:
            if cur: out.append(cur); cur = []
        else: cur.append(r)
    return O.trim(max(out, key=lambda b: sum(c != '.' for r in b for c in r)))


def G(idx, p, **kw):
    """gráfico com código/símbolo na célula: passo forçado, cor dominante, fundo claro ligado à borda, só a maior peça"""
    a = dict(px=p, mode=True, thr=222, post=lg); a.update(kw)
    return E(idx, **a)


def Plain(idx, p=None, **kw):
    """gráfico limpo: passo forçado só se precisar, fundo pela cor do canto"""
    return E(idx, px=p, **kw)


CFG = [
 # ---- gráficos com código na célula
 ('Stitch dormindo (pixel)', 'Lilo & Stitch', lambda: G(3, 22.2, post=lambda r: big_block(keep(8)(r)))),
 ('Angel dormindo (pixel)', 'Lilo & Stitch', lambda: G(56, 22.2, post=cut(y1=-3, then=keep(8)))),
 ('Cachorro marrom de língua de fora (pixel)', 'Animais', lambda: G(6, 17.94)),
 ('Dumbledore (chibi, pixel)', 'Harry Potter', lambda: G(10, 23.67, post=cut(x1=-2, then=lg))),
 ('Sasuke Uchiha (chibi, gráfico)', 'Naruto', lambda: G(21, 14.52)),
 ('Giyu Tomioka (chibi, pixel)', 'Demon Slayer', lambda: G(22, 13.76)),
 ('Rainbow Dash (pixel)', 'My Little Pony', lambda: G(30, 21.81)),
 ('Hermione Granger (chibi, gráfico)', 'Harry Potter', lambda: G(34, 35.66, colmap=PALE)),
 ('Dragão verde-água (chibi, pixel)', 'Outros', lambda: G(37, 29.02, thr=250)),
 ('Harry Potter (chibi, gráfico)', 'Harry Potter', lambda: G(40, 22.98)),
 ('Jiraiya (chibi, gráfico)', 'Naruto', lambda: G(44, 14.88)),
 ('Rainha de Copas (pixel)', 'Disney', lambda: G(48, 21.75)),
 ('Malévola (pixel)', 'Disney', lambda: G(51, 20.52)),
 ('Obanai Iguro (chibi, pixel)', 'Demon Slayer', lambda: G(53, 10.38)),
 ('Hagrid (chibi, pixel)', 'Harry Potter', lambda: G(60, 40.46, colmap=PALE)),
 ('Gaara (chibi, pixel)', 'Naruto', lambda: G(67, 14.63)),
 ('Tartaruga verde (pixel)', 'Animais', lambda: G(71, 28.46)),
 ('Jogador de futebol loiro (pixel)', 'Outros', lambda: G(72, 15.2, crop=(1, 53, 1, 47))),
 ('Professora McGonagall (chapéu, gráfico)', 'Harry Potter', lambda: G(78, 37.9, colmap=PALE)),
 ('Hello Kitty de Luffy (pixel)', 'Hello Kitty', lambda: G(83, 19.37)),
 ('Naruto (chibi, gráfico)', 'Naruto', lambda: G(134, 15.28)),
 # ---- série de Halloween e One Piece (célula com símbolo)
 ('Espantalho de abóbora (pixel)', 'Halloween', lambda: G(95, 17)),
 ('Lobisomem (pixel)', 'Halloween', lambda: G(96, 12)),
 ('Bruxinha (pixel)', 'Halloween', lambda: G(97, 19)),
 ('Vampiro (pixel)', 'Halloween', lambda: G(98, 20)),
 ('Múmia (pixel)', 'Halloween', lambda: G(99, 20)),
 ('Esqueleto (pixel)', 'Halloween', lambda: G(100, 20)),
 ('Zumbi (pixel)', 'Halloween', lambda: G(101, 20)),
 ('Boneco de pano costurado (pixel)', 'Halloween', lambda: G(102, 12)),
 ('Aranha (pixel)', 'Halloween', lambda: G(103, 23)),
 ('Caldeirão (pixel)', 'Halloween', lambda: G(104, 26)),
 ('Morcego (pixel)', 'Halloween', lambda: G(106, 19)),
 ('Fantasma (pixel)', 'Halloween', lambda: G(107, 25)),
 ('Chapéu de bruxa (pixel)', 'Halloween', lambda: G(116, 23)),
 ('Gato preto (pixel)', 'Halloween', lambda: G(120, 23)),
 ('Casa assombrada (pixel)', 'Halloween', lambda: G(123, 21)),
 ('Balde de abóbora (pixel)', 'Halloween', lambda: G(124, 21)),
 ('Fantasminha com balde (pixel)', 'Halloween', lambda: G(125, 20)),
 ('Franky (One Piece, gráfico)', 'One Piece', lambda: G(108, 13)),
 ('Jinbe (One Piece, gráfico)', 'One Piece', lambda: G(109, 13)),
 ('Nico Robin (One Piece, gráfico)', 'One Piece', lambda: G(110, 18)),
 ('Brook (One Piece, gráfico)', 'One Piece', lambda: G(111, 13)),
 ('Usopp (One Piece, gráfico)', 'One Piece', lambda: G(112, 18)),
 ('Chopper (One Piece, gráfico)', 'One Piece', lambda: G(113, 18)),
 ('Zoro (One Piece, gráfico)', 'One Piece', lambda: G(114, 18)),
 ('Luffy (One Piece, gráfico)', 'One Piece', lambda: G(115, 18)),
 ('Sanji (One Piece, gráfico)', 'One Piece', lambda: G(117, 18)),
 ('Nami (One Piece, gráfico)', 'One Piece', lambda: G(118, 18)),
 ('Hornet (pixel)', 'Hollow Knight', lambda: G(119, 15)),
 ('Goku Super Saiyajin (pixel)', 'Dragon Ball', lambda: G(121, 12)),
 ('Goku (pixel, corpo inteiro)', 'Dragon Ball', lambda: G(122, 12)),
 # ---- gráficos limpos
 ('Guaxinim (pixel)', 'Animais', lambda: Plain(2)),
 ('Mu de Áries (chibi, pixel)', 'Cavaleiros do Zodíaco', lambda: Plain(4, post=lg)),
 ('Gon Freecss (pixel, fundo azul)', 'Hunter x Hunter', lambda: Plain(5)),
 ('Bandeira dos Chapéus de Palha (gráfico)', 'One Piece', lambda: Plain(8)),
 ('Percy Jackson (pixel, com espada)', 'Percy Jackson', lambda: Plain(13, post=cut(y1=-3, then=keep(8)))),
 ('Patinho de guarda-chuva (pixel)', 'Animais', lambda: E(14, px=dict(px=17.15, py=17.25, ox=-4.05, oy=-9.35, W=43, H=43), achro=60, post=lg)),
 ('Bond Forger (pixel)', 'Spy x Family', lambda: Plain(15, 15.3, crop_img=(2, 73, 734, 997), ref=(150, 191, 185), tol=32, post=lg)),
 ('Menina de cabelo preto e mechas azuis (pixel)', 'Outros', lambda: Plain(17, post=lg)),
 ('Golfinho (pixel)', 'Animais', lambda: Plain(18)),
 ('Pernalonga (pixel)', 'Looney Tunes', lambda: Plain(20)),
 ('Annabeth Chase (pixel)', 'Percy Jackson', lambda: Plain(23, post=keep(8))),
 ('Kyojuro Rengoku (chibi, pixel)', 'Demon Slayer', lambda: Plain(25)),
 ('Vi (Arcane, pixel)', 'Arcane', lambda: Plain(26)),
 ('Ace (chibi, gráfico)', 'One Piece', lambda: Plain(29)),
 ('Merida (Valente, pixel)', 'Disney', lambda: Plain(31, 23.4, crop_img=(29, 30, 705, 705), ref=(203, 168, 252), tol=45, post=lg)),
 ('Hermione Granger (pixel)', 'Harry Potter', lambda: Plain(32, post=lg)),
 ('Pomo de Ouro (pixel)', 'Harry Potter', lambda: Plain(35)),
 ('Professora McGonagall (pixel, corpo inteiro)', 'Harry Potter', lambda: Plain(46, crop=(0, 36, 1, 22), thr=225, post=lg)),
 ('Greymon (pixel)', 'Digimon', lambda: Plain(47)),
 ('Pintinho com balão vermelho (pixel)', 'Animais', lambda: Plain(50, 13, crop_img=(0, 0, 326, 460), ref=(20, 197, 252), tol=45, post=keep(8))),
 ('Loki (chibi, pixel)', 'Marvel', lambda: Plain(54, post=lg)),
 ('Papai Noel (pixel)', 'Outros', lambda: Plain(55)),
 ('Drácula (pixel)', 'Halloween', lambda: Plain(59, post=lg)),
 ('Anya Forger (pixel, gráfico)', 'Spy x Family', lambda: Plain(61, thr=160, post=lg)),
 ('Ezio Auditore (pixel, gráfico)', "Assassin's Creed", lambda: Plain(62, crop=(0, 28, 9, 34), thr=225, post=lg)),
 ('Severo Snape (pixel)', 'Harry Potter', lambda: Plain(65, crop=(1, 32, 1, 22), thr=225, post=lg)),
 ('Casal de esquilos com coração (pixel)', 'Animais', lambda: Plain(68)),
 ('Alice (pixel)', 'Disney', lambda: Plain(69, post=lg)),
 ('Sanji (pixel, fumando)', 'One Piece', lambda: Plain(73, post=lg)),
 ('Mulher-Maravilha (chibi, pixel)', 'DC Comics', lambda: Plain(76)),
 ('Pennywise (rosto, pixel)', 'It: A Coisa', lambda: Plain(77)),
 ('Doutor Estranho (chibi, pixel)', 'Marvel', lambda: Plain(79)),
 ('Pennywise (chibi com balão, pixel)', 'It: A Coisa', lambda: Plain(81)),
 ('Tigre (pixel)', 'Animais', lambda: Plain(82, post=lg)),
 ('Sailor Moon (chibi, pixel)', 'Sailor Moon', lambda: Plain(87, post=lg)),
 ('Tricerátops verde (pixel)', 'Animais', lambda: Plain(94)),
 ('Killua Zoldyck (pixel, fundo azul)', 'Hunter x Hunter', lambda: Plain(126, 26.87, crop_img=(112, 341, 1019, 1790), ref=(115, 194, 255), tol=40, post=lg)),
 ('Seto Kaiba (pixel)', 'Yu-Gi-Oh', lambda: Plain(128, post=lg)),
 ('Coala (pixel)', 'Animais', lambda: Plain(135, post=lg)),
 ('Pennywise (chibi, balão, versão 2)', 'It: A Coisa', lambda: Plain(136, post=lg)),
 # ---- Cavaleiros em gráfico (mesma série; as repetidas por MD5 entram com nome novo: o usuário tinha excluído as antigas e mandou de novo)
 ('Seiya de Pégaso (pixel, corpo inteiro)', 'Cavaleiros do Zodíaco', lambda: Plain(0)),
 ('Hyoga de Cisne (pixel, corpo inteiro)', 'Cavaleiros do Zodíaco', lambda: Plain(92)),
 ('Shiryu de Dragão (pixel, corpo inteiro)', 'Cavaleiros do Zodíaco', lambda: Plain(132, colmap=[((0, 128, 0), 22, 'f'), ((248, 152, 104), 30, 's')], post=lg)),
 ('Shun de Andrômeda (pixel, corpo inteiro)', 'Cavaleiros do Zodíaco', lambda: Plain(39)),
 ('Ikki de Fênix (pixel, corpo inteiro)', 'Cavaleiros do Zodíaco', lambda: Plain(137)),
]

_C = {}
def cached(key, fn):
    if key not in _C: _C[key] = fn()
    return _C[key]


def comps(rows, n, by_x=False):
    """as n maiores peças, na ordem de leitura (by_x: só da esquerda para a direita)"""
    m = np.array([[c != '.' for c in r] for r in rows], np.uint8)
    k, lab, st, cen = cv2.connectedComponentsWithStats(m, connectivity=8)
    big = sorted(range(1, k), key=lambda i: -st[i][4])[:n]
    H = len(rows)
    big.sort(key=lambda i: cen[i][0] if by_x else (round(cen[i][1] / (H / 2.2)), cen[i][0]))
    return [O.trim([''.join(c if lab[y, x] == i else '.' for x, c in enumerate(r)) for y, r in enumerate(rows)]) for i in big]


def peel(rows, letters=None):
    """tira os cantos claros que sobraram em volta do brasão: branco/cinza-claro ligado à borda do recorte"""
    if letters is None:
        import colorsys
        letters = {p['letter'] for p in ALL if colorsys.rgb_to_hsv(*[int(p['hex'][i:i + 2], 16) / 255 for i in (1, 3, 5)])[1] < 0.12 and colorsys.rgb_to_hsv(*[int(p['hex'][i:i + 2], 16) / 255 for i in (1, 3, 5)])[2] > 0.75}
    H, W = len(rows), len(rows[0]); g = [list(r) for r in rows]
    st = [(y, x) for y in range(H) for x in range(W) if (y in (0, H - 1) or x in (0, W - 1)) and g[y][x] in letters]
    while st:
        y, x = st.pop()
        if g[y][x] not in letters: continue
        g[y][x] = '.'
        st += [(b, a) for b, a in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)) if 0 <= b < H and 0 <= a < W]
    return O.trim([''.join(r) for r in g])


def fill_rows(rows, letter='w'):
    """o leão branco da Grifinória (bandeira) encosta na borda e o fundo entrava por ele: devolve o branco entre o primeiro e o último ponto de cada linha"""
    out = []
    for r in rows:
        a = len(r) - len(r.lstrip('.')); b = len(r.rstrip('.'))
        out.append(r[:a] + r[a:b].replace('.', letter) + r[b:])
    return out


def quad(rows):
    """folha 2×2 cujas figuras se tocam pelos cantos: corta no meio"""
    H, W = len(rows), len(rows[0])
    return [lg(O.trim([r[a:b] for r in rows[c:d]])) for c, d in ((0, H // 2), (H // 2, H)) for a, b in ((0, W // 2), (W // 2, W))]


for k, n in enumerate(['Grifinória', 'Lufa-Lufa', 'Sonserina', 'Corvinal']):
    CFG.append((f'Brasão da {n} (escudo)', 'Harry Potter', (lambda k=k: cached('c11', lambda: comps(E(11, crop=(2, 99, 0, 72)), 4))[k])))
for k, n in enumerate(['Grifinória', 'Lufa-Lufa', 'Corvinal', 'Sonserina']):
    CFG.append((f'Brasão da {n} (coração)', 'Harry Potter', (lambda k=k: cached('c38', lambda: [peel(c) for c in comps(E(38), 4)])[k])))
for k, n in enumerate(['Lufa-Lufa', 'Corvinal', 'Grifinória', 'Sonserina']):
    CFG.append((f'Brasão da {n} (bandeira)', 'Harry Potter', (lambda k=k: cached('c75', lambda: [fill_rows(c) if j == 2 else c for j, c in enumerate(comps(E(75), 4))])[k])))
for k, n in enumerate(['Sonserina', 'Corvinal', 'Grifinória', 'Lufa-Lufa']):
    CFG.append((f'Brasão da {n} (quadrado)', 'Harry Potter', (lambda k=k: cached('c84', lambda: [peel(c) for c in quad(E(84))])[k])))
for k, n in enumerate(['Jessie (Equipe Rocket, pixel)', 'James (Equipe Rocket, pixel)', 'Meowth (Equipe Rocket, pixel)']):
    CFG.append((n, 'Pokémon', (lambda k=k: cached('c57', lambda: comps(E(57), 3))[k])))


# ---- ilustrações (convert5): (nome, índice, kwargs, irmão grande?). Rosto com pele: skin=True (nome com "chibi"); objeto/armadura: sem a trava de pele
CDZ = 'Cavaleiros do Zodíaco'
F = r6.FILES
CH = dict(K=24, dark_frac=0.45, black_L=11.0, thr=240, pale_skin=True, warm_white=7, seal=0.0)      # sem holes_bg: nos chibis ele esvaziava capacete branco e rosto pálido      # chibis: branco quase puro é fundo; em 1 placa contorno 0,45 (0,25 engole rosto e armadura), nos grandes 0,25 (BIG)
BIG = dict(dark_frac=0.25, black_L=14.0)
# armaduras: holes_bg tira o fundo branco fechado entre pernas/asas; nas armaduras de Pégaso BRANCAS ele esvaziava a própria armadura (branco puro igual ao fundo): lá fica desligado
OB = dict(K=26, dark_frac=0.40, black_L=12.0, thr=240, seal=0.0, holes_bg=1.5, big=dict(K=36, smooth_de=12.0, rare_n=10, dark_frac=0.13, black_L=12.0, lone_dark=True))                      # armaduras (objetos): contorno menos dominante
def _cm(table, warm_dark=None):
    """center_map por molde: table = {letra antiga: letra nova}; warm_dark = letra para o castanho quase preto (sombra de cabelo) que viraria H7"""
    def f(rgb, L, letter, is_black):
        if warm_dark and letter == 'k' and not is_black and rgb[0] - rgb[2] > 15: return warm_dark
        return table.get(letter)
    return f


# revisão 3 (pedido do usuário, 2026-10-30): Seiya rosto grande (sombra castanha do cabelo virava preto), Shiryu piscando e Shun verde vivo (rosto BRANCO puro na arte -> pele clara E14;
# tiara prateada do Shun virava marrom G14 -> cinza H4), aro azul-claro de adesivo do Shiryu (C2) sai da borda, assinatura verde dele (B16) sai
CM_SEIYA42 = _cm({}, warm_dark='Ì')


def put(rows, cells):
    g = [list(r) for r in rows]
    for (y, x), c in cells.items():
        if 0 <= y < len(g) and 0 <= x < len(g[0]): g[y][x] = c
    return [''.join(r) for r in g]


def heal(rows, y0, y1, x0, x1, bad):
    """no retângulo, cada conta de letra `bad` vira a letra mais comum das vizinhas que não são `bad` (repete até acabar): limpa restos antes de redesenhar"""
    from collections import Counter
    g = [list(r) for r in rows]; H, W = len(g), len(g[0])
    for _ in range(12):
        todo = [(y, x) for y in range(max(0, y0), min(H, y1 + 1)) for x in range(max(0, x0), min(W, x1 + 1)) if g[y][x] in bad]
        if not todo: break
        for y, x in todo:
            nb = [g[yy][xx] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1), (y - 1, x - 1), (y - 1, x + 1), (y + 1, x - 1), (y + 1, x + 1))
                  if 0 <= yy < H and 0 <= xx < W and g[yy][xx] not in bad and g[yy][xx] != '.']
            if nb: g[y][x] = Counter(nb).most_common(1)[0][0]
    return [''.join(r) for r in g]


def line(cells, letter):
    return {c: letter for c in cells}


# retoques à mão (molde de 1 placa), desenhados sobre a folha fonte × molde com a grade (2026-10-30). Letras: k H7 · w H2 · y A4 · Ì F11 · Ë F10 · r F5 · & D3 · b C8 · 1 C4
# · Á E14 (pele clara) · l H3 · i H1 · m H4 · | E10 · È F7 · 9 C15 · N B7 · M B6
def FIX_SEIYA42(rows):
    """enfeite de Pégaso na testa: cabeça branca com 2 olhos castanhos, chifre dourado de cada lado (o da esquerda tinha sumido), faixa branca saindo dos dois lados"""
    c = {}
    for y, xs in ((6, (15, 16, 17)), (7, (15, 16, 17, 18)), (8, (14, 15, 16, 17, 18)), (9, (14, 15, 16, 17, 18)), (10, (14, 16, 18)), (11, (14, 15, 16, 17, 18)),
                  (12, (15, 16, 17)), (13, (15, 16))):
        for x in xs: c[(y, x)] = 'w'
    c[(10, 15)] = 'Ë'; c[(10, 17)] = 'Ë'                                                  # olhos
    c.update(line([(4, 13), (5, 13), (6, 13), (7, 14)], 'y'))                                # chifre esquerdo
    c.update(line([(4, 20), (5, 20), (6, 20), (7, 20), (8, 19), (9, 19), (10, 19), (10, 20)], 'y'))   # chifre direito com a volta
    c.update(line([(10, 12), (11, 10), (11, 11), (11, 12)], 'w'))                            # faixa da esquerda
    c.update({(10, 13): 'Ì', (11, 13): 'Ì', (11, 20): 'w', (11, 21): 'w', (7, 19): 'Ì', (8, 20): 'Ì', (12, 14): 'Ì', (12, 18): 'Ì', (13, 17): 'Ì', (6, 14): 'Ì', (6, 18): 'Ì'})
    return put(rows, c)


def FIXG_SEIYA42(rows):
    """grande: o chifre dourado da ESQUERDA do enfeite de Pégaso tinha sumido no castanho (o da direita estava bom)"""
    return put(rows, line([(10, 25), (11, 25), (12, 25), (12, 26), (13, 26), (14, 26), (14, 27), (15, 27), (16, 27), (16, 28), (17, 28), (18, 28), (18, 29), (19, 29)], 'y'))


def FIXG_SHUN74(rows):
    """grande: a tiara prateada saía cor-de-pele (o branco puro do rosto vira pele E14 neste molde) com contorno castanho: acima da testa (linhas 0-24) pele -> prata H1, castanho -> cinza H5"""
    g = [list(r) for r in rows]
    for y in range(0, min(25, len(g))):
        for x, c in enumerate(g[y]):
            if c in 'Áw}@': g[y][x] = 'i'
            elif c == 'È': g[y][x] = 'd'
    return [''.join(r) for r in g]


def FIX_SHIRYU43(rows):
    """tiara: os 4 chifres dourados contínuos (2 de fora compridos, 2 de dentro com dobra), olhos vermelhos e garras douradas do dragão; rosto: olho esquerdo piscando e o direito aberto, azul, com brilho"""
    c = {}
    c.update(line([(3, 9), (4, 9), (4, 10), (5, 10), (6, 10), (6, 11), (7, 11), (7, 12), (8, 12), (8, 13), (8, 14), (9, 14), (9, 15)], 'y'))
    c.update(line([(3, 16), (4, 16), (5, 16), (6, 16), (7, 16), (7, 17), (8, 17)], 'y'))
    c.update(line([(2, 23), (3, 23), (4, 23), (5, 23), (6, 22), (7, 21)], 'y'))
    c.update(line([(1, 28), (2, 28), (3, 28), (4, 27), (5, 27), (6, 26), (6, 27), (7, 25), (7, 26), (8, 24), (8, 25), (9, 23), (9, 24)], 'y'))
    c.update({(4, 11): 'k', (5, 11): 'k', (13, 17): 'y', (13, 18): 'y', (10, 18): 'r', (10, 21): 'r'})
    c.update({(19, 18): 'k', (19, 19): 'k', (20, 19): 'k', (21, 17): 'Á', (20, 15): 'k', (21, 16): 'k', (22, 15): 'k', (22, 16): 'k', (22, 17): 'k'})   # olho piscando
    for x, l1, l2 in ((23, '&', 'b'), (24, 'w', 'b'), (25, 'b', '1'), (26, '&', 'b')):                                                              # olho aberto
        c[(20, x)] = 'k'; c[(21, x)] = l1; c[(22, x)] = l2
    return put(rows, c)


def FIX_SHUN74(rows):
    """tiara prateada: 2 chifres finos que sobem para fora, pedra central de ponta (claro à esquerda, escuro à direita) e as duas asinhas rosa; olhos com íris verde-água, pupila e brilho"""
    rows = heal(rows, 0, 11, 10, 28, set('ÁwimlÈ|]}@V'))
    c = {}
    c.update(line([(1, 11), (2, 12), (3, 12), (4, 13), (5, 13), (6, 14), (7, 15)], 'm'))
    c.update(line([(1, 27), (2, 26), (3, 26), (4, 25), (5, 25), (6, 24), (7, 23)], 'm'))
    gem = {4: {19: 'l'}, 5: {18: 'l', 19: 'i', 20: 'l'}, 6: {17: 'l', 18: 'i', 19: 'i', 20: 'l', 21: 'm'}, 7: {17: 'i', 18: 'i', 19: 'l', 20: 'l', 21: 'm'},
           8: {17: 'i', 18: 'i', 19: 'l', 20: 'm', 21: 'm'}, 9: {17: 'l', 18: 'i', 19: 'l', 20: 'm', 21: 'm'}, 10: {18: 'l', 19: 'l', 20: 'm'}}
    for y, d in gem.items():
        for x, l in d.items(): c[(y, x)] = l
    c.update(line([(8, 15), (8, 16), (9, 13), (9, 14), (9, 15), (10, 12), (10, 13)], '|'))
    c.update(line([(8, 22), (8, 23), (9, 23), (9, 24), (9, 25), (10, 25), (10, 26)], '|'))
    rows = put(rows, c)
    rows = heal(rows, 21, 25, 10, 27, set('Èk&rV'))                                       # olhos antigos fora, depois desenha
    c = {}
    for (y0, x0, hl) in ((21, 12, 13), (21, 21, 22)):
        c.update(line([(y0, x0 + 1), (y0, x0 + 2), (y0, x0 + 3)], 'È'))                    # cílios
        c.update(line([(y0 + 1, x) for x in range(x0, x0 + 5)], 'k'))                      # pálpebra
        c.update({(y0 + 2, x0): 'k', (y0 + 2, x0 + 4): 'k', (y0 + 2, x0 + 1): '9', (y0 + 2, x0 + 2): '9', (y0 + 2, x0 + 3): '9',
                  (y0 + 3, x0 + 1): '9', (y0 + 3, x0 + 2): 'N', (y0 + 3, x0 + 3): '9', (y0 + 4, x0 + 1): 'M', (y0 + 4, x0 + 2): 'M', (y0 + 4, x0 + 3): 'M'})
        c[(y0 + 2, hl)] = 'w'                                                               # brilho do mesmo lado nos dois olhos
    c.update({(23, 10): 'È', (23, 11): 'È', (22, 26): 'È', (23, 26): 'È'})                  # pontinha dos cílios para fora
    return put(rows, c)
CM_SHIRYU43 = _cm({'w': 'Á', 'U': '.'})
CM_SHUN74 = _cm({'Ö': 'm', 'Z': 'i', 'w': 'Á'})
ILL = [
 ('Cavaleiro de Ouro de cabelo roxo (chibi, risada)', 1, CH, 4),
 ('Hyoga de Cisne (chibi, adesivo)', 7, dict(CH, peel=1.0), 4),
 ('Shiryu de Dragão (chibi, escudo)', 33, CH, 4),
 ('Seiya de Pégaso (chibi, rosto grande)', 42, dict(CH, black_L=3.5, center_map=CM_SEIYA42, fix=FIX_SEIYA42, fixg=FIXG_SEIYA42), 4),
 ('Shiryu de Dragão (chibi, piscando)', 43, dict(CH, center_map=CM_SHIRYU43, drop_edge='0Z', fix=FIX_SHIRYU43), 4),
 ('Hyoga de Cisne (chibi, no gelo)', 49, dict(CH, seal=1.0), 4),
 ('Milo de Escorpião (chibi)', 63, CH, 4),
 ('Shun de Andrômeda (chibi, cabelo verde vivo)', 74, dict(CH, center_map=CM_SHUN74, fix=FIX_SHUN74, fixg=FIXG_SHUN74), 4),
 ('Ikki de Fênix (chibi, adesivo)', 130, dict(CH, warm_white=2, peel=1.0), 4),
 ('Shun de Andrômeda (chibi, correntes)', 133, dict(CH, holes_bg=1.5, lone_dark=True), 4),
 ('Armadura de Cisne (objeto, azul)', 19, OB, 4),
 ('Armadura de Cisne (objeto, branca)', 41, OB, 4),
 ('Armadura de Cisne (objeto, voando)', 88, OB, 4),
 ('Armadura de Dragão (objeto)', 28, OB, 4),
 ('Armadura de Dragão (busto)', 85, OB, 4),
 ('Armadura de Fênix (objeto, branca e laranja)', 36, dict(OB, holes_bg=0.0), 4),
 ('Armadura de Fênix (objeto, vermelha)', 127, OB, 4),
 ('Armadura de Fênix (objeto, azul)', 129, OB, 4),
 ('Armadura de Pégaso (objeto, prata)', 52, dict(OB, holes_bg=0.0), 4),
 ('Armadura de Pégaso (objeto, azul)', 64, OB, 4),
 ('Armadura de Pégaso (objeto, vermelha)', 70, dict(OB, holes_bg=0.0), 4),
 ('Armadura de Pégaso (objeto, dourada)', 80, dict(OB, holes_bg=0.0), 4),
 ('Armadura de Andrômeda (objeto, correntes)', 90, OB, 4),
 ('Armadura de Andrômeda (objeto, rosa)', 93, OB, 4),
 ('Armadura de Ouro de Aquário (objeto)', 58, OB, 4),
]
# folhas: a 1 tem contorno preto grosso (0,30 traz o espiral do chifre do Seiya e os olhos); nas 2 e 3 o branco/prata das armaduras e tiaras virava lilás/malva (D9, D5, D6) -> cinza-prata
CM_SILVER = _cm({'x': 'i', '(': 'l', 'v': 'l'})
SHEET_KW = {9: dict(dark_frac=0.30), 16: dict(center_map=CM_SILVER), 45: dict(center_map=CM_SILVER)}
SHEET = {
 9: [('Seiya de Pégaso (chibi, folha 1)', (45, 1, 585, 665)), ('Shiryu de Dragão (chibi, folha 1)', (629, 0, 1139, 665)), ('Shun de Andrômeda (chibi, folha 1)', (3, 675, 367, 1165)),
     ('Hyoga de Cisne (chibi, folha 1)', (391, 716, 798, 1144)), ('Ikki de Fênix (chibi, folha 1)', (808, 699, 1186, 1140))],
 16: [('Shiryu de Dragão (chibi, folha 2)', (26, 15, 502, 800)), ('Hyoga de Cisne (chibi, folha 2)', (540, 60, 1060, 880), [(540, 770, 770, 880)]), ('Seiya de Pégaso (chibi, folha 2)', (340, 700, 790, 1495), [(660, 700, 790, 770), (340, 700, 400, 800), (650, 1360, 790, 1495), (340, 1400, 520, 1495)]),
      ('Ikki de Fênix (chibi, folha 2)', (36, 1426, 544, 2176)), ('Shun de Andrômeda (chibi, folha 2)', (630, 1360, 1060, 2176), [(630, 1360, 690, 1470)])],
 45: [('Shun de Andrômeda (chibi, folha 3)', (38, 85, 165, 265)), ('Ikki de Fênix (chibi, folha 3)', (160, 8, 305, 203)), ('Hyoga de Cisne (chibi, folha 3)', (305, 62, 445, 262)),
      ('Seiya de Pégaso (chibi, folha 3)', (95, 262, 228, 440)), ('Shiryu de Dragão (chibi, folha 3)', (268, 250, 425, 445))],
}
HELMS = [('Capricórnio', (26, 0, 164, 211)), ('Aquário', (202, 65, 330, 204)), ('Peixes', (364, 63, 503, 202)), ('Câncer', (518, 54, 707, 192)),
         ('Leão', (32, 298, 162, 416)), ('Virgem', (194, 269, 356, 414)), ('Áries', (376, 262, 509, 415)), ('Touro', (530, 275, 695, 414)),
         ('Gêmeos', (22, 493, 168, 626)), ('Libra', (212, 512, 333, 620)), ('Escorpião', (382, 494, 499, 619)), ('Sagitário', (553, 497, 677, 607))]


def ill(idx, kw, plates=None, box=None, size=50, skin=True, clear=()):
    """kw: parâmetros do convert5 + (opcionais, deste arquivo) fix/fixg = retoque à mão (facetools.apply_fix) do molde de 1 placa / grande,
    drop_edge = letras de aro claro de adesivo que saem da borda de fora"""
    import loose
    r5.SKIN_ON = skin
    a = dict(kw); a.update(size=size)
    bigkw = a.pop('big', None)
    if plates and bigkw: a.update(bigkw)
    fix = a.get('fixg' if plates else 'fix'); a.pop('fixg', None); a.pop('fix', None)
    drop_edge = a.pop('drop_edge', '')
    lone = a.pop('lone_dark', False)
    if plates: a['plates'] = plates; a.update(BIG if kw.get('warm_white') else {})
    rgb = illus._load(F[idx], box).copy()
    ox, oy = (box[0], box[1]) if box else (0, 0)
    for x0, y0, x1, y1 in clear: rgb[max(0, y0 - oy):max(0, y1 - oy), max(0, x0 - ox):max(0, x1 - ox)] = 255
    rows = illus5.convert5(rgb=rgb, **a)
    if drop_edge: rows = beadclean.drop_edge(rows, drop_edge)
    if lone: rows = beadclean.lone_dark(rows)
    rows = loose.fill_pinholes(beadclean.clean(rows))[0]          # revisão: bordas sem contas soltas, halos nem cores avulsas; buraquinhos de 1-3 contas fechados (rosto) preenchidos
    rows = rows if a.get('post') else lg(rows)
    if fix:
        import facetools
        rows = fix(rows) if callable(fix) else facetools.apply_fix(rows, fix)
        if loose.loose_count(rows): rows = loose.fix_loose(rows)
    return rows


ILLCFG = []
CLR = {43: [(840, 960, 1200, 1200)]}      # assinatura SHYRIU
for n, idx, kw, pl in ILL:
    ILLCFG.append((n, CDZ, idx, kw, pl, None, CLR.get(idx, ())))
for idx, lst in SHEET.items():
    for it in lst:
        n, box = it[:2]
        ILLCFG.append((n, CDZ, idx, dict(CH, peel=1.0, **SHEET_KW.get(idx, {})), (None if idx == 45 else 4), box, it[2] if len(it) > 2 else ()))
for n, box in HELMS:
    ILLCFG.append((f'Capacete de {n} (Cavaleiros de Ouro)', CDZ, 86, dict(K=6, dark_frac=0.28, black_L=30.0, dark_L=60.0, thr=235, seal=1.0, sat=1.0, contrast=1.0, sharp=0.0, size=46, post=keep(10)), None, box, ()))

# ---- REPETIDAS (pedido do usuário, 2026-10-30: "elas podem ir na remessa e devem entrar no catálogo, eu vejo depois se apago": a mesma figura pode ter cores ou poucos pixels diferentes)
CFG += [
 ('Toad (Mario, versão 2)', 'Mario', lambda: Plain(12)),
 ('Ash Ketchum (chibi, versão 2)', 'Pokémon', lambda: Plain(27)),
 ('Yami Yugi (pixel, versão 2)', 'Yu-Gi-Oh', lambda: Plain(91, post=lg)),
 ('Seiya de Pégaso (pixel, corpo inteiro, versão 2)', 'Cavaleiros do Zodíaco', lambda: Plain(66, thr=235, post=lg)),
 ('Aranha (pixel, versão 2)', 'Halloween', lambda: G(105, 23)),
 ('Shiryu de Dragão (foto de peça pronta)', 'Cavaleiros do Zodíaco', lambda: Plain(24, tol=70, post=drop_dull)),
]
for k, n in enumerate(['Seiya de Pégaso', 'Hyoga de Cisne', 'Shiryu de Dragão', 'Shun de Andrômeda', 'Ikki de Fênix']):
    CFG.append((f'{n} (pixel, tira dos 5)', 'Cavaleiros do Zodíaco', (lambda k=k: cached('c89', lambda: comps(E(89, achro=170), 5, by_x=True))[k])))

# MD5 repetidas que JÁ estão no catálogo e outras puladas (o usuário disse que manda as repetidas de propósito; só não duplico o que já está lá):
SKIP = {131: 'Ikki: arquivo idêntico ao 130 desta mesma remessa (daria o mesmo molde, byte a byte)'}


def plates_of(rows):
    return -(-max(len(x) for x in rows) // 50) * -(-len(rows) // 50)


if __name__ == '__main__':
    only = [a for a in sys.argv[1:] if not a.startswith('--')]; part = 'ill' if '--ill' in sys.argv else 'chart' if '--chart' in sys.argv else 'all'
    one = []; multi = []; items = []; itemsg = []
    if part != 'ill':
        for n, g, fn in CFG:
            if only and not any(o in n for o in only): continue
            try:
                r5.SKIN_ON = r5.skin_for(n, g)
                r = fn(); one.append((n, g, r)); items.append((f'{n[:24]} {len(r[0])}x{len(r)} p{len(O.components(r))}'.encode('ascii', 'replace').decode(), r))
                if plates_of(r) > 1: multi.append((n + ' (grande)', g, r, {'plates': plates_of(r)}))     # gráfico maior que 1 placa: a cópia exata fica como irmão; add_templates reduz a de 1 placa
            except Exception as e:
                import traceback; traceback.print_exc(); print('ERRO', n, repr(e))
    if part != 'chart':
        for n, g, idx, kw, pl, box, clr in ILLCFG:
            if only and not any(o in n for o in only): continue
            try:
                sk = 'chibi' in n
                r = ill(idx, kw, box=box, size=kw.get('size', 50), skin=sk, clear=clr); one.append((n, g, r)); items.append((f'{n[:24]} {len(r[0])}x{len(r)}'.encode('ascii', 'replace').decode(), r))
                if pl:
                    b = ill(idx, kw, plates=pl, box=box, skin=sk, clear=clr); multi.append((n + ' (grande)', g, b, {'plates': plates_of(b)})); itemsg.append((f'{n[:24]} {len(b[0])}x{len(b)}'.encode('ascii', 'replace').decode(), b))
            except Exception as e:
                import traceback; traceback.print_exc(); print('ERRO', n, repr(e))
    print(len(one), 'moldes de 1 placa,', len(multi), 'grandes')
    if not only and part == 'all':
        json.dump(one, open(os.path.join(SP, 'data', 'final22' + sfx() + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
        json.dump(multi, open(os.path.join(SP, 'data', 'final22_multi' + sfx() + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    if only and '--merge' in sys.argv:       # troca só os moldes filtrados nos JSONs já gravados
        for fn, new in (('final22', one), ('final22_multi', multi)):
            pth = os.path.join(SP, 'data', fn + sfx() + '.json'); old = json.load(open(pth, encoding='utf-8')); by = {x[0]: x for x in new}
            old = [list(by.pop(x[0])) if x[0] in by else x for x in old] + [list(v) for v in by.values()]
            json.dump(old, open(pth, 'w', encoding='utf-8'), ensure_ascii=False)
    tag = part + ('_f' if only else '')
    for k in range(0, len(items), 16):
        render_flat(items[k:k + 16], os.path.join(OUT, f'r20_{tag}_{k // 16}.png'), scale=6, W=1900)
    for k in range(0, len(itemsg), 8):
        render_flat(itemsg[k:k + 8], os.path.join(OUT, f'r20_{tag}_g{k // 8}.png'), scale=5, W=1900)
    print('folhas', (len(items) + 15) // 16, (len(itemsg) + 7) // 8)
