import os, sys, json
os.environ['REMNUM'] = '8'
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import r6, outline as O
from flat import render_flat
E = r6.exact6
CFG = [
 ('Mimikyu (padrão)', 'Pokémon', lambda: E(0, px=22.0, crop_img=(24, 22, 531, 686), mode=True, dist=18)),
 ('Harry Potter (chibi com cachecol)', 'Harry Potter', lambda: E(1, crop=(0, 29, 0, 29))),
 ('Natsu Dragneel (chibi)', 'Outros animes', lambda: E(2)),
 ('Jiraiya (chibi)', 'Naruto', lambda: E(3, crop=(1, 44, 1, 34))),
 ('Michelangelo (Tartarugas Ninja)', 'Outros desenhos', lambda: E(4, clear=[(0, 1, 0, 5)])),
 ('Vaquinha', 'Animais', lambda: E(5, crop=(0, 36, 0, 39))),
 ('Hello Kitty bruxa na vassoura', 'Hello Kitty', lambda: E(6, clear=[(0, 18, 0, 13)])),
 ('Lavi (D.Gray-man)', 'Outros animes', lambda: E(7)),
 ('Chibi de capacete de gato', 'Outros animes', lambda: E(8)),
 ('Porco verde (Angry Birds)', 'Outros jogos', lambda: E(9)),
 ('Chibi sombrio de antenas', 'Outros animes', lambda: E(10)),
 ('Chibi loira de cabelo longo', 'Outros animes', lambda: E(11, crop=(0, 41, 0, 24))),
 ('Diabinho com tridente', 'Outros desenhos', lambda: E(12)),
 ('Vash the Stampede (chibi)', 'Outros animes', lambda: E(13)),
 ('Vash the Stampede (com arma)', 'Outros animes', lambda: E(23)),
 ('Cattail (Plants vs Zombies)', 'Outros jogos', lambda: E(14)),
 ('Yami Yugi (padrão)', 'Yu-Gi-Oh', lambda: E(15, px=dict(px=32.52, py=30.33, ox=0.0, oy=0.0, W=23, H=30), crop_img=(226, 320, 974, 1230), mode=True, dist=18)),
 ('Yami Yugi (pixel)', 'Yu-Gi-Oh', lambda: E(19)),
 ('Fantasma fofo', 'Outros desenhos', lambda: E(16, crop=(0, 37, 0, 32))),
 ('Criatura marrom de pernas verdes', 'Outros desenhos', lambda: E(17)),
 ('Sonic (chibi)', 'Outros jogos', lambda: E(18, crop=(1, 36, 1, 22), achro=205)),
 ('Inuyasha (chibi)', 'Outros animes', lambda: E(20, crop=(4, 27, 4, 27))),
 ('Lelouch gatinho (Code Geass)', 'Code Geass', lambda: E(21)),
 ('Morcego fofo', 'Animais', lambda: E(22, crop=(0, 22, 0, 40))),
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
    if not only: json.dump(out, open(os.path.join(SP, 'data', 'final10.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for k in range(0, len(items), 12):
        render_flat(items[k:k + 12], os.path.join(OUT, f'r8_x_{k // 12}.png'), scale=8, W=1900)
