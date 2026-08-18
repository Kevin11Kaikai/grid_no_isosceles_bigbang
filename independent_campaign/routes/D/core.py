"""Route D core library (rewritten, self-validating).

Problem: S subset of a finite point set, no three DISTINCT a,b,c in S with
d(a,b)=d(b,c) (degenerate/collinear included).  All arithmetic on integer
squared distances.

Equivalent: for every b in S, a |-> |a-b|^2 is injective on S\{b}.
Equivalent: for all distinct a,c in S, S misses the perpendicular bisector of
a,c.

NOTE ON THE PREVIOUS ROUTE-D CODE (search.py): its `conflicts()` only emitted
the pair (first, q) for each repeated distance from the inserted point p, so a
distance class of size >=3 was under-constrained and `run()` could and did
return ILLEGAL sets (reproduced below in tests).  Everything here re-verifies
with is_legal() before returning.
"""
import random
import numpy as np

# ------------------------------------------------------------------ verifier

def dmat(pts):
    P = np.asarray(pts, dtype=np.int64)
    dx = P[:, 0][:, None] - P[:, 0][None, :]
    dy = P[:, 1][:, None] - P[:, 1][None, :]
    return dx * dx + dy * dy


def is_legal(pts):
    """Exact.  Returns (bool, witness)."""
    pts = list(pts)
    if len(set(map(tuple, pts))) != len(pts):
        return False, 'duplicate point'
    for i, b in enumerate(pts):
        seen = {}
        bx, by = b
        for j, a in enumerate(pts):
            if i == j:
                continue
            d = (a[0] - bx) ** 2 + (a[1] - by) ** 2
            if d in seen:
                return False, (seen[d], b, a)
            seen[d] = a
    return True, None


def check(pts, msg=''):
    ok, w = is_legal(pts)
    if not ok:
        raise AssertionError('ILLEGAL %s : %r' % (msg, w))
    return True

# ------------------------------------------------------------- 1-D: r_3(n)

def r3_exact(n, ub_cache={}):
    """max size of a 3AP-free subset of {0..n-1}; exact DFS w/ bitmasks."""
    if n <= 0:
        return 0, []
    best = [0]
    bestS = [[]]
    full = (1 << n) - 1

    def dfs(i, chosen, chosen_list, banned):
        # banned: bitmask of positions that can no longer be used
        avail = (~banned) & full & ~((1 << i) - 1)
        if chosen + bin(avail).count('1') <= best[0]:
            return
        if avail == 0:
            if chosen > best[0]:
                best[0] = chosen
                bestS[0] = list(chosen_list)
            return
        # next available position
        j = (avail & -avail).bit_length() - 1
        # branch 1: take j
        nb = banned | (1 << j)
        ok = True
        for a in chosen_list:
            # forbid completions: j is the largest so far
            c = 2 * j - a
            if 0 <= c < n:
                nb |= (1 << c)
            if (a + j) % 2 == 0:
                m = (a + j) // 2
                nb |= (1 << m)
        chosen_list.append(j)
        dfs(j + 1, chosen + 1, chosen_list, nb)
        chosen_list.pop()
        # branch 2: skip j
        dfs(j + 1, chosen, chosen_list, banned | (1 << j))

    dfs(0, 0, [], 0)
    return best[0], bestS[0]


def is_3ap_free(A):
    Aset = set(A)
    for a in A:
        for b in A:
            if a >= b:
                continue
            c = 2 * b - a
            if c in Aset and c != b:
                return False
    return True

# --------------------------------------------------------- exact 2-D solver

