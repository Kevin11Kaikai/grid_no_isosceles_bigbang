#!/usr/bin/env python3
"""LH-2: CP-SAT r=4 shells on Rem=union of size-4 joint covers of easiest pairs, Add=LB<=5."""
from __future__ import annotations

import gzip
import importlib.util
import itertools
import json
import os
import sys
import time
from typing import Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")
DETAIL = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_r4c", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


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
    add = sorted(
        {
            tuple(r["q"])
            for r in detail["all_qs_compact"]
            if int(r["lower_bound_min_deletions"]) <= 5
        }
        - s0_set
    )
    edge = {
        q: [
            frozenset((tuple(e[0]), tuple(e[1])))
            for e in ba.analyze_q(q, s0, maps, 100)["blocker_edges"]
        ]
        for q in easy
    }
    rem_set: Set[Point] = set()
    n_covers = 0
    for q1, q2 in itertools.combinations(easy, 2):
        edges = set(edge[q1]) | set(edge[q2])
        involved = sorted({p for e in edges for p in e})
        for comb in itertools.combinations(involved, 4):
            C = set(comb)
            if all(e & C for e in edges):
                rem_set.update(comb)
                n_covers += 1
                break  # one cover per pair enough for Rem union seed
    rem = sorted(rem_set)
    uh = universe_hash(rem, add)
    exp = os.path.join(RUN, "EXPERIMENTS", "LH2_r4_pair_micro")
    os.makedirs(exp, exist_ok=True)
    uni = {
        "U_id": "U_paircover4_LBle5_r4",
        "n_rem": len(rem),
        "n_add": len(add),
        "n_vars": len(rem) + len(add),
        "universe_hash": uh,
        "n_pair_covers_seeded": n_covers,
    }
    with open(os.path.join(exp, "U_paircover4_LBle5_r4.json"), "w", encoding="utf-8") as f:
        json.dump({**uni, "rem": [list(p) for p in rem], "add": [list(p) for p in add]}, f, indent=2)
        f.write("\n")
    print(json.dumps(uni, indent=2))

    result = hamming_shell_search(
        n=100,
        s0=s0,
        removable=rem,
        addable=add,
        r=4,
        time_budget_s=300.0,
        seed=1,
        u_id=uni["U_id"],
        universe_hash_str=uh,
        per_round_time_limit_s=40.0,
        symmetry_mode="asymmetric",
    )
    # Also fullrem r=4 with same Add
    uh2 = universe_hash(s0, add)
    result2 = hamming_shell_search(
        n=100,
        s0=s0,
        removable=s0,
        addable=add,
        r=4,
        time_budget_s=300.0,
        seed=1,
        u_id="U_fullrem_LBle5_r4",
        universe_hash_str=uh2,
        per_round_time_limit_s=40.0,
        symmetry_mode="asymmetric",
    )
    payload = {
        "paircover": {
            "status": result.status,
            "meta": result.meta,
            "universe": uni,
        },
        "fullrem": {
            "status": result2.status,
            "meta": result2.meta,
            "n_rem": 164,
            "n_add": len(add),
            "universe_hash": uh2,
        },
        "baseline_hash": sha256_of_points(s0),
        "wall_s": time.time() - t0,
    }
    out = os.path.join(exp, "cpsat_r4_shells.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "out": out,
                "paircover_status": result.status,
                "paircover_best_V": (result.meta or {}).get("best_illegal_V"),
                "paircover_rounds": (result.meta or {}).get("rounds"),
                "fullrem_status": result2.status,
                "fullrem_best_V": (result2.meta or {}).get("best_illegal_V"),
                "fullrem_rounds": (result2.meta or {}).get("rounds"),
                "wall_s": payload["wall_s"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
