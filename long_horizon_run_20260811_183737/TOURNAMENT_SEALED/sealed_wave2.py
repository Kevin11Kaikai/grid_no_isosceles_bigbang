#!/usr/bin/env python3
"""Sealed-S0 tournament wave 2: from-scratch strong mechanisms.

Does NOT import official baselines, certified coordinates, or S0 blocker lists.
Thresholds: n=64 beat 113; n=100 beat 165.
Reuses project verifiers A/B and existing search primitives.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from collections import defaultdict
from typing import Dict, List, Optional, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from ortools.sat.python import cp_model  # noqa: E402
from src.search.cpsat_lazy import cpsat_lazy_maximize  # noqa: E402
from src.search.greedy import greedy_multistart  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.search.lns import lns_run  # noqa: E402
from src.search.symmetry_guided import symmetric_multistart  # noqa: E402
from src.search.tabu import tabu_run  # noqa: E402
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


def rot180(p: Point, n: int) -> Point:
    return (n - 1 - p[0], n - 1 - p[1])


def witnesses(points: Sequence[Point]):
    out = []
    for pivot in points:
        g: Dict[int, List[Point]] = defaultdict(list)
        for q in points:
            if q != pivot:
                dx = pivot[0] - q[0]
                dy = pivot[1] - q[1]
                g[dx * dx + dy * dy].append(q)
        for _, m in g.items():
            if len(m) < 2:
                continue
            for i in range(len(m)):
                for j in range(i + 1, len(m)):
                    out.append((pivot, m[i], m[j]))
    return out


def grow_from_seed(
    n: int,
    seed_pts: Sequence[Point],
    mode: str,
    rng_seed: int,
    cap_size: Optional[int] = None,
) -> List[Point]:
    rng = random.Random(rng_seed)
    st = IncrementalIsoscelesFreeSet(n)
    for p in seed_pts:
        if 0 <= p[0] < n and 0 <= p[1] < n and st.can_add(p)[0]:
            st.add_point(p)
            if cap_size is not None and len(st.points) >= cap_size:
                return sorted(st.points)
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    if mode == "boundary_first":
        cells.sort(key=lambda p: (min(p[0], p[1], n - 1 - p[0], n - 1 - p[1]), rng.random()))
    elif mode == "center_first":
        cells.sort(key=lambda p: (-min(p[0], p[1], n - 1 - p[0], n - 1 - p[1]), rng.random()))
    for p in cells:
        st.add_point(p)
        if cap_size is not None and len(st.points) >= cap_size:
            break
    return sorted(st.points)


def strip_twins(pts: Sequence[Point], n: int) -> List[Point]:
    kept: List[Point] = []
    have: Set[Point] = set()
    for p in sorted(pts):
        if rot180(p, n) in have:
            continue
        have.add(p)
        kept.append(p)
    return kept


def maximize_core(
    n: int,
    core: List[Point],
    time_s: float,
    seed: int,
    target: int,
    blacklist: Optional[Set[Point]] = None,
    pair_at_most_one: Optional[List[Tuple[Point, Point]]] = None,
    round_s: float = 25.0,
    workers: int = 8,
) -> Tuple[List[Point], dict]:
    st = IncrementalIsoscelesFreeSet(n)
    for p in core:
        if not st.add_point(p):
            raise ValueError(f"illegal core at {p}")
    bl = blacklist or set()
    free = [
        (x, y)
        for x in range(n)
        for y in range(n)
        if (x, y) not in st.points and (x, y) not in bl and st.can_add((x, y))[0]
    ]
    meta = {
        "core": len(core),
        "free": len(free),
        "cap": len(core) + len(free),
        "bl": len(bl),
    }
    if not free:
        meta["status"] = "CAPACITY_FAIL"
        return list(core), meta
    cuts: Set[Tuple[Point, Point, Point]] = set()
    t0 = time.time()
    rounds = 0
    best_size = len(core)
    best_pts = list(core)
    lb_extra = 0
    status = "TIMEOUT"
    while time.time() - t0 < time_s:
        rounds += 1
        model = cp_model.CpModel()
        z = {p: model.NewBoolVar(f"z{p[0]}_{p[1]}") for p in free}
        model.Maximize(sum(z.values()))
        if lb_extra > 0:
            model.Add(sum(z.values()) >= lb_extra)
        for trip in cuts:
            free_in = [z[p] for p in trip if p in z]
            if free_in:
                model.Add(sum(free_in) <= len(free_in) - 1)
        if pair_at_most_one:
            for a, b in pair_at_most_one:
                terms = [z[p] for p in (a, b) if p in z]
                if len(terms) == 2:
                    model.Add(sum(terms) <= 1)
        solver = cp_model.CpSolver()
        rem = max(0.5, time_s - (time.time() - t0))
        solver.parameters.max_time_in_seconds = min(round_s, rem)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = seed + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            status = "MAX_PROVED"
            break
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT"
            break
        sel = list(core) + [p for p, v in z.items() if solver.Value(v) == 1]
        w = witnesses(sel)
        if not w:
            if len(sel) > best_size:
                best_size = len(sel)
                best_pts = sel
                print(json.dumps({"new_best": best_size, "round": rounds}), flush=True)
            lb_extra = best_size - len(core) + 1
            if best_size >= target:
                status = "FEASIBLE_GE_TARGET"
                break
            continue
        before = len(cuts)
        for trip in w:
            cuts.add(tuple(sorted(trip)))
        if len(cuts) == before:
            break
    meta.update(
        {
            "status": status,
            "best_legal_size": best_size,
            "rounds": rounds,
            "final_cuts": len(cuts),
            "wall_s": time.time() - t0,
        }
    )
    return best_pts, meta


def family_G_greedy(n: int, seconds: float, seed: int) -> List[Point]:
    pts, meta = greedy_multistart(
        n,
        num_starts=10**9,
        time_budget_s=seconds,
        seed0=seed,
        orders=("random", "boundary_first", "center_first"),
    )
    print(json.dumps({"T-G_meta": {k: meta[k] for k in meta if k != "points"}}), flush=True)
    return sorted(pts)


def family_H_symmetry(n: int, seconds: float, seed: int) -> List[Point]:
    pts, meta = symmetric_multistart(n, seconds, seed=seed)
    print(json.dumps({"T-H_meta": {"final_size": meta.get("final_size"), "trials": meta.get("trials")}}), flush=True)
    return sorted(pts)


def family_I_patterns(n: int, seconds: float, seed: int) -> List[Point]:
    rng = random.Random(seed)
    t0 = time.time()
    best: List[Point] = []
    plans: List[Tuple[str, List[Point], str]] = []
    for r0 in (0, 1, 2):
        seed_pts = [(x, y) for x in range(n) for y in range(n) if (x + 2 * y) % 5 == r0]
        plans.append((f"knight_r{r0}", seed_pts, "boundary_first"))
    for a, b in ((1, 0), (3, 7), (7, 13)):
        seed_pts = [(x, (a * x * x + b) % n) for x in range(n)]
        plans.append((f"quad_a{a}_b{b}", seed_pts, "boundary_first"))
    for k in (3, 7, 11):
        seed_pts = [(x, (k * x) % n) for x in range(n)]
        seed_pts += [(x, (k * x + n // 2) % n) for x in range(0, n, 2)]
        plans.append((f"stair_k{k}", seed_pts, "center_first"))
    for mod, ox, oy in ((3, 0, 0), (3, 1, 2), (4, 0, 1), (5, 0, 0)):
        seed_pts = [(x, y) for x in range(n) for y in range(n) if (x % mod == ox and y % mod == oy)]
        plans.append((f"lat{mod}_{ox}_{oy}", seed_pts, "boundary_first"))
    rng.shuffle(plans)
    for i, (name, seed_pts, mode) in enumerate(plans):
        if time.time() - t0 > seconds:
            break
        pts = grow_from_seed(n, seed_pts, mode, rng_seed=seed + i)
        print(json.dumps({"T-I": name, "size": len(pts)}), flush=True)
        if len(pts) > len(best):
            best = pts
    return best


def family_J_tabu(n: int, start: List[Point], seconds: float, seed: int) -> List[Point]:
    pts, meta = tabu_run(n, list(start), seconds, seed=seed, remove_batch=3)
    print(json.dumps({"T-J_meta": {"final": meta.get("final_size"), "init": meta.get("initial_size"), "iters": meta.get("iterations")}}), flush=True)
    return sorted(pts)


def family_K_asymm_cpsat(n: int, start: List[Point], seconds: float, seed: int) -> List[Point]:
    """Sealed analogue of the 147 basin: medium core + rot180 blacklist + maximize.

    Does not load official coordinates. A maximal greedy core has free≈0;
    keep a fraction of `start` (or a fresh partial grow) so the free set is
    large, then forbid every 180° twin of the kept core.
    """
    rng = random.Random(seed)
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    west_bl = {max(p, rot180(p, n)) for p in all_pts if p != rot180(p, n)}
    plans: List[Tuple[str, List[Point], Set[Point]]] = []
    for frac, tag in ((0.40, "keep40"), (0.55, "keep55"), (0.70, "keep70")):
        core = list(start)
        rng.shuffle(core)
        core = strip_twins(core[: max(16, int(frac * len(core)))], n)
        bl = {rot180(p, n) for p in core if rot180(p, n) != p}
        plans.append((tag, core, bl))
    partial = grow_from_seed(n, [], "boundary_first", seed + 9, cap_size=max(24, n // 2))
    partial = strip_twins(partial, n)
    plans.append(("partial_west", partial, west_bl | {rot180(p, n) for p in partial}))

    best = list(start)
    t0 = time.time()
    per = seconds / max(1, len(plans))
    for i, (name, core, bl) in enumerate(plans):
        rem = seconds - (time.time() - t0)
        if rem < 3:
            break
        pts, meta = maximize_core(
            n,
            core,
            min(per, rem),
            seed=seed + i,
            target=THRESH[n],
            blacklist=bl,
            round_s=25.0,
        )
        print(json.dumps({"T-K": name, **{k: meta[k] for k in meta}}), flush=True)
        if len(pts) > len(best):
            best = pts
    return sorted(best)


def family_L_lazy(n: int, start: List[Point], seconds: float, seed: int) -> List[Point]:
    pts, meta = cpsat_lazy_maximize(
        n,
        time_budget_s=seconds,
        per_round_time_limit_s=min(30.0, max(8.0, seconds / 6.0)),
        seed=seed,
        warm_start_points=list(start),
        seed_cuts_from_warm_start=True,
    )
    print(json.dumps({"T-L_meta": {"best_legal_size": meta.get("best_legal_size"), "rounds": meta.get("rounds")}}), flush=True)
    return sorted(pts) if pts else list(start)


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


def consider(n: int, name: str, pts: List[Point], t0: float, rows: list, best_pts: List[Point], best_mech):
    d = dual(pts, n)
    row = {"mech": name, "n": n, **d, "wall_s": time.time() - t0}
    print(json.dumps(row), flush=True)
    promo = maybe_promote(n, pts, name)
    if promo:
        row["candidate"] = promo
    rows.append(row)
    if d["oracle"] and d["indep"] and d["size"] > len(best_pts):
        return pts, name
    return best_pts, best_mech


def run_n(n: int, budgets: Dict[str, float]) -> dict:
    rows = []
    best_pts: List[Point] = []
    best_mech = None
    t_all = time.time()
    target = THRESH[n]

    t0 = time.time()
    print(json.dumps({"start": "T-G", "n": n}), flush=True)
    pts = family_G_greedy(n, budgets["T-G"], seed=101 + n)
    best_pts, best_mech = consider(n, "T-G", pts, t0, rows, best_pts, best_mech)

    t0 = time.time()
    print(json.dumps({"start": "T-H", "n": n}), flush=True)
    pts = family_H_symmetry(n, budgets["T-H"], seed=202 + n)
    best_pts, best_mech = consider(n, "T-H", pts, t0, rows, best_pts, best_mech)

    t0 = time.time()
    print(json.dumps({"start": "T-I", "n": n}), flush=True)
    pts = family_I_patterns(n, budgets["T-I"], seed=303 + n)
    best_pts, best_mech = consider(n, "T-I", pts, t0, rows, best_pts, best_mech)

    if best_pts and budgets.get("T-J", 0) > 0:
        t0 = time.time()
        print(json.dumps({"start": "T-J", "n": n, "from": best_mech, "size": len(best_pts)}), flush=True)
        pts = family_J_tabu(n, best_pts, budgets["T-J"], seed=404 + n)
        best_pts, best_mech = consider(n, "T-J", pts, t0, rows, best_pts, best_mech)

    if best_pts and budgets.get("T-K", 0) > 0:
        t0 = time.time()
        print(json.dumps({"start": "T-K", "n": n, "from": best_mech, "size": len(best_pts)}), flush=True)
        pts = family_K_asymm_cpsat(n, best_pts, budgets["T-K"], seed=505 + n)
        best_pts, best_mech = consider(n, "T-K", pts, t0, rows, best_pts, best_mech)

    if best_pts and budgets.get("T-L", 0) > 0:
        t0 = time.time()
        print(json.dumps({"start": "T-L", "n": n, "from": best_mech, "size": len(best_pts)}), flush=True)
        pts = family_L_lazy(n, best_pts, budgets["T-L"], seed=606 + n)
        best_pts, best_mech = consider(n, "T-L", pts, t0, rows, best_pts, best_mech)

    if best_pts and budgets.get("T-F", 0) > 0:
        t0 = time.time()
        print(json.dumps({"start": "T-F", "n": n, "from": best_mech, "size": len(best_pts)}), flush=True)
        out_pts, meta = lns_run(
            n, list(best_pts), budgets["T-F"], seed=707 + n, destroy_frac_range=(0.08, 0.35)
        )
        row = {
            "mech": "T-F",
            "n": n,
            **dual(out_pts, n),
            "from": best_mech,
            "lns_final": meta.get("final_size"),
            "lns_iters": meta.get("iterations"),
            "wall_s": time.time() - t0,
        }
        print(json.dumps(row), flush=True)
        promo = maybe_promote(n, out_pts, "T-F")
        if promo:
            row["candidate"] = promo
        rows.append(row)
        d = dual(out_pts, n)
        if d["oracle"] and d["indep"] and d["size"] > len(best_pts):
            best_pts, best_mech = out_pts, "T-F"

    best_d = dual(best_pts, n) if best_pts else {"size": 0, "oracle": False, "indep": False}
    summary = {
        "schema": "sealed_tournament_wave2_v1",
        "n": n,
        "threshold": target,
        "beat": bool(best_d.get("size", 0) >= target and best_d.get("oracle") and best_d.get("indep")),
        "best_size": best_d.get("size", 0),
        "best_mech": best_mech,
        "best_hash": best_d.get("hash"),
        "rows": rows,
        "wall_s": time.time() - t_all,
    }
    if best_pts and best_d.get("oracle"):
        with open(os.path.join(EXP, f"wave2_best_n{n}.json"), "w", encoding="utf-8") as f:
            json.dump(
                {"points": [list(p) for p in best_pts], **best_d, "mech": best_mech},
                f,
                indent=2,
            )
            f.write("\n")
    with open(os.path.join(EXP, f"wave2_summary_n{n}.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    return summary


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    ns = [int(x) for x in (sys.argv[1:] or ["64", "100"])]
    budgets = {
        64: {"T-G": 40, "T-H": 40, "T-I": 35, "T-J": 70, "T-K": 120, "T-L": 90, "T-F": 150},
        100: {"T-G": 50, "T-H": 50, "T-I": 45, "T-J": 90, "T-K": 240, "T-L": 120, "T-F": 240},
    }
    merged = {}
    for n in ns:
        s = run_n(n, {k: float(v) for k, v in budgets[n].items()})
        merged[f"n{n}"] = {k: s[k] for k in s if k != "rows"}
        print(json.dumps({"done_n": n, "best": s["best_size"], "beat": s["beat"], "mech": s["best_mech"]}), flush=True)
    with open(os.path.join(EXP, "wave2_summary.json"), "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    print(json.dumps(merged, indent=2), flush=True)


if __name__ == "__main__":
    main()
