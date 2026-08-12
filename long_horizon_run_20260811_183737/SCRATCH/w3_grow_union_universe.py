#!/usr/bin/env python3
"""CheapKill → Compute: multi-grow union universe as defect pool; maximize / fixed-card screen."""
from __future__ import annotations

import json
import os
import random
import sys
import time
from typing import List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from ortools.sat.python import cp_model  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
from w3_global_refill_after_destroy import maximize_from_core, witnesses, dual  # noqa: E402
from w3_joint_hs_and_grow_destroy import grow_legal  # noqa: E402

Point = Tuple[int, int]
N = 100


def maximize_in_universe(universe: List[Point], time_s: float, workers: int, seed: int, lb: int = 0) -> dict:
    """Maximize legal subset inside a fixed universe (empty core)."""
    free = list(universe)
    cuts = set()
    t0 = time.time()
    best_size = 0
    best_pts: List[Point] = []
    lb_extra = max(0, lb)
    rounds = 0
    status = "TIMEOUT"
    proved_max = None
    while time.time() - t0 < time_s:
        rounds += 1
        model = cp_model.CpModel()
        z = {p: model.NewBoolVar(f"z{p[0]}_{p[1]}") for p in free}
        model.Maximize(sum(z.values()))
        if lb_extra > 0:
            model.Add(sum(z.values()) >= lb_extra)
        for trip in cuts:
            free_in = [z[p] for p in trip if p in z]
            if free_in:
                model.Add(sum(free_in) <= len(free_in) - 1)
        solver = cp_model.CpSolver()
        rem = max(0.5, time_s - (time.time() - t0))
        solver.parameters.max_time_in_seconds = min(45.0, rem)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = seed + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            proved_max = best_size
            status = "MAX_PROVED" if best_size > 0 else "INFEASIBLE_SCOPED"
            break
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT"
            if lb_extra > 0 and time.time() - t0 < time_s - 5:
                continue
            break
        sel = [p for p, v in z.items() if solver.Value(v) == 1]
        w = witnesses(sel)
        if not w:
            if len(sel) > best_size:
                best_size = len(sel)
                best_pts = sel
                print(json.dumps({"new_best": best_size, "round": rounds}), flush=True)
            lb_extra = best_size + 1
            if best_size >= 165:
                status = "FEASIBLE_GE165"
                break
            continue
        before = len(cuts)
        for trip in w:
            cuts.add(tuple(sorted(trip)))
        if len(cuts) == before:
            if time.time() - t0 < time_s - 5:
                continue
            break
        if rounds % 25 == 0:
            print(json.dumps({"round": rounds, "cuts": len(cuts), "best": best_size}), flush=True)

    out = {
        "status": status,
        "universe": len(free),
        "best_legal_size": best_size,
        "proved_max": proved_max,
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_s": time.time() - t0,
    }
    if best_pts:
        out["dual"] = dual(best_pts)
        out["best_hash"] = out["dual"]["hash"]
        out["points"] = [list(p) for p in best_pts]
    return out


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_grow_union_universe")
    os.makedirs(exp, exist_ok=True)
    workers = int(os.environ.get("W3_WORKERS", "4"))

    union: Set[Point] = set()
    grow_rows = []
    # Cheap multi-grow pool
    for seed, mode in [
        (202, "boundary_first"),
        (203, "spiral_mix"),
        (301, "boundary_first"),
        (401, "spiral_mix"),
        (501, "random"),
        (601, "center_first"),
        (701, "boundary_first"),
        (801, "spiral_mix"),
    ]:
        g = grow_legal(seed, mode, 75.0)
        grow_rows.append({k: v for k, v in g.items() if k != "points"})
        for p in g["points"]:
            union.add(tuple(p))
        print(json.dumps({"grow": grow_rows[-1], "union": len(union)}), flush=True)

    # Also include official S0 cells (reachable basin)
    from data.baselines.official_raw import SOL_100

    for x, y in SOL_100:
        union.add((int(x), int(y)))
    U = sorted(union)
    print(json.dumps({"universe_size": len(U), "cap": len(U)}), flush=True)
    json.dump(
        {"grow_rows": grow_rows, "universe_size": len(U), "universe": [list(p) for p in U]},
        open(os.path.join(exp, "universe.json"), "w"),
    )

    if len(U) < 165:
        out = {"schema": "w3_grow_union_v1", "status": "CAPACITY_FAIL", "universe": len(U), "any_plus": False}
        json.dump(out, open(os.path.join(exp, "summary.json"), "w"), indent=2)
        print(json.dumps(out, indent=2), flush=True)
        return

    # Screen: maximize inside union, 20 min
    print(json.dumps({"phase": "maximize_universe"}), flush=True)
    res = maximize_in_universe(U, 1200.0, workers, seed=3100, lb=130)
    row = {k: v for k, v in res.items() if k != "points"}
    print(json.dumps(row, indent=2), flush=True)
    if res.get("best_legal_size", 0) >= 165 and res.get("dual", {}).get("oracle"):
        json.dump(res, open(os.path.join(RUN, "CANDIDATES", "grow_union_legal.json"), "w"), indent=2)

    # Also: maximize_from_core using intersection of all grows as core if large enough
    # Skip if empty.

    out = {
        "schema": "w3_grow_union_v1",
        "grow_rows": grow_rows,
        "universe_size": len(U),
        "maximize": row,
        "best": row.get("best_legal_size", 0),
        "any_plus": row.get("best_legal_size", 0) >= 165,
    }
    json.dump(out, open(os.path.join(exp, "summary.json"), "w"), indent=2)
    print(json.dumps({"done": True, "best": out["best"], "any_plus": out["any_plus"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
