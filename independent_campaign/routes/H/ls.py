"""Plateau / ejection local search for maximum isosceles-free sets.

Move: pick p not in S. Compute the set of "bad pairs" created by adding p
(each bad pair is a pair of existing points, at least one of which must go).
 - 0 bad pairs  -> add p                       (size +1)
 - all pairs share a common point r -> swap    (size +0, plateau)
 - occasionally accept a 2-removal              (perturbation)

Everything exact integer arithmetic.
"""
import numpy as np, random, json, os, time
import core, fastcore


class IsoLS:
    """Isosceles-free set supporting add / remove / conflict analysis.
    used[i] : dict  squared-distance -> the point (tuple) at that distance from pts[i].
    """
    __slots__ = ("pts", "X", "Y", "used", "pos")

    def __init__(self, pts=()):
        self.pts = []
        self.X = np.zeros(0, dtype=np.int64)
        self.Y = np.zeros(0, dtype=np.int64)
        self.used = []
        self.pos = {}
        for p in pts:
            ok, r = self.analyse(p)
            assert ok and not r, "seed set not isosceles-free at %r" % (p,)
            self.add(p)

    def __len__(self):
        return len(self.pts)

    def _d(self, p):
        return (self.X - p[0]) ** 2 + (self.Y - p[1]) ** 2

    def analyse(self, p):
        """Return (valid_point, bad_pairs).  bad_pairs is a list of frozensets of
        1 or 2 existing points; adding p is legal iff we delete a hitting set."""
        p = (int(p[0]), int(p[1]))
        if p in self.pos:
            return False, None
        m = len(self.pts)
        if m == 0:
            return True, []
        d = self._d(p)
        dl = d.tolist()
        pairs = []
        # type A: p itself is the apex.  A group of k>=2 points equidistant from p
        # must be cut down to <=1 survivor, i.e. ALL C(k,2) pairs are bad pairs.
        groups = {}
        for i, v in enumerate(dl):
            if v == 0:
                return False, None
            groups.setdefault(v, []).append(i)
        for v, g in groups.items():
            if len(g) > 1:
                for a in range(len(g)):
                    for b in range(a + 1, len(g)):
                        pairs.append((self.pts[g[a]], self.pts[g[b]]))
        # type B: an existing point is the apex
        for i, v in enumerate(dl):
            w = self.used[i].get(v)
            if w is not None:
                pairs.append((self.pts[i], w))
        return True, pairs

    def add(self, p):
        p = (int(p[0]), int(p[1]))
        m = len(self.pts)
        if m:
            dl = self._d(p).tolist()
            for i, v in enumerate(dl):
                self.used[i][v] = p
            self.used.append({v: self.pts[i] for i, v in enumerate(dl)})
        else:
            self.used.append({})
        self.pts.append(p)
        self.pos[p] = len(self.pts) - 1
        self.X = np.append(self.X, np.int64(p[0]))
        self.Y = np.append(self.Y, np.int64(p[1]))

    def remove(self, p):
        p = (int(p[0]), int(p[1]))
        j = self.pos.pop(p)
        last = self.pts[-1]
        # remove distance entries pointing at p
        dl = self._d(p).tolist()
        for i, v in enumerate(dl):
            if i != j:
                self.used[i].pop(v, None)
        # swap-delete slot j
        self.pts[j] = last
        self.used[j] = self.used[-1]
        self.X[j] = self.X[-1]
        self.Y[j] = self.Y[-1]
        if last != p:
            self.pos[last] = j
        self.pts.pop()
        self.used.pop()
        self.X = self.X[:-1]
        self.Y = self.Y[:-1]

    def try_add(self, p):
        ok, pairs = self.analyse(p)
        if ok and not pairs:
            self.add(p)
            return True
        return False

    def copy(self):
        o = IsoLS.__new__(IsoLS)
        o.pts = list(self.pts)
        o.X = self.X.copy()
        o.Y = self.Y.copy()
        o.used = [dict(u) for u in self.used]
        o.pos = dict(self.pos)
        return o


def _hitters(pairs):
    """Points that hit every pair (i.e. single-removal fixes)."""
    if not pairs:
        return []
    s = set(pairs[0])
    for q in pairs[1:]:
        s &= set(q)
        if not s:
            return []
    return list(s)