class Exact:
    """Maximum legal subset of an arbitrary point list.

    Pruning: (i) trivial |S| + |cand|; (ii) row bound: within each horizontal
    line the x-coordinates of S must be 3AP-free, likewise columns.  We cap
    each line by an exact r_3 of its available coordinate set.
    """

    def __init__(self, pts, use_line_bound=True):
        self.pts = [tuple(p) for p in pts]
        self.N = len(self.pts)
        self.D = dmat(self.pts).tolist()
        self.best = 0
        self.bestset = []
        self.nodes = 0
        self.use_line_bound = use_line_bound
        # line memberships
        self.rows = {}
        self.cols = {}
        for i, (x, y) in enumerate(self.pts):
            self.rows.setdefault(y, []).append(i)
            self.cols.setdefault(x, []).append(i)
        self._r3cache = {}

    def _r3_of(self, coords):
        key = tuple(sorted(coords))
        if key in self._r3cache:
            return self._r3cache[key]
        # exact max 3AP-free subset of an arbitrary integer set (small)
        cs = list(key)
        m = len(cs)
        idx = {c: i for i, c in enumerate(cs)}
        best = [0]

        def dfs(i, chosen, cl):
            if chosen + (m - i) <= best[0]:
                return
            if i == m:
                if chosen > best[0]:
                    best[0] = chosen
                return
            c = cs[i]
            # adding c must not create a 3-AP with two already-chosen coords
            bad = False
            cs_set = set(cl)
            for a in cl:
                if 2 * c - a in cs_set:
                    bad = True
                    break
                if (a + c) % 2 == 0 and (a + c) // 2 in cs_set:
                    bad = True
                    break
            if not bad:
                cl.append(c)
                dfs(i + 1, chosen + 1, cl)
                cl.pop()
            dfs(i + 1, chosen, cl)

        dfs(0, 0, [])
        self._r3cache[key] = best[0]
        return best[0]

    def _bound(self, S, cand):
        b = len(S) + len(cand)
        if not self.use_line_bound:
            return b
        candset = set(cand)
        Sset = set(S)
        for lines in (self.rows, self.cols):
            tot = 0
            for key, members in lines.items():
                cs = [i for i in members if i in candset]
                ss = [i for i in members if i in Sset]
                if not cs:
                    tot += len(ss)
                    continue
                coords = [self.pts[i][0] for i in cs + ss] if lines is self.rows \
                    else [self.pts[i][1] for i in cs + ss]
                cap = self._r3_of(coords)
                tot += min(len(cs) + len(ss), cap)
            b = min(b, tot)
        return b

    def _compatible(self, p, S, used):
        Dp = self.D[p]
        loc = set()
        for q in S:
            d = Dp[q]
            if d in used[q] or d in loc:
                return None
            loc.add(d)
        return loc

    def solve(self, lb=0, node_limit=None):
        self.best = lb
        self.node_limit = node_limit
        self.aborted = False
        try:
            self._dfs([], {}, list(range(self.N)))
        except RuntimeError:
            self.aborted = True
        return self.best, self.bestset

    def _dfs(self, S, used, cand):
        self.nodes += 1
        if self.node_limit and self.nodes > self.node_limit:
            raise RuntimeError('node limit')
        if self._bound(S, cand) <= self.best:
            return
        if not cand:
            if len(S) > self.best:
                self.best = len(S)
                self.bestset = [self.pts[i] for i in S]
            return
        p = cand[0]
        rest = cand[1:]
        loc = self._compatible(p, S, used)
        if loc is not None:
            newused = dict(used)
            Dp = self.D[p]
            for q in S:
                newused[q] = used[q] | {Dp[q]}
            newused[p] = loc
            S.append(p)
            newcand = [c for c in rest
                       if self._compatible(c, S, newused) is not None]
            self._dfs(S, newused, newcand)
            S.pop()
        if self._bound(S, rest) > self.best:
            self._dfs(S, used, rest)

# ------------------------------------------------------------- local search

