#!/usr/bin/env python3
"""Next stretch: (1) joint HS2-pair deletes + global max; (2) grow legal cores + structured destroy/refill."""
from __future__ import annotations

import gzip
import itertools
import json
import os
import random
import sys
import time
from typing import List, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
from w3_global_refill_after_destroy import dual, frame, maximize_from_core  # noqa: E402

Point = Tuple[int, int]
N = 100
DETAIL = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")


def is_vc(edges, hs: Set[Point]) -> bool:
    for e in edges:
        a, b = tuple(e[0]), tuple(e[1])
        if a not in hs and b not in hs:
            return False
    return True


def hs2(edges, involved) -> List[Point] | None:
    verts = [tuple(p) for p in involved]
    for a, b in itertools.combinations(verts, 2):
        if is_vc(edges, {a, b}):
            return sorted([a, b])
    return None


def ring(p: Point) -> int:
    x, y = p
    return min(x, y, N - 1 - x, N - 1 - y)


def grow_legal(seed: int, mode: str, seconds: float) -> dict:
    rng = random.Random(seed)
    cells = [(x, y) for x in range(N) for y in range(N)]
    if mode == "boundary_first":
        cells.sort(key=lambda p: (ring(p), rng.random()))
    elif mode == "spiral_mix":
        cells.sort(key=lambda p: (ring(p) % 3, ring(p), rng.random()))
    else:
        rng.shuffle(cells)
    st = IncrementalIsoscelesFreeSet(N)
    t0 = time.time()
    for p in cells:
        if time.time() - t0 > seconds * 0.45:
            break
        if st.can_add(p)[0]:
            st.add_point(p)
    best = sorted(st.points)
    best_size = len(best)
    iters = 0
    while time.time() - t0 < seconds:
        iters += 1
        if not st.points:
            break
        batch = rng.sample(sorted(st.points), k=min(rng.choice([2, 3, 5, 8]), len(st.points)))
        for p in batch:
            st.remove_point(p)
        refill = list(cells)
        rng.shuffle(refill)
        for p in refill:
            if st.can_add(p)[0]:
                st.add_point(p)
        if len(st.points) > best_size:
            best = sorted(st.points)
            best_size = len(best)
    oka, _ = is_legal_pivot_method(best, N)
    okb, _ = verify_independent(best, N)
    return {
        "size": best_size,
        "seed": seed,
        "mode": mode,
        "iters": iters,
        "oracle": bool(oka),
        "indep": bool(okb),
        "hash": sha256_of_points(best),
        "points": [list(p) for p in best],
    }


