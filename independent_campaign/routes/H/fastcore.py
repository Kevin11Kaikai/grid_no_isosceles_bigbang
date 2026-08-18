"""Fast (numpy) machinery for the isosceles-free grid problem.

Everything is exact INTEGER arithmetic: numpy int64 on squared distances.
Grid coords < 2^15 so squared distances < 2^31: int64 is exact.

Independent verifier `verify_np` is cross-checked against core.verify_isofree
and core.verify_isofree_ref (pure-python brute force) in tests().
"""
import numpy as np, random, itertools, json, os, sys
import core

# ------------------------------------------------------------------ verify

def verify_np(pts):
    """Exact numpy verifier. Returns (ok, witness). Independent logic:
    for each apex index j, sort the squared-distance row and look for ties."""
    P = np.asarray(sorted(map(tuple, pts)), dtype=np.int64)
    if P.ndim != 2 or P.shape[1] != 2:
        return False, ("shape", None)
    m = P.shape[0]
    if m == 0:
        return True, None
    # duplicates
    if len(set(map(tuple, P.tolist()))) != m:
        return False, ("duplicate", None)
    dx = P[:, 0][:, None] - P[:, 0][None, :]
    dy = P[:, 1][:, None] - P[:, 1][None, :]
    D = dx * dx + dy * dy                      # exact int64
    for j in range(m):
        row = np.delete(D[j], j)
        s = np.sort(row)
        eq = np.nonzero(s[1:] == s[:-1])[0]
        if eq.size:
            r = int(s[eq[0]])
            idx = [i for i in range(m) if i != j and D[j, i] == r]
            return False, (tuple(P[idx[0]]), tuple(P[j]), tuple(P[idx[1]]), r)
    return True, None


def distmat(P):
    P = np.asarray(P, dtype=np.int64)
    dx = P[:, 0][:, None] - P[:, 0][None, :]
    dy = P[:, 1][:, None] - P[:, 1][None, :]
    return dx * dx + dy * dy


def iso_conflicts(P):
    """Return array of counts: for each point index j, how many 'excess'
    equal-distance pairs it is the apex of (0 == fine)."""
    D = distmat(P)
    m = D.shape[0]
    cnt = np.zeros(m, dtype=np.int64)
    for j in range(m):
        row = np.delete(D[j], j)
        s = np.sort(row)
        # number of pairs with equal value = sum over values C(mult,2)
        # cheap: count adjacent equal runs
        d = np.diff(s)
        cnt[j] = int(np.count_nonzero(d == 0))
    return cnt


def bad_triples(P):
    """All (apex_index, i, k) witnesses of isosceles triples."""
    D = distmat(P)
    m = D.shape[0]
    out = []
    for j in range(m):
        row = D[j].copy()
        row[j] = -1
        order = np.argsort(row, kind='stable')
        s = row[order]
        for t in range(1, m):
            if s[t] == s[t - 1] and s[t] >= 0:
                out.append((j, int(order[t - 1]), int(order[t])))
    return out


# ------------------------------------------------------------------ greedy

class Iso:
    """Incremental isosceles-free set, numpy-accelerated."""
    __slots__ = ("X", "Y", "used", "n", "pts")

    def __init__(self, pts=()):
        self.pts = []
        self.X = np.zeros(0, dtype=np.int64)
        self.Y = np.zeros(0, dtype=np.int64)
        self.used = []
        for p in pts:
            if not self.try_add(p):
                raise ValueError("not isosceles-free at %r" % (p,))

    def dists(self, p):
        return (self.X - p[0]) ** 2 + (self.Y - p[1]) ** 2

    def can_add(self, p):
        m = len(self.pts)
        if m == 0:
            return True
        d = self.dists(p)
        if (d == 0).any():
            return False
        # p as apex: all its distances distinct
        u = np.unique(d)
        if u.size != m:
            return False
        # each existing q as apex
        dl = d.tolist()
        for i in range(m):
            if dl[i] in self.used[i]:
                return False
        return True

    def add(self, p):
        m = len(self.pts)
        d = self.dists(p) if m else np.zeros(0, dtype=np.int64)
        dl = d.tolist()
        for i in range(m):
            self.used[i].add(dl[i])
        self.used.append(set(dl))
        self.pts.append((int(p[0]), int(p[1])))
        self.X = np.append(self.X, np.int64(p[0]))
        self.Y = np.append(self.Y, np.int64(p[1]))

    def try_add(self, p):
        if self.can_add(p):
            self.add(p)
            return True
        return False

    def __len__(self):
        return len(self.pts)


