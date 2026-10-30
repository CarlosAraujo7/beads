"""Consertos de rosto (olhos, sobrancelhas, boca) dos moldes que o usuário pediu para melhorar (2026-10-30). Veja tools/faces_apply.py e CLAUDE.md §7.16.
Coordenadas = linha, coluna do MOLDE (a mesma régua das folhas tools/out/ft_*.png). Nos blocos: ' ' não mexe, '.' esvazia, qualquer outro caractere = letra da paleta,
ou o código Pindou da `legend` do próprio conserto (ex.: 'V' -> D7 violeta)."""

FIX = {}


def rm_small(n, keep_largest=False):
    """post: apaga pedaços soltos com menos de n contas (restos de texto/marca do adesivo); keep_largest=True mantém só o maior"""
    def f(rows):
        import numpy as np, cv2, outline as O
        m = np.array([[c != '.' for c in r] for r in rows], np.uint8)
        k, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
        big = max(range(1, k), key=lambda i: st[i][4]) if k > 1 else 0
        out = []
        for y, r in enumerate(rows):
            out.append(''.join(c if (c == '.' or st[lab[y, x]][4] >= n) and (not keep_largest or lab[y, x] == big) else '.' for x, c in enumerate(r)))
        return O.trim(out)
    return f


def clean_specks(rows, max_black=5, fix_inside=True):
    """limpa pontos avulsos: (1) pedaço PRETO pequeno (<= max_black contas, 8-conexo) que encosta no vazio (restos do contorno do adesivo na borda) é apagado — o contorno de verdade é um pedaço grande e fica;
    (2) conta isolada (nenhum vizinho de mesma letra) cercada por >= 3 vizinhos de uma só outra letra ganha a letra deles (o ponto preto/azul perdido no meio do cabelo branco)."""
    import numpy as np, cv2, outline as O
    from collections import Counter
    H, W = len(rows), len(rows[0]); g = [list(r) for r in rows]
    m = np.array([[c == 'k' for c in r] for r in rows], np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    for j in range(1, n):
        if st[j][4] > max_black: continue
        ys, xs = np.nonzero(lab == j)
        touch = any(not (0 <= yy < H and 0 <= xx < W) or g[yy][xx] == '.' for y, x in zip(ys, xs) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)))
        if touch:
            for y, x in zip(ys, xs): g[y][x] = '.'
    for y in range(H):                                     # conta preta de borda ligada ao contorno só pela DIAGONAL (nenhum vizinho preto de lado) = ponto avulso
        for x in range(W):
            if g[y][x] != 'k': continue
            nb = [g[yy][xx] if 0 <= yy < H and 0 <= xx < W else '.' for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))]
            if nb.count('k') == 0 and '.' in nb: g[y][x] = '.'
    for x in (0, W - 1):                                   # coluna da ponta: se só tem uns pontinhos pretos (<= 6), é resto da borda do adesivo
        col = [g[y][x] for y in range(H)]
        if 0 < sum(1 for c in col if c != '.') <= 6 and all(c in '.k' for c in col):
            for y in range(H): g[y][x] = '.'
    if fix_inside:
        for y in range(H):
            for x in range(W):
                c = g[y][x]
                if c == '.': continue
                nb = [g[yy][xx] if 0 <= yy < H and 0 <= xx < W else '.' for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))]
                if nb.count(c) == 0 and '.' not in nb:
                    top, cnt = Counter(nb).most_common(1)[0]
                    if cnt >= 3: g[y][x] = top
    return O.trim([''.join(r) for r in g])


def panda_post(rows):
    import r14_exfinal, r5
    return r5.largest(r14_exfinal.drop_reds(rows))


def grin(top, seps, teeth=2):
    """sorriso de dentes em U (Koro-sensei): top = {coluna: linha da linha de cima}; entre ela e a de baixo ficam `teeth` linhas de dentes brancos; `seps` = colunas dos separadores pretos.
    devolve o dict de contas (linha, coluna) -> letra para o `cells` do conserto."""
    out = {}
    for c, t in top.items():
        out[(t, c)] = 'k'
        for j in range(1, teeth + 1): out[(t + j, c)] = 'k' if c in seps else 'w'
        out[(t + teeth + 1, c)] = 'k'
    return out

