#!/usr/bin/env python3
"""Newfam v3: (G) S0-avoiding grow+max; (H) densest-row band destroy with row blacklist."""
from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter
from typing import List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from w3_new_families_v1 import dual, maximize_core, ring  # noqa: E402

Point = Tuple[int, int]
N = 100
TARGET = 165
EXP = os.path.join(RUN, "EXPERIMENTS", "W3_new_families")


def grow_avoiding(forbidden: Set[Point], mode: str, seconds: float, seed: int) -> dict:
    rng = random.Random(seed)
    st = IncrementalIsoscelesFreeSet(N)
    cells = [(x, y) for x in range(N) for y in range(N) if (x, y) not in forbidden]
    if mode == "boundary_first":
        cells.sort(key=lambda p: (ring(p, N), rng.random()))
    elif mode == "center_first":
        cells.sort(key=lambda p: (-ring(p, N), rng.random()))
    else:
        rng.shuffle(cells)
    import time

    t0 = time.time()
    for p in cells:
        if time.time() - t0 > seconds * 0.45:
            break
        if st.can_add(p)[0]:
            st.add_point(p)
    best = sorted(st.points)
    best_size = len(best)
    while time.time() - t0 < seconds:
        if not st.points:
            break
        batch = rng.sample(sorted(st.points), k=min(rng.choice([2, 3, 5, 8]), len(st.points)))
        for p in batch:
            st.remove_point(p)
        refill = list(cells)
        rng.shuffle(refill)
        for p in refill:
            if st.can_add(p)[0]:
                st.add_point(p)
        if len(st.points) > best_size:
            best = sorted(st.points)
            best_size = len(best)
    d = dual(best, N)
    # Ensure no forbidden leaked
    leak = [p for p in best if p in forbidden]
    return {
        "size": best_size,
        "oracle": d["oracle"],
        "indep": d["indep"],
        "hash": d["hash"],
        "points": [list(p) for p in best],
        "mode": mode,
        "seed": seed,
        "forbidden": len(forbidden),
        "leaks": len(leak),
    }


def family_G(workers: int, grow_s: float, max_s: float) -> dict:
    s0 = set((int(x), int(y)) for x, y in SOL_100)
    rows = []
    best_g = None
    for seed, mode in [(801, "boundary_first"), (802, "center_first"), (803, "random"), (804, "boundary_first")]:
        g = grow_avoiding(s0, mode, grow_s, seed)
        print(json.dumps({"G_grow": {k: v for k, v in g.items() if k != "points"}}), flush=True)
        grow_row = {k: v for k, v in g.items() if k != "points"}
        if g["oracle"] and g["indep"] and (best_g is None or g["size"] > best_g["size"]):
            best_g = g
        # Maximize while still blacklisting S0
        core = [tuple(p) for p in g["points"]]
        res = maximize_core(N, core, max_s, workers, seed=8000 + seed, target=TARGET, blacklist=s0)
        row = {k: v for k, v in res.items() if k != "points"}
        row.update({"plan": f"avoid_S0_{mode}_{seed}", "grow_size": g["size"], "grow_hash": g["hash"]})
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= TARGET and res.get("points"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"avoid_S0_{seed}_legal.json"), "w"), indent=2)
            break
    if best_g:
        json.dump(best_g, open(os.path.join(EXP, "best_avoid_S0_grow.json"), "w"), indent=2)
    return {
        "schema": "w3_newfam_G_avoid_S0_v1",
        "rows": rows,
        "best": max((r.get("best_legal_size") or r.get("grow_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= TARGET for r in rows),
        "best_grow": max((r.get("grow_size") or 0) for r in rows) if rows else 0,
    }


def family_H(workers: int, max_s: float) -> dict:
    s0 = set((int(x), int(y)) for x, y in SOL_100)
    row_ct = Counter(p[1] for p in s0)
    col_ct = Counter(p[0] for p in s0)
    densest_rows = [r for r, _ in row_ct.most_common(100)]
    densest_cols = [c for c, _ in col_ct.most_common(100)]
    rows = []
    plans = []
    for k in (8, 12, 16, 20):
        ban_rows = set(densest_rows[:k])
        rem = [p for p in s0 if p[1] in ban_rows]
        # Blacklist entire rows (all cells on those rows), not just rem points
        bl = {(x, y) for y in ban_rows for x in range(N)}
        plans.append((f"ban_rows_top{k}", sorted(s0 - set(rem)), bl, len(rem)))
        ban_cols = set(densest_cols[:k])
        rem = [p for p in s0 if p[0] in ban_cols]
        bl = {(x, y) for x in ban_cols for y in range(N)}
        plans.append((f"ban_cols_top{k}", sorted(s0 - set(rem)), bl, len(rem)))
    for i, (name, core, bl, nrem) in enumerate(plans):
        print(json.dumps({"H": name, "core": len(core), "bl": len(bl), "nrem": nrem}), flush=True)
        res = maximize_core(N, core, max_s, workers, seed=9000 + i, target=TARGET, blacklist=bl)
        row = {k: v for k, v in res.items() if k != "points"}
        row.update({"plan": name, "n_removed": nrem, "blacklist": len(bl)})
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= TARGET and res.get("points"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"famH_{name}_legal.json"), "w"), indent=2)
            break
    return {
        "schema": "w3_newfam_H_rowband_v1",
        "rows": rows,
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= TARGET for r in rows),
    }


