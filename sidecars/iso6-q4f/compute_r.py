"""Compute max number of diagonals that share a killed anti-diagonal (r(a))."""
import json
import os
from collections import defaultdict
from q4 import verify

HERE = os.path.dirname(os.path.abspath(__file__))


def max_r(pts):
    dia = defaultdict(list)
    ua = {p[0] + p[1] for p in pts}
    for x, y in pts:
        dia[x - y].append(x + y)
    r = defaultdict(set)
    for d, A in dia.items():
        A = sorted(A)
        for i, a in enumerate(A):
            for b in A[i + 1 :]:
                mid = (a + b) // 2
                r[mid].add(d)
    # only killed (must be outside U_ant)
    r_kill = {a: s for a, s in r.items() if a not in ua}
    mx = max((len(s) for s in r_kill.values()), default=0)
    return mx, {int(a): len(s) for a, s in sorted(r_kill.items())}


def main():
    rows = []
    for n in range(1, 11):
        path = os.path.join(HERE, "out", f"exact_n{n}.json")
        rec = json.load(open(path, encoding="utf-8"))
        pts = [tuple(p) for p in rec["set"]]
        assert verify(n, pts)
        mx, hist = max_r(pts)
        rows.append({"n": n, "|S|": len(pts), "max_r": mx, "r_hist": hist})
        print(f"n={n:2d} |S|={len(pts):3d}  max_r={mx:2d}  hist={hist}")
    os.makedirs(os.path.join(HERE, "out", "upperbound"), exist_ok=True)
    json.dump(rows, open(os.path.join(HERE, "out", "upperbound", "max_r_exact.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
