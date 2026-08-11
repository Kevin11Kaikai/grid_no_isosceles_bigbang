"""Route D: Large Neighborhood Search seeded from a baseline construction.

Strategy: load a legal baseline (e.g. the official 112/164-point construction),
repeatedly (a) destroy a region (remove all points within a random box, or
remove a random subset of points), (b) greedily repair by re-scanning
candidate points in a randomized/boundary-biased order and re-adding whatever
is still legal, (c) keep the result if it grew the set size, else revert to
the best-so-far checkpoint. This is standard destroy-and-repair LNS; the
incremental state guarantees every accepted state is exactly legal (fail
closed -- there is no "soft" scoring of illegal states here).
"""
from __future__ import annotations

import os
import random
import sys
import time
from typing import List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.search.incremental_state import IncrementalIsoscelesFreeSet

Point = Tuple[int, int]


def _repair(ifs: IncrementalIsoscelesFreeSet, candidates: List[Point], rng: random.Random) -> None:
    order = list(candidates)
    rng.shuffle(order)
    for p in order:
        if p not in ifs.points:
            ifs.add_point(p)


def lns_run(
    n: int,
    initial_points: List[Point],
    time_budget_s: float,
    seed: int = 0,
    destroy_frac_range: Tuple[float, float] = (0.05, 0.25),
    region_destroy_prob: float = 0.5,
    oracle_check_every: int = 25,
) -> Tuple[List[Point], dict]:
    rng = random.Random(seed)
    all_pts = [(x, y) for x in range(n) for y in range(n)]

    ifs = IncrementalIsoscelesFreeSet(n)
    for p in initial_points:
        ok = ifs.add_point(p)
        if not ok:
            raise ValueError(f"initial_points not legal/consistent at point {p}")
    ifs.cross_check_with_oracle()

    best_points = set(ifs.points)
    best_size = len(best_points)
    iterations = 0
    improvements = []
    t0 = time.time()

    while time.time() - t0 < time_budget_s:
        iterations += 1
        current = list(ifs.points)
        if rng.random() < region_destroy_prob and current:
            # box destroy: pick a random center and radius, remove points inside
            cx, cy = rng.choice(current)
            radius = rng.randint(max(2, n // 12), max(3, n // 5))
            to_remove = [p for p in current if abs(p[0] - cx) <= radius and abs(p[1] - cy) <= radius]
        else:
            frac = rng.uniform(*destroy_frac_range)
            k = max(1, int(len(current) * frac))
            to_remove = rng.sample(current, min(k, len(current)))

        for p in to_remove:
            ifs.remove_point(p)

        _repair(ifs, all_pts, rng)

        if len(ifs.points) > best_size:
            best_size = len(ifs.points)
            best_points = set(ifs.points)
            improvements.append({"iteration": iterations, "size": best_size, "t": time.time() - t0})
        elif len(ifs.points) < best_size:
            # revert to best checkpoint to avoid random-walking away from the best region
            ifs = IncrementalIsoscelesFreeSet(n)
            for p in best_points:
                ifs.add_point(p)

        if iterations % oracle_check_every == 0:
            ifs.cross_check_with_oracle()

    ifs2 = IncrementalIsoscelesFreeSet(n)
    for p in best_points:
        ifs2.add_point(p)
    ifs2.cross_check_with_oracle()

    meta = {
        "iterations": iterations,
        "wall_time_s": time.time() - t0,
        "improvements": improvements,
        "final_size": best_size,
        "initial_size": len(initial_points),
        "seed": seed,
    }
    return list(best_points), meta
