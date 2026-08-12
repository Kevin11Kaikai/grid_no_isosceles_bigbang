#!/usr/bin/env python3
"""Wave3: rem>=3 elite -> strip witnesses -> exact core extend to 165.

Not S0+1 soft grinding. Saves illegal rem3 elites even when V>0, then tries:
  (A) soft core = points not in any witness triple; CP-SAT pick need free cells
  (B) full-involved strip core; CP-SAT over addable-only pool
Scoped INFEAS != global UB. TIMEOUT != INFEAS.
"""
from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(RUN, "SCRATCH"))

from fixedcard_forced_exchange import run_seed  # noqa: E402
from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]
N = 100
TARGET = 165


def sq(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def witnesses(points: Sequence[Point]) -> List[Tuple[Point, Point, Point]]:
    pts = [tuple(p) for p in points]
    out: List[Tuple[Point, Point, Point]] = []
    for pivot in pts:
        groups: Dict[int, List[Point]] = defaultdict(list)
        for q in pts:
            if q == pivot:
                continue
            groups[sq(pivot, q)].append(q)  # type: ignore[arg-type]
        for members in groups.values():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    out.append((pivot, members[i], members[j]))
    return out


def dual(pts: Sequence[Point]) -> dict:
    pts_t = [tuple(p) for p in pts]
    ok_a, _ = is_legal_pivot_method(pts_t, N)
    ok_b, _ = verify_independent(pts_t, N)
    return {
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "V": int(conflict_count(pts_t, N)),
        "size": len(pts_t),
        "hash": sha256_of_points(pts_t),
    }


def make_elite(seed: int, seconds: float, r_min: int = 3) -> dict:
    """Like run_seed but always retains best_pts (patched locally)."""
    import random
    from fixedcard_forced_exchange import init_exchange

    rng = random.Random(seed)
    s0 = [tuple(p) for p in SOL_100]
    s0_set = set(s0)
    pts = init_exchange(s0, rng, r_min=r_min)
    best_v = conflict_count(pts, N)
    best_pts = list(pts)
    t0 = time.time()
    iters = 0
    while time.time() - t0 < seconds:
        iters += 1
        k = rng.choice([1, 2, 3])
        rem_cand = list(pts)
        rng.shuffle(rem_cand)
        remove = rem_cand[:k]
        core = [p for p in pts if p not in set(remove)]
        occ = set(core)
        pool = [(x, y) for x in range(N) for y in range(N) if (x, y) not in occ]
        rng.shuffle(pool)
        st = IncrementalIsoscelesFreeSet(N)
        legal_core = True
        for p in core:
            if not st.add_point(p):
                legal_core = False
                break
        added: List[Point] = []
        if legal_core:
            for p in pool:
                if len(added) >= k:
                    break
                ok, _ = st.can_add(p)
                if ok:
                    st.add_point(p)
                    added.append(p)
        for p in pool:
            if len(added) >= k:
                break
            if p not in set(added) and p not in occ:
                added.append(p)
        new_pts = core + added
        if len(new_pts) != TARGET:
            continue
        if len(s0_set - set(new_pts)) < r_min:
            continue
        v = conflict_count(new_pts, N)
        if v <= best_v:
            pts = new_pts
            if v < best_v:
                best_v = v
                best_pts = list(new_pts)
                if best_v == 0:
                    break
        elif rng.random() < 0.03:
            pts = new_pts
    return {
        "seed": seed,
        "r_min": r_min,
        "best_V": best_v,
        "iters": iters,
        "final_remove_from_s0": len(s0_set - set(best_pts)),
        "final_add": len(set(best_pts) - s0_set),
        "status": "V0_LEGAL" if best_v == 0 else "BEST_V",
        "wall_s": time.time() - t0,
        "points": [list(p) for p in best_pts],
    }


def soft_core(pts: List[Point]) -> Tuple[List[Point], Set[Point], int]:
    wits = witnesses(pts)
    involved: Set[Point] = set()
    for a, b, c in wits:
        involved.update((a, b, c))
    core = sorted(p for p in pts if p not in involved)
    # verify legal
    st = IncrementalIsoscelesFreeSet(N)
    for p in core:
        assert st.add_point(p)
    return core, involved, len(wits)


def addable_pool(core: List[Point]) -> List[Point]:
    st = IncrementalIsoscelesFreeSet(N)
    for p in core:
        assert st.add_point(p)
    pool = []
    occ = set(core)
    for x in range(N):
        for y in range(N):
            p = (x, y)
            if p in occ:
                continue
            ok, _ = st.can_add(p)
            if ok:
                pool.append(p)
    return pool


def exact_extend(
    core: List[Point],
    free: List[Point],
    time_s: float,
    tag: str,
    workers: int = 8,
) -> dict:
    from ortools.sat.python import cp_model

    need = TARGET - len(core)
    t0 = time.time()
    if need <= 0:
        d = dual(core)
        return {
            "tag": tag,
            "status": "ALREADY_LARGE" if d["V"] == 0 else "CORE_ILLEGAL",
            "core_size": len(core),
            "need": need,
            "free": len(free),
            "dual": d,
            "wall_s": 0.0,
        }
    if len(free) < need:
        return {
            "tag": tag,
            "status": "CAPACITY_FAIL",
            "core_size": len(core),
            "need": need,
            "free": len(free),
            "wall_s": 0.0,
        }

    cuts: Set[Tuple[Point, Point, Point]] = set()
    status = "TIMEOUT"
    best_legal = None
    rounds = 0
    while time.time() - t0 < time_s:
        rounds += 1
        model = cp_model.CpModel()
        z = {p: model.NewBoolVar(f"z_{p[0]}_{p[1]}") for p in free}
        model.Add(sum(z.values()) == need)
        for trip in cuts:
            free_in = [z[p] for p in trip if p in z]
            core_in = [p for p in trip if p in set(core)]
            if len(core_in) == 3:
                continue
            if not free_in:
                continue
            model.Add(sum(free_in) <= len(free_in) - 1)
        solver = cp_model.CpSolver()
        rem = max(0.5, time_s - (time.time() - t0))
        solver.parameters.max_time_in_seconds = min(30.0, rem)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = 9300 + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            status = "INFEASIBLE_SCOPED"
            break
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            # Keep searching until wall budget; one UNKNOWN round ≠ campaign TIMEOUT.
            status = "TIMEOUT"
            if rounds % 10 == 0:
                print(
                    json.dumps(
                        {
                            "tag": tag,
                            "round": rounds,
                            "cuts": len(cuts),
                            "note": "round_unknown_continue",
                            "elapsed": time.time() - t0,
                        }
                    ),
                    flush=True,
                )
            continue
        sel = list(core) + [p for p, v in z.items() if solver.Value(v) == 1]
        assert len(sel) == TARGET
        w = witnesses(sel)
        if not w:
            best_legal = sel
            status = "FEASIBLE_LEGAL"
            break
        before = len(cuts)
        for trip in w:
            cuts.add(tuple(sorted(trip)))
        if len(cuts) == before:
            # No progress on cuts — bump seed and continue until wall.
            status = "TIMEOUT"
            if rounds % 10 == 0:
                print(
                    json.dumps(
                        {
                            "tag": tag,
                            "round": rounds,
                            "cuts": len(cuts),
                            "note": "no_new_cuts_continue",
                            "elapsed": time.time() - t0,
                        }
                    ),
                    flush=True,
                )
            continue
        if rounds % 25 == 0:
            print(
                json.dumps(
                    {"tag": tag, "round": rounds, "cuts": len(cuts), "elapsed": time.time() - t0}
                ),
                flush=True,
            )
    out = {
        "tag": tag,
        "status": status,
        "core_size": len(core),
        "need": need,
        "free": len(free),
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_s": time.time() - t0,
        "dual": dual(best_legal) if best_legal else None,
    }
    if best_legal:
        out["points"] = [list(p) for p in best_legal]
    return out


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_rem3_residual")
    os.makedirs(exp, exist_ok=True)
    cand_dir = os.path.join(RUN, "CANDIDATES")
    os.makedirs(cand_dir, exist_ok=True)

    rows = []
    t_all = time.time()
    for seed, soft_s, ext_s in ((802, 240.0, 600.0), (801, 180.0, 420.0)):
        print(json.dumps({"phase": "elite", "seed": seed}), flush=True)
        elite = make_elite(seed, soft_s, r_min=3)
        pts = [tuple(p) for p in elite["points"]]
        elite_path = os.path.join(exp, f"elite_s{seed}_V{elite['best_V']}.json")
        json.dump(elite, open(elite_path, "w", encoding="utf-8"), indent=2)
        open(elite_path, "a", encoding="utf-8").write("\n")
        print(
            json.dumps(
                {
                    "seed": seed,
                    "best_V": elite["best_V"],
                    "rem": elite["final_remove_from_s0"],
                    "add": elite["final_add"],
                }
            ),
            flush=True,
        )
        if elite["best_V"] == 0:
            d = dual(pts)
            if d["oracle_legal"] and d["independent_legal"]:
                cand = os.path.join(cand_dir, f"rem3_elite_s{seed}_legal.json")
                json.dump({"points": [list(p) for p in pts], **d, **elite}, open(cand, "w"), indent=2)
                rows.append({"seed": seed, "status": "V0_DIRECT", "dual": d})
                break

        core, involved, n_w = soft_core(pts)
        pool = addable_pool(core)
        print(
            json.dumps(
                {
                    "seed": seed,
                    "soft_core": len(core),
                    "involved": len(involved),
                    "witnesses": n_w,
                    "addable": len(pool),
                    "need": TARGET - len(core),
                }
            ),
            flush=True,
        )
        # A: soft core + full addable
        a = exact_extend(core, pool, ext_s, tag=f"soft_s{seed}", workers=8)
        a_path = os.path.join(exp, f"soft_extend_s{seed}.json")
        json.dump({k: v for k, v in a.items() if k != "points"}, open(a_path, "w"), indent=2)
        open(a_path, "a").write("\n")
        print(json.dumps({k: v for k, v in a.items() if k != "points"}), flush=True)
        if a.get("status") == "FEASIBLE_LEGAL" and a.get("points"):
            cand = os.path.join(cand_dir, f"rem3_soft_extend_s{seed}_legal.json")
            json.dump(a, open(cand, "w"), indent=2)
            rows.append(a)
            break

        # B: full strip of involved from elite, then addable-restricted
        full_core = sorted(p for p in pts if p not in involved)
        # Actually soft_core already is that. Try larger free: all empties that pass can_add
        # Plus try stripping only high-degree involved (keep low-degree)
        deg: Dict[Point, int] = defaultdict(int)
        for trip in witnesses(pts):
            for p in trip:
                deg[p] += 1
        # keep points with deg <= median among involved
        inv_list = sorted(involved)
        degs = sorted(deg[p] for p in inv_list)
        med = degs[len(degs) // 2] if degs else 0
        partial = sorted(p for p in pts if p not in involved or deg[p] <= max(1, med // 2))
        st = IncrementalIsoscelesFreeSet(N)
        legal_partial = []
        for p in partial:
            if st.can_add(p)[0]:
                st.add_point(p)
                legal_partial.append(p)
        pool2 = addable_pool(legal_partial)
        b = exact_extend(
            legal_partial, pool2, min(ext_s, 420.0), tag=f"partial_s{seed}", workers=8
        )
        b_path = os.path.join(exp, f"partial_extend_s{seed}.json")
        json.dump({k: v for k, v in b.items() if k != "points"}, open(b_path, "w"), indent=2)
        open(b_path, "a").write("\n")
        print(json.dumps({k: v for k, v in b.items() if k != "points"}), flush=True)
        if b.get("status") == "FEASIBLE_LEGAL" and b.get("points"):
            cand = os.path.join(cand_dir, f"rem3_partial_extend_s{seed}_legal.json")
            json.dump(b, open(cand, "w"), indent=2)
            rows.append(b)
            break
        rows.append({"seed": seed, "elite_V": elite["best_V"], "soft": a, "partial": b})

    summary = {
        "schema": "w3_rem3_exact_residual_v1",
        "rows": [{k: v for k, v in r.items() if k != "points"} for r in rows],
        "wall_s": time.time() - t_all,
        "any_legal": any(
            (r.get("status") == "FEASIBLE_LEGAL")
            or (isinstance(r.get("soft"), dict) and r["soft"].get("status") == "FEASIBLE_LEGAL")
            for r in rows
        ),
    }
    path = os.path.join(exp, "summary.json")
    json.dump(summary, open(path, "w", encoding="utf-8"), indent=2)
    open(path, "a", encoding="utf-8").write("\n")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
