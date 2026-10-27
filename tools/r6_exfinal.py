import sys, os, json
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import r6, outline as O
from flat import render_flat
E = r6.exact6
import numpy as np, colorsys
def _hsv(c):
    h, s, v = colorsys.rgb_to_hsv(*(np.array(c) / 255)); return h * 360, s, v

# ---- Shiryu (foto sobre madeira): fundo = madeira e cinzas ligados a borda; verde-agua vira verde menta / verde escuro
def _bg10(c):
    h, s, v = _hsv(c); warm = (h <= 50 or h >= 324)
    return 0.28 <= v < 0.82 and (s < 0.12 or (warm and s < 0.42))
def _mp10(c):
    h, s, v = _hsv(c)
    if 160 <= h <= 190 and s >= 0.5 and v >= 0.3: return 'h' if v < 0.6 else 'g'
def shiryu(): return r6.photo6(10, 8.5, spread=0.3, bgfn=_bg10, minsize=3, mapper=_mp10)[0]

# ---- Mimikyu (foto sobre pegboard escuro): so contam bege/ocre/marrom (quentes) e preto; o resto e a placa
def _design15(c):
    h, s, v = _hsv(c)
    return v < 0.14 or (18 <= h <= 48 and s >= 0.38 and v >= 0.36)
def _mp15(c):
    h, s, v = _hsv(c)
    if v < 0.14: return 'k'
    if v >= 0.78: return 's'
    if v >= 0.64: return 's'
    return 'n'
