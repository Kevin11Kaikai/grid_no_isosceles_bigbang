"""Greedy lower bounds: square-corner-free vs corner-free vs isosceles-free vs Q4-feasible.
Used only to compare growth exponents (EMPIRICAL, heuristic; never a status change)."""
import numpy as np, sys, time

def rot(v):  # 90 degree rotation
    return np.stack([-v[..., 1], v[..., 0]], axis=-1)

class Grid:
    def __init__(self, n):
        self.n = n
        self.g = np.zeros((n, n), dtype=bool)
        self.pts = np.zeros((n * n, 2), dtype=np.int64)
        self.m = 0
    def inside(self, P):
        n = self.n
        return (P[..., 0] >= 0) & (P[..., 0] < n) & (P[..., 1] >= 0) & (P[..., 1] < n)
    def mem(self, P):
        ok = self.inside(P)
        out = np.zeros(P.shape[:-1], dtype=bool)
        if ok.any():
            Q = P[ok]
            out[ok] = self.g[Q[:, 0], Q[:, 1]]
        return out
    def add(self, p):
        self.g[p[0], p[1]] = True
        self.pts[self.m] = p; self.m += 1
    def Q(self):
        return self.pts[:self.m]

def ok_square(G, p):
    Q = G.Q()
    if G.m == 0: return True
    d = Q - p                      # w for apex role
    if G.mem(p + rot(d)).any(): return True and False or False
    return True

def can_add_square(G, p):
    Q = G.Q()
    if G.m == 0: return True
    d = Q - p
    # p as apex: p+w in S (w=d), need p+rot(w) in S
    if G.mem(p + rot(d)).any(): return False
    # p as a leg: b=Q, w = p-b -> other vertex b+rot(w); or p = b+rot(w) -> other b-rot(w)...
    e = p - Q
    if G.mem(Q + rot(e)).any(): return False
    if G.mem(Q - rot(e)).any(): return False
    return True

def can_add_corner(G, p):
    """classical corner-free: no (x,y),(x+d,y),(x,y+d)."""
    Q = G.Q()
    if G.m == 0: return True
    x, y = int(p[0]), int(p[1])
    qx, qy = Q[:, 0], Q[:, 1]
    # p apex: need (x+d,y),(x,y+d) both in S
    same_row = qy == y
    ds = qx[same_row] - x
    if len(ds):
        tgt = np.stack([np.full(len(ds), x), y + ds], 1)
        if G.mem(tgt).any(): return False
    # p = (x+d,y) : apex b=(x-d,y) in S, need (x-d, y+d) in S
    if len(ds):
        b = np.stack([qx[same_row], np.full(len(ds), y)], 1)
        d2 = x - qx[same_row]
        tgt = np.stack([qx[same_row], y + d2], 1)
        if G.mem(tgt).any(): return False
    # p = (x, y+d): apex b=(x, y-d) in S, need (x+d, y-d) in S
    same_col = qx == x
    ds2 = y - qy[same_col]
    if len(ds2):
        tgt = np.stack([x + ds2, qy[same_col]], 1)
        if G.mem(tgt).any(): return False
    return True

def can_add_iso(G, p):
    Q = G.Q()
    if G.m == 0: return True
    d = Q - p
    r2 = d[:, 0] ** 2 + d[:, 1] ** 2
    if len(np.unique(r2)) != len(r2): return False   # p apex
    for i in range(G.m):
        b = Q[i]
        dd = Q - b
        rr = dd[:, 0] ** 2 + dd[:, 1] ** 2
        t = (p[0] - b[0]) ** 2 + (p[1] - b[1]) ** 2
        if (rr == t).any(): return False
    return True

def greedy(n, pred, seed):
    rng = np.random.default_rng(seed)
    G = Grid(n)
    for idx in rng.permutation(n * n):
        p = np.array([int(idx) // n, int(idx) % n], dtype=np.int64)
        if pred(G, p): G.add(p)
    return G.Q()

if __name__ == '__main__':
    ns = [int(v) for v in sys.argv[1].split(',')]
    R = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    which = sys.argv[3] if len(sys.argv) > 3 else 'sq,corner'
    preds = {'sq': can_add_square, 'corner': can_add_corner, 'iso': can_add_iso}
    t0 = time.time()
    for n in ns:
        row = [f"n={n:4d}"]
        for nm in which.split(','):
            best = 0
            for s in range(R):
                best = max(best, len(greedy(n, preds[nm], s)))
            row.append(f"{nm}={best}")
        print("  ".join(row) + f"   ({time.time()-t0:.0f}s)", flush=True)
