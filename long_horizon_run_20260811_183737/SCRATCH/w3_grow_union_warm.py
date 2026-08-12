#!/usr/bin/env python3
"""Warm-start grow-union maximize from best grow legal set (fix empty-LB bug)."""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from ortools.sat.python import cp_model  # noqa: E402
from w3_global_refill_after_destroy import dual, witnesses  # noqa: E402
from w3_joint_hs_and_grow_destroy import grow_legal  # noqa: E402

N = 100


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_grow_union_universe")
    os.makedirs(exp, exist_ok=True)
    workers = int(os.environ.get("W3_WORKERS", "4"))

    uni_path = os.path.join(exp, "universe.json")
    if os.path.exists(uni_path):
        uni = json.load(open(uni_path))
        U = [tuple(p) for p in uni["universe"]]
        print(json.dumps({"reused_universe": len(U)}), flush=True)
    else:
        raise SystemExit("missing universe.json")

    # Warm start: short grow inside modes, pick best legal subset of U if needed
    # Prefer regenerate one strong grow and intersect? Better: grow freely then project not needed —
    # just grow and take points (all grow points are in U by construction if we rebuild).
    # Use fresh grow for warm start points.
    best_pts = None
    best_size = 0
    for seed, mode in ((202, "boundary_first"), (203, "spiral_mix"), (901, "boundary_first")):
        g = grow_legal(seed, mode, 90.0)
        print(json.dumps({"warm_grow": {k: v for k, v in g.items() if k != "points"}}), flush=True)
        if g["oracle"] and g["indep"] and g["size"] > best_size:
            best_size = g["size"]
            best_pts = [tuple(p) for p in g["points"]]
            # ensure in universe
            missing = [p for p in best_pts if p not in set(U)]
            if missing:
                U = sorted(set(U) | set(best_pts))
                print(json.dumps({"expanded_universe": len(U), "added": len(missing)}), flush=True)

    free = list(U)
    cuts = set()
    t0 = time.time()
    time_s = 1500.0
    lb_extra = best_size + 1
    rounds = 0
    status = "TIMEOUT"
    proved_max = None
    while time.time() - t0 < time_s:
        rounds += 1
        model = cp_model.CpModel()
        z = {p: model.NewBoolVar(f"z{p[0]}_{p[1]}") for p in free}
        model.Maximize(sum(z.values()))
        model.Add(sum(z.values()) >= lb_extra)
        for trip in cuts:
            free_in = [z[p] for p in trip if p in z]
            if free_in:
                model.Add(sum(free_in) <= len(free_in) - 1)
        solver = cp_model.CpSolver()
        rem = max(0.5, time_s - (time.time() - t0))
        solver.parameters.max_time_in_seconds = min(45.0, rem)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = 3200 + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            proved_max = best_size
            status = "MAX_PROVED"
            break
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT"
            if time.time() - t0 < time_s - 5:
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
        if len(cuts) == before and time.time() - t0 >= time_s - 5:
            break
        if rounds % 20 == 0:
            print(json.dumps({"round": rounds, "cuts": len(cuts), "best": best_size, "lb": lb_extra}), flush=True)

    out = {
        "schema": "w3_grow_union_warm_v1",
        "status": status,
        "universe": len(free),
        "best_legal_size": best_size,
        "proved_max": proved_max,
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_s": time.time() - t0,
        "dual": dual(best_pts) if best_pts else None,
    }
    if best_pts:
        out["points"] = [list(p) for p in best_pts]
        out["best_hash"] = out["dual"]["hash"]
    path = os.path.join(exp, "summary_warm.json")
    json.dump({k: v for k, v in out.items() if k != "points"}, open(path, "w"), indent=2)
    if best_pts and best_size >= 165 and out["dual"]["oracle"] and out["dual"]["indep"]:
        json.dump(out, open(os.path.join(RUN, "CANDIDATES", "grow_union_warm_legal.json"), "w"), indent=2)
    print(json.dumps({k: out[k] for k in out if k != "points"}, indent=2), flush=True)
    print(json.dumps({"done_warm": True, "best": best_size, "any_plus": best_size >= 165}, indent=2), flush=True)


if __name__ == "__main__":
    main()
