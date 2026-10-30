"""Cubos 3D DE ENCAIXE gerados por tools/cube3d.py (a junta é a de dentes alternados dos cubos lidos das fotos: Abelha, Presente).
Hoje só o DADO (cubo de 6 lados, 9×9×9). Os 12 cubos de personagens feitos em 2026-10-29 (Pikachu, Kirby, Creeper, Minion, Batman, Homem de Ferro, Darth Vader, Toad,
Groot, Hello Kitty, Naruto e o Dado 13×13×13) foram APAGADOS a pedido do usuário; o que se aprendeu com eles está em CLAUDE.md (§3, "Cubos GERADOS").
make_3d.py usa cubes() daqui. Para um cubo novo: monte um `spec` (veja cube3d.cube_project) com a textura de cada face.
"""
import os, sys
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import cube3d


def steps():
    return ['Monte as peças (as iguais são feitas mais de uma vez) e passe o ferro em cada uma, dos dois lados, com papel de forno; deixe esfriar sob um peso.',
            'Os dentes alternam de propósito: onde uma peça tem conta na borda, a vizinha tem vão. Comece pela base e erga a frente, a traseira e as duas laterais.',
            'Feche com a tampa de cima. Se ficar frouxo, uma gota de cola nos cantos. Projeto desenhado (não é de uma foto): teste o encaixe antes de fazer em várias cores.']


def die_face(n, N=9):
    """face de dado N×N com `n` pintas de 1 conta (só no miolo: a borda é das outras faces)"""
    g = [['w'] * N for _ in range(N)]
    a, b, c = 2, N // 2, N - 3                       # posições das pintas (N=9: 2, 4, 6)
    pos = {'tl': (a, a), 'tr': (c, a), 'ml': (a, b), 'mr': (c, b), 'bl': (a, c), 'br': (c, c), 'c': (b, b)}
    lay = {1: ['c'], 2: ['tl', 'br'], 3: ['tl', 'c', 'br'], 4: ['tl', 'tr', 'bl', 'br'], 5: ['tl', 'tr', 'c', 'bl', 'br'], 6: ['tl', 'tr', 'ml', 'mr', 'bl', 'br']}
    for p in lay[n]:
        x, y = pos[p]; g[y][x] = 'k'
    return [''.join(r) for r in g]


def build():
    N = 9
    return [{'id': 'cubo-dado', 'name': 'Cubo Dado (9×9×9)', 'size': (N, N, N), 'level': 'Fácil',
             'tex': {'front': die_face(1), 'back': die_face(6), 'right': die_face(2), 'left': die_face(5), 'top': die_face(3), 'bottom': die_face(4)},
             'fill': {'*': 'w'}, 'ears': None, 'steps': steps(),
             'desc': f'Dado de 6 lados de {N}×{N}×{N} contas (cerca de {N * 0.26:.1f} cm), branco com pintas pretas, em 6 peças planas com dentes alternados que se encaixam sem sobrar nem faltar conta. '
                     'As 6 faces têm de 1 a 6 pintas e as opostas somam 7 (1×6, 2×5, 3×4). É um projeto desenhado (não é de uma foto de peça pronta): teste o encaixe antes.'}]


def cubes():
    return [cube3d.cube_project(s) for s in build()]


if __name__ == '__main__':
    for p in cubes():
        n = sum(sum(1 for r in pc['rows'] for ch in r if ch != '.') * pc['qty'] for pc in p['pieces'])
        print(f"{p['name']:28} peças {sum(pc['qty'] for pc in p['pieces'])} contas {n} casca {p['_shell']}")
        for pc in p['pieces']:
            print('  ', pc['name'], pc['qty'])
            for r in pc['rows']: print('     ', r)
