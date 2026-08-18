"""
Isosceles-free point set verifier + tiny-case brute force.

DEFINITION
----------
S subset of {0,...,n-1}^2 is *isosceles-free* iff there do NOT exist three
distinct points a,b,c in S with d(a,b) = d(b,c)  (Euclidean distance).
Degenerate (collinear) isosceles triples count as forbidden: b the midpoint
of a 3-term AP is exactly the case d(a,b)=d(b,c) with a,b,c collinear.

Equivalent local form: for every b in S, the multiset of distances from b to
S\{b} has no repeats.

ALL ARITHMETIC IS EXACT INTEGER: we only ever compare SQUARED distances,
which are integers.  No floating point anywhere.
"""
from itertools import combinations


def d2(p, q):
    """Exact integer squared Euclidean distance."""
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def is_isofree(pts):
    """True iff pts (iterable of integer pairs) is isosceles-free.

    Method: for each apex b, collect squared distances to all other points and
    check for duplicates.  O(m^2) integer ops, exact.
    """
    pts = list(pts)
    if len(set(pts)) != len(pts):
        return False                      # repeated points are not a valid set
    m = len(pts)
    for i in range(m):
        seen = set()
        b = pts[i]
        for j in range(m):
            if i == j:
                continue
            r = d2(b, pts[j])
            if r in seen:
                return False
            seen.add(r)
    return True


def is_isofree_naive(pts):
    """Reference implementation: literally test every ordered triple.

    Used only to validate is_isofree().  O(m^3).
    """
    pts = list(pts)
    if len(set(pts)) != len(pts):
        return False
    for a, b, c in combinations(range(len(pts)), 3):
        A, B, C = pts[a], pts[b], pts[c]
        if d2(A, B) == d2(B, C):
            return False
        if d2(B, A) == d2(A, C):
            return False
        if d2(A, C) == d2(C, B):
            return False
    return True


def witnesses(pts):
    """Return list of (a,b,c) with b the apex, d(a,b)==d(b,c). Empty iff isofree."""
    pts = list(pts)
    out = []
    m = len(pts)
    for i in range(m):
        seen = {}
        for j in range(m):
            if i == j:
                continue
            r = d2(pts[i], pts[j])
            if r in seen:
                out.append((pts[seen[r]], pts[i], pts[j]))
            else:
                seen[r] = j
    return out


# ----------------------------------------------------------------------------
# Brute-force exact maximum, for validation on tiny boards.
# ----------------------------------------------------------------------------
def brute_max(n, m=None):
    """Exhaustive DFS over the n x m grid; returns (size, one witness set).

    Exhaustive because: points are considered in a fixed index order and at
    every index we branch on both 'take' and 'skip'; nothing is pruned except
    branches that are already infeasible (adding the point creates an
    isosceles triple) or that cannot beat the incumbent even if every
    remaining point were taken.  Both are sound.
    """
    if m is None:
        m = n
    P = [(x, y) for y in range(m) for x in range(n)]
    N = len(P)
    best = [0, []]
    cur = []

    def rec(i):
        if len(cur) + (N - i) <= best[0]:
            return
        if i == N:
            if len(cur) > best[0]:
                best[0] = len(cur)
                best[1] = list(cur)
            return
        p = P[i]
        # try taking p
        ok = True
        seen = set()
        for q in cur:
            r = d2(p, q)
            if r in seen:
                ok = False
                break
            seen.add(r)
        if ok:
            for q in cur:                       # q as apex, legs p and other
                rq = d2(q, p)
                for t in cur:
                    if t is q:
                        continue
                    if d2(q, t) == rq:
                        ok = False
                        break
                if not ok:
                    break
        if ok:
            cur.append(p)
            if len(cur) > best[0]:
                best[0] = len(cur)
                best[1] = list(cur)
            rec(i + 1)
            cur.pop()
        rec(i + 1)

    rec(0)
    return best[0], best[1]


if __name__ == "__main__":
    import random
    random.seed(1)
    # cross-validate the two verifiers on random sets
    bad = 0
    for trial in range(20000):
        n = random.randint(2, 7)
        k = random.randint(3, 7)
        pts = random.sample([(x, y) for x in range(n) for y in range(n)],
                            min(k, n * n))
        if is_isofree(pts) != is_isofree_naive(pts):
            bad += 1
            print("MISMATCH", pts)
    print("verifier cross-validation: %d mismatches in 20000 random sets" % bad)

    for n in range(1, 7):
        s, w = brute_max(n)
        print("brute_max C(%d) = %d   witness=%s" % (n, s, sorted(w)))
