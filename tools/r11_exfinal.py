import os, sys, json
os.environ['REMNUM'] = '11'
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import r5, r6, outline as O
from flat import render_flat
E = r6.exact6

def cblocks(rows):
    """separa em blocos por colunas vazias (personagens lado a lado na mesma imagem)"""
    W = len(rows[0]); out = []; cur = []
    for x in range(W):
        if all(r[x] == '.' for r in rows):
            if cur: out.append(cur); cur = []
        else: cur.append(x)
    if cur: out.append(cur)
    return [O.trim([''.join(r[x] for x in xs) for r in rows]) for xs in out]

def rsplit(rows, y):
    """separa em dois pedaços por uma linha (de cima e de baixo)"""
    return O.trim(rows[:y]), O.trim(rows[y:])

# gráfico numerado 19x29 (img 3): passo forçado depois de recortar os números das bordas
G3 = dict(crop_img=(22, 22, 440, 661), px=21.95, mode=True,
          colmap=[((184, 182, 88), 14, 'a'),      # tom escuro do cabelo (10 no gráfico) -> âmbar, para manter o sombreado
                  ((103, 84, 32), 14, 'n'),       # 11 no gráfico: sombra dos olhos -> marrom
                  ((246, 236, 229), 10, 'w')])    # 7 = branco
# gráfico pixiecraft 32x48 (img 13) e 30x48 (img 7): passo forçado, mode=True ignora os códigos escritos nas células
G13 = dict(px=dict(px=30.05, py=30.23, ox=94.4, oy=249, W=32, H=48), mode=True)
G7 = dict(px=dict(px=15.3, py=15.3, ox=15, oy=15, W=30, H=48), mode=True, dist=3,
          # E16 = pele clarinha (a marca d'água clareia algumas células; sem isso a pele virava branco)
          colmap=[((252, 243, 236), 4, 's'), ((254, 249, 244), 4, 's'), ((246, 235, 229), 4, 's')])
SKIN14 = [((253, 235, 229), 8, 's')]

_SLAM = []
# pele oliva do Akagi (148,131,79 e tons vizinhos): a paleta não tem oliva; âmbar fica laranja demais, então vai tudo para marrom G7
OLIVE = [((148, 131, 79), 24, 'n'), ((137, 122, 59), 24, 'n'), ((155, 144, 87), 20, 'n'), ((126, 117, 72), 20, 'n'),
         ((79, 58, 23), 18, 'n'), ((100, 70, 22), 18, 'n')]   # marrons escuros do chapéu (a regra geral os mandava para o salmão G5)
def slam():
    """painel do Slam Dunk (img 8): 3 personagens em cima; chapéu+óculos, bola e Akagi embaixo. A assinatura 'ADAPT BY ZMOMO' (linhas 102-103) é apagada."""
    if not _SLAM:
        r = [list(row) for row in E(8, colmap=OLIVE)]
        for y in (102, 103):
            for x in range(33, 62): r[y][x] = '.'
        r = [''.join(row) for row in r]
        _SLAM.extend(cblocks(r[:51]) + cblocks(r[51:]))
    return _SLAM

