"""Non-right isosceles census on peeling / greedy / full row."""
from __future__ import annotations

import json
import random
from pathlib import Path

from iso_census import census_set
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


def main():
    rng = random.Random(3)
    rows = []

    def add(name, n, pts, cap=None):
        d = census_set(name, n, pts, cap_triples=cap)
        rows.append(d)
        print(
            f"{name:16s} n={n:4d} m={d['m']:5d} tri={d['n_triples']:6d} "
            f"J1={d['n_rot90_J1']:5d} ap3={d['n_ap3_collinear']:5d} "
            f"other={d['n_other']:5d} iso_free={d['iso_free']}",
            flush=True,
        )

    for m in (6, 8, 9):
        rec = build_Am(m)
        add(f"peel_m{m}", rec["n"], rec["set"])

    rec10 = build_Am(10)
    add("peel_m10", rec10["n"], rec10["set"], cap=200000)

    for n in (16, 24, 32):
        add(f"greedy_{n}", n, greedy_sq(n, rng))

    for n in (16, 36, 64):
        add(f"fullrow_{n}", n, [(x, 0) for x in range(n)])

    p = OUT / "iso_census.json"
    p.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", p, flush=True)


if __name__ == "__main__":
    main()
