#!/usr/bin/env python3
"""LH-1: Expand residual Rem beyond witness-involved points.

For each V=3 elite: free involved ∪ spatial neighbors in S, refill to |S|=165
from freed ∪ halo. Tests whether CORE_STILL too large was the issue.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from typing import List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]
N = 100


def dual(points):
    pts = [tuple(p) for p in points]
    ok_a, _ = is_legal_pivot_method(pts, N)
    ok_b, _ = verify_independent(pts, N)
    return {
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "V": int(conflict_count(pts, N)),
        "size": len(pts),
        "hash": sha256_of_points(pts),
    }


def sq(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def cpsat_refill(core, pool, need, time_limit_s=90.0):
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    addv = [model.NewBoolVar(f"a{i}") for i in range(len(pool))]
    model.Add(sum(addv) == need)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = max(1, (os.cpu_count() or 4) // 4)
    cuts = 0
    rounds = 0
    best_v = 10**9
    t0 = time.time()
    status = "UNKNOWN"
    while time.time() - t0 < time_limit_s:
        rounds += 1
        solver.parameters.max_time_in_seconds = max(1.0, time_limit_s - (time.time() - t0))
        res = solver.Solve(model)
        if res == cp_model.INFEASIBLE:
            status = "INFEASIBLE_SCOPED"
            break
        if res not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT_INCONCLUSIVE"
            break
        added = [pool[i] for i, v in enumerate(addv) if solver.Value(v) == 1]
        cand = sorted(core + added)
        v = conflict_count(cand, N)
        best_v = min(best_v, v)
        if v == 0:
            d = dual(cand)
            if d["oracle_legal"] and d["independent_legal"]:
                return {
                    "status": "FEASIBLE_LEGAL",
                    "rounds": rounds,
                    "cuts": cuts,
                    "dual": d,
                    "points": [list(p) for p in cand],
                }
        pts = [tuple(p) for p in cand]
        core_set = set(core)
        idx = {p: i for i, p in enumerate(pool)}
        cut_added = False
        for pivot in pts:
            groups = defaultdict(list)
            for q in pts:
                if q == pivot:
                    continue
                groups[sq(pivot, q)].append(q)
            for members in groups.values():
                if len(members) < 2:
                    continue
                trip = [pivot, members[0], members[1]]
                lits = []
                forced = 0
                for p in trip:
                    if p in core_set:
                        forced += 1
                    elif p in idx:
                        lits.append(addv[idx[p]])
                if forced == 3 or not lits:
                    continue
                model.AddBoolOr([lit.Not() for lit in lits])
                cuts += 1
                cut_added = True
                break
            if cut_added:
                break
        if not cut_added:
            status = "ERROR_NO_CUT"
            break
    else:
        status = "TIMEOUT_INCONCLUSIVE"
    return {
        "status": status,
        "rounds": rounds,
        "cuts": cuts,
        "best_illegal_V": best_v if best_v < 10**9 else None,
        "wall_s": time.time() - t0,
    }


def main():
    with open(
        os.path.join(RUN, "EXPERIMENTS", "LH1_v3_residual", "v3_residual_n100.json"),
        encoding="utf-8",
    ) as f:
        residual = json.load(f)
    elite_dir = os.path.join(ROOT, "scratch", "agent_c", "elite_archive")
    # Only first 3 distinct-ish elites to save budget; then escalate if signal
    results = []
    t_all = time.time()
    for erow in residual["elites"][:4]:
        name = erow["file"]
        with open(os.path.join(elite_dir, name), encoding="utf-8") as f:
            data = json.load(f)
        points = [tuple(p) for p in data["points"]]
        involved = [tuple(p) for p in erow["involved_points"]]
        inv = set(involved)
        # expand free set: involved + all S points within chebyshev R of any involved
        for R_free, R_halo, budget in [(2, 5, 90.0), (3, 6, 120.0)]:
            free: Set[Point] = set(inv)
            for p in points:
                if p in inv:
                    continue
                for ix, iy in inv:
                    if max(abs(p[0] - ix), abs(p[1] - iy)) <= R_free:
                        free.add(p)
                        break
            core = [p for p in points if p not in free]
            need = 165 - len(core)
            v_core = conflict_count(core, N)
            ok_core, _ = is_legal_pivot_method(core, N)
            # pool = free ∪ empty halo around free
            occ = set(points)
            pool_set = set(free)
            for x, y in free:
                for dx in range(-R_halo, R_halo + 1):
                    for dy in range(-R_halo, R_halo + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < N and 0 <= ny < N:
                            p = (nx, ny)
                            if p not in set(core):
                                pool_set.add(p)
            pool = sorted(pool_set)
            row = {
                "elite": name,
                "R_free": R_free,
                "R_halo": R_halo,
                "n_free": len(free),
                "n_core": len(core),
                "need": need,
                "V_core": v_core,
                "core_legal": bool(ok_core),
                "n_pool": len(pool),
            }
            if not ok_core:
                row["status"] = "CORE_ILLEGAL"
                results.append(row)
                continue
            cpsat = cpsat_refill(core, pool, need, time_limit_s=budget)
            row["cpsat"] = {k: cpsat[k] for k in cpsat if k != "points"}
            row["status"] = cpsat["status"]
            if cpsat["status"] == "FEASIBLE_LEGAL":
                row["dual"] = cpsat["dual"]
                row["points"] = cpsat["points"]
                results.append(row)
                break
            results.append(row)

    out = {
        "schema": "lh1_expanded_residual_refill_v1",
        "results": results,
        "n_legal": sum(1 for r in results if r.get("status") == "FEASIBLE_LEGAL"),
        "wall_time_s": time.time() - t_all,
    }
    path = os.path.join(
        RUN, "EXPERIMENTS", "LH1_v3_residual", "expanded_residual_refill.json"
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "path": path,
                "n_legal": out["n_legal"],
                "summaries": [
                    {
                        "elite": r["elite"],
                        "R_free": r["R_free"],
                        "need": r["need"],
                        "n_pool": r["n_pool"],
                        "status": r["status"],
                        "best_V": (r.get("cpsat") or {}).get("best_illegal_V"),
                        "cuts": (r.get("cpsat") or {}).get("cuts"),
                    }
                    for r in results
                ],
                "wall_s": out["wall_time_s"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
