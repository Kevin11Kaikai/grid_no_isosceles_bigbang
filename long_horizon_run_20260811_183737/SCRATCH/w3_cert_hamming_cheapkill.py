#!/usr/bin/env python3
"""Wave3 R2: certificate-driven Hamming Rem/Add cheap-kills (outside Wave2 U_*).

Two new U_ids at r=2 (primary; r=1 negative-control only elsewhere):
  1) U_cert_involved_e16_Add_e56_r2
     Rem = union of involved baseline points of all LB<=2 qs (from top-K full records)
     Add = all qs with LB<=3 (compact)
  2) U_certfreq_top48_Add_LBle5_r2
     Rem = top-48 baseline verts by q-weighted certificate frequency
     Add = qs with LB<=5

Cheap-kill budget first (default 90s). Escalate survivors only.
Scoped INFEASIBLE != global UB. TIMEOUT != INFEASIBLE.
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
from src.search.hamming_shell_conflict import (  # noqa: E402
    hamming_shell_search,
    universe_hash,
)
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
N = 100
DETAIL_GZ = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")
COMM = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_communities_n100.json")


def _pts(seq: Sequence[Sequence[int]]) -> List[Point]:
    return [(int(p[0]), int(p[1])) for p in seq]


def build_universes():
    s0 = sorted(_pts(SOL_100))
    s0_set = set(s0)
    with gzip.open(DETAIL_GZ, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    top = detail["top_k_full_records"]
    compact = detail["all_qs_compact"]

    rem1 = set()
    e16 = []
    for r in top:
        if int(r["lower_bound_min_deletions"]) <= 2:
            e16.append(tuple(r["q"]))
            for p in r["involved_baseline_points"]:
                rem1.add(tuple(p))
    add1 = []
    for r in compact:
        if int(r["lower_bound_min_deletions"]) <= 3:
            q = (int(r["q"][0]), int(r["q"][1]))
            if q not in s0_set:
                add1.append(q)
    rem1_l = sorted(rem1)
    add1_l = sorted(set(add1))

    with open(COMM, "r", encoding="utf-8") as f:
        comm = json.load(f)
    verts = Counter()
    for rec in comm["bipartite_incidence"]["top_certificates_by_q_frequency"]:
        w = int(rec["n_qs_blocked_by_this_edge"])
        for p in rec["certificate_edge"]:
            verts[tuple(p)] += w
    rem2_l = [p for p, _ in verts.most_common(48) if p in s0_set]
    rem2_l = sorted(set(rem2_l))
    add2 = []
    for r in compact:
        if int(r["lower_bound_min_deletions"]) <= 5:
            q = (int(r["q"][0]), int(r["q"][1]))
            if q not in s0_set:
                add2.append(q)
    add2_l = sorted(set(add2))

    u1 = {
        "U_id": "U_cert_involved_e16_Add_e56_r2",
        "rem": rem1_l,
        "add": add1_l,
        "n_rem": len(rem1_l),
        "n_add": len(add1_l),
        "universe_hash": universe_hash(rem1_l, add1_l),
        "note": "certificate-involved Rem for LB<=2 qs; Add LB<=3; r=2; not Wave2 score-U",
        "e16_qs": [list(q) for q in e16],
    }
    u2 = {
        "U_id": "U_certfreq_top48_Add_LBle5_r2",
        "rem": rem2_l,
        "add": add2_l,
        "n_rem": len(rem2_l),
        "n_add": len(add2_l),
        "universe_hash": universe_hash(rem2_l, add2_l),
        "note": "Rem=top48 q-weighted cert-frequency verts; Add LB<=5; r=2",
    }
    return s0, [u1, u2]


def run_one(s0, uni, time_budget_s: float, seed: int, workers: int):
    rem = [tuple(p) for p in uni["rem"]]
    add = [tuple(p) for p in uni["add"]]
    uh = uni["universe_hash"]
    t0 = time.time()
    result = hamming_shell_search(
        n=N,
        s0=s0,
        removable=rem,
        addable=add,
        r=2,
        time_budget_s=time_budget_s,
        seed=seed,
        u_id=uni["U_id"],
        universe_hash_str=uh,
        per_round_time_limit_s=min(30.0, time_budget_s),
        num_workers=workers,
        symmetry_mode="asymmetric",
    )
    return {
        "U_id": uni["U_id"],
        "status": result.status,
        "universe_hash": uh,
        "n_rem": uni["n_rem"],
        "n_add": uni["n_add"],
        "n_vars": uni["n_rem"] + uni["n_add"],
        "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
        "rounds": (result.meta or {}).get("rounds"),
        "final_cuts": (result.meta or {}).get("final_cuts"),
        "wall_time_s": time.time() - t0,
        "points": [list(p) for p in result.points] if result.points else None,
        "baseline_hash": sha256_of_points(s0),
        "meta": result.meta,
        "note": uni.get("note"),
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    cheap_s = float(os.environ.get("W3_CHEAP_S", "90"))
    long_s = float(os.environ.get("W3_LONG_S", "600"))
    workers = int(os.environ.get("W3_WORKERS", str(max(1, (os.cpu_count() or 4) // 5))))
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_cert_hamming")
    os.makedirs(exp, exist_ok=True)

    s0, unis = build_universes()
    for uni in unis:
        path_u = os.path.join(exp, f"{uni['U_id']}_universe.json")
        with open(path_u, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "U_id": uni["U_id"],
                    "n_rem": uni["n_rem"],
                    "n_add": uni["n_add"],
                    "universe_hash": uni["universe_hash"],
                    "note": uni.get("note"),
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
                    "n_rem": uni["n_rem"],
                    "n_add": uni["n_add"],
                    "hash": uni["universe_hash"][:16],
                }
            ),
            flush=True,
        )

    rows = []
    escalate = []
    for uni in unis:
        print(json.dumps({"cheapkill_start": uni["U_id"], "budget_s": cheap_s}), flush=True)
        row = run_one(s0, uni, cheap_s, seed=501, workers=workers)
        path = os.path.join(exp, f"{uni['U_id']}_cheap.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(row, f, indent=2, sort_keys=True)
            f.write("\n")
        rows.append({"phase": "cheap", **{k: row[k] for k in row if k not in ("meta", "points")}})
        print(json.dumps(rows[-1], indent=2), flush=True)
        if row["status"] == "FEASIBLE_LEGAL":
            cand_dir = os.path.join(RUN, "CANDIDATES")
            os.makedirs(cand_dir, exist_ok=True)
            with open(os.path.join(cand_dir, f"{uni['U_id']}_legal.json"), "w", encoding="utf-8") as f:
                json.dump(row, f, indent=2)
            escalate.append(uni["U_id"])  # already done
        elif row["status"] == "TIMEOUT_INCONCLUSIVE":
            escalate.append(uni["U_id"])
        # INFEASIBLE_SCOPED => cheap-killed; do not escalate

    # Escalate only TIMEOUT survivors
    for uni in unis:
        if uni["U_id"] not in escalate:
            continue
        if any(r.get("status") == "FEASIBLE_LEGAL" and r.get("U_id") == uni["U_id"] for r in rows):
            continue
        print(json.dumps({"escalate_start": uni["U_id"], "budget_s": long_s}), flush=True)
        row = run_one(s0, uni, long_s, seed=502, workers=workers)
        path = os.path.join(exp, f"{uni['U_id']}_long.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(row, f, indent=2, sort_keys=True)
            f.write("\n")
        rows.append({"phase": "long", **{k: row[k] for k in row if k not in ("meta", "points")}})
        print(json.dumps(rows[-1], indent=2), flush=True)
        if row["status"] == "FEASIBLE_LEGAL" and row.get("points"):
            cand_dir = os.path.join(RUN, "CANDIDATES")
            os.makedirs(cand_dir, exist_ok=True)
            with open(os.path.join(cand_dir, f"{uni['U_id']}_legal.json"), "w", encoding="utf-8") as f:
                json.dump(row, f, indent=2)

    summary = {
        "schema": "w3_cert_hamming_v1",
        "cheap_s": cheap_s,
        "long_s": long_s,
        "workers": workers,
        "rows": rows,
        "escalated": escalate,
        "killed_wave2_uids_not_rerun": [
            "U_small",
            "U_small_r2",
            "U_medium",
            "U_large",
            "U_fullrem_LBle4_r2",
        ],
    }
    sp = os.path.join(exp, "summary.json")
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"summary": sp, "n_rows": len(rows)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
