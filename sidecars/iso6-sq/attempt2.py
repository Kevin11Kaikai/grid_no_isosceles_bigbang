"""Q_SQ power attempt 2: heavy rows, A_w energy. Not G≤mn. No iso6 import."""
from __future__ import annotations

import math
from collections import defaultdict

from peel import build_Am
from sq import is_sq_free, rot90_pm


def row_sizes(pts, n):
    r = [0] * n
    cols = [[] for _ in range(n)]
    for x, y in pts:
        if 0 <= y < n:
            r[y] += 1
        if 0 <= y < n and 0 <= x < n:
            cols[y].append(x)
    return r, cols


def heavy_row_forbidden(xs, y, n):
    """F = cells forbidden by horizontal pairs on row y with x-set xs.

    Apex (x,y), partner (x+d,y) ⇒ third (x, y±d).
    """
    X = set(xs)
    F = set()
    for x in X:
        for xp in X:
            if xp == x:
                continue
            d = xp - x
            for yy in (y + d, y - d):
                if 0 <= yy < n:
                    F.add((x, yy))
    return F


def method_a_report(name, n, pts):
    pts = [tuple(p) for p in pts]
    r, cols = row_sizes(pts, n)
    m = len(pts)
    thresh = math.sqrt(n)
    heavy = [(y, r[y]) for y in range(n) if r[y] > thresh]
    max_r = max(r) if r else 0
    light_bound = n * thresh  # if all rows light: m ≤ n^{3/2}
    F_union = set()
    per_heavy = []
    for y, ry in heavy:
        F = heavy_row_forbidden(cols[y], y, n)
        F_union |= F
        # F lives in the r columns of the heavy row
        ncols = len(set(cols[y]))
        per_heavy.append(
            {
                "y": y,
                "r": ry,
                "|F|": len(F),
                "r^2": ry * ry,
                "r*n": ry * n,
                "n^2": n * n,
                "ncols": ncols,
                "|F|<=r*n": len(F) <= ry * n,
            }
        )
    return {
        "name": name,
        "n": n,
        "m": m,
        "max_r": max_r,
        "n_heavy_rows": len(heavy),
        "sqrt_n": thresh,
        "all_light": len(heavy) == 0,
        "light_implies_m_le_n32": m <= n * thresh + 1e-9,
        "m_le_n32": m <= n ** 1.5 + 1e-9,
        "|F_union|": len(F_union),
        "n^2 - |F|": n * n - len(F_union),
        "per_heavy": per_heavy[:8],
        "sq_free": is_sq_free(pts) if m <= 5000 else None,
    }


def difference_apexes(pts):
    """A_w = {b in S: b+w in S}."""
    P = [tuple(p) for p in pts]
    S = set(P)
    A = defaultdict(list)
    for b in P:
        bx, by = b
        for a in P:
            if a == b:
                continue
            w = (a[0] - bx, a[1] - by)
            A[w].append(b)
    return S, A


def method_b_report(name, n, pts):
    pts = [tuple(p) for p in pts]
    m = len(pts)
    S, A = difference_apexes(pts)
    sum_A = sum(len(v) for v in A.values())
    sum_A2 = sum(len(v) ** 2 for v in A.values())
    n_w = len(A)
    pairing_ok = True
    pairing_fail = 0
    max_pair_sum = 0
    for w, apexes in A.items():
        Aw = set(map(tuple, apexes))
        for Rw in rot90_pm(w):
            shifted = {(p[0] + Rw[0], p[1] + Rw[1]) for p in Aw}
            if shifted & S:
                pairing_ok = False
                pairing_fail += 1
            Ar = set(A.get(Rw, ()))
            max_pair_sum = max(max_pair_sum, len(Aw) + len(Ar))
            if len(Aw) + len(Ar) > m + 0:
                pairing_ok = False
    # CS: (sum |A_w|)^2 ≤ n_w * sum |A_w|^2
    cs_ok = sum_A ** 2 <= n_w * sum_A2 + 1e-6 if n_w else True
    # naive from pairing: sum |A| ≤ 2m * (#orbits) ≤ 2m * n_w
    # m(m-1)=sum|A| ≤ 2 m n_w ≤ 2 m * (2n-1)^2  ⇒ m = O(n^2)
    bound_n2 = 2 * m * (2 * n) ** 2
    return {
        "name": name,
        "n": n,
        "m": m,
        "sum_|A_w|": sum_A,
        "m(m-1)": m * (m - 1),
        "identity": sum_A == m * (m - 1),
        "n_w": n_w,
        "sum_|A_w|^2": sum_A2,
        "cs_ok": cs_ok,
        "pairing_Aw_disjoint_from_S_minus_Rw": pairing_fail == 0,
        "max_|Aw|+|A_Rw|": max_pair_sum,
        "max_pair_le_m": max_pair_sum <= m,
        "trivial_from_nw": "m=O(n^2) via sum|A|≤2m n_w and n_w≤O(n^2)",
        "implies_O(n)": False,  # we refuse this
        "sq_free": is_sq_free(pts) if m <= 4000 else None,
    }


def method_c_decision():
    """IRT is a+ic=(1+i)b, a rotation, not a point-line incidence.

    Axis lines: k=2n, I=m, ST is tautological.
    Circles centred at S, one per radius: k is huge (Θ(m n^2) possible), ST
    does not cap m below n^2.
    No small explicit line set was found whose incidences equal IRT count.
    """
    return {
        "st_applied": False,
        "reason": "no honest point-line system whose incidences dominate IRTs; skip",
    }
