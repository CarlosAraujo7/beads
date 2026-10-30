"""Letras da paleta mais próximas de uma cor RGB (Lab, CIE76): python tools/nearpal.py r,g,b [r,g,b ...]"""
import sys, json, os
import numpy as np, cv2
SP = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(SP, 'data', 'palette.json'), encoding='utf-8'))
P = P if isinstance(P, list) else P.get('colors', P)
HEX = np.array([[int(c['hex'][i:i + 2], 16) for i in (1, 3, 5)] for c in P], np.uint8)
LAB = cv2.cvtColor(HEX[None], cv2.COLOR_RGB2LAB)[0].astype(float)
def near(rgb, k=3):
    l = cv2.cvtColor(np.array(rgb, np.uint8)[None, None], cv2.COLOR_RGB2LAB)[0, 0].astype(float)
    d = np.linalg.norm(LAB - l, axis=1); idx = np.argsort(d)[:k]
    return [(P[i]['code'], P[i]['letter'], P[i]['hex'], round(float(d[i]), 1)) for i in idx]
if __name__ == '__main__':
    for a in sys.argv[1:]:
        rgb = [int(v) for v in a.split(',')]; print(a, near(rgb))
