#!/usr/bin/env python3
"""LH-1 Route A: new universe U_fullrem_LBle4_r2 — Rem=all S0, Add=all unselected with LB<=4.

Distinct from Wave2 U_fullrem_A* (score/halo add pools). Uses blocker LB filter.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from typing import List, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import (  # noqa: E402
    hamming_shell_search,
    universe_hash,
)
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
N = 100
AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_u", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main():
    t0 = time.time()
    ba = load_ba()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    maps = ba.precompute_pivot_maps(s0)

    # Collect Add = all q with LB <= 4 (exact when available)
    add: List[Point] = []
    lb_hist = {}
    # Scanning all 9836 is OK if analyze_q is fast enough; use LB via quick bound first
    # For speed: compute type1_forced + matching quickly by calling analyze_q
    # Budget: analyze all unselected — Agent A did this once; we re-do for LB<=4 filter only
    # Optimization: only check cells where a cheap LB proxy is small
    for x in range(N):
        for y in range(N):
            q = (x, y)
            if q in s0_set:
                continue
            rec = ba.analyze_q(q, s0, maps, N)
            lb = rec["lower_bound_min_deletions"]
            lb_hist[lb] = lb_hist.get(lb, 0) + 1
            if lb <= 4:
                add.append(q)

    rem = list(s0)
    add = sorted(add)
    uh = universe_hash(rem, add)
    uni = {
        "U_id": "U_fullrem_LBle4_r2",
        "n_rem": len(rem),
        "n_add": len(add),
        "n_vars": len(rem) + len(add),
        "universe_hash": uh,
        "lb_hist_all_unselected": {str(k): v for k, v in sorted(lb_hist.items())},
        "add": [list(p) for p in add],
        "note": "Rem=all baseline; Add=unselected with blocker LB<=4; r=2 shell.",
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH1_hamming_newU")
    os.makedirs(exp, exist_ok=True)
    with open(os.path.join(exp, "U_fullrem_LBle4_r2.json"), "w", encoding="utf-8") as f:
        json.dump(uni, f, indent=2, sort_keys=True)
        f.write("\n")

    print(
        json.dumps(
            {
                "universe_built": True,
                "n_add": len(add),
                "n_vars": uni["n_vars"],
                "hash": uh,
                "lb_hist": uni["lb_hist_all_unselected"],
                "build_s": time.time() - t0,
            },
            indent=2,
        )
    )

    # CP-SAT shell
    out_path = os.path.join(exp, "shell_r2_seed1.json")
    result = hamming_shell_search(
        n=N,
        s0=s0,
        removable=rem,
        addable=add,
        r=2,
        time_budget_s=180.0,
        seed=1,
        u_id="U_fullrem_LBle4_r2",
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
        "n_add": len(add),
        "n_rem": len(rem),
        "wall_s": time.time() - t0,
        "claim_discipline": "Scoped only; not global UB.",
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "out_path": out_path,
                "status": result.status,
                "meta_keys": list((result.meta or {}).keys())[:20],
                "best_V": (result.meta or {}).get("best_illegal_V"),
                "rounds": (result.meta or {}).get("rounds"),
                "cuts": (result.meta or {}).get("final_cuts")
                or (result.meta or {}).get("cuts"),
                "wall_s": payload["wall_s"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
