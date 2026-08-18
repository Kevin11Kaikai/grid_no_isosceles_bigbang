"""Exact F_k(n): max sq-free set on k specified rows of [n]^2."""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

from sq import can_add

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)


def search_rows(n, ys):
    """Max sq-free subset of the k rows ys. Recursive by column."""
    k = len(ys)
    best = [0]

    def rec(x, P, sz):
        rem = k * (n - x)
        if sz + rem <= best[0]:
            return
        if x == n:
            if sz > best[0]:
                best[0] = sz
            return
        # masks: which of the k rows occupied in column x
        for mask in range(1 << k):
            added = []
            ok = True
            newP = set(P)
            extra = 0
            for i in range(k):
                if mask >> i & 1:
                    p = (x, ys[i])
                    if not can_add(newP, p):
                        ok = False
                        break
                    newP.add(p)
                    added.append(p)
                    extra += 1
            if not ok:
                continue
            rec(x + 1, newP, sz + extra)

    rec(0, set(), 0)
    return best[0]


def F_k(n, k):
    best = 0
    ex_ys = None
    for ys in combinations(range(n), k):
        val = search_rows(n, ys)
        if val > best:
            best = val
            ex_ys = ys
    return best, ex_ys


def main():
    rows = []
    # k=1,2 known; compute k=3 for n=3..7 and k=4 for n=4..6
    for n in range(3, 8):
        f3, ys3 = F_k(n, 3)
        rec = {
            "n": n,
            "F_2": 2 * n - 2,
            "F_3": f3,
            "F_3_rows": list(ys3) if ys3 else None,
            "Q_SQ_oeis": {3: 4, 4: 6, 5: 9, 6: 11, 7: 14, 8: 17}.get(n),
        }
        if n <= 6:
            f4, ys4 = F_k(n, 4)
            rec["F_4"] = f4
            rec["F_4_rows"] = list(ys4) if ys4 else None
        rows.append(rec)
        print(rec, flush=True)

    p = OUT / "F_k.json"
    p.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", p, flush=True)


if __name__ == "__main__":
    main()
