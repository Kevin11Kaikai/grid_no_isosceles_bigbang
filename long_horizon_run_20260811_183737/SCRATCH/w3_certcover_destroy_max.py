#!/usr/bin/env python3
"""Exact microproblem: delete a min hitting-set of an easiest q, then maximize
over ALL individually-addable cells (not score-restricted Hamming Add).

Why this is new vs FAILED routes:
- Wave2 / LH2 Hamming used tiny Add pools (U_small, LBle3).
- Family K deleted *random* S0 points, not certificate covers of exact-min qs.
- Frozen-core rem-k CAPACITY_FAIL does not speak to the two n64 exact-deletion-1
  cells or the 16 n100 exact-deletion-2 cells.

If this experiment succeeds: legal +1 (dual-verify before promote).
If it fails with CAPACITY_FAIL: that exact cover does not open enough addables
for net +1 (scoped; other covers / multi-q still open).
If TIMEOUT: escalate that cover only.

Requires `.venv_solver` (ortools).
"""
from __future__ import annotations

import gzip
import importlib.util
import itertools
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
from data.baselines.official_raw import SOL_64, SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import (  # noqa: E402
    verify_independent,
)

Point = Tuple[int, int]
AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")

EXP = os.path.join(RUN, "EXPERIMENTS", "W3_certcover_max")
os.makedirs(EXP, exist_ok=True)


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_cc", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def sq(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def dual(pts: Sequence[Point], n: int) -> dict:
    oka, _ = is_legal_pivot_method(pts, n)
    okb, _ = verify_independent(pts, n)
    return {
        "oracle": bool(oka),
        "indep": bool(okb),
        "size": len(pts),
        "hash": sha256_of_points(pts),
    }


def witnesses(points: Sequence[Point]):
    out = []
    for pivot in points:
        g: Dict[int, List[Point]] = defaultdict(list)
        for q in points:
            if q != pivot:
                g[sq(pivot, q)].append(q)
        for _d, m in g.items():
            if len(m) < 2:
                continue
            for i in range(len(m)):
                for j in range(i + 1, len(m)):
                    out.append((pivot, m[i], m[j]))
    return out


def hitting_sets(edges: List[frozenset], k: int) -> List[Tuple[Point, ...]]:
    verts = sorted({p for e in edges for p in e})
    out = []
    for comb in itertools.combinations(verts, k):
        s = set(comb)
        if all(s & e for e in edges):
            out.append(tuple(sorted(s)))
    return out


def addable_pool(n: int, core: Sequence[Point]) -> List[Point]:
    st = IncrementalIsoscelesFreeSet(n)
    for p in core:
        if not st.add_point(p):
            raise RuntimeError(f"illegal core at {p}")
    free = []
    core_set = set(core)
    for x in range(n):
        for y in range(n):
            p = (x, y)
            if p in core_set:
                continue
            if st.can_add(p)[0]:
                free.append(p)
    return free


def maximize_from_core(
    n: int,
    core: List[Point],
    target: int,
    time_s: float,
    workers: int,
    seed: int,
) -> dict:
    free = addable_pool(n, core)
    cap = len(core) + len(free)
    if cap < target:
        return {
            "status": "CAPACITY_FAIL",
            "core": len(core),
            "free": len(free),
            "best_legal_size": len(core),
            "proved_max": cap,
            "cap": cap,
        }

    cuts: Set[Tuple[Point, Point, Point]] = set()
    t0 = time.time()
    rounds = 0
    best_size = len(core)
    best_pts = list(core)
    lb_extra = target - len(core)
    # First try feasibility at target, then maximize if time remains.
    status = "TIMEOUT"
    proved_max = None
    found_target = False

    def solve_round(feas_extra: int | None, round_lim: float) -> str:
        nonlocal best_size, best_pts, found_target
        model = cp_model.CpModel()
        z = {p: model.NewBoolVar(f"z{p[0]}_{p[1]}") for p in free}
        if feas_extra is not None:
            model.Add(sum(z.values()) >= feas_extra)
        else:
            model.Maximize(sum(z.values()))
        for trip in cuts:
            free_in = [z[p] for p in trip if p in z]
            if free_in:
                model.Add(sum(free_in) <= len(free_in) - 1)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max(0.5, round_lim)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = seed + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            return "INFEAS"
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return "UNKNOWN"
        sel = list(core) + [p for p, v in z.items() if solver.Value(v) == 1]
        w = witnesses(sel)
        if not w:
            if len(sel) > best_size:
                best_size = len(sel)
                best_pts = sel
            if best_size >= target:
                found_target = True
            return "LEGAL"
        for trip in w:
            cuts.add(tuple(sorted(trip)))
        return "CUT"

    while time.time() - t0 < time_s:
        rounds += 1
        rem = time_s - (time.time() - t0)
        if not found_target:
            r = solve_round(lb_extra, min(25.0, rem))
        else:
            r = solve_round(None, min(25.0, rem))
        if r == "INFEAS":
            if not found_target and lb_extra == target - len(core):
                status = "SCOPED_INFEAS_TARGET"
                proved_max = target - 1
            else:
                status = "MAX_PROVED"
                proved_max = best_size
            break
        if r == "LEGAL" and found_target:
            status = "FEASIBLE_TARGET"
            # keep maximizing a bit if time left
            if time.time() - t0 > time_s - 8:
                break
            lb_extra = best_size - len(core) + 1
            continue
        if r == "UNKNOWN" and time.time() - t0 >= time_s - 2:
            status = "TIMEOUT"
            break

    out = {
        "status": status,
        "core": len(core),
        "free": len(free),
        "cap": cap,
        "best_legal_size": best_size,
        "proved_max": proved_max,
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_s": time.time() - t0,
    }
    if best_size > len(core) or found_target:
        out["dual"] = dual(best_pts, n)
        out["best_hash"] = out["dual"]["hash"]
        if found_target and out["dual"]["oracle"] and out["dual"]["indep"]:
            out["points"] = [list(p) for p in sorted(best_pts)]
            out["status"] = "FEASIBLE_TARGET"
    return out


