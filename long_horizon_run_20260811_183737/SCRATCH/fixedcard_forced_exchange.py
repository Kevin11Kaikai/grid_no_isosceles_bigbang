#!/usr/bin/env python3
"""LH-3: Fixed |S|=165 with hard constraint |S0\\S| >= r_min (default 2).

Prevents Wave2-C / eject basin of baseline+1 (V=3) elites. Minimize V under exchange.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from collections import defaultdict
from typing import List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402

Point = Tuple[int, int]
N = 100
TARGET = 165


def sq(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def init_exchange(s0: List[Point], rng: random.Random, r_min: int = 2) -> List[Point]:
    """Remove r_min baseline points, add r_min+1 empties (possibly illegal)."""
    rem = set(rng.sample(s0, r_min))
    core = [p for p in s0 if p not in rem]
    empty = [(x, y) for x in range(N) for y in range(N) if (x, y) not in set(s0)]
    rng.shuffle(empty)
    # Prefer legal adds when possible
    st = IncrementalIsoscelesFreeSet(N)
    for p in core:
        assert st.add_point(p)
    added = []
    for p in empty:
        if len(added) >= r_min + 1:
            break
        ok, _ = st.can_add(p)
        if ok:
            st.add_point(p)
            added.append(p)
    for p in empty:
        if len(added) >= r_min + 1:
            break
        if p not in set(added):
            added.append(p)
    pts = core + added
    assert len(pts) == TARGET
    assert len(set(s0) - set(pts)) >= r_min
    return pts


def run_seed(seed: int, seconds: float = 120.0, r_min: int = 2) -> dict:
    rng = random.Random(seed)
    s0 = [tuple(p) for p in SOL_100]
    s0_set = set(s0)
    pts = init_exchange(s0, rng, r_min=r_min)
    best_v = conflict_count(pts, N)
    best_pts = list(pts)
    t0 = time.time()
    iters = 0
    while time.time() - t0 < seconds:
        iters += 1
        # 2-for-2 or 3-for-3 swap preserving |S0\\S| >= r_min
        k = rng.choice([1, 2, 3])
        # remove k from current, add k from outside
        rem_cand = list(pts)
        rng.shuffle(rem_cand)
        remove = rem_cand[:k]
        core = [p for p in pts if p not in set(remove)]
        # ensure after refill we still have enough removed from s0
        occ = set(core)
        pool = [(x, y) for x in range(N) for y in range(N) if (x, y) not in occ]
        rng.shuffle(pool)
        st = IncrementalIsoscelesFreeSet(N)
        legal_core = True
        for p in core:
            if not st.add_point(p):
                legal_core = False
                break
        added = []
        if legal_core:
            for p in pool:
                if len(added) >= k:
                    break
                ok, _ = st.can_add(p)
                if ok:
                    st.add_point(p)
                    added.append(p)
        for p in pool:
            if len(added) >= k:
                break
            if p not in set(added) and p not in occ:
                added.append(p)
        new_pts = core + added
        if len(new_pts) != TARGET:
            continue
        if len(s0_set - set(new_pts)) < r_min:
            continue
        v = conflict_count(new_pts, N)
        if v <= best_v:
            pts = new_pts
            if v < best_v:
                best_v = v
                best_pts = list(new_pts)
                if best_v == 0:
                    break
        elif rng.random() < 0.03:
            pts = new_pts
    return {
        "seed": seed,
        "r_min": r_min,
        "best_V": best_v,
        "iters": iters,
        "final_remove_from_s0": len(s0_set - set(best_pts)),
        "final_add": len(set(best_pts) - s0_set),
        "status": "V0_LEGAL" if best_v == 0 else "BEST_V",
        "wall_s": time.time() - t0,
        "points": [list(p) for p in best_pts] if best_v == 0 else None,
    }


def main():
    t0 = time.time()
    results = []
    for seed in (401, 402, 403, 404):
        results.append(run_seed(seed, seconds=100.0, r_min=2))
        print(json.dumps({k: results[-1][k] for k in results[-1] if k != "points"}), flush=True)
    out = {
        "schema": "lh3_fixedcard_forced_exchange_v1",
        "results": results,
        "best_V": min(r["best_V"] for r in results),
        "any_v0": any(r["status"] == "V0_LEGAL" for r in results),
        "wall_s": time.time() - t0,
        "note": "Prevents baseline+1 V=3 basin documented in LH2_elite_distance.",
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH3_forced_exchange")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "forced_exchange_n100.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"path": path, "best_V": out["best_V"], "any_v0": out["any_v0"], "wall_s": out["wall_s"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
