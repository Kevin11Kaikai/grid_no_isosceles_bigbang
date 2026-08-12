#!/usr/bin/env python3
"""Wave3: soft residual — strip top-k witness pivots only, then exact-extend to 165."""
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
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402

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


def exact_extend(core: List[Point], time_s: float, workers: int, seed: int) -> dict:
    free = [(x, y) for x in range(N) for y in range(N) if (x, y) not in set(core)]
    need = TARGET - len(core)
    if need <= 0:
        return {"status": "CORE_TOO_LARGE", "core_size": len(core)}
    cuts: Set[Tuple[Point, Point, Point]] = set()
    t0 = time.time()
    rounds = 0
    status = "TIMEOUT"
    while time.time() - t0 < time_s:
        rounds += 1
        model = cp_model.CpModel()
        z = {p: model.NewBoolVar(f"z{p[0]}_{p[1]}") for p in free}
        model.Add(sum(z.values()) == need)
        core_set = set(core)
        for trip in cuts:
            free_in = [z[p] for p in trip if p in z]
            if not free_in:
                continue
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
            return {
                "status": "FEASIBLE_LEGAL",
                "core_size": len(core),
                "rounds": rounds,
                "final_cuts": len(cuts),
                "wall_time_s": time.time() - t0,
                "points": [list(p) for p in sel],
                "V": 0,
            }
        before = len(cuts)
        for trip in w:
            cuts.add(tuple(sorted(trip)))
        if len(cuts) == before:
            status = "TIMEOUT"
            break
    return {
        "status": status,
        "core_size": len(core),
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_time_s": time.time() - t0,
    }


def legalize_by_strip(pts: List[Point], strip: Set[Point]) -> List[Point]:
    core = [p for p in pts if p not in strip]
    st = IncrementalIsoscelesFreeSet(N)
    # may still be illegal if strip incomplete — drop points until legal
    kept = []
    for p in core:
        if st.can_add(p)[0]:
            st.add_point(p)
            kept.append(p)
    return kept


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_rem2_residual")
    os.makedirs(exp, exist_ok=True)
    src = os.path.join(RUN, "EXPERIMENTS", "LH3_forced_exchange", "seed504_points_v25.json")
    data = json.load(open(src, encoding="utf-8"))
    pts = [tuple(p) for p in data["points"]]
    wits = witnesses(pts)
    pivots = Counter(t[0] for t in wits)
    involved = set()
    for a, b, c in wits:
        involved.add(a)
        involved.add(b)
        involved.add(c)

    workers = int(os.environ.get("W3_WORKERS", "5"))
    per = float(os.environ.get("W3_PER_CORE_S", "420"))
    rows = []
    # full strip baseline already INFEAS — try soft strips
    plans = []
    # top-k pivots
    ranked = [p for p, _ in pivots.most_common()]
    for k in (5, 10, 15, 20, 25):
        plans.append(("top_pivots", k, set(ranked[:k])))
    # random half involved
    inv_l = sorted(involved)
    for k in (15, 25, 35):
        plans.append(("first_involved", k, set(inv_l[:k])))

    for kind, k, strip in plans:
        core = legalize_by_strip(pts, strip)
        print(json.dumps({"plan": kind, "k": k, "strip": len(strip), "core": len(core)}), flush=True)
        if len(core) >= TARGET:
            rows.append({"plan": kind, "k": k, "status": "CORE_TOO_LARGE", "core": len(core)})
            continue
        if len(core) < 100:
            rows.append({"plan": kind, "k": k, "status": "CORE_TOO_SMALL", "core": len(core)})
            continue
        res = exact_extend(core, per, workers, seed=9300 + k)
        res["plan"] = kind
        res["k"] = k
        rows.append({kk: vv for kk, vv in res.items() if kk != "points"})
        print(json.dumps(rows[-1], indent=2), flush=True)
        if res.get("status") == "FEASIBLE_LEGAL" and res.get("points"):
            cand = os.path.join(RUN, "CANDIDATES", f"rem2_soft_{kind}_k{k}_legal.json")
            json.dump(res, open(cand, "w"), indent=2)
            break

    summary = {
        "schema": "w3_rem2_soft_core_extend_v1",
        "source": src,
        "full_involved_strip_ref": "core_extend_s504.json INFEASIBLE_SCOPED",
        "rows": rows,
        "any_legal": any(r.get("status") == "FEASIBLE_LEGAL" for r in rows),
    }
    path = os.path.join(exp, "soft_core_extend_summary.json")
    json.dump(summary, open(path, "w", encoding="utf-8"), indent=2)
    open(path, "a", encoding="utf-8").write("\n")
    print(json.dumps({"done": True, "any_legal": summary["any_legal"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
