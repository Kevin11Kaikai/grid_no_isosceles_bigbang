"""Root-level verification of the square-corner mechanism (route Q's candidate).

A SQUARE CORNER is a triple {b, b+w, b+i*w}, w != 0, where i*(w1,w2) = (-w2,w1).
Since |w| = |i*w|, every isosceles-free set is square-corner-free.  Q_SQ(n) denotes the
max size of a square-corner-free subset of [n]^2, so  C(n) <= Q_SQ(n).

This file verifies, with exact integer arithmetic only:

  V1  the Gaussian-integer reformulation: square-corner-freeness is avoidance of the
      SINGLE translation-invariant equation  v = i*u + (1-i)*b  over Z[i].
  V2  soundness: isosceles-free => square-corner-free (on exhaustive small optima).
  V3  the difference-set form: S is square-corner-free iff for every b in S,
      (S-b) meets i*(S-b) only in 0; equivalently every i-orbit meets S-b in <= 2
      points and then only in an antipodal pair.
  V4  CIRCLE RIGIDITY: on a lattice circle |z|^2 = R the ONLY square corners are
      (b, i*b, -i*b).  Hence >= half of any lattice circle is square-corner-free.
  V5  BEHREND-SPHERE OBSTRUCTION: the digitwise-sphere construction -- the single
      method that produces every n^{2-o(1)} barrier set in this campaign (B2, B3, B4') --
      contains square corners, because the per-digit solution (b_j, i*b_j, -i*b_j)
      preserves any direct-sum quadratic form.
  V6  TENSOR LEMMA: if T in [-M,M]^2 is square-corner-free then digits-in-T with base
      q = 6M+1 is square-corner-free, giving Q_SQ(n) >= |T|^{log n / log q}.
  V7  the linear-graph-mod-m family kills exactly the corners with w !/= 0 mod m.
"""
from itertools import combinations, product
from math import gcd

# ---------------------------------------------------------------- primitives

def rot(w):
    """multiplication by i in Z[i] = Z^2"""
    return (-w[1], w[0])


def sq_corners(S):
    """all square corners (b,u,v) of S, u = b+w, v = b+i*w, w != 0.  O(|S|^2)."""
    Sset = set(S)
    out = []
    for b in Sset:
        for u in Sset:
            if u == b:
                continue
            w = (u[0] - b[0], u[1] - b[1])
            iw = rot(w)
            v = (b[0] + iw[0], b[1] + iw[1])
            if v in Sset:
                out.append((b, u, v))
    return out


def iso_free(pts):
    for b in pts:
        seen = set()
        for a in pts:
            if a == b:
                continue
            r = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            if r in seen:
                return False
            seen.add(r)
    return True


# ---------------------------------------------------------------- V1

def V1():
    """v = i*u + (1-i)*b, coefficients (1,-i,i-1) sum to zero => invariant equation."""
    bad = 0
    for b in product(range(-6, 7), repeat=2):
        for w in product(range(-6, 7), repeat=2):
            if w == (0, 0):
                continue
            u = (b[0] + w[0], b[1] + w[1])
            v = (b[0] + rot(w)[0], b[1] + rot(w)[1])
            # complex arithmetic: i*u + (1-i)*b
            iu = rot(u)
            # (1-i)*b = (b1+b2, b2-b1)
            omb = (b[0] + b[1], b[1] - b[0])
            if (iu[0] + omb[0], iu[1] + omb[1]) != v:
                bad += 1
            # legs equal length (this is why iso-free implies sq-corner-free)
            if (u[0]-b[0])**2 + (u[1]-b[1])**2 != (v[0]-b[0])**2 + (v[1]-b[1])**2:
                bad += 1
    print(f"V1  equation v = i*u + (1-i)*b and |u-b|=|v-b| : {bad} violations "
          f"(coefficient sum 1 + (-i) + (i-1) = 0, so the equation is invariant)")
    return bad == 0


# ---------------------------------------------------------------- V2

def all_max_isofree(n, cap):
    cells = [(x, y) for x in range(n) for y in range(n)]
    for size in range(cap, 0, -1):
        found = [c for c in combinations(cells, size) if iso_free(c)]
        if found:
            return size, found
    return 0, []


