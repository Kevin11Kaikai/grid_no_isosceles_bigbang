"""Core exact tooling for the isosceles-free grid problem.

C(n) = max |S|, S subset of {0,...,n-1}^2 such that there are NO three distinct
points a,b,c in S with |a-b| = |b-c|  (b is the apex; degenerate/collinear
triples are forbidden too).

Equivalently: for every b in S, the squared distances from b to the other
points of S are pairwise DISTINCT.

ALL arithmetic is exact integer arithmetic on squared distances.
"""
import itertools, random, json, os, sys

# ---------------------------------------------------------------- verifiers

def verify_isofree_ref(pts):
    """Reference verifier #1: brute force over ordered triples, pure python ints.
    Returns (ok, witness)."""
    pts = list(map(tuple, pts))
    assert len(set(pts)) == len(pts), "duplicate points"
    m = len(pts)
    for j in range(m):
        bx, by = pts[j]
        for i in range(m):
            if i == j: continue
            for k in range(i+1, m):
                if k == j: continue
                ax, ay = pts[i]; cx, cy = pts[k]
                d1 = (ax-bx)*(ax-bx) + (ay-by)*(ay-by)
                d2 = (cx-bx)*(cx-bx) + (cy-by)*(cy-by)
                if d1 == d2:
                    return False, (pts[i], pts[j], pts[k], d1)
    return True, None

def verify_isofree(pts):
    """Verifier #2 (independent logic): for each apex b, collect the multiset of
    squared distances to all other points and require no repeats."""
    pts = list(map(tuple, pts))
    if len(set(pts)) != len(pts):
        return False, ("duplicate", None)
    for b in pts:
        seen = {}
        bx, by = b
        for a in pts:
            if a == b: continue
            d = (a[0]-bx)**2 + (a[1]-by)**2
            if d in seen:
                return False, (seen[d], b, a, d)
            seen[d] = a
    return True, None

def in_box(pts, n, m=None):
    m = n if m is None else m
    return all(0 <= x < n and 0 <= y < m for (x, y) in pts)

# ---------------------------------------------------------------- incremental structure

class IsoSet:
    """Incremental isosceles-free set with O(|S|) add/test."""
    __slots__ = ("pts", "used")
    def __init__(self):
        self.pts = []          # list of (x,y)
        self.used = []         # used[i] = set of squared distances from pts[i]

    def can_add(self, p):
        px, py = p
        newd = set()
        for i, (qx, qy) in enumerate(self.pts):
            d = (px-qx)**2 + (py-qy)**2
            if d == 0: return False
            if d in newd: return False        # p itself would be an apex
            if d in self.used[i]: return False # q would be an apex
            newd.add(d)
        return True

    def add(self, p):
        px, py = p
        newd = set()
        for i, (qx, qy) in enumerate(self.pts):
            d = (px-qx)**2 + (py-qy)**2
            newd.add(d)
            self.used[i].add(d)
        self.pts.append(tuple(p))
        self.used.append(newd)

    def try_add(self, p):
        if self.can_add(p):
            self.add(p); return True
        return False

    def remove(self, p):
        p = tuple(p)
        j = self.pts.index(p)
        px, py = p
        self.pts.pop(j); self.used.pop(j)
        for i, (qx, qy) in enumerate(self.pts):
            self.used[i].discard((px-qx)**2 + (py-qy)**2)

    def copy(self):
        o = IsoSet()
        o.pts = list(self.pts)
        o.used = [set(s) for s in self.used]
        return o

    def __len__(self): return len(self.pts)

# ---------------------------------------------------------------- io

SETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sets")

def save_set(name, pts, n, m=None, status="VERIFIED_COMPUTATIONAL_RESULT", note=""):
    os.makedirs(SETS_DIR, exist_ok=True)
    pts = sorted(map(tuple, pts))
    ok1, w1 = verify_isofree(pts)
    ok2, w2 = (verify_isofree_ref(pts) if len(pts) <= 260 else (ok1, w1))
    rec = dict(name=name, n=n, m=(n if m is None else m), size=len(pts),
               isosceles_free=bool(ok1 and ok2), in_box=in_box(pts, n, m),
               status=status, note=note, points=pts)
    with open(os.path.join(SETS_DIR, name + ".json"), "w") as f:
        json.dump(rec, f)
    return rec
