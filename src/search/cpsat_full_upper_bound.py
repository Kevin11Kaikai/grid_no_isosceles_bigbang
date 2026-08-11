"""Round 2 bonus, high-risk/high-reward attempt: a FULLY (not lazily) enumerated
CP-SAT feasibility model for a single n, targeting a genuine complete-constraint
upper-bound proof attempt.

Unlike `cpsat_lazy.py` (which adds constraints incrementally as violations are
discovered, because the full constraint set is assumed too large to enumerate
eagerly), this script enumerates the ENTIRE forbidden-triple constraint set for
one specific n up front (every grid point as apex, every equidistant pair of
other grid points), then issues a single CP-SAT feasibility solve for
`sum(x) >= target`. Because the constraint set is complete (not a subset), a
terminal status of:
  - INFEASIBLE  -> C(n) < target, a genuine complete upper-bound proof (Level 5
    if target - 1 matches an already-certified lower bound).
  - FEASIBLE    -> a genuinely legal construction of size >= target (re-verified
    against the pure-Python oracle before being trusted at all).
  - time-limit / unknown -> inconclusive; the enumerated constraint count and
    wall-clock spent are still a reportable, honest data point about
    tractability at this n.

This is expensive to even build (tens of millions of individual constraints for
n=64) and is explicitly an exploratory, bounded-time attempt, not a claim that
it will complete. Must be run under the project-local venv (ortools).
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.search.cpsat_lazy import seed_cuts_from_points
from src.verification.oracle_verifier import is_legal_pivot_method

from ortools.sat.python import cp_model


def run(n: int, target: int, solve_time_limit_s: float, seed: int = 1, max_cuts: int = 60_000_000):
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    idx = {p: i for i, p in enumerate(all_pts)}
    m = len(all_pts)

    t0 = time.time()
    print(f"[t={time.time()-t0:.1f}s] enumerating FULL constraint set for n={n} ...", flush=True)
    cuts = seed_cuts_from_points(n, all_pts, idx, max_cuts=max_cuts)
    enum_time = time.time() - t0
    print(f"[t={time.time()-t0:.1f}s] enumerated {len(cuts)} constraints in {enum_time:.1f}s; building model ...", flush=True)

    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(m)]
    for k, (pi, ai, bi) in enumerate(cuts):
        model.Add(x[pi] + x[ai] + x[bi] <= 2)
        if k % 2_000_000 == 0 and k > 0:
            print(f"[t={time.time()-t0:.1f}s] added {k}/{len(cuts)} constraints ...", flush=True)
    model.Add(sum(x) >= target)
    build_time = time.time() - t0 - enum_time
    print(f"[t={time.time()-t0:.1f}s] model built ({build_time:.1f}s for constraint-adding); solving (limit {solve_time_limit_s}s) ...", flush=True)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = solve_time_limit_s
    solver.parameters.random_seed = seed
    solver.parameters.num_search_workers = 16
    status = solver.Solve(model)
    solve_time = time.time() - t0 - enum_time - build_time

    result = {
        "n": n,
        "target": target,
        "num_constraints": len(cuts),
        "enum_time_s": enum_time,
        "build_time_s": build_time,
        "solve_time_s": solve_time,
        "total_time_s": time.time() - t0,
        "status": solver.StatusName(status),
    }

    if status == cp_model.INFEASIBLE:
        result["verdict"] = f"COMPLETE UPPER BOUND PROVEN: C({n}) < {target}"
    elif status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        selected = [all_pts[i] for i in range(m) if solver.Value(x[i]) == 1]
        ok, witness = is_legal_pivot_method(selected, n)
        result["oracle_legal"] = ok
        if ok:
            result["verdict"] = f"NEW CANDIDATE FOUND: legal set of size {len(selected)} >= target {target}"
            result["points"] = selected
        else:
            result["verdict"] = "ENCODING BUG: CP-SAT solution rejected by independent oracle -- DO NOT TRUST, investigate cut-generation code"
            result["oracle_witness"] = witness
    else:
        result["verdict"] = "INCONCLUSIVE within time budget"

    print(json.dumps({k: v for k, v in result.items() if k != "points"}, indent=2), flush=True)
    os.makedirs("logs", exist_ok=True)
    out = f"logs/cpsat_full_upperbound_n{n}_target{target}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"wrote {out}", flush=True)
    return result


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    target = int(sys.argv[2]) if len(sys.argv) > 2 else (113 if n == 64 else 165)
    solve_time_limit = float(sys.argv[3]) if len(sys.argv) > 3 else 3600.0
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    run(n, target, solve_time_limit, seed=seed)
