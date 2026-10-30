"""Lê peças de contas de uma FOTO de cima (placa transparente ou fundo liso): ajusta a grade das contas dentro de uma caixa, amostra o anel de cada conta e devolve letras da paleta.
Contas altas fotografadas de cima ficam um pouco MAIORES que os pinos da placa (estão mais perto da câmera): o passo certo é o das contas (ex.: 17,2 px quando os pinos têm 16,4).

  fit(img, box, pitch=(16.5, 18.0))       -> (ox, oy, px, py)  grade que melhor encaixa os furos das contas dentro de `box`
                                             (ox, oy) = CENTRO (furo) da conta de coluna/linha 0; centro da célula (i, j) = (ox + i*px, oy + j*py)
  read(img, lat, cols, rows, pal, ...)    -> linhas de letras ('.' = vazio) e o overlay para conferir
  overlay(img, lat, box, rows, path)      -> grava recorte ampliado com as letras desenhadas por cima

`pal` = lista [((r,g,b), 'letra'), ...] com os centros das cores das contas NESTA foto (o resultado é reprodutível e a escolha de
laranja×vermelho, branco×cinza etc. é sua); `bg` = lista de cores do fundo/placa (viram '.').
"""
import numpy as np, cv2
from PIL import Image


def load(path):
    return np.array(Image.open(path).convert('RGB'))


def _ring(img, cx, cy, r, n=10):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    xs = np.clip((cx + r * np.cos(a)).round().astype(int), 0, img.shape[1] - 1)
    ys = np.clip((cy + r * np.sin(a)).round().astype(int), 0, img.shape[0] - 1)
    return img[ys, xs].astype(float)


def fit(img, box, pitch=(16.5, 18.0), fixed=None, step=0.1, mask_fn=None):
    """Procura passo e fase da grade que mais alinha o FURO escuro de cada conta com o centro da célula.
    mask_fn(rgb)->bool diz quais pixels são conta (padrão: saturados ou muito claros em relação à placa)."""
    x0, y0, x1, y1 = box
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(float)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(float)
    if mask_fn is None:
        m = (hsv[..., 1] > 90) | (g > 190)
    else:
        m = mask_fn(img)
    best = None
    ps = [fixed] if fixed else np.arange(pitch[0], pitch[1] + 1e-6, step)
    for p in ps:
        for oy in np.arange(0, p, 1.0):
            for ox in np.arange(0, p, 1.0):
                sc = 0.0; n = 0
                xs = np.arange(x0 + ((ox - x0) % p), x1, p)
                ys = np.arange(y0 + ((oy - y0) % p), y1, p)
                for cy in ys:
                    for cx in xs:
                        ring = _ring(g, cx, cy, p * 0.34, 8)
                        mr = np.mean([m[int(min(max(cy + p * 0.34 * np.sin(a), 0), m.shape[0] - 1)), int(min(max(cx + p * 0.34 * np.cos(a), 0), m.shape[1] - 1))]
                                      for a in np.linspace(0, 2 * np.pi, 8, endpoint=False)])
                        if mr < 0.75: continue
                        c = g[int(cy), int(cx)]
                        sc += ring.mean() - c; n += 1
                if n >= 4 and (best is None or sc > best[0]):
                    best = (sc, ox % p, oy % p, p)
    return best[1], best[2], best[3], best[3]


def read(img, lat, cols, rows, pal, bg=(), maxd=60, r=0.32, c0=0, r0=0):
    """cols/rows = nº de células a ler a partir da célula (c0, r0) da grade `lat`=(ox,oy,px,py). Devolve (linhas, dist)."""
    ox, oy, px, py = lat
    out = []; dd = []
    refs = [(np.array(c, float), l) for c, l in pal] + [(np.array(c, float), '.') for c in bg]
    for j in range(rows):
        s = ''; drow = []
        for i in range(cols):
            cx = ox + (c0 + i) * px; cy = oy + (r0 + j) * py
            if not (0 <= cx < img.shape[1] and 0 <= cy < img.shape[0]): s += '.'; drow.append(999); continue
            ring = _ring(img, cx, cy, px * r, 12)
            col = np.median(ring, axis=0)
            best = min(((np.linalg.norm(col - c), l) for c, l in refs), key=lambda t: t[0])
            s += best[1] if best[0] <= maxd else '?'; drow.append(best[0])
        out.append(s); dd.append(drow)
    return out, dd


def overlay(img, lat, box, rows, path, c0=0, r0=0, sc=3, letters=True):
    x0, y0, x1, y1 = box
    x0 = max(0, x0); y0 = max(0, y0); x1 = min(img.shape[1], x1); y1 = min(img.shape[0], y1)
    ox, oy, px, py = lat
    v = cv2.resize(img[y0:y1, x0:x1], None, fx=sc, fy=sc, interpolation=cv2.INTER_CUBIC).copy()
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            cx = (ox + (c0 + i) * px - x0) * sc; cy = (oy + (r0 + j) * py - y0) * sc
            cv2.rectangle(v, (int(cx - px * sc / 2), int(cy - py * sc / 2)), (int(cx + px * sc / 2), int(cy + py * sc / 2)), (255, 0, 255), 1)
            if letters and ch != '.':
                cv2.putText(v, ch if ord(ch) < 128 else '#', (int(cx - 6), int(cy + 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                cv2.putText(v, ch if ord(ch) < 128 else '#', (int(cx - 6), int(cy + 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    Image.fromarray(v).save(path)
    return path


def fit_fast(img, box, pitch=(16.5, 18.0), step=0.1, mask_fn=None, ostep=1.0):
    """igual a fit(), mas vetorizado com numpy (centenas de vezes mais rápido): procura passo e fase que mais alinham o FURO escuro de cada conta com o centro da célula."""
    x0, y0, x1, y1 = box
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(float)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(float)
    m = ((hsv[..., 1] > 90) | (g > 190)) if mask_fn is None else mask_fn(img)
    H, W = g.shape
    ang = np.linspace(0, 2 * np.pi, 8, endpoint=False)
    best = None
    for p in np.arange(pitch[0], pitch[1] + 1e-6, step):
        for oy in np.arange(0, p, ostep):
            ys = np.arange(y0 + ((oy - y0) % p), y1, p)
            for ox in np.arange(0, p, ostep):
                xs = np.arange(x0 + ((ox - x0) % p), x1, p)
                X, Y = np.meshgrid(xs, ys)
                rx = np.clip((X[..., None] + p * 0.34 * np.cos(ang)).round().astype(int), 0, W - 1)
                ry = np.clip((Y[..., None] + p * 0.34 * np.sin(ang)).round().astype(int), 0, H - 1)
                ok = m[ry, rx].mean(axis=-1) >= 0.75
                if ok.sum() < 4: continue
                cen = g[np.clip(Y.astype(int), 0, H - 1), np.clip(X.astype(int), 0, W - 1)]
                sc = ((g[ry, rx].mean(axis=-1) - cen) * ok).sum()
                if best is None or sc > best[0]: best = (sc, ox % p, oy % p, p)
    return best[1], best[2], best[3], best[3]
