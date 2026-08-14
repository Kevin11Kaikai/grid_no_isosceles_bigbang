#!/usr/bin/env python3
"""Hamming r=3/4 with Rem = min-cover ∪ conflict extras ∪ geo-near S0.

F = S0\\Rem is strictly smaller than the frozen min-cover core, so the
addable-to-F pool can exceed the tight free=3 seen in W3_certcover_max.
Distinct from Wave2 U_small_r2 (score Add) and from frozen-core plus1.

Cheap-kill: 4 symmetry-class representatives, 45s each, r=3 then r=4 if
|Add| allows. INFEASIBLE_SCOPED is scoped to that U_id only.
"""
from __future__ import annotations

import gzip
import importlib.util
import itertools
import json
import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import (  # noqa: E402
    hamming_shell_search,
    universe_hash,
)
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")
EXP = os.path.join(RUN, "EXPERIMENTS", "W3_cover_hamming_r34")
os.makedirs(EXP, exist_ok=True)

REPS = [(0, 43), (3, 17), (4, 1), (24, 18)]


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_h34", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def sq(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def witnesses(points: Sequence[Point]):
    out = []
    for pivot in points:
        g: Dict[int, List[Point]] = defaultdict(list)
        for q in points:
            if q != pivot:
                g[sq(pivot, q)].append(q)
        for _d, m in g.items():
            if len(m) < 2:
                continue
            for i in range(len(m)):
                for j in range(i + 1, len(m)):
                    out.append((pivot, m[i], m[j]))
    return out


def hitting_sets(edges, k):
    verts = sorted({p for e in edges for p in e})
    out = []
    for comb in itertools.combinations(verts, k):
        s = set(comb)
        if all(s & e for e in edges):
            out.append(tuple(sorted(s)))
    return out


def addable_to(n, core):
    st = IncrementalIsoscelesFreeSet(n)
    for p in core:
        assert st.add_point(p)
    cs = set(core)
    free = []
    for x in range(n):
        for y in range(n):
            p = (x, y)
            if p in cs:
                continue
            if st.can_add(p)[0]:
                free.append(p)
    return free


def conflict_core_verts(core, free):
    core_set = set(core)
    verts = set()
    for r in range(1, len(free) + 1):
        for sub in itertools.combinations(free, r):
            pts = list(core) + list(sub)
            for trip in witnesses(pts):
                if any(p in sub for p in trip):
                    for p in trip:
                        if p in core_set:
                            verts.add(p)
    return verts


def first_cover(ba, s0, maps, q):
    rec = ba.analyze_q(q, s0, maps, 100)
    edges = [frozenset((tuple(e[0]), tuple(e[1]))) for e in rec["blocker_edges"]]
    k = rec["exact_min_hitting_set"] or 2
    hs = hitting_sets(edges, int(k))
    return hs[0] if hs else None


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    n = 100
    ba = load_ba()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    maps = ba.precompute_pivot_maps(s0)
    rows = []
    t0 = time.time()
    for q in REPS:
        cov = first_cover(ba, s0, maps, q)
        if cov is None:
            continue
        core_min = sorted(s0_set - set(cov))
        free_min = addable_to(n, core_min)
        extras = conflict_core_verts(core_min, free_min)
        geo = sorted(
            [p for p in s0 if p not in cov],
            key=lambda p: (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2,
        )[:8]
        rem = sorted(set(cov) | extras | set(geo))
        rem_set = set(rem)
        fixed = sorted(s0_set - rem_set)
        add_raw = addable_to(n, fixed)
        add_from_rem = [p for p in add_raw if p in rem_set]
        add = sorted(p for p in add_raw if p not in s0_set)
        uh = universe_hash(rem, add)
        meta = {
            "q": list(q),
            "cover": [list(p) for p in cov],
            "n_rem": len(rem),
            "n_add": len(add),
            "n_add_from_rem": len(add_from_rem),
            "n_fixed": len(fixed),
            "universe_hash": uh,
        }
        print(json.dumps(meta), flush=True)
        for r in (3, 4):
            if r > len(rem) or r + 1 > len(add):
                rows.append({**meta, "r": r, "status": "SKIP_SMALL"})
                continue
            uid = f"U_coverhalo_q{q[0]}_{q[1]}_r{r}"
            ckpt = os.path.join(EXP, f"{uid}.ckpt.json")
            res = hamming_shell_search(
                n=n,
                s0=s0,
                removable=rem,
                addable=add,
                r=r,
                time_budget_s=45.0,
                seed=1,
                u_id=uid,
                universe_hash_str=uh,
                per_round_time_limit_s=15.0,
                num_workers=4,
                checkpoint_path=ckpt,
            )
            row = {
                **meta,
                "r": r,
                "status": res.status,
                "points_n": len(res.points) if res.points else 0,
                "meta": res.meta if isinstance(res.meta, dict) else {},
            }
            if res.points:
                row["cand_hash"] = sha256_of_points(res.points)
                row["cand_size"] = len(res.points)
            rows.append(row)
            print(json.dumps({k: v for k, v in row.items() if k != "meta"}), flush=True)
            payload = {"row": row, "meta_full": res.meta, "points": res.points}
            with open(os.path.join(EXP, f"{uid}.json"), "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
                f.write("\n")
            if res.status in ("FEASIBLE", "OPTIMAL") or (res.points and len(res.points) >= 165):
                cand = os.path.join(RUN, "CANDIDATES", f"{uid}_k{len(res.points)}.json")
                with open(cand, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2, default=str)
                    f.write("\n")
                break

    summary = {
        "schema": "w3_cover_hamming_r34_v1",
        "rows": rows,
        "any_plus": any((r.get("cand_size") or 0) >= 165 for r in rows),
        "statuses": [r.get("status") for r in rows],
        "wall_s": time.time() - t0,
    }
    with open(os.path.join(EXP, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    print(json.dumps({k: summary[k] for k in ("any_plus", "statuses", "wall_s")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
