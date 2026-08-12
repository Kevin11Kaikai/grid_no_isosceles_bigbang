#!/usr/bin/env python3
"""Fund survivors from newfam v1: lattice destroy-refill, ring-even escalate, intersection D."""
from __future__ import annotations

import json
import os
import random
import sys
import time
from typing import List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from data.baselines.official_raw import SOL_100  # noqa: E402
from w3_new_families_v1 import (  # noqa: E402
    dual,
    grow_from_seed,
    lattice_seed,
    maximize_core,
    ring,
)

Point = Tuple[int, int]
N = 100
TARGET = 165
EXP = os.path.join(RUN, "EXPERIMENTS", "W3_new_families")


def destroy_plans(S: Set[Point]):
    plans = []
    # NOT parity_even (killed midset) — use different kernels
    rem = [p for p in S if p[0] % 3 == 0]
    plans.append(("lat_colmod3_0", rem))
    rem = [p for p in S if ring(p, N) % 2 == 0]
    plans.append(("lat_ring_even", rem))
    rem = [p for p in S if abs(p[0] - p[1]) <= 15]
    plans.append(("lat_diagband15", rem))
    rem = [p for p in S if (p[0] // 10 + p[1] // 10) % 2 == 0]
    plans.append(("lat_block_checker", rem))
    rng = random.Random(99)
    pts = sorted(S)
    for k, name in ((25, "lat_rand25"), (45, "lat_rand45"), (70, "lat_rand70")):
        plans.append((name, rng.sample(pts, k=min(k, len(pts)))))
    return plans


def run_lattice_destroy(workers: int, grow_s: float, max_s: float) -> dict:
    # Rebuild best lattice grow from v1
    seed = lattice_seed(N, 3, 1, 2)
    from src.search.incremental_state import IncrementalIsoscelesFreeSet

    st = IncrementalIsoscelesFreeSet(N)
    kept = []
    for p in seed:
        if st.can_add(p)[0]:
            st.add_point(p)
            kept.append(p)
    g = grow_from_seed(N, kept, "boundary_first", grow_s, rng_seed=2202)
    print(json.dumps({"lattice_grow": {k: v for k, v in g.items() if k != "points"}}), flush=True)
    json.dump(g, open(os.path.join(EXP, "lattice_grow_for_destroy.json"), "w"), indent=2)
    S = set(map(tuple, g["points"]))
    rows = []
    for i, (name, rem) in enumerate(destroy_plans(S)):
        rem_set = set(map(tuple, rem))
        core = sorted(S - rem_set)
        # Allow re-add of rem (not forbid) — leave lattice basin freely
        print(json.dumps({"plan": name, "core": len(core), "removed": len(rem_set)}), flush=True)
        res = maximize_core(N, core, max_s, workers, seed=6000 + i, target=TARGET, blacklist=None)
        row = {k: v for k, v in res.items() if k != "points"}
        row.update({"plan": name, "n_removed": len(rem_set), "grow_size": g["size"]})
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= TARGET and res.get("points"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"lat_destroy_{name}_legal.json"), "w"), indent=2)
            break
    return {
        "schema": "w3_lattice_destroy_v1",
        "grow_hash": g["hash"],
        "grow_size": g["size"],
        "rows": rows,
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= TARGET for r in rows),
    }


def run_ring_even_escalate(workers: int, grow_s: float, max_s: float) -> dict:
    s0 = set((int(x), int(y)) for x, y in SOL_100)
    even = [p for p in s0 if ring(p, N) % 2 == 0]
    odd = set(p for p in s0 if ring(p, N) % 2 == 1)
    # Warm: grow from even-ring S0 seed, blacklist odd-ring S0 (force leave)
    g = grow_from_seed(N, even, "boundary_first", grow_s, rng_seed=3301)
    print(json.dumps({"ring_even_grow": {k: v for k, v in g.items() if k != "points"}}), flush=True)
    core = [tuple(p) for p in g["points"]]
    # Also try maximize from even-only core with blacklist odd
    res1 = maximize_core(N, sorted(even), max_s, workers, seed=7001, target=TARGET, blacklist=odd)
    row1 = {k: v for k, v in res1.items() if k != "points"}
    row1["plan"] = "even_core_forbid_odd"
    print(json.dumps(row1, indent=2), flush=True)
    res2 = maximize_core(N, core, max_s, workers, seed=7002, target=TARGET, blacklist=odd)
    row2 = {k: v for k, v in res2.items() if k != "points"}
    row2["plan"] = "even_grow_forbid_odd"
    row2["grow_size"] = g["size"]
    print(json.dumps(row2, indent=2), flush=True)
    # And maximize grown set without blacklist
    res3 = maximize_core(N, core, max_s * 0.5, workers, seed=7003, target=TARGET, blacklist=None)
    row3 = {k: v for k, v in res3.items() if k != "points"}
    row3["plan"] = "even_grow_readd"
    print(json.dumps(row3, indent=2), flush=True)
    rows = [row1, row2, row3]
    for res, tag in ((res1, "even_core"), (res2, "even_grow"), (res3, "even_readd")):
        if res.get("best_legal_size", 0) >= TARGET and res.get("points"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"ring_even_{tag}_legal.json"), "w"), indent=2)
    return {
        "schema": "w3_ring_even_esc_v1",
        "grow": {k: v for k, v in g.items() if k != "points"},
        "rows": rows,
        "best": max(r.get("best_legal_size") or 0 for r in rows),
        "any_plus": any(r.get("best_legal_size", 0) >= TARGET for r in rows),
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    os.makedirs(EXP, exist_ok=True)
    workers = int(os.environ.get("W3_WORKERS", "4"))
    phase = os.environ.get("W3_PHASE", "all")  # lat|ring|D|all

    summary = {"schema": "w3_newfam_v2_v1", "phases": {}}

    if phase in ("D", "all"):
        from w3_new_families_v1 import family_D_intersection

        d = family_D_intersection(workers, grow_s=90.0, max_s=360.0)
        json.dump(d, open(os.path.join(EXP, "family_D.json"), "w"), indent=2)
        summary["phases"]["D"] = {"best": d["best"], "any_plus": d["any_plus"]}
        print(json.dumps({"done_D": True, **summary["phases"]["D"]}), flush=True)

    if phase in ("lat", "all"):
        lat = run_lattice_destroy(workers, grow_s=120.0, max_s=420.0)
        json.dump(lat, open(os.path.join(EXP, "family_lattice_destroy.json"), "w"), indent=2)
        summary["phases"]["lat"] = {"best": lat["best"], "any_plus": lat["any_plus"]}
        print(json.dumps({"done_lat": True, **summary["phases"]["lat"]}), flush=True)

    if phase in ("ring", "all"):
        rg = run_ring_even_escalate(workers, grow_s=120.0, max_s=600.0)
        json.dump(rg, open(os.path.join(EXP, "family_ring_even_esc.json"), "w"), indent=2)
        summary["phases"]["ring"] = {"best": rg["best"], "any_plus": rg["any_plus"]}
        print(json.dumps({"done_ring": True, **summary["phases"]["ring"]}), flush=True)

    summary["any_plus"] = any(p.get("any_plus") for p in summary["phases"].values())
    summary["best"] = max((p.get("best") or 0) for p in summary["phases"].values()) if summary["phases"] else 0
    json.dump(summary, open(os.path.join(EXP, "summary_v2.json"), "w"), indent=2)
    print(json.dumps({"done_v2": True, **summary}, indent=2), flush=True)


if __name__ == "__main__":
    main()
