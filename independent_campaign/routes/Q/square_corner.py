"""Candidate mechanism: the SQUARE-CORNER (rotated-corner) constraint.

  b, b+w, b+w^perp  are three vertices of a square; |w| = |w^perp|, so
  b+w and b+w^perp are equidistant from b.  Isosceles-free => forbidden, for EVERY w.

Pattern data with apex b: a = b+w, c = b+w^perp,  u = b-a = -w,  v = c-b = w^perp.
For a direction e:  U = <u,e> = -<w,e>,  V = <v,e> = det(w,e) = w1*e2 - w2*e1.
3-AP-freeness of W_e kills the configuration iff
  P1: U=V!=0   <=> w1(e1+e2)   + w2(e2-e1)   = 0
  P2: U+2V=0   <=> w1(-e1+2e2) + w2(-e2-2e1) = 0
  P3: 2U+V=0   <=> w1(-2e1+e2) + w2(-2e2-e1) = 0
each a single linear equation in w: at most 3 lines through the origin per direction.
"""
import numpy as np, sys, collections
from math import gcd
from patterns import dirset, norm_dir

def killed_w(e, R):
    """Set of w in [-R,R]^2 whose square-corner is killed by direction e."""
    e1, e2 = e
    lines = [(e1 + e2, e2 - e1), (-e1 + 2 * e2, -e2 - 2 * e1), (-2 * e1 + e2, -2 * e2 - e1)]
    out = set()
    for (c1, c2) in lines:
        if c1 == 0 and c2 == 0:
            continue  # would kill everything; check whether this can happen
        for w1 in range(-R, R + 1):
            for w2 in range(-R, R + 1):
                if (w1, w2) == (0, 0): continue
                if c1 * w1 + c2 * w2 == 0:
                    # exclude degenerate: need the corresponding U or V nonzero
                    U = -(w1 * e1 + w2 * e2); V = w1 * e2 - w2 * e1
                    if (U == V and U != 0) or (U + 2 * V == 0 and U != 0) or (2 * U + V == 0 and V != 0):
                        out.add((w1, w2))
    return out

def coverage(E, R):
    tot = (2 * R + 1) ** 2 - 1
    K = set()
    for e in E: K |= killed_w(e, R)
    return len(K), tot

def count_square_corners(S):
    """Count triples (b, b+w, b+w^perp) inside S."""
    P = set(map(tuple, S.tolist()))
    cnt = 0; ws = collections.Counter()
    for (bx, by) in P:
        for (ax, ay) in P:
            w = (ax - bx, ay - by)
            if w == (0, 0): continue
            c = (bx - w[1], by + w[0])
            if c in P:
                cnt += 1
                ws[norm_dir(w)] += 1
    return cnt, ws   # each unordered square-corner counted twice (w and w^perp swap)

if __name__ == '__main__':
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    print(f"Fraction of w in [-{R},{R}]^2 whose square-corner is excluded by the "
          f"3-AP-freeness of the projections:")
    for name in ['axis', 'Q4', '2', '3', '4', '6']:
        E = dirset(name)
        k, tot = coverage(E, R)
        print(f"  E={name:5s} |E|={len(E):3d}: killed {k}/{tot} = {100.0*k/tot:.2f}%"
              f"   (bound 3|E|(2R+1)/(2R+1)^2 = {300.0*len(E)/(2*R+1):.2f}%)")
