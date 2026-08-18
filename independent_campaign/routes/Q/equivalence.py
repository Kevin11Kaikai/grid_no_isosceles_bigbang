"""Route Q -- CLAIM: isosceles-freeness IS the line-kill family over ALL primitive directions.

Claim (PROVED in report.md, verified here):
    S is isosceles-free
      <=>  for every primitive e in Z^2, the line-kill constraint LK(e) holds:
             for every e-line L and every pair p,q in S cap L,
             the level (phi_e(p)+phi_e(q))/2 is not in phi_e(S)
             -- imposed only when phi_e(p) = phi_e(q) mod 2.
    where phi_e(p) = <p,e>.

So Q4 = LK(e) for the four directions e = (1,0),(0,1),(1,1),(1,-1), and isosceles-freeness
is the same family with ALL ~n^2 primitive directions.  The line-kill mechanism is therefore
LOSSLESS; the entire question is how the family degrades under truncation of the direction set.

Verified by brute force on random sets.
"""
import random
from math import gcd


def primitive_dirs(n):
    """One representative per primitive direction (up to sign) with |e|_inf < n."""
    out = []
    for a in range(-(n - 1), n):
        for b in range(0, n):
            if (a, b) == (0, 0):
                continue
            if gcd(abs(a), abs(b)) != 1:
                continue
            if b == 0 and a < 0:
                continue
            out.append((a, b))
    return out


def lk_violations(S, e):
    """Violations of LK(e).  Group S by the e-LINE it lies on (level of psi_e = <p,e^perp>),
    and test same-parity midpoints of phi_e values against phi_e(S)."""
    ex, ey = e
    phi = lambda p: p[0] * ex + p[1] * ey
    psi = lambda p: -p[0] * ey + p[1] * ex
    lines = {}
    for p in S:
        lines.setdefault(psi(p), []).append(p)
    PHI = {phi(p) for p in S}
    bad = []
    for lev, pts in lines.items():
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                a, b = phi(pts[i]), phi(pts[j])
                if (a + b) % 2 == 0 and (a + b) // 2 in PHI:
                    bad.append((e, pts[i], pts[j], (a + b) // 2))
    return bad


def isosceles_triples(S):
    P = list(S)
    out = []
    for b in P:
        by = {}
        for a in P:
            if a == b:
                continue
            r = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            by.setdefault(r, []).append(a)
        for r, L in by.items():
            for i in range(len(L)):
                for j in range(i + 1, len(L)):
                    out.append((L[i], b, L[j], r))
    return out


def main():
    rng = random.Random(11)
    mismatches = 0
    trials = 0
    for _ in range(500):
        n = rng.randint(3, 9)
        k = rng.randint(2, 9)
        S = set()
        while len(S) < k:
            S.add((rng.randrange(n), rng.randrange(n)))
        iso = isosceles_triples(S)
        anylk = any(lk_violations(S, e) for e in primitive_dirs(2 * n))
        trials += 1
        if bool(iso) != anylk:
            mismatches += 1
            print("MISMATCH", n, sorted(S), len(iso), anylk)
    print(f"isosceles-free  <=>  LK(e) for all primitive e:  "
          f"{trials} random sets, {mismatches} mismatches")

    # stronger: for each isosceles triple, the base direction must be the responsible e
    rng = random.Random(12)
    checked = 0
    for _ in range(200):
        n = rng.randint(4, 10)
        S = set()
        while len(S) < rng.randint(3, 10):
            S.add((rng.randrange(n), rng.randrange(n)))
        for (a, b, c, r) in isosceles_triples(S):
            d = (c[0] - a[0], c[1] - a[1])
            g = gcd(abs(d[0]), abs(d[1]))
            e = (d[0] // g, d[1] // g)
            v = lk_violations(S, e)
            assert any({x, y} == {a, c} for (_, x, y, _) in v), \
                f"base direction {e} did not explain triple {a},{b},{c}"
            checked += 1
    print(f"every isosceles triple is explained by LK(base direction): {checked} triples, OK")


if __name__ == "__main__":
    main()
