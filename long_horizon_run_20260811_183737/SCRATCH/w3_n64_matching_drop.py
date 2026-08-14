#!/usr/bin/env python3
"""n=64 keepbl phase 2: smaller cores.

Phase 1 (w3_n64_matching.py) showed cap up to 218 but core=58 maximize
stuck at 87–90. This drops pairs from the greedy matching (both twins
blacklisted) and also retries the original S unpaired rule (core≈56).
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import List, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from w3_n64_matching import (  # noqa: E402
    CAND,
    EXP,
    N,
    TARGET,
    apply_matching,
    dual,
    dump,
    measure,
    rot180,
    s0_pairs,
)
from w3_new_families_v1 import maximize_core  # noqa: E402
from src.search.lns import lns_run  # noqa: E402

Point = Tuple[int, int]


def s_style_unpaired(pairs, unpaired):
    """Original family-S rule: unpaired p>rot180(p) goes to blacklist, not core."""
    keep_u, bl_u = [], set()
    for p in unpaired:
        q = rot180(p)
        if p <= q:
            keep_u.append(p)
            if q != p:
                bl_u.add(q)
        else:
            bl_u.add(p)
    return keep_u, bl_u


def drop_pairs(keep: List[Point], bl: Set[Point], drop: Sequence[Tuple[Point, Point]]):
    drop_pts = {p for ab in drop for p in ab}
    new_keep = [p for p in keep if p not in drop_pts]
    new_bl = set(bl) | drop_pts
    return new_keep, new_bl


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    pairs, unpaired = s0_pairs()
    greedy_path = os.path.join(EXP, "match_53e522115e3f.json")
    with open(greedy_path, encoding="utf-8") as f:
        spec = json.load(f)
    g_keep = [tuple(p) for p in spec["keep"]]
    g_bl = {tuple(p) for p in spec["bl"]}
    g_bits = spec["bits"]

    plans = []
    # Original S unpaired + lex / greedy bits on pairs only
    ku, bu = s_style_unpaired(pairs, unpaired)
    for name, bits in (("s_lex", [0] * len(pairs)), ("s_greedybits", g_bits)):
        keep, bl = apply_matching(pairs, [], bits)
        keep = sorted(set(keep) | set(ku))
        bl = (bl - set(ku)) | bu
        # remove unpaired from keep if S-rule blacklisted them
        keep = [p for p in keep if p not in bl]
        m = measure(keep, bl)
        plans.append((name, keep, bl, m))

    # Drop k pairs from greedy matching (both twins blacklisted)
    pair_caps = []
    for i, ab in enumerate(pairs):
        k2, b2 = drop_pairs(g_keep, g_bl, [ab])
        m = measure(k2, b2)
        pair_caps.append((m["cap"], i, ab))
    pair_caps.sort(reverse=True)
    for kdrop in (4, 8, 12, 16):
        drop = [ab for _, _, ab in pair_caps[:kdrop]]
        keep, bl = drop_pairs(g_keep, g_bl, drop)
        m = measure(keep, bl)
        plans.append((f"drop{kdrop}", keep, bl, m))

    for name, keep, bl, m in plans:
        print(json.dumps({"plan": name, "core": len(keep), **{k: m[k] for k in ("free", "cap")}}), flush=True)

    workers = 8
    cheap_s = float(os.environ.get("DROP_CHEAP_S", "50"))
    max_rows = []
    best_pts = None
    best_sz = -1
    best_name = None
    best_keep_bl = None
    t0 = time.time()
    # sort by cap descending, take all (6 plans)
    plans.sort(key=lambda t: t[3]["cap"], reverse=True)
    for i, (name, keep, bl, m) in enumerate(plans):
        if m["cap"] < TARGET:
            print(json.dumps({"skip": name, "cap": m["cap"]}), flush=True)
            continue
        print(json.dumps({"maximize": name, "cap": m["cap"], "core": len(keep)}), flush=True)
        res = maximize_core(
            N, keep, cheap_s, workers, seed=66000 + i, target=TARGET, blacklist=bl, keep_points=True, round_s=22.0
        )
        out = {k: v for k, v in res.items() if k != "points"}
        out["plan"] = name
        max_rows.append(out)
        print(json.dumps(out), flush=True)
        sz = int(res.get("best_legal_size") or 0)
        if res.get("points") and sz > best_sz:
            best_sz = sz
            best_pts = [tuple(p) for p in res["points"]]
            best_name = name
            best_keep_bl = (keep, bl)
            dump(os.path.join(EXP, "best_drop.json"), {"points": res["points"], **out})
            d = res.get("dual") or dual(best_pts, N)
            if d.get("oracle") and d.get("indep") and d.get("size", 0) >= TARGET:
                dump(os.path.join(CAND, f"n64_k{d['size']}_drop_{d['hash'][:12]}.json"), {"points": res["points"], **d, "plan": name})
                dump(os.path.join(EXP, "drop_summary.json"), {"best": best_sz, "any_plus": True, "max_rows": max_rows})
                print(json.dumps({"PROMOTE": True, **d}), flush=True)
                return

    esc_s = float(os.environ.get("DROP_ESC_S", "240"))
    if best_pts and best_sz < TARGET and best_keep_bl:
        keep, bl = best_keep_bl
        print(json.dumps({"escalate": best_name, "start": best_sz, "esc_s": esc_s}), flush=True)
        res = maximize_core(
            N, keep, esc_s, workers, seed=66999, target=TARGET, blacklist=bl, keep_points=True, round_s=35.0
        )
        out = {k: v for k, v in res.items() if k != "points"}
        out["plan"] = f"{best_name}_esc"
        max_rows.append(out)
        print(json.dumps(out), flush=True)
        sz = int(res.get("best_legal_size") or 0)
        if res.get("points") and sz >= best_sz:
            best_sz = sz
            best_pts = [tuple(p) for p in res["points"]]
            dump(os.path.join(EXP, "best_drop.json"), {"points": res["points"], **out})

    lns_s = float(os.environ.get("DROP_LNS_S", "150"))
    if best_pts and best_sz < TARGET and lns_s > 0:
        pts, meta = lns_run(N, list(best_pts), lns_s, seed=67001, destroy_frac_range=(0.12, 0.40))
        d = dual(pts, N)
        row = {"plan": "lns", **{k: v for k, v in meta.items() if k != "improvements"}, **d}
        max_rows.append(row)
        print(json.dumps(row), flush=True)
        if d["oracle"] and d["indep"] and d["size"] >= best_sz:
            best_sz = d["size"]
            best_pts = pts
            dump(os.path.join(EXP, "best_drop.json"), {"points": [list(p) for p in pts], **d, "from": "lns"})
            if d["size"] >= TARGET:
                dump(os.path.join(CAND, f"n64_k{d['size']}_drop_{d['hash'][:12]}.json"), {"points": [list(p) for p in pts], **d})

    dump(
        os.path.join(EXP, "drop_summary.json"),
        {
            "schema": "n64_matching_drop_v1",
            "max_rows": max_rows,
            "best": best_sz,
            "best_name": best_name,
            "any_plus": best_sz >= TARGET,
            "wall_s": time.time() - t0,
        },
    )
    print(json.dumps({"done": True, "best": best_sz, "any_plus": best_sz >= TARGET, "name": best_name}), flush=True)


if __name__ == "__main__":
    main()
