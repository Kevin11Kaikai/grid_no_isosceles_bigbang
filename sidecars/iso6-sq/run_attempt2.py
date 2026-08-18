"""Run Method A/B/C measurements for Q_SQ power attempt 2."""
from __future__ import annotations

import json
import random
from math import sqrt
from pathlib import Path

from attempt2 import method_a_report, method_b_report, method_c_decision
from peel import build_Am
from sq import can_add

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)


def dump(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    print("wrote", p, flush=True)


def greedy_sq(n, rng):
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    P = set()
    for p in cells:
        if can_add(P, p):
            P.add(p)
    return list(P)


def synthetic_heavy_row(n, r):
    """One heavy row of r points (an AP), rest empty. Not sq-free if 2nd row added;
    used only to measure |F|."""
    xs = list(range(r))
    return [(x, n // 2) for x in xs]


def main():
    rng = random.Random(2)
    a_rows = []
    b_rows = []

    def add_a(name, n, pts):
        d = method_a_report(name, n, pts)
        a_rows.append(d)
        print(
            f"A {name:16s} n={n:4d} m={d['m']:5d} max_r={d['max_r']:4d} "
            f"heavy={d['n_heavy_rows']} |F|={d['|F_union|']:6d} "
            f"n^2-|F|={d['n^2 - |F|']:7d} light={d['all_light']}",
            flush=True,
        )

    def add_b(name, n, pts):
        d = method_b_report(name, n, pts)
        b_rows.append(d)
        print(
            f"B {name:16s} n={n:4d} m={d['m']:5d} n_w={d['n_w']:6d} "
            f"id={d['identity']} pair_le_m={d['max_pair_le_m']} "
            f"fail={not d['pairing_Aw_disjoint_from_S_minus_Rw']}",
            flush=True,
        )

    # peeling
    for m in (6, 8, 9):
        rec = build_Am(m)
        add_a(f"peel_m{m}", rec["n"], rec["set"])
        add_b(f"peel_m{m}", rec["n"], rec["set"])

    # greedy sq-free
    for n in (16, 24, 32):
        pts = greedy_sq(n, rng)
        add_a(f"greedy_{n}", n, pts)
        add_b(f"greedy_{n}", n, pts)

    # full row (light or heavy depending on sqrt n: r=n > sqrt n ⇒ heavy)
    for n in (16, 36, 64):
        pts = [(x, 0) for x in range(n)]
        add_a(f"fullrow_{n}", n, pts)
        add_b(f"fullrow_{n}", n, pts)

    # synthetic heavy row
    for n, r in ((36, 12), (36, 20), (64, 16), (64, 32)):
        pts = synthetic_heavy_row(n, r)
        add_a(f"synth_r{r}_n{n}", n, pts)

    dump("attempt2_A.json", a_rows)
    dump("attempt2_B.json", b_rows)
    dump("attempt2_C.json", method_c_decision())
    print("done", flush=True)


if __name__ == "__main__":
    main()