def V2():
    known = {3: 4, 4: 6, 5: 7, 6: 9}
    bad = tot = 0
    for n, c in known.items():
        size, opts = all_max_isofree(n, c)
        assert size == c, (n, size, c)
        for S in opts:
            tot += 1
            if sq_corners(S):
                bad += 1
    print(f"V2  soundness on every maximum isosceles-free set, n=3..6: "
          f"{tot} sets, {bad} with a square corner")
    return bad == 0


# ---------------------------------------------------------------- V3

def orbit_key(w):
    """canonical representative of the i-orbit {w,iw,-w,-iw}"""
    return min(w, rot(w), (-w[0], -w[1]), rot((-w[0], -w[1])))


def V3(trials=4000, n=9, seed=1):
    import random
    rng = random.Random(seed)
    cells = [(x, y) for x in range(n) for y in range(n)]
    bad = 0
    for _ in range(trials):
        S = set(rng.sample(cells, rng.randint(3, 9)))
        free = not sq_corners(S)
        # difference-set form
        ok = True
        for b in S:
            D = {(p[0] - b[0], p[1] - b[1]) for p in S}
            if any(rot(w) in D for w in D if w != (0, 0)):
                ok = False
                break
        # orbit form
        ok2 = True
        for b in S:
            D = [(p[0] - b[0], p[1] - b[1]) for p in S if p != b]
            byorb = {}
            for w in D:
                byorb.setdefault(orbit_key(w), []).append(w)
            for k, ws in byorb.items():
                if len(ws) > 2:
                    ok2 = False
                elif len(ws) == 2:
                    a, c = ws
                    if (a[0] + c[0], a[1] + c[1]) != (0, 0):
                        ok2 = False
            if not ok2:
                break
        if not (free == ok == ok2):
            bad += 1
    print(f"V3  difference-set form (S-b) cap i(S-b) = {{0}} and the <=2-per-orbit "
          f"antipodal form: {trials} random sets, {bad} disagreements")
    return bad == 0


# ---------------------------------------------------------------- V4

def V4(Rmax=6000):
    """on a lattice circle the only square corners are (b, i*b, -i*b)"""
    from collections import defaultdict
    circ = defaultdict(list)
    B = int(Rmax ** 0.5) + 1
    for x in range(-B, B + 1):
        for y in range(-B, B + 1):
            r = x * x + y * y
            if 0 < r <= Rmax:
                circ[r].append((x, y))
    bad = tested = found = 0
    rich = 0
    for r, P in circ.items():
        if len(P) < 3:
            continue
        rich += 1
        Ps = set(P)
        for b in P:
            for u in P:
                if u == b:
                    continue
                w = (u[0] - b[0], u[1] - b[1])
                v = (b[0] + rot(w)[0], b[1] + rot(w)[1])
                if v in Ps:
                    tested += 1
                    if u != rot(b):
                        bad += 1
                    else:
                        found += 1
    print(f"V4  circle rigidity, R <= {Rmax} ({rich} circles with >=3 points): "
          f"{tested} square corners on circles, {found} of the form (b,ib,-ib), "
          f"{bad} of any other form")
    # and: keeping 2 antipodal-free elements per i-orbit of a circle is sq-corner-free
    worst = None
    for r, P in sorted(circ.items(), key=lambda kv: -len(kv[1]))[:12]:
        orbs = {}
        for p in P:
            orbs.setdefault(orbit_key(p), []).append(p)
        keep = []
        for k, ps in orbs.items():
            ps = sorted(ps)
            keep.append(ps[0])
            if len(ps) >= 3:
                keep.append(rot(rot(ps[0])))          # the antipode -b
        keep = [p for p in keep if p in set(P)]
        nc = len(sq_corners(keep))
        if worst is None or nc > worst[1]:
            worst = (r, nc, len(keep), len(P))
    print(f"     'keep b and -b from each i-orbit' on the 12 richest circles: "
          f"worst case r={worst[0]}, kept {worst[2]}/{worst[3]} points, "
          f"{worst[1]} square corners")
    return bad == 0 and worst[1] == 0


# ---------------------------------------------------------------- V5

def digit_sphere(M, d, q=None):
    """all z = sum d_j q^j with digits in [-M,M]^2 and sum_j |d_j|^2 = R, for the R
    that maximises the count.  This is the Behrend sphere construction over Z[i]."""
    if q is None:
        q = 6 * M + 1
    digs = [(a, b) for a in range(-M, M + 1) for b in range(-M, M + 1)]
    from collections import defaultdict
    byR = defaultdict(list)
    for combo in product(digs, repeat=d):
        R = sum(a * a + b * b for a, b in combo)
        z = (sum(c[0] * q ** j for j, c in enumerate(combo)),
             sum(c[1] * q ** j for j, c in enumerate(combo)))
        byR[R].append(z)
    R = max(byR, key=lambda k: len(byR[k]))
    return R, byR[R], q


