#!/usr/bin/env python3
"""LH-3: Destroy half of S0 (far from +1 basin), rebuild with greedy+LNS-style refill.

Measures whether leaving S0 neighborhood can recover sizes near 164/165.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100, SOL_64  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402


def rebuild(n, sol, seed, keep_frac, seconds):
    rng = random.Random(seed)
    s0 = [tuple(p) for p in sol]
    keep_n = int(len(s0) * keep_frac)
    keep = set(rng.sample(s0, keep_n))
    st = IncrementalIsoscelesFreeSet(n)
    for p in keep:
        assert st.add_point(p)
    cells = [(x, y) for x in range(n) for y in range(n) if (x, y) not in keep]
    # boundary bias
    cells.sort(key=lambda p: (min(p[0], p[1], n - 1 - p[0], n - 1 - p[1]), rng.random()))
    for p in cells:
        ok, _ = st.can_add(p)
        if ok:
            st.add_point(p)
    best = sorted(st.points)
    best_size = len(best)
    t0 = time.time()
    iters = 0
    while time.time() - t0 < seconds:
        iters += 1
        if not st.points:
            break
        k = min(rng.choice([2, 4, 6, 10]), len(st.points))
        # prefer removing non-original-keep points sometimes
        pts = sorted(st.points)
        rem = rng.sample(pts, k)
        for p in rem:
            st.remove_point(p)
        order = cells[:]
        rng.shuffle(order)
        for p in order:
            ok, _ = st.can_add(p)
            if ok:
                st.add_point(p)
        if len(st.points) > best_size:
            best = sorted(st.points)
            best_size = len(best)
    ok_a, _ = is_legal_pivot_method(best, n)
    ok_b, _ = verify_independent(best, n)
    return {
        "n": n,
        "seed": seed,
        "keep_frac": keep_frac,
        "kept": keep_n,
        "size": best_size,
        "V": conflict_count(best, n),
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "hamming_remove_from_s0": len(set(s0) - set(best)),
        "hamming_add": len(set(best) - set(s0)),
        "iters": iters,
        "points_hash": sha256_of_points(best),
        "wall_s": time.time() - t0,
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    t0 = time.time()
    results = []
    for seed, frac in [(21, 0.5), (22, 0.5), (23, 0.25), (24, 0.75)]:
        row = rebuild(64, SOL_64, seed, frac, seconds=60.0)
        results.append(row)
        print(json.dumps(row), flush=True)
    for seed, frac in [(31, 0.5), (32, 0.5), (33, 0.25), (34, 0.75), (35, 0.5)]:
        row = rebuild(100, SOL_100, seed, frac, seconds=120.0)
        results.append(row)
        print(json.dumps(row), flush=True)
    out = {
        "schema": "lh3_half_baseline_rebuild_v1",
        "results": results,
        "best_n64": max(r["size"] for r in results if r["n"] == 64),
        "best_n100": max(r["size"] for r in results if r["n"] == 100),
        "wall_s": time.time() - t0,
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH3_from_scratch")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "half_baseline_rebuild.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"path": path, "best_n64": out["best_n64"], "best_n100": out["best_n100"], "wall_s": out["wall_s"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