CFG = [
 # --- Demon Slayer
 ('Tanjiro Kamado (chibi)', 'Demon Slayer', lambda: E(0)),
 ('Inosuke (máscara de javali)', 'Demon Slayer', lambda: E(1)),
 # --- Dragon Ball / Naruto
 ('Gogeta Super Saiyajin (pixel)', 'Dragon Ball', lambda: E(4)),
 # Naruto de corpo inteiro (img 5): é a mesma arte de 'Naruto (corpo inteiro)', que já está no catálogo (99% iguais); não entra de novo
 ('Sakura Haruno (chibi de corpo inteiro)', 'Naruto', lambda: E(7, **G7)),
 ('Sakura Haruno (chibi, cabelo longo)', 'Naruto', lambda: E(13, **G13)),
 ('Sakura Haruno (chibi cabeça)', 'Naruto', lambda: E(12, colmap=[((255, 239, 223), 8, 's')])),   # rosto creme (senão vira branco)
 # --- Fullmetal Alchemist
 ('Edward Elric (pixel)', 'Fullmetal Alchemist', lambda: E(15)),
 # --- Bob Esponja / Duolingo
 ('Patrick e Bob Esponja (pixel)', 'Bob Esponja', lambda: E(10)),
 ('Coruja do Duolingo (versão 2)', 'Duolingo', lambda: E(9)),
 # --- Soul Eater (painel com 4 chibis)
 ('Crona (chibi)', 'Soul Eater', lambda: E(14, crop_img=(0, 0, 1152, 1255), colmap=SKIN14, crop=(1, 19, 2, 17))),
 ('Soul Eater Evans (chibi)', 'Soul Eater', lambda: E(14, crop_img=(0, 0, 1152, 1255), colmap=SKIN14, crop=(1, 19, 17, 33))),
 ('Maka Albarn (chibi)', 'Soul Eater', lambda: E(14, crop_img=(0, 0, 1152, 1255), colmap=SKIN14, crop=(19, 37, 2, 17))),
 ('Death the Kid (chibi)', 'Soul Eater', lambda: E(14, crop_img=(0, 0, 1152, 1255), colmap=SKIN14, crop=(19, 37, 17, 34))),
 # --- Slam Dunk (painel com 5 personagens e a bola)
 ('Chibi de regata azul e sacola vermelha (Slam Dunk)', 'Slam Dunk', lambda: slam()[0]),
 ('Hanamichi Sakuragi (Slam Dunk)', 'Slam Dunk', lambda: slam()[1]),
 ('Chibi de cabelo preto espetado e sacola vermelha (Slam Dunk)', 'Slam Dunk', lambda: slam()[2]),
 ('Chibi de chapéu e óculos escuros (Slam Dunk)', 'Slam Dunk', lambda: slam()[3]),
 ('Bola de basquete', 'Slam Dunk', lambda: slam()[4]),
 ('Takenori Akagi (Slam Dunk)', 'Slam Dunk', lambda: slam()[5]),
 # --- emblemas do painel do Soul Eater (img 14, parte de baixo)
 ('Lua sorridente (Soul Eater, com contorno)', 'Soul Eater', lambda: E(14, crop_img=(0, 1262, 560, 1940))),
 ('Alma negra com rosto (Soul Eater)', 'Soul Eater', lambda: E(14, crop_img=(578, 1290, 1120, 1925), tol=48, post=r5.largest)),
 # --- sem franquia identificada
 ('Taco', 'Outros desenhos', lambda: E(6, crop=(0, 19, 0, 21))),   # tira a marca d'água do canto (última linha)
 ('Chibi loiro de camisa branca', 'Outros animes', lambda: E(3, **G3)),
 ('Chibi de cabelo branco e joia na testa', 'Outros animes', lambda: E(16, clear=[(16, 29, 0, 2), (16, 29, 19, 22)])),   # tira as etiquetas da marca d'água (amarela e azul)
]
if __name__ == '__main__':
    only = sys.argv[1:]
    out = []; items = []
    for n, g, fn in CFG:
        if only and not any(o in n for o in only): continue
        try:
            r = fn(); out.append((n, g, r)); items.append((f'{n[:26]} {len(r[0])}x{len(r)} p{len(O.components(r))}'.encode('ascii', 'replace').decode(), r))
        except Exception as e:
            import traceback; traceback.print_exc(); print('ERRO', n, repr(e))
    print(len(out), 'templates')
    if not only: json.dump(out, open(os.path.join(SP, 'data', 'final13.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for k in range(0, len(items), 12):
        render_flat(items[k:k + 12], os.path.join(OUT, f'r11_x_{k // 12}.png'), scale=8, W=1900)
