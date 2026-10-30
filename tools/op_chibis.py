"""10 chibis de One Piece (folha da remessa 13 idx 33) reconvertidos com illus5.convert5 (regiões lisas) — revisão pedida pelo usuário (2026-10-30). Ver CLAUDE.md §7.16/7.17.
 python tools/op_chibis.py [--show]   -> out/op_new.png (fonte | atual | novo)"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.environ.setdefault('BEADPAL', '120')
import numpy as np, cv2
import illus, illus5, r5, facetools as F

NAMES = ['luffy', 'zoro', 'nami', 'chopper', 'usopp', 'sanji', 'nico-robin', 'franky', 'brook', 'jinbe']
IDS = [n + '-chibi-one-piece' for n in NAMES]


def crops(join=3, min_area=0.003, thr=205):
    rgb = illus._load(F.src_path(13, 33))
    mask = illus.background(rgb, thr); fg = (~mask).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * join + 1, 2 * join + 1))
    cnt, lab = cv2.connectedComponents(cv2.dilate(fg, k), connectivity=8)
    boxes = []
    for i in range(1, cnt):
        m = (lab == i) & (fg > 0)
        if m.sum() < min_area * fg.size: continue
        ys, xs = np.nonzero(m); boxes.append((ys.min(), ys.max() + 1, xs.min(), xs.max() + 1))
    assert len(boxes) == 10, len(boxes)
    boxes.sort(key=lambda b: (b[0] + b[1]) / 2)
    rows_, cur = [], [boxes[0]]
    for b in boxes[1:]:
        if abs((b[0] + b[1]) / 2 - np.mean([(c[0] + c[1]) / 2 for c in cur])) < 0.5 * max(b[1] - b[0], cur[0][1] - cur[0][0]): cur.append(b)
        else: rows_.append(cur); cur = [b]
    rows_.append(cur)
    ordered = [b for r in rows_ for b in sorted(r, key=lambda b: b[2])]
    return rgb, ordered


def convert_all(native=False, **kw):
    """native=False: versão de 1 PLACA (lado maior 50; o Chopper já é 49x49 no tamanho nativo); native=True: tamanho NATIVO do sprite (cada pixel do sprite = 3 px da folha = 1 conta), que dá 2-4 placas.
    A folha é um sprite pixel-art de pixel de 3 px (autocorrelação 3 nas duas direções): converter a 40 contas (como na 1ª versão) jogava fora ~1/3 do detalhe; a 50 fica quase 1:1."""
    rgb, boxes = crops(); out = []
    for n, (y0, y1, x0, x1) in zip(NAMES, boxes):
        sub = rgb[max(0, y0 - 2):y1 + 2, max(0, x0 - 2):x1 + 2]
        r5.SKIN_ON = True
        ns = int(round(max(y1 - y0, x1 - x0) / 3.0))
        nat = native or (n == 'chopper')
        a = dict(size=ns if nat else 50, K=20 if nat else 18, dark_frac=0.28 if nat else 0.25, black_L=16.0, thr=205); a.update(kw)
        out.append(illus5.convert5(rgb=sub, **a))
    return out, None


if __name__ == '__main__':
    import tplfile
    from flat import render_flat
    from PIL import Image
    d = tplfile.parse(os.path.join(os.path.dirname(HERE), 'templates.js')); by = {i['id']: i['rows'] for i in d['items']}
    new, subs = convert_all()
    items = []
    for n, a, b in zip(NAMES, [by[i] for i in IDS], new): items += [(n + ' atual', a), (n + ' novo', b)]
    render_flat(items[:10], os.path.join(HERE, 'out', 'op_new_a.png'), scale=9, W=1900)
    render_flat(items[10:], os.path.join(HERE, 'out', 'op_new_b.png'), scale=9, W=1900)
