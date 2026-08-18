"""How strong is the FOUR-direction line-kill relaxation?

Barrier B3 shows B x B (Behrend product) satisfies every ROW+COLUMN line-kill constraint
while having size n^{2-o(1)}.  Question: does adding the two diagonal directions
(e=(1,1) and e=(1,-1)) destroy that, or does a near-quadratic set still survive?

Relaxation studied (strictly weaker than isosceles-free -- it uses only 4 of the ~n^2
primitive directions of L2):

  rows:       p,q in a common row with x-coords of equal parity  ->  column (px+qx)/2 empty
  columns:    p,q in a common column, y-coords equal parity      ->  row    (py+qy)/2 empty
  diagonals:  p,q with x-y equal                                 ->  antidiagonal mean empty
  antidiags:  p,q with x+y equal                                 ->  diagonal     mean empty

(The diagonal families need no parity condition -- see proofs/root_reformulations.md L2b.)

We greedily build maximal feasible sets with many random restarts and report growth.
A large answer extends barrier B3 to four directions.  A small answer means the
non-axis directions carry decisive extra strength.

Exact integer arithmetic only.
"""
import random
import sys


class FourDir:
    """Incremental feasibility structure for the four-direction line-kill relaxation."""

    def __init__(self, n):
        self.n = n
        self.pts = set()
        self.rows = {}   # y -> list of x
        self.cols = {}   # x -> list of y
        self.dia = {}    # x-y -> list of x+y
        self.ant = {}    # x+y -> list of x-y
        self.cnt_col = [0] * n
        self.cnt_row = [0] * n
        self.cnt_dia = [0] * (2 * n - 1)   # index d + (n-1)
        self.cnt_ant = [0] * (2 * n - 1)
        self.kill_col = set()
        self.kill_row = set()
        self.kill_dia = set()
        self.kill_ant = set()

    def can_add(self, x, y):
        n = self.n
        d, a = x - y, x + y
        if x in self.kill_col or y in self.kill_row:
            return None
        if d in self.kill_dia or a in self.kill_ant:
            return None
        new_col, new_row, new_dia, new_ant = set(), set(), set(), set()
        # row pairs -> killed columns
        for qx in self.rows.get(y, ()):
            if (qx + x) % 2 == 0:
                c = (qx + x) // 2
                if self.cnt_col[c] > 0:
                    return None
                new_col.add(c)
        # column pairs -> killed rows
        for qy in self.cols.get(x, ()):
            if (qy + y) % 2 == 0:
                r = (qy + y) // 2
                if self.cnt_row[r] > 0:
                    return None
                new_row.add(r)
        # diagonal pairs -> killed antidiagonals
        for qa in self.dia.get(d, ()):
            t = (qa + a) // 2          # same diagonal => same parity, always integral
            if self.cnt_ant[t] > 0:
                return None
            new_ant.add(t)
        # antidiagonal pairs -> killed diagonals
        for qd in self.ant.get(a, ()):
            t = (qd + d) // 2
            if self.cnt_dia[t + n - 1] > 0:
                return None
            new_dia.add(t)
        # a line we are about to kill must not be the line the new point sits on
        if x in new_col or y in new_row or d in new_dia or a in new_ant:
            return None
        return new_col, new_row, new_dia, new_ant

    def add(self, x, y, killsets):
        d, a = x - y, x + y
        nc, nr, nd, na = killsets
        self.pts.add((x, y))
        self.rows.setdefault(y, []).append(x)
        self.cols.setdefault(x, []).append(y)
        self.dia.setdefault(d, []).append(a)
        self.ant.setdefault(a, []).append(d)
        self.cnt_col[x] += 1
        self.cnt_row[y] += 1
        self.cnt_dia[d + self.n - 1] += 1
        self.cnt_ant[a] += 1
        self.kill_col |= nc
        self.kill_row |= nr
        self.kill_dia |= nd
        self.kill_ant |= na


def verify(n, pts):
    """Independent O(|S|^2) recheck of all four families."""
    P = set(pts)
    occ_col = {p[0] for p in P}
    occ_row = {p[1] for p in P}
    occ_dia = {p[0] - p[1] for p in P}
    occ_ant = {p[0] + p[1] for p in P}
    L = list(P)
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            (x1, y1), (x2, y2) = L[i], L[j]
            if y1 == y2 and (x1 + x2) % 2 == 0 and (x1 + x2) // 2 in occ_col:
                return False
            if x1 == x2 and (y1 + y2) % 2 == 0 and (y1 + y2) // 2 in occ_row:
                return False
            if x1 - y1 == x2 - y2 and ((x1 + y1) + (x2 + y2)) // 2 in occ_ant:
                return False
            if x1 + y1 == x2 + y2 and ((x1 - y1) + (x2 - y2)) // 2 in occ_dia:
                return False
    return True


def greedy(n, rng):
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    st = FourDir(n)
    for (x, y) in cells:
        ks = st.can_add(x, y)
        if ks is not None:
            st.add(x, y, ks)
    return st.pts


def main():
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    print(f"{'n':>5} {'best':>7} {'best/n':>8} {'best/n^2':>10}  log-log slope vs prev")
    prev = None
    for n in (8, 12, 16, 24, 32, 48, 64, 96):
        rng = random.Random(12345 + n)
        best, bestset = 0, None
        for _ in range(seeds):
            s = greedy(n, rng)
            if len(s) > best:
                best, bestset = len(s), s
        assert verify(n, bestset), f"verification FAILED at n={n}"
        slope = ""
        if prev:
            pn, pb = prev
            from math import log
            slope = f"{log(best / pb) / log(n / pn):.3f}"
        print(f"{n:>5} {best:>7} {best / n:>8.3f} {best / n**2:>10.4f}       {slope}")
        prev = (n, best)


if __name__ == "__main__":
    main()