FIX['rukia-kuchiki-chibi'] = dict(
    src=(14, 17), conv=dict(dark_L=16, dark_frac=0.30, ncolors=20), skin=True, scale=10,
    legend={'V': 'D7', 'P': 'D15', 'n': 'G7'},
    blocks=[
        # olho esquerdo (do espectador): pálpebra preta, esclera, íris violeta com brilho, pálpebra de baixo marrom
        (18, 6, ['kkkkkk',
                 'kwVwVk',
                 'kwPPPk',
                 ' nnnn ']),
        # olho direito (1 linha mais alto: o rosto está inclinado)
        (16, 16, ['kkkkkkk',
                  'kkkkkkk',
                  'wwwVwVk',
                  'wwwPPPk',
                  ' nnnnn ']),
        (14, 10, ['kk', ' kk']),             # sobrancelha esquerda
        (14, 17, ['kk']), (15, 15, ['kk']),  # sobrancelha direita
    ],
    cells={(23, 14): 'n'},                   # a bocarra torta
)


# ---- convert5 (regiões lisas) + rosto à mão ----------------------------------------------------------------------------------------------------------------------------------------------------
FIX['lelouch-chibi-traje-de-zero'] = dict(
    src=(16, 29), conv5=dict(K=18), skin=True, scale=10,
    legend={'V': 'D7', 'P': 'D15', 'n': 'G7'},
    blocks=[
        (17, 19, ['kkkkkkk']),                                    # pálpebra de cima do olho do Geass
        (20, 8, ['kkkkk']),                                       # pálpebra do olho esquerdo
        (21, 8, ['wwVPV']), (22, 8, ['wwPPw']),                   # esclera + íris violeta com brilho
        (23, 9, ['nnnn']),
        (27, 15, ['nnnn']), (26, 14, ['n']), (26, 19, ['n']),                                       # sorriso discreto (um U raso, marrom: o preto pesava e parecia careta)
    ],
    cells={(24, 15): 'n'},
)

FIX['power-chainsaw-man-chibi'] = dict(
    src=(16, 23), conv5=dict(K=18), skin=True, scale=10,
    legend={'A': 'A6', 'P': 'F10', 'n': 'G7'},
    blocks=[
        # olho esquerdo (cols 9-13, linhas 24-27)
        (24, 9, ['kkkkk', 'kAwAk', 'wAPAk', 'wnAn ']),
        # olho direito (cols 19-25, linhas 20-24)
        (20, 19, [' kkkkk ', 'wkAwAkw', 'wkAPAkw', 'wkAAAkw', '  kkk  ']),
    ],
)

FIX['denji-chainsaw-man-chibi'] = dict(
    src=(16, 18), conv5=dict(K=18), skin=True, scale=10,
    legend={'B': 'F13', 'P': 'F10', 'n': 'G7'},
    blocks=[
        # olho esquerdo (cols 10-17, linhas 19-23): pálpebra grossa, esclera enorme, íris marrom-avermelhada com pupila escura
        (19, 10, ['kkkkkkkk', 'wwBBBwww', 'wwBPBwww', 'wwBBBww ', ' kkkkk  ']),
        # olho direito (cols 23-29, linhas 21-25)
        (21, 23, [' kkkkk ', 'kBBBwwk', 'kBPBwww', ' BBBww ', ' kkkkk ']),
    ],
    recolor=[(31, 33, 10, 20, 'skin', 'H1'), (34, 39, 11, 21, 'skin', 'H1')],       # a camisa branca saía cor de pele (a trava de pele do near120)
)

FIX['killua-zoldyck-chibi'] = dict(
    src=(17, 10), conv5=dict(K=18, pale_skin=True), skin=True, scale=10,
    legend={'B': 'D3', 'P': 'D15', 'c': 'C7', 'n': 'G7'},
    blocks=[(19, 8, ['kkkk', 'BBwB', 'BPPB', 'BBcc']),             # olho esquerdo de 4x4 (íris azul-escura com brilho); o direito sai do espelho (a2=29)
            (24, 13, ['k    k']), (25, 14, ['kkkk'])],               # sorriso
    cells={(24, 15): 'n'},
    sym=[(19, 22, 29, 'L', 8, 11)],
)

