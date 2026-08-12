#!/usr/bin/env python3
"""Wave3: fixed-card / Hamming with forced remove>=2 + nonlocal free vars.

Uses V=3 elite witness-involved Rem (must delete >=2 from S0∩involved or
from a larger cert Rem), Add = multicomm nonlocal pool. NOT S0+1 soft grinding.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
import time
from typing import List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]
N = 100


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
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_forced_rem2")
    os.makedirs(exp, exist_ok=True)
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    with open(
        os.path.join(RUN, "EXPERIMENTS", "LH1_v3_residual", "v3_residual_n100.json"),
        "r",
        encoding="utf-8",
    ) as f:
        resid = json.load(f)
    rem: Set[Point] = set()
    for e in resid["elites"]:
        for p in e["involved_points"]:
            pt = (int(p[0]), int(p[1]))
            if pt in s0_set:
                rem.add(pt)
    # Expand Rem with cert-involved of LB<=2 for nonlocal exchange capacity
    with gzip.open(
        os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz"),
        "rt",
        encoding="utf-8",
    ) as f:
        detail = json.load(f)
    for r in detail["top_k_full_records"]:
        if int(r["lower_bound_min_deletions"]) <= 2:
            for p in r["involved_baseline_points"]:
                rem.add(tuple(p))
    rem_l = sorted(rem)
    add = [
        (int(r["q"][0]), int(r["q"][1]))
        for r in detail["all_qs_compact"]
        if int(r.get("n_spatial_knn_communities_touched") or 0) >= 3
        and (int(r["q"][0]), int(r["q"][1])) not in s0_set
    ]
    add_l = sorted(set(add))
    uh = universe_hash(rem_l, add_l)
    u_id = "U_v3cert_rem_Add_multicomm3_r2"
    print(
        json.dumps(
            {"U_id": u_id, "n_rem": len(rem_l), "n_add": len(add_l), "hash": uh[:16], "r": 2}
        ),
        flush=True,
    )
    workers = max(1, (os.cpu_count() or 4) // 5)
    result = hamming_shell_search(
        n=N,
        s0=s0,
        removable=rem_l,
        addable=add_l,
        r=2,
        time_budget_s=float(os.environ.get("W3_CHEAP_S", "180")),
        seed=701,
        u_id=u_id,
        universe_hash_str=uh,
        per_round_time_limit_s=30.0,
        num_workers=workers,
        symmetry_mode="asymmetric",
    )
    out = {
        "U_id": u_id,
        "status": result.status,
        "universe_hash": uh,
        "n_rem": len(rem_l),
        "n_add": len(add_l),
        "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
        "rounds": (result.meta or {}).get("rounds"),
        "final_cuts": (result.meta or {}).get("final_cuts"),
        "wall_time_s": (result.meta or {}).get("wall_time_s"),
        "points": [list(p) for p in result.points] if result.points else None,
        "note": "forced r=2; Rem=V3-involved∪e16-involved; Add multicomm>=3; not S0+1 grind",
        "meta": result.meta,
    }
    if out["points"]:
        out["dual"] = dual([tuple(p) for p in out["points"]])
    with open(os.path.join(exp, f"{u_id}_result.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    with open(os.path.join(exp, f"{u_id}_universe.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "U_id": u_id,
                "universe_hash": uh,
                "n_rem": len(rem_l),
                "n_add": len(add_l),
                "rem": [list(p) for p in rem_l],
                "add": [list(p) for p in add_l],
            },
            f,
            indent=2,
            sort_keys=True,
        )
        f.write("\n")
    print(json.dumps({k: out[k] for k in out if k not in ("meta", "points")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
