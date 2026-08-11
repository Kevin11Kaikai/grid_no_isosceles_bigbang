#!/usr/bin/env python3
"""LH-2: r=4 microproblems for easiest-16 pairs (joint_VC=4 necessary).

For each pair (q1,q2): take exact size-4 joint covers as Rem; test legality of
S0\\R ∪ {q1,q2}; then search 3 more adds from LB<=5 pool / halo for |S|=165.
"""
from __future__ import annotations

import gzip
import importlib.util
import itertools
import json
import os
import sys
import time
from typing import List, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]
N = 100
AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")
DETAIL = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_r4", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def edges_fs(rec):
    return [frozenset((tuple(e[0]), tuple(e[1]))) for e in rec["blocker_edges"]]


def size_k_covers(edges, k: int, limit: int = 80):
    involved = sorted({p for e in edges for p in e})
    if len(involved) < k:
        return []
    covers = []
    for comb in itertools.combinations(involved, k):
        C = set(comb)
        if all(e & C for e in edges):
            covers.append(sorted(comb))
            if len(covers) >= limit:
                break
    return covers


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


def find_three_adds(core: List[Point], forced: Sequence[Point], pool: List[Point], max_checks: int = 30000):
    """Require core ∪ forced legal, then search 3 adds from pool."""
    base = list(core) + list(forced)
    st0 = IncrementalIsoscelesFreeSet(N)
    for p in base:
        if not st0.add_point(p):
            return None, 0, "forced_not_legal"
    solo = []
    for p in pool:
        if p in st0.points:
            continue
        ok, _ = st0.can_add(p)
        if ok:
            solo.append(p)
    if len(solo) < 3:
        return None, 0, f"solo={len(solo)}"
    checked = 0
    # Prefer combinations among first 80 solo
    solo = solo[:100]
    for comb in itertools.combinations(solo, 3):
        checked += 1
        if checked > max_checks:
            return None, checked, "capped"
        st = IncrementalIsoscelesFreeSet(N)
        for p in base:
            st.add_point(p)
        ok_all = True
        for p in comb:
            ok, _ = st.can_add(p)
            if not ok:
                ok_all = False
                break
            st.add_point(p)
        if ok_all:
            pts = sorted(base + list(comb))
            d = dual(pts)
            if d["V"] == 0 and d["oracle_legal"] and d["independent_legal"]:
                return {
                    "added": [list(p) for p in comb],
                    "dual": d,
                    "points": [list(p) for p in pts],
                }, checked, "FEASIBLE_LEGAL"
    return None, checked, "exhausted"


def main():
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
    pool = sorted(
        {
            tuple(r["q"])
            for r in detail["all_qs_compact"]
            if int(r["lower_bound_min_deletions"]) <= 5
        }
        - s0_set
    )
    edge = {}
    for q in easy:
        edge[q] = edges_fs(ba.analyze_q(q, s0, maps, N))

    rows = []
    feasible = []
    # Sample pairs: all 120 is OK if covers small; cap cover checks
    for q1, q2 in itertools.combinations(easy, 2):
        edges = set(edge[q1]) | set(edge[q2])
        covers = size_k_covers(edges, 4, limit=40)
        pair_legal = 0
        found = None
        covers_checked = 0
        for rem in covers:
            covers_checked += 1
            rem_set = set(map(tuple, rem))
            core = [p for p in s0 if p not in rem_set]
            # pair legality
            st = IncrementalIsoscelesFreeSet(N)
            ok_core = True
            for p in core:
                if not st.add_point(p):
                    ok_core = False
                    break
            if not ok_core:
                continue
            ok1, _ = st.can_add(q1)
            if not ok1:
                continue
            st.add_point(q1)
            ok2, _ = st.can_add(q2)
            if not ok2:
                continue
            pair_legal += 1
            # search 3 adds excluding q1,q2
            add_pool = [p for p in pool if p not in (q1, q2)]
            # also halo around rem∪{q1,q2}
            for ax, ay in list(rem_set) + [q1, q2]:
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        x, y = ax + dx, ay + dy
                        if 0 <= x < N and 0 <= y < N:
                            p = (x, y)
                            if p not in s0_set and p not in (q1, q2):
                                add_pool.append(p)
            # uniq preserve
            seen = set()
            uniq_pool = []
            for p in add_pool:
                if p not in seen:
                    seen.add(p)
                    uniq_pool.append(p)
            hit, checked, status = find_three_adds(core, [q1, q2], uniq_pool, max_checks=8000)
            if hit:
                found = {
                    "rem": [list(p) for p in rem],
                    "q1": list(q1),
                    "q2": list(q2),
                    "triple_status": status,
                    "triple_checks": checked,
                    **hit,
                }
                feasible.append(found)
                break
        rows.append(
            {
                "q1": list(q1),
                "q2": list(q2),
                "n_covers_enum": len(covers),
                "covers_checked": covers_checked,
                "n_pair_legal": pair_legal,
                "found": found is not None,
            }
        )
        # early stop if we found one — still continue a bit for stats? keep going for full map but break inner
        # For budget: after 30 pairs if none, continue; full 120 OK if fast

    out = {
        "schema": "lh2_r4_easiest_pair_micro_v1",
        "n_pairs": len(rows),
        "n_pair_legal_any_cover": sum(1 for r in rows if r["n_pair_legal"] > 0),
        "n_feasible_165": len(feasible),
        "feasible": feasible,
        "rows": rows,
        "wall_s": time.time() - t0,
        "claim_discipline": "Scoped microproblems; promote only with dual+certificate.",
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH2_r4_pair_micro")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "r4_easiest_pair_micro.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    if feasible:
        with open(os.path.join(RUN, "CANDIDATES", "n100_k165_r4_pair.json"), "w", encoding="utf-8") as f:
            json.dump(feasible[0], f, indent=2)
    print(
        json.dumps(
            {
                "path": path,
                "n_pairs": out["n_pairs"],
                "n_pair_legal_any_cover": out["n_pair_legal_any_cover"],
                "n_feasible_165": out["n_feasible_165"],
                "wall_s": out["wall_s"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
