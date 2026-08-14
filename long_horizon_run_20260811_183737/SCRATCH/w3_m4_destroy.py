#!/usr/bin/env python3
"""M4: destroy+refill the dual-OK 147 asymm set (singleton-maximal).
S: n64 forced-asymm half-S0 maximize toward 113.
Outside S0-snap and midset<=139: core is the 147 construction, not S0/parity.
"""
from __future__ import annotations

import json
import os
import random
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from data.baselines.official_raw import SOL_64  # noqa: E402
from w3_new_families_v1 import maximize_core, ring  # noqa: E402
from w3_new_families_v4 import (  # noqa: E402
    CAND,
    EXP,
    S0_HASH_100,
    _asymm_west_core,
    _dump,
    _maybe_promote,
    dual,
)

N, TARGET = 100, 165


def load_147():
    path = os.path.join(EXP, "best_asymm_west.json")
    blob = json.load(open(path, encoding="utf-8"))
    pts = [tuple(p) for p in blob["points"]]
    assert len(pts) >= 147
    return pts, blob


def family_M4(workers: int, per: float) -> dict:
    S, blob = load_147()
    Sset = set(S)
    _, twins = _asymm_west_core()
    rng = random.Random(21)
    pts = sorted(Sset)
    plans = []
    for k, name in ((20, "des20"), (35, "des35"), (50, "des50"), (70, "des70")):
        rem = set(rng.sample(pts, k=min(k, len(pts))))
        core = sorted(Sset - rem)
        plans.append((name + "_keepbl", core, set(twins)))
        plans.append((name + "_nobl", core, None))
    # Structured destroys (not parity/rowband)
    rem = {p for p in Sset if p[0] % 5 == 0}
    plans.append(("colmod5_keepbl", sorted(Sset - rem), set(twins)))
    plans.append(("colmod5_nobl", sorted(Sset - rem), None))
    rem = {p for p in Sset if ring(p, N) <= 4}
    plans.append(("outer4_keepbl", sorted(Sset - rem), set(twins)))
    plans.append(("outer4_nobl", sorted(Sset - rem), None))
    rem = {p for p in Sset if (p[0] + 2 * p[1]) % 5 == 0}
    plans.append(("knight0_keepbl", sorted(Sset - rem), set(twins)))
    plans.append(("knight0_nobl", sorted(Sset - rem), None))

    rows = []
    best = len(S)
    for i, (name, core, bl) in enumerate(plans):
        print(json.dumps({"M4": name, "core": len(core), "bl": 0 if bl is None else len(bl)}), flush=True)
        res = maximize_core(
            N,
            list(core),
            per,
            workers,
            seed=12000 + i,
            target=TARGET,
            blacklist=bl,
            keep_points=True,
            round_s=25.0,
        )
        row = {k: v for k, v in res.items() if k != "points"}
        row["plan"] = name
        if str(res.get("best_hash", "")).startswith(S0_HASH_100):
            row["s0_snap"] = True
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        sz = int(res.get("best_legal_size") or 0)
        if sz > best and res.get("points") and res.get("dual", {}).get("oracle"):
            best = sz
            _dump(os.path.join(EXP, "best_asymm_west.json"), {"points": res["points"], **row, "from": f"M4_{name}"})
        if sz >= TARGET and res.get("points"):
            _maybe_promote(N, TARGET, [tuple(p) for p in res["points"]], f"famM4_{name}")
            break
    out = {
        "schema": "w3_newfam_M4_destroy147_v1",
        "start_hash": blob.get("hash"),
        "start_size": len(S),
        "rows": rows,
        "best": max([best] + [r.get("best_legal_size") or 0 for r in rows]),
        "any_plus": any(r.get("best_legal_size", 0) >= TARGET for r in rows),
        "any_s0_snap": any(r.get("s0_snap") for r in rows),
    }
    _dump(os.path.join(EXP, "family_M4_destroy147.json"), out)
    return out


def family_S_n64(workers: int, per: float) -> dict:
    n, target = 64, 113
    s0 = set((int(x), int(y)) for x, y in SOL_64)
    partner = lambda p: (n - 1 - p[0], n - 1 - p[1])
    keep, bl = set(), set()
    for p in s0:
        q = partner(p)
        if p <= q:
            keep.add(p)
            if q != p and q in s0:
                bl.add(q)
        else:
            bl.add(p)
    rows = []
    plans = [
        ("n64_asymm_keepbl", sorted(keep), bl),
        ("n64_asymm_nobl", sorted(keep), None),
        ("n64_geom_west_bl", sorted(p for p in s0 if p[0] < 32), s0 - {p for p in s0 if p[0] < 32}),
    ]
    for i, (name, core, blacklist) in enumerate(plans):
        print(json.dumps({"S": name, "core": len(core)}), flush=True)
        res = maximize_core(
            n, list(core), per, workers, seed=13000 + i, target=target, blacklist=set(blacklist) if blacklist else None, keep_points=True, round_s=25.0
        )
        row = {k: v for k, v in res.items() if k != "points"}
        row["plan"] = name
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= target and res.get("points"):
            d = dual([tuple(p) for p in res["points"]], n)
            _dump(os.path.join(CAND, f"{name}_legal.json"), {"points": res["points"], **d})
            break
    out = {
        "schema": "w3_newfam_S_n64_asymm_v1",
        "rows": rows,
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= target for r in rows),
    }
    _dump(os.path.join(EXP, "family_S_n64_asymm.json"), out)
    return out


