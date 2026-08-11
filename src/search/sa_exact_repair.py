"""Round 2, Strategy B: Simulated annealing over exact regional repairs.

Round 1's LNS+MILP route (`lns_exact_repair.py`) only ever accepts a
regional repair if it does not shrink the current legal set (size-monotonic,
with a small 30% chance of accepting an equal-size lateral move). That is a
strict hill-climb: once it reaches a local plateau where every single-region
repair is size-neutral or worse, it cannot escape without accepting a
temporary size decrease first. This module removes that restriction: regional
repairs that *shrink* the current set are accepted probabilistically under a
standard SA acceptance criterion, so the search can walk through worse
intermediate states to reach configurations a strict hill-climb cannot.

Move: same as Round 1 -- destroy a randomly chosen region (box / row-col band
/ boundary frame window) and re-solve it EXACTLY via 0-1 ILP
(`exact_repair_region`, imported unchanged from `lns_exact_repair.py` -- same
formulation, same correctness guarantees, not re-derived here).

Acceptance: let delta = len(new_set) - len(current). If delta >= 0, always
accept. If delta < 0, accept with probability exp(delta / T) (standard
Metropolis criterion; delta is negative here so this is in (0, 1)).
Temperature follows geometric cooling T <- T * alpha each iteration, with a
reheat back to T0 whenever the search has gone `reheat_after` iterations
without a new best (to avoid freezing at a bad plateau for the rest of the
budget).

CORRECTNESS DISCLOSURE (same pattern as lns_exact_repair.py, stated up front
this time rather than fixed after a Red Team finding): the slow oracle is
called on the initial state, on every NEW BEST, and on the final returned
state -- not on every accepted intermediate `current` (which would be too
slow at scale, since many thousands of iterations are expected). Only
oracle-verified states are ever recorded as `best` or returned.
"""
from __future__ import annotations

import math
import os
import random
import sys
import time
from typing import List, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.search.incremental_state import IncrementalIsoscelesFreeSet
from src.search.lns_exact_repair import exact_repair_region
from src.verification.oracle_verifier import is_legal_pivot_method

Point = Tuple[int, int]


def _random_region(n: int, rng: random.Random, size_cap: int) -> List[Point]:
    kind = rng.choices(["box", "row_col", "frame_window"], weights=(0.5, 0.3, 0.2), k=1)[0]
    if kind == "box":
        cx, cy = rng.randint(0, n - 1), rng.randint(0, n - 1)
        r = rng.randint(3, max(4, n // 6))
        region = [
            (x, y)
            for x in range(max(0, cx - r), min(n, cx + r + 1))
            for y in range(max(0, cy - r), min(n, cy + r + 1))
        ]
    elif kind == "row_col":
        if rng.random() < 0.5:
            row = rng.randint(0, n - 1)
            band = rng.randint(1, 3)
            region = [
                (x, y)
                for y in range(max(0, row - band), min(n, row + band + 1))
                for x in range(n)
            ]
        else:
            col = rng.randint(0, n - 1)
            band = rng.randint(1, 3)
            region = [
                (x, y)
                for x in range(max(0, col - band), min(n, col + band + 1))
                for y in range(n)
            ]
    else:
        depth = rng.randint(1, max(2, n // 8))
        side = rng.choice(["top", "bottom", "left", "right"])
        if side == "top":
            region = [(x, y) for x in range(n) for y in range(0, depth)]
        elif side == "bottom":
            region = [(x, y) for x in range(n) for y in range(n - depth, n)]
        elif side == "left":
            region = [(x, y) for x in range(0, depth) for y in range(n)]
        else:
            region = [(x, y) for x in range(n - depth, n) for y in range(n)]

    if len(region) > size_cap:
        region = rng.sample(region, size_cap)
    return region


def sa_exact_repair_run(
    n: int,
    initial_points: List[Point],
    time_budget_s: float,
    seed: int = 0,
    T0: float = 3.0,
    alpha: float = 0.9995,
    milp_time_limit_s: float = 3.0,
    region_size_cap: int = 300,
    reheat_after: int = 600,
    oracle_check_every: int = 200,
) -> Tuple[List[Point], dict]:
    rng = random.Random(seed)

    ifs = IncrementalIsoscelesFreeSet(n)
    for p in initial_points:
        if not ifs.add_point(p):
            raise ValueError(f"initial_points illegal at {p}")
    ifs.cross_check_with_oracle()

    current: Set[Point] = set(ifs.points)
    best: Set[Point] = set(current)
    best_size = len(best)
    T = T0
    t0 = time.time()
    iterations = 0
    improvements = []
    accepted_worse = 0
    since_best = 0
    milp_calls = 0

    while time.time() - t0 < time_budget_s:
        iterations += 1
        region_all = _random_region(n, rng, region_size_cap)
        removed_in_region = [p for p in region_all if p in current]
        fixed = current - set(removed_in_region)
        region_candidates = [p for p in region_all if p not in fixed]
        if not region_candidates:
            continue

        selected, _ = exact_repair_region(n, fixed, region_candidates, time_limit_s=milp_time_limit_s)
        milp_calls += 1
        new_set = fixed | set(selected)
        delta = len(new_set) - len(current)

        accept = False
        if delta >= 0:
            accept = True
        else:
            p_accept = math.exp(delta / max(T, 1e-9))
            if rng.random() < p_accept:
                accept = True
                accepted_worse += 1

        if accept:
            current = new_set

        if len(current) > best_size:
            ok, witness = is_legal_pivot_method(list(current), n)
            if not ok:
                raise AssertionError(f"SA+exact-repair produced illegal state! witness={witness}")
            best = set(current)
            best_size = len(best)
            improvements.append(
                {"iteration": iterations, "size": best_size, "t": time.time() - t0, "T": T}
            )
            since_best = 0
        else:
            since_best += 1

        T *= alpha
        if since_best >= reheat_after:
            T = T0
            since_best = 0
            # walk back toward best (not reset fully -- keep some exploration value)
            if rng.random() < 0.5:
                current = set(best)

        if iterations % oracle_check_every == 0:
            ok, witness = is_legal_pivot_method(list(current), n)
            if not ok:
                raise AssertionError(f"SA+exact-repair current state diverged from legality! witness={witness}")

    ok, witness = is_legal_pivot_method(list(best), n)
    if not ok:
        raise AssertionError(f"SA+exact-repair final best illegal: {witness}")

    meta = {
        "method": "sa_exact_repair",
        "iterations": iterations,
        "milp_calls": milp_calls,
        "wall_time_s": time.time() - t0,
        "improvements": improvements,
        "final_size": best_size,
        "initial_size": len(initial_points),
        "seed": seed,
        "T0": T0,
        "alpha": alpha,
        "accepted_worse_moves": accepted_worse,
    }
    return sorted(best), meta


if __name__ == "__main__":
    import json

    from data.baselines.official_raw import SOL_64, SOL_100

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    init = list(SOL_64 if n == 64 else SOL_100)
    best, meta = sa_exact_repair_run(n, init, budget, seed=seed)
    print(json.dumps(meta, indent=2))
    os.makedirs("logs", exist_ok=True)
    out = f"logs/sa_exact_n{n}_seed{seed}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "points": best}, f)
    print(f"wrote {out}")
