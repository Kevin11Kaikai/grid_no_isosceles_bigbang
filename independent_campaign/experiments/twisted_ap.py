"""THE FALSIFICATION TEST for the square-corner route.

Reduction (proved here, verified below).  Let p = 1 mod 4 and k^2 = -1 mod p.  The map
      psi(x + iy) = (x + k y,  x - k y)
is a ring isomorphism (Z_p)^2 = Z_p[i] -> F_p x F_p, and psi(i z) = (k psi_1, -k psi_2).
Under psi the square-corner equation v = i u + (1-i) b becomes the two independent
one-dimensional equations
      v_1 = k u_1 + (1-k) b_1        i.e.  avoid  {y, y+d, y + k d}
      v_2 = -k u_2 + (1+k) b_2       i.e.  avoid  {y, y+d, y - k d}
A violation needs u != b, hence u_1 != b_1 or u_2 != b_2, so

      PRODUCT LEMMA:  A avoids {y,y+d,y+kd} and B avoids {y,y+d,y-kd}
                      ==>  T = psi^{-1}(A x B) is torus square-corner-free,
                      and |T| = |A| |B|.

Combined with the tensor lemma (torus_sq.py) this gives
      Q_SQ(n) >= n^{2 log m(p) / log p},        m(p) = max |A|.

So: if m(p) = p^{1-o(1)} then Q_SQ(n) = n^{2-o(1)} and THE SQUARE-CORNER ROUTE IS DEAD,
exactly as Q4 died.  If m(p) = p^{1/2+o(1)} the route survives, because an interval of
length ~sqrt(p) is already pattern-free (Minkowski: the lattice {(d, kd mod p)} has
determinant p, so its shortest vector has norm ~sqrt(p)) and that only reproduces the
trivial bound Q_SQ(n) >= n.

A LOWER bound on m(p) is all that is needed to kill the route, so heuristic search is
legitimate here -- the asymmetry runs the right way (contrast the Q4 lesson, where a
heuristic UPPER estimate was worthless).
"""
import math
import random
import sys


def sqrt_m1(p):
    for k in range(2, p):
        if (k * k + 1) % p == 0:
            return k
    return None


def violations(A, p, k):
    """count triples y, y+d, y+kd (d != 0) fully inside A -- naive, independent check"""
    S = set(A)
    c = 0
    for y in S:
        for d in range(1, p):
            if (y + d) % p in S and (y + k * d) % p in S:
                c += 1
    return c


def greedy(p, k, rounds, rng):
    """randomised greedy lower bound for m(p)"""
    best = []
    order = list(range(p))
    for _ in range(rounds):
        rng.shuffle(order)
        A = set()
        for y in order:
            ok = True
            # adding y must not complete any pattern; y can play any of the 3 roles
            for z in A:
                d = (z - y) % p                      # y first, z second
                if d and (y + k * d) % p in A:
                    ok = False
                    break
                d = (y - z) % p                      # z first, y second
                if d and (z + k * d) % p in A:
                    ok = False
                    break
                # y is the third point: y = w + k*d, z = w + d  -> w = (k z - y)/(k-1)
                num = (k * z - y) % p
                den = (k - 1) % p
                w = num * pow(den, -1, p) % p
                if w in A and w != z and (z - w) % p:
                    ok = False
                    break
            if ok:
                A.add(y)
        if len(A) > len(best):
            best = sorted(A)
    return best


def exact(p, k, cap_time=None):
    """exhaustive max, branch and bound; only for small p"""
    from time import time
    t0 = time()
    # forbidden: for each pair (a,b) the third points completing a pattern
    third = {}
    for a in range(p):
        for b in range(p):
            if a == b:
                continue
            out = set()
            d = (b - a) % p
            out.add((a + k * d) % p)                       # a first, b second
            # a second, b first
            d2 = (a - b) % p
            out.add((b + k * d2) % p)
            # a third: a = w + k d, b = w + d
            den = pow((k - 1) % p, -1, p)
            out.add((k * b - a) % p * den % p)
            out.add((k * a - b) % p * den % p)
            out.discard(a)
            out.discard(b)
            third[(a, b)] = out
    best = [0, None]

    def rec(A, cand):
        if cap_time and time() - t0 > cap_time:
            raise TimeoutError
        if len(A) + len(cand) <= best[0]:
            return
        if len(A) > best[0]:
            best[0], best[1] = len(A), list(A)
        for j, y in enumerate(cand):
            if len(A) + len(cand) - j <= best[0]:
                return
            rest = [z for z in cand[j + 1:]
                    if all(z not in third[(a, y)] for a in A + [y] if a != y)
                    and not any(third[(y, z)] & set(A))]
            # the second clause is subsumed; keep the simple sound filter
            rec(A + [y], rest)

    # translation invariance: 0 in A
    cand = [z for z in range(1, p)]
    try:
        rec([0], cand)
    except TimeoutError:
        return None, None
    return best[0], best[1]


if __name__ == "__main__":
    rng = random.Random(20250817)
    print("m(p) = max subset of F_p with no {y, y+d, y+kd}, k^2 = -1 mod p")
    print(f"{'p':>6} {'sqrt(p)':>8} {'m_exact':>8} {'m_greedy':>9} "
          f"{'log m/log p':>12} {'m/sqrt(p)':>10} {'viol':>5}")
    ps = [5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97, 101, 109, 113, 137, 149, 157,
          173, 181, 193, 197, 229, 257, 269, 281, 313, 337, 353, 389, 401, 449, 509,
          577, 641, 733, 809, 929, 1013, 1201, 1409, 1601, 2003, 2503, 3001, 4001,
          5003, 6007, 8009, 10007]
    for p in ps:
        k = sqrt_m1(p)
        if k is None:
            continue
        rounds = max(3, min(400, 2_000_00 // p))
        A = greedy(p, k, rounds, rng)
        v = violations(A, p, k) if p <= 2000 else -1
        ex = ""
        if p <= 61:
            e, _ = exact(p, k, cap_time=60)
            ex = str(e) if e else "t/o"
        print(f"{p:>6} {math.sqrt(p):>8.2f} {ex:>8} {len(A):>9} "
              f"{math.log(len(A))/math.log(p):>12.4f} "
              f"{len(A)/math.sqrt(p):>10.3f} {v:>5}")
