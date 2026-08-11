#!/usr/bin/env python3
"""LH-1: Search for complementary insertion pairs with low joint VC.

Thesis: easiest-16 pairs all have joint_VC=4 (anti-complementary).
Look among a broader sample of low-LB unselected cells for pairs with
joint_VC <= 2 (r=2 necessary) or ==3 (r=3).

Uses Agent A analyze_q on sampled qs; does not claim global results.
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
from typing import Dict, List, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
N = 100
AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_comp", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def edges_fs(rec):
    return [frozenset((tuple(e[0]), tuple(e[1]))) for e in rec["blocker_edges"]]


def exact_vc(edges, max_k=5):
    if not edges:
        return 0
    involved = sorted({p for e in edges for p in e})
    for k in range(0, min(max_k, len(involved)) + 1):
        for comb in itertools.combinations(involved, k):
            C = set(comb)
            if all(e & C for e in edges):
                return k
    return None


def load_top_qs(ba, s0, maps) -> List[Tuple[Point, dict]]:
    """Prefer gzip full top-200 if present; else compute LB<=5 sample via scanning frame."""
    gz = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_edges_top200_n100.json.gz")
    # alternate names
    candidates = [
        gz,
        os.path.join(ROOT, "scratch", "audit", "agent_a", "easiest_top200_n100.json.gz"),
    ]
    for path in candidates:
        if os.path.exists(path):
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
            # flexible schema
            rows = data if isinstance(data, list) else data.get("records") or data.get("top")
            out = []
            for r in rows:
                q = tuple(r["q"] if "q" in r else r["point"])
                out.append((q, r))
            return out

    # Compute: sample unselected with small involved by analyzing ring-ish cells
    # Use multi_spatial list + synthetic grid sample of boundary/mid
    with open(
        os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_stats_n100.json"),
        encoding="utf-8",
    ) as f:
        stats = json.load(f)
    qs = []
    for row in stats["easiest_to_insert_candidates"]["top_20_summary"]:
        qs.append(tuple(row["q"]))
    for row in stats["easiest_to_insert_candidates"]["multi_spatial_community_among_easiest"]:
        qs.append(tuple(row["q"]))

    s0_set = set(s0)
    # stratified sample: all cells with ring_depth in {0,1,2,3,18,19,24,25,26} subset
    rng = random.Random(42)
    sample_pool = []
    for x in range(N):
        for y in range(N):
            p = (x, y)
            if p in s0_set:
                continue
            rd = min(x, y, N - 1 - x, N - 1 - y)
            if rd <= 3 or rd in (17, 18, 19, 24, 25, 26):
                sample_pool.append(p)
    rng.shuffle(sample_pool)
    for p in sample_pool[:400]:
        qs.append(p)
    # unique
    seen = set()
    uniq = []
    for q in qs:
        if q not in seen:
            seen.add(q)
            uniq.append(q)

    analyzed = []
    for q in uniq:
        rec = ba.analyze_q(q, s0, maps, N)
        lb = rec["lower_bound_min_deletions"]
        if lb <= 6:
            analyzed.append((q, rec))
    analyzed.sort(
        key=lambda t: (
            t[1]["lower_bound_min_deletions"],
            t[1]["blocker_edge_count"],
            t[0],
        )
    )
    return analyzed[:120]


def main():
    t0 = time.time()
    ba = load_ba()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    maps = ba.precompute_pivot_maps(s0)
    rows = load_top_qs(ba, s0, maps)
    # ensure recs have blocker_edges
    recs: Dict[Point, dict] = {}
    for q, r in rows:
        if "blocker_edges" in r and r.get("_ready"):
            recs[q] = r
        else:
            recs[q] = ba.analyze_q(q, s0, maps, N)

    qs = list(recs.keys())
    edge = {q: edges_fs(recs[q]) for q in qs}

    hist = defaultdict(int)
    best_pairs = []
    n_pairs = 0
    for q1, q2 in itertools.combinations(qs, 2):
        n_pairs += 1
        k = exact_vc(set(edge[q1]) | set(edge[q2]), max_k=5)
        hist[str(k)] += 1
        if k is not None and k <= 3:
            best_pairs.append(
                {
                    "q1": list(q1),
                    "q2": list(q2),
                    "joint_vc": k,
                    "lb1": recs[q1]["lower_bound_min_deletions"],
                    "lb2": recs[q2]["lower_bound_min_deletions"],
                    "ex1": recs[q1]["exact_min_hitting_set"],
                    "ex2": recs[q2]["exact_min_hitting_set"],
                    "e1": recs[q1]["blocker_edge_count"],
                    "e2": recs[q2]["blocker_edge_count"],
                }
            )

    best_pairs.sort(key=lambda d: (d["joint_vc"], d["lb1"] + d["lb2"]))
    out = {
        "schema": "lh1_complementary_blocker_pairs_v1",
        "n_qs": len(qs),
        "n_pairs": n_pairs,
        "joint_vc_histogram": dict(hist),
        "n_joint_le_2": sum(1 for p in best_pairs if p["joint_vc"] <= 2),
        "n_joint_le_3": len(best_pairs),
        "best_pairs": best_pairs[:100],
        "qs_lb_hist": dict(
            defaultdict(
                int,
                {
                    str(k): sum(
                        1
                        for q in qs
                        if recs[q]["lower_bound_min_deletions"] == k
                    )
                    for k in range(0, 10)
                },
            )
        ),
        "baseline_hash": sha256_of_points(s0),
        "wall_time_s": time.time() - t0,
    }
    # fix qs_lb_hist properly
    lbh = defaultdict(int)
    for q in qs:
        lbh[str(recs[q]["lower_bound_min_deletions"])] += 1
    out["qs_lb_hist"] = dict(lbh)

    exp = os.path.join(RUN, "EXPERIMENTS", "LH1_blocker_pair")
    path = os.path.join(exp, "complementary_blocker_pairs.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "path": path,
                "n_qs": out["n_qs"],
                "n_pairs": out["n_pairs"],
                "hist": out["joint_vc_histogram"],
                "n_joint_le_2": out["n_joint_le_2"],
                "n_joint_le_3": out["n_joint_le_3"],
                "top_best": best_pairs[:10],
                "qs_lb_hist": out["qs_lb_hist"],
                "wall_s": out["wall_time_s"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
