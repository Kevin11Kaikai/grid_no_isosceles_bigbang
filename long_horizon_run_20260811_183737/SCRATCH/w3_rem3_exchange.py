#!/usr/bin/env python3
"""Wave3: forced rem>=3 fixed-card exchange (leave rem2 residual basin)."""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(RUN, "SCRATCH"))

from fixedcard_forced_exchange import run_seed  # noqa: E402


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_rem3_exchange")
    os.makedirs(exp, exist_ok=True)
    results = []
    t0 = time.time()
    for seed in (801, 802, 803, 804, 805, 806):
        r = run_seed(seed, seconds=150.0, r_min=3)
        results.append({k: v for k, v in r.items() if k != "points"})
        print(json.dumps(results[-1]), flush=True)
        if r.get("status") == "V0_LEGAL" and r.get("points"):
            cand = os.path.join(RUN, "CANDIDATES", f"rem3_ex_s{seed}_legal.json")
            json.dump(r, open(cand, "w"), indent=2)
            break
    out = {
        "schema": "w3_rem3_forced_exchange_v1",
        "results": results,
        "best_V": min(r["best_V"] for r in results) if results else None,
        "any_v0": any(r.get("status") == "V0_LEGAL" for r in results),
        "wall_s": time.time() - t0,
    }
    path = os.path.join(exp, "forced_exchange_rem3.json")
    json.dump(out, open(path, "w"), indent=2)
    open(path, "a").write("\n")
    print(json.dumps({"done": True, "best_V": out["best_V"], "any_v0": out["any_v0"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