def mimikyu(): return r6.photo6(15, 27, spread=0.06, angles=np.arange(-3, 3.1, 1.0), bgfn=lambda c: not _design15(c), keepbg=True, minsize=2, mapper=_mp15)[0]
CFG = [
 # --- Cavaleiros do Zodíaco
 ('Shun de Andrômeda', 'Cavaleiros do Zodíaco', lambda: E(0)),
 ('Seiya de Pégaso', 'Cavaleiros do Zodíaco', lambda: E(25, crop=(0, 47, 0, 53), dist=24)),
 ('Hyoga de Cisne', 'Cavaleiros do Zodíaco', lambda: E(33)),
 ('Ikki de Fênix', 'Cavaleiros do Zodíaco', lambda: E(47)),
 # --- Naruto / One Piece / Dragon Ball / outros animes
 ('Naruto (chibi com Rasengan)', 'Naruto', lambda: E(1, clear=[(0, 4, 21, 30)])),
 ('Naruto Modo Sapo', 'Naruto', lambda: E(34)),
 ('Ace (chibi)', 'One Piece', lambda: E(2)),
 ('Zoro (chibi, versão 2)', 'One Piece', lambda: E(36, crop=(0, 47, 4, 33))),
 ('Jolly Roger de Trafalgar Law', 'One Piece', lambda: E(39)),
 ('Goku (chibi, versão 2)', 'Dragon Ball', lambda: E(9)),
 ('Gogeta Super Saiyajin 4', 'Dragon Ball', lambda: E(19)),
 ('Gojo (chibi)', 'Jujutsu Kaisen', lambda: E(18)),
 ('Gojo (chibi roxo)', 'Jujutsu Kaisen', lambda: E(24, px=22.02, mode=True, dist=14, crop=(1, 32, 1, 20))),
 ('Gon Freecss', 'Hunter x Hunter', lambda: E(46, crop=(1, 59, 1, 33))),
 # --- super-heróis
 ('Hulk (chibi)', 'Super-heróis', lambda: E(23)),
 ('Superman (chibi)', 'Super-heróis', lambda: E(30, achro=190)),
 ('Wolverine (Logan chibi)', 'Super-heróis', lambda: E(32)),
 ('Wolverine (máscara)', 'Super-heróis', lambda: E(45)),
 ('Power Ranger Vermelho', 'Outros filmes e séries', lambda: E(6, crop=(2, 47, 1, 28), clear=[(0, 2, 0, 6)])),
 # --- desenhos
 ('Taz (Diabo da Tasmânia)', 'Looney Tunes', lambda: E(14)),
 ('Patolino de vestido', 'Looney Tunes', lambda: E(35, achro=200)),
 ('Docinho (Meninas Superpoderosas)', 'Meninas Superpoderosas', lambda: E(28)),
 ('Lindinha (Meninas Superpoderosas)', 'Meninas Superpoderosas', lambda: E(37)),
 ('Mojo Jojo', 'Meninas Superpoderosas', lambda: E(42)),
 ('Ravena (Jovens Titãs)', 'Outros desenhos', lambda: E(22)),
 ('Omnitrix (Ben 10)', 'Outros desenhos', lambda: E(27)),
 ('Remy (Ratatouille)', 'Disney', lambda: E(29, grad=14)),
 ('Calcifer', 'Studio Ghibli', lambda: E(40)),
 ('Menino de boné com bola', 'Outros desenhos', lambda: E(21)),
 ('Criatura cinza espinhosa', 'Outros desenhos', lambda: E(41)),
 ('Monstro azul peludo', 'Outros desenhos', lambda: E(44)),
 ('Cavaleiro de Ouro', 'Cavaleiros do Zodíaco', lambda: r6.ring_render(4, colmap=[((240, 242, 167), 30, 'y'), ((244, 235, 108), 20, 'y'), ((249, 209, 16), 25, 'a')])),
 ('Shiryu de Dragão (foto)', 'Cavaleiros do Zodíaco', shiryu),
 ('Mimikyu (foto)', 'Pokémon', mimikyu),
 ('Stitch (rosto grande)', 'Disney', lambda: E(43, crop_img=(0, 0, 1152, 970))),
 ('Angel (Lilo & Stitch)', 'Disney', lambda: E(43, crop_img=(0, 975, 1152, 2048), colmap=[((105, 53, 71), 30, 'n'), ((120, 83, 89), 24, 't')])),
 ('Stitch sobre livros', 'Disney', lambda: E(17)),
 # --- jogos
 ('Espada de diamante (Minecraft)', 'Outros jogos', lambda: E(12)),
 ('Girassol (Plants vs Zombies)', 'Outros jogos', lambda: E(38)),
 # --- símbolos e animais
 ('Nossa Senhora Aparecida (padrão)', 'Símbolos e objetos', lambda: E(5, colmap=[((128, 173, 230), 34, 'e')])),
 ('Olho de Hórus', 'Símbolos e objetos', lambda: E(7)),
 ('Planeta Terra', 'Símbolos e objetos', lambda: E(8)),
 ('Esfera vermelha manchada', 'Símbolos e objetos', lambda: E(13)),
 ('Faraó (mini)', 'Símbolos e objetos', lambda: E(16)),
 ('Esfinge', 'Símbolos e objetos', lambda: E(20)),
 ('Ankh (cruz egípcia)', 'Símbolos e objetos', lambda: E(26, allbg=True)),
 ('Cabeça de lobo', 'Animais', lambda: E(3, colmap=[((190, 147, 80), 26, 'a')])),
]
if __name__ == '__main__':
    only = [a for a in sys.argv[1:]]
    out = []; items = []
    for n, g, fn in CFG:
        if only and not any(o in n for o in only): continue
        try:
            __import__('r5').SKIN_ON = __import__('r5').skin_for(n, g)
            r = fn(); out.append((n, g, r)); items.append((f'{n[:26]} {len(r[0])}x{len(r)} p{len(O.components(r))}'.encode('ascii', 'replace').decode(), r))
        except Exception as e:
            import traceback; traceback.print_exc(); print('ERRO', n, repr(e))
    print(len(out), 'templates')
    if not only: json.dump(out, open(os.path.join(SP, 'data', 'final8' + __import__('palette').sfx() + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for k in range(0, len(items), 10):
        render_flat(items[k:k + 10], os.path.join(OUT, f'r6_x_{k // 10}' + __import__('palette').sfx() + '.png'), scale=8, W=1900)
