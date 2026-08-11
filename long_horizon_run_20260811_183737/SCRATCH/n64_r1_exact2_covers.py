#!/usr/bin/env python3
"""n64 sandbox: r=1 shells with Rem=exact size-1 covers of easiest qs (exact deletion=1).

Global min deletion=1 on n64, so r=1 is valid. Wave2 score U_small was INFEAS;
certificate Rem may differ.
"""
from __future__ import annotations

import gzip
import importlib.util
import itertools
import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_64  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")
DETAIL = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n64.json.gz")


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_n64", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main():
    t0 = time.time()
    ba = load_ba()
    s0 = sorted((int(x), int(y)) for x, y in SOL_64)
    s0_set = set(s0)
    maps = ba.precompute_pivot_maps(s0)
    with gzip.open(DETAIL, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    easy = [
        tuple(r["q"])
        for r in detail["all_qs_compact"]
        if r.get("exact_min_hitting_set") == 1
        or (
            r.get("lower_bound_min_deletions") == 1
            and r.get("upper_bound_min_deletions") == 1
        )
    ]
    # Also include Gate1 easiest [[62,2],[62,61]]
    for q in [(62, 2), (62, 61)]:
        if q not in easy:
            easy.append(q)
    rem_set = set()
    add = set(easy)
    for q in easy:
        rec = ba.analyze_q(q, s0, maps, 64)
        edges = [frozenset((tuple(e[0]), tuple(e[1]))) for e in rec["blocker_edges"]]
        involved = sorted({p for e in edges for p in e})
        # size-1 covers: vertices that hit all edges
        for v in involved:
            if all(v in e for e in edges):
                rem_set.add(v)
        # if no universal hitter, take all size-1? none; then use all involved as Rem pool
        if not any(all(v in e for e in edges) for v in involved):
            rem_set.update(involved)
    # Expand Add: all LB<=3
    for r in detail["all_qs_compact"]:
        if int(r["lower_bound_min_deletions"]) <= 3:
            q = tuple(r["q"])
            if q not in s0_set:
                add.add(q)
    rem = sorted(rem_set)
    add_l = sorted(add)
    uh = universe_hash(rem, add_l)
    exp = os.path.join(RUN, "EXPERIMENTS", "LH2_n64_cert_r1")
    os.makedirs(exp, exist_ok=True)
    uni = {
        "U_id": "U_n64_exact1covers_LBle3_r1",
        "n_rem": len(rem),
        "n_add": len(add_l),
        "n_vars": len(rem) + len(add_l),
        "universe_hash": uh,
        "n_easy": len(easy),
        "easy": [list(q) for q in easy],
    }
    with open(os.path.join(exp, "universe.json"), "w", encoding="utf-8") as f:
        json.dump({**uni, "rem": [list(p) for p in rem], "add": [list(p) for p in add_l]}, f, indent=2)
        f.write("\n")
    print(json.dumps(uni, indent=2), flush=True)
    result = hamming_shell_search(
        n=64,
        s0=s0,
        removable=rem,
        addable=add_l,
        r=1,
        time_budget_s=120.0,
        seed=1,
        u_id=uni["U_id"],
        universe_hash_str=uh,
        per_round_time_limit_s=20.0,
        symmetry_mode="asymmetric",
    )
    payload = {
        "status": result.status,
        "meta": result.meta,
        "points": result.points,
        "universe": uni,
        "baseline_hash": sha256_of_points(s0),
        "wall_s": time.time() - t0,
    }
    out = os.path.join(exp, "shell_r1_seed1.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "out": out,
                "status": result.status,
                "best_V": (result.meta or {}).get("best_illegal_V"),
                "rounds": (result.meta or {}).get("rounds"),
                "cuts": (result.meta or {}).get("final_cuts"),
                "wall_s": payload["wall_s"],
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
