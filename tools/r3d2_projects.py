"""Projetos 3D da `remessa 3D 2` (gráficos limpos lidos célula a célula com tools/gridread.py; conferidos por tools/boxsolve.py e pelas conferências do make_3d.py).
Letras (paleta de 120): Ë F10 (terra escura), Ô G9 (terra clara), K B2 (grama), R B13 (grama clara), l H3 (pedra) · abelha: y A4, a A6, Ë F10, Ì F11, 1 C4 (azul), i H1 (cinza), k preto, w branco · árvore: h B8, r F5, v D6, c C5, y A4, w branco.
Os dados foram extraídos por um script único (tools/out/gen_r3d2.py); para refazer a leitura veja os comentários de cada projeto.
"""

# ---------- Bloco de grama do Minecraft (cubo 9×9×9) — gráfico de darcyshamabeadpatterns (Pinterest): 4 laterais do mesmo formato ("cata-vento") ----------
GR_BAIXO = ["..Ô.Ë.Ë..", ".ÔËÔËÔËË.", "ËËlÔÔËÔËË", ".ÔËËËËËl.", "ÔËËlÔËÔËË", ".ÔËËÔËËË.", "ËËËÔËËlÔË", ".ËËËËËÔË.", "..Ô.Ë.Ë.."]
GR_CIMA = ["..K.K.K..", ".KKKKRRK.", "RKRRKKKKK", ".KRKRKKK.", "KKKKKKRKK", ".RKKKKKR.", "RKKKRKKKK", ".KKRKKKK.", "..K.K.R.."]
GR_L1 = [".K.R.K.KK", "KRRKKKRK.", ".ËKËRRÔËË", "ËÔËlËËËÔ.", ".ÔËËÔÔËËË", "ËËÔËËËlË.", ".ËlËËÔËËÔ", "ËÔÔËËËÔË.", ".Ë.Ô.Ë.ËË"]
GR_L2 = [".K.R.K.RK", "KRRKRKRK.", ".ËRËËRËËË", "ËËÔËËËÔË.", ".lËËÔÔËlË", "ËËËËlËËË.", ".ËÔÔËËÔÔË", "ËËËËËlËË.", ".Ô.Ë.Ë.ËË"]
GR_L3 = [".K.K.K.RK", "RKRRKKRK.", ".lËËRRËËË", "ÔËËËËÔÔË.", ".ÔËÔÔËËËË", "ËËlËËËÔË.", ".ËËÔËlËÔË", "ËÔËËÔËÔË.", ".Ë.Ë.Ë.ËË"]
GR_L4 = [".K.R.K.KK", "KRKKRRKR.", ".ËRËËËRËË", "ËËËÔÔËlË.", ".ËÔËËËÔÔË", "ÔËËÔËËËË.", ".ËlËÔÔËËË", "ËËÔËËËËÔ.", ".Ë.Ë.Ô.ËË"]
grama = {
    'id': 'minecraft-bloco-de-grama', 'name': 'Bloco de grama (Minecraft, 9×9×9)', 'level': 'Médio', 'view': [-30, -35], 'box': {'dims': [9, 9, 9], 'skip': []},
    'desc': 'Bloco de grama do Minecraft, um cubo de 9×9×9 contas em 6 peças planas com dentes alternados que se encaixam sem sobrar nem faltar conta (conferido: 386 contas na casca). As 4 laterais têm o mesmo formato (os dentes da direita ficam nas fileiras pares e os da esquerda nas ímpares, então elas vão em volta como um cata-vento) e só mudam as manchinhas de terra; o topo é de grama e a base é de terra. Peças lidas do gráfico (Pinterest @darcyshamabeadpatterns).',
    'pieces': [{'name': 'Topo (grama)', 'qty': 1, 'rows': GR_CIMA}, {'name': 'Base (terra)', 'qty': 1, 'rows': GR_BAIXO},
               {'name': 'Lateral 1', 'qty': 1, 'rows': GR_L1}, {'name': 'Lateral 2', 'qty': 1, 'rows': GR_L2},
               {'name': 'Lateral 3', 'qty': 1, 'rows': GR_L3}, {'name': 'Lateral 4', 'qty': 1, 'rows': GR_L4}],
    'parts': [{'piece': 2, 'face': 'front', 'at': [0, 0, 8]}, {'piece': 3, 'face': 'right', 'at': [8, 0, 8]},
              {'piece': 4, 'face': 'back', 'at': [8, 0, 0]}, {'piece': 5, 'face': 'left', 'at': [0, 0, 0]},
              {'piece': 0, 'face': 'top', 'at': [0, 0, 0]}, {'piece': 1, 'face': 'bottom', 'at': [0, 8, 8]}],
    'steps': ['Monte as 6 peças separadas e passe o ferro em cada uma, dos dois lados, com papel de forno; deixe esfriar sob um peso.',
              'As 4 laterais têm o mesmo formato (dentes na esquerda e na direita, nas fileiras alternadas). Ponha uma ao lado da outra em volta, cada uma encaixando na vizinha, com a grama para cima.',
              'Encaixe a base de terra por baixo e o topo de grama por cima. Se ficar frouxo, uma gota de cola nos cantos.'],
}

