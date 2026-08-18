"""Joint constraints implied by RF1, and the B4′ gate.

J1 (right-isosceles / rotate-90 stencil).
  RF1: isosceles-free ⇒ no apex b with two distinct legs of equal squared length.
  In particular, no u ≠ 0 and R = rotate ±90° with {b, b+u, b+R(u)} ⊂ S.
  This is a two-leg constraint, not a fifth line-kill.

A set 'fires' J1 if it contains such a stencil.
"""
from __future__ import annotations

from collections import Counter

from census import is_q4_survivor, is_rotate90, rotate90_pm
from fourfold import build_S, greedy_3ap_free, is_3ap_free
from iso import iso_triples


def rot90_stencils(pts):
    """Occurrences of {b, b+u, b+R(u)} with R = ±90°, u ≠ 0.

    Dedup by frozenset of the three points.
    """
    P = set(map(tuple, pts))
    seen = set()
    hits = []
    for b in P:
        bx, by = b
        for a in P:
            if a == b:
                continue
            u = (a[0] - bx, a[1] - by)
            if u == (0, 0):
                continue
            for Ru in rotate90_pm(u):
                c = (bx + Ru[0], by + Ru[1])
                if c in P and c != a and c != b:
                    tri = frozenset((b, a, c))
                    if tri in seen:
                        continue
                    seen.add(tri)
                    v = Ru
                    hits.append(
                        {
                            "apex": b,
                            "u": u,
                            "v": v,
                            "pts": tri,
                            "q4_survivor": is_q4_survivor(u, v),
                            "rot90": True,
                        }
                    )
    return hits


def fires_J1(pts):
    return len(rot90_stencils(pts)) > 0


def project(pts, e):
    ex, ey = e
    return [ex * x + ey * y for x, y in pts]


def filter_3ap_free_projection(pts, e, rng):
    """Keep a subset whose projection along e is 3-AP-free (greedy on fibers).

    Not used as a 'power-saving extra line-kill'; only for the B4′ diagnostic:
    can we keep a J1 stencil after forcing one more 3-AP-free projection?
    """
    from collections import defaultdict

    fibers = defaultdict(list)
    ex, ey = e
    for p in pts:
        fibers[ex * p[0] + ey * p[1]].append(p)
    keys = greedy_3ap_free(list(fibers.keys()), rng)
    kept = []
    for k in keys:
        kept.extend(fibers[k])
    return kept


def rot90_q4_survivor_family(pmax=12):
    """Small (p,q) where (u, R90(u)) is never P1–P3 on the four Q4 forms."""
    fam = []
    for p in range(-pmax, pmax + 1):
        for q in range(-pmax, pmax + 1):
            if (p, q) == (0, 0):
                continue
            u = (p, q)
            for v in rotate90_pm(u):
                if is_q4_survivor(u, v):
                    fam.append((u, v))
    # dedup unordered
    seen = set()
    out = []
    for u, v in fam:
        key = tuple(sorted((u, v)))
        if key in seen:
            continue
        seen.add(key)
        out.append((u, v))
    return out


def embed_rot90_fourfold(p, q, n=None):
    """Three-point four-fold realizing the rotate-90 stencil (p,q), R90.

    Apex at a shift so all points lie in [n]^2. Projections are 3-AP-free
    precisely when (u, R90(u)) is a Q4 survivor.
    """
    u = (p, q)
    v = (-q, p)
    xs = [0, u[0], v[0]]
    ys = [0, u[1], v[1]]
    minx, miny = min(xs), min(ys)
    pts = [(x - minx, y - miny) for x, y in zip(xs, ys)]
    need = max(max(x for x, _y in pts), max(y for _x, y in pts)) + 1
    if n is None:
        n = need
    if need > n:
        return None
    A = sorted({x for x, _y in pts})
    B = sorted({y for _x, y in pts})
    W = sorted({x + y for x, y in pts})
    Z = sorted({x - y for x, y in pts})
    return {
        "n": n,
        "kind": "J1_embed",
        "u": u,
        "v": v,
        "|A|": len(A),
        "|B|": len(B),
        "|W|": len(W),
        "|Z|": len(Z),
        "|S|": 3,
        "A": A,
        "B": B,
        "W": W,
        "Z": Z,
        "set": pts,
        "A_3ap_free": is_3ap_free(A),
        "B_3ap_free": is_3ap_free(B),
        "W_3ap_free": is_3ap_free(W),
        "Z_3ap_free": is_3ap_free(Z),
    }


def extra_linekill_subset(n, pts, e, rng):
    """Maximal subset with 3-AP-free projection along e, plus Q4 already assumed.

    Implementation: take values of φ_e that form a greedy 3-AP-free set.
    """
    return filter_3ap_free_projection(pts, e, rng)


def J1_holds_if_q4_plus_extra(pts, extra_forms):
    """True iff every rot90 stencil is P1–P3 on at least one extra form.

    If True, J1 on this set is explained by extra 3-AP-free projections
    (B4′: dead as a power-saving route). If False, a rot90 stencil survives
    all extra forms — J1 is not a restatement of those line-kills.
    """
    st = rot90_stencils(pts)
    if not st:
        return True, []
    survivors = []
    for h in st:
        ux, uy = h["u"]
        vx, vy = h["v"]
        killed = False
        for name, psi in extra_forms:
            U, V = psi(ux, uy), psi(vx, vy)
            if U == V != 0 or (U + 2 * V == 0 and U != 0) or (2 * U + V == 0 and V != 0):
                killed = True
                break
        if not killed:
            survivors.append(h)
    return len(survivors) == 0, survivors
