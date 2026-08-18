"""Scan small n: intersection adversary with best 3-AP-free sets, count isosceles triples."""
import numpy as np, sys, json, time
from qlib import greedy_3ap_free, base3_set, is_3ap_free, q4_violations, iso_triples
from build_adv import best_3apfree

def build(n, A, B, W, Z):
    """A,B subset of [0,n); W subset of Z (x+y values); Z subset of Z (x-y values)."""
    As = np.zeros(n, bool); As[A[(A >= 0) & (A < n)]] = True
    Bs = np.zeros(n, bool); Bs[B[(B >= 0) & (B < n)]] = True
    Ws = np.zeros(2 * n - 1, bool)
    Wv = W[(W >= 0) & (W < 2 * n - 1)]; Ws[Wv] = True
    Zs = np.zeros(2 * n - 1, bool)
    Zv = Z[(Z >= -(n - 1)) & (Z < n)]; Zs[Zv + (n - 1)] = True
    X = np.repeat(np.arange(n, dtype=np.int64), n).reshape(n, n); Y = X.T.copy()
    M = As[X] & Bs[Y] & Ws[X + Y] & Zs[X - Y + (n - 1)]
    xs, ys = np.nonzero(M)
    return np.stack([xs, ys], 1).astype(np.int64)

def opt_shifts(n, T, Tp, seed=0, iters=60):
    rng = np.random.default_rng(seed)
    a = int(rng.integers(-int(T.max()), n)); b = int(rng.integers(-int(T.max()), n))
    w = int(rng.integers(-int(Tp.max()), 2 * n - 1))
    zz = int(rng.integers(-int(Tp.max()) - (n - 1), n))
    cur = len(build(n, T + a, T + b, Tp + w, Tp + zz))
    for it in range(iters):
        improved = False
        for coord in range(4):
            bestv, bestc = cur, None
            if coord == 0: rng_ = range(-int(T.max()), n)
            elif coord == 1: rng_ = range(-int(T.max()), n)
            elif coord == 2: rng_ = range(-int(Tp.max()), 2 * n - 1)
            else: rng_ = range(-int(Tp.max()) - (n - 1), n)
            for s in rng_:
                aa, bb, ww, zzz = a, b, w, zz
                if coord == 0: aa = s
                elif coord == 1: bb = s
                elif coord == 2: ww = s
                else: zzz = s
                v = len(build(n, T + aa, T + bb, Tp + ww, Tp + zzz))
                if v > bestv: bestv, bestc = v, s
            if bestc is not None:
                if coord == 0: a = bestc
                elif coord == 1: b = bestc
                elif coord == 2: w = bestc
                else: zz = bestc
                cur = bestv; improved = True
        if not improved: break
    return cur, (a, b, w, zz)

if __name__ == '__main__':
    ns = [int(x) for x in sys.argv[1].split(',')]
    nseeds = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    t0 = time.time()
    for n in ns:
        T = best_3apfree(n, restarts=60)
        Tp = best_3apfree(2 * n - 1, restarts=60, seed0=999)
        best = (0, None)
        for s in range(nseeds):
            v, sh = opt_shifts(n, T, Tp, seed=s)
            if v > best[0]: best = (v, sh)
        a, b, w, zz = best[1]
        S = build(n, T + a, T + b, Tp + w, Tp + zz)
        tri = iso_triples(S)
        qv = q4_violations(S)
        nq = sum(len(x) for x in qv.values())
        print(f"n={n} |T|={len(T)} |T'|={len(Tp)} |S|={len(S)} "
              f"n^(2/3)={n**(2/3):.0f} triples={len(tri)} q4viol={nq} shifts={best[1]} "
              f"({time.time()-t0:.0f}s)", flush=True)
        np.savez(f'small_{n}.npz', S=S, T=T, Tp=Tp, shifts=np.array(best[1]))
