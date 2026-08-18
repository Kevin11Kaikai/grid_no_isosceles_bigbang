"""Elementary power attempt for Q_SQ. Identities machine-checked. No iso6 import.

Stencil: apex b=(x,y), w=(p,q) ≠ 0 ⇒ third point (x-q, y+p)  [R_+]
and (x+q, y-p) [R_-].

A false O(n) bound is rejected by the peeling construction.
"""
from __future__ import annotations

from collections import defaultdict

from sq import is_sq_free, square_corners


def count_pairs(pts):
    """Number of ordered (b, w) with b, b+w both in S, w≠0."""
    P = set(map(tuple, pts))
    c = 0
    for b in P:
        for a in P:
            if a != b:
                c += 1
    return c


def count_in_grid_completions(pts, n):
    """(b,w) with b, b+w in S and at least one R±(w) in the GRID (not necessarily S)."""
    P = set(map(tuple, pts))
    in_grid = 0
    in_S = 0
    for b in P:
        bx, by = b
        for a in P:
            if a == b:
                continue
            p, q = a[0] - bx, a[1] - by
            for cx, cy in ((bx - q, by + p), (bx + q, by - p)):
                if 0 <= cx < n and 0 <= cy < n:
                    in_grid += 1
                    if (cx, cy) in P:
                        in_S += 1
    return {"pair_completions_in_grid": in_grid, "pair_completions_in_S": in_S}


def row_sizes(pts, n):
    r = [0] * n
    for x, y in pts:
        if 0 <= y < n:
            r[y] += 1
    return r


def cs_row_bound(pts, n):
    """Naive CS: m = Σ r_i, Σ r_i^2 ≥ m^2 / n.

    This does NOT by itself bound m: a full row has r_0=n, m=n, no contradiction.
    """
    r = row_sizes(pts, n)
    m = sum(r)
    s2 = sum(v * v for v in r)
    return {"m": m, "sum_r2": s2, "m2_over_n": (m * m / n) if n else 0.0}


def try_n32_argument(pts, n):
    """The attempted O(n^{3/2}) counting.

    Let P = # ordered pairs (b,a) in S^2, a≠b. P = m(m-1).
    For each pair, two candidate third vertices R±. Let G be the number of
    those that lie in the grid, I the number that lie in S.

    Sq-free ⇒ I = 0 (each unordered corner counted a constant times).

    FALSE STEP that would give O(n^{3/2}): 'G ≥ c P  and G ≤ m n' or
    'G ≤ n^2 m' etc. We measure the actual G vs P vs m n on this set.
    """
    m = len(pts)
    P = m * (m - 1)
    cc = count_in_grid_completions(pts, n)
    G, I = cc["pair_completions_in_grid"], cc["pair_completions_in_S"]
    return {
        "m": m,
        "P": P,
        "G": G,
        "I": I,
        "G/P": (G / P) if P else 0.0,
        "m*n": m * n,
        "n**1.5": n ** 1.5,
        "m <= n**1.5": m <= n ** 1.5 + 1e-9,
        "G <= m*n": G <= m * n,
        "G <= 2*P": G <= 2 * P + 1e-9,
    }


def random_set(n, m, rng):
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    return cells[:m]
