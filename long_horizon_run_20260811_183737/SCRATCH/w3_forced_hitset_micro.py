#!/usr/bin/env python3
"""Wave3 exact microproblem: force delete an exact size-2 hitting set for q, seek |S|=165.

For each easiest LB=2 q with exact_min_hitting_set==2:
  compute a concrete size-2 vertex cover of blocker_edges (exact HS),
  Rem = that HS (size 2)  [r=2 forces deleting both],
  Add = {q} ∪ (LB<=8 qs) ∪ Chebyshev-halo around HS∪{q},
  run Hamming r=2 CP-SAT (cheap then escalate TIMEOUT).

This is certificate-driven and forces remove>=2 (not S0+1 soft).
"""
from __future__ import annotations

import gzip
import itertools
import json
import os
import sys
import time
from typing import List, Optional, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402

Point = Tuple[int, int]
N = 100
DETAIL = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")


def is_vertex_cover(edges: Sequence[Sequence[Sequence[int]]], hs: Set[Point]) -> bool:
    for e in edges:
        a, b = tuple(e[0]), tuple(e[1])
        if a not in hs and b not in hs:
            return False
    return True


def find_exact_hs2(edges: Sequence[Sequence[Sequence[int]]], involved: Sequence[Sequence[int]]) -> Optional[List[Point]]:
    verts = [tuple(p) for p in involved]
    # try all pairs among involved
    for a, b in itertools.combinations(verts, 2):
        if is_vertex_cover(edges, {a, b}):
            return sorted([a, b])
    # also try single? shouldn't for LB=2
    return None


def halo(points: Sequence[Point], radius: int, forbidden: Set[Point]) -> List[Point]:
    out: Set[Point] = set()
    for x, y in points:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if max(abs(dx), abs(dy)) > radius:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < N and 0 <= ny < N:
                    p = (nx, ny)
                    if p not in forbidden:
                        out.add(p)
    return sorted(out)


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_forced_hitset")
    os.makedirs(exp, exist_ok=True)
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    with gzip.open(DETAIL, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    top = detail["top_k_full_records"]
    compact = detail["all_qs_compact"]
    lb8 = [
        (int(r["q"][0]), int(r["q"][1]))
        for r in compact
        if int(r["lower_bound_min_deletions"]) <= 8
        and (int(r["q"][0]), int(r["q"][1])) not in s0_set
    ]
    easy = [r for r in top if int(r["lower_bound_min_deletions"]) == 2 and int(r.get("exact_min_hitting_set") or 0) == 2]
    workers = int(os.environ.get("W3_WORKERS", "3"))
    cheap = float(os.environ.get("W3_CHEAP_S", "90"))
    rows = []
    # Cap: first 8 qs for cheap-kill diversity
    for idx, rec in enumerate(easy[:8]):
        q = (int(rec["q"][0]), int(rec["q"][1]))
        hs = find_exact_hs2(rec["blocker_edges"], rec["involved_baseline_points"])
        if hs is None:
            rows.append({"q": list(q), "status": "ERROR_NO_HS2"})
            print(json.dumps(rows[-1]), flush=True)
            continue
        rem = hs  # exactly 2
        add_set = set(lb8)
        add_set.add(q)
        add_set.update(halo(hs + [q], 3, s0_set))
        add = sorted(add_set)
        uh = universe_hash(rem, add)
        u_id = f"U_forced_hs2_q{q[0]}_{q[1]}_r2"
        print(
            json.dumps(
                {
                    "start": u_id,
                    "hs": [list(p) for p in hs],
                    "n_add": len(add),
                    "hash": uh[:16],
                }
            ),
            flush=True,
        )
        t0 = time.time()
        result = hamming_shell_search(
            n=N,
            s0=s0,
            removable=rem,
            addable=add,
            r=2,
            time_budget_s=cheap,
            seed=1000 + idx,
            u_id=u_id,
            universe_hash_str=uh,
            per_round_time_limit_s=20.0,
            num_workers=workers,
            symmetry_mode="asymmetric",
        )
        out = {
            "U_id": u_id,
            "q": list(q),
            "hs": [list(p) for p in hs],
            "status": result.status,
            "universe_hash": uh,
            "n_rem": len(rem),
            "n_add": len(add),
            "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
            "rounds": (result.meta or {}).get("rounds"),
            "final_cuts": (result.meta or {}).get("final_cuts"),
            "wall_time_s": time.time() - t0,
            "points": [list(p) for p in result.points] if result.points else None,
        }
        with open(os.path.join(exp, f"{u_id}.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, sort_keys=True)
            f.write("\n")
        rows.append({k: out[k] for k in out if k != "points"})
        print(json.dumps(rows[-1], indent=2), flush=True)
        if out["status"] == "FEASIBLE_LEGAL" and out.get("points"):
            os.makedirs(os.path.join(RUN, "CANDIDATES"), exist_ok=True)
            with open(
                os.path.join(RUN, "CANDIDATES", f"{u_id}_legal.json"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(out, f, indent=2)
            break  # stop on first legal

    summary = {
        "schema": "w3_forced_hitset_v1",
        "n_tried": len(rows),
        "any_legal": any(r.get("status") == "FEASIBLE_LEGAL" for r in rows),
        "status_counts": {},
        "rows": rows,
    }
    for r in rows:
        st = r.get("status", "?")
        summary["status_counts"][st] = summary["status_counts"].get(st, 0) + 1
    with open(os.path.join(exp, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"done": True, **{k: summary[k] for k in ("n_tried", "any_legal", "status_counts")}}, indent=2), flush=True)


if __name__ == "__main__":
    main()
