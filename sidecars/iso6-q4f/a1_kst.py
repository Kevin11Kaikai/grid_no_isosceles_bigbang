"""KST / bipartite pattern diagnostics on S* (diagonal vs delta)."""
from __future__ import annotations

import json
import os
from collections import defaultdict

from lemma3_search import overlap_stats, sigma
from q4 import verify

HERE = os.path.dirname(os.path.abspath(__file__))


def delta_sets(n, pts):
    pts = {tuple(p) for p in pts}
    st = overlap_stats(n, pts)
    a = st["a_star"]
    star = {p for p in pts if sigma(a, *p) in pts and sigma(a, *p) != p}
    dia = defaultdict(set)
    for x, y in star:
        d = x - y
        delta = abs((x + y) - a)
        if delta:
            dia[d].add(delta)
    sets = list(dia.values())
    max_t = max((len(s) for s in sets), default=0)
    max_inter = 0
    n_c4 = 0
    n_k23 = 0
    n_k24 = 0
    for i, A in enumerate(sets):
        for B in sets[i + 1 :]:
            inter = len(A & B)
            max_inter = max(max_inter, inter)
            if inter >= 2:
                n_c4 += 1
            if inter >= 3:
                n_k23 += 1
            if inter >= 4:
                n_k24 += 1
    pair_hit = defaultdict(int)
    triple_hit = defaultdict(int)
    for A in sets:
        Al = sorted(A)
        for i, d1 in enumerate(Al):
            for j, d2 in enumerate(Al[i + 1 :], start=i + 1):
                pair_hit[(d1, d2)] += 1
                for d3 in Al[j + 1 :]:
                    triple_hit[(d1, d2, d3)] += 1
    max_s_for_2 = max(pair_hit.values(), default=0)
    max_s_for_3 = max(triple_hit.values(), default=0)
    st.update(
        ndia=len(sets),
        max_t=max_t,
        max_inter=max_inter,
        n_c4=n_c4,
        n_k23=n_k23,
        n_k24=n_k24,
        max_Ks2=max_s_for_2,
        max_Ks3=max_s_for_3,
    )
    return st


def main():
    for n in (7, 8, 16, 32, 81, 128, 243):
        if n <= 10:
            path = os.path.join(HERE, "out", f"exact_n{n}.json")
            tag = "exact"
        else:
            path = os.path.join(HERE, "out", "lemma3", f"forced_n{n}.json")
            tag = "forced"
        if not os.path.isfile(path):
            continue
        rec = json.load(open(path, encoding="utf-8"))
        pts = [tuple(p) for p in rec["set"]]
        assert verify(n, pts)
        st = delta_sets(n, pts)
        print(
            f"{tag:7s} n={n:3d} |S*|={st['|S_star|']:4d} ndia={st['ndia']:3d} "
            f"max_t={st['max_t']} max_inter={st['max_inter']} "
            f"C4={st['n_c4']} K23={st['n_k23']} K24={st['n_k24']} "
            f"max_Ks2={st['max_Ks2']} max_Ks3={st['max_Ks3']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
