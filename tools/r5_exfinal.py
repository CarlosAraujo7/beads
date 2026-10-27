import sys, os, json
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import r5, r5_final, outline as O
from flat import render_flat
E = r5.exact
import palette as _P
_WM = 'tsqo' if _P.MODE == '24' else ''.join(c['letter'] for c in _P.ALL if c['code'] in ('G5', 'G1', 'E2', 'A7', 'E1', 'E11', 'E14', 'E15', 'G2', 'G3', 'A12', 'G9', 'A9', 'A10', 'G6'))
wm = lambda y0: (lambda r: [x if y < y0 else ''.join('.' if c in _WM else c for c in x) for y, x in enumerate(r)])   # texto/marca d'agua no pe
CFG = [
 ('Homem-Aranha (chibi)', 'Super-heróis', lambda: E(1)),
 ('Deadpool', 'Super-heróis', lambda: E(3)),
 ('Batman (pixel)', 'Super-heróis', lambda: E(9, post=wm(34))),
 ('Groot (no vaso)', 'Super-heróis', lambda: E(13)),
 ('Homem de Ferro (chibi)', 'Super-heróis', lambda: E(18)),
 ('Yoshi', 'Mario', lambda: E(4)),
 ('Mario (pixel)', 'Mario', lambda: E(38)),
 ('Cogumelo laranja', 'Mario', lambda: E(10)),
 ('Kurama (Raposa de Nove Caudas)', 'Naruto', lambda: E(5)),
 ('Kakashi (pixel)', 'Naruto', lambda: E(6)),
 ('Naruto (corpo inteiro)', 'Naruto', lambda: E(15)),
 ('Naruto (chibi cabeçudo)', 'Naruto', lambda: E(31)),
 ('Vegeta Super Saiyajin Blue (pixel)', 'Dragon Ball', lambda: E(11)),
 ('Goku (chibi pixel)', 'Dragon Ball', lambda: E(17, thr=205)),
 ('Goku (em pé)', 'Dragon Ball', lambda: E(23)),
 ('Majin Boo', 'Dragon Ball', lambda: r5.sprite_exact(35)),
 ('Ichigo Kurosaki', 'Bleach', lambda: r5.sprite_exact(34)),
 ('Sabo', 'One Piece', lambda: r5.sprite_exact(41)),
 ('Sanji', 'One Piece', lambda: r5.sprite_exact(42)),
 ('Trafalgar Law', 'One Piece', lambda: r5.sprite_exact(44)),
 ('Zoro (pixel)', 'One Piece', lambda: E(39, px=20.0, tol=40)),
 ('Crash Bandicoot', 'Outros jogos', lambda: E(16)),
 ('Togepi (pixel)', 'Pokémon', lambda: E(20, thr=215)),
 ('Bulbasaur (versão azul)', 'Pokémon', lambda: E(32)),
 ('Grogu (Baby Yoda) no berço', 'Star Wars', lambda: E(14, post=lambda r: r5.largest(r))),
 ('Sem-Rosto com coração', 'Studio Ghibli', lambda: E(2)),
 ('Sem-Rosto (mini)', 'Studio Ghibli', lambda: E(8)),
 ('Haku (Viagem de Chihiro)', 'Studio Ghibli', lambda: E(0, thr=232, drop='x', post=lambda r: r5.largest(r))),
 ('Haku (versão pastel)', 'Studio Ghibli', lambda: E(19, thr=215, drop='x', clear=[(0, 28, 54, 60), (3, 8, 2, 15), (0, 68, 0, 2), (0, 2, 0, 59)])),
 ('Hello Kitty zumbi', 'Hello Kitty', lambda: E(22)),
 ('Hello Kitty Homem-Aranha', 'Hello Kitty', lambda: E(30, post=lambda r: r5.largest(r))),
 ('Banguela (padrão)', 'Como Treinar o seu Dragão', lambda: E(27, thr=215, crop=(16, 45, 2, 29))),
 ('Jesus (chibi)', 'Símbolos e objetos', lambda: E(26)),
 ('Chibi de óculos e maria-chiquinha', 'Outros animes', lambda: E(12)),
]
if __name__ == '__main__':
    out = []; items = []
    for n, g, fn in CFG + r5_final.EXTRA[2:]:
        try:
            __import__('r5').SKIN_ON = __import__('r5').skin_for(n, g)
            r = fn(); out.append((n, g, r)); items.append((f'{n[:24]} {len(r[0])}x{len(r)} p{len(O.components(r))}'.encode('ascii', 'replace').decode(), r))
        except Exception as e:
            print('ERRO', n, repr(e))
    json.dump(out, open(os.path.join(SP, 'data', 'final7' + __import__('palette').sfx() + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(len(out), 'templates')
    for k in range(0, len(items), 10):
        render_flat(items[k:k + 10], os.path.join(OUT, f'r5_x_{k // 10}' + __import__('palette').sfx() + '.png'), scale=8, W=1900)
