#!/usr/bin/env python3
"""Maximize legal extension of rem2 soft core (k=5 -> core ~160).

Lazy CP-SAT: maximize free vars; on illegal add witness cuts; on legal raise LB.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter, defaultdict
from typing import Dict, List, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from ortools.sat.python import cp_model  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
N = 100


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


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    src = os.path.join(RUN, "EXPERIMENTS", "LH3_forced_exchange", "seed504_points_v25.json")
    data = json.load(open(src, encoding="utf-8"))
    pts = [tuple(p) for p in data["points"]]
    wits = witnesses(pts)
    pivots = Counter(t[0] for t in wits)
    ranked = [p for p, _ in pivots.most_common()]
    strip = set(ranked[:5])
    core: List[Point] = []
    st = IncrementalIsoscelesFreeSet(N)
    for p in pts:
        if p in strip:
            continue
        if st.can_add(p)[0]:
            st.add_point(p)
            core.append(p)
    free = [(x, y) for x in range(N) for y in range(N) if (x, y) not in set(core)]
    print(json.dumps({"core": len(core), "free": len(free)}), flush=True)

    time_s = float(os.environ.get("W3_CHEAP_S", "1800"))
    workers = int(os.environ.get("W3_WORKERS", "6"))
    cuts: Set[Tuple[Point, Point, Point]] = set()
    t0 = time.time()
    rounds = 0
    best_size = len(core)
    best_pts = list(core)
    lb_extra = 0  # minimum free points beyond core
    status = "TIMEOUT"
    proved_max = None
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
        rem = max(0.5, time_s - (time.time() - t0))
        solver.parameters.max_time_in_seconds = min(40.0, rem)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = 9500 + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            # cannot reach lb_extra free points
            proved_max = best_size
            status = "MAX_PROVED" if best_size >= len(core) else "INFEASIBLE_SCOPED"
            break
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT"
            break
        sel = list(core) + [p for p, v in z.items() if solver.Value(v) == 1]
        w = witnesses(sel)
        if not w:
            if len(sel) > best_size:
                best_size = len(sel)
                best_pts = sel
                print(json.dumps({"new_best_legal": best_size, "round": rounds}), flush=True)
            # search for strictly larger
            lb_extra = best_size - len(core) + 1
            if best_size >= 165:
                status = "FEASIBLE_LEGAL_GE165"
                break
            continue
        before = len(cuts)
        for trip in w:
            cuts.add(tuple(sorted(trip)))
        if len(cuts) == before:
            status = "TIMEOUT"
            break
        if rounds % 100 == 0:
            print(
                json.dumps(
                    {
                        "round": rounds,
                        "cuts": len(cuts),
                        "best": best_size,
                        "lb_extra": lb_extra,
                    }
                ),
                flush=True,
            )

    out = {
        "schema": "w3_rem2_core_maximize_v1",
        "core_size": len(core),
        "best_legal_size": best_size,
        "proved_max": proved_max,
        "status": status,
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_time_s": time.time() - t0,
    }
    if best_size >= 165:
        ok_a, _ = is_legal_pivot_method(best_pts, N)
        ok_b, _ = verify_independent(best_pts, N)
        out["dual"] = {"oracle": ok_a, "indep": ok_b, "hash": sha256_of_points(best_pts)}
        cand = os.path.join(RUN, "CANDIDATES", "rem2_core160_max_legal.json")
        json.dump({"points": [list(p) for p in best_pts], **out}, open(cand, "w"), indent=2)
        out["candidate"] = cand
    elif best_size > len(core):
        # save best legal extension even if <165
        path_pts = os.path.join(RUN, "EXPERIMENTS", "W3_rem2_residual", f"core160_best{best_size}.json")
        json.dump(
            {"points": [list(p) for p in best_pts], "size": best_size},
            open(path_pts, "w"),
            indent=2,
        )
        out["best_points_path"] = path_pts
    path = os.path.join(RUN, "EXPERIMENTS", "W3_rem2_residual", "core160_maximize.json")
    json.dump(out, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
