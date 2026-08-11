#!/usr/bin/env python3
"""LH-2 Route C evolution: fixed |S|=165 starting from baseline+random, eject witness pivots.

New operator vs Wave2 C: identify current witness pivots and force-eject them + refill
from a large external pool (not residual-halo-only). Short multi-seed pilot.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from collections import defaultdict
from typing import List, Tuple

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


def witness_pivots(points):
    pts = [tuple(p) for p in points]
    pivots = []
    for pivot in pts:
        groups = defaultdict(list)
        for q in pts:
            if q == pivot:
                continue
            groups[sq(pivot, q)].append(q)
        for members in groups.values():
            if len(members) >= 2:
                pivots.append(pivot)
                break
    return pivots


def build_fixed(seed: int) -> List[Point]:
    rng = random.Random(seed)
    s0 = [tuple(p) for p in SOL_100]
    # Start: baseline, remove 2 random, add random empties until TARGET with possible V>0
    # Better: use baseline, add one random empty (illegal), then repair by swaps
    occupied = set(s0)
    empty = [(x, y) for x in range(N) for y in range(N) if (x, y) not in occupied]
    rng.shuffle(empty)
    # Force cardinality 165 by adding 1 empty (likely V>0)
    pts = list(s0) + [empty[0]]
    return pts


def run_seed(seed: int, seconds: float = 90.0) -> dict:
    rng = random.Random(seed)
    pts = build_fixed(seed)
    assert len(pts) == TARGET
    best_v = conflict_count(pts, N)
    best_pts = list(pts)
    t0 = time.time()
    iters = 0
    accepts = 0
    while time.time() - t0 < seconds:
        iters += 1
        pivots = witness_pivots(pts)
        if not pivots:
            # already legal?
            v = conflict_count(pts, N)
            if v == 0:
                return {
                    "seed": seed,
                    "status": "V0_LEGAL",
                    "best_V": 0,
                    "iters": iters,
                    "points": [list(p) for p in pts],
                    "wall_s": time.time() - t0,
                }
        # eject 1-3 witness pivots (or random if none)
        eject_n = rng.choice([1, 2, 3])
        if pivots:
            rem = rng.sample(pivots, min(eject_n, len(pivots)))
        else:
            rem = rng.sample(pts, eject_n)
        core = [p for p in pts if p not in set(rem)]
        occ = set(core)
        empty = [(x, y) for x in range(N) for y in range(N) if (x, y) not in occ]
        rng.shuffle(empty)
        # refill to TARGET preferring can_add when possible
        st = IncrementalIsoscelesFreeSet(N)
        legal_core = True
        for p in core:
            if not st.add_point(p):
                legal_core = False
                break
        new_pts = list(core)
        if legal_core:
            for p in empty:
                if len(new_pts) >= TARGET:
                    break
                ok, _ = st.can_add(p)
                if ok:
                    st.add_point(p)
                    new_pts.append(p)
            # if still short, force-add (may increase V)
            for p in empty:
                if len(new_pts) >= TARGET:
                    break
                if p not in set(new_pts):
                    new_pts.append(p)
        else:
            # core illegal: just random refill
            for p in empty:
                if len(new_pts) >= TARGET:
                    break
                new_pts.append(p)
        new_pts = new_pts[:TARGET]
        v = conflict_count(new_pts, N)
        if v < best_v or (v == best_v and rng.random() < 0.05):
            pts = new_pts
            accepts += 1
            if v < best_v:
                best_v = v
                best_pts = list(new_pts)
                if best_v == 0:
                    break
        elif rng.random() < 0.02:
            pts = new_pts  # occasional explore
    return {
        "seed": seed,
        "status": "V0_LEGAL" if best_v == 0 else "BEST_V",
        "best_V": best_v,
        "iters": iters,
        "accepts": accepts,
        "wall_s": time.time() - t0,
        "points": [list(p) for p in best_pts] if best_v == 0 else None,
    }


def main():
    t0 = time.time()
    results = [run_seed(s, seconds=75.0) for s in (301, 302, 303, 304)]
    out = {
        "schema": "lh2_fixedcard_conflict_eject_v1",
        "results": results,
        "best_V": min(r["best_V"] for r in results),
        "any_v0": any(r["status"] == "V0_LEGAL" for r in results),
        "wall_s": time.time() - t0,
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH2_fixedcard_eject")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "conflict_eject_n100.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "path": path,
                "best_V": out["best_V"],
                "any_v0": out["any_v0"],
                "per_seed": [{k: r[k] for k in ("seed", "best_V", "iters", "status")} for r in results],
                "wall_s": out["wall_s"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
