#!/usr/bin/env python3
"""Sealed-S0 mechanism tournament.

Does NOT import official baselines or certified coordinates.
Thresholds: n=64 beat 113; n=100 beat 165.
Uses project verifiers A/B only.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from typing import Callable, Dict, List, Optional, Sequence, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.search.lns import lns_run  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]
EXP = os.path.join(RUN, "TOURNAMENT_SEALED", "EXPERIMENTS")
CAND = os.path.join(RUN, "TOURNAMENT_SEALED", "CANDIDATES")
os.makedirs(EXP, exist_ok=True)
os.makedirs(CAND, exist_ok=True)

THRESH = {64: 113, 100: 165}


def dual(pts: Sequence[Point], n: int) -> dict:
    a, _ = is_legal_pivot_method(pts, n)
    b, _ = verify_independent(pts, n)
    return {
        "oracle": bool(a),
        "indep": bool(b),
        "size": len(pts),
        "hash": sha256_of_points(pts),
    }


def legalize_fill(
    n: int,
    seed_pts: Sequence[Point],
    rng: random.Random,
    fill: bool = True,
) -> List[Point]:
    st = IncrementalIsoscelesFreeSet(n)
    order = list(seed_pts)
    rng.shuffle(order)
    for p in order:
        if 0 <= p[0] < n and 0 <= p[1] < n:
            st.add_point(p)
    if fill:
        rest = [(x, y) for x in range(n) for y in range(n)]
        rng.shuffle(rest)
        for p in rest:
            st.add_point(p)
    return sorted(st.points)


def family_A_lookahead(n: int, seed: int, seconds: float) -> List[Point]:
    rng = random.Random(seed)
    st = IncrementalIsoscelesFreeSet(n)
    allp = [(x, y) for x in range(n) for y in range(n)]
    t0 = time.time()
    probe_n = 48 if n >= 64 else 32
    pool_n = 24 if n >= 64 else 16
    while time.time() - t0 < seconds:
        cands = [p for p in allp if p not in st.points and st.can_add(p)[0]]
        if not cands:
            break
        pool = cands if len(cands) <= pool_n else rng.sample(cands, pool_n)
        probe = rng.sample(allp, min(probe_n, len(allp)))
        best_p, best_sc = pool[0], -1
        for p in pool:
            st.add_point(p)
            sc = 0
            for q in probe:
                if q not in st.points and st.can_add(q)[0]:
                    sc += 1
            st.remove_point(p)
            if sc > best_sc:
                best_sc, best_p = sc, p
        st.add_point(best_p)
    return sorted(st.points)


def family_B_algebraic(n: int, seed: int, seconds: float) -> List[Point]:
    rng = random.Random(seed)
    t0 = time.time()
    best: List[Point] = []
    params = []
    for a in range(1, min(n, 9)):
        for b in range(0, min(n, 7)):
            for c in (0, 1, n // 3, n // 2):
                params.append((a, b, c, "parab"))
            params.append((a, b, 0, "line"))
    rng.shuffle(params)
    for a, b, c, kind in params:
        if time.time() - t0 > seconds:
            break
        seed_pts = []
        if kind == "parab":
            for x in range(n):
                y = (a * x * x + b * x + c) % n
                seed_pts.append((x, y))
                seed_pts.append((y, x))
        else:
            for x in range(n):
                seed_pts.append((x, (a * x + b) % n))
                seed_pts.append(((a * x + b) % n, x))
        # unique
        seed_pts = list(dict.fromkeys(seed_pts))
        pts = legalize_fill(n, seed_pts, rng, fill=True)
        if len(pts) > len(best):
            best = pts
    return best


def family_C_scale_lift(n: int, seed: int, seconds: float) -> List[Point]:
    rng = random.Random(seed)
    t0 = time.time()
    best: List[Point] = []
    for m in (6, 8, 10, 12, 16):
        if time.time() - t0 > seconds:
            break
        small = legalize_fill(m, [(x, y) for x in range(m) for y in range(m)], rng, fill=True)
        for ox in range(3):
            for oy in range(3):
                if time.time() - t0 > seconds:
                    break
                lifted = []
                for x, y in small:
                    xx = ox + (x * (n - ox)) // m
                    yy = oy + (y * (n - oy)) // m
                    if 0 <= xx < n and 0 <= yy < n:
                        lifted.append((xx, yy))
                pts = legalize_fill(n, lifted, rng, fill=True)
                if len(pts) > len(best):
                    best = pts
    return best


def family_D_two_per_row(n: int, seed: int, seconds: float) -> List[Point]:
    rng = random.Random(seed)
    t0 = time.time()
    best: List[Point] = []
    while time.time() - t0 < seconds:
        seed_pts: List[Point] = []
        for x in range(n):
            cols = rng.sample(range(n), k=min(3, n))
            for y in cols:
                seed_pts.append((x, y))
        for y in range(n):
            rows = rng.sample(range(n), k=min(2, n))
            for x in rows:
                seed_pts.append((x, y))
        pts = legalize_fill(n, seed_pts, rng, fill=True)
        if len(pts) > len(best):
            best = pts
    return best


def family_E_beam(n: int, seed: int, seconds: float, width: int = 4) -> List[Point]:
    rng = random.Random(seed)
    t0 = time.time()
    allp = [(x, y) for x in range(n) for y in range(n)]
    beams: List[List[Point]] = [[]]
    best: List[Point] = []
    while time.time() - t0 < seconds:
        expanded: List[List[Point]] = []
        for pts in beams:
            st = IncrementalIsoscelesFreeSet(n)
            for p in pts:
                st.add_point(p)
            cands = [p for p in allp if p not in st.points and st.can_add(p)[0]]
            if not cands:
                if len(pts) > len(best):
                    best = pts
                continue
            rng.shuffle(cands)
            for p in cands[:8]:
                expanded.append(pts + [p])
        if not expanded:
            break
        expanded.sort(key=len, reverse=True)
        # diversity: keep widest and a few random
        beams = expanded[:width]
        if len(expanded) > width:
            beams += rng.sample(expanded[width:], k=min(2, len(expanded) - width))
        if len(beams[0]) > len(best):
            best = list(beams[0])
        if len(best) >= n * n:
            break
    # fill leftover on best
    return legalize_fill(n, best, rng, fill=True) if best else []


def maybe_promote(n: int, pts: List[Point], mech: str) -> Optional[str]:
    d = dual(pts, n)
    if not (d["oracle"] and d["indep"]):
        return None
    if d["size"] < THRESH[n]:
        return None
    path = os.path.join(CAND, f"n{n}_k{d['size']}_{mech}_{d['hash'][:12]}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"n": n, "mech": mech, "points": [list(p) for p in pts], **d}, f, indent=2)
        f.write("\n")
    return path


def run_n(n: int, family_seconds: Dict[str, float], lns_s: float) -> dict:
    rng = random.Random(7 + n)
    rows = []
    best_pts: List[Point] = []
    best_mech = None
    fams: List[Tuple[str, Callable]] = [
        ("T-A", lambda: family_A_lookahead(n, 101, family_seconds["T-A"])),
        ("T-B", lambda: family_B_algebraic(n, 202, family_seconds["T-B"])),
        ("T-C", lambda: family_C_scale_lift(n, 303, family_seconds["T-C"])),
        ("T-D", lambda: family_D_two_per_row(n, 404, family_seconds["T-D"])),
        ("T-E", lambda: family_E_beam(n, 505, family_seconds["T-E"])),
    ]
    t_all = time.time()
    for name, fn in fams:
        t0 = time.time()
        print(json.dumps({"start": name, "n": n}), flush=True)
        pts = fn()
        d = dual(pts, n)
        row = {"mech": name, "n": n, **d, "wall_s": time.time() - t0}
        print(json.dumps(row), flush=True)
        rows.append(row)
        promo = maybe_promote(n, pts, name)
        if promo:
            row["candidate"] = promo
        if d["oracle"] and d["indep"] and d["size"] > len(best_pts):
            best_pts = pts
            best_mech = name

    if best_pts and lns_s > 0:
        print(json.dumps({"T-F": "lns", "start": len(best_pts), "from": best_mech}), flush=True)
        t0 = time.time()
        out_pts, meta = lns_run(
            n, list(best_pts), lns_s, seed=909 + n, destroy_frac_range=(0.08, 0.35)
        )
        d = dual(out_pts, n)
        row = {"mech": "T-F", "n": n, **d, "from": best_mech, "lns": meta, "wall_s": time.time() - t0}
        print(json.dumps({k: v for k, v in row.items() if k != "lns"}), flush=True)
        rows.append(row)
        promo = maybe_promote(n, out_pts, "T-F")
        if promo:
            row["candidate"] = promo
        if d["oracle"] and d["indep"] and d["size"] > len(best_pts):
            best_pts = out_pts
            best_mech = "T-F"

    best_d = dual(best_pts, n) if best_pts else {"size": 0}
    summary = {
        "schema": "sealed_tournament_v1",
        "n": n,
        "threshold": THRESH[n],
        "beat": bool(best_d.get("size", 0) >= THRESH[n] and best_d.get("oracle") and best_d.get("indep")),
        "best_size": best_d.get("size", 0),
        "best_mech": best_mech,
        "best_hash": best_d.get("hash"),
        "rows": rows,
        "wall_s": time.time() - t_all,
    }
    if best_pts and best_d.get("oracle"):
        with open(os.path.join(EXP, f"best_n{n}.json"), "w", encoding="utf-8") as f:
            json.dump({"points": [list(p) for p in best_pts], **best_d, "mech": best_mech}, f, indent=2)
            f.write("\n")
    with open(os.path.join(EXP, f"summary_n{n}.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    return summary


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    ns = [int(x) for x in (sys.argv[1:] or ["64", "100"])]
    # Time split: n=64 cheaper sandbox; n=100 more budget.
    budgets = {
        64: {"T-A": 45, "T-B": 40, "T-C": 40, "T-D": 40, "T-E": 35, "lns": 180},
        100: {"T-A": 70, "T-B": 50, "T-C": 50, "T-D": 50, "T-E": 40, "lns": 240},
    }
    merged = {}
    for n in ns:
        b = budgets[n]
        fam = {k: float(b[k]) for k in ("T-A", "T-B", "T-C", "T-D", "T-E")}
        s = run_n(n, fam, lns_s=float(b["lns"]))
        merged[f"n{n}"] = {k: s[k] for k in s if k != "rows"}
        print(json.dumps({"done_n": n, "best": s["best_size"], "beat": s["beat"], "mech": s["best_mech"]}), flush=True)
    with open(os.path.join(EXP, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    print(json.dumps(merged, indent=2), flush=True)


if __name__ == "__main__":
    main()
