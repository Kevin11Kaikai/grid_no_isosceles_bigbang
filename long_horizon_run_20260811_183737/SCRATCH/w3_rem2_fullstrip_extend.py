#!/usr/bin/env python3
"""Exact-extend rem2 full-involved cores using only individually-addable free cells."""
from __future__ import annotations

import json
import os
import sys
import time
import random
from collections import defaultdict
from typing import Dict, List, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(RUN, "SCRATCH"))

from ortools.sat.python import cp_model  # noqa: E402
from fixedcard_forced_exchange import init_exchange  # noqa: E402
from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
N = 100
TARGET = 165


def sq(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def witnesses(points: Sequence[Point]):
    out = []
    for pivot in points:
        g: Dict[int, List[Point]] = defaultdict(list)
        for q in points:
            if q != pivot:
                g[sq(pivot, q)].append(q)
        for d, m in g.items():
            if len(m) < 2:
                continue
            for i in range(len(m)):
                for j in range(i + 1, len(m)):
                    out.append((pivot, m[i], m[j]))
    return out


def get_best(seed, seconds=50):
    s0 = [tuple(p) for p in SOL_100]
    s0_set = set(s0)
    rng = random.Random(seed)
    pts = init_exchange(s0, rng, r_min=2)
    best = list(pts)
    best_v = conflict_count(pts, N)
    t0 = time.time()
    while time.time() - t0 < seconds:
        k = rng.choice([1, 2, 3])
        rem = list(pts)
        rng.shuffle(rem)
        remove = rem[:k]
        core = [p for p in pts if p not in set(remove)]
        occ = set(core)
        pool = [(x, y) for x in range(N) for y in range(N) if (x, y) not in occ]
        rng.shuffle(pool)
        st = IncrementalIsoscelesFreeSet(N)
        ok = True
        for p in core:
            if not st.add_point(p):
                ok = False
                break
        added = []
        if ok:
            for p in pool:
                if len(added) >= k:
                    break
                if st.can_add(p)[0]:
                    st.add_point(p)
                    added.append(p)
        for p in pool:
            if len(added) >= k:
                break
            if p not in set(added) and p not in occ:
                added.append(p)
        new = core + added
        if len(new) != TARGET or len(s0_set - set(new)) < 2:
            continue
        v = conflict_count(new, N)
        if v < best_v:
            best_v = v
            best = list(new)
            pts = new
        elif v <= best_v:
            pts = new
    return best, best_v


def full_involved_core(pts):
    wits = witnesses(pts)
    involved = set()
    for a, b, c in wits:
        involved.add(a)
        involved.add(b)
        involved.add(c)
    core = []
    st = IncrementalIsoscelesFreeSet(N)
    for p in pts:
        if p in involved:
            continue
        if st.can_add(p)[0]:
            st.add_point(p)
            core.append(p)
    addable = []
    for x in range(N):
        for y in range(N):
            p = (x, y)
            if p in st.points:
                continue
            if st.can_add(p)[0]:
                addable.append(p)
    return core, addable


def exact_extend(core, free, time_s, workers, seed):
    need = TARGET - len(core)
    if need > len(free) or need <= 0:
        return {"status": "CAPACITY_FAIL", "core": len(core), "free": len(free), "need": need}
    cuts: Set[Tuple[Point, Point, Point]] = set()
    t0 = time.time()
    rounds = 0
    status = "TIMEOUT"
    best_legal = []
    while time.time() - t0 < time_s:
        rounds += 1
        model = cp_model.CpModel()
        z = {p: model.NewBoolVar(f"z{p[0]}_{p[1]}") for p in free}
        model.Add(sum(z.values()) == need)
        for trip in cuts:
            free_in = [z[p] for p in trip if p in z]
            if free_in:
                model.Add(sum(free_in) <= len(free_in) - 1)
        solver = cp_model.CpSolver()
        rem = max(0.5, time_s - (time.time() - t0))
        solver.parameters.max_time_in_seconds = min(25.0, rem)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = seed + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            status = "INFEASIBLE_SCOPED"
            break
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT"
            break
        sel = list(core) + [p for p, v in z.items() if solver.Value(v) == 1]
        w = witnesses(sel)
        if not w:
            best_legal = sel
            status = "FEASIBLE_LEGAL"
            break
        before = len(cuts)
        for trip in w:
            cuts.add(tuple(sorted(trip)))
        if len(cuts) == before:
            status = "TIMEOUT"
            break
        if rounds % 100 == 0:
            print(json.dumps({"round": rounds, "cuts": len(cuts)}), flush=True)
    out = {
        "status": status,
        "core": len(core),
        "free": len(free),
        "need": need,
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_time_s": time.time() - t0,
    }
    if best_legal:
        ok_a, _ = is_legal_pivot_method(best_legal, N)
        ok_b, _ = verify_independent(best_legal, N)
        out["dual"] = {"oracle": ok_a, "indep": ok_b, "hash": sha256_of_points(best_legal)}
        out["points"] = [list(p) for p in best_legal]
    return out


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_rem2_residual")
    os.makedirs(exp, exist_ok=True)
    workers = int(os.environ.get("W3_WORKERS", "6"))
    per = float(os.environ.get("W3_PER_S", "900"))
    rows = []
    for seed in (602, 603, 605, 701, 504):
        if seed == 504:
            pts = [
                tuple(p)
                for p in json.load(
                    open(
                        os.path.join(RUN, "EXPERIMENTS", "LH3_forced_exchange", "seed504_points_v25.json")
                    )
                )["points"]
            ]
            v = 25
        else:
            pts, v = get_best(seed, 40)
        core, addable = full_involved_core(pts)
        print(
            json.dumps(
                {"seed": seed, "V": v, "core": len(core), "addable": len(addable), "need": TARGET - len(core)}
            ),
            flush=True,
        )
        res = exact_extend(core, addable, per, workers, seed=9700 + seed)
        row = {k: v for k, v in res.items() if k != "points"}
        row.update({"seed": seed, "start_V": v})
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("status") == "FEASIBLE_LEGAL" and res.get("points"):
            cand = os.path.join(RUN, "CANDIDATES", f"rem2_fullstrip_s{seed}_legal.json")
            json.dump(res, open(cand, "w"), indent=2)
            break
    out = {
        "schema": "w3_rem2_fullstrip_addable_extend_v1",
        "rows": rows,
        "any_legal": any(r.get("status") == "FEASIBLE_LEGAL" for r in rows),
    }
    path = os.path.join(exp, "fullstrip_addable_extend.json")
    json.dump(out, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    print(json.dumps({"done": True, "any_legal": out["any_legal"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
