"""Diagnostics for Case A1: extra midpoints on S* diagonals with t>=2."""
from __future__ import annotations

import json
import os
from collections import defaultdict

from lemma3_search import overlap_stats, sigma
from q4 import verify

HERE = os.path.dirname(os.path.abspath(__file__))


def extra_kill_profile(n, pts):
    pts = {tuple(p) for p in pts}
    st = overlap_stats(n, pts)
    a = st["a_star"]
    if a is None:
        return st
    star = {p for p in pts if sigma(a, *p) in pts and sigma(a, *p) != p}
    dia = defaultdict(list)
    for x, y in star:
        dia[x - y].append(x + y)
    extra_by_d = {}
    hit = defaultdict(set)
    for d, A in dia.items():
        A = sorted(A)
        mids = set()
        for i in range(len(A)):
            for j in range(i + 1, len(A)):
                mids.add((A[i] + A[j]) // 2)
        extra = mids - {a}
        extra_by_d[d] = extra
        for b in extra:
            hit[b].add(d)
    max_extra_r = max((len(s) for s in hit.values()), default=0)
    n_heavy = sum(1 for A in dia.values() if len(A) >= 4)
    st.update(
        n_heavy_dia=n_heavy,
        extra_midpoints=len(hit),
        max_extra_r=max_extra_r,
        sum_extra=sum(len(v) for v in extra_by_d.values()),
        disjoint_extra=max_extra_r <= 1,
    )
    return st


def main():
    rows = []
    for n in (16, 24, 32, 48, 64, 81, 128, 243):
        path = os.path.join(HERE, "out", "lemma3", f"forced_n{n}.json")
        if not os.path.isfile(path):
            continue
        rec = json.load(open(path, encoding="utf-8"))
        pts = [tuple(p) for p in rec["set"]]
        assert verify(n, pts)
        st = extra_kill_profile(n, pts)
        rows.append(st)
        print(
            f"n={n:3d} |S*|={st['|S_star|']:4d} heavy={st['n_heavy_dia']:3d}  "
            f"extra_mids={st['extra_midpoints']:4d} max_extra_r={st['max_extra_r']:3d}  "
            f"sum_extra={st['sum_extra']:4d} disjoint={st['disjoint_extra']}",
            flush=True,
        )
    os.makedirs(os.path.join(HERE, "out", "lemma3"), exist_ok=True)
    json.dump(rows, open(os.path.join(HERE, "out", "lemma3", "extra_kills.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
