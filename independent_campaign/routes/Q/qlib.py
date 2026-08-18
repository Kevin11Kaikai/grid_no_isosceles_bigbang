"""Route Q core library: adversary construction + independent verifiers.

Exact integer arithmetic only (squared distances). No floats in any predicate.
"""
import numpy as np
from math import gcd

# ---------------------------------------------------------------- 3-AP-free sets

def greedy_3ap_free(N, seed=0, order=None):
    """Return a 3-AP-free subset of [0,N) (no x<y<z with x+z=2y).
    Randomised greedy in a random order; deterministic if seed is None -> base-3."""
    if order is None:
        rng = np.random.default_rng(seed)
        order = rng.permutation(N)
    chosen = []
    inset = np.zeros(N, dtype=bool)
    for v in order:
        v = int(v)
        ok = True
        for u in chosen:
            # midpoint of u,v must not be in set; and v must not be midpoint of u,w
            if (u + v) % 2 == 0 and inset[(u + v) // 2]:
                ok = False
                break
            w = 2 * v - u
            if 0 <= w < N and inset[w]:
                ok = False
                break
            w2 = 2 * u - v
            if 0 <= w2 < N and inset[w2]:
                ok = False
                break
        if ok:
            chosen.append(v)
            inset[v] = True
    return np.array(sorted(chosen), dtype=np.int64)


def base3_set(N):
    """Digit-2-avoiding base-3 set intersected with [0,N): 3-AP-free (Szekeres)."""
    out = []
    for v in range(N):
        t = v
        ok = True
        while t:
            if t % 3 == 2:
                ok = False
                break
            t //= 3
        if ok:
            out.append(v)
    return np.array(out, dtype=np.int64)


def is_3ap_free(arr):
    """Independent check: no distinct x,z in arr with (x+z)/2 in arr."""
    s = set(int(v) for v in arr)
    a = sorted(s)
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            x, z = a[i], a[j]
            if (x + z) % 2 == 0 and (x + z) // 2 in s:
                return False, (x, (x + z) // 2, z)
    return True, None


# ---------------------------------------------------------------- indicator helpers

class Ind:
    """Indicator of a shifted set over an integer window [lo,hi)."""
    def __init__(self, base, shift, lo, hi):
        self.lo, self.hi = lo, hi
        self.arr = np.zeros(hi - lo, dtype=bool)
        v = base + shift
        v = v[(v >= lo) & (v < hi)]
        self.arr[v - lo] = True
        self.vals = np.sort(v)

    def __call__(self, x):
        x = np.asarray(x)
        out = np.zeros(x.shape, dtype=bool)
        m = (x >= self.lo) & (x < self.hi)
        out[m] = self.arr[x[m] - self.lo]
        return out


def build_S(n, A, B, W, Z):
    """S = {(x,y) in [n]^2 : x in A, y in B, x+y in W, x-y in Z}.
    A,B: arrays of ints (used as sets); W,Z: arrays of ints."""
    As, Bs = set(map(int, A)), set(map(int, B))
    Ws, Zs = set(map(int, W)), set(map(int, Z))
    pts = []
    for x in sorted(As):
        if not (0 <= x < n):
            continue
        for y in sorted(Bs):
            if not (0 <= y < n):
                continue
            if (x + y) in Ws and (x - y) in Zs:
                pts.append((x, y))
    return np.array(pts, dtype=np.int64).reshape(-1, 2)


# ---------------------------------------------------------------- Q4 verifier (independent)

def midpoints(vals):
    """Same-parity midpoints of distinct pairs."""
    v = np.asarray(sorted(set(int(t) for t in vals)), dtype=np.int64)
    out = set()
    for i in range(len(v)):
        for j in range(i + 1, len(v)):
            if (v[i] + v[j]) % 2 == 0:
                out.add(int((v[i] + v[j]) // 2))
    return out


def q4_violations(S):
    """Return dict of violation lists for the four line-kill constraints.
    (1) M(X_y) cap U_col   (2) M(Y_x) cap U_row
    (3) M(A_d) cap U_ant   (4) M(D_a) cap U_dia
    where X_y = x-coords in row y, Y_x = y-coords in col x,
    A_d = (x+y)-values on diagonal d = x-y, D_a = (x-y)-values on antidiag a = x+y.
    """
    x, y = S[:, 0], S[:, 1]
    U_col = set(map(int, np.unique(x)))
    U_row = set(map(int, np.unique(y)))
    U_ant = set(map(int, np.unique(x + y)))
    U_dia = set(map(int, np.unique(x - y)))
    res = {1: [], 2: [], 3: [], 4: []}
    # (1) rows
    for yy in sorted(U_row):
        Xy = x[y == yy]
        for m in midpoints(Xy):
            if m in U_col:
                res[1].append((yy, m))
    # (2) cols
    for xx in sorted(U_col):
        Yx = y[x == xx]
        for m in midpoints(Yx):
            if m in U_row:
                res[2].append((xx, m))
    # (3) diagonals d = x-y ; values x+y
    for dd in sorted(U_dia):
        Ad = (x + y)[(x - y) == dd]
        for m in midpoints(Ad):
            if m in U_ant:
                res[3].append((dd, m))
    # (4) antidiagonals a = x+y ; values x-y
    for aa in sorted(U_ant):
        Da = (x - y)[(x + y) == aa]
        for m in midpoints(Da):
            if m in U_dia:
                res[4].append((aa, m))
    return res


# ---------------------------------------------------------------- isosceles machinery

def iso_triples(S):
    """All isosceles triples (a,b,c) with apex b, a<c in index order, |a-b|^2=|c-b|^2.
    Returns list of (ib, ia, ic, r2)."""
    m = len(S)
    P = S.astype(np.int64)
    out = []
    for ib in range(m):
        d = P - P[ib]
        r2 = d[:, 0] ** 2 + d[:, 1] ** 2
        order = np.argsort(r2, kind='stable')
        rs = r2[order]
        i = 0
        while i < len(rs):
            j = i
            while j + 1 < len(rs) and rs[j + 1] == rs[i]:
                j += 1
            if rs[i] != 0 and j > i:
                grp = order[i:j + 1]
                for u in range(len(grp)):
                    for v in range(u + 1, len(grp)):
                        ia, ic = int(grp[u]), int(grp[v])
                        out.append((ib, ia, ic, int(rs[i])))
            i = j + 1
    return out


def is_iso_free(S):
    """Independent check via per-apex duplicate squared distances."""
    P = S.astype(np.int64)
    for ib in range(len(P)):
        d = P - P[ib]
        r2 = d[:, 0] ** 2 + d[:, 1] ** 2
        r2 = r2[r2 != 0]
        if len(np.unique(r2)) != len(r2):
            return False
    return True


def prim_dir(v):
    """Primitive direction of nonzero integer vector v, normalised:
    first nonzero coordinate positive."""
    a, b = int(v[0]), int(v[1])
    g = gcd(abs(a), abs(b))
    a, b = a // g, b // g
    if a < 0 or (a == 0 and b < 0):
        a, b = -a, -b
    return (a, b), g


def bisector_has_lattice(a, c):
    """L1 criterion: bisector of a,c contains a lattice point."""
    d = (int(c[0]) - int(a[0]), int(c[1]) - int(a[1]))
    e, g = prim_dir(d)
    return (g % 2 == 0) or (e[0] % 2 == 1 and e[1] % 2 == 1)
