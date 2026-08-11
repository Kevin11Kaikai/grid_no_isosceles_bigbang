#!/usr/bin/env python3
"""LH-1: Extend blocker-pair necessary condition beyond easiest-16×easiest-16.

Scan pairs (q_easy, q_other) where q_other has exact/LB in {2,3,4} from Agent A
top list, looking for joint_VC <= 2 (r=2 necessary) or ==3 (r=3 necessary).
Also scan pairs among LB=3 cells.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
N = 100
AUDIT_SCRIPT = os.path.join(
    ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py"
)


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_mix", AUDIT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def edges_fs(rec) -> List[frozenset]:
    return [frozenset((tuple(e[0]), tuple(e[1]))) for e in rec["blocker_edges"]]


def exact_vc(edges):
    if not edges:
        return 0, [[]]
    involved = sorted({p for e in edges for p in e})
    n_inv = len(involved)
    limit = min(n_inv, 6)
    for k in range(0, limit + 1):
        covers = []
        for comb in itertools.combinations(involved, k):
            C = set(comb)
            if all(e & C for e in edges):
                covers.append(sorted(comb))
        if covers:
            return k, covers
    return None, []


def main():
    t0 = time.time()
    ba = load_ba()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    maps = ba.precompute_pivot_maps(s0)
    with open(
        os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_stats_n100.json"),
        encoding="utf-8",
    ) as f:
        stats = json.load(f)
    top = stats["easiest_to_insert_candidates"]["top_20_summary"]
    # Also pull more from top if available
    top_full = stats["easiest_to_insert_candidates"].get("top_200") or top
    if isinstance(top_full, dict):
        top_full = top

    # Build candidate qs: all with exact==2, and LB<=4 from top_20 + extend via re-analyze
    easy2 = []
    lb3 = []
    lb4 = []
    for row in top:
        q = tuple(row["q"])
        ex = row.get("exact_min_hitting_set")
        lb = row["lower_bound_min_deletions"]
        if ex == 2 or lb == 2:
            easy2.append(q)
        elif lb == 3 or ex == 3:
            lb3.append(q)
        elif lb == 4 or ex == 4:
            lb4.append(q)

    # Dedup preserve order
    def uniq(xs):
        seen = set()
        out = []
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    easy2, lb3, lb4 = uniq(easy2), uniq(lb3), uniq(lb4)

    # Analyze all needed
    need = uniq(easy2 + lb3 + lb4)
    recs = {}
    for q in need:
        recs[q] = ba.analyze_q(q, s0, maps, N)
        # refresh classification by exact/lb
    easy2 = [q for q in need if (recs[q]["exact_min_hitting_set"] or 99) == 2 or recs[q]["lower_bound_min_deletions"] == 2]
    # keep only exact 2 for easy2 purity
    easy2 = [q for q in need if recs[q]["exact_min_hitting_set"] == 2]
    lb3 = [q for q in need if recs[q]["lower_bound_min_deletions"] == 3]
    lb4 = [q for q in need if recs[q]["lower_bound_min_deletions"] == 4]

    edge = {q: edges_fs(recs[q]) for q in need}

    hist = defaultdict(int)
    promising = []  # joint_vc <= 3

    def consider(q1, q2, tag):
        edges = set(edge[q1]) | set(edge[q2])
        k, covers = exact_vc(edges)
        hist[str(k)] += 1
        if k is not None and k <= 3:
            promising.append(
                {
                    "tag": tag,
                    "q1": list(q1),
                    "q2": list(q2),
                    "joint_vc": k,
                    "n_edges": len(edges),
                    "n_covers": len(covers),
                    "exact1": recs[q1]["exact_min_hitting_set"],
                    "exact2": recs[q2]["exact_min_hitting_set"],
                    "lb1": recs[q1]["lower_bound_min_deletions"],
                    "lb2": recs[q2]["lower_bound_min_deletions"],
                }
            )

    for q1, q2 in itertools.combinations(easy2, 2):
        consider(q1, q2, "easy2_x_easy2")
    for q1 in easy2:
        for q2 in lb3:
            consider(q1, q2, "easy2_x_lb3")
    for q1 in easy2:
        for q2 in lb4:
            consider(q1, q2, "easy2_x_lb4")
    for q1, q2 in itertools.combinations(lb3, 2):
        consider(q1, q2, "lb3_x_lb3")

    out = {
        "schema": "lh1_mixed_pair_vc_v1",
        "n_easy2": len(easy2),
        "n_lb3": len(lb3),
        "n_lb4": len(lb4),
        "joint_vc_histogram_all_scanned_pairs": dict(hist),
        "n_promising_joint_vc_le_3": len(promising),
        "n_promising_joint_vc_le_2": sum(1 for p in promising if p["joint_vc"] <= 2),
        "promising": promising,
        "baseline_hash": sha256_of_points(s0),
        "wall_time_s": time.time() - t0,
        "interpretation": (
            "joint_vc>2 kills co-insertion of that pair at Hamming r=2; "
            "joint_vc==3 is necessary-ok only for r>=3; "
            "easy2×easy2 previously all 4."
        ),
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH1_blocker_pair")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "mixed_pair_vc_scan.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "path": path,
                "counts": {
                    "easy2": len(easy2),
                    "lb3": len(lb3),
                    "lb4": len(lb4),
                },
                "hist": dict(hist),
                "promising_le3": len(promising),
                "promising_le2": out["n_promising_joint_vc_le_2"],
                "wall_s": out["wall_time_s"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