def easiest_qs(n: int, detail_path: str, exact_k: int) -> List[Point]:
    with gzip.open(detail_path, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    easy = []
    for r in detail["all_qs_compact"]:
        ex = r.get("exact_min_hitting_set")
        lb = r.get("lower_bound_min_deletions")
        ub = r.get("upper_bound_min_deletions")
        if ex == exact_k or (lb == exact_k and ub == exact_k):
            easy.append(tuple(r["q"]))
    return easy


def run_grid(n: int, sol, exact_k: int, target: int, time_s: float, workers: int, max_solves: int) -> dict:
    ba = load_ba()
    s0 = sorted((int(x), int(y)) for x, y in sol)
    maps = ba.precompute_pivot_maps(s0)
    detail = os.path.join(
        ROOT, "scratch", "audit", "agent_a", f"blocker_detail_n{n}.json.gz"
    )
    easy = easiest_qs(n, detail, exact_k)
    if n == 64:
        for q in [(62, 2), (62, 61)]:
            if q not in easy:
                easy.append(q)
    rows = []
    capacity_only = []
    t0 = time.time()
    for qi, q in enumerate(easy):
        rec = ba.analyze_q(q, s0, maps, n)
        edges = [frozenset((tuple(e[0]), tuple(e[1]))) for e in rec["blocker_edges"]]
        k = rec["exact_min_hitting_set"]
        if k is None:
            k = exact_k
        covers = hitting_sets(edges, int(k))
        for ci, cov in enumerate(covers):
            core = sorted(set(s0) - set(cov))
            free = addable_pool(n, core)
            cap = len(core) + len(free)
            cap_row = {
                "q": list(q),
                "cover": [list(p) for p in cov],
                "k": int(k),
                "core": len(core),
                "free": len(free),
                "cap": cap,
                "q_in_free": list(q) in [list(p) for p in free] or q in free,
            }
            capacity_only.append(cap_row)
            print(json.dumps({"cap": cap_row}), flush=True)
    cap_path = os.path.join(EXP, f"capacity_n{n}.json")
    with open(cap_path, "w", encoding="utf-8") as f:
        json.dump({"n": n, "exact_k": exact_k, "rows": capacity_only}, f, indent=2)
        f.write("\n")

    survivors = [r for r in capacity_only if r["cap"] >= target]
    survivors.sort(key=lambda r: -r["cap"])
    print(
        json.dumps(
            {
                "n": n,
                "n_easy": len(easy),
                "n_covers": len(capacity_only),
                "n_cap_ge_target": len(survivors),
                "max_cap": max((r["cap"] for r in capacity_only), default=0),
            }
        ),
        flush=True,
    )

    solves = 0
    for r in survivors:
        if solves >= max_solves:
            break
        cov = tuple(tuple(p) for p in r["cover"])
        core = sorted(set(s0) - set(cov))
        print(json.dumps({"solve": r, "idx": solves}), flush=True)
        res = maximize_from_core(n, core, target, time_s, workers, seed=2100 + solves)
        row = {**res, "q": r["q"], "cover": r["cover"], "k": r["k"]}
        rows.append(row)
        print(json.dumps({k: v for k, v in row.items() if k != "points"}, indent=2), flush=True)
        solves += 1
        if res.get("status") == "FEASIBLE_TARGET" and res.get("points"):
            cand = os.path.join(
                RUN,
                "CANDIDATES",
                f"certcover_n{n}_q{r['q'][0]}_{r['q'][1]}_k{len(res['points'])}.json",
            )
            os.makedirs(os.path.dirname(cand), exist_ok=True)
            with open(cand, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=2)
                f.write("\n")
            break

    # Joint two-q covers (n64 both exact-1; n100 sample of easiest 8 pairs)
    joint_rows = []
    if len(easy) >= 2:
        pair_iter = list(itertools.combinations(easy[: min(8, len(easy))], 2))
        for q1, q2 in pair_iter[:12]:
            rec1 = ba.analyze_q(q1, s0, maps, n)
            rec2 = ba.analyze_q(q2, s0, maps, n)
            e1 = [frozenset((tuple(a), tuple(b))) for a, b in rec1["blocker_edges"]]
            e2 = [frozenset((tuple(a), tuple(b))) for a, b in rec2["blocker_edges"]]
            union_edges = e1 + [e for e in e2 if e not in e1]
            verts = sorted({p for e in union_edges for p in e})
            joint_k = None
            joint_cov = None
            for kk in range(1, min(6, len(verts) + 1)):
                hs = hitting_sets(union_edges, kk)
                if hs:
                    joint_k = kk
                    joint_cov = hs[0]
                    break
            if joint_cov is None:
                continue
            core = sorted(set(s0) - set(joint_cov))
            free = addable_pool(n, core)
            cap = len(core) + len(free)
            jrow = {
                "q1": list(q1),
                "q2": list(q2),
                "joint_k": joint_k,
                "cover": [list(p) for p in joint_cov],
                "core": len(core),
                "free": len(free),
                "cap": cap,
                "both_in_free": (q1 in free and q2 in free),
            }
            joint_rows.append(jrow)
            print(json.dumps({"joint_cap": jrow}), flush=True)
            if cap >= target and solves < max_solves:
                res = maximize_from_core(
                    n, core, target, time_s, workers, seed=3100 + solves
                )
                row = {**res, **jrow, "kind": "joint"}
                rows.append(row)
                solves += 1
                print(
                    json.dumps({k: v for k, v in row.items() if k != "points"}, indent=2),
                    flush=True,
                )
                if res.get("status") == "FEASIBLE_TARGET" and res.get("points"):
                    cand = os.path.join(
                        RUN,
                        "CANDIDATES",
                        f"certcover_joint_n{n}_k{len(res['points'])}.json",
                    )
                    with open(cand, "w", encoding="utf-8") as f:
                        json.dump(res, f, indent=2)
                        f.write("\n")
                    break

    summary = {
        "schema": "w3_certcover_max_v1",
        "n": n,
        "target": target,
        "exact_k": exact_k,
        "n_easy": len(easy),
        "capacity": capacity_only,
        "n_cap_ge_target": sum(1 for r in capacity_only if r["cap"] >= target),
        "max_cap": max((r["cap"] for r in capacity_only), default=0),
        "joint": joint_rows,
        "solves": rows,
        "any_plus": any(
            (r.get("best_legal_size") or 0) >= target for r in rows
        ),
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else max(
            (r["core"] for r in capacity_only), default=0
        ),
        "wall_s": time.time() - t0,
    }
    path = os.path.join(EXP, f"summary_n{n}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    return summary


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    workers = int(os.environ.get("W3_WORKERS", "4"))
    # Cheap-kill first: n64 exact-1 (tiny), then n100 exact-2.
    s64 = run_grid(64, SOL_64, 1, 113, time_s=90.0, workers=workers, max_solves=8)
    print(json.dumps({"done_n64": True, "any_plus": s64["any_plus"], "max_cap": s64["max_cap"], "best": s64["best"]}), flush=True)
    s100 = run_grid(100, SOL_100, 2, 165, time_s=90.0, workers=workers, max_solves=10)
    print(json.dumps({"done_n100": True, "any_plus": s100["any_plus"], "max_cap": s100["max_cap"], "best": s100["best"]}), flush=True)
    merged = {
        "schema": "w3_certcover_max_merged_v1",
        "n64": {k: s64[k] for k in s64 if k not in ("capacity", "solves", "joint")},
        "n100": {k: s100[k] for k in s100 if k not in ("capacity", "solves", "joint")},
        "any_plus": bool(s64["any_plus"] or s100["any_plus"]),
    }
    path = os.path.join(EXP, "summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    print(json.dumps(merged, indent=2), flush=True)


if __name__ == "__main__":
    main()
