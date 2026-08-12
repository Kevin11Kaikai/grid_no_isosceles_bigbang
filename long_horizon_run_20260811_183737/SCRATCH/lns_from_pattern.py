#!/usr/bin/env python3
"""LH-3: Exact LNS starting from best pattern construction (annulus legal ~132)."""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.search.lns_exact_repair import lns_exact_run  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
import random


def build_annulus_legal(n=100, r0=0, r1=10, seed=0, seconds=25.0):
    rng = random.Random(seed)
    cand = []
    for x in range(n):
        for y in range(n):
            rd = min(x, y, n - 1 - x, n - 1 - y)
            if r0 <= rd <= r1:
                cand.append((x, y))
    rng.shuffle(cand)
    st = IncrementalIsoscelesFreeSet(n)
    for p in cand:
        ok, _ = st.can_add(p)
        if ok:
            st.add_point(p)
    t0 = time.time()
    order = cand[:]
    while time.time() - t0 < seconds:
        if not st.points:
            break
        rem = rng.sample(sorted(st.points), k=min(3, len(st.points)))
        for p in rem:
            st.remove_point(p)
        rng.shuffle(order)
        for p in order:
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
    start = build_annulus_legal()
    print(json.dumps({"start_size": len(start), "hash": sha256_of_points(start)}), flush=True)
    best, meta = lns_exact_run(n=100, initial_points=start, time_budget_s=420.0, seed=91)
    pts = [tuple(p) for p in best]
    ok_a, _ = is_legal_pivot_method(pts, 100)
    ok_b, _ = verify_independent(pts, 100)
    out = {
        "start_size": len(start),
        "final_size": len(pts),
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "final_hash": sha256_of_points(pts),
        "improvements": meta.get("improvements"),
        "iterations": meta.get("iterations"),
        "milp_calls": meta.get("milp_calls"),
        "beats_164": len(pts) > 164 and ok_a and ok_b,
        "wall_s": time.time() - t0,
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH3_patterns")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "lns_from_annulus.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    if out["beats_164"]:
        with open(os.path.join(RUN, "CANDIDATES", "n100_from_annulus_lns.json"), "w", encoding="utf-8") as f:
            json.dump({"n": 100, "size": len(pts), "points": [list(p) for p in pts]}, f, indent=2)
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
