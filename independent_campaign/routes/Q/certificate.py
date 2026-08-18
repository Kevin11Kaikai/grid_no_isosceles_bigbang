"""Explicit certificate: a Behrend-intersection adversary that
  (i) has A,B,W,Z all 3-AP-free,
  (ii) satisfies all four Q4 line-kill constraints (independent verifier),
  (iii) CONTAINS a square corner {b, b+w, b+w^perp}, hence is NOT isosceles-free.
Built by seeding the greedy 3-AP-free construction with the required elements."""
import numpy as np, sys
from qlib import is_3ap_free, q4_violations, iso_triples, is_iso_free
from scan_small import build

def greedy_seeded(N, seed_elems, rng_seed=0, lo=0):
    """3-AP-free subset of [lo, lo+N) containing seed_elems."""
    S = list(seed_elems)
    ok, wit = is_3ap_free(np.array(S))
    assert ok, f"seed itself not 3-AP-free: {wit}"
    s = set(S)
    rng = np.random.default_rng(rng_seed)
    for v in rng.permutation(N) + lo:
        v = int(v)
        if v in s: continue
        good = True
        for u in s:
            if (u + v) % 2 == 0 and (u + v) // 2 in s: good = False; break
            if 2 * v - u in s: good = False; break
            if (2 * u - v) in s: good = False; break
        if good: s.add(v)
    return np.array(sorted(s), dtype=np.int64)

def main(n, w, b, rng_seed=0):
    w1, w2 = w; bx, by = b
    pts = [(bx, by), (bx + w1, by + w2), (bx - w2, by + w1)]
    xs = sorted({p[0] for p in pts}); ys = sorted({p[1] for p in pts})
    ss = sorted({p[0] + p[1] for p in pts}); tt = sorted({p[0] - p[1] for p in pts})
    print("square corner points:", pts)
    print("  x-values", xs, "y-values", ys, "sigma", ss, "tau", tt)
    for nm, v in [('x', xs), ('y', ys), ('sigma', ss), ('tau', tt)]:
        ok, wit = is_3ap_free(np.array(v))
        print(f"  seed {nm} 3-AP-free: {ok}")
        if not ok: return None
    A = greedy_seeded(n, xs, rng_seed + 1, 0)
    B = greedy_seeded(n, ys, rng_seed + 2, 0)
    W = greedy_seeded(2 * n - 1, ss, rng_seed + 3, 0)
    Z = greedy_seeded(2 * n - 1, tt, rng_seed + 4, -(n - 1))
    for nm, arr in [('A', A), ('B', B), ('W', W), ('Z', Z)]:
        ok, wit = is_3ap_free(arr)
        print(f"  |{nm}|={len(arr)} 3-AP-free={ok}")
        assert ok
    S = build(n, A, B, W, Z)
    v = q4_violations(S); nq = sum(len(t) for t in v.values())
    P = set(map(tuple, S.tolist()))
    has = all(p in P for p in pts)
    tri = iso_triples(S)
    print(f"  |S|={len(S)}  Q4 violations = {nq} (rows {len(v[1])} cols {len(v[2])} "
          f"diag {len(v[3])} anti {len(v[4])})")
    print(f"  contains the square corner: {has}")
    print(f"  isosceles-free: {is_iso_free(S)};  #isosceles triples = {len(tri)}")
    return S, A, B, W, Z

if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    w = (2, 3)
    b = (n // 3, n // 3)
    for rs in range(int(sys.argv[2]) if len(sys.argv) > 2 else 1):
        print(f"--- rng_seed={rs}")
        out = main(n, w, b, rs * 10)
