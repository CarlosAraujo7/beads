"""Procura, por CONTEÚDO, moldes novos que já existem no catálogo (a conferência por MD5 só pega arquivos idênticos;
a mesma arte salva em outro arquivo/tamanho passa batida).

uso (na raiz do projeto):  python tools/dupcheck.py tools/data/final13.json
Para cada molde do JSON mostra o mais parecido do templates.js (tamanho igual ±2, deslocamento ±1, % de contas iguais).
>= 0.60 vira "PARECIDO": olhe os dois; ~0.99 é a mesma arte (não inclua de novo).
"""
import os, sys, json
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import tplfile

ROOT = os.path.dirname(SP)
cat = tplfile.parse(os.path.join(ROOT, 'templates.js'))['items']
new = json.load(open(sys.argv[1], encoding='utf-8'))


def sim(a, b):
    best = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            same = tot = 0
            H = max(len(a), len(b) + 2); W = max(len(a[0]), len(b[0]) + 2)
            for y in range(H):
                for x in range(W):
                    ca = a[y][x] if 0 <= y < len(a) and 0 <= x < len(a[y]) else '.'
                    yy, xx = y + dy, x + dx
                    cb = b[yy][xx] if 0 <= yy < len(b) and 0 <= xx < len(b[yy]) else '.'
                    if ca == '.' and cb == '.': continue
                    tot += 1; same += (ca == cb)
            if tot: best = max(best, same / tot)
    return best


for n, g, r in new:
    res = []
    for t in cat:
        h, w = len(t['rows']), len(t['rows'][0])
        if abs(h - len(r)) <= 2 and abs(w - len(r[0])) <= 2:
            res.append((sim(r, t['rows']), t['name']))
    res.sort(reverse=True)
    top = res[0] if res else (0, '-')
    flag = '  <<< PARECIDO' if top[0] > 0.6 else ''
    print(f'{n[:44]:46s} melhor: {top[0]:.2f} {top[1][:40]}{flag}')