FIX['kurapika-chibi-espadas-de-madeira'] = dict(
    src=(17, 50), conv5=dict(K=20, dark_frac=0.36, black_L=14.0), skin=True, scale=10,
    legend={'d': 'H5', 'm': 'H4', 'n': 'G7', 'a': 'A6'},
    blocks=[
        # rosto de 3/4: o olho da direita é maior que o da esquerda (como na ilustração), então os dois são desenhados à parte
        (19, 10, ['kkkkk', 'wdkwk', 'wdkdk', ' kmmk']),
        (19, 19, ['kkkkkk', 'wwdkwk', 'wwdkdk', ' wkmmk']),
    ],
    cells={(25, 16): 'n', (26, 17): 'n'},
)

FIX['himmel-frieren-chibi'] = dict(
    src=(17, 51), conv5=dict(K=18, pale_skin=True), skin=True, scale=10,
    legend={'n': 'G7'},
    pre_recolor=[(17, 20, 10, 22, ['H7'], 'H2')],           # limpa os pedaços pretos soltos da conversão em volta dos olhos
    # OLHOS FECHADOS como na ilustração (pedido do usuário: "pode manter assim, só deixar claro"): dois arcos pretos (⌒) bem marcados; o da esquerda mais baixo (cabeça inclinada)
    cells={(19, 10): 'k', (18, 11): 'k', (18, 12): 'k', (19, 13): 'k',                     # olho esquerdo fechado
           (17, 15): 'k', (16, 16): 'k', (16, 17): 'k', (16, 18): 'k', (17, 19): 'k',      # olho direito fechado
           (17, 20): 'n', (19, 14): 'n', (21, 14): 'n', (21, 15): 'n', (21, 16): 'n', (20, 17): 'n'},   # pinta, nariz, sorriso
)

FIX['senku-ishigami-chibi-bravo'] = dict(
    src=(17, 18), conv5=dict(K=20, dark_frac=0.36, black_L=14.0), skin=True, scale=10,
    legend={'R': 'F5', 'P': 'F8', 'Q': 'F10'},
    blocks=[
        (20, 9, ['QQQQ']),                                                              # sobrancelha grossa esquerda
        (22, 7, ['kkkkkk', 'wPPPPw', 'wRRwRw', 'wRPPRw', ' PRRP ', ' kkkk ']),           # olho esquerdo: íris vermelha com anel escuro, pupila e brilho
        (23, 19, ['QQ     ', 'kkkkkkk', 'kPRwwwk', 'kRPRwwk', ' PRRwk ', ' kkk   ']),   # olho direito (ângulo diferente)
        (29, 12, ['kkkkkkkk', 'wwwwwwww', 'iiiiiiii']),                                  # dentes cerrados
    ],
)

FIX['seu-barriga-chaves'] = dict(
    src=(16, 28), conv5=dict(K=18), skin=True, scale=10,
    legend={'S': 'G2'},
    pre_recolor=[(3, 13, 8, 21, ['H7'], 'G2')],            # as lentes e o bigode saíam num bloco preto só
    blocks=[                                               # óculos de armação grossa (duas lentes com o olho dentro), cabelo preto do lado e o bigodão
        (3, 8,  ['kkkkkkkkkkkkkk',
                 'kSSSkkkkkkkSkk',
                 'kwkSkkSSSSSSkk',
                 'kSSSkkSwkwSSkk',
                 'kkkkkkkkkkkkkk']),
        (9, 8,  [' kkkkkkkk', '  kkkkkkkk', '    kkkkkk', '      kkkk']),
    ],
)


_e_top = {**{c: 20 for c in (9, 10, 26, 27)}, **{c: 21 for c in (11, 12, 13, 23, 24, 25)}, **{c: 22 for c in range(14, 23)}}
FIX['koro-sensei-emblema'] = dict(
    src=(15, 0), conv5=dict(K=18), skin=False, scale=10,
    legend={'j': 'A1'},
    cells={**grin(_e_top, seps={12, 15, 18, 21, 24}), (16, 14): 'k', (16, 22): 'k'},
    recolor=[(8, 14, 11, 17, 'skin', 'A1')],            # o brilho da cabeça saía rosa-pele; é amarelo bem claro
)

_c_top = {**{c: 11 for c in (11, 12, 21, 22)}, **{c: 12 for c in range(13, 21)}}
FIX['koro-sensei-corpo-inteiro'] = dict(
    src=(15, 15), conv5=dict(K=18), skin=False, scale=10,
    cells={**grin(_c_top, seps={13, 16, 19}, teeth=1), (8, 14): 'k', (9, 14): 'k', (8, 19): 'k', (9, 19): 'k'},
)

