"""Computational verification of the two NO-GO relaxations.

(A)  3AP-relaxation T(n): forbid only DEGENERATE isosceles triples (collinear,
     b the midpoint of a,c) -- i.e. S contains no 3-term AP in Z^2.
     Claim: A 3AP-free in [n]  =>  A x A is 3AP-free in [n]^2.  Hence
     T(n) >= r_3(n)^2 = n^{2-o(1)}  (Behrend), so T(kn)/T(n) -> k^2.

(B)  bounded-leg relaxation R_L(n): forbid only isosceles triples with legs of
     squared length <= L.  Claim: positive density, hence R_L(kn)/R_L(n)->k^2.
"""
import itertools, math

def r3_set(n):
    """exact max 3AP-free subset of [n] by DFS (small n)."""
    best = []
    def ok(S, x):
        for a in S:
            # a, x  ->  need midpoint & extension checks
            if (a + x) % 2 == 0 and (a + x)//2 in S: return False
            if 2*x - a in S: return False
            if 2*a - x in S: return False
        return True
    def dfs(i, S):
        nonlocal best
        if len(S) + (n - i) <= len(best): return
        if i == n:
            if len(S) > len(best): best = list(S)
            return
        if ok(S, i):
            S.append(i); dfs(i+1, S); S.pop()
        dfs(i+1, S)
    dfs(0, [])
    return best

def has_3ap_2d(pts):
    P = set(pts)
    for b in pts:
        for a in pts:
            if a == b: continue
            c = (2*b[0]-a[0], 2*b[1]-a[1])
            if c in P and c != a and c != b:
                return True, (a, b, c)
    return False, None

print("=== (A) Behrend product is 3AP-free in Z^2 ===")
for n in range(2, 26):
    A = r3_set(n)
    S = [(x, y) for x in A for y in A]
    bad, w = has_3ap_2d(S)
    print(f"  n={n:>2}  r3(n)={len(A):>2}  |AxA|={len(S):>3}  "
          f"3AP-free in Z^2: {not bad}  {'' if not bad else w}")

print("\n  ratio T(2n)/T(n) lower bound from the product construction, using")
print("  the trivial upper bound T(m) <= m^2:   >= r3(2n)^2 / (n^2)")
for n in [4,6,8,10,12]:
    a, b = len(r3_set(n)), len(r3_set(2*n))
    print(f"  n={n:>2}: r3(n)={a}, r3(2n)={b}, (r3(2n)/r3(n))^2 = {(b/a)**2:.4f}  (-> 4)")

print("\n=== (B) bounded-leg relaxation has positive density ===")
print("  S = M*Z^2 cap [n]^2 has min pairwise squared distance M^2 > L,")
print("  so it has NO isosceles triple with legs of squared length <= L.")
for L in [1,2,4,8,16,50]:
    M = int(math.isqrt(L)) + 1
    print(f"  L={L:>3}: take M={M}, density 1/M^2 = {1/M**2:.5f} > 0")
