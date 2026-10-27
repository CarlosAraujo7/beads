"""Paleta de cores do projeto (lida de data/palette.json; gerada por make_palette.py).

São 120 cores (kit Pindou de 120). As 24 primeiras são as do kit antigo, na ordem da tabela impressa = índices 1..24 do app.

    import palette as P
    P.ALL        lista das 120 cores [{code, name, hex, letter, est}]
    P.BASE24     as 24 primeiras
    P.MODE       '24' (padrão; o pipeline antigo, reprodutível) ou '120' — escolhido pela variável de ambiente BEADPAL
    P.PAL        [(código, '#HEX')] das cores do modo ativo (é o que img2tpl.PAL exporta)
    P.LETTER     código -> letra (das 120, para qualquer modo)
    P.HEX_BY_LETTER   letra -> 'RRGGBB' (das 120: dá para desenhar moldes de qualquer das duas paletas)
    P.LEGEND     letra -> código (o TPL_LEGEND do templates.js)

Cada linha de molde tem 1 caractere por conta: '.' = vazio, o resto é a `letter` da cor.
"""
import os, json

SP = os.path.dirname(os.path.abspath(__file__))
ALL = json.load(open(os.path.join(SP, 'data', 'palette.json'), encoding='utf-8'))['colors']
BASE24 = ALL[:24]
MODE = os.environ.get('BEADPAL', '24')
if MODE not in ('24', '120'): raise SystemExit('BEADPAL deve ser 24 ou 120')
ACTIVE = ALL if MODE == '120' else BASE24
PAL = [(c['code'], c['hex']) for c in ACTIVE]
LETTER = {c['code']: c['letter'] for c in ALL}
HEX_BY_LETTER = {c['letter']: c['hex'].lstrip('#').upper() for c in ALL}
LEGEND = {c['letter']: c['code'] for c in ALL}
LETTERS24 = ''.join(c['letter'] for c in BASE24)


def sfx():
    """sufixo dos arquivos de saída: '' no modo 24 (o pipeline antigo), '_120' no modo 120 (não sobrescreve os finalN.json antigos)"""
    return '_120' if MODE == '120' else ''
