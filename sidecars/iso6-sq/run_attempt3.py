"""Run Method D (multi-row / two-row forbidden union)."""
from __future__ import annotations

import json
import random
from pathlib import Path

from attempt3 import method_d_report
from peel import build_Am
from sq import can_add

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)


def greedy_sq(n, rng):
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    P = set()
    for p in cells:
        if can_add(P, p):
            P.add(p)
    return list(P)


def two_medium_rows(n, r, shared):
    """Two rows of size r, sharing `shared` columns. Disjoint remainder."""
    y1, y2 = n // 3, 2 * n // 3
    I = list(range(shared))
    extra1 = list(range(shared, r))
    extra2 = list(range(n - (r - shared), n))
    pts = [(x, y1) for x in I + extra1] + [(x, y2) for x in I + extra2]
    return n, pts


def main():
    rng = random.Random(4)
    rows = []

    def add(name, n, pts):
        d = method_d_report(name, n, pts)
        rows.append(d)
        print(
            f"D {name:16s} n={n:4d} m={d['m']:5d} |F|={d['|F_union|']:6d} "
            f"left={d['n^2 - |F|']:7d} frac={d['leftover / n^2']:.3f} "
            f"shared_pairs={d['n_row_pairs_shared_col']} "
            f"hit={d['S_hits_F_rows']+d['S_hits_F_cols']+d['S_hits_F_tworow']}",
            flush=True,
        )

    for m in (6, 8, 9):
        rec = build_Am(m)
        add(f"peel_m{m}", rec["n"], rec["set"])

    for n in (16, 24, 32):
        add(f"greedy_{n}", n, greedy_sq(n, rng))

    for n in (16, 36, 64):
        add(f"fullrow_{n}", n, [(x, 0) for x in range(n)])

    for n, r, sh in ((36, 12, 0), (36, 12, 6), (64, 20, 0), (64, 20, 10)):
        nn, pts = two_medium_rows(n, r, sh)
        add(f"tworow_r{r}_sh{sh}_n{n}", nn, pts)

    p = OUT / "attempt3_D.json"
    p.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", p, flush=True)


if __name__ == "__main__":
    main()
