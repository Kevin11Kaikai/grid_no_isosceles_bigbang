#!/usr/bin/env python3
"""Build legal mid-size set via parity destroy, then aggressive LNS / multi-destroy maximize."""
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

from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.search.lns import lns_run  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
from w3_global_refill_after_destroy import maximize_from_core  # noqa: E402

Point = Tuple[int, int]
N = 100


def dual(pts):
    oka, _ = is_legal_pivot_method(pts, N)
    okb, _ = verify_independent(pts, N)
    return {"oracle": bool(oka), "indep": bool(okb), "size": len(pts), "hash": sha256_of_points(pts)}


def maximize_saving_points(core, time_s, workers, seed):
    """Like maximize_from_core but always returns best points when legal improved."""
    res = maximize_from_core(core, time_s, workers, seed)
    return res


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_midset_lns")
    os.makedirs(exp, exist_ok=True)
    workers = int(os.environ.get("W3_WORKERS", "4"))

    grow = json.load(open(os.path.join(RUN, "EXPERIMENTS", "W3_grow_destroy_max", "grow_seed203_spiral_mix.json")))
    S = set(tuple(p) for p in grow["points"])
    rem = [p for p in S if (p[0] + p[1]) % 2 == 0]
    core = sorted(S - set(rem))
    print(json.dumps({"phase": "parity_max", "core": len(core)}), flush=True)
    # Patch: reimplement quick maximize that keeps points
    from collections import defaultdict
    from ortools.sat.python import cp_model
    from w3_global_refill_after_destroy import witnesses

    st = IncrementalIsoscelesFreeSet(N)
    for p in core:
        assert st.add_point(p)
    free = []
    for x in range(N):
        for y in range(N):
            p = (x, y)
            if p in st.points:
                continue
            if st.can_add(p)[0]:
                free.append(p)
    cuts = set()
    t0 = time.time()
    time_s = 420.0
    best_size = len(core)
    best_pts = list(core)
    lb_extra = 0
    rounds = 0
    status = "TIMEOUT"
    while time.time() - t0 < time_s:
        rounds += 1
        model = cp_model.CpModel()
        z = {p: model.NewBoolVar(f"z{p[0]}_{p[1]}") for p in free}
        model.Maximize(sum(z.values()))
        if lb_extra > 0:
            model.Add(sum(z.values()) >= lb_extra)
        for trip in cuts:
            free_in = [z[p] for p in trip if p in z]
            if free_in:
                model.Add(sum(free_in) <= len(free_in) - 1)
        solver = cp_model.CpSolver()
        remt = max(0.5, time_s - (time.time() - t0))
        solver.parameters.max_time_in_seconds = min(30.0, remt)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = 2100 + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            status = "MAX_PROVED"
            break
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT"
            if lb_extra > 0 and time.time() - t0 < time_s - 5:
                continue
            break
        sel = list(core) + [p for p, v in z.items() if solver.Value(v) == 1]
        w = witnesses(sel)
        if not w:
            if len(sel) > best_size:
                best_size = len(sel)
                best_pts = sel
                print(json.dumps({"new_best": best_size, "round": rounds}), flush=True)
            lb_extra = best_size - len(core) + 1
            if best_size >= 165:
                status = "FEASIBLE_GE165"
                break
            continue
        before = len(cuts)
        for trip in w:
            cuts.add(tuple(sorted(trip)))
        if len(cuts) == before:
            if time.time() - t0 < time_s - 5:
                continue
            break

    mid = {
        "status": status,
        "best_legal_size": best_size,
        "rounds": rounds,
        "cuts": len(cuts),
        "wall_s": time.time() - t0,
        "dual": dual(best_pts),
        "points": [list(p) for p in best_pts],
    }
    json.dump(mid, open(os.path.join(exp, "parity_midset.json"), "w"), indent=2)
    print(json.dumps({k: mid[k] for k in mid if k != "points"}, indent=2), flush=True)

    # Aggressive LNS from midset
    lns_rows = []
    start = [tuple(p) for p in mid["points"]]
    for seed, frac in ((301, (0.15, 0.45)), (302, (0.25, 0.55)), (303, (0.35, 0.65))):
        print(json.dumps({"phase": "lns", "seed": seed, "frac": frac}), flush=True)
        best, meta = lns_run(N, start, 600.0, seed=seed, destroy_frac_range=frac)
        d = dual(best)
        row = {"seed": seed, "frac": list(frac), **meta, **d, "hash": d["hash"]}
        lns_rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if d["oracle"] and d["indep"] and d["size"] >= 165:
            json.dump({"points": [list(p) for p in best], **row}, open(os.path.join(RUN, "CANDIDATES", f"midset_lns_{seed}_legal.json"), "w"), indent=2)
            break
        if d["size"] > len(start):
            start = list(best)

    # Multi-core destroy from midset: remove random 40%, maximize 8min
    S2 = set(tuple(p) for p in start)
    destroy_rows = []
    rng = random.Random(77)
    pts = sorted(S2)
    for i, k in enumerate((30, 50, 70)):
        rem = set(rng.sample(pts, k=min(k, len(pts))))
        core2 = sorted(S2 - rem)
        print(json.dumps({"phase": "redestroy", "k": k, "core": len(core2)}), flush=True)
        res = maximize_from_core(core2, 480.0, workers, seed=2200 + i)
        row = {kk: vv for kk, vv in res.items() if kk != "points"}
        row["k"] = k
        destroy_rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= 165 and res.get("dual", {}).get("oracle"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"midset_redestroy_k{k}_legal.json"), "w"), indent=2)
            break

    out = {
        "schema": "w3_midset_lns_v1",
        "mid_size": mid["best_legal_size"],
        "mid_hash": mid["dual"]["hash"],
        "lns_rows": lns_rows,
        "destroy_rows": destroy_rows,
        "best": max(
            [mid["best_legal_size"]]
            + [r.get("size", 0) for r in lns_rows]
            + [r.get("best_legal_size", 0) for r in destroy_rows]
        ),
        "any_plus": any(r.get("size", 0) >= 165 for r in lns_rows)
        or any(r.get("best_legal_size", 0) >= 165 for r in destroy_rows),
    }
    json.dump(out, open(os.path.join(exp, "summary.json"), "w"), indent=2)
    print(json.dumps({"done": True, "best": out["best"], "any_plus": out["any_plus"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
