import sys, os
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import r6
def dump(i, px=None, dist=14, crop_img=None, mode=False, rows=None, cols=None):
    arr = r6.load_cells(i, px, crop_img=crop_img, mode=mode); sn = r6.snap(arr, dist); H, W, _ = sn.shape
    print('IMG', i, 'px', px, 'crop', crop_img, W, 'x', H)
    r0, r1 = rows if rows else (0, H); c0, c1 = cols if cols else (0, W)
    print('   ' + ''.join(str(x % 10) for x in range(c0, c1)))
    for y in range(r0, r1): print('%2d '%y + ''.join(r6.mapc(sn[y, x]) for x in range(c0, c1)))
if __name__ == '__main__':
    a = sys.argv[1:]
    kw = {}
    i = int(a[0]); 
    for t in a[1:]:
        k, v = t.split('=', 1)
        kw[k] = eval(v)
    dump(i, **kw)
