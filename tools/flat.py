import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import img2tpl as T

from palette import HEX_BY_LETTER
L2HEX = {l: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for l, h in HEX_BY_LETTER.items()}    # as 120 letras (moldes de qualquer das paletas)

def render_flat(items, path, scale=8, cols=4, cell=None, W=1500):
    """items = [(titulo, rows)]"""
    pad = 24; x = pad; y = pad; rowh = 0; pos = []
    for t, rows in items:
        w = len(rows[0]) * scale; h = len(rows) * scale + 18
        if x + w + pad > W: x = pad; y += rowh + pad; rowh = 0
        pos.append((x, y)); x += w + pad; rowh = max(rowh, h)
    H = y + rowh + pad
    im = Image.new('RGB', (W, H), (60, 60, 66)); d = ImageDraw.Draw(im)
    for (t, rows), (x, y) in zip(items, pos):
        d.text((x, y), f'{t}  {len(rows[0])}x{len(rows)}', fill=(255, 255, 255))
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                px, py = x + i * scale, y + 16 + j * scale
                if ch == '.':
                    c = (200, 200, 205) if (i + j) % 2 == 0 else (225, 225, 228)
                else:
                    c = L2HEX[ch]
                d.rectangle((px, py, px + scale - 1, py + scale - 1), fill=c)
    im.save(path)
