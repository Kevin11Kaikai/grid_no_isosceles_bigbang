"""Count global heavy diagonals / antis vs n^{3/4} and n^{7/8}."""
from __future__ import annotations

import json
import os
from collections import Counter

from q4 import verify

HERE = os.path.dirname(os.path.abspath(__file__))


def heavy_portrait(n, pts):
    pts = [tuple(p) for p in pts]
    dia = Counter(x - y for x, y in pts)
    ant = Counter(x + y for x, y in pts)
    th = n ** 0.75
    th2 = n ** 0.875
    H = sum(1 for c in dia.values() if c > th)
    J = sum(1 for c in ant.values() if c > th)
    H2 = sum(1 for c in dia.values() if c > th2)
    J2 = sum(1 for c in ant.values() if c > th2)
    return {
        "n": n,
        "|S|": len(pts),
        "max_dia": max(dia.values()) if dia else 0,
        "max_ant": max(ant.values()) if ant else 0,
        "|H|": H,
        "|J|": J,
        "|H78|": H2,
        "|J78|": J2,
        "th": round(th, 2),
        "th2": round(th2, 2),
        "gap": H > th and (H > th2 or J > th2) and J > th,
    }


def main():
    print(
        f"{'src':<8} {'n':>4} {'|S|':>5} {'md':>4} {'ma':>4} "
        f"{'|H|':>4} {'|J|':>4} {'H78':>4} {'J78':>4} {'gap':>5}",
        flush=True,
    )
    rows = []
    for n in (7, 8, 16, 32, 81, 128, 243):
        if n <= 10:
            path = os.path.join(HERE, "out", f"exact_n{n}.json")
            src = "exact"
        else:
            path = os.path.join(HERE, "out", "lemma3", f"forced_n{n}.json")
            src = "forced"
        if not os.path.isfile(path):
            continue
        rec = json.load(open(path, encoding="utf-8"))
        pts = [tuple(p) for p in rec["set"]]
        assert verify(n, pts)
        p = heavy_portrait(n, pts)
        rows.append(p)
        print(
            f"{src:<8} {p['n']:4d} {p['|S|']:5d} {p['max_dia']:4d} {p['max_ant']:4d} "
            f"{p['|H|']:4d} {p['|J|']:4d} {p['|H78|']:4d} {p['|J78|']:4d} "
            f"{str(p['gap']):>5}",
            flush=True,
        )
    out = os.path.join(HERE, "out", "lemma3", "heavy_portrait.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(rows, open(out, "w"), indent=2)


if __name__ == "__main__":
    main()
