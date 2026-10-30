"""Conversão FIEL de gráficos com grade (revisão da remessa 19, 2026-10-30): o usuário notou que algumas conversões "perderam os olhos" (Eeveelutions: o olho azul-claro do Sylveon sumia).
Causas no `exact6` padrão: (1) `snap` (fusão no RGB, raio 16) junta cores diferentes que são vizinhas no gráfico; (2) `r5.despeckle120` troca célula isolada por uma cor parecida (ΔE < 11) da
vizinhança — e olhos/brilhos pequenos de cor clara são exatamente "células isoladas parecidas com o fundo".
Este módulo troca os dois por: fusão em **Lab** só de cores quase idênticas (ΔE76 ≤ T, a mais comum vence) e **nenhum despeckle**.
uso:
    import faithful
    with faithful.patched(T=6):
        rows = r6.exact6(...)        # qualquer chamada do pipeline dentro do bloco usa a conversão fiel
"""
import numpy as np, cv2
import r5, r6


def _lab(arr):
    a = np.clip(arr, 0, 255).astype(np.uint8).reshape(-1, 1, 3)
    return cv2.cvtColor(a, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(float) * np.array([100 / 255, 1, 1]) - np.array([0, 128, 128])


def smooth(arr, T=10.0):
    """tira o ruído de JPEG: uma célula que difere MENOS que T (Lab CIE76) da mediana dos 8 vizinhos+ela ganha a cor da mediana; detalhes que diferem mais (olhos, brilhos)
    ficam como estão. Células vazias (fundo) entram igual às outras (quem decide o fundo é o flood do exact6, antes)."""
    H, W, _ = arr.shape
    lab = _lab(arr.reshape(-1, 3)).reshape(H, W, 3)
    out = arr.copy()
    for y in range(H):
        for x in range(W):
            ys = slice(max(0, y - 1), min(H, y + 2)); xs = slice(max(0, x - 1), min(W, x + 2))
            nb = lab[ys, xs].reshape(-1, 3); med = np.median(nb, axis=0)
            if np.linalg.norm(lab[y, x] - med) < T:
                # cor RGB do vizinho cuja lab é a mais perto da mediana
                cand = arr[ys, xs].reshape(-1, 3); k = int(np.argmin(np.linalg.norm(nb - med, axis=1))); out[y, x] = cand[k]
    return out


def lab_snap(arr, T=6.0):
    """funde cores quase iguais (ruído de JPEG) na mais comum do grupo, medindo em Lab (CIE76)"""
    H, W, _ = arr.shape
    flat = arr.reshape(-1, 3)
    cols, inv, cnt = np.unique(flat.astype(np.int32), axis=0, return_inverse=True, return_counts=True)
    lab = _lab(cols)
    order = np.argsort(-cnt)
    rep = np.full(len(cols), -1)
    reps = []
    for i in order:
        hit = None
        for r in reps:
            if np.linalg.norm(lab[i] - lab[r]) <= T: hit = r; break
        if hit is None: reps.append(i); rep[i] = i
        else: rep[i] = hit
    # cor do grupo = MÉDIA ponderada dos membros (a mais comum podia estar deslocada: Jolteon amarelo-claro virava amarelo-oliva)
    mean = {}
    for r in set(rep.tolist()):
        m = rep == r
        mean[r] = (cols[m] * cnt[m][:, None]).sum(axis=0) / cnt[m].sum()
    table = np.array([mean[r] for r in rep])
    out = table[inv.reshape(-1)].reshape(H, W, 3)
    return np.round(out)


class patched:
    """T = fusão em Lab (0 = usa o snap RGB padrão do pipeline); smooth_T = suavização por vizinhos; desp_T = limiar do despeckle (None = sem despeckle; o padrão do pipeline é 11)"""
    def __init__(self, T=6.0, smooth_T=None, desp_T=None): self.T = T; self.smooth_T = smooth_T; self.desp_T = desp_T
    def __enter__(self):
        self._snap, self._desp = r6.snap, r5.despeckle120
        def snp(arr, dist=16):
            a = smooth(arr, self.smooth_T) if self.smooth_T else arr
            return lab_snap(a, self.T) if self.T else self._snap(a, dist)
        r6.snap = snp
        if self.desp_T: r5.despeckle120 = lambda rows, T=11.0, minsame=2: self._desp(rows, T=self.desp_T, minsame=minsame)
        else: r5.despeckle120 = lambda rows, *a, **k: rows
        return self
    def __exit__(self, *a):
        r6.snap, r5.despeckle120 = self._snap, self._desp
