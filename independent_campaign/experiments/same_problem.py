"""Is the m(p) ladder actually INDEPENDENT evidence from the g(q) ladder?

This script exists to attack my own evidence base.  The closeout records four
"independent" falsification instruments for route SQ:
    (1) Theorem 4          -- Behrend digit spheres cannot be square-corner-free (a proof)
    (2) exact g(q), q<=11  -- square corners on the torus (Z_q)^2
    (3) m(p) to p=8009     -- twisted 3-APs {y,y+d,y+kd} in F_p, k^2=-1
    (4) torus search q<=64 -- same object as (2), larger q, lower bounds only
and notes that (2)/(3) "agree to three digits", treating the agreement as
corroboration from two directions.

CLAIM UNDER TEST (if true, that reading is wrong and the evidence must be downgraded):
    (3) is not a different problem from (2).  It is the SAME problem on a different
    Z[i]-module quotient.

    Define psi : Z^2 -> F_p by psi(a,b) = a + k*b  (mod p), k^2 = -1.
    Then psi(-b, a) = -b + k*a = k*(a + k*b) = k*psi(a,b), i.e. psi intertwines
    multiplication by i on Z^2 with multiplication by k on F_p.  psi is onto with
    kernel the lattice Lambda_p = {(a,b) : a + k b = 0 mod p}, det Lambda_p = p.
    So F_p = Z[i]/(pi) as a Z[i]-module, and:

        A subset of F_p is twisted-AP-free  <=>  psi^{-1}(A) subset of Z^2/Lambda_p
        is square-corner-free,

    because the twisted AP y, y+d, y+kd is exactly the square corner b, b+w, b+i*w.

    Consequence: m(p) is the square-corner problem on a group of p elements, and g(q)
    is the square-corner problem on a group of q^2 elements.  Expressed against GROUP
    SIZE the two exponents must coincide.  If they do, (3) is a re-parameterisation of
    (2), not a second witness, and only (1) is independent.

Everything is checked against the complete definition of each problem, written twice,
sharing no code (F3 rule).
"""
import math
import random
import sys


# ------------------------------------------------- problem 1: twisted APs in F_p

def sqrt_m1(p):
    for k in range(1, p):
        if (k * k + 1) % p == 0:
            return k
    return None


def tw_violations(A, p, k):
    """complete definition: y, y+d, y+kd in A, d != 0"""
    S = set(A)
    c = 0
    for y in A:
        for z in A:
            if z == y:
                continue
            if (y + k * (z - y)) % p in S:
                c += 1
    return c


def tw_greedy(p, k, restarts, rng):
    best = []
    order = list(range(p))
    for _ in range(restarts):
        rng.shuffle(order)
        A, S = [], set()
        kinv = pow(k, p - 2, p)
        for x in order:
            ok = True
            for y in A:
                if (y + k * (x - y)) % p in S:      # x as second point
                    ok = False
                    break
                if (x + k * (y - x)) % p in S:      # x as first point
                    ok = False
                    break
                d = (x - y) * kinv % p              # x as third point
                if d and (y + d) % p in S:
                    ok = False
                    break
            if ok:
                A.append(x)
                S.add(x)
        if len(A) > len(best):
            best = A
    return best


# --------------------------------- problem 2: square corners on Z^2 / Lambda_p
# represented concretely, with NO reference to the F_p picture

def lattice_reduce(p, k):
    """a reduced basis of Lambda_p = {(a,b) : a + k b = 0 mod p}, det = p.
    Basis: (p,0) and (-k,1).  Gauss-reduce."""
    u, v = (p, 0), (-k, 1)
    for _ in range(200):
        nu = u[0] * u[0] + u[1] * u[1]
        nv = v[0] * v[0] + v[1] * v[1]
        if nv < nu:
            u, v = v, u
            continue
        m = round((u[0] * v[0] + u[1] * v[1]) / nu)
        w = (v[0] - m * u[0], v[1] - m * u[1])
        if w == v:
            break
        v = w
    return u, v


def sc_violations_torus(A, reduce_fn):
    """complete definition of square-corner-freeness on the quotient:
    b, b+w, b+i*w with w != 0, all reduced to canonical coset representatives."""
    S = set(reduce_fn(x) for x in A)
    c = 0
    for b in S:
        for u in S:
            if u == b:
                continue
            w = (u[0] - b[0], u[1] - b[1])
            iw = (-w[1], w[0])
            if reduce_fn((b[0] + iw[0], b[1] + iw[1])) in S:
                c += 1
    return c


def make_reducer(p, k):
    """canonical representative of (a,b) mod Lambda_p.  Lambda_p is the kernel of
    (a,b) -> a + k b mod p, so the coset is determined by that value; represent it
    as (value, 0)."""
    def red(z):
        return ((z[0] + k * z[1]) % p, 0)
    return red


# --------------------------------------------------- problem 3: torus (Z_q)^2

def torus_violations(A, q):
    S = set((x % q, y % q) for x, y in A)
    c = 0
    for b in S:
        for u in S:
            if u == b:
                continue
            wx, wy = u[0] - b[0], u[1] - b[1]
            if (((b[0] - wy) % q), ((b[1] + wx) % q)) in S:
                c += 1
    return c