# ---------- Abelha do Minecraft (caixa 7×6×11) — gráfico em fundo azul-petróleo ----------
# ATENÇÃO: no gráfico original a última fileira da TRASEIRA estava com os dentes em posições erradas (2 contas em dobro e 2 faltando na casca): corrigida para NN.M.NN.
MB_FRENTE = ["yy.y.ya", ".ayayy.", "k1yya1k", ".kayyk.", "kkyaykk", "ya.y.ay"]
MB_TRAS = ["ËÌ.Ë.ËË", ".ËÌÌËÌ.", "ÌËÌËÌËÌ", ".ÌËËËÌ.", "ÌËÌËÌËË", "ËË.Ì.ËË"]
MB_LAT_E = ["..y.y.a.y..", "ËËyËaËyyayy", ".ËaÌyËyayk.", "ËÌyËaÌayakk", ".ËaÌyËyyyk.", "..y.a.y.a.."]
MB_LAT_D = ["..y.y.a.y..", "yayyaËyÌaÌË", ".kayyÌaËyË.", "kkyayËyËyÌÌ", ".kayaËaÌyË.", "..y.y.y.a.."]
MB_TAMPA = ["..y.y..", "ayayyay", ".yyaay.", "yyayyay", ".ayayy.", "ËÌËËÌËÌ", ".yayay.", "ÌËÌËÌËË", ".ayyay.", "ËËÌËËÌË", "..Ë.Ì.."]
MB_BASE = ["..y.a..", "yayayya", ".yaaay.", "ayyaaay", ".ayyay.", "ÌËÌËÌËË", ".yyaya.", "ËËËÌËÌÌ", ".yaayy.", "ÌËÌËËÌË", "..Ë.Ë.."]
MB_ANT1 = [".k", "kk", "k.", "k."]
MB_ANT2 = ["k.", "k.", "kk", ".k"]
MB_ASA = ["....ww.", "..wwiiw", ".wiiiiw", "wiwwiw.", "wiiiw..", ".www..."]
MB_ASA_ESP = [".ww....", "wiiww..", "wiiiiw.", ".wiwwiw", "..wiiiw", "...www."]
mcbee = {
    'id': 'minecraft-abelha', 'name': 'Abelha do Minecraft (6 peças + antenas e asas)', 'level': 'Difícil', 'view': [-30, -32], 'box': {'dims': [7, 6, 11], 'skip': [6, 7, 8, 9]},
    'desc': 'Abelha do Minecraft: caixa de 7×6×11 contas em 6 peças planas com dentes alternados (conferido: 282 contas na casca). Frente com os olhos (azul e preto), traseira marrom, laterais e tampas listradas de amarelo, âmbar e marrom. As antenas pretas e as duas asas (contas brancas e cinza) não têm posição indicada no gráfico: coloquei as antenas no topo da frente e as asas deitadas sobre a tampa, uma de cada lado. O gráfico original tinha um erro na última fileira da traseira (dentes em posições erradas), corrigido aqui.',
    'pieces': [{'name': 'Frente (olhos)', 'qty': 1, 'rows': MB_FRENTE}, {'name': 'Traseira', 'qty': 1, 'rows': MB_TRAS, 'note': 'última fileira corrigida em relação ao gráfico'},
               {'name': 'Lateral esquerda', 'qty': 1, 'rows': MB_LAT_E, 'note': 'a traseira (marrom) fica do lado esquerdo da peça'},
               {'name': 'Lateral direita', 'qty': 1, 'rows': MB_LAT_D, 'note': 'a frente (amarela) fica do lado esquerdo da peça'},
               {'name': 'Tampa de cima', 'qty': 1, 'rows': MB_TAMPA, 'note': 'a fileira de dentes amarelos fica na frente'},
               {'name': 'Base', 'qty': 1, 'rows': MB_BASE},
               {'name': 'Antena esquerda', 'qty': 1, 'rows': MB_ANT1, 'note': 'posição não indicada no gráfico'},
               {'name': 'Antena direita', 'qty': 1, 'rows': MB_ANT2, 'note': 'posição não indicada no gráfico (gire 180°)'},
               {'name': 'Asa direita', 'qty': 1, 'rows': MB_ASA}, {'name': 'Asa esquerda', 'qty': 1, 'rows': MB_ASA_ESP, 'note': 'espelho da outra'}],
    'parts': [{'piece': 0, 'face': 'front', 'at': [0, 0, 10]}, {'piece': 1, 'face': 'back', 'at': [6, 0, 0]},
              {'piece': 2, 'face': 'left', 'at': [0, 0, 0]}, {'piece': 3, 'face': 'right', 'at': [6, 0, 10]},
              {'piece': 4, 'face': 'top', 'at': [0, 0, 0], 'rot': 2}, {'piece': 5, 'face': 'bottom', 'at': [0, 5, 10]},
              {'piece': 6, 'face': 'left', 'at': [1, -4, 9]}, {'piece': 7, 'face': 'right', 'at': [5, -4, 10], 'rot': 2},
              {'piece': 8, 'face': 'top', 'at': [6, -1, 3]}, {'piece': 9, 'face': 'top', 'at': [-6, -1, 3]}],
    'steps': ['Monte as 10 peças separadas (6 do corpo, 2 antenas e 2 asas) e passe o ferro em cada uma, dos dois lados.',
              'Os dentes alternam de propósito: onde uma parede tem dente, a vizinha tem vão. Comece pela base e erga a frente (com os olhos), a traseira marrom e as duas laterais (a parte amarela de cada lateral fica na frente).',
              'Feche com a tampa de cima (os dentes amarelos ficam do lado da frente). Se ficar frouxo, uma gota de cola nos cantos.',
              'Prenda as antenas no topo da frente e as asas dos dois lados da tampa (a posição é uma sugestão: o gráfico não mostra).'],
}

