#!/usr/bin/env python3
"""Longer LNS from dual-verified family-M 147 (asymm west)."""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.search.lns import lns_run  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

SRC = os.path.join(RUN, "EXPERIMENTS", "W3_new_families", "best_asymm_west.json")
EXP = os.path.join(RUN, "EXPERIMENTS", "W3_asymm147_lns")
os.makedirs(EXP, exist_ok=True)
N = 100


def dual(pts):
    a, _ = is_legal_pivot_method(pts, N)
    b, _ = verify_independent(pts, N)
    return {"oracle": bool(a), "indep": bool(b), "size": len(pts), "hash": sha256_of_points(pts)}


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    blob = json.load(open(SRC, encoding="utf-8"))
    pts0 = [tuple(p) for p in blob["points"]]
    d0 = dual(pts0)
    print(json.dumps({"start": d0}), flush=True)
    assert d0["oracle"] and d0["indep"] and d0["size"] == 147
    budget = float(os.environ.get("W3_LNS_S", "1200"))
    rows = []
    best_pts = pts0
    best = 147
    for i, (seed, fr) in enumerate([(21, (0.08, 0.30)), (22, (0.15, 0.45)), (23, (0.20, 0.55))]):
        print(json.dumps({"lns": i, "seed": seed, "frac": fr, "start": best}), flush=True)
        pts, meta = lns_run(N, list(best_pts), budget / 3, seed=seed, destroy_frac_range=fr)
        d = dual(pts)
        row = {**meta, **d, "seed": seed, "frac": fr}
        rows.append(row)
        print(json.dumps({k: row[k] for k in row if k not in ("improvements",)}), flush=True)
        if d["oracle"] and d["indep"] and d["size"] > best:
            best = d["size"]
            best_pts = pts
            json.dump(
                {"points": [list(p) for p in sorted(pts)], **d},
                open(os.path.join(EXP, f"best_k{best}.json"), "w"),
                indent=2,
            )
            if best >= 165:
                json.dump(
                    {"points": [list(p) for p in sorted(pts)], **d},
                    open(os.path.join(RUN, "CANDIDATES", f"asymm_lns_{best}.json"), "w"),
                    indent=2,
                )
                break
    out = {"schema": "w3_asymm147_lns_v1", "rows": rows, "best": best, "any_plus": best >= 165}
    json.dump(out, open(os.path.join(EXP, "summary.json"), "w"), indent=2)
    print(json.dumps({"done": True, "best": best, "any_plus": out["any_plus"]}), flush=True)


if __name__ == "__main__":
    main()
