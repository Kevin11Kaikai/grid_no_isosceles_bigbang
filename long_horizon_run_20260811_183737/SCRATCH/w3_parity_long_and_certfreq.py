#!/usr/bin/env python3
"""Escalate large free-pool maximize: long parity from grow core + cert-freq Rem on S0."""
from __future__ import annotations

import gzip
import json
import os
import sys
import time
from collections import Counter
from typing import List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from data.baselines.official_raw import SOL_100  # noqa: E402
from w3_global_refill_after_destroy import maximize_from_core  # noqa: E402

Point = Tuple[int, int]
DETAIL = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    workers = int(os.environ.get("W3_WORKERS", "4"))
    phase = os.environ.get("W3_PHASE", "both")
    rows = []

    if phase in ("parity", "both"):
        exp = os.path.join(RUN, "EXPERIMENTS", "W3_parity_long")
        os.makedirs(exp, exist_ok=True)
        # Prefer saved grow points from prior run
        grow_path = os.path.join(RUN, "EXPERIMENTS", "W3_grow_destroy_max", "grow_seed203_spiral_mix.json")
        g = json.load(open(grow_path))
        S = set(tuple(p) for p in g["points"])
        rem = [p for p in S if (p[0] + p[1]) % 2 == 0]
        core = sorted(S - set(rem))
        print(json.dumps({"plan": "parity_even_long", "core": len(core), "removed": len(rem), "grow": g["size"]}), flush=True)
        res = maximize_from_core(core, 1800.0, workers, seed=1901)
        row = {k: v for k, v in res.items() if k != "points"}
        row["plan"] = "parity_even_long_30m"
        rows.append(row)
        json.dump({"schema": "w3_parity_long_v1", "rows": rows, "grow_hash": g["hash"]}, open(os.path.join(exp, "summary.json"), "w"), indent=2)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= 165 and res.get("points"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", "parity_even_long_legal.json"), "w"), indent=2)

    if phase in ("certfreq", "both"):
        exp = os.path.join(RUN, "EXPERIMENTS", "W3_certfreq_destroy")
        os.makedirs(exp, exist_ok=True)
        s0 = set((int(x), int(y)) for x, y in SOL_100)
        detail = json.load(gzip.open(DETAIL, "rt", encoding="utf-8"))
        ctr = Counter()
        for r in detail["top_k_full_records"]:
            for p in r.get("involved_baseline_points") or []:
                ctr[tuple(p)] += 1
        top = [p for p, _ in ctr.most_common(80)]
        cert_rows = []
        for k in (16, 32, 48, 64):
            rem = [p for p in top[:k] if p in s0]
            core = sorted(s0 - set(rem))
            print(json.dumps({"plan": f"certfreq_top{k}", "removed": len(rem), "core": len(core)}), flush=True)
            # capacity screen first with 120s; escalate interesting ones
            res = maximize_from_core(core, 600.0, workers, seed=2000 + k)
            row = {k2: v for k2, v in res.items() if k2 != "points"}
            row.update({"plan": f"certfreq_top{k}", "n_removed": len(rem)})
            cert_rows.append(row)
            print(json.dumps(row, indent=2), flush=True)
            if res.get("best_legal_size", 0) >= 165 and res.get("dual", {}).get("oracle"):
                json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"certfreq_top{k}_legal.json"), "w"), indent=2)
                break
        out = {
            "schema": "w3_certfreq_destroy_v1",
            "rows": cert_rows,
            "any_plus": any(r.get("best_legal_size", 0) >= 165 for r in cert_rows),
            "best": max((r.get("best_legal_size") or 0) for r in cert_rows) if cert_rows else 0,
        }
        json.dump(out, open(os.path.join(exp, "summary.json"), "w"), indent=2)
        print(json.dumps({"done_certfreq": True, **{k: out[k] for k in ("best", "any_plus")}}, indent=2), flush=True)

    print(json.dumps({"done": True, "phase": phase}, indent=2), flush=True)


if __name__ == "__main__":
    main()