# ---------- Árvore de Natal de encaixe (2 painéis que se cruzam) — gráfico + foto das peças prontas ----------
AR_A = [".......y.......", ".......y.......", ".....yyyyy.....", "......yyy......", "......yhy......", "......hvh......", ".....hhhrh.....", "......hhh......", ".....hchhh.....", "....hwhhhyh....", ".....hhhhh.....", "....yhhhhhh....", "...hhhh.hvhh...", "....hvh.hhc....", "...hhhh.hhhh...", "..hhhh..hhyhh..", "...hrhh.hhhh...", "..hhhhh.hrhhh..", ".hhyhhh.hhhhhh.", "..hhhvh.hhhch..", ".hchhhh.hwhhhh.", "hhhhhhh.hhhhhhh"]
AR_B = ["hhhhhhhhhhhhhhh", ".hhrhhvhhhhhyh.", "..hhhhhhwhhhh..", ".hhhwhhhhhchhh.", "..hhhhhhhhhhh..", "...hhhvhhhhv...", "..hhhhhhhrhhh..", "...hhhhhhhhh...", "....hchhhhh....", "...hhhhhhhyh...", "....vhh.hhh....", ".....hh..h.....", "....hrh.hhh....", ".....hh.hv.....", "......h.h......", ".....yh.ch.....", "......h.h......", "......y.y......", "......y.y......", ".....yy.yy....."]
arvore = {
    'id': 'arvore-de-natal-encaixe', 'name': 'Árvore de Natal de encaixe (2 peças)', 'level': 'Fácil', 'view': [-14, -35], 'disjoint': True,
    'desc': 'Árvore de Natal feita de 2 painéis do mesmo tamanho que se cruzam em ângulo reto: um tem a fenda aberta por baixo e o outro (desenhado de cabeça para baixo no gráfico) tem a fenda aberta por cima. Enfeites coloridos e brancos (os 4 brancos são contas brancas, como na foto das peças prontas) e uma estrela amarela. Peças lidas do gráfico e conferidas com a foto.',
    'pieces': [{'name': 'Árvore com a estrela (fenda por baixo)', 'qty': 1, 'rows': AR_A}, {'name': 'Árvore de cabeça para baixo (fenda por cima)', 'qty': 1, 'rows': AR_B, 'note': 'no gráfico ela aparece invertida: monte como no desenho e, ao encaixar, vire-a de pé'}],
    'parts': [{'piece': 0, 'face': 'front', 'at': [0, 0, 7]}, {'piece': 1, 'face': 'right', 'at': [7, 2, 14], 'rot': 2}],
    'steps': ['Monte as 2 peças (a da estrela e a invertida) e passe o ferro em cada uma, dos dois lados.',
              'Vire a peça invertida de pé (de cabeça para baixo ela vira uma árvore normal, com as duas pontas amarelas em cima).',
              'Encaixe uma na outra pelas fendas, em cruz: a fenda de baixo de uma recebe a parte de baixo da outra.'],
}

R3D2 = [grama, mcbee, arvore]
