#!/usr/bin/env python3
"""Wave3 new destroy+refill families (outside S0-snap / midset≤139 / forbid-rand).

Families:
  A) Ring-band Rem from S0 + blacklist maximize
  B) Column-mod / diagonal-band Rem + blacklist maximize
  C) Modular-lattice seed → grow → global maximize (no S0)
  D) Intersection-core of two diverse grows → maximize
  E) n64 structured destroy+refill allowing re-add (F067 only tested forbid)
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
from data.baselines.official_raw import SOL_64, SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402

Point = Tuple[int, int]


def ring(p: Point, n: int) -> int:
    x, y = p
    return min(x, y, n - 1 - x, n - 1 - y)


def sq(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def witnesses(points: Sequence[Point]):
    out = []
    for pivot in points:
        g: Dict[int, List[Point]] = defaultdict(list)
        for q in points:
            if q != pivot:
                g[sq(pivot, q)].append(q)
        for _, m in g.items():
            if len(m) < 2:
                continue
            for i in range(len(m)):
                for j in range(i + 1, len(m)):
                    out.append((pivot, m[i], m[j]))
    return out


def dual(pts: Sequence[Point], n: int) -> dict:
    oka, _ = is_legal_pivot_method(pts, n)
    okb, _ = verify_independent(pts, n)
    return {"oracle": bool(oka), "indep": bool(okb), "size": len(pts), "hash": sha256_of_points(pts)}


def maximize_core(
    n: int,
    core: List[Point],
    time_s: float,
    workers: int,
    seed: int,
    target: int,
    blacklist: Optional[Set[Point]] = None,
    keep_points: bool = False,
    round_s: float = 30.0,
) -> dict:
    st = IncrementalIsoscelesFreeSet(n)
    for p in core:
        assert st.add_point(p)
    bl = blacklist or set()
    free = [
        (x, y)
        for x in range(n)
        for y in range(n)
        if (x, y) not in st.points and (x, y) not in bl and st.can_add((x, y))[0]
    ]
    print(
        json.dumps(
            {"core": len(core), "free": len(free), "cap": len(core) + len(free), "bl": len(bl)}
        ),
        flush=True,
    )
    if len(core) + len(free) < target:
        return {
            "status": "CAPACITY_FAIL",
            "core": len(core),
            "free": len(free),
            "best_legal_size": len(core),
            "proved_max": len(core) + len(free),
        }
    cuts: Set[Tuple[Point, Point, Point]] = set()
    t0 = time.time()
    rounds = 0
    best_size = len(core)
    best_pts = list(core)
    lb_extra = 0
    status = "TIMEOUT"
    proved_max = None
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
        solver = cp_model.CpSolver()
        rem = max(0.5, time_s - (time.time() - t0))
        solver.parameters.max_time_in_seconds = min(round_s, rem)
        solver.parameters.num_search_workers = workers
        solver.parameters.random_seed = seed + rounds
        code = solver.Solve(model)
        if code == cp_model.INFEASIBLE:
            proved_max = best_size
            status = "MAX_PROVED"
            break
        if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            status = "TIMEOUT"
            if lb_extra > 0 and time.time() - t0 < time_s - 5:
                continue
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
        if len(cuts) == before and time.time() - t0 >= time_s - 5:
            break
    out = {
        "status": status,
        "core": len(core),
        "free": len(free),
        "best_legal_size": best_size,
        "proved_max": proved_max,
        "rounds": rounds,
        "final_cuts": len(cuts),
        "wall_s": time.time() - t0,
    }
    if best_pts and (best_size > len(core) or best_size >= target or keep_points):
        out["dual"] = dual(best_pts, n)
        out["best_hash"] = out["dual"]["hash"]
    if best_pts and (keep_points or (best_size >= target and out.get("dual", {}).get("oracle") and out.get("dual", {}).get("indep"))):
        out["points"] = [list(p) for p in best_pts]
    return out


def grow_from_seed(n: int, seed_pts: List[Point], mode: str, seconds: float, rng_seed: int) -> dict:
    rng = random.Random(rng_seed)
    st = IncrementalIsoscelesFreeSet(n)
    for p in seed_pts:
        if st.can_add(p)[0]:
            st.add_point(p)
    cells = [(x, y) for x in range(n) for y in range(n)]
    if mode == "boundary_first":
        cells.sort(key=lambda p: (ring(p, n), rng.random()))
    elif mode == "center_first":
        cells.sort(key=lambda p: (-ring(p, n), rng.random()))
    else:
        rng.shuffle(cells)
    t0 = time.time()
    for p in cells:
        if time.time() - t0 > seconds * 0.45:
            break
        if st.can_add(p)[0]:
            st.add_point(p)
    best = sorted(st.points)
    best_size = len(best)
    while time.time() - t0 < seconds:
        if not st.points:
            break
        batch = rng.sample(sorted(st.points), k=min(rng.choice([2, 3, 5]), len(st.points)))
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
    d = dual(best, n)
    return {
        "size": best_size,
        "oracle": d["oracle"],
        "indep": d["indep"],
        "hash": d["hash"],
        "points": [list(p) for p in best],
        "seed_size": len(seed_pts),
        "mode": mode,
    }


def lattice_seed(n: int, mod: int, ox: int, oy: int) -> List[Point]:
    return [(x, y) for x in range(ox, n, mod) for y in range(oy, n, mod)]


def family_A_B_n100(workers: int, per: float) -> dict:
    s0 = set((int(x), int(y)) for x, y in SOL_100)
    n, target = 100, 165
    plans = []
    # Ring bands: remove outer / mid / inner rings
    for name, pred in [
        ("ring_outer_le5", lambda p: ring(p, n) <= 5),
        ("ring_mid_6_15", lambda p: 6 <= ring(p, n) <= 15),
        ("ring_inner_ge16", lambda p: ring(p, n) >= 16),
        ("ring_odd", lambda p: ring(p, n) % 2 == 1),
        ("ring_even", lambda p: ring(p, n) % 2 == 0),
    ]:
        rem = [p for p in s0 if pred(p)]
        core = sorted(s0 - set(rem))
        plans.append((name, core, set(rem)))
    # Column-mod / diagonal
    for r in (0, 1, 2):
        rem = [p for p in s0 if p[0] % 3 == r]
        plans.append((f"colmod3_r{r}", sorted(s0 - set(rem)), set(rem)))
    for r in (0, 1):
        rem = [p for p in s0 if (p[0] + p[1]) % 4 == r]
        # note: x+y mod 4 is finer than parity_even (mod 2) — different kernel
        plans.append((f"diagmod4_r{r}", sorted(s0 - set(rem)), set(rem)))
    rem = [p for p in s0 if abs(p[0] - p[1]) <= 12]
    plans.append(("diagband_le12", sorted(s0 - set(rem)), set(rem)))

    rows = []
    for i, (name, core, bl) in enumerate(plans):
        if len(core) < 40:
            rows.append({"plan": name, "status": "SKIP_SMALL_CORE", "core": len(core)})
            continue
        print(json.dumps({"family": "AB", "plan": name, "core": len(core), "bl": len(bl)}), flush=True)
        res = maximize_core(n, core, per, workers, seed=1000 + i, target=target, blacklist=bl)
        row = {k: v for k, v in res.items() if k != "points"}
        row["plan"] = name
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= target and res.get("points"):
            path = os.path.join(RUN, "CANDIDATES", f"famAB_{name}_legal.json")
            json.dump(res, open(path, "w"), indent=2)
            break
    return {
        "schema": "w3_newfam_AB_v1",
        "rows": rows,
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= target for r in rows),
    }


def family_C_lattice(workers: int, grow_s: float, max_s: float) -> dict:
    n, target = 100, 165
    rows = []
    best_legal = None
    for mod, ox, oy, mode in [
        (3, 0, 0, "boundary_first"),
        (3, 1, 2, "boundary_first"),
        (4, 0, 1, "center_first"),
        (5, 0, 0, "boundary_first"),
        (5, 2, 3, "spiral"),
    ]:
        seed = lattice_seed(n, mod, ox, oy)
        # CheapKill: if raw lattice already illegal, filter greedily
        st = IncrementalIsoscelesFreeSet(n)
        kept = []
        for p in seed:
            if st.can_add(p)[0]:
                st.add_point(p)
                kept.append(p)
        print(json.dumps({"family": "C", "mod": mod, "ox": ox, "oy": oy, "seed_kept": len(kept)}), flush=True)
        g = grow_from_seed(n, kept, mode if mode != "spiral" else "boundary_first", grow_s, rng_seed=2000 + mod * 10 + ox)
        grow_row = {k: v for k, v in g.items() if k != "points"}
        grow_row.update({"mod": mod, "ox": ox, "oy": oy})
        print(json.dumps({"grow": grow_row}), flush=True)
        if not (g["oracle"] and g["indep"]):
            rows.append({"plan": f"lat{mod}_{ox}_{oy}", "status": "GROW_ILLEGAL", **grow_row})
            continue
        pts = [tuple(p) for p in g["points"]]
        if best_legal is None or g["size"] > best_legal["size"]:
            best_legal = g
        # Global maximize from this core (no blacklist) — leave S0 entirely
        res = maximize_core(n, pts, max_s, workers, seed=3000 + mod * 10 + ox, target=target, blacklist=None)
        row = {k: v for k, v in res.items() if k != "points"}
        row.update({"plan": f"lat{mod}_{ox}_{oy}_{mode}", "grow_size": g["size"], "grow_hash": g["hash"]})
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= target and res.get("points"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"famC_lat{mod}_legal.json"), "w"), indent=2)
            break
    out = {
        "schema": "w3_newfam_C_v1",
        "rows": rows,
        "best": max((r.get("best_legal_size") or r.get("grow_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= target for r in rows),
    }
    if best_legal:
        out["best_grow"] = {k: v for k, v in best_legal.items() if k != "points"}
        json.dump(best_legal, open(os.path.join(RUN, "EXPERIMENTS", "W3_new_families", "best_lattice_grow.json"), "w"), indent=2)
    return out


def family_D_intersection(workers: int, grow_s: float, max_s: float) -> dict:
    n, target = 100, 165
    grows = []
    for seed, mode in [(501, "boundary_first"), (502, "center_first"), (503, "random"), (504, "boundary_first")]:
        g = grow_from_seed(n, [], mode, grow_s, rng_seed=seed)
        print(json.dumps({"family": "D", "grow": {k: v for k, v in g.items() if k != "points"}}), flush=True)
        if g["oracle"] and g["indep"]:
            grows.append(g)
    rows = []
    for i in range(len(grows)):
        for j in range(i + 1, len(grows)):
            A = set(map(tuple, grows[i]["points"]))
            B = set(map(tuple, grows[j]["points"]))
            inter = sorted(A & B)
            uni = A | B
            print(
                json.dumps(
                    {
                        "pair": f"{grows[i]['hash'][:8]}_{grows[j]['hash'][:8]}",
                        "inter": len(inter),
                        "union": len(uni),
                    }
                ),
                flush=True,
            )
            if len(inter) < 30:
                rows.append({"plan": f"inter_{i}_{j}", "status": "SKIP_SMALL_INTER", "inter": len(inter)})
                continue
            # Maximize with free pool = individually addable; warm bias via union not enforced
            res = maximize_core(n, inter, max_s, workers, seed=4000 + i * 10 + j, target=target, blacklist=None)
            row = {k: v for k, v in res.items() if k != "points"}
            row.update(
                {
                    "plan": f"inter_{i}_{j}",
                    "inter": len(inter),
                    "union": len(uni),
                    "sizes": [grows[i]["size"], grows[j]["size"]],
                }
            )
            rows.append(row)
            print(json.dumps(row, indent=2), flush=True)
            if res.get("best_legal_size", 0) >= target and res.get("points"):
                json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"famD_inter_{i}_{j}_legal.json"), "w"), indent=2)
                return {
                    "schema": "w3_newfam_D_v1",
                    "rows": rows,
                    "best": res["best_legal_size"],
                    "any_plus": True,
                }
    return {
        "schema": "w3_newfam_D_v1",
        "rows": rows,
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= target for r in rows),
    }


def family_E_n64(workers: int, per: float) -> dict:
    s0 = set((int(x), int(y)) for x, y in SOL_64)
    n, target = 64, 113
    rows = []
    plans = []
    for name, pred in [
        ("ring_outer_le4", lambda p: ring(p, n) <= 4),
        ("ring_odd", lambda p: ring(p, n) % 2 == 1),
        ("colmod3_r0", lambda p: p[0] % 3 == 0),
        ("diagmod4_r0", lambda p: (p[0] + p[1]) % 4 == 0),
    ]:
        rem = [p for p in s0 if pred(p)]
        core = sorted(s0 - set(rem))
        plans.append((name + "_readd", core, None))  # allow re-add
        plans.append((name + "_forbid", core, set(rem)))
    for i, (name, core, bl) in enumerate(plans):
        print(json.dumps({"family": "E", "plan": name, "core": len(core)}), flush=True)
        res = maximize_core(n, core, per, workers, seed=5000 + i, target=target, blacklist=bl)
        row = {k: v for k, v in res.items() if k != "points"}
        row["plan"] = name
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= target and res.get("points"):
            json.dump(res, open(os.path.join(RUN, "CANDIDATES", f"famE_n64_{name}_legal.json"), "w"), indent=2)
            break
    return {
        "schema": "w3_newfam_E_n64_v1",
        "rows": rows,
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= target for r in rows),
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    workers = int(os.environ.get("W3_WORKERS", "4"))
    phase = os.environ.get("W3_PHASE", "all")  # AB|C|D|E|all
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_new_families")
    os.makedirs(exp, exist_ok=True)
    summary = {"schema": "w3_new_families_v1", "phases": {}}

    if phase in ("AB", "all"):
        ab = family_A_B_n100(workers, per=float(os.environ.get("W3_AB_S", "180")))
        json.dump(ab, open(os.path.join(exp, "family_AB.json"), "w"), indent=2)
        summary["phases"]["AB"] = {"best": ab["best"], "any_plus": ab["any_plus"]}
        print(json.dumps({"done_AB": True, **summary["phases"]["AB"]}), flush=True)

    if phase in ("C", "all"):
        c = family_C_lattice(
            workers,
            grow_s=float(os.environ.get("W3_GROW_S", "90")),
            max_s=float(os.environ.get("W3_C_S", "300")),
        )
        json.dump(c, open(os.path.join(exp, "family_C.json"), "w"), indent=2)
        summary["phases"]["C"] = {"best": c["best"], "any_plus": c["any_plus"]}
        print(json.dumps({"done_C": True, **summary["phases"]["C"]}), flush=True)

    if phase in ("D", "all"):
        d = family_D_intersection(
            workers,
            grow_s=float(os.environ.get("W3_GROW_S", "90")),
            max_s=float(os.environ.get("W3_D_S", "300")),
        )
        json.dump(d, open(os.path.join(exp, "family_D.json"), "w"), indent=2)
        summary["phases"]["D"] = {"best": d["best"], "any_plus": d["any_plus"]}
        print(json.dumps({"done_D": True, **summary["phases"]["D"]}), flush=True)

    if phase in ("E", "all"):
        e = family_E_n64(workers, per=float(os.environ.get("W3_E_S", "180")))
        json.dump(e, open(os.path.join(exp, "family_E_n64.json"), "w"), indent=2)
        summary["phases"]["E"] = {"best": e["best"], "any_plus": e["any_plus"]}
        print(json.dumps({"done_E": True, **summary["phases"]["E"]}), flush=True)

    summary["any_plus"] = any(p.get("any_plus") for p in summary["phases"].values())
    summary["best_n100"] = max(
        (summary["phases"].get(k, {}).get("best") or 0) for k in ("AB", "C", "D")
    )
    json.dump(summary, open(os.path.join(exp, "summary.json"), "w"), indent=2)
    print(json.dumps({"done_all": True, **summary}, indent=2), flush=True)


if __name__ == "__main__":
    main()
