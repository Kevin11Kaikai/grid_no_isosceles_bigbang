#!/usr/bin/env python3
"""LH-3: Structured geometric constructions far from official S0.

Try modular / annular / triangular-lattice-like subsets; greedily repair to legality;
report best legal sizes. Not claimed optimal.
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

from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402


def legalize(n, candidates, seconds=30.0, seed=0):
    rng = random.Random(seed)
    order = list(candidates)
    rng.shuffle(order)
    st = IncrementalIsoscelesFreeSet(n)
    t0 = time.time()
    for p in order:
        ok, _ = st.can_add(p)
        if ok:
            st.add_point(p)
    best = sorted(st.points)
    while time.time() - t0 < seconds:
        if not st.points:
            break
        rem = rng.sample(sorted(st.points), k=min(rng.choice([1, 2, 3]), len(st.points)))
        for p in rem:
            st.remove_point(p)
        rng.shuffle(order)
        for p in order:
            ok, _ = st.can_add(p)
            if ok:
                st.add_point(p)
        if len(st.points) > len(best):
            best = sorted(st.points)
    ok_a, _ = is_legal_pivot_method(best, n)
    ok_b, _ = verify_independent(best, n)
    return {
        "size": len(best),
        "V": conflict_count(best, n),
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "hash": sha256_of_points(best),
        "points": [list(p) for p in best] if len(best) >= (165 if n == 100 else 113) and ok_a else None,
    }


def pattern_modular(n, a, b, c):
    return [(x, y) for x in range(n) for y in range(n) if (a * x + b * y) % c == 0]


def pattern_annulus(n, r0, r1):
    out = []
    for x in range(n):
        for y in range(n):
            # distance to nearest corner/center? use ring depth
            rd = min(x, y, n - 1 - x, n - 1 - y)
            if r0 <= rd <= r1:
                out.append((x, y))
    return out


def pattern_checker_thick(n, period, phase=0):
    return [
        (x, y)
        for x in range(n)
        for y in range(n)
        if ((x // period) + (y // period)) % 2 == phase
    ]


def pattern_diag_bands(n, width):
    return [(x, y) for x in range(n) for y in range(n) if (x + y) % (2 * width) < width]


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    t0 = time.time()
    results = []
    n = 100
    patterns = []
    for c in (3, 4, 5, 6, 7):
        for a, b in ((1, 0), (0, 1), (1, 1), (1, 2), (2, 1)):
            patterns.append((f"mod_{a}_{b}_{c}", pattern_modular(n, a, b, c)))
    for r0, r1 in ((0, 5), (0, 10), (5, 15), (10, 20), (15, 26), (20, 30)):
        patterns.append((f"annulus_{r0}_{r1}", pattern_annulus(n, r0, r1)))
    for period in (2, 3, 4, 5):
        for phase in (0, 1):
            patterns.append((f"check_{period}_{phase}", pattern_checker_thick(n, period, phase)))
    for width in (2, 3, 4, 5):
        patterns.append((f"diag_{width}", pattern_diag_bands(n, width)))

    for i, (name, cand) in enumerate(patterns):
        row = legalize(n, cand, seconds=20.0, seed=1000 + i)
        row["pattern"] = name
        row["n_candidates"] = len(cand)
        results.append(row)
        print(json.dumps({k: row[k] for k in row if k != "points"}), flush=True)

    best = max(results, key=lambda r: r["size"])
    out = {
        "schema": "lh3_pattern_constructions_v1",
        "n": n,
        "n_patterns": len(results),
        "best_size": best["size"],
        "best_pattern": best["pattern"],
        "results": results,
        "wall_s": time.time() - t0,
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH3_patterns")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "pattern_summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"path": path, "best_size": out["best_size"], "best_pattern": out["best_pattern"], "wall_s": out["wall_s"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
