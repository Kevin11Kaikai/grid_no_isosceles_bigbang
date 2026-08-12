#!/usr/bin/env python3
"""Wave3: Type0 xlarge defect 2-hour escalate (after 45–60min TIMEOUTs)."""
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


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    time_s = float(os.environ.get("W3_ORBIT_TIME", "7200"))
    seed = int(os.environ.get("W3_ORBIT_SEED", "901"))
    workers = int(os.environ.get("W3_ORBIT_WORKERS", "6"))
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_orbit_enlarge")
    os.makedirs(exp, exist_ok=True)
    cfg = SearchConfig(
        n=100,
        symmetry_type=0,
        mode="defect",
        target_size=165,
        defect_budget_min=1,
        defect_budget_max=16,
        time_budget_s=time_s,
        seed=seed,
        num_workers=workers,
        max_extra_orbits=320,
        max_defect_pool=320,
        halo_radius=18,
        agent_c_universe="U_large",
        defect_rank="agent_c",
    )
    print(json.dumps({"start": "w3_t0_defect_2h", "time_s": time_s, "seed": seed}), flush=True)
    t0 = time.time()
    res = solve_orbit_defect(cfg)
    ck = save_checkpoint(res, f"w3_2h_n100_t0_defect_s{seed}")
    cand = maybe_save_candidate(res)
    out = {
        "status": res.get("solver_status"),
        "size": res.get("size"),
        "universe_id": (res.get("universe") or {}).get("universe_id"),
        "model_hash": res.get("model_hash"),
        "wall_time_s": res.get("wall_time_s"),
        "rounds": res.get("rounds"),
        "final_cuts": res.get("final_cuts"),
        "checkpoint": str(ck),
        "candidate": str(cand) if cand else None,
        "elapsed_wrapper_s": time.time() - t0,
    }
    path = os.path.join(exp, f"long2h_t0_defect_s{seed}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
