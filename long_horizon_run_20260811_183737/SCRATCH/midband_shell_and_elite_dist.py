#!/usr/bin/env python3
"""LH-2 parallel: (1) mid-band Add shells; (2) Hamming distance of V3 elites vs S0."""
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
from src.structures.candidate_io import sha256_of_points  # noqa: E402


def ring(p, n=100):
    x, y = p
    return min(x, y, n - 1 - x, n - 1 - y)


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    t0 = time.time()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)

    # Elite distances
    elite_dir = os.path.join(ROOT, "scratch", "agent_c", "elite_archive")
    elite_rows = []
    for name in sorted(os.listdir(elite_dir)):
        if not (name.startswith("n100_V3_") and name.endswith(".json")):
            continue
        with open(os.path.join(elite_dir, name), encoding="utf-8") as f:
            pts = {tuple(p) for p in json.load(f)["points"]}
        rem = len(s0_set - pts)
        add = len(pts - s0_set)
        elite_rows.append(
            {
                "file": name,
                "hamming_remove": rem,
                "hamming_add": add,
                "symmetric_diff": rem + add,
                "size": len(pts),
            }
        )
    dist_path = os.path.join(RUN, "EXPERIMENTS", "LH2_elite_distance", "v3_vs_s0.json")
    os.makedirs(os.path.dirname(dist_path), exist_ok=True)
    with open(dist_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "schema": "lh2_v3_elite_distance_v1",
                "baseline_hash": sha256_of_points(s0),
                "elites": elite_rows,
                "min_remove": min(r["hamming_remove"] for r in elite_rows) if elite_rows else None,
                "min_add": min(r["hamming_add"] for r in elite_rows) if elite_rows else None,
            },
            f,
            indent=2,
        )
        f.write("\n")
    print(json.dumps({"elite_distance": dist_path, "rows": elite_rows}, indent=2), flush=True)

    # Mid-band Add: ring in [10,26]
    add = sorted(
        (x, y)
        for x in range(100)
        for y in range(100)
        if (x, y) not in s0_set and 10 <= ring((x, y)) <= 26
    )
    rem = list(s0)
    uh = universe_hash(rem, add)
    exp = os.path.join(RUN, "EXPERIMENTS", "LH2_midband_shells")
    os.makedirs(exp, exist_ok=True)
    print(json.dumps({"midband_n_add": len(add), "n_vars": len(rem)+len(add), "hash": uh}), flush=True)
    summaries = []
    for r in (2, 4):
        u_id = f"U_fullrem_midband10_26_r{r}"
        result = hamming_shell_search(
            n=100,
            s0=s0,
            removable=rem,
            addable=add,
            r=r,
            time_budget_s=120.0,
            seed=1,
            u_id=u_id,
            universe_hash_str=uh,
            per_round_time_limit_s=25.0,
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
        }
        summaries.append(row)
        with open(os.path.join(exp, f"{u_id}.json"), "w", encoding="utf-8") as f:
            json.dump(row, f, indent=2)
            f.write("\n")
        print(json.dumps(row, indent=2), flush=True)
    with open(os.path.join(exp, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"summaries": summaries, "wall_s": time.time() - t0}, f, indent=2)
        f.write("\n")
    print(json.dumps({"done": True, "wall_s": time.time() - t0}, indent=2), flush=True)


if __name__ == "__main__":
    main()