def greedy(cands, order=None, rng=None, start=()):
    """Greedy over candidate list in given order."""
    S = Iso(start)
    idx = list(range(len(cands)))
    if order is not None:
        idx = list(order)
    elif rng is not None:
        rng.shuffle(idx)
    for i in idx:
        S.try_add(cands[i])
    return S.pts


def grid_points(n, m=None):
    m = n if m is None else m
    return [(x, y) for x in range(n) for y in range(m)]


# ------------------------------------------------------------------ random + deletion

def random_plus_deletion(n, m=None, density=None, rng=None, rounds=3):
    """Pick a random subset of density delta, then repeatedly delete the point
    involved in most isosceles triples until none remain; then greedily refill."""
    m = n if m is None else m
    rng = rng or random.Random(0)
    N = n * m
    if density is None:
        density = 1.0 / max(1.0, (n * (2 * np.log(max(n, 3))) ** 0.5))
    k = max(4, int(density * N))
    pts = rng.sample(grid_points(n, m), min(k, N))
    P = np.array(pts, dtype=np.int64)
    while True:
        tri = bad_triples(P)
        if not tri:
            break
        cnt = np.zeros(P.shape[0], dtype=np.int64)
        for (j, a, b) in tri:
            cnt[j] += 1
            cnt[a] += 1
            cnt[b] += 1
        drop = int(np.argmax(cnt))
        P = np.delete(P, drop, axis=0)
    return [tuple(map(int, q)) for q in P]


# ------------------------------------------------------------------ search driver

def search(n, m=None, iters=30, seed=0, time_budget=None, cands=None, start_pool=None,
           verbose=False):
    """Repeated randomized greedy + plunge local search. Returns best point list."""
    import time
    t0 = time.time()
    m = n if m is None else m
    rng = random.Random(seed)
    C = cands if cands is not None else grid_points(n, m)
    best = []
    for it in range(iters):
        if time_budget and time.time() - t0 > time_budget:
            break
        S = Iso()
        order = list(range(len(C)))
        rng.shuffle(order)
        for i in order:
            S.try_add(C[i])
        cur = list(S.pts)
        cur = plunge(cur, C, rng, rounds=40, time_budget=(
            None if not time_budget else max(0.0, time_budget - (time.time() - t0))))
        if len(cur) > len(best):
            best = cur
            if verbose:
                print("  n=%d it=%d size=%d  (%.1fs)" % (n, it, len(best), time.time() - t0),
                      flush=True)
    return best


def plunge(pts, cands, rng, rounds=40, kick=2, time_budget=None):
    """Local search: remove `kick` random points, greedily refill; keep if not worse."""
    import time
    t0 = time.time()
    cur = list(pts)
    best = list(cur)
    for r in range(rounds):
        if time_budget is not None and time.time() - t0 > time_budget:
            break
        if len(cur) <= kick:
            break
        keep = list(cur)
        for _ in range(kick):
            keep.pop(rng.randrange(len(keep)))
        S = Iso(keep)
        order = list(range(len(cands)))
        rng.shuffle(order)
        for i in order:
            S.try_add(cands[i])
        if len(S.pts) >= len(cur):
            cur = list(S.pts)
        if len(cur) > len(best):
            best = list(cur)
    return best


# ------------------------------------------------------------------ tests

def tests():
    rng = random.Random(7)
    for t in range(1500):
        n = rng.randint(2, 8)
        k = rng.randint(2, 8)
        pts = rng.sample(grid_points(n), min(k, n * n))
        a = core.verify_isofree_ref(pts)[0]
        b = core.verify_isofree(pts)[0]
        c = verify_np(pts)[0]
        assert a == b == c, (pts, a, b, c)
    # bad_triples consistency
    for t in range(400):
        n = rng.randint(3, 7)
        pts = rng.sample(grid_points(n), min(rng.randint(3, 9), n * n))
        P = np.array(pts, dtype=np.int64)
        bt = bad_triples(P)
        assert (len(bt) == 0) == verify_np(pts)[0]
    # Iso class consistency
    for t in range(300):
        n = rng.randint(3, 9)
        S = Iso()
        for p in rng.sample(grid_points(n), n * n):
            S.try_add(p)
        assert verify_np(S.pts)[0] and core.verify_isofree_ref(S.pts)[0]
    print("fastcore tests OK")


if __name__ == "__main__":
    tests()
