#!/usr/bin/env python3
"""Wave3 R2: spatial-block Hamming Rem/Add (new U_ids, outside killed Wave2/cert shells).

Rem = contiguous spatial knn-block of S0 (size 24/32); Add = empties in opposite
half / outer rings with low cert involvement. Primary r=2. Cheap-kill <=120s.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from typing import List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402

Point = Tuple[int, int]
N = 100


def ring(p: Point) -> int:
    x, y = p
    return min(x, y, N - 1 - x, N - 1 - y)


def knn_block(s0: List[Point], seed_idx: int, k: int) -> List[Point]:
    seed = s0[seed_idx % len(s0)]

    def d2(a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

    ranked = sorted(s0, key=lambda p: (d2(p, seed), p))
    return ranked[:k]


def opposite_add(s0_set: Set[Point], rem: List[Point], limit: int) -> List[Point]:
    # centroid of rem
    cx = sum(p[0] for p in rem) / len(rem)
    cy = sum(p[1] for p in rem) / len(rem)
    # prefer empties far from rem centroid and in outer rings
    cands = []
    for x in range(N):
        for y in range(N):
            p = (x, y)
            if p in s0_set:
                continue
            dx, dy = x - cx, y - cy
            dist2 = dx * dx + dy * dy
            cands.append((-(dist2), -ring(p), p))
    cands.sort()
    return [p for _, __, p in cands[:limit]]


def outer_ring_add(s0_set: Set[Point], r_lo: int, r_hi: int, limit: int) -> List[Point]:
    out = [
        (x, y)
        for x in range(N)
        for y in range(N)
        if (x, y) not in s0_set and r_lo <= ring((x, y)) <= r_hi
    ]
    out.sort(key=lambda p: (ring(p), p))
    return out[:limit]


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_spatial_hamming")
    os.makedirs(exp, exist_ok=True)
    s0 = [tuple(p) for p in SOL_100]
    s0_set = set(s0)
    plans = []
    # three Rem seeds × two Add styles
    for seed_idx, k in ((0, 24), (40, 24), (80, 32), (120, 32)):
        rem = knn_block(s0, seed_idx, k)
        for add_name, add in (
            (f"opp400", opposite_add(s0_set, rem, 400)),
            (f"outer_r8_20_500", outer_ring_add(s0_set, 8, 20, 500)),
        ):
            u_id = f"U_spatial_knn{k}_s{seed_idx}_Add_{add_name}_r2"
            plans.append((u_id, rem, add))

    rows = []
    t0 = time.time()
    for u_id, rem, add in plans:
        uh = universe_hash(rem, add)
        path = os.path.join(exp, f"{u_id}_cheap.json")
        print(json.dumps({"start": u_id, "rem": len(rem), "add": len(add), "uh": uh[:12]}), flush=True)
        res = hamming_shell_search(
            n=N,
            s0=s0,
            removable=rem,
            addable=add,
            r=2,
            time_budget_s=90.0,
            seed=42,
            u_id=u_id,
            universe_hash_str=uh,
            per_round_time_limit_s=20.0,
            checkpoint_path=path,
        )
        row = {
            "u_id": u_id,
            "status": res.status,
            "rem": len(rem),
            "add": len(add),
            "uh": uh,
            "meta": {k: res.meta.get(k) for k in ("rounds", "cuts", "wall_time_s", "best_size") if isinstance(res.meta, dict)},
        }
        if res.points:
            row["dual"] = res.meta.get("dual") if isinstance(res.meta, dict) else None
            cand = os.path.join(RUN, "CANDIDATES", f"{u_id}_legal.json")
            json.dump({"points": [list(p) for p in res.points], **row}, open(cand, "w"), indent=2)
        json.dump(row, open(path, "w"), indent=2)
        open(path, "a").write("\n")
        rows.append(row)
        print(json.dumps(row), flush=True)
        if res.status in ("FEASIBLE", "FEASIBLE_LEGAL") or (res.points and len(res.points) >= 165):
            break

    summary = {
        "schema": "w3_spatial_hamming_v1",
        "rows": rows,
        "any_feas": any(r["status"] in ("FEASIBLE", "FEASIBLE_LEGAL") for r in rows),
        "wall_s": time.time() - t0,
    }
    sp = os.path.join(exp, "summary.json")
    json.dump(summary, open(sp, "w"), indent=2)
    open(sp, "a").write("\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
