#!/usr/bin/env python3
"""Escalate soft rem2 core extend for largest cores (need few adds)."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(RUN, "SCRATCH"))

from w3_rem2_soft_core_extend import (  # noqa: E402
    exact_extend,
    legalize_by_strip,
    witnesses,
)
from collections import Counter


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    src = os.path.join(RUN, "EXPERIMENTS", "LH3_forced_exchange", "seed504_points_v25.json")
    data = json.load(open(src, encoding="utf-8"))
    pts = [tuple(p) for p in data["points"]]
    wits = witnesses(pts)
    pivots = Counter(t[0] for t in wits)
    ranked = [p for p, _ in pivots.most_common()]
    # largest cores: k=5 -> 160, k=10 -> 155
    jobs = [(5, 1800.0), (10, 1200.0)]
    workers = int(os.environ.get("W3_WORKERS", "6"))
    rows = []
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_rem2_residual")
    for k, t in jobs:
        strip = set(ranked[:k])
        core = legalize_by_strip(pts, strip)
        print(json.dumps({"k": k, "core": len(core), "need": 165 - len(core), "time": t}), flush=True)
        res = exact_extend(core, t, workers, seed=9400 + k)
        row = {kk: vv for kk, vv in res.items() if kk != "points"}
        row["k"] = k
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("status") == "FEASIBLE_LEGAL" and res.get("points"):
            cand = os.path.join(RUN, "CANDIDATES", f"rem2_soft_k{k}_long_legal.json")
            json.dump(res, open(cand, "w"), indent=2)
            # dual verify
            from src.verification.oracle_verifier import is_legal_pivot_method
            from src.verification_independent.independent_verifier import verify_independent
            from src.structures.candidate_io import sha256_of_points
            pts2 = [tuple(p) for p in res["points"]]
            ok_a, _ = is_legal_pivot_method(pts2, 100)
            ok_b, _ = verify_independent(pts2, 100)
            print(json.dumps({"dual": {"oracle": ok_a, "indep": ok_b, "hash": sha256_of_points(pts2)}}), flush=True)
            break
    out = {"schema": "w3_rem2_soft_long_v1", "rows": rows, "any_legal": any(r.get("status") == "FEASIBLE_LEGAL" for r in rows)}
    path = os.path.join(exp, "soft_core_extend_long.json")
    json.dump(out, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    print(json.dumps({"done": True, **{k: out[k] for k in ("any_legal",)}}, indent=2), flush=True)


if __name__ == "__main__":
    main()
