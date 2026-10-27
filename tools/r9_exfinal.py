import os, sys, json
os.environ['REMNUM'] = '9'
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import r6, outline as O
from flat import render_flat
E = r6.exact6
def blocks(rows):
    out = []; cur = []
    for r in rows:
        if set(r) == {'.'}:
            if cur: out.append(cur); cur = []
        else: cur.append(r)
    if cur: out.append(cur)
    return [O.trim(b) for b in out]
CFG = [
 ('Guitarra vermelha', 'Símbolos e objetos', lambda: E(0)),
 ('Asas da Liberdade (padrão)', 'Attack on Titan', lambda: E(1)),
 ('Titã Colossal (chibi)', 'Attack on Titan', lambda: E(2, crop=(3, 27, 3, 26))),
 ('Chibi de cabelo preto e olhos turquesa', 'Outros animes', lambda: E(3)),
 ('Akuma no Mi (padrão)', 'One Piece', lambda: E(4)),
 ('Emblema de caveira com chifres', 'Símbolos e objetos', lambda: E(5)),
 ('Charmander (sprite)', 'Pokémon', lambda: blocks(E(6))[0]),
 ('Charmeleon (sprite)', 'Pokémon', lambda: blocks(E(6))[1]),
 ('Charizard (sprite)', 'Pokémon', lambda: blocks(E(6))[2]),
]
if __name__ == '__main__':
    only = sys.argv[1:]
    out = []; items = []
    for n, g, fn in CFG:
        if only and not any(o in n for o in only): continue
        try:
            __import__('r5').SKIN_ON = __import__('r5').skin_for(n, g)
            r = fn(); out.append((n, g, r)); items.append((f'{n[:26]} {len(r[0])}x{len(r)} p{len(O.components(r))}'.encode('ascii', 'replace').decode(), r))
        except Exception as e:
            import traceback; traceback.print_exc(); print('ERRO', n, repr(e))
    print(len(out), 'templates')
    if not only: json.dump(out, open(os.path.join(SP, 'data', 'final11' + __import__('palette').sfx() + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    render_flat(items, os.path.join(OUT, 'r9_x_0' + __import__('palette').sfx() + '.png'), scale=10, W=1900)
