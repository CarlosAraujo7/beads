import sys, os, math
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import numpy as np, cv2

def detect_centers(gray, rmin, rmax, param2=16, param1=80, blur=5):
    b = cv2.GaussianBlur(gray, (blur, blur), 1.5)
    c = cv2.HoughCircles(b, cv2.HOUGH_GRADIENT, dp=1, minDist=int(rmin * 1.6), param1=param1, param2=param2, minRadius=rmin, maxRadius=rmax)
    return np.zeros((0, 3)) if c is None else c[0]

def nn_stats(P):
    d = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2); np.fill_diagonal(d, 1e9)
    return d, d.min(1)

def lattice(img_bgr, rmin, rmax, param2=16, pitch=None, verbose=False, centers=None):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    C = detect_centers(gray, rmin, rmax, param2) if centers is None else np.hstack([np.asarray(centers, float), np.full((len(centers), 1), rmin)])
    P = C[:, :2]
    d, nn = nn_stats(P)
    p = pitch or float(np.median(nn))
    # mantem circulos com vizinhos a ~1 passo (descarta falsos positivos do fundo)
    good = ((d > 0.8 * p) & (d < 1.25 * p)).sum(1) >= 2
    P = P[good]
    # rotacao: angulo medio dos vetores entre vizinhos (modulo 90 graus)
    d, _ = nn_stats(P); ang = []
    for i in range(len(P)):
        for j in np.nonzero((d[i] > 0.8 * p) & (d[i] < 1.25 * p))[0]:
            v = P[j] - P[i]; ang.append(math.atan2(v[1], v[0]) * 4)
    th = math.atan2(np.mean(np.sin(ang)), np.mean(np.cos(ang))) / 4
    th_deg = math.degrees(th)
    h, w = img_bgr.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), th_deg, 1.0)
    rot = cv2.warpAffine(img_bgr, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    Pr = (np.hstack([P, np.ones((len(P), 1))]) @ M.T)
    # colunas e linhas por agrupamento 1D
    def groups(v):
        o = np.argsort(v); v = v[o]; gs = [[v[0]]]
        for a in v[1:]:
            if a - gs[-1][-1] > 0.5 * p: gs.append([a])
            else: gs[-1].append(a)
        return [float(np.mean(g)) for g in gs]
    def fill(g):
        out = [g[0]]
        for a in g[1:]:
            n = int(round((a - out[-1]) / p))
            for k in range(1, n): out.append(out[-1] + (a - out[-1]) / (n - k + 1))
            out.append(a)
        return out
    cx = fill(groups(Pr[:, 0])); cy = fill(groups(Pr[:, 1]))
    # estende a grade ate as bordas da imagem (contas pretas nao sao detectadas e podem estar alem da ultima deteccao)
    def extend(c, lim, step):
        c = list(c)
        st = (c[-1] - c[0]) / max(1, len(c) - 1) if len(c) > 1 else step
        while c[0] - st > p * 0.6: c.insert(0, c[0] - st)
        while c[-1] + st < lim - p * 0.6: c.append(c[-1] + st)
        return c
    cx = extend(cx, w, p); cy = extend(cy, h, p)
    if verbose: print('circulos', len(C), 'bons', len(P), 'passo %.1f' % p, 'rot %.2f' % th_deg, 'colunas', len(cx), 'linhas', len(cy))
    return rot, np.array(cx), np.array(cy), p, th_deg, Pr

def sample(rot_bgr, cx, cy, p, ring=(0.27, 0.45)):
    h, w = rot_bgr.shape[:2]; rgb = rot_bgr[..., ::-1].astype(float)
    out = np.zeros((len(cy), len(cx), 3))
    yy, xx = np.mgrid[-int(p * ring[1]) - 1:int(p * ring[1]) + 2, -int(p * ring[1]) - 1:int(p * ring[1]) + 2]
    dd = np.hypot(xx, yy) / p; sel = (dd >= ring[0]) & (dd <= ring[1])
    for j, y in enumerate(cy):
        for i, x in enumerate(cx):
            ys = int(round(y)) + yy[sel]; xs = int(round(x)) + xx[sel]
            ok = (ys >= 0) & (ys < h) & (xs >= 0) & (xs < w)
            out[j, i] = np.median(rgb[ys[ok], xs[ok]], axis=0) if ok.any() else (255, 255, 255)
    return out

def kmeans_colors(arr, k=9, seed=1):
    X = arr.reshape(-1, 3).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.5)
    _, lab, cen = cv2.kmeans(X, k, None, crit, 5, cv2.KMEANS_PP_CENTERS)
    return lab.reshape(arr.shape[:2]), cen
