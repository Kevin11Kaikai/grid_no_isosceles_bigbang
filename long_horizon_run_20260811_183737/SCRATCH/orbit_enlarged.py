#!/usr/bin/env python3
"""LH-4: Orbit defect with enlarged universes (beyond Wave2 halo caps)."""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.search.orbit_defect_search import SearchConfig, solve_orbit_defect, save_checkpoint  # noqa: E402


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    t0 = time.time()
    exp = os.path.join(RUN, "EXPERIMENTS", "LH4_orbit_enlarged")
    os.makedirs(exp, exist_ok=True)
    rows = []
    jobs = [
        dict(n=100, symmetry_type=0, mode="defect", dmin=1, dmax=10, seed=201, time=180.0),
        dict(n=100, symmetry_type=1, mode="defect", dmin=1, dmax=10, seed=202, time=180.0),
        dict(n=100, symmetry_type=1, mode="pure", dmin=0, dmax=0, seed=203, time=90.0),
    ]
    for j in jobs:
        cfg = SearchConfig(
            n=j["n"],
            symmetry_type=j["symmetry_type"],
            mode=j["mode"],
            target_size=165,
            defect_budget_min=j["dmin"],
            defect_budget_max=j["dmax"],
            time_budget_s=j["time"],
            seed=j["seed"],
            num_workers=max(1, (os.cpu_count() or 4) // 4),
            max_extra_orbits=220,
            max_defect_pool=220,
            halo_radius=14,
        )
        print(json.dumps({"start": j}), flush=True)
        result = solve_orbit_defect(cfg)
        ck = save_checkpoint(result, f"enlarged_n100_t{j['symmetry_type']}_{j['mode']}_s{j['seed']}")
        row = {
            "job": j,
            "status": result.get("solver_status"),
            "size": result.get("size"),
            "universe_id": (result.get("universe") or {}).get("universe_id"),
            "n_free_orbits": (result.get("universe") or {}).get("n_free_orbits"),
            "n_defect_points": (result.get("universe") or {}).get("n_defect_points"),
            "model_hash": result.get("model_hash"),
            "wall_time_s": result.get("wall_time_s"),
            "checkpoint": str(ck),
        }
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if result.get("solver_status") in ("FEASIBLE", "FEASIBLE_LEGAL") or (result.get("size") or 0) >= 165:
            # freeze if any candidate points
            if result.get("points"):
                with open(os.path.join(RUN, "CANDIDATES", "n100_orbit_enlarged.json"), "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, default=str)
            break
    out = {"schema": "lh4_orbit_enlarged_v1", "rows": rows, "wall_s": time.time() - t0}
    path = os.path.join(exp, "summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"path": path, "wall_s": out["wall_s"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
