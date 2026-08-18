#!/usr/bin/env python3
"""Independent verifier for Route C.

Brute force, deliberately naive: for every ordered triple of DISTINCT points
(a,b,c) it checks d(a,b) != d(b,c).  Exact integer (squared) distances only.
No shared code with the solver.

Usage:
    python verify.py FILE          # FILE contains lines "x y" (blank lines / '#' ignored)
    python verify.py --inline "0,0 1,3 2,7"   n
Prints VALID / INVALID plus the offending triple, the size, and the bounding box.
"""
import sys
from itertools import permutations


def read_points(path):
    pts = []
    with open(path) as f:
        for line in f:
            line = line.split('#')[0].strip()
            if not line:
                continue
            line = line.replace(',', ' ')
            parts = line.split()
            if len(parts) < 2:
                continue
            pts.append((int(parts[0]), int(parts[1])))
    return pts


def check(pts, n=None):
    errs = []
    m = len(pts)
    if len(set(pts)) != m:
        errs.append("DUPLICATE POINTS")
    if n is not None:
        for (x, y) in pts:
            if not (0 <= x < n and 0 <= y < n):
                errs.append("OUT OF RANGE %s (n=%d)" % ((x, y), n))
    # naive triple scan
    for a, b, c in permutations(pts, 3):
        d1 = (a[0]-b[0])**2 + (a[1]-b[1])**2
        d2 = (b[0]-c[0])**2 + (b[1]-c[1])**2
        if d1 == d2:
            errs.append("ISOSCELES apex=%s legs to %s,%s  d^2=%d" % (b, a, c, d1))
            if len(errs) > 5:
                return errs
    return errs


def main():
    if sys.argv[1] == '--inline':
        toks = sys.argv[2].replace(',', ' ').split()
        pts = [(int(toks[i]), int(toks[i+1])) for i in range(0, len(toks), 2)]
        n = int(sys.argv[3]) if len(sys.argv) > 3 else None
    else:
        pts = read_points(sys.argv[1])
        n = int(sys.argv[2]) if len(sys.argv) > 2 else None
    errs = check(pts, n)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    print("size=%d  bbox=[%d..%d]x[%d..%d]" % (len(pts), min(xs), max(xs), min(ys), max(ys)))
    if errs:
        print("INVALID")
        for e in errs[:6]:
            print("  ", e)
        sys.exit(1)
    print("VALID")


if __name__ == '__main__':
    main()
