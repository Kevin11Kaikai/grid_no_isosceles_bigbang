"""Native lemmas for Q_SQ. Machine-checked against sq.py. No iso6 import.

Z[i] form: clockwise square-corner at b iff a + i c = (1+i) b.
"""
from __future__ import annotations

from sq import is_sq_free, rot90_pm, square_corners


def as_g(p):
    return (p[0], p[1])


def zi_clockwise(a, b, c):
    """a + i c == (1+i) b."""
    lhs = (a[0] - c[1], a[1] + c[0])
    rhs = (b[0] - b[1], b[0] + b[1])
    return lhs == rhs


def zi_counterclockwise(a, b, c):
    """Clockwise on the swapped legs: a + i c = (1+i)b after swapping a,c
    is the other orientation: a - i c = (1-i) b, i.e. c + i a = (1+i) b.
    """
    return zi_clockwise(c, b, a)


def is_square_corner_triple(b, a, c):
    """True iff {b,a,c} is a J1 square-corner with apex b."""
    w = (a[0] - b[0], a[1] - b[1])
    if w == (0, 0):
        return False
    v = (c[0] - b[0], c[1] - b[1])
    return v in rot90_pm(w)


def lemma_zi_iff_j1(n=12):
    """Every ordered triple in [n]^2: zi clockwise/ccw iff J1 apex b."""
    pts = [(x, y) for x in range(n) for y in range(n)]
    mismatches = 0
    checked = 0
    for b in pts:
        for a in pts:
            if a == b:
                continue
            for c in pts:
                if c == b or c == a:
                    continue
                checked += 1
                j1 = is_square_corner_triple(b, a, c)
                zi = zi_clockwise(a, b, c) or zi_counterclockwise(a, b, c)
                if j1 != zi:
                    mismatches += 1
    return {"n": n, "checked": checked, "mismatches": mismatches, "ok": mismatches == 0}


def full_row(n, y=0):
    return [(x, y) for x in range(n)]


def full_col(n, x=0):
    return [(x, y) for y in range(n)]


def lemma_one_row_free(ns=(8, 16, 32, 48)):
    rows = []
    for n in ns:
        S = full_row(n, 0)
        rows.append({"n": n, "kind": "row", "sq_free": is_sq_free(S), "|S|": len(S)})
        S = full_col(n, 0)
        rows.append({"n": n, "kind": "col", "sq_free": is_sq_free(S), "|S|": len(S)})
    return {"ok": all(r["sq_free"] for r in rows), "rows": rows}


def three_full_rows(n, y1, y2, y3):
    S = []
    for y in (y1, y2, y3):
        S.extend(full_row(n, y))
    return S


def lemma_two_full_rows_not_free(ns=(4, 8, 16, 24)):
    """Any two distinct full rows contain a classical square-corner.

    Witness: rows y and y+d, apex (x,y), w=(0,d), R_+(w)=(-d,0):
    {(x,y), (x,y+d), (x-d,y)} with x=d.
    """
    rows = []
    for n in ns:
        all_dirty = True
        witness = None
        for y1 in range(n):
            for y2 in range(y1 + 1, n):
                S = full_row(n, y1) + full_row(n, y2)
                free = is_sq_free(S)
                if free:
                    all_dirty = False
                elif witness is None:
                    d = y2 - y1
                    witness = {
                        "n": n,
                        "rows": (y1, y2),
                        "pts": [(d, y1), (d, y2), (0, y1)],
                        "j1": is_square_corner_triple((d, y1), (d, y2), (0, y1)),
                    }
        rows.append({"n": n, "ok": all_dirty, "witness": witness})
    return {"ok": all(r["ok"] for r in rows), "rows": rows}


def lemma_three_full_rows_not_free(n=16):
    """Any 3 distinct full rows contain a square-corner (they contain two full rows)."""
    hits = []
    ys = list(range(n))
    for i, y1 in enumerate(ys):
        for y2 in ys[i + 1 :]:
            for y3 in ys:
                if y3 == y1 or y3 == y2:
                    continue
                S = three_full_rows(n, y1, y2, y3)
                free = is_sq_free(S)
                hits.append({"rows": (y1, y2, y3), "sq_free": free, "|S|": len(S)})
    n_free = sum(1 for h in hits if h["sq_free"])
    return {
        "n": n,
        "triples_tested": len(hits),
        "n_sq_free": n_free,
        "ok": n_free == 0,
        "sample_bad": next((h for h in hits if not h["sq_free"]), None),
        "sample_free": next((h for h in hits if h["sq_free"]), None),
    }


def three_rows_analytic_witness(n, y1, y2, y3):
    """Construct the stencil point if it fits: apex (x,y1), w=(y3-y1, y2-y1)."""
    p = y3 - y1
    q = y2 - y1
    # need x, x+p, x-q in [0,n)
    # x in [max(0,q), min(n-1, n-1-p) ] if p>=0, etc.
    for x in range(n):
        xs = (x, x + p, x - q)
        if all(0 <= t < n for t in xs):
            b = (x, y1)
            a = (x + p, y1 + q)  # should be (x+p, y2)
            c = (x - q, y1 + p)  # should be (x-q, y3)
            return {"b": b, "a": a, "c": c, "fits": True, "j1": is_square_corner_triple(b, a, c)}
    return {"fits": False}
