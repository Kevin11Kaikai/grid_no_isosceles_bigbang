#!/usr/bin/env python3
"""LH-2 follow-up: longer CP-SAT on TIMEOUT frame shells (not treating TIMEOUT as INFEAS)."""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402


def ring(p, n=100):
    x, y = p
    return min(x, y, n - 1 - x, n - 1 - y)


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    exp = os.path.join(RUN, "EXPERIMENTS", "LH2_frame_shells")
    os.makedirs(exp, exist_ok=True)
    jobs = [(2, 2, 600.0), (6, 2, 600.0)]
    rows = []
    t0 = time.time()
    for R, r, budget in jobs:
        add = sorted(
            (x, y)
            for x in range(100)
            for y in range(100)
            if (x, y) not in s0_set and ring((x, y)) <= R
        )
        rem = list(s0)
        uh = universe_hash(rem, add)
        u_id = f"U_fullrem_frameR{R}_r{r}_long"
        print(json.dumps({"start": u_id, "n_vars": len(rem) + len(add), "budget": budget}), flush=True)
        result = hamming_shell_search(
            n=100,
            s0=s0,
            removable=rem,
            addable=add,
            r=r,
            time_budget_s=budget,
            seed=2,
            u_id=u_id,
            universe_hash_str=uh,
            per_round_time_limit_s=45.0,
            symmetry_mode="asymmetric",
        )
        row = {
            "U_id": u_id,
            "status": result.status,
            "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
            "rounds": (result.meta or {}).get("rounds"),
            "final_cuts": (result.meta or {}).get("final_cuts"),
            "wall_time_s": (result.meta or {}).get("wall_time_s"),
            "n_add": len(add),
            "universe_hash": uh,
            "points": result.points,
        }
        rows.append(row)
        with open(os.path.join(exp, f"{u_id}.json"), "w", encoding="utf-8") as f:
            json.dump(row, f, indent=2)
            f.write("\n")
        print(json.dumps({k: row[k] for k in row if k != "points"}, indent=2), flush=True)
        if result.status == "FEASIBLE_LEGAL":
            break
    out = {"schema": "lh2_frame_long_v1", "rows": rows, "wall_s": time.time() - t0}
    with open(os.path.join(exp, "frame_long_summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"done": True, "wall_s": out["wall_s"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
