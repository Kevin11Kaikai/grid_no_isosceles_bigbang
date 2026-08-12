#!/usr/bin/env python3
"""LH-4: Keep most of S0; Rem = random 20 baseline points; Add = midband∪frame∪LB<=8; r=2.

Tests whether a large Rem pool + diverse Add (not low-LB-only) admits r=2 at 165.
"""
from __future__ import annotations

import gzip
import json
import os
import random
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402


def ring(p, n=100):
    x, y = p
    return min(x, y, n - 1 - x, n - 1 - y)


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    t0 = time.time()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    rng = random.Random(99)
    rem = sorted(rng.sample(s0, 40))
    with gzip.open(
        os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz"),
        "rt",
        encoding="utf-8",
    ) as f:
        detail = json.load(f)
    add = set()
    for r in detail["all_qs_compact"]:
        if int(r["lower_bound_min_deletions"]) <= 8:
            q = (int(r["q"][0]), int(r["q"][1]))
            if q not in s0_set:
                add.add(q)
    for x in range(100):
        for y in range(100):
            p = (x, y)
            if p in s0_set:
                continue
            rd = ring(p)
            if rd <= 8 or 10 <= rd <= 26:
                add.add(p)
    add_l = sorted(add)
    uh = universe_hash(rem, add_l)
    print(
        json.dumps({"n_rem": len(rem), "n_add": len(add_l), "n_vars": len(rem) + len(add_l), "hash": uh}),
        flush=True,
    )
    result = hamming_shell_search(
        n=100,
        s0=s0,
        removable=rem,
        addable=add_l,
        r=2,
        time_budget_s=480.0,
        seed=99,
        u_id="U_hybrid_rem40_diverseAdd_r2",
        universe_hash_str=uh,
        per_round_time_limit_s=40.0,
        symmetry_mode="asymmetric",
    )
    out = {
        "status": result.status,
        "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
        "rounds": (result.meta or {}).get("rounds"),
        "final_cuts": (result.meta or {}).get("final_cuts"),
        "wall_time_s": (result.meta or {}).get("wall_time_s"),
        "universe_hash": uh,
        "n_rem": len(rem),
        "n_add": len(add_l),
        "wall_s": time.time() - t0,
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH4_hybrid")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "hybrid_rem40_r2.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(json.dumps({"path": path, **out}, indent=2), flush=True)


if __name__ == "__main__":
    main()
