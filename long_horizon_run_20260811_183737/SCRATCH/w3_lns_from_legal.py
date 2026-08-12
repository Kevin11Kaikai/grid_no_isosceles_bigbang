#!/usr/bin/env python3
"""Wave3: exact-LNS destroy/refill from legal sets (S0=164 and grow~135).

NOT S0+1 soft grind: region destroy can remove many baseline points; repair is exact MILP.
Aim |S|>=165 with dual verify on improvement.
"""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(RUN, "SCRATCH"))

from data.baselines.official_raw import SOL_100  # noqa: E402
from from_scratch_grow import grow  # noqa: E402
from src.search.lns_exact_repair import lns_exact_run  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402


def dual(pts, n=100):
    oka, _ = is_legal_pivot_method(pts, n)
    okb, _ = verify_independent(pts, n)
    return {
        "oracle": bool(oka),
        "indep": bool(okb),
        "size": len(pts),
        "hash": sha256_of_points(pts) if pts else None,
    }


def run_one(tag, start, time_s, seed, milp_s):
    print(json.dumps({"start": tag, "n0": len(start), "time_s": time_s, "milp_s": milp_s}), flush=True)
    t0 = time.time()
    best, meta = lns_exact_run(
        n=100,
        initial_points=start,
        time_budget_s=time_s,
        seed=seed,
        milp_time_limit_s=milp_s,
        region_kind_weights=(0.4, 0.35, 0.25),
    )
    pts = [tuple(p) for p in best] if best else []
    d = dual(pts)
    row = {
        "tag": tag,
        "start_size": len(start),
        "final_size": len(pts),
        "beats_164": d["size"] > 164 and d["oracle"] and d["indep"],
        "dual": d,
        "meta": {k: meta.get(k) for k in ("iterations", "milp_calls", "improvements", "wall_time_s", "final_size")},
        "wall_wrapper_s": time.time() - t0,
    }
    print(json.dumps({k: v for k, v in row.items() if k != "dual"} | {"dual": d}, indent=2), flush=True)
    if row["beats_164"]:
        cand = os.path.join(RUN, "CANDIDATES", f"{tag}_legal_plus.json")
        json.dump({"points": [list(p) for p in pts], **row}, open(cand, "w"), indent=2)
        row["candidate"] = cand
    return row


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_lns_from_legal")
    os.makedirs(exp, exist_ok=True)
    rows = []

    # Job A: from official S0
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    assert dual(s0)["oracle"] and dual(s0)["indep"]
    rows.append(
        run_one(
            "lns_from_S0_164",
            s0,
            time_s=float(os.environ.get("W3_LNS_S0_TIME", "1800")),
            seed=int(os.environ.get("W3_LNS_S0_SEED", "1201")),
            milp_s=float(os.environ.get("W3_LNS_MILP", "8.0")),
        )
    )
    if rows[-1].get("beats_164"):
        pass
    else:
        # Job B: grow legal then LNS
        g = grow(100, seed=302, mode="boundary_first", seconds=150.0)
        start = [tuple(p) for p in (g.get("points") or [])]
        if len(start) < 100:
            # ensure points present
            from from_scratch_grow import order_candidates
            from src.search.incremental_state import IncrementalIsoscelesFreeSet
            import random

            rng = random.Random(302)
            st = IncrementalIsoscelesFreeSet(100)
            for p in order_candidates(100, rng, "boundary_first"):
                if st.can_add(p)[0]:
                    st.add_point(p)
            # destroy-refill briefly
            t_end = time.time() + 60
            best = sorted(st.points)
            while time.time() < t_end and st.points:
                batch = rng.sample(sorted(st.points), k=min(rng.choice([2, 3, 5]), len(st.points)))
                for p in batch:
                    st.remove_point(p)
                for p in order_candidates(100, rng, "boundary_first"):
                    if st.can_add(p)[0]:
                        st.add_point(p)
                if len(st.points) > len(best):
                    best = sorted(st.points)
            start = best
        print(json.dumps({"grow_start": len(start), "V": g.get("V")}), flush=True)
        rows.append(
            run_one(
                "lns_from_grow_bf302",
                start,
                time_s=float(os.environ.get("W3_LNS_GROW_TIME", "1500")),
                seed=int(os.environ.get("W3_LNS_GROW_SEED", "1302")),
                milp_s=float(os.environ.get("W3_LNS_MILP", "8.0")),
            )
        )

    out = {
        "schema": "w3_lns_from_legal_v1",
        "rows": rows,
        "best_final": max((r["final_size"] for r in rows), default=0),
        "any_plus": any(r.get("beats_164") for r in rows),
    }
    path = os.path.join(exp, "summary.json")
    json.dump(out, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    print(json.dumps({"done": True, "best_final": out["best_final"], "any_plus": out["any_plus"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
