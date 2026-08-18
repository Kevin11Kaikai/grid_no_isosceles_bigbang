"""Try to make max_row, max_dia, max_ant of S* all exceed sqrt(n) at once."""
from __future__ import annotations

import random
from collections import defaultdict

from q4 import FourDir, verify
from lemma3_search import overlap_stats, sigma
from a1_construct import behrend_like
from a1_longrow import greedy_row_apfree, seed_row_fold, fill


def place_heavy_diag(st, n, a, t_target):
    deltas = behrend_like(n // 2)
    chosen = []
    for delta in deltas:
        trial = chosen + [delta]
        vals = sorted([-x for x in trial] + trial)
        A = [a + v for v in vals]
        if min(A) < 0 or max(A) > 2 * n - 2:
            continue
        ss = set(A)
        ok = True
        for i, x in enumerate(A):
            for y in A[i + 1 :]:
                if (x + y) % 2 == 0 and (x + y) // 2 in ss:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            chosen = trial
        if len(chosen) >= t_target:
            break
    if len(chosen) < 2:
        return 0
    for d in range(1 - n, n):
        pts = []
        good = True
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
        if not good:
            continue
        recs = []
        ok = True
        for p in pts:
            if p in st.pts:
                continue
            ks = st.can_add(*p)
            if ks is None:
                ok = False
                break
            recs.append(st.push(*p, ks))
        if ok:
            return len(chosen)
        for rec in reversed(recs):
            st.pop(rec)
    return 0


def star_maxes(n, pts):
    stt = overlap_stats(n, pts)
    a = stt["a_star"]
    star = set()
    if a is not None:
        for p in pts:
            q = sigma(a, *p)
            if q in pts and q != p:
                star.add(p)
    row = defaultdict(int)
    col = defaultdict(int)
    dia = defaultdict(int)
    ant = defaultdict(int)
    for x, y in star:
        row[y] += 1
        col[x] += 1
        dia[x - y] += 1
        ant[x + y] += 1
    stt["max_row_star"] = max(row.values()) if row else 0
    stt["max_col_star"] = max(col.values()) if col else 0
    stt["max_dia_star"] = max(dia.values()) if dia else 0
    stt["max_ant_star"] = max(ant.values()) if ant else 0
    stt["min_max"] = min(
        stt["max_row_star"],
        stt["max_col_star"],
        stt["max_dia_star"],
        stt["max_ant_star"],
    )
    return stt


def main():
    rng = random.Random(2)
    for n in (32, 48, 81):
        a = n - 1
        sqrtn = n ** 0.5
        best = None
        for y in range(0, n, max(1, n // 8)):
            xs = greedy_row_apfree(n, y, 0) or greedy_row_apfree(n, y, 1)
            L = min(len(xs), int(sqrtn) + 3)
            if L < 3:
                continue
            for t_target in (2, 3, 4, int(sqrtn) // 2 + 2):
                st, placed = seed_row_fold(n, a, y, xs[:L])
                if st is None:
                    continue
                place_heavy_diag(st, n, a, t_target)
                fill(st, n, rng)
                pts = set(st.pts)
                assert verify(n, pts)
                stt = star_maxes(n, pts)
                if best is None or stt["min_max"] > best["min_max"]:
                    best = stt
        print(
            f"n={n:3d} min_of_maxes={best['min_max']:2d} "
            f"row={best['max_row_star']:2d} col={best['max_col_star']:2d} "
            f"dia={best['max_dia_star']:2d} ant={best['max_ant_star']:2d} "
            f"max_r={best['max_r']:3d} |S*|={best['|S_star|']:4d} sqrtn={sqrtn:.2f} "
            f"case={best['case']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
