"""Try to build Case A sets with large max_dia(S*): one heavy symmetric
diagonal plus many a*-pairs. If this works with max_dia > sqrt(n), A1's
hypothesis is not always true.
"""
from __future__ import annotations

import os
import random

from q4 import FourDir, greedy_from, verify
from lemma3_search import overlap_stats, sigma

HERE = os.path.dirname(os.path.abspath(__file__))


def behrend_like(m):
    """Small 3-AP-free subset of {1,...,m}, greedy."""
    s = []
    for x in range(1, m + 1):
        ok = True
        ss = set(s)
        for a in s:
            b = 2 * x - a
            if b in ss:
                ok = False
                break
        if ok:
            s.append(x)
    return s


def try_heavy_plus_pairs(n, t_target, a, rng):
    """Put a symmetric 3-AP-free set of 2t points on one diagonal, then pairs."""
    # choose diagonal d=0 (x=y) if a even enough; pick d so points exist
    # points: x-y = d, x+y = a +/- delta
    deltas = behrend_like(n // 2)
    # need {+/- deltas} 3-AP-free as a whole; take smallest t_target
    chosen = []
    for delta in deltas:
        trial = chosen + [delta]
        vals = sorted([-x for x in trial] + trial)
        # shift by a: anti-values a+v
        A = [a + v for v in vals]
        if min(A) < 0 or max(A) > 2 * n - 2:
            continue
        ok = True
        ss = set(A)
        for i, x in enumerate(A):
            for y in A[i + 1 :]:
                mid = (x + y) // 2
                if mid in ss:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            chosen = trial
        if len(chosen) >= t_target:
            break
    if len(chosen) < 2:
        return None, "tiny_delta"
    # find a diagonal d that realizes all these points in-grid
    d_ok = None
    for d in range(1 - n, n):
        good = True
        pts = []
        for v in [-x for x in chosen] + chosen:
            alpha = a + v
            if (alpha + d) % 2:
                good = False
                break
            x = (alpha + d) // 2
            y = (alpha - d) // 2
            if not (0 <= x < n and 0 <= y < n):
                good = False
                break
            pts.append((x, y))
        if good:
            d_ok = d
            heavy = pts
            break
    if d_ok is None:
        return None, "no_diag"
    st = FourDir(n)
    for p in heavy:
        ks = st.can_add(*p)
        if ks is None:
            return None, "heavy_infeas"
        st.push(*p, ks)
    # add as many a*-pairs as possible
    candidates = []
    seen = set()
    for x in range(n):
        for y in range(n):
            if x + y == a:
                continue
            sx, sy = a - y, a - x
            if not (0 <= sx < n and 0 <= sy < n):
                continue
            if (sx, sy) == (x, y):
                continue
            key = tuple(sorted(((x, y), (sx, sy))))
            if key in seen:
                continue
            seen.add(key)
            candidates.append(key)
    rng.shuffle(candidates)
    for p, q in candidates:
        if p in st.pts or q in st.pts:
            continue
        ks = st.can_add(*p)
        if ks is None:
            continue
        rec1 = st.push(*p, ks)
        ks2 = st.can_add(*q)
        if ks2 is None:
            st.pop(rec1)
            continue
        st.push(*q, ks2)
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    for x, y in cells:
        ks = st.can_add(x, y)
        if ks is not None:
            st.add(x, y, ks)
    pts = list(st.pts)
    assert verify(n, pts)
    stats = overlap_stats(n, pts)
    # max_dia of S*
    star = {p for p in pts if sigma(stats["a_star"], *p) in pts and sigma(stats["a_star"], *p) != p} if stats["a_star"] is not None else set()
    from collections import defaultdict
    dia = defaultdict(int)
    for x, y in star:
        dia[x - y] += 1
    stats["max_dia_star"] = max(dia.values()) if dia else 0
    row = defaultdict(int)
    col = defaultdict(int)
    ant = defaultdict(int)
    for x, y in star:
        row[y] += 1
        col[x] += 1
        ant[x + y] += 1
    stats["max_row_star"] = max(row.values()) if row else 0
    stats["max_col_star"] = max(col.values()) if col else 0
    stats["max_ant_star"] = max(ant.values()) if ant else 0
    stats["n_row_star"] = len(row)
    stats["heavy_t"] = len(chosen)
    stats["heavy_placed"] = len(heavy)
    return stats, "ok"


def main():
    rng = random.Random(0)
    for n in (16, 32, 48, 81):
        a = n - 1  # central anti-diagonal often works
        sqrtn = n ** 0.5
        for t_target in (2, 3, 4, max(3, int(sqrtn) + 1), max(4, int(n ** 0.6))):
            st, why = try_heavy_plus_pairs(n, t_target, a, rng)
            if st is None:
                print(f"n={n:3d} t~{t_target:3d} FAIL {why}", flush=True)
                continue
            print(
                f"n={n:3d} t_target={t_target:3d} heavy_t={st['heavy_t']:2d} "
                f"|S|={st['|S|']:4d} max_r={st['max_r']:3d} |S*|={st['|S_star|']:4d} "
                f"max_dia*={st['max_dia_star']:2d} max_row*={st['max_row_star']:2d} "
                f"max_ant*={st['max_ant_star']:2d} sqrtn={sqrtn:.2f} case={st['case']}",
                flush=True,
            )


if __name__ == "__main__":
    main()
