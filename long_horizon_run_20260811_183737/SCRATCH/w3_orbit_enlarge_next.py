#!/usr/bin/env python3
"""Wave3 R1 next: further-enlarged Type0 defect after s401 45min.

Universe caps beyond LH4-220/h14:
  max_extra_orbits=320, max_defect_pool=320, halo_radius=18,
  agent_c_universe=U_large, dmax=16, time default 3600s.
"""
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
    time_s = float(os.environ.get("W3_ORBIT_TIME", "3600"))
    seed = int(os.environ.get("W3_ORBIT_SEED", "501"))
    workers = int(os.environ.get("W3_ORBIT_WORKERS", str(max(1, (os.cpu_count() or 4) // 4))))
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
    )
    print(
        json.dumps(
            {
                "start": "w3_t0_defect_xlarge",
                "time_s": time_s,
                "seed": seed,
                "workers": workers,
                "max_extra": 320,
                "halo": 18,
                "agent_c_universe": "U_large",
            }
        ),
        flush=True,
    )
    t0 = time.time()
    res = solve_orbit_defect(cfg)
    ck = save_checkpoint(res, f"w3_xlarge_n100_t0_defect_s{seed}")
    cand = maybe_save_candidate(res)
    out = {
        "status": res.get("solver_status"),
        "size": res.get("size"),
        "universe_id": (res.get("universe") or {}).get("universe_id"),
        "n_free_orbits": (res.get("universe") or {}).get("n_free_orbits"),
        "n_defect_points": (res.get("universe") or {}).get("n_defect_points"),
        "model_hash": res.get("model_hash"),
        "wall_time_s": res.get("wall_time_s"),
        "rounds": res.get("rounds"),
        "final_cuts": res.get("final_cuts"),
        "checkpoint": str(ck),
        "candidate": str(cand) if cand else None,
        "elapsed_outer_s": time.time() - t0,
        "cfg": {
            "max_extra_orbits": 320,
            "max_defect_pool": 320,
            "halo_radius": 18,
            "agent_c_universe": "U_large",
            "dmax": 16,
            "time_s": time_s,
            "seed": seed,
        },
    }
    path = os.path.join(exp, f"long_t0_defect_s{seed}_xlarge.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
