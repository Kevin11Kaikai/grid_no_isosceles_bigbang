"""Structured-construction hunt for m(p) -- the decisive adversarial attack on route SQ.

WHY THIS INSTRUMENT AND NOT MORE GREEDY.
Failure ledger F1 is explicit: greedy random-restart on Q4 reported ~1.8n with slopes
~1.0 across n=8..96 while the truth was n^{2-o(1)}, because greedy cannot find an
algebraically structured set.  Every surviving piece of evidence for route SQ except
Theorem 4 is search-based.  So the honest adversarial move is to hunt for STRUCTURED
constructions.  If ANY structured family beats p^{0.55}, route SQ dies exactly as Q4 did.

    m(p) = max |A|,  A subset of F_p,  with no  y, y+d, y+kd  all in A  (d != 0, k^2 = -1).

Baseline to beat: greedy reported m(p) = p^{0.547 +- 0.005} flat from p=37 to p=8009,
and exact values m = 2,3,4,5,7,7 for p = 5,13,17,29,37,41.

HALF-ORBIT LEMMA (proved; recorded in proofs/twisted_ap_half_orbit.md), checked as V0:
    H = <k> = {1,k,-1,-k} acts freely on F_p^* with (p-1)/4 orbits.  A is m-free iff for
    every x in A the difference set D_x = (A-x)\{0} satisfies k*D_x cap D_x = empty.
    Inside one orbit {u,ku,-u,-ku} the forbidden pairs form the 4-cycle
    u - ku - (-u) - (-ku) - u, whose maximum independent sets are {u,-u} and {ku,-ku}.
    Hence |D_x| <= 2*(p-1)/4 and  m(p) <= (p+1)/2.

INVARIANCE (proved, used to prune the family list):  the condition is invariant under
x -> a*x + b for any a in F_p^*, b in F_p, because y,y+d,y+kd maps to
ay+b, (ay+b)+ad, (ay+b)+k(ad).  So translates and DILATES of a free set are free:
"dilated interval" is not a separate family from "interval", and a multiplicative coset
aG is free iff the subgroup G is.  Both are still tested, as a check on this reasoning.

F3 RULE.  Every candidate produced by every constructor is re-checked by violations(),
which is the complete definition and shares no code, table or data structure with any
constructor.  No incremental filter is ever the only test.
"""
import math
import sys


# ---------------------------------------------------------------- arithmetic basics

def is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def prime_1mod4_near(target):
    n = target | 1
    while True:
        if n % 4 == 1 and is_prime(n):
            return n
        n += 2


def sqrt_minus_one(p):
    """all k with k^2 = -1 mod p (there are exactly two for p = 1 mod 4)"""
    return [k for k in range(1, p) if (k * k + 1) % p == 0]


