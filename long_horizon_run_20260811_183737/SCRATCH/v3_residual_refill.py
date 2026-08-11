#!/usr/bin/env python3
"""LH-1: Residual refill — strip all involved points (should leave legal core),
then choose |involved| replacements from involved∪halo to restore |S|=165 with V=0.

Uses IncrementalIsoscelesFreeSet only on a verified-legal core.
Also runs CP-SAT lazy cuts over keep/add variables.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
from collections import defaultdict
from typing import List, Optional, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]
N = 100


def dual(points: Sequence[Point]) -> dict:
    pts = [tuple(p) for p in points]
    ok_a, _ = is_legal_pivot_method(pts, N)  # type: ignore[arg-type]
    ok_b, _ = verify_independent(pts, N)
    return {
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "V": int(conflict_count(pts, N)),
        "size": len(pts),
        "hash": sha256_of_points(pts),
    }


def sq(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def halo(points: Sequence[Point], radius: int, blocked: Set[Point]) -> List[Point]:
    out: Set[Point] = set()
    for x, y in points:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N:
                    p = (nx, ny)
                    if p not in blocked:
                        out.add(p)
    return sorted(out)


def greedy_refill(core: List[Point], pool: List[Point], need: int) -> Optional[List[Point]]:
    state = IncrementalIsoscelesFreeSet(N)
    for p in core:
        if not state.add_point(p):
            return None
    chosen = []
    # multi-pass randomized-ish: order by how many conflicts... just sequential + retries
    remaining = list(pool)
    # Try deterministic: repeatedly add first can_add
    progress = True
    while len(chosen) < need and progress:
        progress = False
        for p in remaining:
            ok, _ = state.can_add(p)
            if ok:
                state.add_point(p)
                chosen.append(p)
                remaining = [q for q in remaining if q != p]
                progress = True
                break
    if len(chosen) == need:
        return sorted(core + chosen)
    return None


def brute_small_refill(
    core: List[Point], pool: List[Point], need: int, max_combos: int = 200000
) -> Optional[dict]:
    """If pool small enough relative to need, enum combinations with incremental prune."""
    # Beam: build by depth with can_add
    state0 = IncrementalIsoscelesFreeSet(N)
    for p in core:
        assert state0.add_point(p)
    # Get solo-feasible first
    solo = []
    for p in pool:
        ok, _ = state0.can_add(p)
        if ok:
            solo.append(p)
    if len(solo) < need:
        return {"status": "TOO_FEW_SOLO", "n_solo": len(solo), "need": need}

    checked = 0
    # Prefer combinations that include few original involved — handled by caller pool order
    for comb in itertools.combinations(solo, need):
        checked += 1
        if checked > max_combos:
            return {"status": "CAPPED", "checked": checked, "n_solo": len(solo)}
        st = IncrementalIsoscelesFreeSet(N)
        for p in core:
            st.add_point(p)
        ok_all = True
        for p in comb:
            ok, _ = st.can_add(p)
            if not ok:
                ok_all = False
                break
            st.add_point(p)
        if ok_all:
            pts = sorted(core + list(comb))
            d = dual(pts)
            if d["V"] == 0 and d["oracle_legal"] and d["independent_legal"]:
                return {
                    "status": "FEASIBLE_LEGAL",
                    "checked": checked,
                    "added": [list(p) for p in comb],
                    "dual": d,
                    "points": [list(p) for p in pts],
                }
    return {"status": "EXHAUSTED_NO_LEGAL", "checked": checked, "n_solo": len(solo)}


def cpsat_refill(
    core: List[Point], pool: List[Point], need: int, time_limit_s: float = 90.0
) -> dict:
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        return {"status": "NO_ORTOOLS"}

    model = cp_model.CpModel()
    addv = [model.NewBoolVar(f"a{i}") for i in range(len(pool))]
    model.Add(sum(addv) == need)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = min(30.0, time_limit_s)
    solver.parameters.num_search_workers = max(1, (os.cpu_count() or 4) // 4)

    cuts = 0
    rounds = 0
    best_v = 10**9
    t0 = time.time()
    status_name = "UNKNOWN"
    while time.time() - t0 < time_limit_s:
        rounds += 1
        # refresh time per round
        solver.parameters.max_time_in_seconds = max(1.0, time_limit_s - (time.time() - t0))
        res = solver.Solve(model)
        if res == cp_model.INFEASIBLE:
            status_name = "INFEASIBLE_SCOPED"
            break
        if res not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status_name = "TIMEOUT_INCONCLUSIVE"
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
                    "added": [list(p) for p in added],
                    "points": [list(p) for p in cand],
                }
        # witness cut
        pts = [tuple(p) for p in cand]
        cut_added = False
        core_set = set(core)
        idx = {p: i for i, p in enumerate(pool)}
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
                if forced == 3:
                    continue
                if not lits:
                    continue
                model.AddBoolOr([lit.Not() for lit in lits])
                cuts += 1
                cut_added = True
                break
            if cut_added:
                break
        if not cut_added:
            status_name = "ERROR_NO_CUT"
            break
    else:
        status_name = "TIMEOUT_INCONCLUSIVE"
    return {
        "status": status_name,
        "rounds": rounds,
        "cuts": cuts,
        "best_illegal_V": best_v if best_v < 10**9 else None,
        "wall_s": time.time() - t0,
        "n_pool": len(pool),
        "need": need,
    }


def main() -> None:
    residual_path = os.path.join(RUN, "EXPERIMENTS", "LH1_v3_residual", "v3_residual_n100.json")
    with open(residual_path, encoding="utf-8") as f:
        residual = json.load(f)
    elite_dir = os.path.join(ROOT, "scratch", "agent_c", "elite_archive")
    results = []
    t_all = time.time()
    for erow in residual["elites"]:
        name = erow["file"]
        with open(os.path.join(elite_dir, name), encoding="utf-8") as f:
            data = json.load(f)
        points = [tuple(p) for p in data["points"]]
        involved = [tuple(p) for p in erow["involved_points"]]
        inv_set = set(involved)
        core = [p for p in points if p not in inv_set]
        need = len(involved)  # restore |S|=165
        assert len(core) + need == 165
        v_core = conflict_count(core, N)
        ok_core, _ = is_legal_pivot_method(core, N)
        occupied = set(points)
        pool = sorted(set(involved) | set(halo(involved, 6, occupied - inv_set)))
        # pool may include involved (re-keep) and new halo cells; exclude core
        pool = [p for p in pool if p not in set(core)]

        row = {
            "elite": name,
            "n_involved": len(involved),
            "n_core": len(core),
            "V_core": v_core,
            "core_legal": bool(ok_core),
            "n_pool": len(pool),
            "need": need,
        }
        if not ok_core or v_core != 0:
            row["status"] = "CORE_STILL_ILLEGAL"
            results.append(row)
            continue

        t0 = time.time()
        # Brute if C(n_solo, need) manageable — need~6-7, solo often dozens
        brute = brute_small_refill(core, pool, need, max_combos=50000)
        row["brute"] = {k: brute.get(k) for k in brute if k != "points"}
        if brute.get("status") == "FEASIBLE_LEGAL":
            row["status"] = "FEASIBLE_LEGAL"
            row["dual"] = brute["dual"]
            row["points"] = brute["points"]
            row["wall_s"] = time.time() - t0
            results.append(row)
            # freeze candidate
            cand_dir = os.path.join(RUN, "CANDIDATES")
            os.makedirs(cand_dir, exist_ok=True)
            with open(
                os.path.join(cand_dir, f"n100_k165_from_{name}"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    {
                        "n": 100,
                        "size": 165,
                        "points": brute["points"],
                        "dual": brute["dual"],
                        "source_elite": name,
                        "method": "v3_residual_refill_brute",
                    },
                    f,
                    indent=2,
                )
            continue

        cpsat = cpsat_refill(core, pool, need, time_limit_s=120.0)
        row["cpsat"] = {k: cpsat.get(k) for k in cpsat if k != "points"}
        if cpsat.get("status") == "FEASIBLE_LEGAL":
            row["status"] = "FEASIBLE_LEGAL"
            row["dual"] = cpsat["dual"]
            row["points"] = cpsat["points"]
            cand_dir = os.path.join(RUN, "CANDIDATES")
            os.makedirs(cand_dir, exist_ok=True)
            with open(
                os.path.join(cand_dir, f"n100_k165_cpsat_from_{name}"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    {
                        "n": 100,
                        "size": 165,
                        "points": cpsat["points"],
                        "dual": cpsat["dual"],
                        "source_elite": name,
                        "method": "v3_residual_refill_cpsat",
                    },
                    f,
                    indent=2,
                )
        else:
            row["status"] = cpsat.get("status") or brute.get("status")
        row["wall_s"] = time.time() - t0
        results.append(row)

    out = {
        "schema": "lh1_v3_residual_refill_v1",
        "n_elites": len(results),
        "n_legal": sum(1 for r in results if r.get("status") == "FEASIBLE_LEGAL"),
        "n_core_illegal": sum(1 for r in results if r.get("status") == "CORE_STILL_ILLEGAL"),
        "results": results,
        "wall_time_s": time.time() - t_all,
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH1_v3_residual")
    path = os.path.join(exp, "v3_residual_refill_n100.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "path": path,
                "n_elites": out["n_elites"],
                "n_legal": out["n_legal"],
                "n_core_illegal": out["n_core_illegal"],
                "summaries": [
                    {
                        "elite": r["elite"],
                        "status": r.get("status"),
                        "V_core": r.get("V_core"),
                        "n_pool": r.get("n_pool"),
                        "brute": (r.get("brute") or {}).get("status"),
                        "cpsat": (r.get("cpsat") or {}).get("status"),
                        "best_V": (r.get("cpsat") or {}).get("best_illegal_V"),
                        "wall_s": r.get("wall_s"),
                    }
                    for r in results
                ],
                "wall_time_s": out["wall_time_s"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
