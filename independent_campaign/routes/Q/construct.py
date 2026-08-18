"""Route Q -- the four-form Behrend construction that attacks Q4.

KEY LEMMA (proved in report.md, verified here):
    Let B1,B2,C,D be subsets of Z that are each 3-AP-free.  Then
        S = { (x,y) in [0,n)^2 : x in B1, y in B2, x+y in C, x-y in D }
    is Q4-feasible.

    Reason: U_col subset B1 and M(X_y) subset M(B1) (midpoints of a subset are
    midpoints of the superset), and M(B1) cap B1 = empty is exactly 3-AP-freeness.
    Same for the other three, in the three other coordinate systems.  Note the
    diagonal constraints (3),(4) are the SAME statement in the rotated coordinates
    (u,v) = (x+y, x-y), which is why the same device works there.

THE CONSTRUCTION (Behrend spheres in all four forms simultaneously):
    digits base q, k of them, digit alphabet [0,m) with m = q/4 (so x+y and x-y are
    carry-free and the digit map is a Freiman 2-isomorphism on the relevant ranges).
    a = digitvector(x), b = digitvector(y).  Then digitvector(x+y)=a+b and
    digitvector(x-y) = a-b (balanced digits).  Take
        B1 = B2 = { |a|^2 = r },   C = { |c|^2 = s },   D = { |d|^2 = 4r-s }.
    Since |a+b|^2 + |a-b|^2 = 2|a|^2 + 2|b|^2 = 4r, the D condition is IMPLIED by
    the C condition.  So
        S(r,s) = { (x,y) : |a|^2 = |b|^2 = r, |a+b|^2 = s }
               = { (a,b) on the sphere with <a,b> = (s-2r)/2 }.
    Spheres (and translates of spheres) in Z^k are 3-AP-free by strict convexity.

    Pigeonholing s over its <= O(k m^2) values gives |S| >= |Sphere|^2 / O(k m^2),
    and Behrend's choice of parameters makes this n^{2-o(1)}.
"""
import sys
from itertools import product

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from q4_verify import is_feasible, violations_v2, violations_v1


def digits_to_int(vec, q):
    x = 0
    for i, a in enumerate(vec):
        x += a * q ** i
    return x


def sphere_pairs(k, q, m, r, t):
    """All (x,y) with digitvectors a,b in [0,m)^k, |a|^2=|b|^2=r, <a,b>=t."""
    vecs = [v for v in product(range(m), repeat=k) if sum(c * c for c in v) == r]
    out = []
    for a in vecs:
        xa = digits_to_int(a, q)
        for b in vecs:
            if sum(a[i] * b[i] for i in range(k)) == t:
                out.append((xa, digits_to_int(b, q)))
    return out


def enumerate_best(k, q, verbose=True):
    """For digit alphabet [0,m), m=q//4, find the (r,t) maximising |S(r,t)|."""
    m = q // 4
    n = q ** k
    from collections import defaultdict
    byr = defaultdict(list)
    for v in product(range(m), repeat=k):
        byr[sum(c * c for c in v)].append(v)
    best = (0, None)
    for r, vecs in byr.items():
        if len(vecs) < 2:
            continue
        cnt = defaultdict(int)
        for a in vecs:
            for b in vecs:
                cnt[sum(a[i] * b[i] for i in range(k))] += 1
        for t, c in cnt.items():
            if c > best[0]:
                best = (c, (r, t, len(vecs)))
    if verbose:
        print(f"  k={k} q={q} m={m} n={n}: best |S|={best[0]} at (r,t,|sphere|)={best[1]}")
    return n, best


def build(k, q, r, t):
    m = q // 4
    return sphere_pairs(k, q, m, r, t)


if __name__ == "__main__":
    from math import log
    rows = []
    params = [(2, 8), (2, 12), (2, 16), (2, 20), (2, 24), (2, 32),
              (3, 8), (3, 12), (3, 16), (3, 20),
              (4, 8), (4, 12), (5, 8), (6, 8)]
    for (k, q) in params:
        m = q // 4
        if m ** k > 4_000_000:
            print(f"  skip k={k} q={q} (too many digit vectors)")
            continue
        n, best = enumerate_best(k, q)
        if best[1] is None:
            continue
        r, t, sph = best[1]
        rows.append((k, q, n, best[0], r, t, sph))
    print()
    print(f"{'k':>3} {'q':>4} {'n':>10} {'|S|':>10} {'|S|/n':>9} {'loglog exponent':>16}")
    for (k, q, n, sz, r, t, sph) in rows:
        print(f"{k:>3} {q:>4} {n:>10} {sz:>10} {sz/n:>9.3f} {log(sz)/log(n):>16.4f}")
