#!/usr/bin/env python3
"""Wave3: residual exact repair of rem>=2 fixed-card illegal core (V=25 seed504).

Strip all witness-involved points -> legal core; try refill to |S|=165 via
Hamming shell over Rem=core∩S0? No: free vars = involved ∪ halo empties,
fixed = legal core. Use hamming_shell with removable=involved∩S_current,
addable=empties in halo∪involved neighborhood, r chosen so |S|=165.
Simpler: grow from legal core with CP-SAT-ish via Incremental greedy +
hamming_shell_search from S_legal with Rem=empty of size needing fill.
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

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
N = 100
TARGET = 165


def sq(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def all_witnesses(points: Sequence[Point]) -> List[dict]:
    pts = [tuple(p) for p in points]
    out = []
    for pivot in pts:
        groups: Dict[int, List[Point]] = defaultdict(list)
        for q in pts:
            if q == pivot:
                continue
            groups[sq(pivot, q)].append(q)  # type: ignore[arg-type]
        for d, members in groups.items():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    out.append({"pivot": pivot, "a": members[i], "b": members[j], "d2": d})
    return out


def halo(seeds: Sequence[Point], radius: int, forbidden: Set[Point]) -> Set[Point]:
    out: Set[Point] = set()
    for x, y in seeds:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if max(abs(dx), abs(dy)) > radius:
                    continue
                p = (x + dx, y + dy)
                if 0 <= p[0] < N and 0 <= p[1] < N and p not in forbidden:
                    out.add(p)
    return out


def dual(pts):
    ok_a, _ = is_legal_pivot_method(pts, N)
    ok_b, _ = verify_independent(pts, N)
    return {
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "V": int(conflict_count(pts, N)),
        "size": len(pts),
        "hash": sha256_of_points(pts),
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
    except Exception:
        pass
    exp = os.path.join(RUN, "EXPERIMENTS", "W3_rem2_residual")
    os.makedirs(exp, exist_ok=True)
    src = os.path.join(RUN, "EXPERIMENTS", "LH3_forced_exchange", "seed504_points_v25.json")
    data = json.load(open(src, encoding="utf-8"))
    pts = [tuple(p) for p in data["points"]]
    assert len(pts) == TARGET
    wits = all_witnesses(pts)
    involved: Set[Point] = set()
    for w in wits:
        involved.add(w["pivot"])
        involved.add(w["a"])
        involved.add(w["b"])
    core = [p for p in pts if p not in involved]
    st = IncrementalIsoscelesFreeSet(N)
    for p in core:
        assert st.add_point(p), f"core illegal at {p}"
    core_legal = True
    need = TARGET - len(core)
    print(
        json.dumps(
            {
                "start_V": data["best_V"],
                "n_witnesses": len(wits),
                "n_involved": len(involved),
                "core_size": len(core),
                "need_add": need,
            }
        ),
        flush=True,
    )
    # Greedy refill from involved∪halo first
    pool = sorted(involved | halo(list(involved) + core, 4, set(core)))
    greedy = list(core)
    st2 = IncrementalIsoscelesFreeSet(N)
    for p in greedy:
        st2.add_point(p)
    for p in pool:
        if len(greedy) >= TARGET:
            break
        if p in st2.points:
            continue
        if st2.can_add(p)[0]:
            st2.add_point(p)
            greedy.append(p)
    greedy_row = {
        "method": "greedy_involved_halo4",
        "size": len(greedy),
        "V": conflict_count(greedy, N) if len(greedy) == TARGET else None,
        "dual": dual(greedy) if len(greedy) == TARGET else None,
    }
    print(json.dumps(greedy_row, indent=2), flush=True)

    # Exact Hamming: treat core as S0, Rem=[], Add=pool empties, need need adds
    # API is remove r and add r+delta for fixed card from S0.
    # Use: S0' = core + pad dummies? Better: use searchable with s0=full greedy illegal
    # and Rem=involved∩pts, Add=pool - core, r = |Rem|.
    s0_pts = sorted(pts)  # illegal V=25 set as baseline
    rem = sorted(p for p in involved if p in set(pts))
    add = sorted(p for p in (involved | halo(list(involved), 5, set(pts) - involved)) if p not in set(pts) or p in involved)
    # Also allow re-adding rem points selectively via rem/add
    add = sorted(set(add) | set(rem))
    r_del = min(len(rem), max(2, need // 2))
    # Try several r
    rows = [greedy_row]
    workers = int(os.environ.get("W3_WORKERS", "4"))
    cheap = float(os.environ.get("W3_CHEAP_S", "300"))
    for r in sorted({2, 3, 4, min(6, len(rem)), r_del}):
        if r < 1 or r > len(rem):
            continue
        uh = universe_hash(rem, add)
        u_id = f"U_rem2res_r{r}_inv{len(involved)}"
        print(json.dumps({"start": u_id, "r": r, "n_rem": len(rem), "n_add": len(add)}), flush=True)
        t0 = time.time()
        result = hamming_shell_search(
            n=N,
            s0=s0_pts,
            removable=rem,
            addable=add,
            r=r,
            time_budget_s=cheap,
            seed=9000 + r,
            u_id=u_id,
            universe_hash_str=uh,
            per_round_time_limit_s=30.0,
            num_workers=workers,
            symmetry_mode="asymmetric",
        )
        row = {
            "U_id": u_id,
            "r": r,
            "status": result.status,
            "universe_hash": uh,
            "n_rem": len(rem),
            "n_add": len(add),
            "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
            "rounds": (result.meta or {}).get("rounds"),
            "final_cuts": (result.meta or {}).get("final_cuts"),
            "wall_time_s": time.time() - t0,
            "size": len(result.points) if result.points else 0,
        }
        if result.status == "FEASIBLE_LEGAL" and result.points:
            row["dual"] = dual(result.points)
            cand_path = os.path.join(RUN, "CANDIDATES", f"{u_id}_legal.json")
            os.makedirs(os.path.dirname(cand_path), exist_ok=True)
            json.dump(
                {"points": [list(p) for p in result.points], **row},
                open(cand_path, "w"),
                indent=2,
            )
            row["candidate"] = cand_path
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if row.get("dual") and row["dual"].get("oracle_legal"):
            break

    summary = {
        "schema": "w3_rem2_residual_v1",
        "source": src,
        "start_V": data["best_V"],
        "n_witnesses": len(wits),
        "n_involved": len(involved),
        "core_size": len(core),
        "core_legal": core_legal,
        "rows": rows,
        "any_legal": any(
            (r.get("dual") or {}).get("oracle_legal") for r in rows if isinstance(r.get("dual"), dict)
        ),
    }
    path = os.path.join(exp, "summary.json")
    json.dump(summary, open(path, "w", encoding="utf-8"), indent=2)
    open(path, "a", encoding="utf-8").write("\n")
    print(json.dumps({"done": True, "path": path, "any_legal": summary["any_legal"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
