#!/usr/bin/env python3
"""LH-2: For each exact-2 q, Rem = its size-2 blocker covers (union), Add = all LB<=5.

Small Rem + large Add r=2 shells — distinct from fullrem and from U_small_r2.
"""
from __future__ import annotations

import gzip
import importlib.util
import itertools
import json
import os
import sys
import time
from typing import List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
N = 100
AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")
DETAIL = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_sq", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def covers_size2(edges, max_report=200):
    involved = sorted({p for e in edges for p in e})
    covers = []
    for comb in itertools.combinations(involved, 2):
        C = set(comb)
        if all(e & C for e in edges):
            covers.append(sorted(comb))
            if len(covers) >= max_report:
                break
    return covers


def main():
    t0 = time.time()
    ba = load_ba()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    maps = ba.precompute_pivot_maps(s0)
    with gzip.open(DETAIL, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    easy = [
        tuple(r["q"])
        for r in detail["all_qs_compact"]
        if r.get("exact_min_hitting_set") == 2
    ]
    add = sorted(
        {
            tuple(r["q"])
            for r in detail["all_qs_compact"]
            if int(r["lower_bound_min_deletions"]) <= 5
        }
    )
    # Union Rem over all size-2 covers of all exact-2 qs
    rem_set: Set[Point] = set()
    per_q = []
    for q in easy:
        rec = ba.analyze_q(q, s0, maps, N)
        edges = [frozenset((tuple(e[0]), tuple(e[1]))) for e in rec["blocker_edges"]]
        covs = covers_size2(edges)
        for c in covs:
            rem_set.update(map(tuple, c))
        per_q.append({"q": list(q), "n_covers": len(covs), "n_edges": len(edges)})

    rem = sorted(rem_set)
    # Ensure add excludes s0
    s0_set = set(s0)
    add = [p for p in add if p not in s0_set]
    uh = universe_hash(rem, add)
    exp = os.path.join(RUN, "EXPERIMENTS", "LH2_single_q_large_add")
    os.makedirs(exp, exist_ok=True)
    uni = {
        "U_id": "U_exact2covers_LBle5_r2",
        "n_rem": len(rem),
        "n_add": len(add),
        "n_vars": len(rem) + len(add),
        "universe_hash": uh,
        "n_exact2_qs": len(easy),
        "per_q_cover_counts": per_q,
        "rem": [list(p) for p in rem],
        "add": [list(p) for p in add],
    }
    with open(os.path.join(exp, "universe.json"), "w", encoding="utf-8") as f:
        json.dump(uni, f, indent=2, sort_keys=True)
        f.write("\n")

    print(json.dumps({"universe": {k: uni[k] for k in ("U_id","n_rem","n_add","n_vars","universe_hash","n_exact2_qs")}}, indent=2))

    result = hamming_shell_search(
        n=N,
        s0=s0,
        removable=rem,
        addable=add,
        r=2,
        time_budget_s=240.0,
        seed=1,
        u_id=uni["U_id"],
        universe_hash_str=uh,
        per_round_time_limit_s=30.0,
        symmetry_mode="asymmetric",
    )
    payload = {
        "status": result.status,
        "meta": result.meta,
        "points": result.points,
        "baseline_hash": sha256_of_points(s0),
        "universe_hash": uh,
        "wall_s": time.time() - t0,
    }
    out = os.path.join(exp, "shell_r2_seed1.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "out": out,
                "status": result.status,
                "best_V": (result.meta or {}).get("best_illegal_V"),
                "rounds": (result.meta or {}).get("rounds"),
                "cuts": (result.meta or {}).get("final_cuts"),
                "wall_s": payload["wall_s"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
