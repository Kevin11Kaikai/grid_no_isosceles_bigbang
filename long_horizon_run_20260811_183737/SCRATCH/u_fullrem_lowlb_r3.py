#!/usr/bin/env python3
"""LH-2: U_fullrem_LBle4 at r=3 (need |R|=3,|A|=4) after r=2 scoped INFEAS."""
from __future__ import annotations

import gzip
import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

DETAIL = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")


def main():
    t0 = time.time()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    with gzip.open(DETAIL, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    add = sorted(
        {
            (int(r["q"][0]), int(r["q"][1]))
            for r in detail["all_qs_compact"]
            if int(r["lower_bound_min_deletions"]) <= 4
        }
    )
    rem = list(s0)
    uh = universe_hash(rem, add)
    exp = os.path.join(RUN, "EXPERIMENTS", "LH1_hamming_newU")
    os.makedirs(exp, exist_ok=True)
    result = hamming_shell_search(
        n=100,
        s0=s0,
        removable=rem,
        addable=add,
        r=3,
        time_budget_s=300.0,
        seed=1,
        u_id="U_fullrem_LBle4_r3",
        universe_hash_str=uh,
        per_round_time_limit_s=40.0,
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
        "r": 3,
        "wall_s": time.time() - t0,
        "claim_discipline": "Scoped only.",
    }
    out = os.path.join(exp, "shell_r3_LBle4_seed1.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "out": out,
                "status": result.status,
                "n_vars": len(rem) + len(add),
                "hash": uh,
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
