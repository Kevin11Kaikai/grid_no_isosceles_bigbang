#!/usr/bin/env python3
"""LH-3: Seed |S|=165 states from size-4 joint covers (pair-legal) + 3 adds; minimize V.

Uses IncrementalIsoscelesFreeSet greedy refill then CP-SAT residual refill on
witness-involved points (learned from LH-1). Forces leave-S0 exchange.
"""
from __future__ import annotations

import gzip
import importlib.util
import itertools
import json
import os
import random
import sys
import time
from collections import defaultdict
from typing import List, Sequence, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")
DETAIL = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")
N = 100


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_cs", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def dual(pts):
    ok_a, _ = is_legal_pivot_method(pts, N)
    ok_b, _ = verify_independent(pts, N)
    return {
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "V": int(conflict_count(pts, N)),
        "size": len(pts),
    }


def witnesses_involved(points):
    pts = [tuple(p) for p in points]
    inv = set()

    def sq(a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

    for pivot in pts:
        groups = defaultdict(list)
        for q in pts:
            if q == pivot:
                continue
            groups[sq(pivot, q)].append(q)
        for members in groups.values():
            if len(members) >= 2:
                inv.add(pivot)
                inv.add(members[0])
                inv.add(members[1])
    return sorted(inv)


def cpsat_refill(core, pool, need, time_limit_s=60.0):
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    addv = [model.NewBoolVar(f"a{i}") for i in range(len(pool))]
    model.Add(sum(addv) == need)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = max(1, (os.cpu_count() or 4) // 4)
    cuts = 0
    best_v = 10**9
    best_pts = None
    t0 = time.time()
    status = "UNKNOWN"
    while time.time() - t0 < time_limit_s:
        solver.parameters.max_time_in_seconds = max(1.0, time_limit_s - (time.time() - t0))
        res = solver.Solve(model)
        if res == cp_model.INFEASIBLE:
            status = "INFEASIBLE_SCOPED"
            break
        if res not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT_INCONCLUSIVE"
            break
        added = [pool[i] for i, v in enumerate(addv) if solver.Value(v) == 1]
        cand = sorted(core + added)
        v = conflict_count(cand, N)
        if v < best_v:
            best_v = v
            best_pts = cand
        if v == 0:
            d = dual(cand)
            if d["oracle_legal"] and d["independent_legal"]:
                return {"status": "FEASIBLE_LEGAL", "dual": d, "points": [list(p) for p in cand], "cuts": cuts}
        # cut
        pts = [tuple(p) for p in cand]
        core_set = set(core)
        idx = {p: i for i, p in enumerate(pool)}

        def sq(a, b):
            return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

        cut_added = False
        for pivot in pts:
            groups = defaultdict(list)
            for q in pts:
                if q == pivot:
                    continue
                groups[sq(pivot, q)].append(q)
            for members in groups.values():
                if len(members) < 2:
                    continue
                lits = []
                for p in (pivot, members[0], members[1]):
                    if p in core_set:
                        continue
                    if p in idx:
                        lits.append(addv[idx[p]])
                if not lits:
                    continue
                model.AddBoolOr([lit.Not() for lit in lits])
                cuts += 1
                cut_added = True
                break
            if cut_added:
                break
        if not cut_added:
            status = "ERROR_NO_CUT"
            break
    else:
        status = "TIMEOUT_INCONCLUSIVE"
    return {
        "status": status,
        "best_V": best_v if best_v < 10**9 else None,
        "cuts": cuts,
        "points": [list(p) for p in best_pts] if best_pts else None,
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    t0 = time.time()
    ba = load_ba()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    maps = ba.precompute_pivot_maps(s0)
    with gzip.open(DETAIL, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    easy = [
        tuple(r["q"])
        for r in detail["all_qs_compact"]
        if r.get("exact_min_hitting_set") == 2
    ]
    edge = {
        q: [frozenset((tuple(e[0]), tuple(e[1]))) for e in ba.analyze_q(q, s0, maps, N)["blocker_edges"]]
        for q in easy
    }
    pool_lb5 = sorted(
        {
            tuple(r["q"])
            for r in detail["all_qs_compact"]
            if int(r["lower_bound_min_deletions"]) <= 5
        }
        - s0_set
    )
    rng = random.Random(7)
    pairs = list(itertools.combinations(easy, 2))
    rng.shuffle(pairs)
    results = []
    best_global = 10**9
    for q1, q2 in pairs[:24]:  # sample 24 pairs
        edges = set(edge[q1]) | set(edge[q2])
        involved = sorted({p for e in edges for p in e})
        covers = []
        for comb in itertools.combinations(involved, 4):
            C = set(comb)
            if all(e & C for e in edges):
                covers.append(sorted(comb))
                if len(covers) >= 3:
                    break
        for rem in covers[:2]:
            rem_set = set(map(tuple, rem))
            core = [p for p in s0 if p not in rem_set]
            st = IncrementalIsoscelesFreeSet(N)
            ok = True
            for p in core:
                if not st.add_point(p):
                    ok = False
                    break
            if not ok:
                continue
            ok1, _ = st.can_add(q1)
            ok2 = False
            if ok1:
                st.add_point(q1)
                ok2, _ = st.can_add(q2)
            if not (ok1 and ok2):
                continue
            st.add_point(q2)
            # greedy add 3 more
            added = [q1, q2]
            for p in pool_lb5 + [
                (x, y)
                for x in range(N)
                for y in range(N)
                if (x, y) not in s0_set and (x, y) not in (q1, q2)
            ][:2000]:
                if len(added) >= 5:  # q1,q2 + 3
                    break
                if p in (q1, q2) or p in rem_set:
                    continue
                okp, _ = st.can_add(p)
                if okp:
                    st.add_point(p)
                    added.append(p)
            # force fill if short
            if len(added) < 5:
                for p in pool_lb5:
                    if len(added) >= 5:
                        break
                    if p not in set(added) and p not in rem_set:
                        added.append(p)
            pts = core + added[:5]
            if len(pts) != 165:
                continue
            v0 = conflict_count(pts, N)
            # residual CP-SAT on involved witnesses
            inv = witnesses_involved(pts)
            if not inv:
                d = dual(pts)
                row = {"q1": list(q1), "q2": list(q2), "rem": [list(p) for p in rem], "V": v0, "status": "ALREADY_LEGAL" if v0 == 0 else "NO_WITNESS_BUG", "dual": d}
                results.append(row)
                continue
            fixed = [p for p in pts if p not in set(inv)]
            need = 165 - len(fixed)
            # pool = inv ∪ halo
            pset = set(inv)
            for x, y in inv:
                for dx in range(-4, 5):
                    for dy in range(-4, 5):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in set(fixed):
                            pset.add((nx, ny))
            refill = cpsat_refill(fixed, sorted(pset), need, time_limit_s=45.0)
            row = {
                "q1": list(q1),
                "q2": list(q2),
                "rem": [list(p) for p in rem],
                "V_seed": v0,
                "n_involved": len(inv),
                "refill": {k: refill[k] for k in refill if k != "points"},
            }
            if refill.get("status") == "FEASIBLE_LEGAL":
                row["status"] = "FEASIBLE_LEGAL"
                row["dual"] = refill["dual"]
                row["points"] = refill["points"]
                best_global = 0
            else:
                bv = refill.get("best_V")
                if bv is not None:
                    best_global = min(best_global, bv, v0)
                row["status"] = refill.get("status")
                row["best_V"] = min([v for v in [bv, v0] if v is not None], default=v0)
            results.append(row)
            print(json.dumps({k: row[k] for k in row if k not in ("points", "dual")}, indent=2), flush=True)
            if best_global == 0:
                break
        if best_global == 0:
            break

    out = {
        "schema": "lh3_cert_seeded_minv_v1",
        "n_trials": len(results),
        "n_legal": sum(1 for r in results if r.get("status") == "FEASIBLE_LEGAL"),
        "best_V_seen": 0 if best_global == 0 else (best_global if best_global < 10**9 else None),
        "results": results,
        "wall_s": time.time() - t0,
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH3_cert_seeded")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "cert_seeded_minv.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    if out["n_legal"]:
        for r in results:
            if r.get("status") == "FEASIBLE_LEGAL":
                with open(os.path.join(RUN, "CANDIDATES", "n100_k165_cert_seeded.json"), "w", encoding="utf-8") as f:
                    json.dump(r, f, indent=2)
                break
    print(json.dumps({"path": path, "n_trials": out["n_trials"], "n_legal": out["n_legal"], "best_V_seen": out["best_V_seen"], "wall_s": out["wall_s"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
