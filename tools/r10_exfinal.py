import os, sys, json
os.environ['REMNUM'] = '10'
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

RED = [((244, 40, 15), 30, 'r')]     # vermelho puro muito saturado: a regra geral o mandaria para o laranja
CFG = [
 # --- Pokémon
 ('Lucario', 'Pokémon', lambda: E(0, crop=(1, 37, 1, 26))),
 ('Magikarp', 'Pokémon', lambda: E(4)),
 ('Umbreon na Pokébola', 'Pokémon', lambda: E(12)),
 ('Ash e Pikachu (chibi)', 'Pokémon', lambda: E(9)),
 ('Vaporeon (padrão)', 'Pokémon', lambda: E(18, crop=(1, 31, 1, 40))),
 ('Rayquaza', 'Pokémon', lambda: E(19, crop=(1, 43, 1, 41))),
 ('Lugia', 'Pokémon', lambda: E(22)),
 ('Tyranitar', 'Pokémon', lambda: E(23, crop=(1, 39, 1, 36))),
 ('Criatura amarela e marrom (tabela)', 'Outros desenhos', lambda: E(14, px=22.0, crop_img=(22, 22, 396, 353), mode=True)),
 # --- Mario / jogos
 ('Toad (Mario)', 'Mario', lambda: E(3, colmap=RED)),
 ('Kirby', 'Outros jogos', lambda: E(13)),
 ('Red (Angry Birds)', 'Outros jogos', lambda: E(27)),
 ('Espada de diamante (versão 2)', 'Outros jogos', lambda: E(2, crop=(1, 19, 1, 21), colmap=[((48, 236, 203), 24, 'g'), ((42, 199, 170), 24, 'c')])),
 ('Diamante (Minecraft)', 'Outros jogos', lambda: E(11)),
 ('Armadura de diamante (Minecraft)', 'Outros jogos', lambda: E(15)),
 # --- animes
 ('Shoto Todoroki (chibi)', 'Outros animes', lambda: E(25)),
 ('Chibi de cabelo azul e vestido vermelho', 'Outros animes', lambda: E(1, crop=(0, 29, 0, 18))),
 ('Banguela (chibi)', 'Como Treinar o seu Dragão', lambda: E(5)),
 # --- desenhos / filmes
 ('Judy Hopps (Zootopia)', 'Disney', lambda: cblocks(E(7))[0]),
 ('Nick Wilde (Zootopia)', 'Disney', lambda: cblocks(E(7))[1]),
 ('Relâmpago McQueen (Carros)', 'Disney', lambda: E(20, crop=(2, 12, 0, 20))),
 ('Carro azul (Carros)', 'Disney', lambda: E(20, crop=(16, 27, 0, 20))),
 ('Perry (padrão, de lado)', 'Phineas e Ferb', lambda: E(10, crop=(0, 28, 0, 28))),
 ('Corvo e dragão roxo', 'Outros desenhos', lambda: E(8)),
 ('Dragãozinho verde', 'Outros desenhos', lambda: E(24)),
 ('Chibi de cabelo roxo e jaqueta azul', 'Outros desenhos', lambda: E(21)),
 # --- animais
 ('Galinha (versão grande)', 'Animais', lambda: E(6)),
 ('Crocodilo fofo', 'Animais', lambda: E(16)),
 ('Galinha preta (pequena)', 'Animais', lambda: E(17, crop=(2, 18, 0, 25))),
 ('Galinha preta (grande)', 'Animais', lambda: E(17, crop=(20, 40, 0, 25), tol=48, post=r5.largest)),
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
    if not only: json.dump(out, open(os.path.join(SP, 'data', 'final12' + __import__('palette').sfx() + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for k in range(0, len(items), 12):
        render_flat(items[k:k + 12], os.path.join(OUT, f'r10_x_{k // 12}' + __import__('palette').sfx() + '.png'), scale=8, W=1900)
