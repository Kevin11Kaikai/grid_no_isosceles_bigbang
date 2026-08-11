"""Strategy A: Tabu search with informed removal, seeded from a legal baseline.

Fast variant: score a small random subset of removal candidates by actually
trial-removing each and counting how many sampled empty cells become legal,
then commit the best removal batch and greedily refill. Tabu blocks re-adding
recently removed points unless aspiration (new best) applies.
"""
from __future__ import annotations

import os
import random
import sys
import time
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.search.incremental_state import IncrementalIsoscelesFreeSet
from src.verification.oracle_verifier import is_legal_pivot_method

Point = Tuple[int, int]


def _ring(p: Point, n: int) -> int:
    return min(p[0], p[1], n - 1 - p[0], n - 1 - p[1])


def _trial_free_count(
    ifs: IncrementalIsoscelesFreeSet,
    remove_ps: List[Point],
    probe: List[Point],
) -> int:
    """Temporarily remove points; count how many probe cells become addable."""
    for p in remove_ps:
        ifs.remove_point(p)
    freed = sum(1 for q in probe if q not in ifs.points and ifs.can_add(q)[0])
    for p in remove_ps:
        ifs.add_point(p)  # restore (was legal before)
    return freed


def tabu_run(
    n: int,
    initial_points: List[Point],
    time_budget_s: float,
    seed: int = 0,
    tenure: Optional[int] = None,
    remove_batch: int = 3,
    removal_candidates: int = 12,
    probe_size: int = 250,
    refill_passes: int = 2,
    oracle_check_every: int = 100,
) -> Tuple[List[Point], dict]:
    rng = random.Random(seed)
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    if tenure is None:
        tenure = max(8, len(initial_points) // 15)

    ifs = IncrementalIsoscelesFreeSet(n)
    for p in initial_points:
        if not ifs.add_point(p):
            raise ValueError(f"initial_points illegal at {p}")
    ifs.cross_check_with_oracle()

    best_points: Set[Point] = set(ifs.points)
    best_size = len(best_points)
    tabu_until: Dict[Point, int] = {}
    iterations = 0
    improvements: List[dict] = []
    plateau = 0
    t0 = time.time()

    while time.time() - t0 < time_budget_s:
        iterations += 1
        current = list(ifs.points)
        empty = [p for p in all_pts if p not in ifs.points]
        probe = empty if len(empty) <= probe_size else rng.sample(empty, probe_size)

        # Sample removal candidates; prefer interior-ish points slightly (higher ring)
        # so we stress-test whether periphery-only packing is forced.
        cands = rng.sample(current, min(removal_candidates, len(current)))
        cands.sort(key=lambda p: (-_ring(p, n), rng.random()))

        best_score = -1
        best_remove: List[Point] = cands[:remove_batch]
        # Evaluate singletons / small batches greedily from ranked pool
        pool = cands[: max(remove_batch, removal_candidates // 2)]
        for i in range(0, len(pool), remove_batch):
            batch = pool[i : i + remove_batch]
            if len(batch) < remove_batch:
                batch = pool[:remove_batch]
            score = _trial_free_count(ifs, batch, probe)
            if score > best_score:
                best_score = score
                best_remove = batch

        for p in best_remove:
            ifs.remove_point(p)
            tabu_until[p] = iterations + tenure

        # Refill: boundary-first among non-tabu empties
        for _ in range(refill_passes):
            empties = [p for p in all_pts if p not in ifs.points]
            rng.shuffle(empties)
            empties.sort(key=lambda p: -_ring(p, n))
            for q in empties:
                until = tabu_until.get(q, -1)
                if until >= iterations and len(ifs.points) + 1 <= best_size:
                    continue  # tabu unless aspiration path
                ifs.add_point(q)

        if len(ifs.points) > best_size:
            best_size = len(ifs.points)
            best_points = set(ifs.points)
            improvements.append(
                {"iteration": iterations, "size": best_size, "t": time.time() - t0}
            )
            plateau = 0
        else:
            plateau += 1
            if len(ifs.points) < best_size and rng.random() < 0.85:
                ifs = IncrementalIsoscelesFreeSet(n)
                for p in best_points:
                    ifs.add_point(p)

        if iterations % oracle_check_every == 0:
            ifs.cross_check_with_oracle()

        if plateau > max(400, 8 * tenure) and time.time() - t0 > 0.5 * time_budget_s:
            break

    ok, witness = is_legal_pivot_method(list(best_points), n)
    if not ok:
        raise AssertionError(f"tabu best illegal: {witness}")

    meta = {
        "method": "tabu_informed_removal",
        "iterations": iterations,
        "wall_time_s": time.time() - t0,
        "improvements": improvements,
        "final_size": best_size,
        "initial_size": len(initial_points),
        "tenure": tenure,
        "seed": seed,
        "remove_batch": remove_batch,
        "best_score_last": best_score,
    }
    return sorted(best_points), meta


if __name__ == "__main__":
    import json
    from data.baselines.official_raw import SOL_64, SOL_100

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    init = list(SOL_64 if n == 64 else SOL_100)
    best, meta = tabu_run(n, init, budget, seed=seed, remove_batch=3)
    print(json.dumps(meta, indent=2))
    os.makedirs("logs", exist_ok=True)
    out = f"logs/tabu_n{n}_seed{seed}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "points": best}, f)
    print(f"wrote {out}")
