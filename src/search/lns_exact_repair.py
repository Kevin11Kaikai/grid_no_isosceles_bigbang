"""Route D (Strategy C from Proposer round 1): LNS with EXACT MILP repair.

Unlike src/search/lns.py (greedy single-pass repair), this destroys a small
region of a legal baseline and repairs it by solving, EXACTLY, the maximum
subset of currently-empty region cells that can be added back without
creating any isosceles triple -- either among themselves or with the fixed
(untouched) rest of the set. This is a genuine 0-1 ILP solved with
scipy.optimize.milp (HiGHS), not a heuristic.

Formulation for a destroy region with fixed set F (legal, untouched) and
candidate set C (currently-empty grid cells inside the region, i.e. every
non-F point of the region -- NOT the whole grid, to keep the ILP small):

  Step 1 (prefilter): drop every candidate p in C that individually conflicts
  with F alone (checked via the same incremental legality primitive used
  elsewhere in the project) -- such p can never be selected regardless of
  other candidates, so it is removed from the ILP outright.

  Step 2 (constraints), for the remaining candidates C':
    - For every FIXED pivot f in F: group the other points of F' union C'
      by squared distance to f. Since F is legal on its own, at most one
      member of any such group can already be fixed. If exactly one fixed
      member occupies a group, every candidate in that group is forced to 0
      (selecting it would complete a fixed-pivot isosceles triple). If zero
      fixed members occupy the group, add sum(x_a for a in group) <= 1.
    - For every CANDIDATE pivot p in C': after the Step-1 prefilter, no two
      fixed points are equidistant from p (guaranteed by the filter). For
      every OTHER pair of points {a, b} (drawn from F union C', excluding p)
      equidistant from p, add x_p + x_a + x_b <= 2 (using the constant 1 for
      any fixed member of the pair). This forbids p, a, b all being selected
      simultaneously with p as apex.

  Objective: maximize sum(x_p for p in C').

This is solved once per destroyed region (no lazy-constraint iteration is
needed -- the enumeration above is already exhaustive over the candidate
universe, not sampled).

CORRECTNESS DISCLOSURE (Red Team round 1, Finding #1, LOW severity, fixed here):
an earlier version of this docstring claimed every accepted intermediate
`current` state is re-verified against the slow oracle. That was inaccurate:
`lns_exact_run` only calls the slow oracle (a) once on the initial seed and
(b) whenever a NEW BEST is recorded -- not on every accepted `current`
reassignment in between. The function's actual *return value* (`best`) is
always oracle-verified before being reported, so this gap never affects the
final output of a call to `lns_exact_run`; it only means the many
intermediate, non-improving `current` states visited mid-search are not
individually oracle-cross-checked (they do pass through
`exact_repair_region`'s own fixed-set self-consistency assertion, which is a
narrower check than the full oracle). Any caller that wants intermediate
states to be individually oracle-verified (not just the final returned best)
must add that check itself.
"""
from __future__ import annotations

import os
import random
import sys
import time
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
from scipy.optimize import LinearConstraint, Bounds, milp
from scipy.sparse import lil_matrix

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.search.incremental_state import IncrementalIsoscelesFreeSet
from src.verification.oracle_verifier import is_legal_pivot_method

Point = Tuple[int, int]


