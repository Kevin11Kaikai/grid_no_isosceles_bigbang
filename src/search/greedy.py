"""Route A: Greedy multistart construction."""
from __future__ import annotations

import os
import random
import sys
import time
from typing import List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.search.incremental_state import IncrementalIsoscelesFreeSet

Point = Tuple[int, int]


def greedy_once(n: int, seed: int, order: str = "random") -> Tuple[List[Point], int]:
    rng = random.Random(seed)
    all_pts = [(x, y) for x in range(n) for y in range(n)]

    if order == "random":
        rng.shuffle(all_pts)
    elif order == "boundary_first":
        cx = cy = (n - 1) / 2.0
        all_pts.sort(key=lambda p: -max(abs(p[0] - cx), abs(p[1] - cy)))
        # break exact ties randomly
        rng.shuffle(all_pts)
        cx = cy = (n - 1) / 2.0
        all_pts.sort(key=lambda p: -max(abs(p[0] - cx), abs(p[1] - cy)))
    elif order == "center_first":
        cx = cy = (n - 1) / 2.0
        all_pts.sort(key=lambda p: max(abs(p[0] - cx), abs(p[1] - cy)))
    else:
        raise ValueError(order)

    ifs = IncrementalIsoscelesFreeSet(n)
    for p in all_pts:
        ifs.add_point(p)
    return list(ifs.points), seed


def greedy_multistart(
    n: int, num_starts: int, time_budget_s: float, seed0: int = 0, orders=("random",)
) -> Tuple[List[Point], dict]:
    t0 = time.time()
    best: List[Point] = []
    best_meta = {}
    trial = 0
    while time.time() - t0 < time_budget_s and trial < num_starts:
        order = orders[trial % len(orders)]
        pts, seed = greedy_once(n, seed0 + trial, order=order)
        if len(pts) > len(best):
            best = pts
            best_meta = {"seed": seed, "order": order, "trial": trial}
        trial += 1
    best_meta["trials_run"] = trial
    best_meta["wall_time_s"] = time.time() - t0
    return best, best_meta
