#!/usr/bin/env python3
"""LH-1 Route C/D: exact residual repair on V=3 elites (tiny involved sets).

For each elite with ~3 witness triples / ~6-7 involved points:
  - Try 1-removal + 1-add over involved × empty-halo
  - Try 2-removal + 2-add over involved pairs × halo (capped)
  - Optionally CP-SAT Hamming-style on Rem=involved, Add=halo, r in {1,2,3}
    keeping cardinality 165 (i.e. |add|=|rem|).

Does NOT claim global results. Writes under this run only.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
from typing import List, Optional, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import (  # noqa: E402
    verify_independent,
)

Point = Tuple[int, int]
N = 100


def load_residual() -> dict:
    path = os.path.join(RUN, "EXPERIMENTS", "LH1_v3_residual", "v3_residual_n100.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def halo_around(points: Sequence[Point], radius: int, occupied: Set[Point]) -> List[Point]:
    out: Set[Point] = set()
    for x, y in points:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N:
                    p = (nx, ny)
                    if p not in occupied:
                        out.add(p)
    return sorted(out)


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


def try_swap1(
    points: List[Point], involved: List[Point], add_pool: List[Point]
) -> Optional[dict]:
    base = set(points)
    scanned = 0
    for rem in involved:
        core = base - {rem}
        state = IncrementalIsoscelesFreeSet(N)
        for p in core:
            assert state.add_point(p)
        for add in add_pool:
            if add in core:
                continue
            scanned += 1
            ok, _ = state.can_add(add)
            if ok:
                pts = sorted(core | {add})
                d = dual(pts)
                if d["oracle_legal"] and d["independent_legal"] and d["V"] == 0:
                    return {
                        "mode": "swap1",
                        "removed": list(rem),
                        "added": list(add),
                        "dual": d,
                        "points": [list(p) for p in pts],
                        "scanned": scanned,
                    }
    return {"mode": "swap1", "found": False, "scanned": scanned}


def try_swap2(
    points: List[Point],
    involved: List[Point],
    add_pool: List[Point],
    max_pair_adds: int = 8000,
) -> Optional[dict]:
    base = set(points)
    pairs = list(itertools.combinations(involved, 2))
    checked = 0
    for r1, r2 in pairs:
        core = base - {r1, r2}
        state = IncrementalIsoscelesFreeSet(N)
        for p in core:
            assert state.add_point(p)
        solo = []
        for a in add_pool:
            if a in core:
                continue
            ok, _ = state.can_add(a)
            if ok:
                solo.append(a)
        if len(solo) < 2:
            continue
        for a, b in itertools.combinations(solo[:120], 2):
            checked += 1
            if checked > max_pair_adds:
                return {"mode": "swap2", "found": False, "pairs_checked": checked, "capped": True}
            ok_a, _ = state.can_add(a)
            if not ok_a:
                continue
            state.add_point(a)
            ok_b, _ = state.can_add(b)
            if ok_b:
                pts = sorted(core | {a, b})
                d = dual(pts)
                if d["oracle_legal"] and d["independent_legal"] and d["V"] == 0:
                    return {
                        "mode": "swap2",
                        "removed": [list(r1), list(r2)],
                        "added": [list(a), list(b)],
                        "dual": d,
                        "points": [list(p) for p in pts],
                        "pairs_checked": checked,
                    }
            state.remove_point(a)
    return {"mode": "swap2", "found": False, "pairs_checked": checked}


def cpsat_card_preserve(
    points: List[Point],
    involved: List[Point],
    add_pool: List[Point],
    time_limit_s: float = 60.0,
) -> dict:
    """Use hamming_shell_conflict with r such that |S|=165: rem from involved, add from pool,
    but shell model is about S0 baseline — here elite is not baseline.

    Instead: fixed = points\\involved; choose keep subset of involved and add subset of pool
    with |keep|+|add| = |involved|, maximize legality via lazy CP-SAT if ortools available.
    """
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        return {"status": "NO_ORTOOLS"}

    fixed = [p for p in points if p not in set(involved)]
    rem_vars_pts = list(involved)
    add_vars_pts = list(add_pool)
    k = len(rem_vars_pts)
    model = cp_model.CpModel()
    keep = [model.NewBoolVar(f"k{i}") for i in range(k)]
    addv = [model.NewBoolVar(f"a{i}") for i in range(len(add_vars_pts))]
    # cardinality: sum keep + sum add = k  => size = |fixed|+k = 165
    model.Add(sum(keep) + sum(addv) == k)
    # soft: prefer solutions; objective dummy
    model.Maximize(sum(addv))  # diversify toward using new points

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_s
    solver.parameters.num_search_workers = max(1, (os.cpu_count() or 4) // 4)

    # Lazy cut loop
    cuts = 0
    rounds = 0
    best_v = 10**9
    status_name = "UNKNOWN"
    t0 = time.time()
    while time.time() - t0 < time_limit_s:
        rounds += 1
        res = solver.Solve(model)
        if res == cp_model.INFEASIBLE:
            status_name = "INFEASIBLE_SCOPED"
            break
        if res not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status_name = "TIMEOUT_INCONCLUSIVE"
            break
        kept = [rem_vars_pts[i] for i, v in enumerate(keep) if solver.Value(v) == 1]
        added = [add_vars_pts[i] for i, v in enumerate(addv) if solver.Value(v) == 1]
        cand = sorted(fixed + kept + added)
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
                    "kept_involved": [list(p) for p in kept],
                    "added": [list(p) for p in added],
                }
        # add witness cuts: for each witness triple among cand, forbid that combination
        # Encode: cannot have all three points selected under keep/add/fixed.
        # Fixed points always present — if a witness is entirely in fixed, model is broken.
        ok, wit = is_legal_pivot_method(cand, N)
        assert not ok
        # find one witness via groups
        from collections import defaultdict

        def sq(a, b):
            return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

        cut_added = False
        pts = [tuple(p) for p in cand]
        for pivot in pts:
            groups = defaultdict(list)
            for q in pts:
                if q == pivot:
                    continue
                groups[sq(pivot, q)].append(q)
            for members in groups.values():
                if len(members) < 2:
                    continue
                a, b = members[0], members[1]
                trip = [pivot, a, b]
                # literals that are selectable
                lits = []
                fixed_set = set(fixed)
                inv_index = {p: i for i, p in enumerate(rem_vars_pts)}
                add_index = {p: i for i, p in enumerate(add_vars_pts)}
                forced = 0
                for p in trip:
                    if p in fixed_set:
                        forced += 1
                        continue
                    if p in inv_index:
                        lits.append(keep[inv_index[p]])
                    elif p in add_index:
                        lits.append(addv[add_index[p]])
                if forced == 3:
                    # impossible to cut — residual involves only fixed (should not happen)
                    continue
                if not lits:
                    continue
                # forbid all lits true
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
    }


def main() -> None:
    residual = load_residual()
    elite_dir = os.path.join(ROOT, "scratch", "agent_c", "elite_archive")
    results = []
    t_all = time.time()
    for erow in residual["elites"]:
        name = erow["file"]
        with open(os.path.join(elite_dir, name), "r", encoding="utf-8") as f:
            data = json.load(f)
        points = [tuple(p) for p in data["points"]]
        involved = [tuple(p) for p in erow["involved_points"]]
        occupied = set(points)
        pool = halo_around(involved, radius=5, occupied=occupied)
        # also include all currently empty? too big — stick to halo + maybe ring-0..2 boundary empties near involved
        t0 = time.time()
        hit1 = try_swap1(points, involved, pool)
        if hit1 and "dual" in hit1:
            results.append({"elite": name, "repair": hit1, "wall_s": time.time() - t0})
            continue
        hit2 = try_swap2(points, involved, pool, max_pair_adds=12000)
        if hit2 and hit2.get("dual"):
            results.append({"elite": name, "repair": hit2, "wall_s": time.time() - t0})
            continue
        # CP-SAT residual
        cpsat = cpsat_card_preserve(points, involved, pool, time_limit_s=45.0)
        results.append(
            {
                "elite": name,
                "n_involved": len(involved),
                "n_add_pool": len(pool),
                "swap1": hit1,
                "swap2": hit2,
                "cpsat": cpsat,
                "wall_s": time.time() - t0,
            }
        )

    legal = [
        r
        for r in results
        if (r.get("repair") or {}).get("dual", {}).get("oracle_legal")
        or (r.get("cpsat") or {}).get("status") == "FEASIBLE_LEGAL"
    ]
    out = {
        "schema": "lh1_v3_residual_exact_repair_v1",
        "n_elites_tried": len(results),
        "n_legal_found": len(legal),
        "results": results,
        "legal": legal,
        "wall_time_s": time.time() - t_all,
        "claim_discipline": "If legal found: freeze + dual already in dual(); still need certificate bundle before incumbent promote.",
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH1_v3_residual")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "v3_exact_repair_n100.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "path": path,
                "n_elites_tried": out["n_elites_tried"],
                "n_legal_found": out["n_legal_found"],
                "statuses": [
                    {
                        "elite": r.get("elite"),
                        "has_repair": "repair" in r and "dual" in r.get("repair", {}),
                        "cpsat": (r.get("cpsat") or {}).get("status"),
                        "swap2_checked": (r.get("swap2") or {}).get("pairs_checked"),
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