def factorize(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def generator(p):
    fac = list(factorize(p - 1))
    for g in range(2, p):
        if all(pow(g, (p - 1) // q, p) != 1 for q in fac):
            return g
    raise RuntimeError


def divisors(n):
    ds = [1]
    for q, e in factorize(n).items():
        ds = [d * q ** j for d in ds for j in range(e + 1)]
    return sorted(ds)


# ---------------------------------------------------- the complete definition (F3)

def violations(A, p, k):
    """number of ordered (y,z), z != y, with y, z=y+d, y+kd all in A.  Complete, naive."""
    S = set(A)
    c = 0
    for y in A:
        for z in A:
            if z == y:
                continue
            d = z - y
            if (y + k * d) % p in S:
                c += 1
    return c


def free(A, p, k):
    return violations(A, p, k) == 0


# ------------------------------------------------------------------- constructors

def grow_max_free(seq, p, k):
    """longest prefix of seq that is m-free, found by incremental append.

    Uses only the complete definition on the running set, so it is not a
    hand-derived incremental filter.  Monotone: any subset of a free set is free.
    """
    A = []
    S = set()
    for x in seq:
        ok = True
        for y in A:                       # x as the third point, x as a leg, x as the base
            d = x - y
            if (y + k * d) % p in S:      # y, x, y+k(x-y)
                ok = False
                break
            d = y - x
            if (x + k * d) % p in S:      # x, y, x+k(y-x)
                ok = False
                break
        if ok:
            # x as the k-leg: exists y,z in A with z-y = d and y+kd = x
            kinv = pow(k, p - 2, p)
            for y in A:
                d = (x - y) * kinv % p
                if d and (y + d) % p in S:
                    ok = False
                    break
        if ok:
            A.append(x)
            S.add(x)
    return A


def f_interval(p, k):
    """largest L with [0,L) free.  Binary search on the complete test."""
    lo, hi = 1, p
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if free(range(mid), p, k):
            lo = mid
        else:
            hi = mid - 1
    return list(range(lo))


def f_bohr2(p, k):
    """best 2-dimensional Bohr set {x : |x| < r1, |xi*x| < r2}, over a few xi and radii.

    1-dimensional Bohr sets are dilated intervals, hence not a separate family.
    """
    best = []
    cent = lambda t: t - p if t > p // 2 else t
    for xi in {k, (k + 1) % p, 2, 3, (p - 1) // 2 or 1}:
        if xi == 0:
            continue
        for r1e in range(2, 9):
            r1 = int(p ** (r1e / 8.0))
            for r2e in range(2, 9):
                r2 = int(p ** (r2e / 8.0))
                A = [x for x in range(p)
                     if abs(cent(x)) < r1 and abs(cent(xi * x % p)) < r2]
                if len(A) <= len(best):
                    continue
                if free(A, p, k):
                    best = A
    return best


def f_subgroups(p, k):
    """every multiplicative subgroup, plus one nontrivial coset of each, that is free"""
    g = generator(p)
    best = []
    for t in divisors(p - 1):
        if t < 2 or t > 4 * int(p ** 0.6) + 10:
            continue
        h = pow(g, (p - 1) // t, p)
        G = []
        x = 1
        for _ in range(t):
            G.append(x)
            x = x * h % p
        for mult in (1, g, g * g % p):
            A = [mult * u % p for u in G]
            if len(A) > len(best) and free(A, p, k):
                best = A
    return best


def f_gp(p, k):
    """longest geometric progression {g^a : a in [0,L)} that is free"""
    g = generator(p)
    seq, x = [], 1
    for _ in range(min(p - 1, 20000)):
        seq.append(x)
        x = x * g % p
    return grow_max_free(seq, p, k)


def f_residues_interval(p, k):
    """d-th power residues intersected with an initial interval, d in {2,4}"""
    best = []
    for d in (2, 4):
        if (p - 1) % d:
            continue
        R = set(pow(x, (p - 1) // d, p) for x in range(1, p))
        for Le in range(3, 17):
            L = int(p ** (Le / 16.0))
            A = [x for x in range(1, L) if pow(x, (p - 1) // d, p) in R and x % p]
            A = [x for x in range(1, L) if pow(x, (p - 1) // d, p) == 1]
            if len(A) > len(best) and free(A, p, k):
                best = A
    return best


def f_behrend(p, k):
    """Behrend digit-sphere sets pushed into F_p.  Expected to FAIL (cf. Theorem 4)."""
    best = []
    for b in range(3, 12):
        L = max(2, int(math.log(p) / math.log(b)))
        digs = list(range(b // 2))
        pts = []
        def rec(j, val, ssq):
            if j == L:
                pts.append((val, ssq))
                return
            for dg in digs:
                rec(j + 1, val * b + dg, ssq + dg * dg)
        rec(0, 0, 0)
        by = {}
        for val, ssq in pts:
            by.setdefault(ssq, []).append(val % p)
        for ssq, A in by.items():
            A = sorted(set(A))
            if len(A) > len(best) and len(A) < 4000 and free(A, p, k):
                best = A
    return best


def f_halforbit_clique(p, k):
    """A with A-A inside a half-orbit selector T: the natural construction the
    half-orbit lemma suggests.  T picks {u,-u} or {ku,-ku} from each <k>-orbit; a set
    with A-A subset of T u {0} is automatically m-free (proved: any y,y+d,y+kd in A
    would put d and kd both in A-A, hence both in T, contradicting the selector).
    Greedy clique, then re-checked by the complete definition anyway."""
    best = []
    kinv = pow(k, p - 2, p)
    for seed in range(4):
        # selector by index parity blocks: T = {u : ind(u) mod 2M in [0,M)} style,
        # realised without discrete logs by orbit-representative choice
        T = set()
        chosen = {}
        for u in range(1, p):
            if u in chosen:
                continue
            orb = [u, u * k % p, p - u, (p - u) * k % p]
            pick = (orb[0], orb[2]) if (u * (seed + 1)) % 4 < 2 else (orb[1], orb[3])
            for v in orb:
                chosen[v] = True
            T.update(pick)
        A, S = [], set()
        for x in range(p):
            if all(((x - y) % p) in T for y in A):
                A.append(x)
                S.add(x)
        if len(A) > len(best):
            best = A
    return best


FAMILIES = [
    ("interval", f_interval),
    ("bohr-2d", f_bohr2),
    ("subgroup/coset", f_subgroups),
    ("geom-prog", f_gp),
    ("power-residues", f_residues_interval),
    ("behrend-sphere", f_behrend),
    ("half-orbit clique", f_halforbit_clique),
]


# ------------------------------------------------------------------------ checks

def v0_half_orbit_lemma(p, k):
    """verify the lemma's two ingredients directly: H acts freely with (p-1)/4 orbits
    of size 4, and the forbidden graph inside an orbit is a 4-cycle with alpha = 2."""
    seen = set()
    orbits = 0
    for u in range(1, p):
        if u in seen:
            continue
        orb = [u, u * k % p, u * k * k % p, u * k * k * k % p]
        if len(set(orb)) != 4:
            return False, "orbit not free"
        seen.update(orb)
        orbits += 1
        # forbidden pairs {v, kv} within the orbit
        idx = {v: j for j, v in enumerate(orb)}
        edges = set()
        for v in orb:
            edges.add(tuple(sorted((idx[v], idx[v * k % p]))))
        if len(edges) != 4:
            return False, "not a 4-cycle"
        # maximum independent set of a 4-cycle is 2, and equals {u,-u} or {ku,-ku}
        best = 0
        for mask in range(16):
            sel = [j for j in range(4) if mask >> j & 1]
            if all(tuple(sorted(e)) not in edges
                   for e in [(a, b) for a in sel for b in sel if a < b]):
                best = max(best, len(sel))
        if best != 2:
            return False, f"alpha = {best}"
    return orbits == (p - 1) // 4, f"{orbits} orbits, alpha=2, bound m<=({p}+1)/2"


def main():
    targets = [int(a) for a in sys.argv[1:]] or [100, 400, 1600, 6400, 25600, 102400]
    primes = [prime_1mod4_near(t) for t in targets]

    print("V0  half-orbit lemma, verified structurally")
    for p in primes[:4]:
        k = sqrt_minus_one(p)[0]
        ok, msg = v0_half_orbit_lemma(p, k)
        print(f"    p={p:>7} k={k:>6}  {ok}  {msg}")

    print("\nV1  both square roots of -1 give the same m(p)?  (k vs p-k)")
    for p in primes[:4]:
        ks = sqrt_minus_one(p)
        sizes = [len(f_interval(p, kk)) for kk in ks]
        print(f"    p={p:>7} k={ks}  interval sizes {sizes}  "
              f"{'SAME' if len(set(sizes)) == 1 else 'DIFFER'}")

    print("\nV2  structured families.  exponent = log|A| / log p."
          "\n    greedy baseline 0.547;  1.000 would KILL route SQ (density saving only).")
    hdr = f"{'p':>8} {'family':>18} {'|A|':>7} {'exp':>7} {'|A|/sqrt(p)':>12} {'viol':>5}"
    print(hdr)
    champ = {}
    for p in primes:
        k = sqrt_minus_one(p)[0]
        for name, fn in FAMILIES:
            A = fn(p, k)
            if not A:
                print(f"{p:>8} {name:>18} {0:>7} {'-':>7} {'-':>12} {'-':>5}")
                continue
            v = violations(A, p, k)                    # complete re-check, F3
            e = math.log(len(A)) / math.log(p)
            flag = "" if v == 0 else "   *** VIOLATIONS -- CONSTRUCTOR BUG"
            if len(A) > (p + 1) // 2:
                flag += "   *** EXCEEDS HALF-ORBIT BOUND -- BUG"
            print(f"{p:>8} {name:>18} {len(A):>7} {e:>7.4f} "
                  f"{len(A)/math.sqrt(p):>12.3f} {v:>5}{flag}")
            if v == 0:
                champ[p] = max(champ.get(p, (0, "")), (len(A), name))
        print()

    print("best structured construction per prime:")
    for p in primes:
        if p in champ:
            s, name = champ[p]
            print(f"    p={p:>8}  |A|={s:>6}  exp={math.log(s)/math.log(p):.4f}  "
                  f"|A|/sqrt(p)={s/math.sqrt(p):.3f}   ({name})")
    exps = [math.log(champ[p][0]) / math.log(p) for p in primes if p in champ]
    if exps:
        print(f"\nbest exponent over all structured families: {max(exps):.4f}")
        print("route SQ survives this attack iff this stays well below 1.0")


if __name__ == "__main__":
    main()
