"""Averaging supersaturation for the barrier construction.

For the shift-averaged Behrend-intersection construction with directions
e_1=(1,0), e_2=(0,1), e_3=(1,1), e_4=(1,-1), base sets T (for x,y) and T' (for x+y,x-y):

  sum_over_shifts |S|            = n^2 * t^2 * t'^2              (barrier's identity)
  sum_over_shifts #{configs}     = sum_w V(w) * prod_i c_i(phi_i(w), phi_i(w^perp'))

where for a configuration {b, b+p, b+q}:
  c_i(P,Q) = #{tau in T_i : tau+P in T_i, tau+Q in T_i},  P=phi_i(p), Q=phi_i(q)
  V(w)     = number of b in [n]^2 with all three points inside the box.

Ratio rho = (avg #configs)/(avg |S|) says how badly the construction fails the constraint.

Cross-check: for CLASSICAL corners p=(d,0), q=(0,d) the ratio must be exactly 0
(those are killed by Q4).
"""
import numpy as np, sys, time
from build_adv import best_3apfree

def corr2(T, N):
    """c[P+N-1, Q+N-1] = #{tau in T: tau+P in T, tau+Q in T}, T subset [0,N)."""
    L = 2 * N - 1
    ind = np.zeros(N, dtype=np.float32); ind[T] = 1.0
    C = np.zeros((L, L), dtype=np.float32)
    for tau in T:
        d = np.zeros(L, dtype=np.float32)
        lo = -tau; hi = N - tau           # P in [lo, hi)
        d[lo + N - 1: hi + N - 1] = ind[tau + np.arange(lo, hi)]
        C += np.outer(d, d)
    return C

def lookup(C, N, P, Q):
    L = 2 * N - 1
    ok = (np.abs(P) < N) & (np.abs(Q) < N)
    out = np.zeros(P.shape, dtype=np.float64)
    out[ok] = C[(P[ok] + N - 1), (Q[ok] + N - 1)]
    return out

def volume(n, p, q):
    """#b in [0,n)^2 with b, b+p, b+q in [0,n)^2."""
    xs = np.stack([np.zeros_like(p[0]), p[0], q[0]])
    ys = np.stack([np.zeros_like(p[1]), p[1], q[1]])
    wx = xs.max(0) - xs.min(0); wy = ys.max(0) - ys.min(0)
    return np.maximum(0, n - wx).astype(np.float64) * np.maximum(0, n - wy)

def run(n, kind='square', Rw=None):
    t0 = time.time()
    T = best_3apfree(n, restarts=30)
    Tp = best_3apfree(2 * n - 1, restarts=30, seed0=777)
    N1, N2 = n, 2 * n - 1
    C1 = corr2(T, N1); C2 = corr2(Tp, N2)
    t, tp = len(T), len(Tp)
    denom = (n ** 2) * (t ** 2) * (tp ** 2)
    Rw = Rw or (n - 1)
    ws = np.arange(-Rw, Rw + 1)
    W1, W2 = np.meshgrid(ws, ws, indexing='ij')
    W1 = W1.ravel(); W2 = W2.ravel()
    keep = (W1 != 0) | (W2 != 0)
    W1, W2 = W1[keep], W2[keep]
    if kind == 'square':
        p = (W1, W2); q = (-W2, W1)
    elif kind == 'corner':                  # classical corner: p=(d,0), q=(0,d)
        m = W2 == 0
        W1, W2 = W1[m], W2[m]
        p = (W1, np.zeros_like(W1)); q = (np.zeros_like(W1), W1)
    else:
        raise ValueError(kind)
    P1x = p[0]; P2x = q[0]                       # phi_1 = x
    P1y = p[1]; P2y = q[1]                       # phi_2 = y
    P1s = p[0] + p[1]; P2s = q[0] + q[1]         # phi_3 = x+y
    P1d = p[0] - p[1]; P2d = q[0] - q[1]         # phi_4 = x-y
    c1 = lookup(C1, N1, P1x, P2x)
    c2 = lookup(C1, N1, P1y, P2y)
    c3 = lookup(C2, N2, P1s, P2s)
    c4 = lookup(C2, N2, P1d, P2d)
    V = volume(n, p, q)
    tot = float((V * c1 * c2 * c3 * c4).sum())
    rho = tot / denom
    nz = int(((c1 * c2 * c3 * c4) > 0).sum())
    print(f"n={n} kind={kind} |T|={t} |T'|={tp}  sum_s|S|={denom:.4g}  "
          f"sum_s#configs={tot:.6g}  rho={rho:.6g}  w-classes alive={nz}/{len(W1)} "
          f"({time.time()-t0:.0f}s)", flush=True)
    return rho

if __name__ == '__main__':
    for n in [int(v) for v in sys.argv[1].split(',')]:
        run(n, 'corner')
        run(n, 'square')