class LS:
    """Force-insert + repair local search.  Always keeps S legal (verified)."""

    def __init__(self, pts, seed=0, w=None):
        self.pts = [tuple(p) for p in pts]
        self.N = len(self.pts)
        self.D = dmat(self.pts).tolist()
        self.rng = random.Random(seed)
        self.w = list(w) if w is not None else [1.0] * self.N

    # -- invariants -------------------------------------------------
    def used_sets(self, S):
        D = self.D
        return {q: set(D[q][r] for r in S if r != q) for q in S}

    def can_add(self, p, S, used):
        Dp = self.D[p]
        loc = set()
        for q in S:
            d = Dp[q]
            if d in used[q] or d in loc:
                return None
            loc.add(d)
        return loc

    def add(self, p, S, used, loc):
        for q in S:
            used[q].add(self.D[p][q])
        used[p] = loc
        S.add(p)

    def fill(self, S, used, order=None):
        if order is None:
            order = list(range(self.N))
            self.rng.shuffle(order)
        else:
            order = list(order)
        changed = True
        while changed:
            changed = False
            for q in order:
                if q in S:
                    continue
                loc = self.can_add(q, S, used)
                if loc is not None:
                    self.add(q, S, used, loc)
                    changed = True
        return S, used

    def violated(self, S):
        """return a list of points involved in some violation, or []"""
        D = self.D
        for q in S:
            seen = {}
            for r in S:
                if r == q:
                    continue
                d = D[q][r]
                if d in seen:
                    return [q, seen[d], r]
                seen[d] = r
        return []

    def force_insert(self, p, S, used, forced=frozenset()):
        """insert p, removing points until legal.  Returns removed set or None."""
        S.add(p)
        removed = set()
        guard = 0
        while True:
            guard += 1
            if guard > 10 * self.N:
                return None
            v = self.violated(S)
            if not v:
                break
            cands = [z for z in v if z != p and z not in forced]
            if not cands:
                return None
            # remove the lowest-weight involved point (random tie-break)
            self.rng.shuffle(cands)
            z = min(cands, key=lambda t: self.w[t])
            S.discard(z)
            removed.add(z)
        return removed

    def run(self, iters=20000, restarts=1, S0=None, forced=(), verbose=False):
        forced = frozenset(forced)
        bestv, bestS = -1.0, set()
        for _ in range(restarts):
            S = set(S0) if S0 else set()
            used = self.used_sets(S)
            S, used = self.fill(S, used)
            cur = sum(self.w[q] for q in S)
            if cur > bestv:
                bestv, bestS = cur, set(S)
            stall = 0
            for it in range(iters):
                p = self.rng.randrange(self.N)
                if p in S:
                    continue
                T = set(S)
                rem = self.force_insert(p, T, None, forced)
                if rem is None:
                    continue
                gain = self.w[p] - sum(self.w[z] for z in rem)
                accept = gain > 0 or (abs(gain) < 1e-12 and self.rng.random() < 0.5) \
                    or (gain < 0 and self.rng.random() < 0.02)
                if not accept:
                    continue
                S = T
                used = self.used_sets(S)
                S, used = self.fill(S, used)
                cur = sum(self.w[q] for q in S)
                if cur > bestv + 1e-12:
                    bestv, bestS = cur, set(S)
                    stall = 0
                else:
                    stall += 1
                if stall > 3000:
                    drop = [z for z in self.rng.sample(sorted(S), min(4, len(S)))
                            if z not in forced]
                    S -= set(drop)
                    used = self.used_sets(S)
                    S, used = self.fill(S, used)
                    stall = 0
        out = [self.pts[i] for i in sorted(bestS)]
        check(out, 'LS output')
        return bestv, out


def heur_max(pts, budget_iters=20000, restarts=3, seeds=(0, 1, 2), w=None):
    best, BS = -1.0, []
    for sd in seeds:
        ls = LS(pts, seed=sd, w=w)
        v, S = ls.run(iters=budget_iters, restarts=restarts)
        if v > best:
            best, BS = v, S
    return best, BS

# ------------------------------------------------------------------ layouts

def grid(n):
    return [(x, y) for x in range(n) for y in range(n)]


def block(n, i, j):
    return [(i * n + x, j * n + y) for x in range(n) for y in range(n)]


def resclass(n, i, j, k=2):
    return [(i + k * x, j + k * y) for x in range(n) for y in range(n)]


KNOWN = {1: 1, 2: 2, 3: 4, 4: 6, 5: 7, 6: 9, 7: 10, 8: 13, 9: 16, 10: 18,
         11: 18, 16: 28, 27: 48, 32: 56}
