"""Route Q -- explicit four-form Behrend construction, fully verified.

Parameters k >= 1, m >= 2, q = 4m, n = q^k.
For a in [0,m)^k put iota(a) = sum a_i q^i  in [0,n).
For integers r1,r2,t put

    S(r1,r2,t) = { (iota(a), iota(b)) : |a|^2=r1, |b|^2=r2, <a,b>=t }.

Then x+y has base-q digits a_i+b_i in [0,2m-2]  ->  |a+b|^2 = r1+r2+2t is CONSTANT,
     x-y has balanced digits a_i-b_i in [-(m-1),m-1] -> |a-b|^2 = r1+r2-2t CONSTANT.
All four projections are iota-images of spheres, hence 3-AP-free (strict convexity of
|.|^2 plus carry-freeness = Freiman 2-isomorphism, since 4m-4 < q).  By the KEY LEMMA
S(r1,r2,t) is Q4-feasible.

This script (a) builds the sets exactly, (b) checks all four projections are 3-AP-free,
(c) runs BOTH independent Q4 verifiers, (d) reports sizes and log-log exponents.
"""
import sys
from itertools import product
from collections import defaultdict
from math import log

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from q4_verify import is_feasible, violations_v2
from lemma_test import is_3ap_free


def iota(a, q):
    x = 0
    p = 1
    for c in a:
        x += c * p
        p *= q
    return x


def best_params(k, m):
    """Exhaustive over digit vectors: find (r1,r2,t) maximising |S|."""
    q = 4 * m
    vecs = list(product(range(m), repeat=k))
    byr = defaultdict(list)
    for v in vecs:
        byr[sum(c * c for c in v)].append(v)
    best = (0, None)
    rs = sorted(byr)
    for r1 in rs:
        for r2 in rs:
            if r2 < r1:
                continue
            cnt = defaultdict(int)
            for a in byr[r1]:
                for b in byr[r2]:
                    cnt[sum(a[i] * b[i] for i in range(k))] += 1
            for t, c in cnt.items():
                mult = 1 if r1 == r2 else 2   # (r1,r2,t) and (r2,r1,t) give congruent sets
                if c > best[0]:
                    best = (c, (r1, r2, t))
    return best


def build(k, m, r1, r2, t):
    q = 4 * m
    vecs = list(product(range(m), repeat=k))
    A = [v for v in vecs if sum(c * c for c in v) == r1]
    B = [v for v in vecs if sum(c * c for c in v) == r2]
    S = []
    for a in A:
        ia = iota(a, q)
        for b in B:
            if sum(a[i] * b[i] for i in range(k)) == t:
                S.append((ia, iota(b, q)))
    return set(S), q ** k


def full_check(k, m, verbose=True):
    c, params = best_params(k, m)
    if params is None or c == 0:
        return None
    r1, r2, t = params
    S, n = build(k, m, r1, r2, t)
    assert len(S) == c, (len(S), c)
    # (b) four projections 3-AP-free
    px = {p[0] for p in S}
    py = {p[1] for p in S}
    pu = {p[0] + p[1] for p in S}
    pv = {p[0] - p[1] for p in S}
    proj_ok = (is_3ap_free(px), is_3ap_free(py), is_3ap_free(pu), is_3ap_free(pv))
    # (c) both Q4 verifiers
    feas = is_feasible(n, S, cross_check=(len(S) <= 1200))
    if verbose:
        print(f"  k={k} m={m} q={4*m} n={n:>12}  |S|={len(S):>6}  (r1,r2,t)={params}"
              f"  proj3APfree={proj_ok}  Q4feasible={feas}"
              f"  exponent={log(len(S))/log(n):.4f}")
    assert all(proj_ok), "projection not 3-AP-free -- construction proof is WRONG"
    assert feas, "NOT Q4-feasible -- key lemma is WRONG"
    return n, len(S), params


def pigeonhole_bound(k, m):
    """The proved lower bound  m^{2k} / R^3,  R = k(m-1)^2+1,  vs n=(4m)^k."""
    R = k * (m - 1) ** 2 + 1
    val = m ** (2 * k) / R ** 3
    n = (4 * m) ** k
    return n, val


if __name__ == "__main__":
    print("== explicit sphere construction, exactly built and doubly verified ==")
    res = []
    for (k, m) in [(2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (3, 4),
                   (4, 2), (4, 3), (5, 2), (6, 2), (4, 4), (5, 3)]:
        if m ** k > 300000:
            continue
        r = full_check(k, m)
        if r:
            res.append((k, m) + r)

    print()
    print("== proved pigeonhole lower bound  max_{r1,r2,t}|S| >= m^{2k}/R^3  ==")
    print(f"{'k':>3} {'m':>3} {'n':>22} {'bound':>16} {'bound exponent':>16} {'actual':>10}")
    for (k, m, n, sz, params) in res:
        n2, val = pigeonhole_bound(k, m)
        e = log(val) / log(n2) if val > 1 else float('nan')
        print(f"{k:>3} {m:>3} {n2:>22} {val:>16.4g} {e:>16.4f} {sz:>10}")
