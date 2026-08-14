#!/usr/bin/env python3
"""n64 sandbox: unselected addables after k-deletes from official S0."""
from __future__ import annotations

import json
import os
import random
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_64  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402

EXP = os.path.join(RUN, "EXPERIMENTS", "W3_n64_kdelete_unsel")
os.makedirs(EXP, exist_ok=True)
N = 64


def n_unsel(s0_set, T):
    Tset = set(T)
    st = IncrementalIsoscelesFreeSet(N)
    for p in s0_set:
        if p not in Tset:
            assert st.add_point(p)
    c = 0
    pts = []
    for x in range(N):
        for y in range(N):
            p = (x, y)
            if p in st.points or p in Tset:
                continue
            if st.can_add(p)[0]:
                c += 1
                if len(pts) < 8:
                    pts.append(p)
    return c, pts


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    s0 = [tuple(map(int, p)) for p in SOL_64]
    s0_set = set(s0)
    rng = random.Random(13)
    # exact-1 covers from Gate1
    special = [((56, 2),), ((56, 61),), ((56, 2), (56, 61))]
    rows = []
    t0 = time.time()
    for T in special:
        nu, pts = n_unsel(s0_set, T)
        k = len(T)
        row = {"k": k, "recipe": "exact1_cover", "T": [list(p) for p in T], "n_unsel": nu, "pts": pts, "surplus": nu - (k + 1)}
        rows.append(row)
        print(json.dumps(row), flush=True)
    for k in (1, 2, 3, 4, 8, 16):
        for s in range(8):
            T = tuple(rng.sample(s0, k))
            nu, pts = n_unsel(s0_set, T)
            row = {"k": k, "recipe": f"random_s{s}", "n_unsel": nu, "surplus": nu - (k + 1), "pts": pts}
            rows.append(row)
            print(json.dumps({k2: row[k2] for k2 in ("k", "recipe", "n_unsel", "surplus")}), flush=True)
    summary = {
        "max_n_unsel": max(r["n_unsel"] for r in rows),
        "any_surplus_ge0": any(r["surplus"] >= 0 for r in rows),
        "best": max(rows, key=lambda r: (r["surplus"], r["n_unsel"])),
        "rows": rows,
        "wall_s": time.time() - t0,
    }
    with open(os.path.join(EXP, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    print(json.dumps({k: summary[k] for k in ("max_n_unsel", "any_surplus_ge0", "best", "wall_s")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