def family_S2(workers: int, max_s: float, lns_s: float) -> dict:
    """Escalate n64 asymm-keepbl (cheap 88, cap=186) toward 113."""
    from src.search.lns import lns_run

    n, target = 64, 113
    s0 = set((int(x), int(y)) for x, y in SOL_64)
    partner = lambda p: (n - 1 - p[0], n - 1 - p[1])
    keep, bl = set(), set()
    for p in s0:
        q = partner(p)
        if p <= q:
            keep.add(p)
            if q != p and q in s0:
                bl.add(q)
        else:
            bl.add(p)
    core = sorted(keep)
    print(json.dumps({"S2": "n64_asymm_keepbl_esc", "core": len(core), "bl": len(bl), "max_s": max_s}), flush=True)
    res = maximize_core(
        n, core, max_s, workers, seed=13101, target=target, blacklist=set(bl), keep_points=True, round_s=90.0
    )
    row = {k: v for k, v in res.items() if k != "points"}
    row["plan"] = "n64_asymm_esc"
    print(json.dumps(row, indent=2), flush=True)
    rows = [row]
    pts = [tuple(p) for p in res["points"]] if res.get("points") else list(core)
    best_sz = int(res.get("best_legal_size") or len(pts))
    if res.get("points"):
        _dump(os.path.join(EXP, "best_n64_asymm.json"), {"points": res["points"], **row})
    if best_sz >= target and res.get("points"):
        d = dual(pts, n)
        if d["oracle"] and d["indep"]:
            _dump(os.path.join(CAND, "n64_asymm_esc_legal.json"), {"points": res["points"], **d})
    elif lns_s > 0 and pts:
        print(json.dumps({"S2_lns": True, "start": len(pts), "budget": lns_s}), flush=True)
        best, meta = lns_run(n, pts, lns_s, seed=13111, destroy_frac_range=(0.15, 0.45))
        d = dual(best, n)
        lns_row = {"plan": "n64_asymm_lns", **{k: v for k, v in meta.items() if k != "improvements"}, **d}
        rows.append(lns_row)
        print(json.dumps(lns_row, indent=2), flush=True)
        if d["oracle"] and d["indep"]:
            _dump(os.path.join(EXP, "best_n64_asymm.json"), {"points": [list(p) for p in best], **d, "from": "lns"})
            if d["size"] >= target:
                _dump(os.path.join(CAND, "n64_asymm_lns_legal.json"), {"points": [list(p) for p in best], **d})
        best_sz = max(best_sz, d.get("size") or 0)
    out = {
        "schema": "w3_newfam_S2_n64_esc_v1",
        "rows": rows,
        "best": best_sz,
        "any_plus": best_sz >= target,
    }
    _dump(os.path.join(EXP, "family_S2_n64_esc.json"), out)
    return out


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    os.makedirs(EXP, exist_ok=True)
    os.makedirs(CAND, exist_ok=True)
    workers = int(os.environ.get("W3_WORKERS", "4"))
    phase = os.environ.get("W3_PHASE", "all")
    per = float(os.environ.get("W3_M4_S", "55"))
    summary = {"schema": "w3_m4s_v1", "phases": {}}
    if phase in ("S", "all"):
        s = family_S_n64(workers, per)
        summary["phases"]["S"] = {"best": s["best"], "any_plus": s["any_plus"]}
        print(json.dumps({"done": "S", **summary["phases"]["S"]}), flush=True)
    if phase in ("M4", "all"):
        m = family_M4(workers, per)
        summary["phases"]["M4"] = {"best": m["best"], "any_plus": m["any_plus"]}
        print(json.dumps({"done": "M4", **summary["phases"]["M4"]}), flush=True)
    if phase in ("S2", "all"):
        s2 = family_S2(
            workers,
            float(os.environ.get("W3_S2_S", "720")),
            float(os.environ.get("W3_S2_LNS_S", "480")),
        )
        summary["phases"]["S2"] = {"best": s2["best"], "any_plus": s2["any_plus"]}
        print(json.dumps({"done": "S2", **summary["phases"]["S2"]}), flush=True)
    summary["any_plus"] = any(p.get("any_plus") for p in summary["phases"].values())
    _dump(os.path.join(EXP, "summary_M4S.json"), summary)
    print(json.dumps({"done_M4S": True, **summary}, indent=2), flush=True)


if __name__ == "__main__":
    main()
