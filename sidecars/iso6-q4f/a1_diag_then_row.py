"""Place heavy diagonal first, then a long row, to test both maxima > sqrt(n)."""
from __future__ import annotations

import random
from collections import defaultdict

from q4 import FourDir, verify
from lemma3_search import overlap_stats, sigma
from a1_allmax import place_heavy_diag, star_maxes
from a1_longrow import greedy_row_apfree


def try_add_row(st, n, a, y, xs):
    recs_all = []
    for x in xs:
        if x + y == a:
            continue
        sx, sy = a - y, a - x
        if not (0 <= sx < n and 0 <= sy < n):
            continue
        added = []
        ok = True
        for p in ((x, y), (sx, sy)):
            if p in st.pts:
                continue
            ks = st.can_add(*p)
            if ks is None:
                ok = False
                break
            added.append(st.push(*p, ks))
        if not ok:
            for rec in reversed(added):
                st.pop(rec)
            continue
        recs_all.extend(added)
    return recs_all


def fill(st, n, rng):
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    for x, y in cells:
        ks = st.can_add(x, y)
        if ks is not None:
            st.add(x, y, ks)


def main():
    rng = random.Random(3)
    for n in (32, 48, 81, 128):
        a = n - 1
        sqrtn = n ** 0.5
        best = None
        t_target = max(3, int(sqrtn) // 2 + 2)
        for trial in range(8):
            st = FourDir(n)
            ht = place_heavy_diag(st, n, a, t_target)
            if ht < 2:
                continue
            for y in range(0, n, max(1, n // 10)):
                for par in (0, 1):
                    xs = greedy_row_apfree(n, y, par)
                    try_add_row(st, n, a, y, xs)
            fill(st, n, rng)
            pts = set(st.pts)
            assert verify(n, pts)
            stt = star_maxes(n, pts)
            stt["heavy_t"] = ht
            if best is None or (stt["max_row_star"] + stt["max_dia_star"], stt["min_max"]) > (
                best["max_row_star"] + best["max_dia_star"],
                best["min_max"],
            ):
                best = stt
        print(
            f"n={n:3d} min_of_maxes={best['min_max']:2d} "
            f"row={best['max_row_star']:2d} col={best['max_col_star']:2d} "
            f"dia={best['max_dia_star']:2d} ant={best['max_ant_star']:2d} "
            f"max_r={best['max_r']:3d} |S*|={best['|S_star|']:4d} sqrtn={sqrtn:.2f}",
            flush=True,
        )


if __name__ == "__main__":
    main()
