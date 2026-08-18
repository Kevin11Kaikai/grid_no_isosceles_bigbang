"""Build the largest adversary S we can at given n by coordinate descent over shifts."""
import numpy as np, sys, json, time
from qlib import greedy_3ap_free, is_3ap_free, base3_set

def best_3apfree(N, restarts=40, seed0=0):
    best = base3_set(N)
    for s in range(restarts):
        T = greedy_3ap_free(N, seed=seed0 + s)
        if len(T) > len(best): best = T
    return np.array(sorted(best), dtype=np.int64)

def ind_from(base, shift, L):
    a = np.zeros(L, dtype=bool)
    v = base + shift
    v = v[(v >= 0) & (v < L)]
    a[v] = True
    return a

def scores(h, T, shifts_lo, shifts_hi):
    """sc[s-shifts_lo] = sum_{t in T} h[s+t] for s in [shifts_lo, shifts_hi)."""
    L = len(h)
    ns = shifts_hi - shifts_lo
    sc = np.zeros(ns, dtype=np.int64)
    s = np.arange(shifts_lo, shifts_hi)
    for t in T:
        idx = s + int(t)
        m = (idx >= 0) & (idx < L)
        sc[m] += h[idx[m]]
    return sc

def run(n, T, Tp, iters=40, seed=0, verbose=False):
    rng = np.random.default_rng(seed)
    LU = 2 * n - 1
    X = np.repeat(np.arange(n, dtype=np.int64), n).reshape(n, n)
    Y = X.T.copy()
    U = X + Y
    V = X - Y + (n - 1)
    aLo, aHi = -int(T.max()), n
    wLo, wHi = -int(Tp.max()), LU
    a = int(rng.integers(aLo, aHi)); b = int(rng.integers(aLo, aHi))
    w = int(rng.integers(wLo, wHi)); z = int(rng.integers(wLo, wHi))
    bestval = 0
    for it in range(iters):
        changed = False
        for coord in range(4):
            iA = ind_from(T, a, n); iB = ind_from(T, b, n)
            iW = ind_from(Tp, w, LU); iZ = ind_from(Tp, z, LU)
            if coord == 0:
                M0 = iB[Y] & iW[U] & iZ[V]
                h = np.bincount(X[M0], minlength=n)
                sc = scores(h, T, aLo, aHi); new = aLo + int(np.argmax(sc))
                if new != a: a = new; changed = True
            elif coord == 1:
                M0 = iA[X] & iW[U] & iZ[V]
                h = np.bincount(Y[M0], minlength=n)
                sc = scores(h, T, aLo, aHi); new = aLo + int(np.argmax(sc))
                if new != b: b = new; changed = True
            elif coord == 2:
                M0 = iA[X] & iB[Y] & iZ[V]
                h = np.bincount(U[M0], minlength=LU)
                sc = scores(h, Tp, wLo, wHi); new = wLo + int(np.argmax(sc))
                if new != w: w = new; changed = True
            else:
                M0 = iA[X] & iB[Y] & iW[U]
                h = np.bincount(V[M0], minlength=LU)
                sc = scores(h, Tp, wLo, wHi); new = wLo + int(np.argmax(sc))
                if new != z: z = new; changed = True
            bestval = int(sc.max())
        if verbose: print(f"  it{it} |S|={bestval} shifts={(a,b,w,z)}", flush=True)
        if not changed: break
    return bestval, (a, b, w, z)

def materialise(n, T, Tp, shifts):
    a, b, w, z = shifts
    LU = 2 * n - 1
    iA = ind_from(T, a, n); iB = ind_from(T, b, n)
    iW = ind_from(Tp, w, LU); iZ = ind_from(Tp, z, LU)
    X = np.repeat(np.arange(n, dtype=np.int64), n).reshape(n, n); Y = X.T.copy()
    M = iA[X] & iB[Y] & iW[X + Y] & iZ[X - Y + (n - 1)]
    xs, ys = np.nonzero(M)
    return np.stack([xs, ys], axis=1).astype(np.int64)

if __name__ == '__main__':
    n = int(sys.argv[1]); nseeds = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    t0 = time.time()
    T = best_3apfree(n); Tp = best_3apfree(2 * n - 1, seed0=1000)
    print(f"n={n} |T|={len(T)} |T'|={len(Tp)}  ({time.time()-t0:.1f}s)", flush=True)
    best = (0, None)
    for s in range(nseeds):
        v, sh = run(n, T, Tp, seed=s)
        if v > best[0]: best = (v, sh)
        print(f" seed{s}: |S|={v} shifts={sh} best={best[0]} ({time.time()-t0:.1f}s)", flush=True)
    S = materialise(n, T, Tp, best[1])
    print("BEST", best, "materialised", len(S))
    np.save(f'S_{n}.npy', S); np.save(f'T_{n}.npy', T); np.save(f'Tp_{n}.npy', Tp)
    json.dump({'n': n, 'size': int(len(S)), 'shifts': list(map(int, best[1]))}, open(f'adv_{n}.json', 'w'))
