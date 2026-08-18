"""Directly search for large Q4-feasible sets (the true adversaries of the 4-direction
line-kill relaxation), by incremental randomised greedy.

State per family f in {col, row, ant, dia}:
  key(p)   : which line p lies on   (row y / col x / diag x-y / antidiag x+y)
  val(p)   : the coordinate whose midpoints matter (x / y / x+y / x-y)
  U_f      : set of realised val() over all of S      (must avoid K_f)
  K_f      : union over lines L of same-parity midpoints of val on L
Constraint: U_f cap K_f = empty.
"""
import numpy as np, sys, time
from qlib import q4_violations, iso_triples

FAMS = 4

def keyval(x, y):
    return ((y, x), (x, y), (x - y, x + y), (x + y, x - y))

class Q4State:
    def __init__(self):
        self.lines = [dict() for _ in range(FAMS)]   # key -> list of vals
        self.U = [dict() for _ in range(FAMS)]       # val -> count
        self.K = [dict() for _ in range(FAMS)]       # midpoint -> count
        self.pts = []

    def can_add(self, x, y):
        kv = keyval(x, y)
        for f in range(FAMS):
            k, v = kv[f]
            if v in self.K[f]:
                return False
            vs = self.lines[f].get(k, ())
            for v2 in vs:
                if (v + v2) % 2 == 0:
                    mid = (v + v2) // 2
                    if mid in self.U[f] or mid == v:
                        return False
        return True

    def add(self, x, y):
        kv = keyval(x, y)
        for f in range(FAMS):
            k, v = kv[f]
            vs = self.lines[f].setdefault(k, [])
            for v2 in vs:
                if (v + v2) % 2 == 0:
                    mid = (v + v2) // 2
                    self.K[f][mid] = self.K[f].get(mid, 0) + 1
            vs.append(v)
            self.U[f][v] = self.U[f].get(v, 0) + 1
        self.pts.append((x, y))


def greedy(n, seed, order=None):
    rng = np.random.default_rng(seed)
    if order is None:
        order = rng.permutation(n * n)
    st = Q4State()
    for idx in order:
        x, y = int(idx) // n, int(idx) % n
        if st.can_add(x, y):
            st.add(x, y)
    return np.array(st.pts, dtype=np.int64)


if __name__ == '__main__':
    ns = [int(v) for v in sys.argv[1].split(',')]
    R = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    t0 = time.time()
    for n in ns:
        best = None
        for s in range(R):
            S = greedy(n, s)
            if best is None or len(S) > len(best): best = S
        v = q4_violations(best)
        nq = sum(len(t) for t in v.values())
        tri = iso_triples(best)
        print(f"n={n} |S|={len(best)} q4viol={nq} isoTriples={len(tri)} "
              f"({time.time()-t0:.0f}s)", flush=True)
        np.save(f'q4best_{n}.npy', best)
