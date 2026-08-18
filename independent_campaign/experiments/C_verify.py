"""C_verify.py -- exact isosceles-free verifier, integer arithmetic only.

Problem: S subseteq {0..n-1}^2 is VALID iff there are NO three distinct
a,b,c in S with d(a,b) = d(b,c)  (b is the apex).
Equivalently: for every b in S, the multiset of squared distances from b
to S\{b} has no repeats.

All arithmetic is on integer SQUARED distances.  No floats anywhere.
"""
from itertools import combinations


def is_valid(S):
    """O(|S|^2) exact check via per-apex distinct-distance test."""
    P = list(S)
    m = len(P)
    if len(set(P)) != m:
        raise ValueError("multiset passed to is_valid")
    for i in range(m):
        xi, yi = P[i]
        seen = set()
        for j in range(m):
            if j == i:
                continue
            xj, yj = P[j]
            d = (xi - xj) * (xi - xj) + (yi - yj) * (yi - yj)
            if d in seen:
                return False
            seen.add(d)
    return True


def is_valid_triples(S):
    """Independent O(|S|^3) reference check straight from the definition."""
    P = list(S)
    for a, b, c in combinations(range(len(P)), 3):
        # try each of the three as apex
        for (u, v, w) in ((a, b, c), (b, a, c), (c, a, b)):
            xu, yu = P[u]
            xv, yv = P[v]
            xw, yw = P[w]
            d1 = (xu - xv) ** 2 + (yu - yv) ** 2
            d2 = (xu - xw) ** 2 + (yu - yw) ** 2
            if d1 == d2:
                return False
    return True


def violations(S):
    """Return list of (apex, p, q, r2) witnessing failures."""
    P = list(S)
    out = []
    for i, (xi, yi) in enumerate(P):
        seen = {}
        for j, (xj, yj) in enumerate(P):
            if j == i:
                continue
            d = (xi - xj) ** 2 + (yi - yj) ** 2
            if d in seen:
                out.append((P[i], seen[d], P[j], d))
            else:
                seen[d] = P[j]
    return out


def in_grid(S, n):
    return all(0 <= x < n and 0 <= y < n for x, y in S)


def brute_force(n, k_from=None):
    """Total enumeration of ALL subsets of the n x n grid (tiny n only)."""
    pts = [(i, j) for i in range(n) for j in range(n)]
    N = len(pts)
    best = 0
    bestset = []
    # enumerate by size descending is wasteful; do full subset scan for n<=3,
    # otherwise incremental DFS over all subsets (still complete).
    def dfs(start, cur):
        nonlocal best, bestset
        if len(cur) > best:
            best = len(cur)
            bestset = list(cur)
        for t in range(start, N):
            cur.append(pts[t])
            if is_valid(cur):
                dfs(t + 1, cur)
            cur.pop()
    dfs(0, [])
    return best, bestset


if __name__ == "__main__":
    import sys
    # self-test: is_valid vs is_valid_triples on random sets
    import random
    random.seed(12345)
    n = 6
    pts = [(i, j) for i in range(n) for j in range(n)]
    bad = 0
    for _ in range(20000):
        k = random.randint(3, 8)
        S = random.sample(pts, k)
        if is_valid(S) != is_valid_triples(S):
            bad += 1
            print("MISMATCH", S)
    print("verifier cross-check (20000 random sets): mismatches =", bad)

    for n in range(1, 6):
        b, s = brute_force(n)
        print(f"brute force C({n}) = {b}   witness={sorted(s)}")