FIX['ichigo-kurosaki-chibi-adesivo'] = dict(
    src=(13, 10), conv5=dict(K=18), skin=True, scale=10,
    legend={'D': 'F10', 'B': 'F13', 'n': 'G7'},
    blocks=[(19, 9, ['kkkkkk', 'kDwDDk', 'kBBBBk', ' kkkk ']), (25, 14, ['nnnn'])],     # olho esquerdo (o direito sai do espelho) e a boquinha
    sym=[(19, 22, 33, 'L', 9, 14)],
)

FIX['passaro-de-mascara-vermelha-adesivo'] = dict(
    src=(13, 12), conv5=dict(K=18), skin=False, scale=10,
    blocks=[
        (19, 19, ['kkkkkkkkkk', ' wkkkwwww ', ' wkkkwwww ', ' wkkkwwww ', ' kkkkkkkk ']),    # olho grande de pálpebra pesada (direito)
        (19, 6, ['kkkkkk', 'wkkwww', 'wkkwww', 'wkkwww', 'kkkkkk']),                       # olho esquerdo, na borda do desenho
    ],
)

FIX['neferpitou-hunter-x-hunter-adesivo'] = dict(
    src=(17, 19), conv5=dict(K=20, dark_frac=0.22, black_L=16.0), skin=True, scale=10, final=clean_specks,
    legend={'M': 'E7', 'O': 'A6', 'L': 'D12'},
    blocks=[
        (16, 8, ['kkkkk', 'wMkMw', 'wMkMw', 'wOkOw', ' kkkk']),          # olho esquerdo grande: íris magenta, fenda preta, borda dourada; o direito sai do espelho
        (22, 12, ['kLLk', 'kLLk', ' kk ']),                              # boquinha de gato aberta (língua lilás)
    ],
    sym=[(16, 20, 28, 'L', 8, 12)],
)

FIX['robin-jovens-titas-em-pe'] = dict(
    src=(17, 57), conv5=dict(K=18, thr=190, dark_frac=0.5), skin=True, scale=10,
    cells={(15, 11): 'k', (15, 12): 'k'},          # boca emburrada
)


FIX['toji-fushiguro-adesivo'] = dict(
    src=(13, 3), conv5=dict(K=20, dark_frac=0.22, black_L=16.0), skin=True, scale=10, post=rm_small(12),
    legend={'n': 'G7', 'd': 'H5'},
    blocks=[
        (15, 14, ['kkkk', 'wdkw', ' kk ']),                 # olho esquerdo (meio fechado)
        (12, 20, ['kkkkk', 'wdkdw', ' kkk ']),              # olho direito
        (19, 17, ['kk', '  ']), (18, 19, ['kw']),           # sorriso de lado com um dente
    ],
    cells={(19, 17): 'k', (19, 18): 'k', (18, 19): 'k', (18, 20): 'w'},
)

FIX['panda-jujutsu-kaisen'] = dict(
    src=(14, 9, None), conv5=dict(K=20, dark_frac=0.22, black_L=16.0, bg='flat', tol=105), skin=False, scale=10, post=panda_post,
    cells={(10, 25): 'w', (11, 31): 'w'},                   # brilho branco dos olhos
)


# ---- Como Treinar o seu Dragão (os 4) -----------------------------------------------------------------------------------------------------------------------------------------------------
# Banguela (chibi) e (padrão) são a MESMA arte (gráfico da remessa 10 idx 5 / remessa 5 idx 27). A conversão antiga mandava o corpo (37,38,43) e o contorno (19,19,19) para o MESMO preto H7, então a
# cabeça virava uma mancha. Aqui: corpo H6 (cinza-chumbo), contorno H7, asas H4 (colmap do exact6; linhas guardadas por extenso).
_BANG = ['......bb........bb......', '.....beeb......beeb.....', '....beeeb......beeeb....', '....beeeb......beeeb....', '....beeeeb....beeeeb....', '..b..beebbbbbbbbeeb..b..',
         '.beb..bbeeeeeeeebb..beb.', '.beb.beeeeeeeeeeeeb.beb.', '.beebeeeeeeeeeeeeeebeeb.', '..bbeeaaaeeeeeeaaaeebb..', '...beaabdaeeeeadbaaeb...', '...beaabbaeeeeabbaaeb...',
         '...beaabbaeeeeabbaaeb...', '...beeaaaaeeeeaaaaeeb...', '....beeeeeebbeeeeeeb....', '.....bbeeeeeeeeeebb.....', '.......bbbbbbbbbb.......', '...bb...beeeeeeb...bb...',
         '..beeb.beeeeeeeeb.beeb..', '.beecebbeeeeeeeebbeceeb.', '.becccebebeeeebebeccceb.', 'beccccbeebeeeebeebcccceb', 'bccccbbeebeeeebeebbccccb',
         'bcccbebeeebeebeeebebcccb', '.bcbbebeeeebbeeeebebbcb.', '..b.beebeeebbeeebeeb.b..', '.....bb.bbb..bbb.bb.....']
