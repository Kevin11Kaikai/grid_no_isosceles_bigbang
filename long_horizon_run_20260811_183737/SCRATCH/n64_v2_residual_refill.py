#!/usr/bin/env python3
"""n64 sandbox: residual refill on Agent-C V=2 elites at |S|=113."""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from typing import List, Sequence, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]
N = 64
TARGET = 113


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


def witnesses(points):
    pts = [tuple(p) for p in points]
    out = []
    for pivot in pts:
        groups = defaultdict(list)
        for q in pts:
            if q == pivot:
                continue
            groups[sq(pivot, q)].append(q)
        for d, members in groups.items():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    out.append((pivot, members[i], members[j], d))
    return out


def cpsat_refill(core, pool, need, time_limit_s=60.0):
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
                    "dual": d,
                    "points": [list(p) for p in cand],
                    "rounds": rounds,
                    "cuts": cuts,
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
                for p in trip:
                    if p in core_set:
                        continue
                    if p in idx:
                        lits.append(addv[idx[p]])
                if not lits:
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
    }


def main():
    elite_dir = os.path.join(ROOT, "scratch", "agent_c", "elite_archive")
    elites = sorted(
        f for f in os.listdir(elite_dir) if f.startswith("n64_V2_") and f.endswith(".json")
    )
    results = []
    t_all = time.time()
    for name in elites[:6]:
        with open(os.path.join(elite_dir, name), encoding="utf-8") as f:
            data = json.load(f)
        points = [tuple(p) for p in data["points"]]
        assert len(points) == TARGET
        wits = witnesses(points)
        involved = sorted({p for w in wits for p in w[:3]})
        core = [p for p in points if p not in set(involved)]
        need = TARGET - len(core)
        v_core = conflict_count(core, N)
        ok_core, _ = is_legal_pivot_method(core, N)
        # pool = involved + halo r=5
        occ = set(points)
        pool_set = set(involved)
        for x, y in involved:
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < N and 0 <= ny < N:
                        p = (nx, ny)
                        if p not in set(core):
                            pool_set.add(p)
        pool = sorted(pool_set)
        row = {
            "elite": name,
            "V": conflict_count(points, N),
            "n_witness": len(wits),
            "n_involved": len(involved),
            "V_core": v_core,
            "core_legal": bool(ok_core),
            "need": need,
            "n_pool": len(pool),
        }
        if ok_core and v_core == 0:
            cpsat = cpsat_refill(core, pool, need, time_limit_s=45.0)
            row["cpsat"] = {k: cpsat[k] for k in cpsat if k != "points"}
            row["status"] = cpsat["status"]
            if cpsat["status"] == "FEASIBLE_LEGAL":
                row["dual"] = cpsat["dual"]
                row["points"] = cpsat["points"]
                cand_path = os.path.join(RUN, "CANDIDATES", f"n64_k113_from_{name}")
                os.makedirs(os.path.dirname(cand_path), exist_ok=True)
                with open(cand_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "n": 64,
                            "size": 113,
                            "points": cpsat["points"],
                            "dual": cpsat["dual"],
                            "source": name,
                        },
                        f,
                        indent=2,
                    )
        else:
            row["status"] = "CORE_ILLEGAL"
        results.append(row)

    out = {
        "schema": "lh1_n64_v2_residual_refill_v1",
        "results": results,
        "n_legal": sum(1 for r in results if r.get("status") == "FEASIBLE_LEGAL"),
        "wall_time_s": time.time() - t_all,
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH1_n64_sandbox")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "n64_v2_residual_refill.json")
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
                        "status": r.get("status"),
                        "n_involved": r.get("n_involved"),
                        "n_pool": r.get("n_pool"),
                        "best_V": (r.get("cpsat") or {}).get("best_illegal_V"),
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
