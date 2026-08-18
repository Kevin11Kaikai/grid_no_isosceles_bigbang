"""Q_SQ power attempt 3: union of row/column forbidden cells; two-row verticals.

Not G≤mn, not a repair of Method A (one heavy row). No iso6 import.
Kill-switch: nothing implying O(n) or O(n^{1.2}).
"""
from __future__ import annotations

from attempt2 import heavy_row_forbidden, row_sizes
from sq import is_sq_free


def col_sizes(pts, n):
    c = [0] * n
    rows_in_col = [[] for _ in range(n)]
    for x, y in pts:
        if 0 <= x < n:
            c[x] += 1
        if 0 <= x < n and 0 <= y < n:
            rows_in_col[x].append(y)
    return c, rows_in_col


def heavy_col_forbidden(ys, x, n):
    """Vertical pairs in column x forbid cells in the same row as the apex."""
    Y = set(ys)
    F = set()
    for y in Y:
        for yp in Y:
            if yp == y:
                continue
            d = yp - y
            for xx in (x + d, x - d):
                if 0 <= xx < n:
                    F.add((xx, y))
    return F


def union_row_forbidden(pts, n):
    _r, cols = row_sizes(pts, n)
    F = set()
    n_active = 0
    for y in range(n):
        xs = cols[y]
        if len(xs) >= 2:
            n_active += 1
            F |= heavy_row_forbidden(xs, y, n)
    S = set(map(tuple, pts))
    return F, n_active, len(F & S)


def union_col_forbidden(pts, n):
    _c, rows_in_col = col_sizes(pts, n)
    F = set()
    n_active = 0
    for x in range(n):
        ys = rows_in_col[x]
        if len(ys) >= 2:
            n_active += 1
            F |= heavy_col_forbidden(ys, x, n)
    S = set(map(tuple, pts))
    return F, n_active, len(F & S)


def two_row_vertical_forbidden(xs, y, xs2, y2, n):
    """Shared columns of two rows: vertical w=(0,d) forbids (x±d, y) and (x±d, y2)."""
    d = y2 - y
    I = set(xs) & set(xs2)
    F = set()
    for x in I:
        for xx in (x + d, x - d):
            if 0 <= xx < n:
                F.add((xx, y))
                F.add((xx, y2))
    return F, I


def union_two_row_forbidden(pts, n):
    _r, cols = row_sizes(pts, n)
    occupied = [y for y in range(n) if cols[y]]
    F = set()
    n_pairs = 0
    n_pairs_shared = 0
    max_shared = 0
    S = set(map(tuple, pts))
    for i, y in enumerate(occupied):
        for y2 in occupied[i + 1 :]:
            n_pairs += 1
            Fy, I = two_row_vertical_forbidden(cols[y], y, cols[y2], y2, n)
            if I:
                n_pairs_shared += 1
                max_shared = max(max_shared, len(I))
                F |= Fy
    return F, n_pairs, n_pairs_shared, max_shared, len(F & S)


def method_d_report(name, n, pts):
    pts = [tuple(p) for p in pts]
    m = len(pts)
    Fr, n_act_r, hit_r = union_row_forbidden(pts, n)
    Fc, n_act_c, hit_c = union_col_forbidden(pts, n)
    F2, n_pairs, n_shared, max_I, hit_2 = union_two_row_forbidden(pts, n)
    F_all = Fr | Fc | F2
    n2 = n * n
    leftover = n2 - len(F_all)
    # A power would need leftover = O(n^{2-ε}) uniformly. Peeling kill-switch:
    # leftover ≥ m is necessary (S itself avoids F if sq-free, but S ⊂ grid).
    return {
        "name": name,
        "n": n,
        "m": m,
        "n_active_rows": n_act_r,
        "n_active_cols": n_act_c,
        "|F_rows|": len(Fr),
        "|F_cols|": len(Fc),
        "|F_tworow|": len(F2),
        "|F_union|": len(F_all),
        "n^2 - |F|": leftover,
        "leftover / n^2": leftover / n2 if n2 else 0.0,
        "S_hits_F_rows": hit_r,
        "S_hits_F_cols": hit_c,
        "S_hits_F_tworow": hit_2,
        "n_row_pairs": n_pairs,
        "n_row_pairs_shared_col": n_shared,
        "max_|A∩B|": max_I,
        "leftover_le_n32": leftover <= n ** 1.5 + 1e-9,
        "implies_O(n)": leftover <= n + 1e-9,
        "sq_free": is_sq_free(pts) if m <= 5000 else None,
    }
