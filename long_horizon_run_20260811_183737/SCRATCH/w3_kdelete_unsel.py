#!/usr/bin/env python3
"""How many unselected cells become addable after deleting k S0 points?

F081/F083: k=2 opens at most 1 unselected (the designed q), else 0.
Need n_unsel >= k+1 for a frozen-core net +1, or n_unsel >= r+1 for Hamming
delete-exactly-r in a larger Rem.

Sweep k and Rem recipes. Cheap kill if n_unsel stays << k+1 until k is in
the already-dead large-destroy band.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402

EXP = os.path.join(RUN, "EXPERIMENTS", "W3_kdelete_unsel")
os.makedirs(EXP, exist_ok=True)
COMM = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_communities_n100.json")
N = 100


def n_unsel(s0_set, T):
    Tset = set(map(tuple, T))
    st = IncrementalIsoscelesFreeSet(N)
    for p in s0_set:
        if p not in Tset:
            assert st.add_point(p)
    c = 0
    for x in range(N):
        for y in range(N):
            p = (x, y)
            if p in st.points or p in Tset:
                continue
            if st.can_add(p)[0]:
                c += 1
    return c


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    s0 = [tuple(map(int, p)) for p in SOL_100]
    s0_set = set(s0)
    rng = random.Random(11)
    with open(COMM, "r", encoding="utf-8") as f:
        comm = json.load(f)
    freq = Counter()
    for item in comm["bipartite_incidence"]["top_certificates_by_q_frequency"][:400]:
        a, b = item["certificate_edge"]
        w = item["n_qs_blocked_by_this_edge"]
        freq[tuple(a)] += w
        freq[tuple(b)] += w
    topv = [p for p, _ in freq.most_common(80)]
    outer = sorted(s0, key=lambda p: min(p[0], p[1], 99 - p[0], 99 - p[1]))
    rows = []
    t0 = time.time()
    ks = [2, 3, 4, 6, 8, 12, 16, 24, 32]
    for k in ks:
        recipes = {
            "random": rng.sample(s0, k),
            "top_degree": topv[:k],
            "outer": outer[:k],
        }
        for name, T in recipes.items():
            nu = n_unsel(s0_set, T)
            row = {
                "k": k,
                "recipe": name,
                "n_unsel": nu,
                "need_for_frozen_plus1": k + 1,
                "surplus": nu - (k + 1),
            }
            rows.append(row)
            print(json.dumps(row), flush=True)
    # extra random seeds for small k
    for k in (2, 3, 4):
        for s in range(12):
            T = rng.sample(s0, k)
            nu = n_unsel(s0_set, T)
            row = {
                "k": k,
                "recipe": f"random_s{s}",
                "n_unsel": nu,
                "need_for_frozen_plus1": k + 1,
                "surplus": nu - (k + 1),
            }
            rows.append(row)
            print(json.dumps(row), flush=True)
    summary = {
        "schema": "w3_kdelete_unsel_v1",
        "rows": rows,
        "max_n_unsel": max(r["n_unsel"] for r in rows),
        "any_surplus_ge0": any(r["surplus"] >= 0 for r in rows),
        "best": max(rows, key=lambda r: (r["surplus"], r["n_unsel"])),
        "wall_s": time.time() - t0,
    }
    with open(os.path.join(EXP, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    print(json.dumps({k: summary[k] for k in ("max_n_unsel", "any_surplus_ge0", "best", "wall_s")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
