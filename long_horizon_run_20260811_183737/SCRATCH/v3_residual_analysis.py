#!/usr/bin/env python3
"""LH-1 Route C: residual conflict structure of Agent-C V=3 elites (n=100, |S|=165)."""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Sequence, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402

Point = Tuple[int, int]
N = 100


def sq(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def witnesses(points: Sequence[Point]) -> List[dict]:
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
                    out.append(
                        {
                            "pivot": list(pivot),
                            "a": list(members[i]),
                            "b": list(members[j]),
                            "d2": int(d),
                        }
                    )
    return out


def main() -> None:
    elite_dir = os.path.join(ROOT, "scratch", "agent_c", "elite_archive")
    elites = sorted(
        f
        for f in os.listdir(elite_dir)
        if f.startswith("n100_V3_") and f.endswith(".json")
    )
    rows = []
    for name in elites:
        path = os.path.join(elite_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pts = [tuple(p) for p in data["points"]]
        assert len(pts) == 165
        v = conflict_count(pts, N)
        ok, _ = is_legal_pivot_method(pts, N)
        wits = witnesses(pts)
        pivots = Counter(tuple(w["pivot"]) for w in wits)
        involved = set()
        for w in wits:
            involved.add(tuple(w["pivot"]))
            involved.add(tuple(w["a"]))
            involved.add(tuple(w["b"]))
        rows.append(
            {
                "file": name,
                "V_recomputed": v,
                "oracle_legal": bool(ok),
                "n_witness_triples": len(wits),
                "n_distinct_pivots": len(pivots),
                "n_involved_points": len(involved),
                "pivot_mult": {str(k): c for k, c in pivots.most_common()},
                "witnesses": wits,
                "involved_points": [list(p) for p in sorted(involved)],
            }
        )

    # Cross-elite overlap of involved sets
    if rows:
        sets = [set(map(tuple, r["involved_points"])) for r in rows]
        inter_all = set.intersection(*sets) if sets else set()
        union_all = set.union(*sets) if sets else set()
    else:
        inter_all, union_all = set(), set()

    out = {
        "schema": "lh1_v3_residual_v1",
        "n_elites": len(rows),
        "V_values": sorted({r["V_recomputed"] for r in rows}),
        "any_legal": any(r["oracle_legal"] for r in rows),
        "witness_triple_counts": [r["n_witness_triples"] for r in rows],
        "involved_sizes": [r["n_involved_points"] for r in rows],
        "intersection_involved_all_elites": [list(p) for p in sorted(inter_all)],
        "union_involved_size": len(union_all),
        "elites": rows,
        "implication": (
            "If n_involved_points is small, exact repair over those points + local halo "
            "is a cheap microproblem distinct from Wave2 Hamming U_small_r2."
        ),
    }
    exp = os.path.join(RUN, "EXPERIMENTS", "LH1_v3_residual")
    os.makedirs(exp, exist_ok=True)
    path = os.path.join(exp, "v3_residual_n100.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(
        json.dumps(
            {
                "path": path,
                "n_elites": out["n_elites"],
                "V_values": out["V_values"],
                "witness_triple_counts": out["witness_triple_counts"],
                "involved_sizes": out["involved_sizes"],
                "intersection_size": len(inter_all),
                "union_involved_size": out["union_involved_size"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
