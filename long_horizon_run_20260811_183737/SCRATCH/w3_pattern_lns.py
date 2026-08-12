#!/usr/bin/env python3
"""Wave3: structured pattern seeds -> greedy legalize -> exact LNS grow toward 165.

Deliberately not S0+1. Uses modular / thick-checker / diag-band patterns.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(RUN, "SCRATCH"))

from pattern_constructions import (  # noqa: E402
    legalize,
    pattern_annulus,
    pattern_checker_thick,
    pattern_diag_bands,
    pattern_modular,
)
from src.search.lns_exact_repair import lns_exact_run  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_pattern_lns")
    os.makedirs(exp, exist_ok=True)
    n = 100
    specs = []
    for c in (5, 7, 8, 9):
        for a, b in ((1, 2), (2, 3), (1, 3)):
            specs.append(("modular", {"a": a, "b": b, "c": c}, pattern_modular(n, a, b, c)))
    for period in (3, 4, 5):
        for phase in (0, 1):
            specs.append(
                (
                    "checker",
                    {"period": period, "phase": phase},
                    pattern_checker_thick(n, period, phase),
                )
            )
    for width in (2, 3, 4):
        specs.append(("diag", {"width": width}, pattern_diag_bands(n, width)))
    for r0, r1 in ((2, 8), (4, 12), (6, 14), (8, 18)):
        specs.append(("annulus", {"r0": r0, "r1": r1}, pattern_annulus(n, r0, r1)))

    # Phase 1: quick legalize screen
    screened = []
    t0 = time.time()
    for i, (kind, params, cells) in enumerate(specs):
        r = legalize(n, cells, seconds=20.0, seed=2000 + i)
        row = {"kind": kind, "params": params, "cand_size": len(cells), **{k: r[k] for k in ("size", "V", "oracle_legal", "independent_legal", "hash")}}
        screened.append((row, r.get("points"), cells))
        print(json.dumps(row), flush=True)
    screened.sort(key=lambda x: x[0]["size"], reverse=True)
    top = screened[:6]
    json.dump(
        {"schema": "w3_pattern_screen_v1", "rows": [t[0] for t in screened], "wall_s": time.time() - t0},
        open(os.path.join(exp, "screen.json"), "w"),
        indent=2,
    )

    # Phase 2: LNS on top starts (rebuild points from legalize if needed)
    lns_rows = []
    for rank, (row, pts_list, cells) in enumerate(top):
        # re-legalize to get points
        r = legalize(n, cells, seconds=45.0, seed=3000 + rank)
        start = [tuple(p) for p in (r.get("points") or [])]
        if not start:
            # legalize didn't store points below threshold — rebuild greedily
            from src.search.incremental_state import IncrementalIsoscelesFreeSet

            rng = random.Random(3000 + rank)
            order = list(cells)
            rng.shuffle(order)
            st = IncrementalIsoscelesFreeSet(n)
            for p in order:
                if st.can_add(p)[0]:
                    st.add_point(p)
            start = sorted(st.points)
        print(
            json.dumps({"phase": "lns", "rank": rank, "start_size": len(start), **row}),
            flush=True,
        )
        best, meta = lns_exact_run(n=n, initial_points=start, time_budget_s=480.0, seed=4000 + rank)
        pts = [tuple(p) for p in best] if best else []
        oka, _ = is_legal_pivot_method(pts, n) if pts else (False, None)
        okb, _ = verify_independent(pts, n) if pts else (False, None)
        out = {
            "rank": rank,
            "kind": row["kind"],
            "params": row["params"],
            "start_size": len(start),
            "final_size": len(pts),
            "oracle": bool(oka),
            "indep": bool(okb),
            "beats_164": len(pts) > 164 and oka and okb,
            "hash": sha256_of_points(pts) if pts else None,
            "meta": {
                k: meta.get(k)
                for k in ("iterations", "improvements", "best_size", "wall_time_s")
                if isinstance(meta, dict)
            },
        }
        lns_rows.append(out)
        print(json.dumps(out), flush=True)
        if out["beats_164"]:
            cand = os.path.join(RUN, "CANDIDATES", f"pattern_lns_{row['kind']}_r{rank}_legal.json")
            json.dump({"points": [list(p) for p in pts], **out}, open(cand, "w"), indent=2)
            break

    summary = {
        "schema": "w3_pattern_lns_v1",
        "screen_best": top[0][0] if top else None,
        "lns_rows": lns_rows,
        "best_final": max((r["final_size"] for r in lns_rows), default=0),
        "any_beats": any(r["beats_164"] for r in lns_rows),
        "wall_s": time.time() - t0,
    }
    path = os.path.join(exp, "summary.json")
    json.dump(summary, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
