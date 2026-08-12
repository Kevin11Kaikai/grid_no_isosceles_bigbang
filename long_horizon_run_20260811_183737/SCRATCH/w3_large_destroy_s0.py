#!/usr/bin/env python3
"""Wave3: one-shot large structured destroys on official S0 → exact MILP repair.

Forces |S0\\fixed| large (not S0+1). Seek |S|>=165.
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.lns_exact_repair import exact_repair_region  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]
N = 100


def dual(pts):
    oka, _ = is_legal_pivot_method(pts, N)
    okb, _ = verify_independent(pts, N)
    return {"oracle": bool(oka), "indep": bool(okb), "size": len(pts), "hash": sha256_of_points(pts)}


def region_frame(depth: int) -> List[Point]:
    return [
        (x, y)
        for x in range(N)
        for y in range(N)
        if min(x, y, N - 1 - x, N - 1 - y) < depth
    ]


def region_box(cx, cy, r) -> List[Point]:
    return [
        (x, y)
        for x in range(max(0, cx - r), min(N, cx + r + 1))
        for y in range(max(0, cy - r), min(N, cy + r + 1))
    ]


def region_band_rows(y0, y1) -> List[Point]:
    return [(x, y) for x in range(N) for y in range(y0, y1)]


def try_destroy(s0: Set[Point], region: List[Point], milp_s: float, tag: str) -> dict:
    removed = [p for p in region if p in s0]
    fixed = s0 - set(removed)
    cands = [p for p in region if p not in fixed]
    # optionally expand candidates to halo empties in region only
    t0 = time.time()
    selected, meta = exact_repair_region(N, fixed, cands, time_limit_s=milp_s)
    new_set = sorted(fixed | set(selected))
    d = dual(new_set)
    row = {
        "tag": tag,
        "n_removed": len(removed),
        "n_fixed": len(fixed),
        "n_cands": len(cands),
        "n_selected": len(selected),
        "final_size": len(new_set),
        "delta_vs_164": len(new_set) - 164,
        "dual": d,
        "repair_meta": meta,
        "wall_s": time.time() - t0,
    }
    return row


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_large_destroy")
    os.makedirs(exp, exist_ok=True)
    s0 = set((int(x), int(y)) for x, y in SOL_100)
    milp = float(os.environ.get("W3_MILP_S", "30"))
    rows = []
    plans = []
    for d in (2, 3, 4, 5):
        plans.append((f"frame_d{d}", region_frame(d)))
    for cx, cy, r in ((25, 25, 12), (50, 50, 14), (75, 75, 12), (50, 20, 15), (20, 50, 15)):
        plans.append((f"box_{cx}_{cy}_r{r}", region_box(cx, cy, r)))
    for y0, y1 in ((0, 8), (46, 54), (92, 100), (20, 35)):
        plans.append((f"rows_{y0}_{y1}", region_band_rows(y0, y1)))

    for tag, reg in plans:
        # cap region
        if len(reg) > 500:
            # keep all S0∩reg plus random empties up to 500
            import random

            rng = random.Random(hash(tag) & 0xFFFFFFFF)
            must = [p for p in reg if p in s0]
            rest = [p for p in reg if p not in s0]
            rng.shuffle(rest)
            reg = must + rest[: max(0, 500 - len(must))]
        row = try_destroy(s0, reg, milp, tag)
        rows.append(row)
        print(
            json.dumps(
                {
                    "tag": tag,
                    "final_size": row["final_size"],
                    "delta": row["delta_vs_164"],
                    "n_removed": row["n_removed"],
                    "n_selected": row["n_selected"],
                    "wall_s": round(row["wall_s"], 2),
                }
            ),
            flush=True,
        )
        if row["delta_vs_164"] > 0 and row["dual"]["oracle"] and row["dual"]["indep"]:
            cand = os.path.join(RUN, "CANDIDATES", f"large_destroy_{tag}_legal.json")
            # need points — recompute
            removed = [p for p in reg if p in s0]
            fixed = s0 - set(removed)
            cands = [p for p in reg if p not in fixed]
            selected, _ = exact_repair_region(N, fixed, cands, time_limit_s=milp)
            pts = sorted(fixed | set(selected))
            json.dump({"points": [list(p) for p in pts], **row}, open(cand, "w"), indent=2)
            row["candidate"] = cand
            break

    out = {
        "schema": "w3_large_destroy_v1",
        "rows": [{k: v for k, v in r.items()} for r in rows],
        "best_final": max((r["final_size"] for r in rows), default=0),
        "any_plus": any(r["delta_vs_164"] > 0 and r["dual"]["oracle"] for r in rows),
    }
    path = os.path.join(exp, "summary.json")
    json.dump(out, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    print(json.dumps({"done": True, "best_final": out["best_final"], "any_plus": out["any_plus"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
