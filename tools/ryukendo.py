"""Revisão dos heróis de armadura de Ryukendo (remessa 17; pedido do usuário, 2026-10-30). Variantes de illus5.convert5 lado a lado com a fonte e o molde atual.
  python tools/ryukendo.py [idx...]     folhas em tools/out/ryu_<idx>.png (fonte | atual 1 placa | variantes 1 placa) e ryu_<idx>_g.png (idem para o grande); NÃO mexe no catálogo.
  python tools/ryukendo.py --snapshot   guarda em tools/data/ryukendo_orig.json os moldes revistos;   --apply   grava (só troca o que ainda é igual ao instantâneo).
O fundo das folhas é roxo de propósito: em cinza-claro as contas H1/H2 da armadura branca parecem buracos."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); os.environ.setdefault('BEADPAL', '120')
import numpy as np, cv2
import tplfile, illus, illus5, r5, loose, shrink, facetools as F
from palette import ALL
from flat import L2HEX
from PIL import Image, ImageDraw

L = {p['code']: p['letter'] for p in ALL}


def _flood(cand, top=True, bottom=True, left=True, right=True, right_to=None):
    """True = candidato ligado às bordas escolhidas por 4 vizinhos (right_to = só a parte de cima da borda direita, até essa linha)"""
    n, lab = cv2.connectedComponents(cand.astype(np.uint8), connectivity=4)
    seeds = []
    if top: seeds.append(lab[0])
    if bottom: seeds.append(lab[-1])
    if left: seeds.append(lab[:, 0])
    if right: seeds.append(lab[:right_to, -1] if right_to else lab[:, -1])
    keep = set(np.concatenate(seeds).tolist()); keep.discard(0)
    return np.isin(lab, list(keep)) if keep else np.zeros(cand.shape, bool)


def mask_signed(thr=235, sign=None):
    """fundo branco; sign = (x0, y0) tira o canto de baixo à direita, onde está a assinatura do artista (idx 0)"""
    def f(rgb):
        m = illus.sticker_bg(rgb, thr, None)
        if sign: m[sign[1]:, sign[0]:] = True
        return m
    return f


def mask_pink():
    """fundo branco + o rastro rosa em volta da figura (idx 3): branco e rosa só saem se estiverem ligados à borda, então o branco da armadura (contornado) e o brilho rosado do vermelho ficam"""
    def f(rgb):
        r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
        white = rgb.min(axis=2) >= 232
        pink = (r > 200) & (g > 80) & (b > 80) & (r - g >= 12) & (r - b >= 8) & (abs(g - b) < 50)
        return _flood(white | pink)
    return f


def mask_sky():
    """fundo branco/azul-claro da arte da bola (idx 31). A armadura é marfim ou cinza-lilás (G <= R), o céu é ciano (G e B bem acima de R); a linha branca em volta da figura sai junto.
    Só inunda de cima, da esquerda e do alto da direita: a figura é cortada pela borda de baixo e pela de baixo à direita."""
    def f(rgb):
        r, g, b = [rgb[..., i].astype(np.int32) for i in range(3)]
        cand = (rgb.min(axis=2) >= 240) | ((g - r > 10) & (b - r > 10) & (r > 130))
        return _flood(cand, bottom=False, right_to=rgb.shape[0] // 3)
    return f


BASE = {0: dict(mask=mask_signed(235, (215, 538))), 3: dict(mask=mask_pink()), 8: dict(thr=240), 27: dict(thr=240), 31: dict(mask=mask_sky())}
# o azul da arte do idx 8 (91,138,254) e o do visor (91,195,254) são vivos: C8 e C5 são os mais próximos em matiz; o ΔE mandava para C7 e C4, apagados.
# no idx 27 o dourado escuro da coroa caía em verde-oliva (B17, M6) e marrom-preto (B11): volta para âmbar e preto.
REMAP = {8: {L['C4']: L['C5'], L['C7']: L['C8']}, 27: {L['B17']: L['A6'], L['M6']: L['A6'], L['B11']: 'k'}}
IDS = {0: 'heroi-de-armadura-vermelha-e-dourada-chibi', 3: 'heroi-de-armadura-vermelha-e-branca-chibi', 8: 'heroi-de-armadura-azul-e-dourada-chibi', 27: 'heroi-de-armadura-azul-e-dourada-com-espada-chibi', 31: None}
GRANDE = {k: (v + '-grande' if v else 'heroi-de-armadura-azul-e-dourada-com-bola-grande') for k, v in IDS.items()}
KW = {0: dict(K=24, dark_frac=0.45, black_L=12.0), 3: dict(K=24, dark_frac=0.60, black_L=10.0), 8: dict(K=24, dark_frac=0.65, black_L=12.0, hatch=3),
      27: dict(K=26, dark_frac=0.60, black_L=12.0, hatch=7, rare_n=10), 31: dict(K=24, dark_frac=0.60, black_L=10.0)}
OVER_1 = {0: dict(K=40)}          # K maior separa o cinza dos chifres e da saia do branco das outras partes
OVER_G = {0: dict(K=34)}
BG = (140, 90, 160)


def conv(idx, plates=None, **over):
    r5.SKIN_ON = False
    a = dict(BASE[idx]); a.update(KW[idx]); a.update(OVER_G.get(idx, {}) if plates else OVER_1.get(idx, {})); a.update(over)
    if plates: a['plates'] = plates
    rows = r5.largest(illus5.convert5(F.src_path(17, idx), **a))
    rm = REMAP.get(idx)
    if rm: rows = [''.join(rm.get(c, c) for c in r) for r in rows]
    return loose.fix_loose(rows) if loose.loose_count(rows) else rows


def one_plate(idx):
    """1 placa reduzida do grande novo (testada e rejeitada: engrossa o preto; fica para comparar)"""
    rows = shrink.shrink(conv(idx, plates=4), 50, 'bias', empty_at=0.6)
    return loose.fix_loose(rows) if loose.loose_count(rows) else rows


def img(rows, cell):
    h, w = len(rows), len(rows[0])
    im = Image.new('RGB', (w * cell, h * cell), BG); d = ImageDraw.Draw(im)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c != '.': d.rectangle((x * cell, y * cell, x * cell + cell - 1, y * cell + cell - 1), fill=L2HEX[c])
    return im


def sheet(path, parts, H=640):
    ims = []
    for lab, p in parts:
        if isinstance(p, Image.Image): im = p.resize((int(p.width * H / p.height), H), Image.LANCZOS)
        else: im = img(p, max(1, H // len(p)))
        ims.append((lab, im))
    out = Image.new('RGB', (sum(i.width + 10 for _, i in ims) + 10, H + 26), (40, 40, 44)); d = ImageDraw.Draw(out); x = 8
    for lab, i in ims:
        out.paste(i, (x, 22)); d.text((x, 5), lab, fill=(255, 255, 255)); x += i.width + 10
    out.save(path)


def build():
    """{id: linhas novas} dos 9 moldes"""
    out = {}
    for idx in IDS:
        if IDS[idx]: out[IDS[idx]] = conv(idx)
        out[GRANDE[idx]] = conv(idx, plates=4)
    return out


if __name__ == '__main__':
    TPL = os.path.join(ROOT, 'templates.js'); SNAP = os.path.join(HERE, 'data', 'ryukendo_orig.json')
    if '--snapshot' in sys.argv:          # guarda os moldes que foram revistos: --apply só troca o que ainda é igual a isto
        d = tplfile.parse(TPL); by = {t['id']: t for t in d['items']}
        json.dump({i: by[i]['rows'] for i in list(filter(None, IDS.values())) + list(GRANDE.values())}, open(SNAP, 'w', encoding='utf-8'), ensure_ascii=False)
        print('instantâneo gravado; TPL_BAKED', d['baked']); sys.exit()
    if '--apply' in sys.argv:
        new = build(); orig = json.load(open(SNAP, encoding='utf-8'))
        d = tplfile.parse(TPL); by = {t['id']: t for t in d['items']}
        for i, rows in new.items():
            if i not in by: print('  NÃO ESTÁ MAIS NO CATÁLOGO, pulei:', i); continue
            if by[i]['rows'] != orig[i] and by[i]['rows'] != rows: print('  PULEI (o desenho mudou depois da revisão: você ajustou no app?):', i); continue
            by[i]['rows'] = rows; print('  trocado', i, '%dx%d' % (len(rows[0]), len(rows)), 'soltas', loose.loose_count(rows))
        tplfile.write(TPL, d['legend'], d['cfg'], d['items'], d.get('removed')); print('gravado'); sys.exit()
    want = [int(a) for a in sys.argv[1:]] or list(IDS)
    by = {t['id']: t for t in tplfile.parse(TPL)['items']}
    for idx in want:
        src = Image.fromarray(F.src_raw(17, idx))
        g = conv(idx, plates=4)
        parts = [('fonte', src)]
        if IDS[idx] in by: parts += [('ATUAL 1 placa', by[IDS[idx]]['rows']), ('direto 50', conv(idx)), ('reduzido do grande', one_plate(idx))]
        sheet(os.path.join(HERE, 'out', 'ryu_%d.png' % idx), parts)
        sheet(os.path.join(HERE, 'out', 'ryu_%d_g.png' % idx), [('fonte', src), ('ATUAL grande', by[GRANDE[idx]]['rows']), ('novo', g)], H=800)
        print('ok', idx, 'grande', len(g[0]), len(g), flush=True)
