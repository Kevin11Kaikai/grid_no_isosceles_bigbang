"""J2 hunt: non-right RF1 stencils on four-fold leftovers.

Not a fifth line-kill. B4′ still applies to any bounded extra-projection list.
Does not import iso6 / iso6-sq.
"""
from __future__ import annotations

from collections import Counter

from census import classify_uv, is_q4_survivor, is_rotate90
from iso import iso_triples


def classify_one(b, a, c, r2):
    u_out = (a[0] - b[0], a[1] - b[1])
    v_out = (c[0] - b[0], c[1] - b[1])
    # census.py walk convention a --u--> b --v--> c with a < c lex
    aa, cc = (a, c) if a <= c else (c, a)
    u = (b[0] - aa[0], b[1] - aa[1])
    v = (cc[0] - b[0], cc[1] - b[1])
    cross = u_out[0] * v_out[1] - u_out[1] * v_out[0]
    ap3 = v_out == (-u_out[0], -u_out[1])
    rot90 = is_rotate90(u, v) or is_rotate90(u_out, v_out)
    hits = classify_uv(u, v)
    return {
        "apex": b,
        "a": aa,
        "c": cc,
        "u": u,
        "v": v,
        "u_out": u_out,
        "v_out": v_out,
        "r2": r2,
        "dot_out": u_out[0] * v_out[0] + u_out[1] * v_out[1],
        "cross": cross,
        "rot90": rot90,
        "ap3": ap3,
        "collinear": cross == 0,
        "q4_hits": hits,
        "q4_survivor": len(hits) == 0,
        "other": (not rot90) and (not ap3),
    }


def canon_uv(u, v):
    return tuple(sorted((tuple(u), tuple(v))))


def census_j2(name, n, pts):
    rows = [classify_one(*t) for t in iso_triples(pts)]
    n_tri = len(rows)
    n_rot = sum(1 for r in rows if r["rot90"])
    n_ap3 = sum(1 for r in rows if r["ap3"])
    n_oth = sum(1 for r in rows if r["other"])
    n_oth_surv = sum(1 for r in rows if r["other"] and r["q4_survivor"])
    n_killed = sum(1 for r in rows if not r["q4_survivor"])
    uv_oth = Counter()
    r2_oth = Counter()
    for r in rows:
        if r["other"] and r["q4_survivor"]:
            uv_oth[canon_uv(r["u_out"], r["v_out"])] += 1
            r2_oth[r["r2"]] += 1
    return {
        "name": name,
        "n": n,
        "m": len(pts),
        "n_triples": n_tri,
        "n_killed_by_q4_forms": n_killed,
        "n_rot90_J1": n_rot,
        "n_ap3": n_ap3,
        "n_other": n_oth,
        "n_other_q4_survivors": n_oth_surv,
        "top_other_surv_uv": uv_oth.most_common(15),
        "top_other_surv_r2": r2_oth.most_common(8),
        "fires_J1": n_rot > 0,
        "fires_ap3": n_ap3 > 0,
        "fires_other": n_oth > 0,
    }
