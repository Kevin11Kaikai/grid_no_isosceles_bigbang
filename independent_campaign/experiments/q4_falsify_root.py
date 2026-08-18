"""ROOT FALSIFICATION ATTEMPT ON Q4.

Claim (proved in comments below): if A,B,W,Z are 3-AP-free and

    S = { (x,y) in [n]^2 : x in A, y in B, x+y in W, x-y in Z }

then S satisfies ALL FOUR Q4 constraints.

Proof.  U_col (occupied columns) is a subset of A.  For any row y, X_y is a subset of A,
so M(X_y) is a subset of M(A), and M(A) cap A = empty because A is 3-AP-free.  Hence
M(X_y) cap U_col = empty: constraint (1).  Constraint (2) is the same with B.  In rotated
coordinates U_ant is a subset of W and U_dia is a subset of Z, giving (3) and (4).  QED

So Q4(n) >= max over 3-AP-free A,B,W,Z of |S|.  Heuristically, if the four membership
events were independent, |S| would be about n^2 * delta^4 with delta = exp(-c sqrt(log n)),
i.e. n^{2-o(1)} -- which would BARRIER Q4 exactly as Behrend's B x B barriers the axis-only
mechanism.  The danger to that heuristic: x, y, x+y, x-y are four linear forms in only two
variables, so the events are strongly dependent.  Indeed for A=B=W=Z the count collapses:
x-y, x, x+y in A is a 3-AP in A, so only y=0 survives.

This script measures the truth by searching over shifted Behrend-type sets.

Exact integer arithmetic only.
"""
import numpy as np


def base3_no_two(L):
    """3-AP-free: integers in [0,L) whose base-3 expansion omits the digit 2."""
    out = []
    for x in range(L):
        t, ok = x, True
        while t:
            if t % 3 == 2:
                ok = False
                break
            t //= 3
        if ok:
            out.append(x)
    return np.array(out, dtype=np.int64)


def behrend(L, d=None):
    """Behrend-type 3-AP-free set: base-d digit vectors on a sphere, no carries."""
    if d is None:
        d = max(3, int(round((2 * np.log(max(L, 3))) ** 0.5)) * 2 + 1)
    k = max(1, int(np.ceil(np.log(max(L, 2)) / np.log(d // 2 + 1))))
    half = d // 2
    best = None
    from collections import defaultdict
    buckets = defaultdict(list)
    digits = np.arange(half)
    # enumerate digit vectors with entries < half, in base d, value < L
    def rec(pos, val, sq, cur):
        if val >= L:
            return
        if pos == k:
            buckets[sq].append(val)
            return
        p = d ** pos
        for g in digits:
            nv = val + int(g) * p
            if nv >= L:
                break
            rec(pos + 1, nv, sq + int(g) * int(g), cur)
    rec(0, 0, 0, [])
    for s, lst in buckets.items():
        if best is None or len(lst) > len(best):
            best = lst
    return np.array(sorted(best), dtype=np.int64)


def is_3ap_free(arr):
    s = set(int(v) for v in arr)
    a = sorted(s)
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if (a[i] + a[j]) % 2 == 0 and (a[i] + a[j]) // 2 in s:
                return False
    return True


def mask_from(arr, lo, hi):
    """boolean mask over [lo,hi) for the integer set arr"""
    m = np.zeros(hi - lo, dtype=bool)
    v = arr[(arr >= lo) & (arr < hi)]
    m[v - lo] = True
    return m


def count_S(n, A, B, W, Z):
    """|{(x,y): x in A, y in B, x+y in W, x-y in Z}| and the point list."""
    mA = mask_from(A, 0, n)
    mB = mask_from(B, 0, n)
    mW = mask_from(W, 0, 2 * n - 1)
    mZ = mask_from(Z, -(n - 1), n)          # index shift by n-1
    xs = np.arange(n)
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    ok = mA[X] & mB[Y] & mW[X + Y] & mZ[X - Y + (n - 1)]
    return int(ok.sum()), ok


def search(n, trials, rng, base="b3"):
    gen = base3_no_two if base == "b3" else behrend
    T1 = gen(n)
    T2 = gen(2 * n)
    assert is_3ap_free(T1) and is_3ap_free(T2), "generator is not 3-AP-free"
    best = (0, None)
    for _ in range(trials):
        a = rng.integers(-n, n)
        b = rng.integers(-n, n)
        w = rng.integers(-2 * n, 2 * n)
        z = rng.integers(-2 * n, 2 * n)
        A, B = T1 + a, T1 + b
        W, Z = T2 + w, T2 + z
        c, _ = count_S(n, A, B, W, Z)
        if c > best[0]:
            best = (c, (int(a), int(b), int(w), int(z)))
    return best, len(T1)


if __name__ == "__main__":
    rng = np.random.default_rng(20260816)
    print("Shifted-Behrend product construction for Q4")
    print(f"{'n':>6} {'|T|':>6} {'best |S|':>9} {'|S|/n':>8}  best shifts (a,b,w,z)")
    prev = None
    for n in (27, 81, 243, 729):
        (c, sh), t = search(n, 4000 if n <= 243 else 1500, rng)
        slope = ""
        if prev and c > 0 and prev[1] > 0:
            slope = f"  slope={np.log(c / prev[1]) / np.log(n / prev[0]):.3f}"
        print(f"{n:>6} {t:>6} {c:>9} {c / n:>8.3f}  {sh}{slope}")
        prev = (n, c)
