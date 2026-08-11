#!/usr/bin/env python3
"""LH-2: Drop low-LB filter — Add = all unselected in ring<=R frame; Rem=all S0; r in {2,4}."""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402


def ring(p, n=100):
    x, y = p
    return min(x, y, n - 1 - x, n - 1 - y)


def main():
    # Ensure live progress under non-TTY runners.
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    t0 = time.time()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    exp = os.path.join(RUN, "EXPERIMENTS", "LH2_frame_shells")
    os.makedirs(exp, exist_ok=True)
    summaries = []
    # Smaller frames first; shorter budgets; skip huge R=12 unless needed.
    for R in (2, 4, 6):
        add = sorted(
            (x, y)
            for x in range(100)
            for y in range(100)
            if (x, y) not in s0_set and ring((x, y)) <= R
        )
        rem = list(s0)
        uh = universe_hash(rem, add)
        print(
            json.dumps({"phase": "universe", "R": R, "n_add": len(add), "n_vars": len(rem) + len(add), "hash": uh}),
            flush=True,
        )
        for r in (2, 4):
            u_id = f"U_fullrem_frameR{R}_r{r}"
            print(json.dumps({"phase": "start", "U_id": u_id}), flush=True)
            result = hamming_shell_search(
                n=100,
                s0=s0,
                removable=rem,
                addable=add,
                r=r,
                time_budget_s=90.0,
                seed=1,
                u_id=u_id,
                universe_hash_str=uh,
                per_round_time_limit_s=20.0,
                symmetry_mode="asymmetric",
            )
            row = {
                "U_id": u_id,
                "R": R,
                "r": r,
                "n_add": len(add),
                "n_vars": len(rem) + len(add),
                "universe_hash": uh,
                "status": result.status,
                "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
                "rounds": (result.meta or {}).get("rounds"),
                "final_cuts": (result.meta or {}).get("final_cuts"),
                "wall_time_s": (result.meta or {}).get("wall_time_s"),
            }
            summaries.append(row)
            # checkpoint each result
            with open(os.path.join(exp, f"{u_id}.json"), "w", encoding="utf-8") as f:
                json.dump(row, f, indent=2)
                f.write("\n")
            print(json.dumps(row, indent=2), flush=True)
            if result.status == "FEASIBLE_LEGAL":
                cand = {
                    "points": result.points,
                    "meta": result.meta,
                    "U_id": u_id,
                }
                with open(
                    os.path.join(RUN, "CANDIDATES", f"n100_k165_{u_id}.json"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(cand, f, indent=2)
                break
        else:
            continue
        break

    out = {
        "schema": "lh2_frame_shells_v1",
        "baseline_hash": sha256_of_points(s0),
        "summaries": summaries,
        "wall_s": time.time() - t0,
        "claim_discipline": "Scoped only.",
    }
    path = os.path.join(exp, "frame_shell_summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"path": path, "n": len(summaries), "wall_s": out["wall_s"]}, indent=2))


if __name__ == "__main__":
    main()
