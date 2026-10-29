"""Gera `projetos3d.js` — PROJETOS DE BEADS EM 3D DE ENCAIXE (peças planas com dentes/fendas que se encaixam), a partir das fotos da `remessa 3D N` do usuário.

Um projeto = peças planas (cada uma é uma grade de contas, como um molde) + onde cada peça vai no objeto montado + passo a passo:
  {id, name, desc, level, view:[rx, ry], pieces:[{name, qty, rows, note?}], parts:[{piece:i, face, at:[X,Y,Z]}], steps:[...]}
  * `parts` tem UMA entrada por peça física (peça com qty 4 aparece 4 vezes); o gerador confere `qty == nº de parts`;
  * face = como a peça é vista DE FORA no objeto: front/back/right/left/top/bottom; `at` = [X,Y,Z] da célula local (0,0) no mundo (células; Y para baixo):
      front (X+cx, Y+cy, Z) · back (X-cx, Y+cy, Z) · right (X, Y+cy, Z-cx) · left (X, Y+cy, Z+cx) · top (X+cx, Y, Z+cy) · bottom (X+cx, Y, Z-cy)
    (cx, cy = coluna e linha da célula na peça). Peças de 1 conta de espessura: o plano passa pelo meio da célula;
  * letras = as da paleta (TPL_LEGEND do templates.js): w branco, k preto, R lima claro (B13), h verde escuro (B8), Ì marrom escuro (F11)…

As peças são LIDAS DAS FOTOS (grade desenhada por cima da foto ampliada: tools/gridview.py) — conferir contra a foto antes de montar.

uso:  python tools/make_3d.py     -> grava projetos3d.js na raiz (confere tamanhos e quantidades)
"""
import os, sys, json
SP = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(SP)
sys.path.insert(0, SP)
from palette import HEX_BY_LETTER


def pieces_ok(p):
    for pc in p['pieces']:
        assert len({len(r) for r in pc['rows']}) == 1, (p['id'], pc['name'], 'linhas desiguais')
        for ch in ''.join(pc['rows']): assert ch == '.' or ch in HEX_BY_LETTER, (p['id'], ch)
    cnt = {}
    for pt in p['parts']: cnt[pt['piece']] = cnt.get(pt['piece'], 0) + 1
    for i, pc in enumerate(p['pieces']): assert cnt.get(i, 0) == pc['qty'], (p['id'], pc['name'], 'qty', pc['qty'], 'partes', cnt.get(i, 0))


# ---------- Maçã verde cortada (encaixe cruzado) — foto 5ae842cf (PicCollage), peças lidas a 15,2 px por conta ----------
MACA_A = [  # metade COM talo e folha, fenda por BAIXO (coluna central, linhas 8-13 vazia)
    '.........hh..',
    '.....n..hhh..',
    '.....nnhh....',
    '..RRR.nhRRR..',
    '.RwwwRnRwwwR.',
    'RwwwwwwwwwwwR',
    'RwwwwwwwwwwwR',
    'RwwwkwwwkwwwR',
    'Rwwwkw.wkwwwR',
    'Rwwwkw.wkwwwR',
    '.Rwwww.wwwwR.',
    '.Rwwww.wwwwR.',
    '..RRww.wwRR..',
    '....RR.RR....',
]
MACA_B = [  # metade SEM talo, fenda por CIMA (coluna central, linhas 0-5 vazia)
    '..RRR...RRR..',
    '.RwwwR.RwwwR.',
    'Rwwwww.wwwwwR',
    'Rwwwkw.wkwwwR',
    'Rwwwkw.wkwwwR',
    'Rwwwkw.wkwwwR',
    'RwwwwwwwwwwwR',
    '.RwwwwwwwwwR.',
    '.RwwwwwwwwwR.',
    '..RRwwRwwRR..',
    '....RR.RR....',
]
maca = {
    'id': 'maca-verde-encaixe', 'name': 'Maçã verde cortada (2 peças de encaixe)', 'level': 'Fácil', 'view': [-14, -38],
    'desc': 'Duas metades de maçã, cada uma com uma fenda no meio: uma fenda vem de baixo, a outra vem de cima. Elas se cruzam em ângulo reto e a maçã fica em pé sozinha, com talo e folha. Peças lidas da foto: confira antes de montar.',
    'pieces': [{'name': 'Metade com talo (fenda por baixo)', 'qty': 1, 'rows': MACA_A, 'note': 'talo e folha em cima'},
               {'name': 'Metade lisa (fenda por cima)', 'qty': 1, 'rows': MACA_B}],
    'parts': [{'piece': 0, 'face': 'front', 'at': [0, 0, 0]},
              {'piece': 1, 'face': 'right', 'at': [6, 3, 6]}],              # a linha 0 da metade lisa fica na linha 3 da outra (o talo ocupa as 3 primeiras)
    'steps': ['Monte as duas metades (cada uma 13 contas de largura). A da folha tem a fenda aberta embaixo; a outra, em cima.',
              'Passe o ferro em cada metade (papel de forno por cima), vire e passe do outro lado. Deixe esfriar sob um peso.',
              'Encaixe: desça a metade lisa pela fenda de cima até as duas fendas se cruzarem — uma metade fica de frente, a outra de lado.',
              'Se ficar solto, uma gotinha de cola na linha onde as metades se cruzam.'],
}


PROJECTS = [maca]


if __name__ == '__main__':
    for p in PROJECTS:
        pieces_ok(p)
        n = sum(sum(1 for r in pc['rows'] for ch in r if ch != '.') * pc['qty'] for pc in p['pieces'])
        print(f"{p['name']}: {sum(pc['qty'] for pc in p['pieces'])} peças, {n} contas")
    out = ['// Projetos de beads em 3D de ENCAIXE (peças planas que se encaixam). GERADO por tools/make_3d.py — veja o cabeçalho de lá para o formato.',
           'window.PROJECTS3D = [']
    for p in PROJECTS: out.append(json.dumps(p, ensure_ascii=False) + ',')
    out.append('];')
    open(os.path.join(ROOT, 'projetos3d.js'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('gravado projetos3d.js')
