"""Round 2 bonus: attempt genuine EXACT C(n) values for small n via CP-SAT.

For each small n: get a strong lower bound quickly (greedy multistart), then
attempt `cpsat_prove_upper_bound(n, target=best_found+1, ...)`. Because
infeasibility under a lazily-relaxed (partial) constraint set is already a
valid infeasibility certificate for the true fully-constrained problem (see
docstring in `cpsat_lazy.py`), an INFEASIBLE_PROVEN result here is a genuine,
machine-checked EXACT optimum for that n -- not just a lower bound. Must be
run under the project-local venv (`.venv_solver`), which has ortools; the
rest of the project's oracle/greedy code has no such dependency and works
under either interpreter.
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.search.cpsat_lazy import cpsat_prove_upper_bound
from src.search.greedy import greedy_multistart
from src.verification.oracle_verifier import is_legal_pivot_method


def sweep(ns, lb_budget_s=60.0, ub_budget_s=300.0, per_round_time_limit_s=30.0, seed=1):
    results = {}
    for n in ns:
        t0 = time.time()
        best, lb_meta = greedy_multistart(
            n, num_starts=10**9, time_budget_s=lb_budget_s, seed0=seed,
            orders=("random", "boundary_first", "center_first"),
        )
        ok, witness = is_legal_pivot_method(best, n)
        assert ok, f"greedy lower bound illegal for n={n}: {witness}"
        lb_size = len(best)

        target = lb_size + 1
        status, ub_meta = cpsat_prove_upper_bound(
            n, target=target, time_budget_s=ub_budget_s,
            per_round_time_limit_s=per_round_time_limit_s, seed=seed,
        )

        entry = {
            "n": n,
            "lower_bound_found": lb_size,
            "lower_bound_meta": {"trials_run": lb_meta.get("trials_run"), "wall_time_s": lb_meta.get("wall_time_s")},
            "target_tested": target,
            "status": status,
            "ub_wall_time_s": ub_meta.get("wall_time_s"),
            "ub_rounds": ub_meta.get("rounds"),
            "ub_final_cuts": ub_meta.get("final_cuts"),
        }

        if status == "INFEASIBLE_PROVEN":
            entry["verdict"] = f"EXACT: C({n}) = {lb_size} (upper bound machine-proven via lazy CP-SAT, lower bound via greedy construction)"
        elif status == "FEASIBLE_FOUND":
            new_pts = ub_meta["points"]
            ok2, witness2 = is_legal_pivot_method(new_pts, n)
            assert ok2, f"cpsat feasible candidate illegal for n={n}: {witness2}"
            entry["verdict"] = f"greedy lower bound was NOT optimal -- cpsat found a legal size-{len(new_pts)} construction beating it"
            entry["improved_points"] = new_pts
        else:
            entry["verdict"] = "INCONCLUSIVE within budget"

        results[n] = entry
        print(f"n={n}: {entry['verdict']}  (t={time.time()-t0:.1f}s)")

    return results


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [8, 10, 12, 15, 20, 25, 30]
    lb_budget = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
    ub_budget = float(sys.argv[3]) if len(sys.argv) > 3 else 300.0
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1

    results = sweep(ns, lb_budget_s=lb_budget, ub_budget_s=ub_budget, seed=seed)
    os.makedirs("logs", exist_ok=True)
    out = "logs/cpsat_small_n_sweep.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"wrote {out}")
