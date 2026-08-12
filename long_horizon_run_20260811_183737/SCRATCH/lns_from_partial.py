#!/usr/bin/env python3
"""LH-3: Exact-MILP LNS starting from half-rebuild legal sets (not official S0)."""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.search.lns_exact_repair import lns_exact_run  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
import random


def build_partial(seed: int = 32, keep_frac: float = 0.5) -> list:
    rng = random.Random(seed)
    s0 = [tuple(p) for p in SOL_100]
    keep = set(rng.sample(s0, int(len(s0) * keep_frac)))
    st = IncrementalIsoscelesFreeSet(100)
    for p in keep:
        st.add_point(p)
    cells = [(x, y) for x in range(100) for y in range(100) if (x, y) not in keep]
    cells.sort(key=lambda p: (min(p[0], p[1], 99 - p[0], 99 - p[1]), rng.random()))
    for p in cells:
        ok, _ = st.can_add(p)
        if ok:
            st.add_point(p)
    return sorted(st.points)


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    t0 = time.time()
    start = build_partial(32, 0.5)
    print(json.dumps({"start_size": len(start), "start_hash": sha256_of_points(start)}), flush=True)
    # lns_exact_run signature
    best, meta = lns_exact_run(
        n=100,
        initial_points=start,
        time_budget_s=300.0,
        seed=77,
    )
    pts = [tuple(p) for p in best] if best else []
    ok_a, _ = is_legal_pivot_method(pts, 100) if pts else (False, None)
    ok_b, _ = verify_independent(pts, 100) if pts else (False, None)
    out = {
        "start_size": len(start),
        "start_hash": sha256_of_points(start),
        "final_size": len(pts),
        "final_hash": sha256_of_points(pts) if pts else None,
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "meta": {
            k: meta.get(k)
            for k in (
                "iterations",
                "improvements",
                "milp_calls",
                "best_size",
                "final_size",
                "wall_time_s",
            )
            if isinstance(meta, dict)
        },
        "wall_s": time.time() - t0,
        "beats_164": len(pts) > 164 and bool(ok_a) and bool(ok_b),
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH3_from_scratch")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "lns_from_partial_n100.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True, default=str)
        f.write("\n")
    if out["beats_164"]:
        with open(os.path.join(RUN, "CANDIDATES", "n100_from_partial_lns.json"), "w", encoding="utf-8") as f:
            json.dump({"n": 100, "size": len(pts), "points": [list(p) for p in pts]}, f, indent=2)
    print(json.dumps(out, indent=2, default=str), flush=True)


if __name__ == "__main__":
    main()
