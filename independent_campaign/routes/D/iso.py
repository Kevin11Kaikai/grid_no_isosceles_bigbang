"""
Route D: cross-scale / recurrence.  Core library.

Problem: S subset of {0..n-1}^2 (or a general point list), no three distinct
a,b,c in S with d(a,b) = d(b,c).  Equivalently: for every b in S the map
a |-> |a-b|^2 is injective on S\{b}.  All arithmetic on SQUARED distances
(exact integers).

Equivalent reformulation used a lot below:
   S is legal  <=>  for every distinct a,c in S, S contains no point on the
   perpendicular bisector of a and c.
"""
import random, itertools, sys
from functools import lru_cache

# ---------------------------------------------------------------- verifier

def is_legal(pts):
    """Exact integer check. pts: list of (x,y). O(m^2) with hashing."""
    for i, b in enumerate(pts):
        seen = set()
        bx, by = b
        for j, a in enumerate(pts):
            if i == j:
                continue
            d = (a[0]-bx)**2 + (a[1]-by)**2
            if d in seen:
                return False, (b, a)
            seen.add(d)
    return True, None


def violations(pts):
    """Number of apex-points b that have a repeated distance (>=1 collision)."""
    bad = 0
    for i, b in enumerate(pts):
        seen = set()
        bx, by = b
        for j, a in enumerate(pts):
            if i == j:
                continue
            d = (a[0]-bx)**2 + (a[1]-by)**2
            if d in seen:
                bad += 1
                break
            seen.add(d)
    return bad

# ------------------------------------------------------- exact branch&bound

class Exact:
    """Maximum legal subset of an arbitrary finite point set, exact DFS."""

    def __init__(self, pts):
        self.pts = list(pts)
        self.N = len(self.pts)
        self.D = [[0]*self.N for _ in range(self.N)]
        for i in range(self.N):
            xi, yi = self.pts[i]
            for j in range(self.N):
                xj, yj = self.pts[j]
                self.D[i][j] = (xi-xj)**2 + (yi-yj)**2
        self.best = 0
        self.bestset = []
        self.nodes = 0

    def _compatible(self, p, S, used):
        """can p join S? used[q] = set of squared dists already spent at q."""
        Dp = self.D[p]
        loc = set()
        for q in S:
            d = Dp[q]
            if d in used[q]:
                return None
            if d in loc:
                return None
            loc.add(d)
        return loc

    def solve(self, lb=0, time_nodes=None):
        self.best = lb
        used = {}
        self._dfs([], used, list(range(self.N)))
        return self.best, self.bestset

    def _dfs(self, S, used, cand):
        self.nodes += 1
        if len(S) + len(cand) <= self.best:
            return
        if not cand:
            if len(S) > self.best:
                self.best = len(S)
                self.bestset = [self.pts[i] for i in S]
            return
        p = cand[0]
        rest = cand[1:]
        # branch: include p
        loc = self._compatible(p, S, used)
        if loc is not None:
            newused = dict(used)
            Dp = self.D[p]
            for q in S:
                newused[q] = used[q] | {Dp[q]}
            newused[p] = loc
            S.append(p)
            newcand = [c for c in rest if self._compatible(c, S, newused) is not None]
            self._dfs(S, newused, newcand)
            S.pop()
        # branch: exclude p
        if len(S) + len(rest) > self.best:
            self._dfs(S, used, rest)


def C_exact(n):
    pts = [(x, y) for x in range(n) for y in range(n)]
    e = Exact(pts)
    v, s = e.solve()
    return v, s, e.nodes


def C_exact_rect(m, n):
    pts = [(x, y) for x in range(m) for y in range(n)]
    e = Exact(pts)
    v, s = e.solve()
    return v, s, e.nodes

# ------------------------------------------------------------ local search

class Heur:
    """Randomized construct + plateau/kick local search on an arbitrary
    ground set of points.  Optional per-region quota objective."""

    def __init__(self, pts, seed=0):
        self.pts = list(pts)
        self.N = len(self.pts)
        self.rng = random.Random(seed)
        self.D = []
        for i in range(self.N):
            xi, yi = self.pts[i]
            self.D.append([(xi-xj)**2 + (yi-yj)**2 for (xj, yj) in self.pts])

    def feasible_add(self, p, S, used):
        Dp = self.D[p]
        loc = set()
        for q in S:
            d = Dp[q]
            if d in used[q] or d in loc:
                return None
            loc.add(d)
        return loc

    def blockers(self, p, S, used):
        """points of S that must be removed for p to be addable (approx: any q
        causing a clash)."""
        Dp = self.D[p]
        loc = {}
        bad = set()
        for q in S:
            d = Dp[q]
            if d in used[q]:
                bad.add(q)
                # also the partner in q's distance set
                for r in S:
                    if r != q and self.D[q][r] == d:
                        bad.add(r)
            if d in loc:
                bad.add(q); bad.add(loc[d])
            else:
                loc[d] = q
        return bad

    def rebuild_used(self, S):
        used = {}
        for q in S:
            used[q] = set(self.D[q][r] for r in S if r != q)
        return used

    def greedy(self, order=None, weight=None):
        if order is None:
            order = list(range(self.N))
            self.rng.shuffle(order)
        S = []
        used = {}
        for p in order:
            loc = self.feasible_add(p, S, used)
            if loc is not None:
                for q in S:
                    used[q].add(self.D[p][q])
                used[p] = loc
                S.append(p)
        return S

    def run(self, iters=20000, weight=None, restarts=1):
        """weight: optional list of per-point weights (maximize total weight)."""
        w = weight if weight is not None else [1]*self.N
        bestS, bestv = [], -1
        for _ in range(restarts):
            S = self.greedy()
            used = self.rebuild_used(S)
            cur = sum(w[p] for p in S)
            if cur > bestv:
                bestv, bestS = cur, list(S)
            for it in range(iters):
                p = self.rng.randrange(self.N)
                if p in used:
                    continue
                bad = self.blockers(p, S, used)
                if len(bad) == 0:
                    S.append(p)
                elif sum(w[q] for q in bad) < w[p] or (
                        sum(w[q] for q in bad) == w[p] and self.rng.random() < 0.35):
                    for q in bad:
                        S.remove(q)
                    S.append(p)
                else:
                    continue
                used = self.rebuild_used(S)
                # opportunistic fill
                order = list(range(self.N)); self.rng.shuffle(order)
                for q in order:
                    if q in used:
                        continue
                    loc = self.feasible_add(q, S, used)
                    if loc is not None:
                        for r in S:
                            used[r].add(self.D[q][r])
                        used[q] = loc
                        S.append(q)
                cur = sum(w[p2] for p2 in S)
                if cur > bestv:
                    bestv = cur
                    bestS = list(S)
        return bestv, [self.pts[i] for i in bestS]


def C_heur(n, iters=20000, restarts=3, seed=1):
    pts = [(x, y) for x in range(n) for y in range(n)]
    h = Heur(pts, seed)
    v, s = h.run(iters=iters, restarts=restarts)
    ok, _ = is_legal(s)
    assert ok
    return v, s


def C_heur_rect(m, n, iters=20000, restarts=3, seed=1):
    pts = [(x, y) for x in range(m) for y in range(n)]
    h = Heur(pts, seed)
    v, s = h.run(iters=iters, restarts=restarts)
    ok, _ = is_legal(s)
    assert ok
    return v, s
