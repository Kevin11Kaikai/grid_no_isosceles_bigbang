"""Fixed-size simulated annealing / tabu search for maximum isosceles-free sets.

Penalty formulation.  Hold |S| = K fixed and minimise

    cost(S) = sum_{b in S} sum_{r} C( c_{b,r}, 2 ),   c_{b,r} = #{a in S\\{b} : |a-b|^2 = r}

cost(S) == 0  <=>  S is isosceles-free.  Move = swap one point out / one in.
When cost 0 is reached we bump K and continue.  All arithmetic is exact
integer arithmetic on squared distances.

`Conf.cost` is validated against a from-scratch recomputation in tests().
"""
import numpy as np, random, math, time, json, os
import core, fastcore


class Conf:
    """Multiset-free point configuration with incremental isosceles-conflict cost."""
    __slots__ = ("pts", "X", "Y", "cnt", "cost", "pos")

    def __init__(self, pts=()):
        self.pts = []
        self.X = np.zeros(0, dtype=np.int64)
        self.Y = np.zeros(0, dtype=np.int64)
        self.cnt = []          # cnt[i] : dict  r -> #points at squared distance r from pts[i]
        self.cost = 0
        self.pos = {}
        for p in pts:
            self.add(p)

    def __len__(self):
        return len(self.pts)

    def _d(self, p):
        return ((self.X - p[0]) ** 2 + (self.Y - p[1]) ** 2).tolist()

    def add_cost(self, p):
        """Cost increase from adding p (p must not already be present)."""
        dl = self._d(p)
        c = 0
        own = {}
        for i, v in enumerate(dl):
            c += self.cnt[i].get(v, 0)
            k = own.get(v, 0)
            c += k
            own[v] = k + 1
        return c

    def add(self, p):
        p = (int(p[0]), int(p[1]))
        dl = self._d(p)
        own = {}
        for i, v in enumerate(dl):
            k = self.cnt[i].get(v, 0)
            self.cost += k
            self.cnt[i][v] = k + 1
            k2 = own.get(v, 0)
            self.cost += k2
            own[v] = k2 + 1
        self.cnt.append(own)
        self.pts.append(p)
        self.pos[p] = len(self.pts) - 1
        self.X = np.append(self.X, np.int64(p[0]))
        self.Y = np.append(self.Y, np.int64(p[1]))

    def remove(self, p):
        p = (int(p[0]), int(p[1]))
        j = self.pos.pop(p)
        dl = self._d(p)
        for i, v in enumerate(dl):
            if i == j:
                continue
            k = self.cnt[i][v] - 1
            self.cost -= k
            if k:
                self.cnt[i][v] = k
            else:
                del self.cnt[i][v]
        for v, k in self.cnt[j].items():
            self.cost -= k * (k - 1) // 2
        last = self.pts[-1]
        self.pts[j] = last
        self.cnt[j] = self.cnt[-1]
        self.X[j] = self.X[-1]
        self.Y[j] = self.Y[-1]
        if last != p:
            self.pos[last] = j
        self.pts.pop()
        self.cnt.pop()
        self.X = self.X[:-1]
        self.Y = self.Y[:-1]

    def brute_cost(self):
        P = np.array(self.pts, dtype=np.int64)
        m = len(self.pts)
        if m < 2:
            return 0
        D = fastcore.distmat(P)
        tot = 0
        for j in range(m):
            row = np.delete(D[j], j)
            _, mult = np.unique(row, return_counts=True)
            tot += int((mult * (mult - 1) // 2).sum())
        return tot


def anneal(cands, K0=None, seed=0, time_budget=30.0, T0=0.9, T1=0.03, start=None,
           forced=(), verbose=False):
    """Anneal at fixed size, bumping K on every success.  Returns best valid set."""
    rng = random.Random(seed)
    ncand = len(cands)
    forced = [tuple(map(int, q)) for q in forced]
    nf = len(forced)
    best = list(forced)
    if start:
        S = Conf(start)
    else:
        S = Conf(forced)
        pool = [c for c in cands if tuple(c) not in S.pos]
        rng.shuffle(pool)
        for p in pool:
            if S.add_cost(p) == 0:
                S.add(p)
    if S.cost == 0 and len(S) > len(best):
        best = list(S.pts)
    K = len(S) + 1
    # add one more point to reach K
    S.add(cands[rng.randrange(ncand)] if True else None) if False else None
    t0 = time.time()
    steps = 0
    while time.time() - t0 < time_budget:
        # grow to K
        while len(S) < K:
            p = cands[rng.randrange(ncand)]
            if tuple(p) not in S.pos:
                S.add(p)
        # anneal at this K
        inner = 0
        stall = 0
        limit = 20000 + 400 * K
        while S.cost > 0 and time.time() - t0 < time_budget and stall < limit:
            inner += 1
            steps += 1
            frac = min(1.0, inner / float(limit))
            T = T0 * (T1 / T0) ** frac
            # choose a point to eject: prefer one in conflict
            j = rng.randrange(len(S.pts))
            pout = S.pts[j]
            if pout in forced:
                continue
            pin = cands[rng.randrange(ncand)]
            if tuple(pin) in S.pos:
                continue
            old = S.cost
            S.remove(pout)
            dc = S.add_cost(pin)
            new = S.cost + dc
            if new <= old or rng.random() < math.exp(-(new - old) / max(T, 1e-9)):
                S.add(pin)
                if new >= old:
                    stall += 1
                else:
                    stall = 0
            else:
                S.add(pout)
                stall += 1
        if S.cost == 0:
            if len(S) > len(best):
                best = list(S.pts)
                if verbose:
                    print("    K=%d  t=%.1f" % (len(best), time.time() - t0), flush=True)
            K = len(S) + 1
        else:
            # failed at this K: drop back, keep going with a fresh perturbation
            for _ in range(max(1, K // 8)):
                if len(S) > nf:
                    q = S.pts[rng.randrange(len(S.pts))]
                    if q not in forced:
                        S.remove(q)
            if S.cost > 0:
                # ensure we restart from a valid-ish config
                while S.cost > 0 and len(S) > nf:
                    # remove the worst offender
                    bad = None
                    for i, d in enumerate(S.cnt):
                        if any(v > 1 for v in d.values()):
                            bad = S.pts[i]
                            break
                    if bad is None or bad in forced:
                        break
                    S.remove(bad)
            K = max(len(S) + 1, len(best) + 1)
    return best, steps


def best_in_box(n, m=None, time_budget=30.0, seed=0, verbose=False, forced=()):
    m = n if m is None else m
    C = [(x, y) for x in range(n) for y in range(m)]
    b, steps = anneal(C, seed=seed, time_budget=time_budget, verbose=verbose, forced=forced)
    return b


def tests():
    rng = random.Random(3)
    for t in range(400):
        n = rng.randint(3, 9)
        C = [(x, y) for x in range(n) for y in range(n)]
        S = Conf()
        for _ in range(40):
            if len(S) == 0 or rng.random() < 0.65:
                p = C[rng.randrange(len(C))]
                if tuple(p) in S.pos:
                    continue
                pred = S.cost + S.add_cost(p)
                S.add(p)
                assert S.cost == pred, ("add_cost mismatch", S.pts, p, S.cost, pred)
            else:
                S.remove(S.pts[rng.randrange(len(S.pts))])
            assert S.cost == S.brute_cost(), (S.pts, S.cost, S.brute_cost())
            assert (S.cost == 0) == core.verify_isofree_ref(S.pts)[0]
    print("anneal tests OK")


if __name__ == "__main__":
    tests()
