#!/usr/bin/env python3
"""Hamming on the first k-delete recipe with n_unsel>0: top-degree Rem k=32, Add=8.

r in 4..7 (need r+1 <= 8). Cheap-kill 40s each. Distinct from Wave2 score U_ids.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

EXP = os.path.join(RUN, "EXPERIMENTS", "W3_topdeg32_hamming")
os.makedirs(EXP, exist_ok=True)
COMM = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_communities_n100.json")
N = 100


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    s0 = [tuple(map(int, p)) for p in SOL_100]
    s0_set = set(s0)
    with open(COMM, "r", encoding="utf-8") as f:
        comm = json.load(f)
    freq = Counter()
    for item in comm["bipartite_incidence"]["top_certificates_by_q_frequency"][:400]:
        a, b = item["certificate_edge"]
        w = item["n_qs_blocked_by_this_edge"]
        freq[tuple(a)] += w
        freq[tuple(b)] += w
    rem = [p for p, _ in freq.most_common(32)]
    rem_set = set(rem)
    st = IncrementalIsoscelesFreeSet(N)
    for p in s0:
        if p not in rem_set:
            assert st.add_point(p)
    add = []
    for x in range(N):
        for y in range(N):
            p = (x, y)
            if p in st.points or p in rem_set:
                continue
            if st.can_add(p)[0]:
                add.append(p)
    uh = universe_hash(rem, add)
    print(json.dumps({"n_rem": len(rem), "n_add": len(add), "hash": uh, "add": add}), flush=True)
    rows = []
    t0 = time.time()
    for r in range(1, min(len(add), len(rem))):
        if r + 1 > len(add):
            continue
        uid = f"U_topdeg32_r{r}"
        res = hamming_shell_search(
            n=N,
            s0=s0,
            removable=rem,
            addable=add,
            r=r,
            time_budget_s=40.0,
            seed=1,
            u_id=uid,
            universe_hash_str=uh,
            per_round_time_limit_s=12.0,
            num_workers=4,
        )
        row = {
            "r": r,
            "status": res.status,
            "n_add": len(add),
            "universe_hash": uh,
            "meta": res.meta if isinstance(res.meta, dict) else {},
            "size": len(res.points) if res.points else 0,
        }
        if res.points:
            row["hash"] = sha256_of_points(res.points)
        rows.append(row)
        print(json.dumps({k: row[k] for k in row if k != "meta"}), flush=True)
        with open(os.path.join(EXP, f"{uid}.json"), "w", encoding="utf-8") as f:
            json.dump({"row": row, "points": res.points}, f, indent=2, default=str)
            f.write("\n")
        if res.points and len(res.points) >= 165:
            break
    summary = {
        "schema": "w3_topdeg32_hamming_v1",
        "n_rem": 32,
        "n_add": len(add),
        "add": [list(p) for p in add],
        "universe_hash": uh,
        "rows": rows,
        "any_plus": any((r.get("size") or 0) >= 165 for r in rows),
        "wall_s": time.time() - t0,
    }
    with open(os.path.join(EXP, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    print(json.dumps({"any_plus": summary["any_plus"], "statuses": [r["status"] for r in rows], "wall_s": summary["wall_s"]}), flush=True)


if __name__ == "__main__":
    main()
