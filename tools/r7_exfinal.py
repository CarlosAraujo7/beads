import os, sys, json
os.environ['REMNUM'] = '7'
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import r6, outline as O
from flat import render_flat
E = r6.exact6
import numpy as np, colorsys
import r5
from PIL import Image
# ---- Visão (foto de peça pronta sobre parede clara): lattice + limpeza de cinzas/sombras
def _bg7(c):
    h, s, v = colorsys.rgb_to_hsv(*(np.array(c) / 255)); return v >= 0.72 and s < 0.22
_MP7 = {'n': 'r', 't': 'r', 'a': 'y', 'o': 'y', 'f': 'h', 'm': '.', 'd': '.', 'l': '.', 'i': '.'}
def _post7(rows): return O.drop_specks(O.trim([''.join(_MP7.get(ch, ch) for ch in r) for r in rows]), maxsize=3)
def visao(): return r6.photo6(7, 29, spread=0.12, angles=np.arange(-3, 3.1, 1.0), bgfn=_bg7, minsize=3, tmp='r7_tmp7.png', post=_post7)[0]
CFG = [
 # --- Pokémon: Eevee e evoluções em Pokébola
 ('Glaceon na Pokébola', 'Pokémon', lambda: E(3)),
 ('Eevee na Pokébola', 'Pokémon', lambda: E(4)),
 ('Vaporeon na Pokébola', 'Pokémon', lambda: E(14)),
 ('Sylveon na Pokébola', 'Pokémon', lambda: E(15)),
 ('Espeon na Pokébola', 'Pokémon', lambda: E(16)),
 ('Flareon na Pokébola', 'Pokémon', lambda: E(22)),
 ('Leafeon na Pokébola', 'Pokémon', lambda: E(29)),
 ('Jolteon na Pokébola', 'Pokémon', lambda: E(33)),
 ('Pokébola (fundo amarelo)', 'Pokémon', lambda: E(27)),
 ('Gengar (padrão)', 'Pokémon', lambda: E(25)),
 ('Clefairy e Gengar', 'Pokémon', lambda: E(12, crop=(0, 58, 0, 56))),
 ('Pikachu de asas (azul)', 'Pokémon', lambda: E(10)),
 ('Pikachu com capuz de Vulpix', 'Pokémon', lambda: E(31, crop=(3, 62, 4, 48))),
 ('Charmander (versão 2)', 'Pokémon', lambda: E(28, crop=(0, 44, 0, 42))),
 # --- animes
 ('Naruto (cabeça chibi)', 'Naruto', lambda: E(9)),
 ('Sasuke (chibi cabeça)', 'Naruto', lambda: E(20, clear=[(27, 40, 0, 40)])),
 ('Sasuke (chibi de corpo inteiro)', 'Naruto', lambda: E(39)),
 ('Shinobu Kocho (chibi)', 'Demon Slayer', lambda: E(23)),
 ('Kaneki (Tokyo Ghoul)', 'Outros animes', lambda: E(8)),
 ('Rem (Re:Zero)', 'Outros animes', lambda: E(5)),
 ('Asta (Black Clover)', 'Outros animes', lambda: E(18)),
 ('Garota de cabelo castanho (chibi)', 'Outros animes', lambda: E(1)),
 ('Chibi de casaco preto', 'Outros animes', lambda: E(37)),
 # --- Winx
 ('Bloom (Winx)', 'Winx', lambda: E(13, crop=(0, 33, 0, 37))),
 ('Stella (Winx)', 'Winx', lambda: E(32, clear=[(10, 15, 28, 33)])),
 ('Tecna (Winx)', 'Winx', lambda: E(34, clear=[(20, 23, 19, 24)])),
 ('Flora (Winx)', 'Winx', lambda: E(38)),
 # --- super-heróis e filmes
 ('Logo do Superman', 'Super-heróis', lambda: E(36, crop=(9, 29, 0, 25))),
 ('Homem de terno (pixel)', 'Outros filmes e séries', lambda: E(19)),
 ('Homem de terno (chibi)', 'Outros filmes e séries', lambda: E(26)),
 # --- desenhos / memes
 ('Lindinha (rosto pequeno)', 'Meninas Superpoderosas', lambda: E(11, crop=(1, 8, 2, 15))),
 ('Florzinha (rosto pequeno)', 'Meninas Superpoderosas', lambda: E(11, crop=(10, 20, 2, 15))),
 ('Docinho (rosto pequeno)', 'Meninas Superpoderosas', lambda: E(11, crop=(22, 29, 2, 15))),
 ('Gato banana (Banana Cat)', 'Outros desenhos', lambda: E(0)),
 # --- jogos
 ('Dinossauro do Chrome', 'Outros jogos', lambda: E(2)),
 ('Pou (padrão)', 'Outros jogos', lambda: E(6, achro=200)),
 ('Shadow (Sonic)', 'Outros jogos', lambda: E(35, crop=(0, 42, 0, 31))),
 ('Okarun (Dan Da Dan)', 'Outros animes', lambda: E(30, px=14.25, mode=True, dist=22, crop=(1, 30, 2, 30), achro=185, clear=[(0, 2, 20, 40), (27, 40, 0, 40)])),
 ('Visão (Marvel)', 'Super-heróis', visao),
 ('Agulha de Irídio (Stardew Valley)', 'Outros jogos', lambda: E(17, crop_img=(223, 126, 512, 416))),
 ('Machado de Irídio (Stardew Valley)', 'Outros jogos', lambda: E(24, crop_img=(115, 155, 619, 628))),
 # --- símbolos
 ('Roda de cores (arco-íris)', 'Símbolos e objetos', lambda: E(21)),
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
    if not only: json.dump(out, open(os.path.join(SP, 'data', 'final9.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for k in range(0, len(items), 10):
        render_flat(items[k:k + 10], os.path.join(OUT, f'r7_x_{k // 10}.png'), scale=8, W=1900)