_BANGLEG = {'a': 'B13', 'b': 'H7', 'c': 'H4', 'd': 'H2', 'e': 'H6'}
FIX['banguela-chibi'] = dict(base_rows=_BANG, legend=_BANGLEG, scale=12)
FIX['banguela-padrao'] = dict(base_rows=_BANG, legend=_BANGLEG, scale=12)

# Banguela (Toothless) 29x34 (desenho do Claude, sem fonte): o corpo era cinza-médio e os olhos verde-água; Banguela é preto: corpo H6, asas H4, olhos verde-limão (como no gráfico)
FIX['banguela-toothless'] = dict(
    scale=12,
    recolor=[(0, 33, 0, 28, ['H5'], 'H6'), (0, 33, 0, 28, ['H3'], 'H4'), (0, 33, 0, 28, ['B3'], 'B13')],
)

# Banguela e Fúria da Luz (28x27): o olho verde do Banguela era uma mancha; agora tem íris verde-limão com anel escuro, fenda preta e brilho
FIX['banguela-e-furia-da-luz'] = dict(
    scale=12, legend={'B': 'B13', 'h': 'B8'},
    pre_recolor=[(13, 21, 3, 12, ['B3', 'B8'], 'H7')],              # limpa a mancha verde antiga
    blocks=[(15, 5, [' hhh ', 'hBkwh', 'hBkBh', 'hBkBh', ' hhh '])],
)

# ---- Tsuna (3) ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
FIX['tsuna-chibi-capa-preta'] = dict(
    src=(14, 0), conv5=dict(K=20, dark_frac=0.22, black_L=16.0), skin=True, scale=10,
    legend={'O': 'A7', 'D': 'F8'},
    blocks=[(20, 9, ['kk', 'Ow', 'OO'])],            # olhos grandes laranja (o direito vem do espelho)
    sym=[(20, 22, 25, 'L', 9, 10)],
)

FIX['tsuna-chibi-chama-na-testa'] = dict(
    src=(14, 37), conv5=dict(K=20, dark_frac=0.22, black_L=16.0), skin=True, scale=10,
    legend={'O': 'F4', 'D': 'F8', 'A': 'A7'},
    blocks=[(22, 10, ['kkkkk', 'wDDDk', 'wOOwk', ' AAk ', ' kkk '])],
    sym=[(22, 26, 34, 'L', 10, 14)],
)

FIX['tsuna-x-burner'] = dict(
    src=(14, 40), conv5=dict(K=20, dark_frac=0.22, black_L=16.0), skin=True, scale=10,
    legend={'O': 'F4', 'A': 'A7'},
    blocks=[(15, 14, ['kkkk', 'wOOk', ' OAk']), (16, 18, ['kkkk', 'kOOw', ' OA '])],        # rosto de 3/4: olho da esquerda maior
    cells={(19, 16): 'k', (19, 17): 'w', (19, 18): 'k'},
)

FIX['kuririn-chibi'] = dict(
    src=(14, 43), conv5=dict(K=18), skin=True, scale=10,
    legend={'n': 'G7', 'p': 'E4'},
    blocks=[(12, 9, ['kkkk']), (12, 15, ['kkk']), (15, 8, ['ppp']), (15, 16, ['ppp'])],
    cells={(13, 11): 'n', (13, 16): 'n', (16, 12): 'k', (17, 13): 'k', (16, 14): 'k',          # olhos meio fechados, bochechas e sorriso
           (5, 13): 'n', (5, 14): 'n', (7, 13): 'n', (7, 14): 'n', (9, 13): 'n', (9, 14): 'n'},   # as 6 pintinhas da testa do Kuririn
)

