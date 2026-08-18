"""Frozen Q4 four-direction line-kill checker.

Snapshot copied 2026-08-16 into iso6-joint. Not imported from iso6.
Exact integer arithmetic only.

Constraints on S subset {0,...,n-1}^2:
  1. same row, equal-parity x  ->  midpoint column empty of S
  2. same column, equal-parity y -> midpoint row empty of S
  3. same diagonal x-y         ->  midpoint anti-diagonal x+y empty of S
  4. same anti-diagonal x+y    ->  midpoint diagonal x-y empty of S
"""


class FourDir:
    """Incremental feasibility structure, plus push/pop for search."""

    def __init__(self, n):
        self.n = n
        self.pts = set()
        self.rows = {}
        self.cols = {}
        self.dia = {}
        self.ant = {}
        self.cnt_col = [0] * n
        self.cnt_row = [0] * n
        self.cnt_dia = [0] * (2 * n - 1)
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
        for qx in self.rows.get(y, ()):
            if (qx + x) % 2 == 0:
                c = (qx + x) // 2
                if self.cnt_col[c] > 0:
                    return None
                new_col.add(c)
        for qy in self.cols.get(x, ()):
            if (qy + y) % 2 == 0:
                r = (qy + y) // 2
                if self.cnt_row[r] > 0:
                    return None
                new_row.add(r)
        for qa in self.dia.get(d, ()):
            t = (qa + a) // 2
            if self.cnt_ant[t] > 0:
                return None
            new_ant.add(t)
        for qd in self.ant.get(a, ()):
            t = (qd + d) // 2
            if self.cnt_dia[t + n - 1] > 0:
                return None
            new_dia.add(t)
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

    def push(self, x, y, killsets):
        nc, nr, nd, na = killsets
        rec = (
            (x, y),
            [c for c in nc if c not in self.kill_col],
            [r for r in nr if r not in self.kill_row],
            [t for t in nd if t not in self.kill_dia],
            [t for t in na if t not in self.kill_ant],
        )
        self.add(x, y, killsets)
        return rec

    def pop(self, rec):
        (x, y), new_col, new_row, new_dia, new_ant = rec
        d, a = x - y, x + y
        self.pts.remove((x, y))
        self.rows[y].remove(x)
        if not self.rows[y]:
            del self.rows[y]
        self.cols[x].remove(y)
        if not self.cols[x]:
            del self.cols[x]
        self.dia[d].remove(a)
        if not self.dia[d]:
            del self.dia[d]
        self.ant[a].remove(d)
        if not self.ant[a]:
            del self.ant[a]
        self.cnt_col[x] -= 1
        self.cnt_row[y] -= 1
        self.cnt_dia[d + self.n - 1] -= 1
        self.cnt_ant[a] -= 1
        for c in new_col:
            self.kill_col.remove(c)
        for r in new_row:
            self.kill_row.remove(r)
        for t in new_dia:
            self.kill_dia.remove(t)
        for t in new_ant:
            self.kill_ant.remove(t)


def verify(n, pts):
    """Independent O(|S|^2) recheck of all four families."""
    P = set(pts)
    occ_col = {p[0] for p in P}
    occ_row = {p[1] for p in P}
    occ_dia = {p[0] - p[1] for p in P}
    occ_ant = {p[0] + p[1] for p in P}
    L = list(P)
    for i in range(len(L)):
        x1, y1 = L[i]
        for j in range(i + 1, len(L)):
            x2, y2 = L[j]
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
    for x, y in cells:
        ks = st.can_add(x, y)
        if ks is not None:
            st.add(x, y, ks)
    return st.pts


def greedy_from(n, pts, rng):
    """Maximal Q4-feasible subset of pts, random insertion order."""
    order = list(pts)
    rng.shuffle(order)
    st = FourDir(n)
    for x, y in order:
        ks = st.can_add(x, y)
        if ks is not None:
            st.add(x, y, ks)
    return set(st.pts)