def _sq_dist(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def exact_repair_region(
    n: int,
    fixed_points: Set[Point],
    region_candidates: List[Point],
    time_limit_s: float = 5.0,
) -> Tuple[List[Point], dict]:
    """Returns (selected_candidates, meta). fixed_points is untouched/returned separately."""
    meta = {"region_size": len(region_candidates)}

    # Step 1: prefilter candidates that individually conflict with F.
    probe = IncrementalIsoscelesFreeSet(n)
    for p in fixed_points:
        probe._add_unchecked(p)
    survivors = []
    for p in region_candidates:
        ok, _ = probe.can_add(p)
        if ok:
            survivors.append(p)
    meta["after_prefilter"] = len(survivors)

    if not survivors:
        return [], meta

    idx = {p: i for i, p in enumerate(survivors)}
    m = len(survivors)
    universe_fixed = list(fixed_points)

    constraints_rows = []  # list of (coeffs dict {var_idx: coeff}, upper_bound)

    # --- fixed-pivot constraints ---
    for f in universe_fixed:
        groups: Dict[int, List[Point]] = {}
        for q in universe_fixed:
            if q == f:
                continue
            groups.setdefault(_sq_dist(f, q), []).append(q)
        for p in survivors:
            groups.setdefault(_sq_dist(f, p), []).append(p)

        for d2, members in groups.items():
            fixed_members = [q for q in members if q in fixed_points]
            cand_members = [q for q in members if q not in fixed_points]
            if len(fixed_members) >= 2:
                raise AssertionError(
                    f"F is not legal on its own: pivot {f} has 2+ fixed points "
                    f"at squared distance {d2}: {fixed_members}"
                )
            if len(fixed_members) == 1:
                for c in cand_members:
                    constraints_rows.append(({idx[c]: 1.0}, 0.0))  # force x_c = 0 (via <=0)
            else:
                if len(cand_members) >= 2:
                    coeffs = {idx[c]: 1.0 for c in cand_members}
                    constraints_rows.append((coeffs, 1.0))

    # --- candidate-pivot constraints ---
    for p in survivors:
        others = [q for q in universe_fixed if q != p] + [q for q in survivors if q != p]
        groups: Dict[int, List[Point]] = {}
        for q in others:
            groups.setdefault(_sq_dist(p, q), []).append(q)
        for d2, members in groups.items():
            if len(members) < 2:
                continue
            fixed_in_group = [q for q in members if q in fixed_points]
            cand_in_group = [q for q in members if q not in fixed_points]
            # every pair {a,b} within `members` triggers x_p + x_a + x_b <= 2
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    a, b = members[i], members[j]
                    coeffs = {idx[p]: 1.0}
                    rhs = 2.0
                    for pt in (a, b):
                        if pt in fixed_points:
                            rhs -= 1.0
                        else:
                            coeffs[idx[pt]] = coeffs.get(idx[pt], 0.0) + 1.0
                    constraints_rows.append((coeffs, rhs))

    meta["num_constraints"] = len(constraints_rows)

    if not constraints_rows:
        # no constraints at all -- everything survives independently
        return survivors, meta

    A = lil_matrix((len(constraints_rows), m))
    ub = np.zeros(len(constraints_rows))
    for r, (coeffs, rhs) in enumerate(constraints_rows):
        for var_idx, coeff in coeffs.items():
            A[r, var_idx] = coeff
        ub[r] = rhs
    A = A.tocsr()

    constraint = LinearConstraint(A, -np.inf, ub)
    bounds = Bounds(0, 1)
    integrality = np.ones(m)
    c = -np.ones(m)  # maximize sum(x) == minimize -sum(x)

    res = milp(
        c=c,
        constraints=[constraint],
        integrality=integrality,
        bounds=bounds,
        options={"time_limit": time_limit_s},
    )
    meta["milp_status"] = res.status
    meta["milp_message"] = res.message

    if res.x is None:
        return [], meta

    selected = [survivors[i] for i in range(m) if res.x[i] > 0.5]
    meta["selected_count"] = len(selected)
    return selected, meta


def lns_exact_run(
    n: int,
    initial_points: List[Point],
    time_budget_s: float,
    seed: int = 0,
    region_kind_weights: Tuple[float, float, float] = (0.5, 0.3, 0.2),
    milp_time_limit_s: float = 4.0,
) -> Tuple[List[Point], dict]:
    rng = random.Random(seed)
    current: Set[Point] = set(initial_points)

    ok, witness = is_legal_pivot_method(list(current), n)
    if not ok:
        raise ValueError(f"initial_points not legal: {witness}")

    best = set(current)
    best_size = len(best)
    t0 = time.time()
    iterations = 0
    improvements = []
    milp_calls = 0

    while time.time() - t0 < time_budget_s:
        iterations += 1
        kind = rng.choices(["box", "row_col", "frame_window"], weights=region_kind_weights, k=1)[0]

        if kind == "box":
            cx, cy = rng.randint(0, n - 1), rng.randint(0, n - 1)
            r = rng.randint(3, max(4, n // 6))
            region_all = [
                (x, y)
                for x in range(max(0, cx - r), min(n, cx + r + 1))
                for y in range(max(0, cy - r), min(n, cy + r + 1))
            ]
        elif kind == "row_col":
            if rng.random() < 0.5:
                row = rng.randint(0, n - 1)
                band = rng.randint(1, 3)
                region_all = [
                    (x, y)
                    for y in range(max(0, row - band), min(n, row + band + 1))
                    for x in range(n)
                ]
            else:
                col = rng.randint(0, n - 1)
                band = rng.randint(1, 3)
                region_all = [
                    (x, y)
                    for x in range(max(0, col - band), min(n, col + band + 1))
                    for y in range(n)
                ]
        else:  # frame_window: a band near the boundary (where density is highest empirically)
            depth = rng.randint(1, max(2, n // 8))
            side = rng.choice(["top", "bottom", "left", "right"])
            if side == "top":
                region_all = [(x, y) for x in range(n) for y in range(0, depth)]
            elif side == "bottom":
                region_all = [(x, y) for x in range(n) for y in range(n - depth, n)]
            elif side == "left":
                region_all = [(x, y) for x in range(0, depth) for y in range(n)]
            else:
                region_all = [(x, y) for x in range(n - depth, n) for y in range(n)]

        # cap region size for ILP tractability
        if len(region_all) > 400:
            region_all = rng.sample(region_all, 400)

        removed_in_region = [p for p in region_all if p in current]
        fixed = current - set(removed_in_region)
        region_candidates = [p for p in region_all if p not in fixed]

        if not region_candidates:
            continue

        selected, repair_meta = exact_repair_region(
            n, fixed, region_candidates, time_limit_s=milp_time_limit_s
        )
        milp_calls += 1

        new_set = fixed | set(selected)
        if len(new_set) > len(current) or (len(new_set) >= len(current) and rng.random() < 0.3):
            current = new_set

        if len(current) > best_size:
            # verify with oracle before accepting as new best
            ok, witness = is_legal_pivot_method(list(current), n)
            if not ok:
                raise AssertionError(f"LNS+MILP produced illegal state! witness={witness}")
            best = set(current)
            best_size = len(best)
            improvements.append(
                {"iteration": iterations, "size": best_size, "t": time.time() - t0, "region_kind": kind}
            )

    meta = {
        "iterations": iterations,
        "milp_calls": milp_calls,
        "wall_time_s": time.time() - t0,
        "improvements": improvements,
        "final_size": best_size,
        "initial_size": len(initial_points),
        "seed": seed,
    }
    return list(best), meta
