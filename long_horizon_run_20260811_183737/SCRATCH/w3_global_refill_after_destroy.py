#!/usr/bin/env python3
"""After structured destroy of S0, maximize legal extension over ALL individually-addable cells.

Unlike region-local MILP repair, free pool = every grid cell addable to the fixed core.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from ortools.sat.python import cp_model  # noqa: E402
from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]
N = 100


def sq(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def witnesses(points: Sequence[Point]):
    out = []
    for pivot in points:
        g: Dict[int, List[Point]] = defaultdict(list)
        for q in points:
            if q != pivot:
                g[sq(pivot, q)].append(q)
        for d, m in g.items():
            if len(m) < 2:
                continue
            for i in range(len(m)):
                for j in range(i + 1, len(m)):
                    out.append((pivot, m[i], m[j]))
    return out


def dual(pts):
    oka, _ = is_legal_pivot_method(pts, N)
    okb, _ = verify_independent(pts, N)
    return {"oracle": bool(oka), "indep": bool(okb), "size": len(pts), "hash": sha256_of_points(pts)}


def frame(depth):
    return [
        (x, y)
        for x in range(N)
        for y in range(N)
        if min(x, y, N - 1 - x, N - 1 - y) < depth
    ]


def maximize_from_core(core: List[Point], time_s: float, workers: int, seed: int) -> dict:
    st = IncrementalIsoscelesFreeSet(N)
    for p in core:
        assert st.add_point(p)
    free = []
    for x in range(N):
        for y in range(N):
            p = (x, y)
            if p in st.points:
                continue
            if st.can_add(p)[0]:
                free.append(p)
    print(json.dumps({"core": len(core), "free": len(free), "cap": len(core) + len(free)}), flush=True)
    if len(core) + len(free) < 165:
        return {
            "status": "CAPACITY_FAIL",
            "core": len(core),
            "free": len(free),
            "best_legal_size": len(core),
            "proved_max": len(core) + len(free),
        }

    cuts: Set[Tuple[Point, Point, Point]] = set()
    t0 = time.time()
    rounds = 0
    best_size = len(core)
    best_pts = list(core)
    lb_extra = 0
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
        solver.parameters.max_time_in_seconds = min(30.0, rem)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = seed + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            proved_max = best_size
            status = "MAX_PROVED"
            break
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT"
            break
        sel = list(core) + [p for p, v in z.items() if solver.Value(v) == 1]
        w = witnesses(sel)
        if not w:
            if len(sel) > best_size:
                best_size = len(sel)
                best_pts = sel
                print(json.dumps({"new_best": best_size, "round": rounds}), flush=True)
            lb_extra = best_size - len(core) + 1
            if best_size >= 165:
                status = "FEASIBLE_GE165"
                break
            continue
        before = len(cuts)
        for trip in w:
            cuts.add(tuple(sorted(trip)))
        if len(cuts) == before:
            status = "TIMEOUT"
            break
        if rounds % 50 == 0:
            print(json.dumps({"round": rounds, "cuts": len(cuts), "best": best_size}), flush=True)

    out = {
        "status": status,
        "core": len(core),
        "free": len(free),
        "best_legal_size": best_size,
        "proved_max": proved_max,
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_s": time.time() - t0,
    }
    if best_size >= 165:
        out["dual"] = dual(best_pts)
        out["points"] = [list(p) for p in best_pts]
    elif best_size > len(core):
        out["dual"] = dual(best_pts)
        out["best_hash"] = out["dual"]["hash"]
    return out


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_global_refill")
    os.makedirs(exp, exist_ok=True)
    s0 = set((int(x), int(y)) for x, y in SOL_100)
    workers = int(os.environ.get("W3_WORKERS", "4"))
    per = float(os.environ.get("W3_PER_S", "600"))
    rows = []
    for depth in (2, 3, 4):
        rem = [p for p in frame(depth) if p in s0]
        core = sorted(s0 - set(rem))
        print(json.dumps({"plan": f"frame_d{depth}", "removed": len(rem), "core": len(core)}), flush=True)
        res = maximize_from_core(core, per, workers, seed=1400 + depth)
        row = {k: v for k, v in res.items() if k != "points"}
        row["plan"] = f"frame_d{depth}"
        row["n_removed"] = len(rem)
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("status") == "FEASIBLE_GE165" and res.get("points"):
            cand = os.path.join(RUN, "CANDIDATES", f"global_refill_frame_d{depth}_legal.json")
            json.dump(res, open(cand, "w"), indent=2)
            break

    out = {
        "schema": "w3_global_refill_v1",
        "rows": rows,
        "any_plus": any(r.get("best_legal_size", 0) >= 165 for r in rows),
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
    }
    path = os.path.join(exp, "summary.json")
    json.dump(out, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    print(json.dumps({"done": True, **{k: out[k] for k in ("any_plus", "best")}}, indent=2), flush=True)


if __name__ == "__main__":
    main()