# ---- Kaiju nº 8: os 4 chibis em medalha redonda ---------------------------------------------------------------------------------------------------------------------------------------------
FIX['kikoru-shinomiya-kaiju-n-8-chibi'] = dict(
    src=(16, 11), conv5=dict(K=20, dark_frac=0.22, black_L=16.0, ), skin=True, scale=9,
    legend={'G': 'B2', 'p': 'E4', 'n': 'G7'},
    blocks=[(22, 18, ['kkkkk', 'wGGGw', 'wGkGw', ' GGG ', ' kkk ']), (29, 22, ['nnnnnnn'])],      # olho esquerdo (o direito sai do espelho) e a boca
    cells={(27, 19): 'p', (27, 20): 'p', (27, 30): 'p', (27, 31): 'p'},
    sym=[(22, 26, 50, 'L', 18, 22)],
)

FIX['mina-ashiro-kaiju-n-8-chibi'] = dict(
    src=(16, 15), conv5=dict(K=20, dark_frac=0.22, black_L=16.0, thr=245), skin=True, scale=9,
    legend={'R': 'F7', 'n': 'G7'},
    blocks=[(18, 20, [' kkk ', 'kRRRk', 'kRkwk', ' kkk ']), (27, 26, ['nn'])],
    sym=[(18, 21, 53, 'L', 20, 24)],
)

FIX['kafka-hibino-kaiju-n-8-chibi'] = dict(
    src=(16, 22), conv5=dict(K=20, dark_frac=0.22, black_L=16.0), skin=True, scale=9,
    legend={'n': 'G7'},
    blocks=[(18, 17, ['kkkkkk', 'wwwwww', 'wwwkww', 'wwkkww', ' kkkk ']),                      # olho esquerdo grande, branco, pupila pequena (o direito sai do espelho)
            (16, 18, ['kk']), (17, 20, ['kkk'])],                                              # sobrancelha brava
    sym=[(16, 22, 48, 'L', 17, 23)],
)

FIX['reno-ichikawa-kaiju-n-8-chibi'] = dict(
    src=(16, 26), conv5=dict(K=20, dark_frac=0.22, black_L=16.0), skin=True, scale=9,
    legend={'L': 'D6', 'n': 'G7'},
    blocks=[(17, 24, [' kkkk', 'wLLLk', 'wwkLk', 'wLLLk', ' kkk ']), (21, 16, ['kkk', 'wLk', ' kk'])],     # olho direito grande e olho esquerdo pequeno (rosto de 3/4)
    cells={(27, 22): 'n', (27, 23): 'n'},
)

# ---- pixel art do catálogo antigo ------------------------------------------------------------------------------------------------------------------------------------------------------
# Ichigo (pixel, corpo inteiro): o gráfico original tem 33x62 e o molde é a versão REDUZIDA a 1 placa (27x50), então os olhos viraram 2-3 contas borradas (marrom + lilás). Aqui os dois olhos são redesenhados
# (íris marrom-escura, brilho branco embaixo, voltado para fora); o resto é o molde do catálogo.
FIX['ichigo-kurosaki-pixel-corpo-inteiro'] = dict(
    scale=11, legend={'L': 'F7', 'M': 'F11', 'H': 'H2'},
    blocks=[(8, 8, ['LM', 'HL']), (8, 13, ['ML', 'LH'])],
)

FIX['ezio-auditore-assassin-s-creed'] = dict(
    scale=18, legend={'a': 'A6'},
    cells={(6, 4): 'i', (6, 7): 'i'},            # dois olhos claros no escuro do capuz (era uma faixa preta lisa)
)

# Lady Rainicorn: a cabeça de unicórnio estava LILÁS (D12) e sem olho nem chifre; a arte tem cabeça rosa-clara, olho branco com aro preto, chifre branco de contorno preto e a língua vermelha.
FIX['lady-rainicorn-hora-de-aventura'] = dict(
    scale=10, legend={'P': 'E12', 'y': 'A1'},
    recolor=[(4, 10, 18, 26, ['D12', 'D5'], 'E12'), (9, 9, 22, 24, ['D12'], 'E12')],
    cells={(5, 21): 'k', (5, 22): 'w', (6, 21): 'k', (6, 22): 'w', (6, 23): 'P', (5, 23): 'P',          # olho
           (3, 24): 'w', (2, 25): 'w', (2, 26): 'w', (1, 27): 'k', (3, 25): 'k', (2, 27): 'k',          # chifre
           (9, 22): 'r'},
)

