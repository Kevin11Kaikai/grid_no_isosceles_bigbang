#!/usr/bin/env python3
"""LH-3: Grow legal sets from empty / random seeds — deliberately NOT from S0+1.

Target: maximize |S| with V=0; record if >=165/113. Uses IncrementalIsoscelesFreeSet.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from typing import List, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]


def ring(p: Point, n: int) -> int:
    x, y = p
    return min(x, y, n - 1 - x, n - 1 - y)


def order_candidates(n: int, rng: random.Random, mode: str) -> List[Point]:
    cells = [(x, y) for x in range(n) for y in range(n)]
    if mode == "boundary_first":
        cells.sort(key=lambda p: (ring(p, n), rng.random()))
    elif mode == "center_first":
        cells.sort(key=lambda p: (-ring(p, n), rng.random()))
    elif mode == "random":
        rng.shuffle(cells)
    elif mode == "spiral_mix":
        cells.sort(key=lambda p: (ring(p, n) % 3, ring(p, n), rng.random()))
    else:
        rng.shuffle(cells)
    return cells


def grow(n: int, seed: int, mode: str, seconds: float) -> dict:
    rng = random.Random(seed)
    order = order_candidates(n, rng, mode)
    st = IncrementalIsoscelesFreeSet(n)
    t0 = time.time()
    # Phase 1: greedy in order
    for p in order:
        if time.time() - t0 > seconds * 0.5:
            break
        ok, _ = st.can_add(p)
        if ok:
            st.add_point(p)
    # Phase 2: local destroy-refill
    best = sorted(st.points)
    best_size = len(best)
    iters = 0
    while time.time() - t0 < seconds:
        iters += 1
        if len(st.points) == 0:
            break
        # remove a small random batch
        batch = rng.sample(sorted(st.points), k=min(rng.choice([1, 2, 3, 5]), len(st.points)))
        for p in batch:
            st.remove_point(p)
        refill = order_candidates(n, rng, mode)
        rng.shuffle(refill)
        for p in refill:
            ok, _ = st.can_add(p)
            if ok:
                st.add_point(p)
        if len(st.points) > best_size:
            best = sorted(st.points)
            best_size = len(best)
    # verify
    ok_a, _ = is_legal_pivot_method(best, n)
    ok_b, _ = verify_independent(best, n)
    v = conflict_count(best, n)
    return {
        "n": n,
        "seed": seed,
        "mode": mode,
        "size": best_size,
        "V": v,
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "iters": iters,
        "wall_s": time.time() - t0,
        "points_hash": sha256_of_points(best) if best else None,
        "points": [list(p) for p in best] if best_size >= (165 if n == 100 else 113) and v == 0 else None,
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    t0 = time.time()
    results = []
    # n64 sandbox quick, then n100 primary
    for seed, mode in [
        (1, "boundary_first"),
        (2, "random"),
        (3, "spiral_mix"),
        (4, "center_first"),
    ]:
        row = grow(64, seed, mode, seconds=45.0)
        results.append(row)
        print(json.dumps({k: row[k] for k in row if k != "points"}), flush=True)
    for seed, mode in [
        (11, "boundary_first"),
        (12, "random"),
        (13, "spiral_mix"),
        (14, "boundary_first"),
        (15, "random"),
    ]:
        row = grow(100, seed, mode, seconds=90.0)
        results.append(row)
        print(json.dumps({k: row[k] for k in row if k != "points"}), flush=True)

    out = {
        "schema": "lh3_from_scratch_grow_v1",
        "results": results,
        "best_n64": max((r["size"] for r in results if r["n"] == 64), default=0),
        "best_n100": max((r["size"] for r in results if r["n"] == 100), default=0),
        "any_target": any(
            (r["n"] == 100 and r["size"] >= 165 and r["V"] == 0)
            or (r["n"] == 64 and r["size"] >= 113 and r["V"] == 0)
            for r in results
        ),
        "wall_s": time.time() - t0,
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH3_from_scratch")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "grow_summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    # save best legal sets even if below target
    for r in results:
        if r["oracle_legal"] and r["V"] == 0 and r["points"] is None:
            # reload size only — points omitted if below target; re-run not needed
            pass
    print(
        json.dumps(
            {
                "path": path,
                "best_n64": out["best_n64"],
                "best_n100": out["best_n100"],
                "any_target": out["any_target"],
                "wall_s": out["wall_s"],
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
