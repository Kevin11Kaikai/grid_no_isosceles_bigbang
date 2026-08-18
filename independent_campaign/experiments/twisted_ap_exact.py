"""Exact m(p) by brute force, and an ADVERSARIAL test of the product lemma.

Two errors were caught while building this and are recorded here so they are not
repeated:

  E1  A hand-written incremental "pattern-completion" table listed only 4 of the 6 ways
      an unordered pair extends to a pattern {w, w+d, w+kd}.  Symptom: overestimated
      m(5) = 3.  The offending set {0,1,3} is 3-AP-free over Z but NOT over Z_5
      (1, 3, 0 has common difference 2 mod 5).  The same omission had already bitten the
      C torus solver.  Fix: never filter with a hand-derived table -- test the complete
      definition (all y, all d != 0) directly.

  E2  The product lemma was briefly believed refuted because it was fed the invalid
      A = {0,1,3} from E1.  A wrong input, not a wrong lemma.

Everything below uses only the complete definition.
"""
from itertools import combinations
import math


def has_pattern(A, p, k):
    """complete test: some y in A, d != 0 with y+d and y+kd in A"""
    S = set(A)
    for y in S:
        for d in range(1, p):
            if (y + d) % p in S and (y + k * d) % p in S:
                return True
    return False


def m_exact(p, k, hi=None):
    """max |A| over A subset F_p with no pattern -- exhaustive.  0 in A wlog
    (the condition is translation invariant)."""
    hi = hi or p
    for size in range(hi, 0, -1):
        for rest in combinations(range(1, p), size - 1):
            A = (0,) + rest
            if not has_pattern(A, p, k):
                return size, A
    return 0, ()


def sqrt_m1(p):
    return next((k for k in range(2, p) if (k * k + 1) % p == 0), None)


# ------------------------------------------------------------------ exact table
print("EXACT m(p), brute force over the complete definition")
print(f"{'p':>5} {'k':>4} {'m(p)':>5} {'log m/log p':>12} {'m/sqrt p':>9}  witness")
exact = {}
for p in (5, 13, 17, 29, 37, 41):
    k = sqrt_m1(p)
    hi = {5: 3, 13: 4, 17: 5, 29: 6, 37: 8, 41: 8}[p] + 1   # start just above greedy
    m, A = m_exact(p, k, hi)
    exact[p] = m
    print(f"{p:>5} {k:>4} {m:>5} {math.log(m)/math.log(p):>12.4f} "
          f"{m/math.sqrt(p):>9.3f}  {A}")

# ------------------------------------------------------------------ product lemma
print("\nPRODUCT LEMMA test, with VERIFIED pattern-free factors")


def torus_corners(T, q):
    S = set(T)
    out = []
    for b in S:
        for u in S:
            if u == b:
                continue
            wx, wy = (u[0] - b[0]) % q, (u[1] - b[1]) % q
            v = ((b[0] - wy) % q, (b[1] + wx) % q)
            if v in S:
                out.append((b, u, v))
    return out


print(f"{'p':>5} {'|A|':>4} {'|B|':>4} {'|A||B|':>7} {'g(p) known':>11} "
      f"{'corners in psi^-1(AxB)':>23}")
gknown = {5: 5, 13: None, 17: None, 29: None, 37: None}
for p in (5, 13, 17, 29):
    k = sqrt_m1(p)
    mA, A = m_exact(p, k, exact.get(p, 6) + 1)
    mB, B = m_exact(p, (-k) % p, exact.get(p, 6) + 1)
    inv2, invk = pow(2, -1, p), pow(k, -1, p)
    T = [(((a + b) * inv2) % p, ((a - b) * inv2 * invk) % p) for a in A for b in B]
    assert len(set(T)) == len(T)
    nc = len(torus_corners(T, p))
    g = gknown.get(p)
    print(f"{p:>5} {mA:>4} {mB:>4} {mA*mB:>7} {str(g):>11} {nc:>23}")

print("\nSo g(p) >= m_A(p) * m_B(p) for split p, and with m(p) ~ p^0.55 that is only")
print("about p^1.10 -- far from the p^{2-o(1)} that would kill the route.")
