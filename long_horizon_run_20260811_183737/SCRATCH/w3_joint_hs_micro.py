#!/usr/bin/env python3
"""Wave3: joint exact-HS microproblem for pairs of easiest qs.

For pairs among first 6 LB=2 qs:
  Rem = HS(q1) ∪ HS(q2)  (expect |Rem| in {3,4})
  r = |Rem|  (force delete the whole joint cover)
  Add = {q1,q2} ∪ LB<=8 ∪ halo
Cheap-kill; stop early if legal.
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


def is_vc(edges, hs: Set[Point]) -> bool:
    for e in edges:
        a, b = tuple(e[0]), tuple(e[1])
        if a not in hs and b not in hs:
            return False
    return True


def hs2(edges, involved) -> Optional[List[Point]]:
    verts = [tuple(p) for p in involved]
    for a, b in itertools.combinations(verts, 2):
        if is_vc(edges, {a, b}):
            return sorted([a, b])
    return None


def halo(points, radius, forbidden):
    out = set()
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
    return out


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_joint_hs")
    os.makedirs(exp, exist_ok=True)
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    with gzip.open(DETAIL, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    easy = [
        r
        for r in detail["top_k_full_records"]
        if int(r["lower_bound_min_deletions"]) == 2 and int(r.get("exact_min_hitting_set") or 0) == 2
    ][:6]
    prepared = []
    for r in easy:
        q = (int(r["q"][0]), int(r["q"][1]))
        h = hs2(r["blocker_edges"], r["involved_baseline_points"])
        if h:
            prepared.append((q, h, r))
    lb8 = [
        (int(r["q"][0]), int(r["q"][1]))
        for r in detail["all_qs_compact"]
        if int(r["lower_bound_min_deletions"]) <= 8
        and (int(r["q"][0]), int(r["q"][1])) not in s0_set
    ]
    workers = int(os.environ.get("W3_WORKERS", "3"))
    cheap = float(os.environ.get("W3_CHEAP_S", "120"))
    rows = []
    # Sample up to 10 pairs
    pairs = list(itertools.combinations(range(len(prepared)), 2))[:10]
    for i, j in pairs:
        q1, h1, _ = prepared[i]
        q2, h2, _ = prepared[j]
        rem = sorted(set(h1) | set(h2))
        r_del = len(rem)
        if r_del < 2 or r_del > 6:
            continue
        add = set(lb8)
        add.add(q1)
        add.add(q2)
        add |= halo(rem + [q1, q2], 3, s0_set)
        add_l = sorted(add)
        uh = universe_hash(rem, add_l)
        u_id = f"U_joint_hs_q{q1[0]}_{q1[1]}__q{q2[0]}_{q2[1]}_r{r_del}"
        print(
            json.dumps(
                {
                    "start": u_id,
                    "r": r_del,
                    "n_rem": len(rem),
                    "n_add": len(add_l),
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
            addable=add_l,
            r=r_del,
            time_budget_s=cheap,
            seed=1100 + i * 10 + j,
            u_id=u_id,
            universe_hash_str=uh,
            per_round_time_limit_s=25.0,
            num_workers=workers,
            symmetry_mode="asymmetric",
        )
        out = {
            "U_id": u_id,
            "q1": list(q1),
            "q2": list(q2),
            "hs1": [list(p) for p in h1],
            "hs2": [list(p) for p in h2],
            "r": r_del,
            "status": result.status,
            "universe_hash": uh,
            "n_rem": len(rem),
            "n_add": len(add_l),
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
            break

    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    summary = {
        "schema": "w3_joint_hs_v1",
        "n_tried": len(rows),
        "any_legal": any(r.get("status") == "FEASIBLE_LEGAL" for r in rows),
        "status_counts": counts,
        "rows": rows,
    }
    with open(os.path.join(exp, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({"done": True, "n_tried": len(rows), "status_counts": counts}, indent=2), flush=True)


if __name__ == "__main__":
    main()
