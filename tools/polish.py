import sys, os
SP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SP, 'out'); os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, SP)
import outline as O
# o preto faz parte do desenho (logos, simbolos, tracos finos): o contorno fica como esta
KEEP_OUTLINE = ['Sharingan', 'Uzumaki', 'Flamel', 'Ouroboros', 'Átomo', 'Yin-yang', 'Pokébola', 'Insígnias', 'TARDIS', 'Lanterna Verde', 'Logo de Red Dead Redemption II', 'Hunter x Hunter',
                'Asas da Liberdade', 'Carta UNO', 'Controle de Super', 'Sigilo do Geass', 'Símbolo de Skyrim', 'Símbolo de Assassin', 'Bandeira', 'Avatar:', 'Estrela com PT', 'Estrela lisa',
                'Sagrado', 'Nossa Senhora', 'Noite Estrelada', 'Saxofone', 'Arco-íris', 'Chapolin', 'Dragonair', 'Smiley do Red John', 'Máscara Hollow', 'Joaninha', 'Diamante', 'Peashooter', 'Dobby', 'Galinha', 'Banguela (Toothless)', 'Professora McGonagall', 'Chaves']
def keeps(name): return any(k in name for k in KEEP_OUTLINE)

def _blocks(rows, f):
    h, w = len(rows), len(rows[0])
    if h % f or w % f: return None
    for y in range(0, h, f):
        for x in range(0, w, f):
            if len({rows[y + i][x + j] for i in range(f) for j in range(f)}) != 1: return None
    return [''.join(rows[y][x] for x in range(0, w, f)) for y in range(0, h, f)]

def _up(rows, f):
    return [''.join(c * f for c in r) for r in rows for _ in range(f)]

def polish(name, rows):
    if keeps(name): r = rows
    else:
        small = _blocks(rows, 2)       # desenho feito em escala 2x (Wanda): tira o contorno na escala original
        if small: r = _up(O.drop_specks(O.recolor_outline(small)), 2)
        else: r = O.drop_specks(O.recolor_outline(rows, max_iter=2 if 'Pintinho' in name else 3))
    return O.connect_components(r)


# desenhos de frente / emblemas que devem ser espelhados (a metade com mais contas manda)
SYM = ['Flamel', 'TARDIS', 'Nossa Senhora', 'Avatar: Reino da Terra', 'Pou', 'Chibi de uniforme preto', 'Morango', 
       'Sininho', 'Diamante', 'Coração', 'Zoro', 'Rimuru', 'Luffy', 'Darth Vader', 'Fantasminha', 'Sagrado Coração', 'Bandeira']
SYM_EXACT = ['Estrela', 'Coração']
def symmetric_name(name): return any(k in name for k in SYM) or name in SYM_EXACT

def symmetrize(rows):
    w = len(rows[0]); half = w // 2
    left = sum(c != '.' for r in rows for c in r[:half]); right = sum(c != '.' for r in rows for c in r[w - half:])
    out = []
    for r in rows:
        mid = r[half] if w % 2 else ''
        if left >= right: L = r[:half]; out.append(L + mid + L[::-1])
        else: R = r[w - half:]; out.append(R[::-1] + mid + R)
    return out