# Guren: as duas gemas dos olhos (azul na testa, verde no peito) tinham se perdido na conversão (viraram vinho)
FIX['guren-code-geass-mecha-de-asas-rosas'] = dict(
    scale=11, legend={'b': 'C8', 'c': 'C5', 'G': 'B4', 'H': 'B2'},
    cells={(14, 16): 'b', (15, 16): 'c', (21, 16): 'G', (21, 17): 'H', (20, 17): 'G'},
)

# Kaiju nº 8 (caveira, círculo): o olho esquerdo da caveira (o da direita na imagem) é um brilho ciano e tinha sumido; o outro estava com 1 conta
FIX['kaiju-n-8-caveira-circulo'] = dict(
    scale=9, legend={'g': 'C2', 'C': 'C5'},
    cells={(23, 21): 'g', (23, 20): 'C', (23, 22): 'C', (22, 21): 'C', (24, 21): 'C', (24, 14): 'g', (24, 13): 'C', (23, 14): 'C', (25, 14): 'C'},
)

# Allen Walker (D.Gray-man, 25x48; foto de uma peça pronta): o rosto tinha só a pele e uma sombra, sem olhos. Dois olhos pretos de 1 conta e a boca.
FIX['allen-walker-d-gray-man'] = dict(
    scale=10, legend={'n': 'G5'},
    cells={(12, 12): 'k', (12, 15): 'k', (14, 13): 'n', (14, 14): 'n'},
)


# ---- 2ª rodada (2026-10-30, retorno do usuário) ------------------------------------------------------------------------------------------------------------------------------------------
def _shun_base():
    import cav_chibis_fix as C
    return C.fix_shun()


# Shun de Andrômeda (chibi), 4ª versão (2026-10-30, "ainda está com os olhos estranhos"). Até aqui eu desenhava o rosto de cabeça: íris azul-petróleo em anel em volta de uma pupila quadrada, mecha em barra verde reta
# entre os olhos e um retângulo de pele. Agora as linhas 22-33 seguem a LEITURA DA FONTE conta a conta (remessa 14 idx 45, grade do molde): olhos nas colunas 10-16 e 21-27 (mesmo desenho, deslocado 11 colunas),
# pálpebra arqueada com cílio, íris redonda cinza H5 (o tom da arte é cinza-esverdeado escuro, (59,83,64); a letra exata B12 é a mesma do cabelo e o olho sumia), pupila em cima, 1 brilho branco voltado para o mesmo lado,
# esclera por fora e embaixo; testa em sombra G3 (a arte tem salmão debaixo do capacete); mecha em CUNHA diagonal com as bordas claras; maxilar afinando até o queixo; nariz de 1 conta e boca discreta G5.
# O capacete (simétrico) e o resto vêm de `cav_chibis_fix.fix_shun`.
FIX['shun-de-andromeda-chibi'] = dict(
    base_fn=_shun_base, scale=10,
    blocks=[
        (22, 13, ['ÑÑÑÑ']),
        (23, 11, ['ÑÑÑÑÑÑÑw   KÑÑÑÑÑ']),
        (24, 16, ['}K   K      }']),
        (25, 9, ['Qkd   d K  Kkd  wdk']),
        (26, 9, ['Q d   dwK K wd  kdw']),
        (27, 11, ['wdddww K  wwddd w']),
        (28, 10, ['Q}   } K   }}  w}}']),
        (29, 12, ['}  }K Ñ    }}}}']),
        (30, 12, ['Q}    }      }']),
        (31, 13, ['}}} }tt   }}']),
        (32, 14, ['}   }}   }']),
        (33, 14, ['t}}    }}K']),
    ],
)


