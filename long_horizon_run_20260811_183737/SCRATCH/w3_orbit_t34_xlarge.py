#!/usr/bin/env python3
"""Wave3 R1: Type3 and Type4 enlarged defect (Wave2 had mixed TIMEOUT/INFEAS on smaller U)."""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.search.orbit_defect_search import (  # noqa: E402
    SearchConfig,
    maybe_save_candidate,
    save_checkpoint,
    solve_orbit_defect,
)


def run_one(stype: int, seed: int, time_s: float, workers: int):
    cfg = SearchConfig(
        n=100,
        symmetry_type=stype,
        mode="defect",
        target_size=165,
        defect_budget_min=1,
        defect_budget_max=16,
        time_budget_s=time_s,
        seed=seed,
        num_workers=workers,
        max_extra_orbits=280,
        max_defect_pool=280,
        halo_radius=16,
        agent_c_universe="U_large",
    )
    print(json.dumps({"start": f"t{stype}_xlarge", "seed": seed, "time_s": time_s}), flush=True)
    res = solve_orbit_defect(cfg)
    ck = save_checkpoint(res, f"w3_xlarge_n100_t{stype}_defect_s{seed}")
    cand = maybe_save_candidate(res)
    out = {
        "status": res.get("solver_status"),
        "size": res.get("size"),
        "universe_id": (res.get("universe") or {}).get("universe_id"),
        "n_free": (res.get("universe") or {}).get("n_free_orbits"),
        "n_def": (res.get("universe") or {}).get("n_defect_points"),
        "model_hash": res.get("model_hash"),
        "wall_time_s": res.get("wall_time_s"),
        "rounds": res.get("rounds"),
        "final_cuts": res.get("final_cuts"),
        "checkpoint": str(ck),
        "candidate": str(cand) if cand else None,
        "symmetry_type": stype,
        "seed": seed,
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_orbit_enlarge")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, f"long_t{stype}_defect_s{seed}_xlarge.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(json.dumps(out, indent=2), flush=True)
    return out


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    time_s = float(os.environ.get("W3_ORBIT_TIME", "1800"))
    workers = int(os.environ.get("W3_ORBIT_WORKERS", "4"))
    rows = []
    # Type3 then Type4 sequentially to avoid oversubscribe with T2 live
    for stype, seed in ((3, 531), (4, 541)):
        rows.append(run_one(stype, seed, time_s, workers))
        if rows[-1].get("size", 0) >= 165:
            break
    summary = {"schema": "w3_orbit_t34_v1", "rows": rows}
    with open(
        os.path.join(RUN, "EXPERIMENTS", "W3_orbit_enlarge", "t34_summary.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(summary, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
