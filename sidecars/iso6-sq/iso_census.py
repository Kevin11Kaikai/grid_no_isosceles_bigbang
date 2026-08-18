"""Classify RF1 isosceles triples: J1 (right), collinear 3-AP, other.

Does not import iso6 / iso6-joint. Exact integer arithmetic.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from sq import rot90_pm


def iso_triples(pts):
    """List (b, a, c, r2) with a != c, |a-b|^2 = |c-b|^2 = r2 > 0."""
    P = [tuple(p) for p in pts]
    out = []
    for i, b in enumerate(P):
        by_r = {}
        for j, a in enumerate(P):
            if j == i:
                continue
            r2 = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            by_r.setdefault(r2, []).append(a)
        for r2, group in by_r.items():
            if len(group) < 2:
                continue
            for ia in range(len(group)):
                for ic in range(ia + 1, len(group)):
                    out.append((b, group[ia], group[ic], r2))
    return out


def classify_one(b, a, c, r2):
    """Legs from apex b are u=a-b and v=c-b (both outgoing)."""
    u = (a[0] - b[0], a[1] - b[1])
    v = (c[0] - b[0], c[1] - b[1])
    dot = u[0] * v[0] + u[1] * v[1]
    cross = u[0] * v[1] - u[1] * v[0]
    ru, su = rot90_pm(u)
    rot90 = v == ru or v == su
    ap3 = v == (-u[0], -u[1])
    collinear = cross == 0
    return {
        "apex": b,
        "a": a,
        "c": c,
        "u": u,
        "v": v,
        "r2": r2,
        "dot": dot,
        "cross": cross,
        "rot90": rot90,
        "ap3": ap3,
        "collinear": collinear,
        "other": (not rot90) and (not collinear),
    }


def canon_uv(u, v):
    return tuple(sorted((tuple(u), tuple(v))))


def slope_key(u):
    """Reduced slope of a vector; vertical is ('inf', sign)."""
    ux, uy = u
    if ux == 0:
        return ("inf", 1 if uy > 0 else -1 if uy < 0 else 0)
    from math import gcd

    g = gcd(abs(ux), abs(uy))
    sx, sy = ux // g, uy // g
    if sx < 0:
        sx, sy = -sx, -sy
    return (sx, sy)


def census_set(name, n, pts, cap_triples=None):
    pts = [tuple(p) for p in pts]
    m = len(pts)
    rows = []
    for rec in iso_triples(pts):
        rows.append(classify_one(*rec))
        if cap_triples is not None and len(rows) >= cap_triples:
            break
    n_tri = len(rows)
    n_rot = sum(1 for r in rows if r["rot90"])
    n_ap3 = sum(1 for r in rows if r["ap3"])
    n_col = sum(1 for r in rows if r["collinear"])
    n_oth = sum(1 for r in rows if r["other"])
    uv_other = Counter()
    r2_other = Counter()
    slope_pairs = Counter()
    dots = Counter()
    for r in rows:
        if r["other"]:
            uv_other[canon_uv(r["u"], r["v"])] += 1
            r2_other[r["r2"]] += 1
            dots[r["dot"]] += 1
            slope_pairs[(slope_key(r["u"]), slope_key(r["v"]))] += 1
    return {
        "name": name,
        "n": n,
        "m": m,
        "n_triples": n_tri,
        "n_rot90_J1": n_rot,
        "n_ap3_collinear": n_ap3,
        "n_collinear": n_col,
        "n_other": n_oth,
        "iso_free": n_tri == 0,
        "sq_free_implies_n_rot90_0": n_rot == 0,
        "top_other_uv": uv_other.most_common(12),
        "top_other_r2": r2_other.most_common(8),
        "top_other_dot": dots.most_common(8),
        "top_other_slopes": slope_pairs.most_common(8),
        "capped": cap_triples is not None and n_tri >= cap_triples,
    }
