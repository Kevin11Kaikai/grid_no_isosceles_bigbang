"""Translated-copy coexistence.

THEOREM (proved separately): for legal A subset [n]^2 there are infinitely many
t with A u (A+(t,t)) legal.  Here we measure the SMALLEST separation, i.e. how
close two extremal blocks can be while both stay fully extremal.  If the
minimum ||v||_inf is O(n) then two "adjacent-scale" extremal blocks coexist and
no pairwise deficit exists at that scale.
Also tests 4 copies on a lattice {0,v1,v2,v1+v2} (the k=2 quadrant pattern).
"""
import sys, time, itertools
from iso import Exact, is_legal

def legal(pts):
    return is_legal(pts)[0]

def extremal(n):
    pts = [(x, y) for x in range(n) for y in range(n)]
    e = Exact(pts)
    v, s = e.solve()
    return v, s

def min_translate(A, n, maxv=None, direction=None):
    """smallest ||v||_inf with A u (A+v) legal."""
    if maxv is None: maxv = 12*n
    best = None
    for R in range(1, maxv+1):
        cands = []
        for a in range(-R, R+1):
            for b in (-R, R):
                cands.append((a, b)); cands.append((b, a))
        cands = sorted(set(c for c in cands if max(abs(c[0]), abs(c[1])) == R))
        for v in cands:
            if direction and (v[0]*direction[1] != v[1]*direction[0]):
                continue
            B = [(x+v[0], y+v[1]) for (x, y) in A]
            if legal(A+B):
                return R, v
    return None, None

def min_lattice4(A, n, maxv=None):
    """smallest R with v1,v2 of inf-norm <= R and all four copies legal."""
    if maxv is None: maxv = 6*n
    for R in range(1, maxv+1):
        vs = [(a, b) for a in range(-R, R+1) for b in range(-R, R+1)
              if max(abs(a), abs(b)) == R]
        vs2 = [(a, b) for a in range(0, R+1) for b in range(0, R+1)
               if max(abs(a), abs(b)) <= R and (a, b) != (0, 0)]
        for v1 in vs:
            if v1[0] < 0: continue
            for v2 in vs2:
                if v2 == v1: continue
                pts = []
                for (c1, c2) in [(0,0),(1,0),(0,1),(1,1)]:
                    dx = c1*v1[0]+c2*v2[0]; dy = c1*v1[1]+c2*v2[1]
                    pts += [(x+dx, y+dy) for (x, y) in A]
                if len(set(pts)) != 4*len(A):
                    continue
                if legal(pts):
                    return R, v1, v2
    return None, None, None

if __name__ == '__main__':
    ns = [int(x) for x in sys.argv[1:]] or [3,4,5,6,7]
    print(f"{'n':>3} {'C(n)':>5} {'minR(2copy)':>12} {'v':>12} {'R/n':>6} | "
          f"{'minR(4copy)':>12} {'v1':>10} {'v2':>10} {'R/n':>6}")
    for n in ns:
        c, A = extremal(n)
        t = time.time()
        R, v = min_translate(A, n)
        R4, v1, v2 = min_lattice4(A, n)
        print(f"{n:>3} {c:>5} {str(R):>12} {str(v):>12} "
              f"{(R/n if R else 0):>6.2f} | {str(R4):>12} {str(v1):>10} {str(v2):>10} "
              f"{(R4/n if R4 else 0):>6.2f}   ({time.time()-t:.0f}s)", flush=True)