def family_G2_destroy_avoid(workers: int, grow_s: float, max_s: float) -> dict:
    """If avoid-S0 grow hits free=0, destroy with non-parity kernels still avoiding S0."""
    s0 = set((int(x), int(y)) for x, y in SOL_100)
    path = os.path.join(EXP, "best_avoid_S0_grow.json")
    if os.path.exists(path):
        g = json.load(open(path))
    else:
        g = grow_avoiding(s0, "boundary_first", grow_s, 801)
    S = set(map(tuple, g["points"]))
    rows = []
    rng = random.Random(55)
    plans = [
        ("avoid_colmod3", [p for p in S if p[0] % 3 == 0]),
        ("avoid_ring_even", [p for p in S if ring(p, N) % 2 == 0]),
        ("avoid_rand40", rng.sample(sorted(S), k=min(40, len(S)))),
        ("avoid_rand70", rng.sample(sorted(S), k=min(70, len(S)))),
    ]
    for i, (name, rem) in enumerate(plans):
        core = sorted(S - set(rem))
        print(json.dumps({"G2": name, "core": len(core)}), flush=True)
        res = maximize_core(N, core, max_s, workers, seed=9100 + i, target=TARGET, blacklist=s0)
        row = {k: v for k, v in res.items() if k != "points"}
        row.update({"plan": name, "grow_size": g["size"]})
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= TARGET and res.get("points"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"{name}_legal.json"), "w"), indent=2)
            break
    return {
        "schema": "w3_newfam_G2_v1",
        "rows": rows,
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= TARGET for r in rows),
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    os.makedirs(EXP, exist_ok=True)
    workers = int(os.environ.get("W3_WORKERS", "4"))
    phase = os.environ.get("W3_PHASE", "all")
    summary = {"schema": "w3_newfam_v3_v1", "phases": {}}

    if phase in ("G", "all"):
        g = family_G(workers, grow_s=120.0, max_s=300.0)
        json.dump(g, open(os.path.join(EXP, "family_G_avoid_S0.json"), "w"), indent=2)
        summary["phases"]["G"] = {"best": g["best"], "best_grow": g["best_grow"], "any_plus": g["any_plus"]}
        print(json.dumps({"done_G": True, **summary["phases"]["G"]}), flush=True)
        g2 = family_G2_destroy_avoid(workers, grow_s=120.0, max_s=420.0)
        json.dump(g2, open(os.path.join(EXP, "family_G2_destroy.json"), "w"), indent=2)
        summary["phases"]["G2"] = {"best": g2["best"], "any_plus": g2["any_plus"]}
        print(json.dumps({"done_G2": True, **summary["phases"]["G2"]}), flush=True)

    if phase in ("H", "all"):
        h = family_H(workers, max_s=240.0)
        json.dump(h, open(os.path.join(EXP, "family_H_rowband.json"), "w"), indent=2)
        summary["phases"]["H"] = {"best": h["best"], "any_plus": h["any_plus"]}
        print(json.dumps({"done_H": True, **summary["phases"]["H"]}), flush=True)

    summary["any_plus"] = any(p.get("any_plus") for p in summary["phases"].values())
    summary["best"] = max((p.get("best") or 0) for p in summary["phases"].values()) if summary["phases"] else 0
    json.dump(summary, open(os.path.join(EXP, "summary_v3.json"), "w"), indent=2)
    print(json.dumps({"done_v3": True, **summary}, indent=2), flush=True)


if __name__ == "__main__":
    main()