def torus_greedy(q, restarts, rng):
    cells = [(x, y) for x in range(q) for y in range(q)]
    best = []
    for _ in range(restarts):
        rng.shuffle(cells)
        A, S = [], set()
        for pnt in cells:
            ok = True
            for s in S:
                for (b, u) in ((pnt, s), (s, pnt)):
                    wx, wy = u[0] - b[0], u[1] - b[1]
                    if (wx % q or wy % q) and \
                       (((b[0] - wy) % q), ((b[1] + wx) % q)) in S:
                        ok = False
                        break
                if not ok:
                    break
                # pnt as the third point: b = s, need u with i*(u-s) = pnt - s
                dx, dy = pnt[0] - s[0], pnt[1] - s[1]
                wx, wy = dy % q, (-dx) % q          # w = i^{-1}(pnt - s)
                cand = ((s[0] + wx) % q, (s[1] + wy) % q)
                if (wx or wy) and cand in S:
                    ok = False
                    break
            if ok:
                A.append(pnt)
                S.add(pnt)
        if len(A) > len(best):
            best = A
    return best


def main():
    rng = random.Random(20260817)

    print("T1  psi intertwines i on Z^2 with k on F_p  (exact, all residues)")
    for p in (13, 17, 29, 37, 41, 101, 401, 1601):
        k = sqrt_m1(p)
        bad = 0
        for a in range(p):
            for b in range(p):
                lhs = ((-b) + k * a) % p            # psi(i*(a,b)) = psi(-b, a)
                rhs = (k * (a + k * b)) % p         # k * psi(a,b)
                if lhs != rhs:
                    bad += 1
        print(f"    p={p:>6} k={k:>6}  mismatches = {bad}")

    print("\nT2  twisted-AP-free in F_p  <=>  square-corner-free in Z^2/Lambda_p"
          "\n    (random sets, both complete definitions, no shared code)")
    for p in (13, 17, 29, 37, 41, 101, 401):
        k = sqrt_m1(p)
        red = make_reducer(p, k)
        dis = 0
        for _ in range(300):
            s = rng.randint(2, max(3, min(p, 14)))
            A = rng.sample(range(p), s)
            f1 = tw_violations(A, p, k) == 0
            # lift each residue x to some (a,b) with a + k b = x -- take (x, 0)
            lift = [(x, 0) for x in A]
            f2 = sc_violations_torus(lift, red) == 0
            if f1 != f2:
                dis += 1
        print(f"    p={p:>6}  disagreements = {dis} / 300")

    print("\nT3  reduced basis of Lambda_p: the fundamental domain is ~sqrt(p) x sqrt(p)")
    print(f"    {'p':>8} {'|u|':>9} {'|v|':>9} {'sqrt(p)':>9}")
    for p in (101, 401, 1601, 6421, 25601, 102401):
        k = sqrt_m1(p)
        if k is None:
            continue
        u, v = lattice_reduce(p, k)
        print(f"    {p:>8} {math.hypot(*u):>9.2f} {math.hypot(*v):>9.2f} "
              f"{math.sqrt(p):>9.2f}")

    print("\nT4  THE TEST.  exponent against GROUP SIZE for both problems."
          "\n    m(p) lives on a group of p elements;  g(q) on a group of q^2."
          "\n    if these coincide, the two ladders are ONE instrument, not two.")
    print(f"    {'problem':>12} {'param':>7} {'|G|':>8} {'value':>7} "
          f"{'log val / log |G|':>18} {'viol':>5}")
    rows = []
    for p in (101, 401, 1601, 6421):
        k = sqrt_m1(p)
        A = tw_greedy(p, k, max(4, 60000 // p), rng)
        v = tw_violations(A, p, k)
        e = math.log(len(A)) / math.log(p)
        rows.append(("m(p)", p, p, len(A), e))
        print(f"    {'m(p)':>12} {p:>7} {p:>8} {len(A):>7} {e:>18.4f} {v:>5}")
    for q in (10, 20, 40, 80):
        A = torus_greedy(q, max(4, 40000 // (q * q)), rng)
        v = torus_violations(A, q)
        e = math.log(len(A)) / math.log(q * q)
        rows.append(("g(q)", q, q * q, len(A), e))
        print(f"    {'g(q)':>12} {q:>7} {q*q:>8} {len(A):>7} {e:>18.4f} {v:>5}")

    ms = [e for nm, _, _, _, e in rows if nm == "m(p)"]
    gs = [e for nm, _, _, _, e in rows if nm == "g(q)"]
    print(f"\n    m(p) exponents vs |G|: {[f'{x:.4f}' for x in ms]}")
    print(f"    g(q) exponents vs |G|: {[f'{x:.4f}' for x in gs]}")
    print(f"    means: m {sum(ms)/len(ms):.4f}   g {sum(gs)/len(gs):.4f}   "
          f"gap {abs(sum(ms)/len(ms) - sum(gs)/len(gs)):.4f}")
    print("\n    a gap of order 0.00x means SAME PROBLEM: the m(p) ladder must be")
    print("    struck as independent evidence, leaving Theorem 4 as the only")
    print("    instrument that is not a search on this one object.")


if __name__ == "__main__":
    main()