# ---- 10 chibis de One Piece (folha da remessa 13 idx 33; revisão pedida em 2026-10-30, 2 vezes) -----------------------------------------------------------------------------------------------
# A folha é um SPRITE pixel-art (pixel de 3 px): a 1ª versão do catálogo foi convertida a 40 contas e a minha 1ª revisão (olhos desenhados à mão sobre 40 contas) também "não ficou boa". A versão certa é
# converter perto do tamanho NATIVO do sprite: 1 placa = lado maior 50 (quase 1:1) e irmãos "(grande)" no tamanho nativo (`op_chibis.convert_all(native=True)`, 36-71 contas). Os olhos do próprio sprite
# aparecem; NADA é desenhado à mão aqui. Luffy Gear 5 (rosto) e Luffy (chibi grande, pixel) ficam de fora (pedido do usuário).
_OPC = {}


def _op_base(k):
    def f():
        if 'v' not in _OPC:
            import op_chibis; _OPC['v'] = op_chibis.convert_all()[0]
        return _OPC['v'][k]
    return f


for _k, _n in enumerate(['luffy', 'zoro', 'nami', 'chopper', 'usopp', 'sanji', 'nico-robin', 'franky', 'brook', 'jinbe']):
    FIX[_n + '-chibi-one-piece'] = dict(base_fn=_op_base(_k), scale=10)

# ---- Tatsumaki (One Punch Man, chibi): olhos e pernas ------------------------------------------------------------------------------------------------------------------------------------
def _tat_legs():
    """pernas da Tatsumaki redesenhadas à mão (2026-10-30, "as pernas estão estranhas"): na ilustração são duas pernas FINAS (a da esquerda reta, 3 contas de pele entre 2 de contorno; a da direita aparece pela fenda
    do manto e desce em diagonal), com os pés descalços; a conversão tinha fundido tudo num bloco de pele de 13 contas de largura. Cores: contorno H7 'k', pele G1 'c', sombra G3 'd'."""
    cells = {}
    def put(y, x, ch): cells[(y, x)] = ch
    for y in range(40, 46):                       # limpa o bloco de pele antigo (colunas 9-24)
        for x in range(9, 25): put(y, x, '.')
    put(39, 12, 'k'); put(39, 15, 'k'); put(39, 16, 'k')   # a barra do manto sobre a perna esquerda e junto da coxa direita
    for y in (40, 41, 42):                        # perna esquerda
        put(y, 11, 'k'); put(y, 12, 'd'); put(y, 13, 'c'); put(y, 14, 'c'); put(y, 15, 'k')
    put(43, 10, 'k'); [put(43, x, 'c') for x in (11, 12, 13, 14)]; put(43, 15, 'k')                                   # pé esquerdo (dedos para a esquerda)
    put(44, 9, 'k'); [put(44, x, 'c') for x in (10, 11, 12, 13, 14)]; put(44, 15, 'k')
    [put(45, x, 'k') for x in range(9, 16)]
    put(39, 20, 'k')                              # coxa direita (aparece pela fenda do manto): contorno
    put(40, 17, 'k'); put(40, 18, 'c'); put(40, 19, 'c'); put(40, 20, 'k')    # joelho e canela em diagonal
    for y in (41, 42):
        put(y, 18, 'k'); put(y, 19, 'd'); put(y, 20, 'c'); put(y, 21, 'k')
    put(43, 19, 'k'); put(43, 20, 'c'); put(43, 21, 'c'); put(43, 22, 'k')
    put(44, 19, 'k'); [put(44, x, 'c') for x in (20, 21, 22)]; put(44, 23, 'k')                                     # pé direito
    [put(45, x, 'k') for x in range(19, 24)]
    return cells


FIX['tatsumaki-one-punch-man-chibi'] = dict(
    src=(14, 44), conv5=dict(K=20, dark_frac=0.30, black_L=14.0), skin=True, scale=10,
    legend={'G': 'B7', 'g': 'B3', 'n': 'G7', 'p': 'H7', 'c': 'G1', 'd': 'G3'},
    blocks=[(15, 8, ['kkkkkk', ' GwpG ', ' GppG ', ' gggg ']), (15, 17, ['kkkkkk', ' GwpG ', ' GppG ', ' gggg '])],       # olhos verde-esmeralda grandes (pálpebra preta, brilho, pupila)
    cells={(20, 13): 'n', (20, 14): 'n', **_tat_legs()},
)


# ---- Os heróis de armadura de Ryukendo saíram daqui: veja tools/ryukendo.py (2026-10-30). ---------------------------------------------------------------------------------------------------
