"""Root-level checks.

(1) Brute-force verification of Lemma L1 (lattice points on a perpendicular bisector).
(2) Numerical optimisation of the diagonal/anti-diagonal constant-factor bound in L3.

Exact integer arithmetic only.
"""
from math import gcd


def bisector_has_lattice_point_bruteforce(a, c, R=60):
    """True iff some lattice point in [-R,R]^2 is equidistant from a and c."""
    for x in range(-R, R + 1):
        for y in range(-R, R + 1):
            d1 = (x - a[0]) ** 2 + (y - a[1]) ** 2
            d2 = (x - c[0]) ** 2 + (y - c[1]) ** 2
            if d1 == d2:
                return True
    return False


def bisector_has_lattice_point_criterion(a, c):
    """L1: lattice points exist iff g even, or e = d/g has both coords odd."""
    d = (c[0] - a[0], c[1] - a[1])
    g = gcd(abs(d[0]), abs(d[1]))
    e = (d[0] // g, d[1] // g)
    return (g % 2 == 0) or (e[0] % 2 == 1 and e[1] % 2 == 1)


def check_L1(M=7):
    bad = []
    for a1 in range(-M, M + 1):
        for a2 in range(-M, M + 1):
            for c1 in range(-M, M + 1):
                for c2 in range(-M, M + 1):
                    if (a1, a2) == (c1, c2):
                        continue
                    got = bisector_has_lattice_point_criterion((a1, a2), (c1, c2))
                    want = bisector_has_lattice_point_bruteforce((a1, a2), (c1, c2), R=40)
                    if got != want:
                        bad.append(((a1, a2), (c1, c2), got, want))
    return bad


def diagonal_bound_constant(n):
    """Best m allowed by the two diagonal/anti-diagonal constraints of L3.

    Anti-diagonal A in 0..2n-2 holds min(A+1, 2n-1-A) grid points.
    Diagonal d in -(n-1)..(n-1) holds n-|d| grid points.
    If w anti-diagonals are occupied, every diagonal obeys |S cap d| <= n+1-w/2
    (from |M(Q_d)| >= 2|Q_d|-3 and M(Q_d) avoiding the w occupied anti-diagonals).
    """
    anti_sizes = sorted((min(A + 1, 2 * n - 1 - A) for A in range(2 * n - 1)), reverse=True)
    prefix = [0]
    for s in anti_sizes:
        prefix.append(prefix[-1] + s)
    best = 0
    for w in range(1, 2 * n):
        cap = n + 1 - w / 2.0
        if cap < 1:
            break
        diag_total = sum(min(n - abs(d), cap) for d in range(-(n - 1), n))
        m = min(prefix[w], diag_total)
        best = max(best, m)
    return best


if __name__ == "__main__":
    bad = check_L1(M=6)
    print("L1 counterexamples:", len(bad))
    if bad:
        print(bad[:5])
    for n in (50, 100, 200, 400, 800):
        b = diagonal_bound_constant(n)
        print(f"n={n:5d}  diagonal-form bound = {b:12.1f}  = {b / n**2:.4f} n^2")
