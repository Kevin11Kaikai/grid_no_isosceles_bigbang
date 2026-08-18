"""Classify isosceles (u,v) against P1–P3 on the four Q4 forms.

Convention (same as Q's patterns.py, reimplemented here):
  For an isosceles triple with apex b and legs to a and c,
    u = b - a,  v = c - b
  so a --u--> b --v--> c and |u|^2 = |v|^2.
  For a linear form ψ, U = ψ(u), V = ψ(v).
    P1: U = V ≠ 0
    P2: U + 2V = 0, U ≠ 0
    P3: 2U + V = 0, V ≠ 0
  A 3-AP-free projection kills P1+P2+P3 on that form.
  Q4 line-kill in direction e kills only P1.
"""
from __future__ import annotations

Q4_FORMS = (
    ("x", lambda dx, dy: dx),
    ("y", lambda dx, dy: dy),
    ("x+y", lambda dx, dy: dx + dy),
    ("x-y", lambda dx, dy: dx - dy),
)


def classify_uv(u, v):
    ux, uy = u
    vx, vy = v
    hits = []
    for name, psi in Q4_FORMS:
        U, V = psi(ux, uy), psi(vx, vy)
        if U == V != 0:
            hits.append((name, "P1"))
        if U + 2 * V == 0 and U != 0:
            hits.append((name, "P2"))
        if 2 * U + V == 0 and V != 0:
            hits.append((name, "P3"))
    return hits


def is_q4_survivor(u, v):
    return len(classify_uv(u, v)) == 0


def canon_uv(u, v):
    """Unordered pair of legs as a hashable key, plus ordered (u,v)."""
    a, c = (u, v) if u <= v else (v, u)
    return (a, c)


def rotate90_pm(u):
    ux, uy = u
    return ((-uy, ux), (uy, -ux))


def is_rotate90(u, v):
    r, s = rotate90_pm(u)
    return v == r or v == s


def census_triples(pts):
    """From iso triples (apex b, two others a,c): emit (u,v) records.

    We report both orderings of the two legs as (u,v)=(b-a, c-b) only when
    we fix a < c lexicographically so each unordered {a,c} is once.
    """
    from iso import iso_triples

    rows = []
    for b, a, c, r2 in iso_triples(pts):
        if a > c:
            a, c = c, a
        u = (b[0] - a[0], b[1] - a[1])
        v = (c[0] - b[0], c[1] - b[1])
        hits = classify_uv(u, v)
        rows.append(
            {
                "apex": b,
                "a": a,
                "c": c,
                "u": u,
                "v": v,
                "r2": r2,
                "hits": hits,
                "survivor": len(hits) == 0,
                "rot90": is_rotate90(u, v),
                "base": (c[0] - a[0], c[1] - a[1]),
            }
        )
    return rows


def summarize(rows):
    from collections import Counter

    n = len(rows)
    n_surv = sum(1 for r in rows if r["survivor"])
    n_killed = n - n_surv
    n_rot = sum(1 for r in rows if r["rot90"])
    n_rot_surv = sum(1 for r in rows if r["rot90"] and r["survivor"])
    uv_surv = Counter()
    base_surv = Counter()
    for r in rows:
        if r["survivor"]:
            uv_surv[canon_uv(r["u"], r["v"])] += 1
            base_surv[r["base"]] += 1
    return {
        "n_triples": n,
        "n_killed_by_q4_forms": n_killed,
        "n_survivors": n_surv,
        "n_rot90": n_rot,
        "n_rot90_survivors": n_rot_surv,
        "top_survivor_uv": uv_surv.most_common(20),
        "top_survivor_base": base_surv.most_common(15),
    }