def local_search(cands, seed_pts=(), rng=None, max_steps=10**9, time_budget=20.0,
                 p2=0.02, verbose=False, report=None):
    """Iterated plateau search.  cands = list of candidate points."""
    rng = rng or random.Random(0)
    S = IsoLS()
    order = list(range(len(cands)))
    rng.shuffle(order)
    for p in seed_pts:
        S.try_add(p)
    for i in order:
        S.try_add(cands[i])
    best = list(S.pts)
    t0 = time.time()
    ncand = len(cands)
    step = 0
    since = 0
    while step < max_steps and time.time() - t0 < time_budget:
        step += 1
        p = cands[rng.randrange(ncand)]
        ok, pairs = S.analyse(p)
        if not ok:
            continue
        if not pairs:
            S.add(p)
        else:
            h = _hitters(pairs)
            if h:
                S.remove(h[rng.randrange(len(h))])
                S.add(p)
            elif rng.random() < p2:
                # 2-removal perturbation: greedy hitting set of size 2 if possible
                a, b = pairs[0]
                rest = [q for q in pairs if a not in q and b not in q]
                h2 = _hitters(rest) if rest else [a]
                cand2 = None
                for x in (a, b):
                    rest = [q for q in pairs if x not in q]
                    hh = _hitters(rest) if rest else []
                    if hh:
                        cand2 = (x, hh[rng.randrange(len(hh))])
                        break
                    if not rest:
                        cand2 = (x, None)
                        break
                if cand2:
                    S.remove(cand2[0])
                    if cand2[1] is not None:
                        S.remove(cand2[1])
                    S.add(p)
        if len(S) > len(best):
            best = list(S.pts)
            since = 0
            if verbose:
                print("   size=%d step=%d t=%.1f" % (len(best), step, time.time() - t0), flush=True)
        else:
            since += 1
        if since > 25000:
            # restart from best with a kick
            S = IsoLS(best)
            for _ in range(max(2, len(best) // 20)):
                if len(S):
                    S.remove(S.pts[rng.randrange(len(S))])
            for i in rng.sample(range(ncand), min(ncand, 4000)):
                S.try_add(cands[i])
            since = 0
    if report is not None:
        report['steps'] = step
        report['time'] = time.time() - t0
    return best


def best_in_box(n, m=None, time_budget=20.0, seed=0, restarts=1, verbose=False):
    m = n if m is None else m
    C = [(x, y) for x in range(n) for y in range(m)]
    best = []
    for r in range(restarts):
        rng = random.Random(seed * 1000 + r)
        b = local_search(C, rng=rng, time_budget=time_budget / restarts, verbose=verbose)
        if len(b) > len(best):
            best = b
    return best


if __name__ == "__main__":
    rng = random.Random(0)
    # cross-validate IsoLS against brute force
    for t in range(400):
        n = rng.randint(3, 8)
        C = [(x, y) for x in range(n) for y in range(n)]
        S = IsoLS()
        for p in rng.sample(C, n * n):
            ok, pairs = S.analyse(p)
            if ok and not pairs:
                S.add(p)
        assert core.verify_isofree_ref(S.pts)[0], S.pts
        # random removals keep consistency
        for _ in range(3):
            if len(S) > 1:
                S.remove(S.pts[rng.randrange(len(S))])
        assert core.verify_isofree_ref(S.pts)[0]
        # analyse must agree with recomputation from scratch
        for _ in range(5):
            p = C[rng.randrange(len(C))]
            ok, pairs = S.analyse(p)
            if ok:
                brute_ok = core.verify_isofree_ref(list(S.pts) + [p])[0]
                assert brute_ok == (not pairs), (S.pts, p, pairs)
                # every hitting set of `pairs` must really repair the addition
                h = _hitters(pairs)
                for r in h:
                    q = [x for x in S.pts if x != r] + [p]
                    assert core.verify_isofree_ref(q)[0], (S.pts, p, r, pairs)
    # exhaustive stress of the incremental state machine vs. brute force
    for t in range(300):
        n = rng.randint(3, 7)
        C = [(x, y) for x in range(n) for y in range(n)]
        S = IsoLS()
        for _ in range(60):
            if rng.random() < 0.65 or len(S) == 0:
                p = C[rng.randrange(len(C))]
                ok, pairs = S.analyse(p)
                if ok and not pairs:
                    S.add(p)
                elif ok:
                    h = _hitters(pairs)
                    if h:
                        S.remove(h[0]); S.add(p)
            else:
                S.remove(S.pts[rng.randrange(len(S))])
            assert core.verify_isofree_ref(S.pts)[0], S.pts
            # incremental `used` tables must match a from-scratch rebuild
            for i, a in enumerate(S.pts):
                exp = {}
                for b in S.pts:
                    if b != a:
                        exp[(a[0]-b[0])**2 + (a[1]-b[1])**2] = b
                assert S.used[i] == exp, (S.pts, a, S.used[i], exp)
    print("ls tests OK")
