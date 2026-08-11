"""Round 2, Strategy: hypergraph/constraint search with lazy cut generation.

Unlike every other search route in this project (which locally modifies a
region of an existing legal set), this treats the WHOLE grid as one 0-1
program: one boolean variable per grid point, and searches for a
maximum-size (or >=target-size) selection with no isosceles triple. The full
constraint set (one forbidden-triple constraint per (apex, equidistant-pair)
combination) is far too large to build upfront for n=64/100 (potentially
O(n^4) groups), so constraints are added LAZILY: solve the relaxed model
(only previously-added cuts), inspect the returned selection for violated
triples, add cuts for every violation found, and re-solve. Requires OR-Tools
CP-SAT, installed only in the project-local venv at `.venv_solver/` (NOT the
global interpreter -- see RESEARCH_LOG.md for why). Run this file with
`.venv_solver/Scripts/python.exe -m src.search.cpsat_lazy ...`, not the
system `python`.

Two modes, both mathematically meaningful because REMOVING constraints can
only ENLARGE the feasible region (monotonicity of relaxation):

  MODE "maximize": objective = maximize sum(x). Each round takes the
  incumbent (even if CP-SAT hits its per-round time limit before proving
  optimality -- the incumbent is still a valid candidate solution to check),
  scans it for violated triples, adds cuts, and re-solves warm-started from
  scratch (CP-SAT does not support persistent incremental warm-start across
  separate Solve() calls in the stable Python API used here, so each round
  rebuilds the model with the accumulated cut set -- this is the standard
  lazy-constraint pattern and is still exact, just not incremental at the
  solver-internals level). Stops when a round produces a selection with ZERO
  violations (a genuine, fully verified candidate) or the time budget is
  exhausted. Only a zero-violation selection is ever reported as a result;
  anything else is reported purely as search progress, never as a candidate.

  MODE "prove_upper_bound": adds a single hard constraint sum(x) >= target
  and asks only for FEASIBILITY (no objective). If CP-SAT proves INFEASIBLE
  under the current (partial!) cut set, that is already a mathematically
  valid certificate that the TRUE fully-constrained problem is infeasible
  too, because the true feasible region is a SUBSET of the lazily-relaxed
  one (fewer constraints can only permit more solutions, never fewer) --
  i.e. an infeasibility proof under a subset of constraints is a fortiori an
  infeasibility proof under the full constraint set. This is the only route
  in this whole project capable of producing a genuine machine-checked UPPER
  bound (as opposed to a lower-bound construction), so if it terminates with
  INFEASIBLE at target = (known best size + 1), that would upgrade a
  reproduced lower bound to a certified EXACT optimum for that n. This is
  expected to be tractable only for small n (used here first as a
  calibration/sanity exercise on small grids, then attempted, time
  permitting, on n=64).

All final candidate point sets returned by this module are re-verified with
the project's own pure-Python oracle (`src.verification.oracle_verifier`,
imported from the venv's sys.path -- no ortools dependency there) before
being written anywhere, exactly like every other search route.
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.verification.oracle_verifier import is_legal_pivot_method

from ortools.sat.python import cp_model  # noqa: E402  (after sys.path setup)

Point = Tuple[int, int]


def _sq_dist(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def _find_violations_and_cuts(
    points: List[Point], idx: Dict[Point, int]
) -> List[Tuple[int, int, int]]:
    """Returns list of (p_idx, a_idx, b_idx) cuts for every violated (apex, pair)
    found in `points` (a selection currently containing an isosceles triple)."""
    cuts = []
    pts_set = set(points)
    for p in points:
        groups: Dict[int, List[Point]] = {}
        for q in points:
            if q == p:
                continue
            groups.setdefault(_sq_dist(p, q), []).append(q)
        for d2, members in groups.items():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    a, b = members[i], members[j]
                    cuts.append((idx[p], idx[a], idx[b]))
    return cuts


def seed_cuts_from_points(
    n: int, seed_points: List[Point], idx: Dict[Point, int], max_cuts: int = 2_000_000
) -> Set[Tuple[int, int, int]]:
    """Round 2 (per Proposer proposal_round2.md Section 2.4-2): derive a large,
    GLOBAL, exact cut set directly from a known-legal point set's own pivot
    structure, before any lazy iteration begins -- avoids the inefficiency of
    starting the lazy loop from zero cuts (observed in the first Round 2 n=100
    run: round 1 alone, with zero seeded cuts, took nearly the entire budget
    because the unconstrained relaxation trivially selects every grid cell,
    producing an enormous violation set to extract and cut on all at once).

    For every point q in `seed_points` (treated purely as a geometric APEX
    location, not as a variable fixed to 1 -- these cuts are universally valid
    regardless of whether q ends up selected, since `x_q + x_a + x_b <= 2` is
    trivially satisfied whenever x_q = 0), group every OTHER grid cell by
    squared distance to q; every group of size >= 2 yields one valid cut per
    pair. This is the same per-apex constraint derivation already used in
    `lns_exact_repair.exact_repair_region` and validated there (main agent's
    own 3 synthetic tests + Red Team's 3 more, all matching brute force) --
    reused conceptually, not re-derived from scratch, exactly as the proposal
    recommended.
    """
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    cuts: Set[Tuple[int, int, int]] = set()
    for q in seed_points:
        groups: Dict[int, List[Point]] = {}
        for r in all_pts:
            if r == q:
                continue
            groups.setdefault(_sq_dist(q, r), []).append(r)
        for d2, members in groups.items():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    a, b = members[i], members[j]
                    cuts.add((idx[q], idx[a], idx[b]))
                    if len(cuts) >= max_cuts:
                        return cuts
    return cuts


def cpsat_lazy_maximize(
    n: int,
    time_budget_s: float,
    per_round_time_limit_s: float = 20.0,
    seed: int = 0,
    warm_start_points: Optional[List[Point]] = None,
    max_cuts_per_round: int = 200000,
    seed_cuts_from_warm_start: bool = True,
) -> Tuple[List[Point], dict]:
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    idx = {p: i for i, p in enumerate(all_pts)}
    m = len(all_pts)

    cuts: Set[Tuple[int, int, int]] = set()
    t0 = time.time()
    rounds = 0
    best_legal: List[Point] = list(warm_start_points) if warm_start_points else []
    best_legal_size = len(best_legal)
    round_log = []
    seed_cuts_count = 0

    if warm_start_points:
        ok, witness = is_legal_pivot_method(warm_start_points, n)
        if not ok:
            raise ValueError(f"warm_start_points illegal: {witness}")
        if seed_cuts_from_warm_start:
            cuts = seed_cuts_from_points(n, warm_start_points, idx)
            seed_cuts_count = len(cuts)

    while time.time() - t0 < time_budget_s:
        rounds += 1
        model = cp_model.CpModel()
        x = [model.NewBoolVar(f"x{i}") for i in range(m)]
        for (pi, ai, bi) in cuts:
            model.Add(x[pi] + x[ai] + x[bi] <= 2)
        model.Maximize(sum(x))

        if warm_start_points and rounds == 1:
            hint_idx = [idx[p] for p in warm_start_points]
            try:
                model.add_hint([x[i] for i in hint_idx], [1] * len(hint_idx))
            except Exception:
                # solver hint is a pure performance nicety, never required for
                # correctness -- if the installed ortools version's hint API
                # is incompatible, just skip the hint rather than fail the run.
                pass

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = min(
            per_round_time_limit_s, max(0.5, time_budget_s - (time.time() - t0))
        )
        solver.parameters.random_seed = seed + rounds
        solver.parameters.num_search_workers = 8
        status = solver.Solve(model)

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            round_log.append({"round": rounds, "status": solver.StatusName(status), "t": time.time() - t0})
            break

        selected = [all_pts[i] for i in range(m) if solver.Value(x[i]) == 1]
        new_cuts = _find_violations_and_cuts(selected, idx)

        round_info = {
            "round": rounds,
            "status": solver.StatusName(status),
            "selected_size": len(selected),
            "violations_found": len(new_cuts),
            "total_cuts": len(cuts),
            "t": time.time() - t0,
        }
        round_log.append(round_info)

        if not new_cuts:
            # zero violations -> genuinely legal selection
            ok, witness = is_legal_pivot_method(selected, n)
            if not ok:
                raise AssertionError(
                    f"cpsat_lazy_maximize: zero cuts found but oracle disagrees! witness={witness}"
                )
            if len(selected) > best_legal_size:
                best_legal = selected
                best_legal_size = len(selected)
            break  # converged to a fully legal max-under-current-cuts solution

        for c in list(new_cuts)[:max_cuts_per_round]:
            cuts.add(c)

    meta = {
        "method": "cpsat_lazy_maximize",
        "n": n,
        "rounds": rounds,
        "wall_time_s": time.time() - t0,
        "final_cuts": len(cuts),
        "seed_cuts_count": seed_cuts_count,
        "best_legal_size": best_legal_size,
        "round_log": round_log,
        "seed": seed,
    }
    return best_legal, meta


def cpsat_prove_upper_bound(
    n: int,
    target: int,
    time_budget_s: float,
    per_round_time_limit_s: float = 30.0,
    seed: int = 0,
) -> Tuple[str, dict]:
    """Returns (status, meta). status in:
    'INFEASIBLE_PROVEN' (target unreachable -- valid upper bound C(n) < target),
    'FEASIBLE_FOUND' (found a genuinely legal selection of size >= target -- a
      new candidate, upgrade path to certification),
    'INCONCLUSIVE' (time budget exhausted without resolving either way).
    """
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    idx = {p: i for i, p in enumerate(all_pts)}
    m = len(all_pts)

    cuts: Set[Tuple[int, int, int]] = set()
    t0 = time.time()
    rounds = 0
    round_log = []

    while time.time() - t0 < time_budget_s:
        rounds += 1
        model = cp_model.CpModel()
        x = [model.NewBoolVar(f"x{i}") for i in range(m)]
        for (pi, ai, bi) in cuts:
            model.Add(x[pi] + x[ai] + x[bi] <= 2)
        model.Add(sum(x) >= target)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = min(
            per_round_time_limit_s, max(0.5, time_budget_s - (time.time() - t0))
        )
        solver.parameters.random_seed = seed + rounds
        solver.parameters.num_search_workers = 8
        status = solver.Solve(model)

        if status == cp_model.INFEASIBLE:
            round_log.append({"round": rounds, "status": "INFEASIBLE", "t": time.time() - t0})
            return "INFEASIBLE_PROVEN", {
                "method": "cpsat_prove_upper_bound",
                "n": n,
                "target": target,
                "rounds": rounds,
                "wall_time_s": time.time() - t0,
                "final_cuts": len(cuts),
                "round_log": round_log,
            }

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            round_log.append({"round": rounds, "status": solver.StatusName(status), "t": time.time() - t0})
            return "INCONCLUSIVE", {
                "method": "cpsat_prove_upper_bound",
                "n": n,
                "target": target,
                "rounds": rounds,
                "wall_time_s": time.time() - t0,
                "final_cuts": len(cuts),
                "round_log": round_log,
            }

        selected = [all_pts[i] for i in range(m) if solver.Value(x[i]) == 1]
        new_cuts = _find_violations_and_cuts(selected, idx)
        round_log.append(
            {
                "round": rounds,
                "status": solver.StatusName(status),
                "selected_size": len(selected),
                "violations_found": len(new_cuts),
                "total_cuts": len(cuts),
                "t": time.time() - t0,
            }
        )

        if not new_cuts:
            ok, witness = is_legal_pivot_method(selected, n)
            if not ok:
                raise AssertionError(
                    f"cpsat_prove_upper_bound: zero cuts found but oracle disagrees! witness={witness}"
                )
            return "FEASIBLE_FOUND", {
                "method": "cpsat_prove_upper_bound",
                "n": n,
                "target": target,
                "rounds": rounds,
                "wall_time_s": time.time() - t0,
                "final_cuts": len(cuts),
                "round_log": round_log,
                "points": selected,
            }

        for c in new_cuts:
            cuts.add(c)

    return "INCONCLUSIVE", {
        "method": "cpsat_prove_upper_bound",
        "n": n,
        "target": target,
        "rounds": rounds,
        "wall_time_s": time.time() - t0,
        "final_cuts": len(cuts),
        "round_log": round_log,
    }


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "maximize"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    budget = float(sys.argv[3]) if len(sys.argv) > 3 else 60.0
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1

    os.makedirs("logs", exist_ok=True)

    if mode == "maximize":
        warm = None
        if len(sys.argv) > 5 and sys.argv[5] == "warm":
            from data.baselines.official_raw import SOL_64, SOL_100
            warm = list(SOL_64 if n == 64 else SOL_100) if n in (64, 100) else None
        best, meta = cpsat_lazy_maximize(n, budget, seed=seed, warm_start_points=warm)
        print(json.dumps(meta, indent=2)[:4000])
        out = f"logs/cpsat_maximize_n{n}_seed{seed}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"meta": meta, "points": best}, f)
        print(f"wrote {out}")
    else:
        target = int(sys.argv[5]) if len(sys.argv) > 5 else n
        status, meta = cpsat_prove_upper_bound(n, target, budget, seed=seed)
        print(status)
        print(json.dumps(meta, indent=2)[:4000])
        out = f"logs/cpsat_upperbound_n{n}_target{target}_seed{seed}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"status": status, "meta": meta}, f)
        print(f"wrote {out}")
