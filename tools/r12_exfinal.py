import os, sys, json
os.environ['REMNUM'] = '12'
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import r5, r6, outline as O
from flat import render_flat
E = r6.exact6

# Pikachu de capuz (img 16): o amarelo-limão do capuz a regra geral manda para verde-menta; aqui é amarelo
YEL = [((234, 238, 127), 14, 'y'), ((232, 237, 145), 14, 'y'), ((230, 236, 110), 14, 'y')]
# Aizen (img 18, ponto-cruz): marrons escuros do cabelo caíam em laranja
AIZEN = [((77, 63, 37), 14, 'k'), ((130, 108, 62), 16, 'n')]
# observação: em exact6 o 'clear' é INCLUSIVO e vale antes do trim (as coordenadas são as da grade ainda sem aparar)

CFG = [
 # --- Pokémon
 ('Ash Ketchum (chibi)', 'Pokémon', lambda: E(7)),
 ('Onix', 'Pokémon', lambda: E(8, crop=(1, 42, 1, 34))),
 ('Chibi de fantasia de Pikachu', 'Pokémon', lambda: E(16, colmap=YEL)),
 # --- Reborn (img 3: é o mesmo arquivo da remessa 3, mas o usuário excluiu o molde antigo e pediu para refazer a partir desta imagem; entra com --readd)
 ('Reborn e Leon (Hitman Reborn)', 'Katekyo Hitman Reborn', lambda: E(3, crop_img=(19, 18, 379, 378), px=8.0)),
 # --- animes
 ('Saitama (One Punch Man)', 'One Punch Man', lambda: E(2, ref=(187, 246, 240), tol=40, allbg=True)),
 ('Kyojuro Rengoku (chibi)', 'Demon Slayer', lambda: E(5, crop_img=(17, 17, 561, 543), achro=100, crop=(0, 33, 0, 33))),
 ('Sosuke Aizen (chibi)', 'Bleach', lambda: E(18, mode=True, colmap=AIZEN)),
 ('Izuku Midoriya (Deku, rosto)', 'My Hero Academia', lambda: E(20, crop_img=(14, 24, 494, 624), px=8.0, crop=(0, 75, 0, 59), clear=[(55, 56, 34, 48)])),
 ('Anya Forger (chibi)', 'Spy x Family', lambda: E(22, crop=(1, 38, 1, 33), achro=190)),   # moldura cinza da captura e fundo xadrez (cinza/branco)
 ('Anya Forger (traços brancos)', 'Spy x Family', lambda: E(28, ref=(0, 255, 0), tol=1)),
 ('Levi Ackerman (limpeza, contorno)', 'Attack on Titan', lambda: E(23, crop_img=(24, 24, 656, 584), px=8.0, clear=[(66, 69, 64, 78)])),
 ('Levi Ackerman (limpeza, ponto-cruz)', 'Attack on Titan', lambda: E(24, mode=True, ref=(236, 196, 197), tol=45)),
 ('Megumin (chibi)', 'KonoSuba', lambda: E(31, crop_img=(14, 14, 658, 764))),
 # --- jogos
 ('Ellie (The Last of Us)', 'The Last of Us', lambda: E(4, post=r5.largest)),   # tira 3 pontinhos da marca d'água
 ('Leon S. Kennedy (chibi)', 'Resident Evil', lambda: E(27)),
 ('Zumbi (Plants vs Zombies)', 'Plants vs Zombies', lambda: E(0)),
 ('Zumbi com placa vermelha (Plants vs Zombies)', 'Plants vs Zombies', lambda: E(34)),
 # --- Marvel
 ('Homem-Aranha (traje vermelho e preto, chibi)', 'Marvel', lambda: E(14)),
 ('Homem-Aranha (chibi clássico)', 'Marvel', lambda: E(29)),
 # --- Ben 10
 ('Echo Echo (Ben 10)', 'Ben 10', lambda: E(1)),
 ('Alienígena branco de linhas verdes (Ben 10)', 'Ben 10', lambda: E(6)),
 ('Alienígena inseto de asas azuis (Ben 10)', 'Ben 10', lambda: E(9)),
 ('Heatblast (Ben 10)', 'Ben 10', lambda: E(15)),
 ('XLR8 (Ben 10)', 'Ben 10', lambda: E(17)),
 ('Diamondhead (Ben 10)', 'Ben 10', lambda: E(26)),
 ('Ghostfreak (Ben 10)', 'Ben 10', lambda: E(32)),
 # --- desenhos / quadrinhos / outros
 ('BMO (pixel)', 'Hora de Aventura', lambda: E(10)),
 ('Scott Pilgrim', 'Scott Pilgrim', lambda: E(11, post=lambda r: r[:-1])),   # última linha = ruído da borda da imagem
 ('Slender Man', 'Outros desenhos', lambda: E(13, post=r5.largest)),   # tira o texto "@pixelcharacterswx" e "SlenderMan." (pontinhos soltos)
 ('Criatura redonda preta com chamas azuis', 'Outros desenhos', lambda: E(25)),
 ('Herói de traje amarelo e preto (voando)', 'Outros desenhos', lambda: E(33)),
 ('Foice e martelo', 'Outros desenhos', lambda: E(21)),
 ('Che Guevara (retrato)', 'Outros desenhos', lambda: E(30)),
 ('Retrato com gorro de Natal e cachorro (malha 1)', 'Outros desenhos', lambda: E(19, crop_img=(28, 82, 633, 723), mode=True)),
 ('Retrato de homem de barba (malha 2)', 'Outros desenhos', lambda: E(19, crop_img=(681, 82, 1286, 723), mode=True, ref=(204, 204, 204), tol=18)),
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
    if not only: json.dump(out, open(os.path.join(SP, 'data', 'final14.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for k in range(0, len(items), 12):
        render_flat(items[k:k + 12], os.path.join(OUT, f'r12_x_{k // 12}.png'), scale=8, W=1900)
