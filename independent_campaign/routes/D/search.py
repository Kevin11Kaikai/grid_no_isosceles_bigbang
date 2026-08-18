"""Stronger local search for max legal (isosceles-free) subsets.

Move = "force-insert p, repair by removing a minimum-ish vertex cover of the
conflict graph induced on S", plus greedy refill.  Weighted version supports
per-point weights so we can ask e.g. "make the four quadrants balanced".
"""
import random


class LS:
    def __init__(self, pts, seed=0):
        self.pts = list(pts)
        self.N = len(self.pts)
        self.rng = random.Random(seed)
        D = []
        for (xi, yi) in self.pts:
            D.append([(xi-xj)**2 + (yi-yj)**2 for (xj, yj) in self.pts])
        self.D = D

    # ---- feasibility helpers (S is a python set of indices) ----
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

    def conflicts(self, p, S, used):
        """list of pairs {q,r} subset S; removing >=1 of each pair makes p
        addable.  Returns None if p already addable (empty list)."""
        D = self.D
        Dp = D[p]
        cons = []
        seen = {}
        for q in S:
            d = Dp[q]
            if d in seen:
                cons.append((seen[d], q))     # apex p sees q,r at same distance
            else:
                seen[d] = q
        # apex q: distance to p equals distance to some r in S
        for q in S:
            d = Dp[q]
            Dq = D[q]
            for r in S:
                if r != q and Dq[r] == d:
                    cons.append((q, r))
        return cons

    def cover(self, cons):
        """randomized greedy vertex cover of the conflict multigraph."""
        if not cons:
            return set()
        cons = list(cons)
        deg = {}
        for a, b in cons:
            deg[a] = deg.get(a, 0) + 1
            deg[b] = deg.get(b, 0) + 1
        C = set()
        rem = cons
        while rem:
            # pick highest-degree endpoint among remaining, random tie-break
            best, bestd = None, -1
            for a, b in rem:
                for v in (a, b):
                    d = deg.get(v, 0) + self.rng.random()
                    if d > bestd:
                        bestd, best = d, v
            C.add(best)
            new = []
            for a, b in rem:
                if a == best or b == best:
                    deg[a] = deg.get(a, 1) - 1
                    deg[b] = deg.get(b, 1) - 1
                else:
                    new.append((a, b))
            rem = new
        return C

    def fill(self, S, used, order=None):
        if order is None:
            order = list(range(self.N))
            self.rng.shuffle(order)
        for q in order:
            if q in S:
                continue
            loc = self.can_add(q, S, used)
            if loc is not None:
                for r in S:
                    used[r].add(self.D[q][r])
                used[q] = loc
                S.add(q)
        return S, used

    def run(self, iters=30000, w=None, restarts=4, S0=None, forced=()):
        """forced: indices that must always stay in S (never removed)."""
        if w is None:
            w = [1.0]*self.N
        forced = set(forced)
        bestv, bestS = -1, set()
        for _ in range(restarts):
            S = set(S0) if S0 else set()
            used = self.used_sets(S)
            S, used = self.fill(S, used)
            cur = sum(w[p] for p in S)
            if cur > bestv:
                bestv, bestS = cur, set(S)
            stall = 0
            for it in range(iters):
                p = self.rng.randrange(self.N)
                if p in S:
                    continue
                cons = self.conflicts(p, S, used)
                cov = self.cover(cons)
                if cov & forced:
                    continue
                loss = sum(w[q] for q in cov)
                gain = w[p]
                if loss < gain or (loss == gain and self.rng.random() < 0.5) or \
                   (loss <= gain + 1e-9 + (1 if self.rng.random() < 0.02 else 0)):
                    S -= cov
                    S.add(p)
                    used = self.used_sets(S)
                    S, used = self.fill(S, used)
                    cur = sum(w[q] for q in S)
                    if cur > bestv:
                        bestv, bestS = cur, set(S)
                        stall = 0
                    else:
                        stall += 1
                    if stall > 4000:
                        # kick
                        drop = self.rng.sample(sorted(S), min(3, len(S)))
                        S -= set(x for x in drop if x not in forced)
                        used = self.used_sets(S)
                        S, used = self.fill(S, used)
                        stall = 0
        return bestv, sorted(bestS)

    def to_pts(self, idx):
        return [self.pts[i] for i in idx]
