#!/usr/bin/env python3
"""Compound repair: min-cover of easiest q plus ONE extra S0 deletion.

Prior W3_certcover_max: every n100 exact-2 cover has free=3, cap=165, and
CP-SAT proves target 165 INFEASIBLE (new-new / new-old conflicts among the
3 addables). n64 exact-1: free=2, cap=113, target INFEASIBLE.

Hypothesis: the leftover conflicts are concentrated on a few remaining S0
vertices; deleting one such vertex expands the addable pool or makes the
existing addables compatible, enabling net +1 (r=3 on n100, r=2 on n64).

If success: dual-verify then certificate.
If all extras CAPACITY_FAIL or SCOPED_INFEAS: this compound family is dead
for easiest-q covers (does not kill larger Rem or other qs).
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
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]
AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")
EXP = os.path.join(RUN, "EXPERIMENTS", "W3_cover_plus1")
os.makedirs(EXP, exist_ok=True)


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_p1", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def sq(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def dual(pts, n):
    oka, _ = is_legal_pivot_method(pts, n)
    okb, _ = verify_independent(pts, n)
    return {"oracle": bool(oka), "indep": bool(okb), "size": len(pts), "hash": sha256_of_points(pts)}


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


def hitting_sets(edges, k):
    verts = sorted({p for e in edges for p in e})
    out = []
    for comb in itertools.combinations(verts, k):
        s = set(comb)
        if all(s & e for e in edges):
            out.append(tuple(sorted(s)))
    return out


def addable_pool(n, core):
    st = IncrementalIsoscelesFreeSet(n)
    for p in core:
        assert st.add_point(p)
    core_set = set(core)
    free = []
    for x in range(n):
        for y in range(n):
            p = (x, y)
            if p in core_set:
                continue
            if st.can_add(p)[0]:
                free.append(p)
    return free


def conflict_core_verts(core: Sequence[Point], free: Sequence[Point]) -> Set[Point]:
    """S0/core points that appear in some illegal triple involving >=1 free point."""
    core_set = set(core)
    verts: Set[Point] = set()
    # all subsets of free of size 1..len(free) plus core
    for r in range(1, len(free) + 1):
        for sub in itertools.combinations(free, r):
            pts = list(core) + list(sub)
            for trip in witnesses(pts):
                if any(p in sub for p in trip):
                    for p in trip:
                        if p in core_set:
                            verts.add(p)
    return verts


def exact_target(n, core, free, target, time_s=15.0, workers=4, seed=1):
    cap = len(core) + len(free)
    if cap < target:
        return {
            "status": "CAPACITY_FAIL",
            "core": len(core),
            "free": len(free),
            "cap": cap,
            "best_legal_size": len(core),
            "proved_max": cap,
        }
    cuts = set()
    t0 = time.time()
    best = list(core)
    best_size = len(core)
    need = target - len(core)
    status = "TIMEOUT"
    rounds = 0
    while time.time() - t0 < time_s:
        rounds += 1
        model = cp_model.CpModel()
        z = {p: model.NewBoolVar(f"z{p[0]}_{p[1]}") for p in free}
        model.Add(sum(z.values()) >= need)
        for trip in cuts:
            fi = [z[p] for p in trip if p in z]
            if fi:
                model.Add(sum(fi) <= len(fi) - 1)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = min(8.0, max(0.4, time_s - (time.time() - t0)))
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = seed + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            return {
                "status": "SCOPED_INFEAS_TARGET",
                "core": len(core),
                "free": len(free),
                "cap": cap,
                "best_legal_size": best_size,
                "proved_max": target - 1,
                "rounds": rounds,
                "final_cuts": len(cuts),
                "wall_s": time.time() - t0,
            }
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT"
            break
        sel = list(core) + [p for p, v in z.items() if solver.Value(v) == 1]
        w = witnesses(sel)
        if not w:
            d = dual(sel, n)
            out = {
                "status": "FEASIBLE_TARGET",
                "core": len(core),
                "free": len(free),
                "cap": cap,
                "best_legal_size": len(sel),
                "rounds": rounds,
                "final_cuts": len(cuts),
                "wall_s": time.time() - t0,
                "dual": d,
            }
            if d["oracle"] and d["indep"]:
                out["points"] = [list(p) for p in sorted(sel)]
            return out
        for trip in w:
            cuts.add(tuple(sorted(trip)))
    return {
        "status": status,
        "core": len(core),
        "free": len(free),
        "cap": cap,
        "best_legal_size": best_size,
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_s": time.time() - t0,
    }


def easiest(n, exact_k, ba, s0):
    path = os.path.join(ROOT, "scratch", "audit", "agent_a", f"blocker_detail_n{n}.json.gz")
    with gzip.open(path, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    easy = []
    for r in detail["all_qs_compact"]:
        ex = r.get("exact_min_hitting_set")
        lb = r.get("lower_bound_min_deletions")
        ub = r.get("upper_bound_min_deletions")
        if ex == exact_k or (lb == exact_k and ub == exact_k):
            easy.append(tuple(r["q"]))
    if n == 64:
        for q in [(62, 2), (62, 61)]:
            if q not in easy:
                easy.append(q)
    maps = ba.precompute_pivot_maps(s0)
    covers = []
    for q in easy:
        rec = ba.analyze_q(q, s0, maps, n)
        edges = [frozenset((tuple(e[0]), tuple(e[1]))) for e in rec["blocker_edges"]]
        k = rec["exact_min_hitting_set"] or exact_k
        for cov in hitting_sets(edges, int(k)):
            covers.append({"q": q, "cover": cov, "k": int(k)})
    return covers


def run_grid(n, sol, exact_k, target, workers):
    ba = load_ba()
    s0 = sorted((int(x), int(y)) for x, y in sol)
    s0_set = set(s0)
    covers = easiest(n, exact_k, ba, s0)
    rows = []
    t0 = time.time()
    n_feas = 0
    n_tried_extras = 0
    for ci, item in enumerate(covers):
        cov = item["cover"]
        q = item["q"]
        core = sorted(s0_set - set(cov))
        free = addable_pool(n, core)
        extras = conflict_core_verts(core, free)
        # Also try the 8 S0 points closest to q (geometric, distinct from cover)
        extras_geo = sorted(
            [p for p in s0 if p not in cov],
            key=lambda p: (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2,
        )[:8]
        extra_list = sorted(set(extras) | set(extras_geo))
        best_cap = len(core) + len(free)
        best_status = "no_extra"
        local = []
        for e in extra_list:
            n_tried_extras += 1
            core2 = sorted(s0_set - set(cov) - {e})
            free2 = addable_pool(n, core2)
            cap2 = len(core2) + len(free2)
            rec = {
                "extra": list(e),
                "core": len(core2),
                "free": len(free2),
                "cap": cap2,
                "source": "conflict" if e in extras else "geo",
            }
            if cap2 >= target:
                res = exact_target(n, core2, free2, target, time_s=12.0, workers=workers, seed=4000 + ci)
                rec.update({k: v for k, v in res.items() if k != "points"})
                if res.get("status") == "FEASIBLE_TARGET" and res.get("points"):
                    rec["points"] = res["points"]
                    n_feas += 1
                    cand = os.path.join(
                        RUN, "CANDIDATES", f"cover_plus1_n{n}_{len(res['points'])}.json"
                    )
                    with open(cand, "w", encoding="utf-8") as f:
                        json.dump(res, f, indent=2)
                        f.write("\n")
            else:
                rec["status"] = "CAPACITY_FAIL"
                rec["proved_max"] = cap2
            local.append(rec)
            best_cap = max(best_cap, cap2)
            if rec.get("status") == "FEASIBLE_TARGET":
                best_status = "FEASIBLE_TARGET"
                break
        row = {
            "q": list(q),
            "cover": [list(p) for p in cov],
            "base_free": len(free),
            "n_conflict_extras": len(extras),
            "n_tried": len(extra_list),
            "best_cap": best_cap,
            "any_feas": any(r.get("status") == "FEASIBLE_TARGET" for r in local),
            "n_cap_ge_target": sum(1 for r in local if r["cap"] >= target),
            "n_infeas": sum(1 for r in local if r.get("status") == "SCOPED_INFEAS_TARGET"),
            "n_capfail": sum(1 for r in local if r.get("status") == "CAPACITY_FAIL"),
            "extras": local,
        }
        rows.append(row)
        print(
            json.dumps({k: v for k, v in row.items() if k != "extras"}),
            flush=True,
        )
        if row["any_feas"]:
            break

    summary = {
        "schema": "w3_cover_plus1_v1",
        "n": n,
        "target": target,
        "n_covers": len(covers),
        "n_tried_extras": n_tried_extras,
        "any_plus": any(r["any_feas"] for r in rows),
        "max_best_cap": max((r["best_cap"] for r in rows), default=0),
        "rows": rows,
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
    s64 = run_grid(64, SOL_64, 1, 113, workers)
    print(json.dumps({"done_n64": True, "any_plus": s64["any_plus"], "max_best_cap": s64["max_best_cap"]}), flush=True)
    s100 = run_grid(100, SOL_100, 2, 165, workers)
    print(json.dumps({"done_n100": True, "any_plus": s100["any_plus"], "max_best_cap": s100["max_best_cap"]}), flush=True)
    merged = {
        "n64_any_plus": s64["any_plus"],
        "n100_any_plus": s100["any_plus"],
        "n64_max_cap": s64["max_best_cap"],
        "n100_max_cap": s100["max_best_cap"],
    }
    with open(os.path.join(EXP, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    print(json.dumps(merged, indent=2), flush=True)


if __name__ == "__main__":
    main()
