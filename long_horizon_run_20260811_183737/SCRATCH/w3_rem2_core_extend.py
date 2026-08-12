#!/usr/bin/env python3
"""Exact: extend legal rem2-residual core to |S|=165 (core forced on)."""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from ortools.sat.python import cp_model  # noqa: E402

from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
N = 100
TARGET = 165


def sq(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def witnesses(points: Sequence[Point]) -> List[Tuple[Point, Point, Point]]:
    out = []
    for pivot in points:
        g: Dict[int, List[Point]] = defaultdict(list)
        for q in points:
            if q != pivot:
                g[sq(pivot, q)].append(q)  # type: ignore[arg-type]
        for d, m in g.items():
            if len(m) < 2:
                continue
            for i in range(len(m)):
                for j in range(i + 1, len(m)):
                    out.append((pivot, m[i], m[j]))
    return out


def dual(pts):
    ok_a, _ = is_legal_pivot_method(pts, N)
    ok_b, _ = verify_independent(pts, N)
    return {
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "V": int(conflict_count(pts, N)),
        "size": len(pts),
        "hash": sha256_of_points(pts),
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_rem2_residual")
    os.makedirs(exp, exist_ok=True)
    src = os.path.join(RUN, "EXPERIMENTS", "LH3_forced_exchange", "seed504_points_v25.json")
    data = json.load(open(src, encoding="utf-8"))
    pts = [tuple(p) for p in data["points"]]
    wits = witnesses(pts)
    involved: Set[Point] = set()
    for a, b, c in wits:
        involved.add(a)
        involved.add(b)
        involved.add(c)
    core = sorted(p for p in pts if p not in involved)
    st = IncrementalIsoscelesFreeSet(N)
    for p in core:
        assert st.add_point(p)
    free = [(x, y) for x in range(N) for y in range(N) if (x, y) not in set(core)]
    need = TARGET - len(core)
    print(json.dumps({"core": len(core), "free": len(free), "need": need}), flush=True)

    # Lazy-constraint CP-SAT: pick need free points; forbid witness triples when found
    time_s = float(os.environ.get("W3_CHEAP_S", "600"))
    workers = int(os.environ.get("W3_WORKERS", "6"))
    t0 = time.time()
    cuts: Set[Tuple[Point, Point, Point]] = set()
    rounds = 0
    best_legal: List[Point] = []
    status = "TIMEOUT"
    while time.time() - t0 < time_s:
        rounds += 1
        model = cp_model.CpModel()
        z = {p: model.NewBoolVar(f"z{p[0]}_{p[1]}") for p in free}
        model.Add(sum(z.values()) == need)
        for trip in cuts:
            bools = []
            for p in trip:
                if p in z:
                    bools.append(z[p])
                elif p in set(core):
                    # core always on — cut becomes sum of free members <= len-1
                    pass
            # reconstruct: for triple involving core points, only free vars constrained
            free_in = [z[p] for p in trip if p in z]
            core_in = [p for p in trip if p in set(core)]
            if len(core_in) == 3:
                # impossible selection already; skip
                continue
            if len(free_in) == 0:
                continue
            # all three selected iff free_in all 1 (core already 1)
            model.Add(sum(free_in) <= len(free_in) - 1)
        solver = cp_model.CpSolver()
        rem = max(0.5, time_s - (time.time() - t0))
        solver.parameters.max_time_in_seconds = min(30.0, rem)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = 9200 + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            status = "INFEASIBLE_SCOPED"
            break
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT"
            break
        sel = list(core) + [p for p, v in z.items() if solver.Value(v) == 1]
        assert len(sel) == TARGET
        w = witnesses(sel)
        if not w:
            best_legal = sel
            status = "FEASIBLE_LEGAL"
            break
        # add cuts from witnesses
        before = len(cuts)
        for trip in w:
            cuts.add(tuple(sorted(trip)))
        if len(cuts) == before:
            # no new cuts — stuck
            status = "TIMEOUT"
            break
        if rounds % 50 == 0:
            print(
                json.dumps({"round": rounds, "cuts": len(cuts), "elapsed": time.time() - t0}),
                flush=True,
            )

    out = {
        "schema": "w3_rem2_core_extend_v1",
        "source": src,
        "core_size": len(core),
        "need": need,
        "status": status,
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_time_s": time.time() - t0,
        "size": len(best_legal),
        "dual": dual(best_legal) if best_legal else None,
    }
    path = os.path.join(exp, "core_extend_s504.json")
    json.dump(out, open(path, "w", encoding="utf-8"), indent=2)
    open(path, "a", encoding="utf-8").write("\n")
    if best_legal:
        cand = os.path.join(RUN, "CANDIDATES", "rem2_core_extend_s504_legal.json")
        json.dump({"points": [list(p) for p in best_legal], **out}, open(cand, "w"), indent=2)
        out["candidate"] = cand
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
