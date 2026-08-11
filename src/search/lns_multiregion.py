"""Round 2: multi-region exact repair -- closes a structural blind spot in Round 1.

Round 1's `lns_exact_repair.py` destroys and exactly repairs ONE disjoint
region per iteration. That proves (across 33766 trials) that no single
region, in isolation, has room for an improving move given the rest of the
set held fixed. It says NOTHING about improvements that require
*simultaneously* changing two or more disjoint regions in a coordinated way
(e.g. removing a point in region A specifically to free up two additional
legal points in far-away region B). This module closes that gap: it destroys
K >= 2 disjoint regions per iteration and repairs their UNION in a single
exact 0-1 ILP call, so the solver can trade off candidates across regions
jointly.

Reuses `exact_repair_region` from `lns_exact_repair.py` unchanged (same
formulation, same correctness guarantees) -- the only difference from Round 1
is what `fixed` / `region_candidates` are constructed from: here they come
from the union of K disjoint destroyed regions rather than one.

Tractability note: the constraint count in `exact_repair_region` grows
roughly with (fixed pivots + candidates) x (candidates in each pivot's
distance-groups), so combining regions is more expensive than a single region
of the same total size (more fixed-pivot cross terms). Region sizes and K are
kept modest and the per-call MILP time limit is raised accordingly; still
strictly exact (no relaxation), just possibly hitting the internal HiGHS time
limit before proving optimality on the largest combined regions -- in that
case `exact_repair_region`'s own returned solution is still a FEASIBLE (legal)
one (HiGHS returns the best incumbent found), just not certified globally
optimal for that sub-instance. The overall LNS accept/reject logic only ever
cares about the size of the resulting *legal* set, and every improving
candidate is oracle-re-verified before being recorded as best, so this
possible sub-optimality never risks correctness -- only search completeness.
"""
from __future__ import annotations

import os
import random
import sys
import time
from typing import List, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.search.lns_exact_repair import exact_repair_region
from src.search.sa_exact_repair import _random_region
from src.verification.oracle_verifier import is_legal_pivot_method

Point = Tuple[int, int]


def _disjoint_regions(n: int, rng: random.Random, k: int, size_cap_each: int) -> List[Point]:
    """Union of k regions, sampled independently; overlaps naturally merge (fine -- the
    union is what matters, not exact disjointness of the raw box coordinates)."""
    union: Set[Point] = set()
    for _ in range(k):
        union.update(_random_region(n, rng, size_cap_each))
    return list(union)


def lns_multiregion_run(
    n: int,
    initial_points: List[Point],
    time_budget_s: float,
    seed: int = 0,
    k_regions: int = 3,
    size_cap_each: int = 150,
    milp_time_limit_s: float = 8.0,
    oracle_check_every: int = 100,
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
    improvements: List[dict] = []
    milp_calls = 0
    total_combined_region_size = 0

    while time.time() - t0 < time_budget_s:
        iterations += 1
        region_all = _disjoint_regions(n, rng, k_regions, size_cap_each)
        total_combined_region_size += len(region_all)

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
            ok, witness = is_legal_pivot_method(list(current), n)
            if not ok:
                raise AssertionError(f"multi-region repair produced illegal state! witness={witness}")
            best = set(current)
            best_size = len(best)
            improvements.append(
                {
                    "iteration": iterations,
                    "size": best_size,
                    "t": time.time() - t0,
                    "combined_region_size": len(region_all),
                }
            )

        if iterations % oracle_check_every == 0:
            ok, witness = is_legal_pivot_method(list(current), n)
            if not ok:
                raise AssertionError(f"multi-region current state diverged from legality! witness={witness}")

    ok, witness = is_legal_pivot_method(list(best), n)
    if not ok:
        raise AssertionError(f"multi-region final best illegal: {witness}")

    meta = {
        "method": "lns_multiregion_exact_repair",
        "iterations": iterations,
        "milp_calls": milp_calls,
        "wall_time_s": time.time() - t0,
        "improvements": improvements,
        "final_size": best_size,
        "initial_size": len(initial_points),
        "seed": seed,
        "k_regions": k_regions,
        "size_cap_each": size_cap_each,
        "avg_combined_region_size": total_combined_region_size / max(iterations, 1),
    }
    return sorted(best), meta


if __name__ == "__main__":
    import json

    from data.baselines.official_raw import SOL_64, SOL_100

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    init = list(SOL_64 if n == 64 else SOL_100)
    best, meta = lns_multiregion_run(n, init, budget, seed=seed, k_regions=k)
    print(json.dumps(meta, indent=2))
    os.makedirs("logs", exist_ok=True)
    out = f"logs/multiregion_n{n}_seed{seed}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "points": best}, f)
    print(f"wrote {out}")
