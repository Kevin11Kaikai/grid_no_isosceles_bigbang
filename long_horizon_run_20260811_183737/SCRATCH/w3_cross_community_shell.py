#!/usr/bin/env python3
"""Wave3 R2: cross spatial-knn community Hamming exchange (structured nonlocal).

Rem = baseline points in spatial knn communities A (e.g. {0,1,2,3} corner quartet
      or a far-conflict bridge pair).
Add = qs with LB<=7 that touch the complementary community set.
Forces r=2. Cheap-kill first; escalate TIMEOUT only.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
import time
from typing import Dict, List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402

Point = Tuple[int, int]
N = 100
COMM = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_communities_n100.json")
DETAIL = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_cross_community")
    os.makedirs(exp, exist_ok=True)
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)

    with open(COMM, "r", encoding="utf-8") as f:
        comm = json.load(f)
    knn = comm["communities_spatial_knn6"]
    p2c: Dict[Point, int] = {}
    for com in knn:
        cid = int(com["community_id"])
        for p in com["baseline_points"]:
            p2c[(int(p[0]), int(p[1]))] = cid

    # Pilot A: rem = far-conflict bridge pair communities with highest weight
    bridges = sorted(
        comm["spatially_far_conflict_bridges_knn"],
        key=lambda b: -int(b["conflict_bridge_weight"]),
    )
    b0 = bridges[0]
    rem_cids = {int(b0["community_a"]), int(b0["community_b"])}
    add_cids = set(range(10)) - rem_cids

    jobs = [
        ("bridge_top", rem_cids, add_cids, 7),
        ("corners_vs_sides", {0, 1, 2, 3}, {4, 5, 6, 7, 8, 9}, 7),
        ("left_vs_right", {6, 7, 8}, {4, 5, 9}, 8),
    ]

    with gzip.open(DETAIL, "rt", encoding="utf-8") as f:
        detail = json.load(f)

    workers = int(os.environ.get("W3_WORKERS", str(max(1, (os.cpu_count() or 4) // 5))))
    cheap = float(os.environ.get("W3_CHEAP_S", "150"))
    long_s = float(os.environ.get("W3_LONG_S", "900"))
    rows = []

    for tag, rem_cids, add_cids, lb_max in jobs:
        rem = sorted([p for p, cid in p2c.items() if cid in rem_cids and p in s0_set])
        add: List[Point] = []
        for r in detail["all_qs_compact"]:
            q = (int(r["q"][0]), int(r["q"][1]))
            if q in s0_set:
                continue
            if int(r["lower_bound_min_deletions"]) > lb_max:
                continue
            touched = set(int(x) for x in (r.get("spatial_knn_communities_touched") or []))
            # must touch rem side (conflict with Rem) AND add side (nonlocal placement)
            if (touched & rem_cids) and (touched & add_cids):
                add.append(q)
        add = sorted(set(add))
        u_id = f"U_cross_knn_{tag}_LBle{lb_max}_r2"
        uh = universe_hash(rem, add)
        meta_u = {
            "U_id": u_id,
            "tag": tag,
            "rem_cids": sorted(rem_cids),
            "add_cids": sorted(add_cids),
            "lb_max": lb_max,
            "n_rem": len(rem),
            "n_add": len(add),
            "universe_hash": uh,
        }
        print(json.dumps({"built": meta_u}), flush=True)
        with open(os.path.join(exp, f"{u_id}_universe.json"), "w", encoding="utf-8") as f:
            json.dump(
                {**meta_u, "rem": [list(p) for p in rem], "add": [list(p) for p in add]},
                f,
                indent=2,
                sort_keys=True,
            )
            f.write("\n")
        if len(rem) < 2 or len(add) < 3:
            rows.append({**meta_u, "status": "ERROR_SMALL_UNIVERSE", "phase": "cheap"})
            continue

        print(json.dumps({"cheapkill_start": u_id, "budget_s": cheap}), flush=True)
        t0 = time.time()
        result = hamming_shell_search(
            n=N,
            s0=s0,
            removable=rem,
            addable=add,
            r=2,
            time_budget_s=cheap,
            seed=801,
            u_id=u_id,
            universe_hash_str=uh,
            per_round_time_limit_s=30.0,
            num_workers=workers,
            symmetry_mode="asymmetric",
        )
        out = {
            **meta_u,
            "status": result.status,
            "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
            "rounds": (result.meta or {}).get("rounds"),
            "final_cuts": (result.meta or {}).get("final_cuts"),
            "wall_time_s": time.time() - t0,
            "points": [list(p) for p in result.points] if result.points else None,
            "phase": "cheap",
        }
        with open(os.path.join(exp, f"{u_id}_cheap.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, sort_keys=True)
            f.write("\n")
        rows.append({k: out[k] for k in out if k != "points"})
        print(json.dumps(rows[-1], indent=2), flush=True)

        if out["status"] == "TIMEOUT_INCONCLUSIVE":
            print(json.dumps({"escalate": u_id, "budget_s": long_s}), flush=True)
            t1 = time.time()
            result2 = hamming_shell_search(
                n=N,
                s0=s0,
                removable=rem,
                addable=add,
                r=2,
                time_budget_s=long_s,
                seed=802,
                u_id=u_id,
                universe_hash_str=uh,
                per_round_time_limit_s=40.0,
                num_workers=workers,
                symmetry_mode="asymmetric",
            )
            out2 = {
                **meta_u,
                "status": result2.status,
                "best_illegal_V": (result2.meta or {}).get("best_illegal_V"),
                "rounds": (result2.meta or {}).get("rounds"),
                "final_cuts": (result2.meta or {}).get("final_cuts"),
                "wall_time_s": time.time() - t1,
                "points": [list(p) for p in result2.points] if result2.points else None,
                "phase": "long",
            }
            with open(os.path.join(exp, f"{u_id}_long.json"), "w", encoding="utf-8") as f:
                json.dump(out2, f, indent=2, sort_keys=True)
                f.write("\n")
            rows.append({k: out2[k] for k in out2 if k != "points"})
            print(json.dumps(rows[-1], indent=2), flush=True)
            if out2["status"] == "FEASIBLE_LEGAL" and out2.get("points"):
                os.makedirs(os.path.join(RUN, "CANDIDATES"), exist_ok=True)
                with open(
                    os.path.join(RUN, "CANDIDATES", f"{u_id}_legal.json"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(out2, f, indent=2)
        elif out["status"] == "FEASIBLE_LEGAL" and out.get("points"):
            os.makedirs(os.path.join(RUN, "CANDIDATES"), exist_ok=True)
            with open(
                os.path.join(RUN, "CANDIDATES", f"{u_id}_legal.json"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(out, f, indent=2)

    summary = {"schema": "w3_cross_community_v1", "rows": rows}
    with open(os.path.join(exp, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"done": True, "n_rows": len(rows)}), flush=True)


if __name__ == "__main__":
    main()
