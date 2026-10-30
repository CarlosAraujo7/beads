"""Simetria dos moldes da categoria Cavaleiros do Zodíaco (pedido do usuário, 2026-10-30: "olhos que deveriam ser iguais e ficam diferentes, marcas e chifres das armaduras que mudam de um lado
para o outro; é minha franquia favorita e quero fazer todos"). Cada molde de FRENTE é espelhado em torno do eixo central (tools/mirror.py), mantendo a metade MAIS BEM RESOLVIDA.
A metade foi escolhida olhando as duas versões espelhadas, principalmente os OLHOS (brilho branco nos dois lados) e a limpeza do contorno do elmo/armadura; nos grandes, pelo menor ruído.
  id -> (eixo em meias-colunas `a2`, lado mantido 'L' esquerdo / 'R' direito)
NÃO espelha o "Seiya de Pégaso (retrato)": é um retrato de 3/4 (rosto e ombro de lado); espelhar viraria duas caras.
uso:  python tools/apply_cav_symmetry.py [--dry]      (cópia de segurança antes: tools/backups/pre-cav-simetria.js)
"""
import os, sys, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import tplfile, loose, mirror

# ATENÇÃO (2026-10-30): estes 3 foram espelhados por inteiro numa 1ª rodada e o usuário reclamou (Shiryu: olhos estranhos; Shun chibi: "cara de espelhado"; Shun corpo inteiro: era melhor o original).
# Hoje são tratados por tools/cav_chibis_fix.py (simetria SÓ do capacete/olhos, olhos desenhados, cabelo natural). Ficam aqui só para o histórico e para o `--apply` reconhecer o estado antigo.
OLD_PICK = {
    'shun-de-andromeda-chibi-corpo-inteiro': (24, 'R'),
    'shun-de-andromeda-chibi': (37, 'L'),
    'shiryu-de-dragao-chibi': (39, 'L'),
}
PICK = {
    'seiya-de-pegaso-chibi-capacete': (40, 'R'),
    'seiya-de-pegaso-chibi-armadura-de-prata': (40, 'L'),
    'seiya-de-sagitario-chibi': (40, 'L'),
    'hyoga-de-cisne-chibi': (41, 'R'),
    'ikki-de-fenix-chibi': (38, 'L'),
    'shiryu-de-dragao-chibi-capacete': (36, 'L'),
    'shaka-de-virgem-chibi': (40, 'R'),
    'seiya-de-sagitario-chibi-asas': (92, 'L'),
    'seiya-de-sagitario-chibi-busto': (97, 'L'),
    'shun-de-andromeda-chibi-capacete-rosa': (84, 'L'),
}


def symmetry(rows):
    a2, sc = mirror.best_axis(rows, span=12 if len(rows[0]) > 60 else 8)
    return sc


if __name__ == '__main__':
    dry = '--dry' in sys.argv
    if not dry and '--force' not in sys.argv:
        sys.exit('já aplicado em 2026-10-30 (e o catálogo é definitivo); rodar de novo SOBRESCREVE tools/backups/pre-cav-simetria.js. Use --dry para só olhar ou --force se for de propósito.')
    TPL = os.path.join(ROOT, 'templates.js'); d = tplfile.parse(TPL)
    by = {it['id']: it for it in d['items']}
    for i, (a2, side) in PICK.items():
        it = by[i]; old = it['rows']
        new = mirror.mirror(old, a2, side)
        if loose.loose_count(new): new = loose.fix_loose(new)
        # o fix_loose pode ter mexido em um lado só: se a simetria caiu, refaz o espelho a partir da metade já corrigida
        s0 = symmetry(new)
        if s0 < 0.999:
            a2n, _ = mirror.best_axis(new, span=4)
            new = mirror.mirror(new, a2n, side); s0 = symmetry(new)
        n_old = sum(1 for r in old for c in r if c != '.'); n_new = sum(1 for r in new for c in r if c != '.')
        print('%-44s %3dx%-3d %5d -> %3dx%-3d %5d  simetria %3.0f%% -> %3.0f%%  (lado %s)' % (i[:44], len(old[0]), len(old), n_old, len(new[0]), len(new), n_new, symmetry(old) * 100, s0 * 100, side))
        assert max(len(new[0]), len(new)) <= 100
        it['rows'] = new
    if dry: print('(--dry: nada gravado)'); sys.exit(0)
    shutil.copy(TPL, os.path.join(HERE, 'backups', 'pre-cav-simetria.js'))
    tplfile.write(TPL, d['legend'], d['cfg'], d['items'], d.get('removed'))
    print('gravado')
