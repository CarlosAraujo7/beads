import sys, os, json
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import r5, outline as O

def head_cream(rows, until=10):       # topo do Togepi: creme, nao cinza claro
    return [r.replace('i', 's') if y < until else r for y, r in enumerate(rows)]

CFG = [
 # (nome, serie, funcao)
 ('Homem-Aranha (chibi)', 'Super-heróis', lambda: r5.pat(1)),
 ('Deadpool', 'Super-heróis', lambda: r5.pat(3)),
 ('Batman (pixel)', 'Super-heróis', lambda: r5.pat(9, post=lambda r: [x if y < 34 else ''.join('.' if c in 'tsqo' else c for c in x) for y, x in enumerate(r)])),
 ('Groot (no vaso)', 'Super-heróis', lambda: r5.pat(13, mp={'o': 'n', 'a': 'n'})),
 ('Homem de Ferro (chibi)', 'Super-heróis', lambda: r5.pat(18)),
 ('Yoshi', 'Mario', lambda: r5.pat(4)),
 ('Mario (pixel)', 'Mario', lambda: r5.pat(38, colors=True)),
 ('Cogumelo laranja', 'Mario', lambda: r5.pat(10)),
 ('Kurama (Raposa de Nove Caudas)', 'Naruto', lambda: r5.pat(5)),
 ('Kakashi (pixel)', 'Naruto', lambda: r5.pat(6)),
 ('Naruto (corpo inteiro)', 'Naruto', lambda: r5.pat(15)),
 ('Naruto (chibi cabeçudo)', 'Naruto', lambda: r5.pat(31)),
 ('Vegeta Super Saiyajin Blue (pixel)', 'Dragon Ball', lambda: r5.pat(11, mp={'f': 'c', 'h': 'b', 'g': 'c'})),
 ('Goku (chibi pixel)', 'Dragon Ball', lambda: r5.pat_flood(17, thr=205)),
 ('Goku (em pé)', 'Dragon Ball', lambda: r5.pat(23, colors=True)),
 ('Majin Boo', 'Dragon Ball', lambda: r5.sprite(35)),
 ('Ichigo Kurosaki', 'Bleach', lambda: r5.sprite(34)),
 ('Sabo', 'One Piece', lambda: r5.sprite(41)),
 ('Sanji', 'One Piece', lambda: r5.sprite(42)),
 ('Trafalgar Law', 'One Piece', lambda: r5.sprite(44)),
 ('Zoro (pixel)', 'One Piece', lambda: r5.pat(39, px=20.0, tol=40)),
 ('Crash Bandicoot', 'Outros jogos', lambda: r5.pat(16)),
 ('Togepi (pixel)', 'Pokémon', lambda: r5.pat_flood(20, thr=215, post=head_cream)),
 ('Bulbasaur (versão azul)', 'Pokémon', lambda: r5.pat(32)),
 ('Grogu (Baby Yoda) no berço', 'Star Wars', lambda: r5.pat(14, clear=[(27, 40, 0, 40)])),
 ('Sem-Rosto com coração', 'Studio Ghibli', lambda: r5.pat(2, post=lambda r: O.bridge(r5.largest(r), 3))),
 ('Sem-Rosto (mini)', 'Studio Ghibli', lambda: r5.pat(8)),
 ('Hello Kitty zumbi', 'Hello Kitty', lambda: r5.pat(22)),
 ('Hello Kitty Homem-Aranha', 'Hello Kitty', lambda: r5.pat(30, clear=[(28, 40, 0, 12)])),
 ('Banguela (padrão)', 'Como Treinar o seu Dragão', lambda: r5.pat_flood(27, thr=215, crop=(16, 45, 2, 29))),
 ('Jesus (chibi)', 'Símbolos e objetos', lambda: r5.pat(26)),
 ('Chibi de óculos e maria-chiquinha', 'Outros animes', lambda: r5.pat(12)),
]
if __name__ == '__main__':
    out = []
    from flat import render_flat
    items = []
    for n, g, fn in CFG:
        try:
            r = fn(); out.append((n, g, r)); items.append((f'{n[:22]} {len(r[0])}x{len(r)} p{len(O.components(r))}'.encode('ascii','replace').decode(), r))
        except Exception as e:
            print('ERRO', n, e)
    json.dump(out, open(os.path.join(OUT, 'final7_firstpass.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for k in range(0, len(items), 11):
        render_flat(items[k:k + 11], os.path.join(OUT, f'r5_w1_{k // 11}.png'), scale=9, W=1900)
    print(len(out))