def destroy_plans_for(S: Set[Point]):
    plans = []
    for d in (2, 3, 4):
        rem = [p for p in frame(d) if p in S]
        plans.append((f"frame_d{d}", rem))
    # checkerboard parity destroy (even x+y)
    rem = [p for p in S if (p[0] + p[1]) % 2 == 0]
    plans.append(("parity_even", rem))
    rem = [p for p in S if (p[0] + p[1]) % 2 == 1]
    plans.append(("parity_odd", rem))
    # quadrant NW
    rem = [p for p in S if p[0] < N // 2 and p[1] < N // 2]
    plans.append(("quad_NW", rem))
    # mid band rows
    rem = [p for p in S if 40 <= p[1] < 60]
    plans.append(("mid_rows_40_60", rem))
    # random large destroy (seeded)
    rng = random.Random(42)
    pts = sorted(S)
    for k, name in ((20, "rand20"), (40, "rand40"), (60, "rand60")):
        rem = rng.sample(pts, k=min(k, len(pts)))
        plans.append((name, rem))
    return plans


def run_joint_hs(exp_dir: str, workers: int) -> dict:
    s0 = set((int(x), int(y)) for x, y in SOL_100)
    detail = json.load(gzip.open(DETAIL, "rt", encoding="utf-8"))
    easy = [
        r
        for r in detail["top_k_full_records"]
        if int(r["lower_bound_min_deletions"]) == 2 and int(r.get("exact_min_hitting_set") or 0) == 2
    ][:12]
    packed = []
    for r in easy:
        h = hs2(r["blocker_edges"], r["involved_baseline_points"])
        if not h:
            continue
        q = (int(r["q"][0]), int(r["q"][1]))
        packed.append({"q": q, "hs": h})

    rows = []
    # pairs of disjoint HS2 (cap 8)
    stop = False
    for i, a in enumerate(packed):
        if stop:
            break
        for b in packed[i + 1 :]:
            ha, hb = set(map(tuple, a["hs"])), set(map(tuple, b["hs"]))
            if ha & hb:
                continue
            rem = ha | hb
            core = sorted(s0 - rem)
            tag = f"q{a['q'][0]}_{a['q'][1]}__q{b['q'][0]}_{b['q'][1]}"
            print(json.dumps({"joint": tag, "removed": len(rem), "core": len(core)}), flush=True)
            res = maximize_from_core(core, 240.0, workers, seed=1700 + len(rows))
            row = {k: v for k, v in res.items() if k != "points"}
            row.update(
                {
                    "tag": tag,
                    "qs": [list(a["q"]), list(b["q"])],
                    "hs_union": [list(p) for p in sorted(rem)],
                }
            )
            rows.append(row)
            print(json.dumps(row, indent=2), flush=True)
            if res.get("best_legal_size", 0) >= 165 and res.get("dual", {}).get("oracle"):
                path = os.path.join(RUN, "CANDIDATES", f"joint_hs_{tag}_legal.json")
                json.dump(res, open(path, "w"), indent=2)
                stop = True
                break
            if len(rows) >= 8:
                stop = True
                break
    out = {
        "schema": "w3_joint_hs2_delete_max_v1",
        "rows": rows,
        "any_plus": any(r.get("best_legal_size", 0) >= 165 for r in rows),
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
        "n_proved_164": sum(
            1 for r in rows if r.get("proved_max") == 164 and r.get("best_legal_size") == 164
        ),
    }
    json.dump(out, open(os.path.join(exp_dir, "summary.json"), "w"), indent=2)
    return out


def run_grow_destroy(exp_dir: str, workers: int) -> dict:
    grow_rows = []
    best_pts = None
    best_size = 0
    for seed, mode in ((202, "boundary_first"), (203, "spiral_mix"), (301, "boundary_first")):
        g = grow_legal(seed, mode, 120.0)
        grow_rows.append({k: v for k, v in g.items() if k != "points"})
        print(json.dumps({"grow": grow_rows[-1]}), flush=True)
        if g["oracle"] and g["indep"] and g["size"] > best_size:
            best_size = g["size"]
            best_pts = [tuple(p) for p in g["points"]]
            json.dump(g, open(os.path.join(exp_dir, f"grow_seed{seed}_{mode}.json"), "w"), indent=2)

    if not best_pts:
        return {"schema": "w3_grow_destroy_max_v1", "error": "no_legal_grow", "grow_rows": grow_rows}

    S = set(best_pts)
    rows = []
    for name, rem in destroy_plans_for(S):
        if len(rem) == 0:
            continue
        core = sorted(S - set(map(tuple, rem)))
        if len(core) < 80:
            # keep capacity plausible but not tiny
            pass
        print(json.dumps({"plan": name, "removed": len(rem), "core": len(core)}), flush=True)
        res = maximize_from_core(core, 300.0, workers, seed=1800 + len(rows))
        row = {k: v for k, v in res.items() if k != "points"}
        row.update({"plan": name, "n_removed": len(rem), "grow_size": best_size})
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= 165 and res.get("dual", {}).get("oracle"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"grow_destroy_{name}_legal.json"), "w"), indent=2)
            break

    out = {
        "schema": "w3_grow_destroy_max_v1",
        "grow_rows": grow_rows,
        "grow_best_size": best_size,
        "grow_best_hash": sha256_of_points(best_pts),
        "rows": rows,
        "any_plus": any(r.get("best_legal_size", 0) >= 165 for r in rows),
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
    }
    json.dump(out, open(os.path.join(exp_dir, "summary.json"), "w"), indent=2)
    return out


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    workers = int(os.environ.get("W3_WORKERS", "4"))
    phase = os.environ.get("W3_PHASE", "both")  # joint | grow | both

    if phase in ("joint", "both"):
        exp = os.path.join(RUN, "EXPERIMENTS", "W3_joint_hs2_delete_max")
        os.makedirs(exp, exist_ok=True)
        out = run_joint_hs(exp, workers)
        print(json.dumps({"done_joint": True, "best": out["best"], "any_plus": out["any_plus"]}, indent=2), flush=True)

    if phase in ("grow", "both"):
        exp = os.path.join(RUN, "EXPERIMENTS", "W3_grow_destroy_max")
        os.makedirs(exp, exist_ok=True)
        out = run_grow_destroy(exp, workers)
        print(
            json.dumps(
                {
                    "done_grow_destroy": True,
                    "best": out.get("best"),
                    "any_plus": out.get("any_plus"),
                    "grow_best": out.get("grow_best_size"),
                },
                indent=2,
            ),
            flush=True,
        )


if __name__ == "__main__":
    main()
