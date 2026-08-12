#!/usr/bin/env python3
"""(I) n64 aggressive LNS from S0 toward 113; (J) merge two avoid-S0 sets via destroy+max in union."""
from __future__ import annotations

import json
import os
import random
import sys
import time
from typing import List, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from data.baselines.official_raw import SOL_64  # noqa: E402
from src.search.lns import lns_run  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
from w3_new_families_v1 import maximize_core  # noqa: E402

Point = Tuple[int, int]
EXP = os.path.join(RUN, "EXPERIMENTS", "W3_new_families")


def dual64(pts):
    oka, _ = is_legal_pivot_method(pts, 64)
    okb, _ = verify_independent(pts, 64)
    return {"oracle": bool(oka), "indep": bool(okb), "size": len(pts), "hash": sha256_of_points(pts)}


def run_n64_lns(workers_unused: int = 4) -> dict:
    start = [(int(x), int(y)) for x, y in SOL_64]
    rows = []
    best_size = 112
    best_pts = list(start)
    for seed, frac, budget in [
        (1001, (0.10, 0.35), 600.0),
        (1002, (0.20, 0.50), 600.0),
        (1003, (0.30, 0.60), 600.0),
        (1004, (0.15, 0.45), 900.0),
        (1005, (0.25, 0.55), 900.0),
    ]:
        print(json.dumps({"n64_lns": seed, "frac": frac, "budget": budget}), flush=True)
        best, meta = lns_run(64, start, budget, seed=seed, destroy_frac_range=frac)
        d = dual64(best)
        row = {"seed": seed, "frac": list(frac), **meta, **d}
        rows.append(row)
        print(json.dumps({k: row[k] for k in row if k != "improvements"}, indent=2), flush=True)
        if d["size"] > best_size and d["oracle"] and d["indep"]:
            best_size = d["size"]
            best_pts = list(best)
            start = list(best)  # warm chain
        if d["size"] >= 113 and d["oracle"] and d["indep"]:
            cand = {
                "points": [list(p) for p in best],
                **d,
                "seed": seed,
                "meta": meta,
            }
            json.dump(cand, open(os.path.join(RUN, "CANDIDATES", f"n64_lns_{seed}_legal113.json"), "w"), indent=2)
            break
    out = {
        "schema": "w3_n64_lns_v1",
        "rows": rows,
        "best": best_size,
        "any_plus": best_size >= 113,
        "best_hash": sha256_of_points(best_pts) if best_pts else None,
    }
    json.dump(out, open(os.path.join(EXP, "family_I_n64_lns.json"), "w"), indent=2)
    return out


def run_avoid_merge(workers: int) -> dict:
    path = os.path.join(EXP, "best_avoid_S0_grow.json")
    # Also grow a second if needed
    from data.baselines.official_raw import SOL_100
    from w3_new_families_v3 import grow_avoiding

    s0 = set((int(x), int(y)) for x, y in SOL_100)
    if os.path.exists(path):
        g1 = json.load(open(path))
    else:
        g1 = grow_avoiding(s0, "center_first", 120.0, 802)
    g2 = grow_avoiding(s0, "boundary_first", 120.0, 901)
    A = set(map(tuple, g1["points"]))
    B = set(map(tuple, g2["points"]))
    print(
        json.dumps(
            {
                "merge": True,
                "a": g1["size"],
                "b": g2["size"],
                "inter": len(A & B),
                "union": len(A | B),
            }
        ),
        flush=True,
    )
    rows = []
    # Maximize from A with free pool unrestricted except S0 blacklist — already did.
    # Instead: destroy half of A, maximize with blacklist = S0, warm universe bias via starting from A∩B or A-destroy
    rng = random.Random(42)
    for k, name in ((30, "merge_desA30"), (50, "merge_desA50"), (40, "merge_desB40")):
        if name.startswith("merge_desA"):
            rem = set(rng.sample(sorted(A), k=min(k, len(A))))
            core = sorted(A - rem)
        else:
            rem = set(rng.sample(sorted(B), k=min(k, len(B))))
            core = sorted(B - rem)
        # Allow refill including B\A cells: no blacklist of B, only S0
        res = maximize_core(100, core, 480.0, workers, seed=9200 + k, target=165, blacklist=s0)
        row = {kk: vv for kk, vv in res.items() if kk != "points"}
        row.update({"plan": name, "core": len(core), "inter": len(A & B), "union": len(A | B)})
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= 165 and res.get("points"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"{name}_legal.json"), "w"), indent=2)
            break
    # Also maximize from intersection if large enough else from empty seed of union greedily
    inter = sorted(A & B)
    if len(inter) >= 20:
        res = maximize_core(100, inter, 480.0, workers, seed=9301, target=165, blacklist=s0)
        row = {kk: vv for kk, vv in res.items() if kk != "points"}
        row["plan"] = "merge_inter"
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
    out = {
        "schema": "w3_avoid_merge_v1",
        "a_hash": g1["hash"],
        "b_hash": g2.get("hash"),
        "rows": rows,
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= 165 for r in rows),
    }
    json.dump(out, open(os.path.join(EXP, "family_J_avoid_merge.json"), "w"), indent=2)
    return out


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    os.makedirs(EXP, exist_ok=True)
    workers = int(os.environ.get("W3_WORKERS", "4"))
    phase = os.environ.get("W3_PHASE", "all")
    summary = {"schema": "w3_n64_merge_v1", "phases": {}}
    if phase in ("I", "all"):
        i = run_n64_lns()
        summary["phases"]["I"] = {"best": i["best"], "any_plus": i["any_plus"]}
        print(json.dumps({"done_I": True, **summary["phases"]["I"]}), flush=True)
    if phase in ("J", "all"):
        j = run_avoid_merge(workers)
        summary["phases"]["J"] = {"best": j["best"], "any_plus": j["any_plus"]}
        print(json.dumps({"done_J": True, **summary["phases"]["J"]}), flush=True)
    summary["any_plus"] = any(p.get("any_plus") for p in summary["phases"].values())
    json.dump(summary, open(os.path.join(EXP, "summary_IJ.json"), "w"), indent=2)
    print(json.dumps({"done_IJ": True, **summary}, indent=2), flush=True)


if __name__ == "__main__":
    main()
