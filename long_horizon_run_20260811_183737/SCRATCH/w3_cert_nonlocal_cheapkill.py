#!/usr/bin/env python3
"""Wave3 R2 follow-up: nonlocal certificate Add + broader involved Rem.

New U_ids (outside killed Wave2 score-U and W3 first cheap-kills):
  A) U_cert_involved_e56_Add_LBle6_r2
     Rem = involved baselines of LB<=3 qs; Add = LB<=6; r=2
  B) U_fullrem_Add_multicomm4_r2
     Rem = all S0; Add = unselected qs with n_spatial_knn_communities_touched >= 4; r=2
  C) U_fullrem_Add_multicomm4_r3  (only if B is TIMEOUT; else also cheap-kill)
  D) U_certfreq_top80_Add_midband_r2
     Rem = top-80 cert-freq verts; Add = midband ring 10..26 union LB<=8; r=2

Cheap-kill <=120s; escalate TIMEOUT only.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
import time
from collections import Counter
from typing import List, Sequence, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
N = 100
DETAIL_GZ = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")
COMM = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_communities_n100.json")


def ring(p: Point, n: int = 100) -> int:
    x, y = p
    return min(x, y, n - 1 - x, n - 1 - y)


def build():
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    with gzip.open(DETAIL_GZ, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    top = detail["top_k_full_records"]
    compact = detail["all_qs_compact"]

    rem_e56 = set()
    for r in top:
        if int(r["lower_bound_min_deletions"]) <= 3:
            for p in r["involved_baseline_points"]:
                rem_e56.add(tuple(p))
    # top only has 200; for LB<=3 some may be outside top — use compact ranks via top ease
    # Supplement: any top record with LB<=3 already covers ease_rank 0..55 typically
    add_lb6 = [
        (int(r["q"][0]), int(r["q"][1]))
        for r in compact
        if int(r["lower_bound_min_deletions"]) <= 6
        and (int(r["q"][0]), int(r["q"][1])) not in s0_set
    ]

    add_mc4 = [
        (int(r["q"][0]), int(r["q"][1]))
        for r in compact
        if int(r.get("n_spatial_knn_communities_touched") or 0) >= 4
        and (int(r["q"][0]), int(r["q"][1])) not in s0_set
    ]

    with open(COMM, "r", encoding="utf-8") as f:
        comm = json.load(f)
    verts = Counter()
    for rec in comm["bipartite_incidence"]["top_certificates_by_q_frequency"]:
        w = int(rec["n_qs_blocked_by_this_edge"])
        for p in rec["certificate_edge"]:
            verts[tuple(p)] += w
    rem80 = sorted({p for p, _ in verts.most_common(80) if p in s0_set})

    add_mid = set()
    for r in compact:
        q = (int(r["q"][0]), int(r["q"][1]))
        if q in s0_set:
            continue
        if int(r["lower_bound_min_deletions"]) <= 8 or 10 <= ring(q) <= 26:
            add_mid.add(q)

    unis = [
        {
            "U_id": "U_cert_involved_e56_Add_LBle6_r2",
            "rem": sorted(rem_e56),
            "add": sorted(set(add_lb6)),
            "r": 2,
            "note": "broader cert-involved Rem (LB<=3); Add LB<=6",
        },
        {
            "U_id": "U_fullrem_Add_multicomm4_r2",
            "rem": list(s0),
            "add": sorted(set(add_mc4)),
            "r": 2,
            "note": "full Rem; Add=nonlocal multi-community qs (>=4 knn CCs)",
        },
        {
            "U_id": "U_fullrem_Add_multicomm4_r3",
            "rem": list(s0),
            "add": sorted(set(add_mc4)),
            "r": 3,
            "note": "same Add as multicomm4; r=3 shell",
        },
        {
            "U_id": "U_certfreq_top80_Add_midband_r2",
            "rem": rem80,
            "add": sorted(add_mid),
            "r": 2,
            "note": "certfreq Rem80; midband∪LB<=8 Add",
        },
    ]
    for u in unis:
        u["universe_hash"] = universe_hash(u["rem"], u["add"])
        u["n_rem"] = len(u["rem"])
        u["n_add"] = len(u["add"])
    return s0, unis


def run_one(s0, uni, budget, seed, workers):
    t0 = time.time()
    result = hamming_shell_search(
        n=N,
        s0=s0,
        removable=uni["rem"],
        addable=uni["add"],
        r=int(uni["r"]),
        time_budget_s=budget,
        seed=seed,
        u_id=uni["U_id"],
        universe_hash_str=uni["universe_hash"],
        per_round_time_limit_s=min(30.0, budget),
        num_workers=workers,
        symmetry_mode="asymmetric",
    )
    return {
        "U_id": uni["U_id"],
        "r": uni["r"],
        "status": result.status,
        "universe_hash": uni["universe_hash"],
        "n_rem": uni["n_rem"],
        "n_add": uni["n_add"],
        "n_vars": uni["n_rem"] + uni["n_add"],
        "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
        "rounds": (result.meta or {}).get("rounds"),
        "final_cuts": (result.meta or {}).get("final_cuts"),
        "wall_time_s": time.time() - t0,
        "points": [list(p) for p in result.points] if result.points else None,
        "baseline_hash": sha256_of_points(s0),
        "note": uni["note"],
        "meta": result.meta,
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    cheap = float(os.environ.get("W3_CHEAP_S", "120"))
    long_s = float(os.environ.get("W3_LONG_S", "900"))
    workers = int(os.environ.get("W3_WORKERS", str(max(1, (os.cpu_count() or 4) // 5))))
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_cert_nonlocal")
    os.makedirs(exp, exist_ok=True)
    s0, unis = build()
    rows = []
    escalate = []
    for uni in unis:
        up = os.path.join(exp, f"{uni['U_id']}_universe.json")
        with open(up, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "U_id": uni["U_id"],
                    "r": uni["r"],
                    "n_rem": uni["n_rem"],
                    "n_add": uni["n_add"],
                    "universe_hash": uni["universe_hash"],
                    "note": uni["note"],
                    "rem": [list(p) for p in uni["rem"]],
                    "add": [list(p) for p in uni["add"]],
                },
                f,
                indent=2,
                sort_keys=True,
            )
            f.write("\n")
        print(
            json.dumps(
                {
                    "built": uni["U_id"],
                    "r": uni["r"],
                    "n_rem": uni["n_rem"],
                    "n_add": uni["n_add"],
                    "hash": uni["universe_hash"][:16],
                }
            ),
            flush=True,
        )

    for uni in unis:
        print(json.dumps({"cheapkill_start": uni["U_id"], "budget_s": cheap}), flush=True)
        row = run_one(s0, uni, cheap, seed=601, workers=workers)
        with open(os.path.join(exp, f"{uni['U_id']}_cheap.json"), "w", encoding="utf-8") as f:
            json.dump(row, f, indent=2, sort_keys=True)
            f.write("\n")
        slim = {k: row[k] for k in row if k not in ("meta", "points")}
        slim["phase"] = "cheap"
        rows.append(slim)
        print(json.dumps(slim, indent=2), flush=True)
        if row["status"] == "TIMEOUT_INCONCLUSIVE":
            escalate.append(uni)
        if row["status"] == "FEASIBLE_LEGAL" and row.get("points"):
            os.makedirs(os.path.join(RUN, "CANDIDATES"), exist_ok=True)
            with open(
                os.path.join(RUN, "CANDIDATES", f"{uni['U_id']}_legal.json"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(row, f, indent=2)

    for uni in escalate:
        print(json.dumps({"escalate_start": uni["U_id"], "budget_s": long_s}), flush=True)
        row = run_one(s0, uni, long_s, seed=602, workers=workers)
        with open(os.path.join(exp, f"{uni['U_id']}_long.json"), "w", encoding="utf-8") as f:
            json.dump(row, f, indent=2, sort_keys=True)
            f.write("\n")
        slim = {k: row[k] for k in row if k not in ("meta", "points")}
        slim["phase"] = "long"
        rows.append(slim)
        print(json.dumps(slim, indent=2), flush=True)
        if row["status"] == "FEASIBLE_LEGAL" and row.get("points"):
            os.makedirs(os.path.join(RUN, "CANDIDATES"), exist_ok=True)
            with open(
                os.path.join(RUN, "CANDIDATES", f"{uni['U_id']}_legal.json"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(row, f, indent=2)

    summary = {
        "schema": "w3_cert_nonlocal_v1",
        "cheap_s": cheap,
        "long_s": long_s,
        "workers": workers,
        "rows": rows,
        "escalated": [u["U_id"] for u in escalate],
    }
    with open(os.path.join(exp, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"done": True, "n_rows": len(rows), "escalated": summary["escalated"]}), flush=True)


if __name__ == "__main__":
    main()