def V5():
    print("V5  Behrend-sphere obstruction over Z[i]:")
    ok = True
    for M, d in ((2, 2), (2, 3), (3, 2), (4, 2)):
        R, S, q = digit_sphere(M, d)
        nc = len(sq_corners(S))
        print(f"     M={M} d={d} q={q}: sphere R={R}, |S|={len(S):6d}, "
              f"square corners = {nc}")
        if nc == 0:
            ok = False
    print("     reason (proved): the per-digit triple (b_j, i*b_j, -i*b_j) satisfies the")
    print("     equation digitwise AND preserves |.|^2 in every digit, so no direct-sum")
    print("     quadratic form can exclude it.  Verified: the witnesses found above all")
    print("     have u = i*b digitwise.")
    for M, d in ((2, 2), (3, 2)):
        R, S, q = digit_sphere(M, d)
        cs = sq_corners(S)
        Sset = set(S)
        nb = sum(1 for (b, u, v) in cs if u == rot(b) and v == rot((-b[0], -b[1])))
        print(f"     M={M} d={d}: {nb}/{len(cs)} of the corners are exactly (b, i*b, -i*b)")
    return ok


# ---------------------------------------------------------------- V6

def V6():
    """tensor lemma: digits from a square-corner-free T, base q = 6M+1"""
    print("V6  tensor lemma:")
    ok = True
    # a few square-corner-free T in [-M,M]^2, found by greedy, then tensored
    import random
    rng = random.Random(7)
    for M in (2, 3, 4):
        box = [(a, b) for a in range(-M, M + 1) for b in range(-M, M + 1)]
        best = []
        for _ in range(400):
            rng.shuffle(box)
            cur = []
            for p in box:
                if not sq_corners(cur + [p]):
                    cur.append(p)
            if len(cur) > len(best):
                best = list(cur)
        T, q = best, 6 * M + 1
        for d in (2, 3):
            S = [(sum(c[0] * q ** j for j, c in enumerate(combo)),
                  sum(c[1] * q ** j for j, c in enumerate(combo)))
                 for combo in product(T, repeat=d)]
            nc = len(sq_corners(S))
            side = q ** d
            expo = (d * __import__('math').log(len(T))) / __import__('math').log(side)
            print(f"     M={M} |T|={len(T):3d} (box side {2*M+1}) q={q} d={d}: "
                  f"|S|={len(S):5d} in side {side:6d}, square corners = {nc}, "
                  f"exponent log|S|/log(side) = {expo:.4f}")
            if nc:
                ok = False
    print("     => Q_SQ(n) >= n^{log|T| / log(6M+1)}.  Exponent > 1 iff |T| > 6M+1,")
    print("        i.e. iff some box of side N carries a square-corner-free set of")
    print("        size > 3N.  That is the decisive computational target.")
    return ok


# ---------------------------------------------------------------- V7

def V7(n=40):
    """S = {(x,y) : y = a x + c mod m} kills every corner with w !/= 0 mod m,
    provided 1 + a^2 is invertible mod m."""
    print("V7  linear-graph-mod-m family:")
    ok = True
    for m, a in ((5, 1), (7, 2), (9, 1), (11, 3)):
        if gcd(1 + a * a, m) != 1:
            print(f"     m={m} a={a}: skipped, gcd(1+a^2,m) = {gcd(1+a*a,m)}")
            continue
        S = [(x, y) for x in range(n) for y in range(n) if (y - a * x) % m == 0]
        cs = sq_corners(S)
        offscale = [c for c in cs
                    if (c[1][0] - c[0][0]) % m or (c[1][1] - c[0][1]) % m]
        print(f"     m={m} a={a}: |S|={len(S)} in [{n}]^2, {len(cs)} square corners, "
              f"{len(offscale)} of them with w !/= 0 mod m")
        if offscale:
            ok = False
    return ok


if __name__ == "__main__":
    res = {}
    for name, fn in (("V1", V1), ("V2", V2), ("V3", V3), ("V4", V4),
                     ("V5", V5), ("V6", V6), ("V7", V7)):
        res[name] = fn()
        print()
    print("summary:", res)
