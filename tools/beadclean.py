"""Limpeza de BORDAS de moldes convertidos de ilustração (pedido do usuário, 2026-10-30, Cavaleiros da remessa 20: "muito ruído principalmente nas bordas, contas soltas,
espaços entre as pernas e cores aleatórias nas bordas; pedaços de fundo que viram branco").

  clean(rows)            -> linhas limpas. Passos (só mexe na BORDA e em contas isoladas; o miolo do desenho fica):
     1. pontas: conta sem vizinho de lado (só diagonal) sai; conta com 1 vizinho de lado e que não é contorno sai (1 passada: linhas finas como correntes só perdem a ponta)
     2. halo: conta clara e sem cor (cinza/branco) na borda que tem o vazio de um lado e o contorno preto do lado oposto = sobra do antisserrilhado de fora do contorno -> sai
     3. cor avulsa na borda: conta da borda sem nenhuma vizinha (8) da mesma cor -> vira a cor mais comum das vizinhas (ou sai, se tiver só 1 vizinha)
     4. cor avulsa no miolo: conta sem vizinha da mesma cor e com >= 5 de 8 vizinhas de uma cor só -> vira essa cor
  enclosed_bg(rgb, m, min_px) -> máscara de fundo + buracos de BRANCO PURO (fundo da imagem) fechados dentro do desenho (entre pernas, entre asas e corpo), com área >= min_px
"""
import colorsys
import numpy as np
from palette import ALL

_HEX = {p['letter']: p['hex'] for p in ALL}


def _hsv(l):
    h = _HEX[l].lstrip('#'); return colorsys.rgb_to_hsv(*[int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def _pale(l):
    h, s, v = _hsv(l); return s < 0.12 and v > 0.6


def _dark(l):
    return _hsv(l)[2] < 0.25


N4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
N8 = N4 + ((-1, -1), (-1, 1), (1, -1), (1, 1))


def clean(rows, spur_passes=1, halo=True, pale_edge=2):
    import outline as O
    from collections import Counter
    g = [list(r) for r in rows]; H, W = len(g), len(g[0])
    at = lambda y, x: g[y][x] if 0 <= y < H and 0 <= x < W else '.'
    # 1. pontas
    for _ in range(spur_passes):
        kill = []
        for y in range(H):
            for x in range(W):
                c = g[y][x]
                if c == '.': continue
                n = sum(at(y + dy, x + dx) != '.' for dy, dx in N4)
                if n == 0 or (n == 1 and not _dark(c)): kill.append((y, x))
        for y, x in kill: g[y][x] = '.'
    # 2. halo claro fora do contorno
    if halo:
        kill = []
        for y in range(H):
            for x in range(W):
                c = g[y][x]
                if c == '.' or not _pale(c): continue
                for (dy, dx) in ((0, 1), (1, 0)):
                    a, b = at(y + dy, x + dx), at(y - dy, x - dx)
                    if (a == '.' and b != '.' and _dark(b)) or (b == '.' and a != '.' and _dark(a)):
                        # só se o lado vazio for mesmo o fora do desenho (não um furo de 1 conta): a outra direção também tem vazio perto
                        kill.append((y, x)); break
        for y, x in kill: g[y][x] = '.'
    # 2b. conta CLARA e sem cor na borda, quase sem vizinhas da mesma cor (<= 1 das 8): brilho/antisserrilhado solto na borda -> sai (pale_edge passadas)
    for _ in range(pale_edge):
        kill = []
        for y in range(H):
            for x in range(W):
                c = g[y][x]
                if c == '.' or not _pale(c): continue
                if not any(at(y + dy, x + dx) == '.' for dy, dx in N4): continue
                if sum(at(y + dy, x + dx) == c for dy, dx in N8) <= 1: kill.append((y, x))
        for y, x in kill: g[y][x] = '.'
        for y in range(H):                              # o que ficou sem vizinho de lado sai junto
            for x in range(W):
                if g[y][x] != '.' and not any(at(y + dy, x + dx) != '.' for dy, dx in N4): g[y][x] = '.'
    # 3 e 4. cores avulsas
    out = [r[:] for r in g]
    for y in range(H):
        for x in range(W):
            c = g[y][x]
            if c == '.': continue
            nb = [at(y + dy, x + dx) for dy, dx in N8]
            if c in nb: continue
            full = [v for v in nb if v != '.']
            edge = any(at(y + dy, x + dx) == '.' for dy, dx in N4)
            if not full: out[y][x] = '.'; continue
            top, cnt = Counter(full).most_common(1)[0]
            if edge:
                out[y][x] = top if cnt >= 2 else '.'
            elif cnt >= 5:
                out[y][x] = top
    return O.trim([''.join(r) for r in out])


def lone_dark(rows, min_nb=3):
    """conta escura SEM nenhuma vizinha escura (8) = fragmento de contorno fino da fonte pequena -> vira a cor mais comum das vizinhas (com >= min_nb vizinhas cheias).
    NÃO use em moldes com olho/boca de 1 conta (some)."""
    from collections import Counter
    g = [list(r) for r in rows]; H, W = len(g), len(g[0])
    at = lambda y, x: g[y][x] if 0 <= y < H and 0 <= x < W else '.'
    out = [r[:] for r in g]
    for y in range(H):
        for x in range(W):
            c = g[y][x]
            if c == '.' or not _dark(c): continue
            nb = [at(y + dy, x + dx) for dy, dx in N8]
            if any(v != '.' and _dark(v) for v in nb): continue
            full = [v for v in nb if v != '.']
            if len(full) >= min_nb: out[y][x] = Counter(full).most_common(1)[0][0]
    return [''.join(r) for r in out]


def drop_edge(rows, letters, passes=2):
    """apaga as contas das letras `letters` que encostam no vazio (borda de fora), `passes` vezes: aro claro de adesivo em volta do contorno"""
    import outline as O
    g = [list(r) for r in rows]; H, W = len(g), len(g[0])
    at = lambda y, x: g[y][x] if 0 <= y < H and 0 <= x < W else '.'
    for _ in range(passes):
        kill = [(y, x) for y in range(H) for x in range(W) if g[y][x] in letters and any(at(y + dy, x + dx) == '.' for dy, dx in N4)]
        for y, x in kill: g[y][x] = '.'
    return O.trim([''.join(r) for r in g])


def enclosed_bg(rgb, m, min_px, tol=6, spread=8, maxd=None):
    """acrescenta à máscara de fundo (m: True = fundo) os buracos FECHADOS dentro da figura que têm a cor do fundo da própria imagem (mediana da borda, até `tol`)
    e área >= min_px. maxd (px): só os que chegam até maxd do fundo de fora (vão entre pernas, asas, correntes); o branco no MEIO da figura (rosto, olho, brilho) fica."""
    import cv2
    edge = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]).astype(int)
    ref = np.median(edge, axis=0)
    a = rgb.astype(int)
    white = (np.abs(a - ref).max(axis=2) <= tol) & ((a.max(axis=2) - a.min(axis=2)) <= spread) & ~m
    k, lab, st, _ = cv2.connectedComponentsWithStats(white.astype(np.uint8), connectivity=4)
    ok = np.zeros(k, bool); ok[1:] = st[1:, 4] >= min_px
    if maxd is not None and k > 1:
        dist = cv2.distanceTransform((~m).astype(np.uint8), cv2.DIST_L2, 3)
        mind = np.full(k, np.inf); np.minimum.at(mind, lab.ravel(), dist.ravel())
        ok &= mind <= maxd
    return m | ok[lab]
