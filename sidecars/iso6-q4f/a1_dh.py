"""Count heavy (d, delta) vertices of S* vs n^{3/4}."""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict

from lemma3_search import overlap_stats, sigma
from q4 import verify

HERE = os.path.dirname(os.path.abspath(__file__))


def portrait(n, pts):
    pts = {tuple(p) for p in pts}
    st = overlap_stats(n, pts)
    a = st["a_star"]
    star = {p for p in pts if sigma(a, *p) in pts and sigma(a, *p) != p}
    rest = pts - star
    T = defaultdict(set)
    for x, y in star:
        d = x - y
        delta = abs((x + y) - a)
        if delta == 0:
            continue
        T[d].add(delta)
    t = {d: len(s) for d, s in T.items()}
    kdelta = Counter()
    for d, s in T.items():
        for delta in s:
            kdelta[delta] += 1
    thresh = n ** 0.75
    Dh = [d for d, td in t.items() if td > thresh]
    Ah = [dl for dl, k in kdelta.items() if k > thresh]
    rho = max((sum(1 for x, y in star if y == yy) for yy in range(n)), default=0)
    mu = max(kdelta.values()) if kdelta else 0
    tmax = max(t.values()) if t else 0
    dia_rest = defaultdict(int)
    for x, y in rest:
        dia_rest[x - y] += 1
    return {
        "n": n,
        "|S_star|": len(star),
        "|S_rest|": len(rest),
        "r": st["r_star"],
        "tmax": tmax,
        "mu": mu,
        "rho": rho,
        "|Dh|": len(Dh),
        "|Ah|": len(Ah),
        "thresh": round(thresh, 2),
        "max_t": sorted(t.values(), reverse=True)[:5],
        "max_k": sorted(kdelta.values(), reverse=True)[:5],
        "max_dia_rest": max(dia_rest.values()) if dia_rest else 0,
        "n_dia_rest": len(dia_rest),
        "unused_dia": (2 * n - 1) - len({x - y for x, y in star}),
    }


def main():
    print(
        f"{'n':>4} {'S*':>5} {'r':>4} {'tmax':>4} {'mu':>3} {'rho':>3} "
        f"{'|Dh|':>4} {'|Ah|':>4} {'mdS':>4} {'ndR':>4} {'unsd':>4}",
        flush=True,
    )
    rows = []
    for n in (7, 8, 16, 32, 81, 128, 243):
        if n <= 10:
            path = os.path.join(HERE, "out", f"exact_n{n}.json")
        else:
            path = os.path.join(HERE, "out", "lemma3", f"forced_n{n}.json")
        if not os.path.isfile(path):
            print("missing", n, flush=True)
            continue
        rec = json.load(open(path, encoding="utf-8"))
        pts = [tuple(p) for p in rec["set"]]
        assert verify(n, pts)
        p = portrait(n, pts)
        rows.append(p)
        print(
            f"{p['n']:4d} {p['|S_star|']:5d} {p['r']:4d} {p['tmax']:4d} "
            f"{p['mu']:3d} {p['rho']:3d} {p['|Dh|']:4d} {p['|Ah|']:4d} "
            f"{p['max_dia_rest']:4d} {p['n_dia_rest']:4d} {p['unused_dia']:4d}  "
            f"t={p['max_t']} k={p['max_k']}",
            flush=True,
        )
    out = os.path.join(HERE, "out", "lemma3", "dh_portrait.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(rows, open(out, "w"), indent=2)


if __name__ == "__main__":
    main()
