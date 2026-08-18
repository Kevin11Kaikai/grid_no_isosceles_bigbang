"""Seed a long S* row (plus partner column) and fill, to test max_row > sqrt(n)."""
from __future__ import annotations

import random

from q4 import FourDir, verify
from lemma3_search import overlap_stats, sigma
from collections import defaultdict


def greedy_row_apfree(n, y, parity):
    xs = []
    for x in range(parity, n, 2):
        ss = set(xs)
        ok = True
        for a in xs:
            if (a + x) % 2 == 0:
                mid = (a + x) // 2
                if mid in ss:
                    ok = False
                    break
        if ok:
            xs.append(x)
    return xs


def seed_row_fold(n, a, y, xs):
    """Place (x,y) and sigma partners. Intersection with x+y=a is skipped."""
    st = FourDir(n)
    placed = []
    for x in xs:
        if x + y == a:
            continue
        sx, sy = a - y, a - x
        if not (0 <= sx < n and 0 <= sy < n):
            continue
        if (sx, sy) == (x, y):
            continue
        for p in ((x, y), (sx, sy)):
            if p in st.pts:
                continue
            ks = st.can_add(*p)
            if ks is None:
                return None, placed
            st.push(*p, ks)
            placed.append(p)
    return st, placed


def fill(st, n, rng):
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    for x, y in cells:
        ks = st.can_add(x, y)
        if ks is not None:
            st.add(x, y, ks)


def portrait_star(n, pts):
    stt = overlap_stats(n, pts)
    a = stt["a_star"]
    star = set()
    if a is not None:
        for p in pts:
            q = sigma(a, *p)
            if q in pts and q != p:
                star.add(p)
    row = defaultdict(int)
    dia = defaultdict(int)
    ant = defaultdict(int)
    for x, y in star:
        row[y] += 1
        dia[x - y] += 1
        ant[x + y] += 1
    stt["max_row_star"] = max(row.values()) if row else 0
    stt["max_dia_star"] = max(dia.values()) if dia else 0
    stt["max_ant_star"] = max(ant.values()) if ant else 0
    stt["seeded_row"] = max(row.values()) if row else 0
    return stt


def main():
    rng = random.Random(1)
    for n in (16, 32, 48, 81):
        a = n - 1
        sqrtn = n ** 0.5
        best = None
        for y in range(n):
            for par in (0, 1):
                xs = greedy_row_apfree(n, y, par)
                # try prefixes of increasing length
                for L in sorted({2, 3, 4, int(sqrtn) + 1, len(xs)}):
                    if L < 2 or L > len(xs):
                        continue
                    st, placed = seed_row_fold(n, a, y, xs[:L])
                    if st is None:
                        continue
                    fill(st, n, rng)
                    pts = set(st.pts)
                    assert verify(n, pts)
                    stt = portrait_star(n, pts)
                    stt["seed_L"] = L
                    stt["seed_y"] = y
                    if best is None or stt["max_row_star"] > best["max_row_star"]:
                        best = stt
        print(
            f"n={n:3d} best max_row*={best['max_row_star']:2d} max_dia*={best['max_dia_star']:2d} "
            f"max_ant*={best['max_ant_star']:2d} max_r={best['max_r']:3d} |S*|={best['|S_star|']:4d} "
            f"sqrtn={sqrtn:.2f} seed_L={best['seed_L']} case={best['case']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
