#!/usr/bin/env python3
"""Wave3: r=3 follow-up on cross-knn universes that were INFEAS at r=2.

r=2 SCOPED INFEAS does not kill r=3 (different cardinality model).
Cheap-kill 180s; escalate TIMEOUT only.
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search  # noqa: E402

EXP = os.path.join(RUN, "EXPERIMENTS", "W3_cross_community")
UNIS = [
    "U_cross_knn_bridge_top_LBle7_r2_universe.json",
    "U_cross_knn_corners_vs_sides_LBle7_r2_universe.json",
    "U_cross_knn_left_vs_right_LBle8_r2_universe.json",
]


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    workers = int(os.environ.get("W3_WORKERS", str(max(1, (os.cpu_count() or 4) // 5))))
    cheap = float(os.environ.get("W3_CHEAP_S", "180"))
    long_s = float(os.environ.get("W3_LONG_S", "900"))
    rows = []
    for fname in UNIS:
        path = os.path.join(EXP, fname)
        if not os.path.exists(path):
            print(json.dumps({"skip_missing": fname}), flush=True)
            continue
        with open(path, "r", encoding="utf-8") as f:
            uni = json.load(f)
        rem = [tuple(p) for p in uni["rem"]]
        add = [tuple(p) for p in uni["add"]]
        uh = uni["universe_hash"]
        base = uni["U_id"].replace("_r2", "")
        u_id = f"{base}_r3"
        print(
            json.dumps(
                {"start": u_id, "n_rem": len(rem), "n_add": len(add), "budget": cheap}
            ),
            flush=True,
        )
        t0 = time.time()
        result = hamming_shell_search(
            n=100,
            s0=s0,
            removable=rem,
            addable=add,
            r=3,
            time_budget_s=cheap,
            seed=901,
            u_id=u_id,
            universe_hash_str=uh,
            per_round_time_limit_s=30.0,
            num_workers=workers,
            symmetry_mode="asymmetric",
        )
        out = {
            "U_id": u_id,
            "r": 3,
            "parent_r2_U_id": uni["U_id"],
            "status": result.status,
            "universe_hash": uh,
            "n_rem": len(rem),
            "n_add": len(add),
            "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
            "rounds": (result.meta or {}).get("rounds"),
            "final_cuts": (result.meta or {}).get("final_cuts"),
            "wall_time_s": time.time() - t0,
            "points": [list(p) for p in result.points] if result.points else None,
            "phase": "cheap",
        }
        with open(os.path.join(EXP, f"{u_id}_cheap.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, sort_keys=True)
            f.write("\n")
        rows.append({k: out[k] for k in out if k != "points"})
        print(json.dumps(rows[-1], indent=2), flush=True)
        if out["status"] == "TIMEOUT_INCONCLUSIVE":
            t1 = time.time()
            result2 = hamming_shell_search(
                n=100,
                s0=s0,
                removable=rem,
                addable=add,
                r=3,
                time_budget_s=long_s,
                seed=902,
                u_id=u_id,
                universe_hash_str=uh,
                per_round_time_limit_s=40.0,
                num_workers=workers,
                symmetry_mode="asymmetric",
            )
            out2 = {
                "U_id": u_id,
                "r": 3,
                "status": result2.status,
                "universe_hash": uh,
                "n_rem": len(rem),
                "n_add": len(add),
                "best_illegal_V": (result2.meta or {}).get("best_illegal_V"),
                "rounds": (result2.meta or {}).get("rounds"),
                "final_cuts": (result2.meta or {}).get("final_cuts"),
                "wall_time_s": time.time() - t1,
                "points": [list(p) for p in result2.points] if result2.points else None,
                "phase": "long",
            }
            with open(os.path.join(EXP, f"{u_id}_long.json"), "w", encoding="utf-8") as f:
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
    with open(os.path.join(EXP, "r3_followup_summary.json"), "w", encoding="utf-8") as f:
        json.dump({"schema": "w3_cross_r3_v1", "rows": rows}, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"done": True, "n_rows": len(rows)}), flush=True)


if __name__ == "__main__":
    main()
