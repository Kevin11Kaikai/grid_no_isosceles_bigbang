"""Isosceles-free (no three distinct a,b,c with d(a,b)=d(b,c)) subsets of grids.

Exact integer arithmetic only (squared distances).
Equivalent formulation used everywhere: for every b in S, the map
    a |-> |a-b|^2   is injective on S \ {b}.
"""
import itertools, random, sys
from functools import lru_cache

# ---------------------------------------------------------------- verifier
def is_iso_free(S):
    """S: iterable of (x,y) int pairs. Exact check."""
    S = list(S)
    for i, b in enumerate(S):
        seen = set()
        bx, by = b
        for j, a in enumerate(S):
            if i == j:
                continue
            d = (a[0] - bx) ** 2 + (a[1] - by) ** 2
            if d in seen:
                return False
            seen.add(d)
    return True


def witness(S):
    """Return an isosceles triple (b apex, p, q) or None."""
    S = list(S)
    for i, b in enumerate(S):
        seen = {}
        for j, a in enumerate(S):
            if i == j:
                continue
            d = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            if d in seen:
                return (b, seen[d], a)
            seen[d] = a
    return None


class State:
    """Incremental isosceles-free set with O(|S|) add/remove."""
    __slots__ = ("pts", "dist")

    def __init__(self):
        self.pts = []          # list of points
        self.dist = []         # dist[i] = set of squared distances from pts[i] to the rest

    def can_add(self, p):
        px, py = p
        new = set()
        for i, b in enumerate(self.pts):
            d = (px - b[0]) ** 2 + (py - b[1]) ** 2
            if d == 0:
                return False
            if d in self.dist[i]:      # apex b: b already uses distance d
                return False
            if d in new:               # apex p: p equidistant from two old points
                return False
            new.add(d)
        return True

    def add(self, p):
        px, py = p
        new = set()
        for i, b in enumerate(self.pts):
            d = (px - b[0]) ** 2 + (py - b[1]) ** 2
            self.dist[i].add(d)
            new.add(d)
        self.pts.append(p)
        self.dist.append(new)

    def pop(self):
        p = self.pts.pop()
        self.dist.pop()
        px, py = p
        for i, b in enumerate(self.pts):
            d = (px - b[0]) ** 2 + (py - b[1]) ** 2
            self.dist[i].discard(d)
        return p

    def copy(self):
        s = State()
        s.pts = list(self.pts)
        s.dist = [set(d) for d in self.dist]
        return s


# ---------------------------------------------------------------- exact solver
def exact(W, H, verbose=False, seed_lb=0, seed_set=None):
    """Max isosceles-free subset of {0..W-1}x{0..H-1}. Branch and bound.
    seed_lb: known lower bound (from heuristic) to prune with; proof is still exact."""
    cells = [(x, y) for x in range(W) for y in range(H)]
    N = len(cells)
    best = [seed_lb]
    best_set = [seed_set]
    st = State()

    def rec(cands):
        if len(st.pts) + len(cands) <= best[0]:
            return
        if not cands:
            if len(st.pts) > best[0]:
                best[0] = len(st.pts)
                best_set[0] = list(st.pts)
            return
        for idx in range(len(cands)):
            if len(st.pts) + len(cands) - idx <= best[0]:
                return
            p = cands[idx]
            if not st.can_add(p):
                continue
            st.add(p)
            if len(st.pts) > best[0]:
                best[0] = len(st.pts)
                best_set[0] = list(st.pts)
                if verbose:
                    print("  best", best[0], flush=True)
            sub = [q for q in cands[idx + 1:] if st.can_add(q)]
            rec(sub)
            st.pop()

    rec(cells)
    return best[0], best_set[0]


# ---------------------------------------------------------------- heuristic
def greedy_random(W, H, rng, order=None):
    cells = [(x, y) for x in range(W) for y in range(H)]
    if order is None:
        rng.shuffle(cells)
    else:
        cells = order
    st = State()
    for p in cells:
        if st.can_add(p):
            st.add(p)
    return st.pts


def local_search(W, H, iters=20000, restarts=8, seed=0, init=None, target=None):
    """Plateau / (k+1)-out k-in style search.  Returns best set found."""
    rng = random.Random(seed)
    cells = [(x, y) for x in range(W) for y in range(H)]
    best = []
    for r in range(restarts):
        cur = list(init) if (init is not None and r == 0) else greedy_random(W, H, rng)
        if len(cur) > len(best):
            best = list(cur)
        for it in range(iters):
            # random removal of 1-2 points then greedy refill in random order
            k = 1 if rng.random() < 0.7 else 2
            cand = list(cur)
            for _ in range(min(k, len(cand))):
                cand.pop(rng.randrange(len(cand)))
            st = State()
            for p in cand:
                st.add(p)
            pool = [c for c in cells if c not in set(cand)]
            rng.shuffle(pool)
            for p in pool:
                if st.can_add(p):
                    st.add(p)
            if len(st.pts) >= len(cur):
                cur = list(st.pts)
            if len(cur) > len(best):
                best = list(cur)
                if target and len(best) >= target:
                    return best
    return best


# ---------------------------------------------------------------- strip analysis
def strip_cells(n):
    """L-shaped strip added when [n]^2 -> [n+1]^2 : new row y=n and new column x=n."""
    return [(x, n) for x in range(n + 1)] + [(n, y) for y in range(n)]


def survivors(S0, n):
    """Cells of the strip individually addable to S0 (a set inside [n]^2)."""
    st = State()
    for p in S0:
        st.add(p)
    return [p for p in strip_cells(n) if st.can_add(p)]


def max_addable(S0, n, tries=400, seed=1):
    """Max number of strip cells jointly addable to S0 (greedy multi-start; exact for small)."""
    surv = survivors(S0, n)
    rng = random.Random(seed)
    base = State()
    for p in S0:
        base.add(p)
    best = 0
    bestset = []
    for t in range(tries):
        order = list(surv)
        rng.shuffle(order)
        st = base.copy()
        got = []
        for p in order:
            if st.can_add(p):
                st.add(p)
                got.append(p)
        if len(got) > best:
            best, bestset = len(got), got
    return best, bestset, len(surv)


if __name__ == "__main__":
    # sanity
    assert is_iso_free([(0, 0), (1, 0)])
    assert not is_iso_free([(0, 0), (1, 0), (2, 0)])
    print("verifier ok")
