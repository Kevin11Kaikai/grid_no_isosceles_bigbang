#!/usr/bin/env python3
"""Structural orbit audit for notebook 7 axis-offset symmetries (Audit Agent B).

Read-only w.r.t. baselines/verifiers/search. Writes only under scratch/audit/agent_b/.
Does NOT run legality solvers or construction search.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from data.baselines.official_raw import SOL_100, SOL_64  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

Point = Tuple[int, int]
OUT_DIR = ROOT / "scratch" / "audit" / "agent_b"

# Notebook comments (cell 4), recovered verbatim alongside offsets.
TYPE_COMMENTS = {
    0: "Reflection about (n-1)/2 axes (standard for n even, axes at X.5, Y.5)",
    1: "Reflection about n/2-1 axes (e.g. 31 for n=64, axes at X.0, Y.0)",
    2: "Reflection about n/2 axes (e.g. 32 for n=64, axes at X.0, Y.0)",
    3: "Mixed symmetry: x-axis at n/2, y-axis at (n-1)/2",
    4: "Mixed symmetry: x-axis at n/2-1, y-axis at (n-1)/2",
    5: "Mixed symmetry: x-axis at (n-1)/2, y-axis at n/2",
    6: "Mixed symmetry: x-axis at (n-1)/2, y-axis at n/2-1",
}

EXPECTED_HASH = {
    64: "47d42165b7804493a847e064494ef067e97bc8ac12121cd04ac19f23fee9c292",
    100: "8a84216d28f5afbbbd6b06301b159eab1b57c85bb814d78dd708da2be65cbdc1",
}

TARGETS = {64: 113, 100: 165}


def offsets_for(n: int) -> List[Tuple[int, int]]:
    """Exact list from notebook get_symmetric_partners."""
    return [
        (n - 1, n - 1),
        (n - 2, n - 2),
        (n, n),
        (n, n - 1),
        (n - 2, n - 1),
        (n - 1, n),
        (n - 1, n - 2),
    ]


def get_symmetric_partners(
    p: Point, n: int, symmetry_type: int
) -> Set[Point]:
    """Notebook logic, recovered verbatim."""
    x, y = p
    offsets = offsets_for(n)
    if not 0 <= symmetry_type < len(offsets):
        raise ValueError(f"Invalid symmetry type: {symmetry_type}")
    offset_x, offset_y = offsets[symmetry_type]
    sym_x, sym_y = offset_x - x, offset_y - y
    partners: Set[Point] = set()
    for px, py in [(sym_x, y), (x, sym_y), (sym_x, sym_y)]:
        if (px, py) != p and 0 <= px < n and 0 <= py < n:
            partners.add((px, py))
    return partners


def formal_images(p: Point, ox: int, oy: int) -> Dict[str, Point]:
    """Unfiltered Klein-four images (may be out of grid)."""
    x, y = p
    return {
        "id": (x, y),
        "rx": (ox - x, y),
        "ry": (x, oy - y),
        "rxy": (ox - x, oy - y),
    }


def in_grid(p: Point, n: int) -> bool:
    return 0 <= p[0] < n and 0 <= p[1] < n


def axis_positions(n: int, ox: int, oy: int) -> Dict[str, object]:
    """Axis locations implied by reflection formula c' = offset - c = 2A - c => A = offset/2."""
    return {
        "offset_x": ox,
        "offset_y": oy,
        "axis_x_A": ox / 2.0,
        "axis_y_A": oy / 2.0,
        "integer_fixed_x": (ox % 2 == 0) and (0 <= ox // 2 < n),
        "integer_fixed_y": (oy % 2 == 0) and (0 <= oy // 2 < n),
        "fixed_x_coord": (ox // 2) if ox % 2 == 0 else None,
        "fixed_y_coord": (oy // 2) if oy % 2 == 0 else None,
    }


def enumerate_orbits(n: int, symmetry_type: int) -> Dict[str, object]:
    """Partition grid into closure-orbits under notebook partner relation.

    Orbit definition used here (documented): undirected connected components of the
    graph with vertices = grid points and edges p--q whenever
    q in get_symmetric_partners(p,n,type) (notebook's filtered partners).
    A component is a FULL orbit iff every formal Klein-four image of every
    representative lands in-grid (equivalently: notebook partners never drop
    an image for points in the component, and component equals formal orbit).
    """
    ox, oy = offsets_for(n)[symmetry_type]
    visited: Set[Point] = set()
    orbits: List[Dict[str, object]] = []

    out_of_grid_image_events = 0
    points_with_oog_image = 0

    for x in range(n):
        for y in range(n):
            p = (x, y)
            imgs = formal_images(p, ox, oy)
            oog = [name for name, q in imgs.items() if name != "id" and not in_grid(q, n)]
            if oog:
                points_with_oog_image += 1
                out_of_grid_image_events += len(oog)

    for x in range(n):
        for y in range(n):
            start = (x, y)
            if start in visited:
                continue
            # BFS under notebook partner relation (symmetric by construction of edges)
            stack = [start]
            comp: Set[Point] = set()
            while stack:
                u = stack.pop()
                if u in visited:
                    continue
                visited.add(u)
                comp.add(u)
                for v in get_symmetric_partners(u, n, symmetry_type):
                    if v not in visited:
                        stack.append(v)
                    # also ensure undirected: if u partner of v
                # notebook relation is already checked both ways below via visiting all

            # Verify undirected closure: every partner of every member is in comp
            closed = True
            for u in list(comp):
                for v in get_symmetric_partners(u, n, symmetry_type):
                    if v not in comp:
                        closed = False
                        comp.add(v)
                        visited.add(v)

            # Formal orbit of a representative
            rep = next(iter(comp))
            formal = formal_images(rep, ox, oy)
            formal_in = {q for q in formal.values() if in_grid(q, n)}
            formal_all_in = all(in_grid(q, n) for q in formal.values())
            formal_size_distinct = len(set(formal.values()))

            # Classify
            on_axis_x = any(
                (ox % 2 == 0) and (p[0] == ox // 2) for p in comp
            )
            on_axis_y = any(
                (oy % 2 == 0) and (p[1] == oy // 2) for p in comp
            )
            is_fixed_point_orbit = len(comp) == 1
            is_boundary = not formal_all_in
            is_full = formal_all_in and closed and (comp == formal_in)

            # Special: size not in {1,2,4}
            size = len(comp)
            size_bucket = size if size in (1, 2, 4) else "other"

            orbits.append(
                {
                    "repr": list(rep),
                    "size": size,
                    "size_bucket": size_bucket,
                    "points": sorted(list(comp)),
                    "is_full": is_full,
                    "is_boundary_truncated": is_boundary,
                    "on_axis_x": on_axis_x,
                    "on_axis_y": on_axis_y,
                    "is_fixed_point_orbit": is_fixed_point_orbit,
                    "formal_all_in_grid": formal_all_in,
                    "formal_distinct_count": formal_size_distinct,
                    "closed_under_notebook_partners": closed,
                }
            )

    # Coverage check
    covered = sum(o["size"] for o in orbits)
    assert covered == n * n, (covered, n * n)

    size_dist = Counter(o["size"] for o in orbits)
    bucket_dist = Counter(str(o["size_bucket"]) for o in orbits)
    full_orbits = [o for o in orbits if o["is_full"]]
    boundary_orbits = [o for o in orbits if o["is_boundary_truncated"]]
    fixed_orbits = [o for o in orbits if o["is_fixed_point_orbit"]]
    axis_orbits = [
        o
        for o in orbits
        if (o["on_axis_x"] or o["on_axis_y"]) and not o["is_fixed_point_orbit"]
    ]
    other_size_orbits = [o for o in orbits if o["size_bucket"] == "other"]

    full_size_dist = Counter(o["size"] for o in full_orbits)
    max_full_symmetric_core = sum(o["size"] for o in full_orbits)

    # Is notebook partner graph a true group action on full grid?
    # True iff every point's formal images are all in-grid.
    true_group_action_on_grid = points_with_oog_image == 0

    return {
        "n": n,
        "symmetry_type": symmetry_type,
        "offset": [ox, oy],
        "axis_info": axis_positions(n, ox, oy),
        "comment": TYPE_COMMENTS[symmetry_type],
        "num_orbits": len(orbits),
        "size_distribution": {str(k): v for k, v in sorted(size_dist.items())},
        "size_bucket_distribution": dict(bucket_dist),
        "num_full_orbits": len(full_orbits),
        "full_orbit_size_distribution": {
            str(k): v for k, v in sorted(full_size_dist.items())
        },
        "num_boundary_truncated_orbits": len(boundary_orbits),
        "num_fixed_point_orbits": len(fixed_orbits),
        "num_axis_nonfixed_orbits": len(axis_orbits),
        "num_other_size_orbits": len(other_size_orbits),
        "other_sizes_present": sorted(
            {o["size"] for o in other_size_orbits}
        ),
        "points_with_out_of_grid_formal_image": points_with_oog_image,
        "out_of_grid_formal_image_events": out_of_grid_image_events,
        "true_group_action_on_full_grid": true_group_action_on_grid,
        "max_fully_symmetric_core_size_full_orbits_only": max_full_symmetric_core,
        "grid_coverage_points": covered,
        # Keep compact orbit size list for subset-sum (full only)
        "full_orbit_sizes": [o["size"] for o in full_orbits],
        # For baseline completeness we need membership; store frozenset keys separately
        "_orbits_for_baseline": orbits,  # stripped before JSON dump
    }


def subset_sum_reachable(sizes: Sequence[int], target: int) -> Dict[str, object]:
    """Classic DP subset-sum over multiset of orbit sizes (FULL orbits only)."""
    if target < 0:
        return {"reachable": False, "reason": "negative_target"}
    # Bitset DP
    reachable = 1  # bit 0 set
    max_sum = sum(sizes)
    if target > max_sum:
        return {
            "reachable": False,
            "reason": f"target {target} > sum of full-orbit sizes {max_sum}",
            "max_sum": max_sum,
        }
    for s in sizes:
        reachable |= reachable << s
    ok = bool((reachable >> target) & 1)
    # Parity proof helpers
    all_even = all(s % 2 == 0 for s in sizes) if sizes else True
    gcd_like_mod = None
    if sizes:
        # strongest simple obstruction: all sizes ≡ 0 mod g for g=gcd
        from math import gcd
        from functools import reduce

        g = reduce(gcd, sizes)
        gcd_like_mod = g
    proof = None
    if not ok:
        if all_even and target % 2 == 1:
            proof = (
                "All FULL orbit sizes are even, target is odd ⇒ impossible by parity."
            )
        elif gcd_like_mod and target % gcd_like_mod != 0:
            proof = (
                f"All FULL orbit sizes divisible by {gcd_like_mod}, "
                f"target {target} not divisible by {gcd_like_mod}."
            )
        else:
            proof = (
                f"Subset-sum DP over FULL orbit sizes cannot form {target} "
                f"(max_sum={max_sum})."
            )
    return {
        "reachable": ok,
        "target": target,
        "max_sum": max_sum,
        "num_full_orbits": len(sizes),
        "all_full_orbit_sizes_even": all_even,
        "gcd_of_full_orbit_sizes": gcd_like_mod,
        "proof_if_unreachable": proof,
    }


def baseline_completeness(
    baseline: Sequence[Point], orbits: List[Dict[str, object]]
) -> Dict[str, object]:
    """How many orbits are fully / partially / empty present in baseline."""
    S = set(tuple(p) for p in baseline)
    # Map point -> orbit index among ALL orbits (for descriptive defect distance)
    point_to_orbit: Dict[Point, int] = {}
    for i, o in enumerate(orbits):
        for p in o["points"]:
            point_to_orbit[tuple(p)] = i

    full_present = 0
    full_present_full_type = 0
    partial = 0
    empty = 0
    partial_details = []
    full_core_points = 0
    deletes_to_full_sym = 0  # remove points from partial orbits
    adds_to_complete_partials = 0  # add missing partners in partial orbits
    # Alternative structural distance: make baseline a union of FULL orbits only
    # by deleting all points in incomplete (partial or boundary) orbits and
    # keeping only complete full orbits; also count adds if we instead complete.

    for i, o in enumerate(orbits):
        pts = [tuple(p) for p in o["points"]]
        present = [p for p in pts if p in S]
        k = len(present)
        if k == 0:
            empty += 1
        elif k == len(pts):
            full_present += 1
            if o["is_full"]:
                full_present_full_type += 1
                full_core_points += len(pts)
        else:
            partial += 1
            missing = len(pts) - k
            deletes_to_full_sym += k  # drop partial membership to restore symmetry
            adds_to_complete_partials += missing
            if len(partial_details) < 20:
                partial_details.append(
                    {
                        "orbit_repr": o["repr"],
                        "orbit_size": o["size"],
                        "present": k,
                        "missing": missing,
                        "is_full_orbit_type": o["is_full"],
                        "is_boundary_truncated": o["is_boundary_truncated"],
                    }
                )

    # Structural distance (descriptive):
    # Path A — delete-only to fully symmetric subset: remove all points that lie
    #   in partial orbits (and optionally keep only full-type orbits).
    # Path B — complete partials by adding missing partners (may go outside baseline).
    size_after_delete_partials = len(S) - deletes_to_full_sym
    return {
        "baseline_size": len(S),
        "orbits_fully_present": full_present,
        "orbits_fully_present_and_full_type": full_present_full_type,
        "orbits_partially_present": partial,
        "orbits_empty": empty,
        "points_in_fully_present_full_orbits": full_core_points,
        "max_fully_symmetric_core_in_baseline": full_core_points,
        "structural_distance": {
            "deletes_to_remove_all_partial_orbit_points": deletes_to_full_sym,
            "adds_to_complete_all_partial_orbits": adds_to_complete_partials,
            "baseline_size_after_deleting_partial_orbit_points": size_after_delete_partials,
            "note": (
                "Descriptive only: deletes = points currently in incomplete orbits; "
                "adds = missing partners to complete those orbits. Not a search."
            ),
        },
        "partial_orbit_examples": partial_details,
        "is_fully_symmetric_all_orbits": partial == 0,
        "is_union_of_full_type_orbits_only": (
            partial == 0 and full_present == full_present_full_type
        ),
    }


def strip_orbits(info: Dict[str, object]) -> Dict[str, object]:
    out = dict(info)
    out.pop("_orbits_for_baseline", None)
    # full_orbit_sizes can be long; keep counts via distribution; still needed for DP
    # We keep sizes in reachability file; for completeness JSON drop raw sizes list
    return out


def analyze_n(n: int, baseline: Sequence[Point]) -> Dict[str, object]:
    h = sha256_of_points(baseline)
    result: Dict[str, object] = {
        "n": n,
        "baseline_size": len(baseline),
        "baseline_hash_sha256": h,
        "expected_gate0_hash": EXPECTED_HASH[n],
        "hash_matches_gate0": h == EXPECTED_HASH[n],
        "target_cardinality": TARGETS[n],
        "types": {},
    }
    for t in range(7):
        info = enumerate_orbits(n, t)
        orbits = info["_orbits_for_baseline"]
        comp = baseline_completeness(baseline, orbits)
        reach = subset_sum_reachable(info["full_orbit_sizes"], TARGETS[n])

        # Status classification
        if not info["true_group_action_on_full_grid"]:
            # Restricted/truncated action: still can do subset-sum on FULL orbits;
            # mapping is clear from notebook code — NOT mapping_semantics_blocked.
            # Flag restriction explicitly.
            action_note = "restricted_not_true_group_action_on_full_grid"
        else:
            action_note = "true_group_action_on_full_grid"

        if reach["reachable"]:
            status = "cardinality_reachable_but_legality_open"
            defects_required_for_cardinality = False
        else:
            status = "cardinality_unreachable"
            defects_required_for_cardinality = True

        # Explicit fixed FULL orbit coords (axis intersection when both axes integer & in-grid)
        fixed_full_coords = None
        ai = info["axis_info"]
        if ai["integer_fixed_x"] and ai["integer_fixed_y"]:
            fx, fy = ai["fixed_x_coord"], ai["fixed_y_coord"]
            # confirm it is a FULL size-1 orbit
            if any(
                o["is_full"] and o["size"] == 1 and tuple(o["repr"]) == (fx, fy)
                for o in orbits
            ):
                fixed_full_coords = [fx, fy]

        type_rec = {
            "symmetry_type": t,
            "offset": info["offset"],
            "comment": info["comment"],
            "axis_info": info["axis_info"],
            "fixed_full_orbit_coord": fixed_full_coords,
            "action_semantics": action_note,
            "true_group_action_on_full_grid": info["true_group_action_on_full_grid"],
            "points_with_out_of_grid_formal_image": info[
                "points_with_out_of_grid_formal_image"
            ],
            "orbit_summary": {
                "num_orbits": info["num_orbits"],
                "size_distribution": info["size_distribution"],
                "size_bucket_distribution": info["size_bucket_distribution"],
                "num_full_orbits": info["num_full_orbits"],
                "full_orbit_size_distribution": info["full_orbit_size_distribution"],
                "num_boundary_truncated_orbits": info["num_boundary_truncated_orbits"],
                "num_fixed_point_orbits": info["num_fixed_point_orbits"],
                "num_axis_nonfixed_orbits": info["num_axis_nonfixed_orbits"],
                "num_other_size_orbits": info["num_other_size_orbits"],
                "other_sizes_present": info["other_sizes_present"],
                "max_fully_symmetric_core_size_full_orbits_only": info[
                    "max_fully_symmetric_core_size_full_orbits_only"
                ],
            },
            "baseline_completeness": comp,
            "cardinality_reachability": reach,
            "cardinality_status": status,
            "defects_required_for_cardinality": defects_required_for_cardinality,
            "phase2_guidance": (
                "defects_mandatory_for_target_cardinality"
                if defects_required_for_cardinality
                else "compare_pure_orbit_vs_orbit_plus_defect"
            ),
        }
        # Drop bulky size list from completeness file; keep in reachability
        result["types"][str(t)] = type_rec
        # stash sizes for reachability aggregate
        type_rec["_full_orbit_sizes"] = info["full_orbit_sizes"]
    return result


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "scripts").mkdir(parents=True, exist_ok=True)

    git_head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True
    ).strip()

    n64 = analyze_n(64, SOL_64)
    n100 = analyze_n(100, SOL_100)

    # --- Write completeness JSONs (without raw size lists) ---
    def completeness_payload(rec: Dict[str, object]) -> Dict[str, object]:
        types_out = {}
        for k, v in rec["types"].items():
            vv = dict(v)
            vv.pop("_full_orbit_sizes", None)
            # remove reachability detail duplication lightly — keep summary
            types_out[k] = {
                "symmetry_type": vv["symmetry_type"],
                "offset": vv["offset"],
                "comment": vv["comment"],
                "axis_info": vv["axis_info"],
                "fixed_full_orbit_coord": vv.get("fixed_full_orbit_coord"),
                "action_semantics": vv["action_semantics"],
                "true_group_action_on_full_grid": vv["true_group_action_on_full_grid"],
                "points_with_out_of_grid_formal_image": vv[
                    "points_with_out_of_grid_formal_image"
                ],
                "orbit_summary": vv["orbit_summary"],
                "baseline_completeness": vv["baseline_completeness"],
            }
        return {
            "git_commit": git_head,
            "n": rec["n"],
            "baseline_size": rec["baseline_size"],
            "baseline_hash_sha256": rec["baseline_hash_sha256"],
            "expected_gate0_hash": rec["expected_gate0_hash"],
            "hash_matches_gate0": rec["hash_matches_gate0"],
            "partner_transform": {
                "source": (
                    "data/external/subsets_of_the_grid_with_no_isosceles_triangles.ipynb "
                    "cell with get_symmetric_partners"
                ),
                "offsets_formula": [
                    "(n-1,n-1)",
                    "(n-2,n-2)",
                    "(n,n)",
                    "(n,n-1)",
                    "(n-2,n-1)",
                    "(n-1,n)",
                    "(n-1,n-2)",
                ],
                "partners": (
                    "sym_x,sym_y = offset_x-x, offset_y-y; "
                    "partners={(sym_x,y),(x,sym_y),(sym_x,sym_y)} "
                    "filtered to in-grid and !=p"
                ),
                "orbit_definition": (
                    "Connected components under notebook partner relation; "
                    "FULL orbit iff all formal Klein-four images in-grid and "
                    "component equals formal in-grid orbit"
                ),
            },
            "types": types_out,
            "symmetry_guided_repo_note": (
                "src/search/symmetry_guided.py uses ONLY central 180° "
                "reflect(x,y)=(n-1-x,n-1-y), i.e. notebook Type 0's rxy alone, "
                "not the 7 reflection-axis offset types."
            ),
        }

    with open(OUT_DIR / "orbit_completeness_n64.json", "w", encoding="utf-8") as f:
        json.dump(completeness_payload(n64), f, indent=2)
        f.write("\n")
    with open(OUT_DIR / "orbit_completeness_n100.json", "w", encoding="utf-8") as f:
        json.dump(completeness_payload(n100), f, indent=2)
        f.write("\n")

    # --- Reachability JSON ---
    reachability = {
        "git_commit": git_head,
        "targets": {"n64": 113, "n100": 165},
        "method": (
            "Subset-sum over sizes of FULL orbits only "
            "(truncated/boundary orbits excluded from pure-orbit cardinality)."
        ),
        "status_vocabulary": [
            "cardinality_unreachable",
            "cardinality_reachable_but_legality_open",
            "mapping_semantics_blocked",
        ],
        "n64": {},
        "n100": {},
        "summary_table": [],
    }
    for label, rec in [("n64", n64), ("n100", n100)]:
        for t in range(7):
            vv = rec["types"][str(t)]
            sizes = vv["_full_orbit_sizes"]
            # compress multiset for JSON
            size_multiset = Counter(sizes)
            entry = {
                "symmetry_type": t,
                "offset": vv["offset"],
                "comment": vv["comment"],
                "fixed_full_orbit_coord": vv.get("fixed_full_orbit_coord"),
                "true_group_action_on_full_grid": vv["true_group_action_on_full_grid"],
                "full_orbit_size_multiset": {
                    str(k): v for k, v in sorted(size_multiset.items())
                },
                "cardinality_reachability": {
                    k: v
                    for k, v in vv["cardinality_reachability"].items()
                    if k != "reachable" or True
                },
                "cardinality_status": vv["cardinality_status"],
                "defects_required_for_cardinality": vv[
                    "defects_required_for_cardinality"
                ],
                "phase2_guidance": vv["phase2_guidance"],
                "mapping_semantics_blocked": False,
            }
            reachability[label][str(t)] = entry
            reachability["summary_table"].append(
                {
                    "n": rec["n"],
                    "target": rec["target_cardinality"],
                    "type": t,
                    "status": vv["cardinality_status"],
                    "defects_required": vv["defects_required_for_cardinality"],
                    "phase2": vv["phase2_guidance"],
                }
            )

    with open(OUT_DIR / "orbit_parity_reachability.json", "w", encoding="utf-8") as f:
        json.dump(reachability, f, indent=2)
        f.write("\n")

    # --- Markdown report ---
    lines: List[str] = []
    lines.append("# Audit Agent B — Orbit / Parity / Reachability (Gate 1)")
    lines.append("")
    lines.append(f"- **git HEAD**: `{git_head}`")
    lines.append(
        f"- **Baseline n=64**: size {n64['baseline_size']}, "
        f"sha256 `{n64['baseline_hash_sha256']}` "
        f"(Gate0 match={n64['hash_matches_gate0']})"
    )
    lines.append(
        f"- **Baseline n=100**: size {n100['baseline_size']}, "
        f"sha256 `{n100['baseline_hash_sha256']}` "
        f"(Gate0 match={n100['hash_matches_gate0']})"
    )
    lines.append(
        "- **Targets**: 113 (n=64), 165 (n=100). Statuses use FULL-orbit subset-sum only."
    )
    lines.append(
        "- **No search performed.** No legality solvers. No `src/search` modules created."
    )
    lines.append("")
    lines.append("## B1 — Recovered notebook symmetries")
    lines.append("")
    lines.append(
        "Source: `data/external/subsets_of_the_grid_with_no_isosceles_triangles.ipynb` "
        "(`get_symmetric_partners`)."
    )
    lines.append("")
    lines.append("Offsets (exact):")
    lines.append("")
    lines.append("```")
    lines.append("offsets = [")
    lines.append("  (n-1, n-1),  # type 0")
    lines.append("  (n-2, n-2),  # type 1")
    lines.append("  (n, n),      # type 2")
    lines.append("  (n, n-1),    # type 3")
    lines.append("  (n-2, n-1),  # type 4")
    lines.append("  (n-1, n),    # type 5")
    lines.append("  (n-1, n-2),  # type 6")
    lines.append("]")
    lines.append("sym_x, sym_y = offset_x - x, offset_y - y")
    lines.append("partners = {(sym_x,y), (x,sym_y), (sym_x,sym_y)} ∩ grid \\ {p}")
    lines.append("```")
    lines.append("")
    lines.append(
        "Partner transform is the Klein four-group of axis reflections with "
        "`c ↦ offset - c` (i.e. reflection across `A = offset/2`), **restricted** "
        "by dropping out-of-grid images. Mapping semantics are clear from code "
        "(not `mapping_semantics_blocked`)."
    )
    lines.append("")
    lines.append(
        "Repo `src/search/symmetry_guided.py` differs: it only uses central 180° "
        "`(n-1-x, n-1-y)` pairs (Type 0’s `rxy`), not the seven axis-offset types."
    )
    lines.append("")
    lines.append("### Per-type group-action / orbit notes (both n even)")
    lines.append("")
    lines.append(
        "| Type | Offset (n=64) | True G-action on full grid? | OOG pts (n64) | FULL size multiset (n64) | Fixed FULL orbits |"
    )
    lines.append("|---:|---|---|---:|---|---|")
    for t in range(7):
        a = n64["types"][str(t)]
        true = a["true_group_action_on_full_grid"]
        dist = a["orbit_summary"]["full_orbit_size_distribution"]
        oog = a["points_with_out_of_grid_formal_image"]
        nfix = a["orbit_summary"]["num_fixed_point_orbits"]
        nfull_fixed = dist.get("1", 0)
        lines.append(
            f"| {t} | `{a['offset']}` | {true} | {oog} | {dist} | "
            f"components={nfix}, FULL size-1={nfull_fixed} |"
        )
    lines.append("")
    lines.append(
        "Only **Type 0** (`offset=(n-1,n-1)`) is a true Klein-four group action on "
        "the entire `[0,n)²` grid (0 out-of-grid formal images). "
        "**Type 1** (`n-2,n-2`) reflects the far boundary `n-1 ↦ -1` (OOG). "
        "**Type 2** (`n,n`) reflects `0 ↦ n` (OOG). Mixed types 3–6 each have one "
        "OOG-producing axis. Truncated/boundary components are excluded from "
        "pure FULL-orbit cardinality. Types **1 and 2** each admit exactly one "
        "FULL size-1 fixed orbit at the integer axis intersection "
        "`(⌊offset_x/2⌋, ⌊offset_y/2⌋)` — i.e. `(n/2-1,n/2-1)` for type 1 and "
        "`(n/2,n/2)` for type 2 — which is what makes odd targets "
        "cardinality-reachable."
    )
    lines.append("")
    lines.append("## B2 — Baseline orbit completeness")
    lines.append("")
    for label, rec in [("n=64 / 112", n64), ("n=100 / 164", n100)]:
        lines.append(f"### {label}")
        lines.append("")
        lines.append(
            "| Type | Fully present (any) | Fully present FULL-type | Partial | Empty | "
            "FULL sym core (pts) | Deletes (partial) | Adds to complete |"
        )
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
        for t in range(7):
            c = rec["types"][str(t)]["baseline_completeness"]
            sd = c["structural_distance"]
            lines.append(
                f"| {t} | {c['orbits_fully_present']} | {c['orbits_fully_present_and_full_type']} | "
                f"{c['orbits_partially_present']} | {c['orbits_empty']} | "
                f"{c['max_fully_symmetric_core_in_baseline']} | "
                f"{sd['deletes_to_remove_all_partial_orbit_points']} | "
                f"{sd['adds_to_complete_all_partial_orbits']} |"
            )
        lines.append("")
    lines.append(
        "Notes: n=100 Type 0 has **0 partial orbits** and FULL core 164/164 "
        "(exact central reflection symmetry, consistent with H-001). "
        "n=64 Type 0 has FULL core 108/112 with 2 partial orbits (4 pts present / 4 missing). "
        "Structural distance is descriptive only (not a construction search)."
    )
    lines.append("")
    lines.append("## B3 — Cardinality reachability (FULL orbits → subset-sum)")
    lines.append("")
    lines.append("| Type | n=64 → 113 | n=100 → 165 | Defects for cardinality? | Phase 2 |")
    lines.append("|---:|---|---|---|---|")
    for t in range(7):
        a = n64["types"][str(t)]
        b = n100["types"][str(t)]
        # defects required if EITHER target needs defects when using that type on that n
        # Report per-column; Phase2 column combined
        def short(st: str) -> str:
            if st == "cardinality_unreachable":
                return "unreachable"
            if st == "cardinality_reachable_but_legality_open":
                return "reachable (legality open)"
            return st

        def phase(a_st, b_st):
            # For reporting "which require defects; which compare pure vs defect"
            ra = a_st == "cardinality_unreachable"
            rb = b_st == "cardinality_unreachable"
            if ra and rb:
                return "defects mandatory (both targets)"
            if ra or rb:
                return "mixed: defects on unreachable n; compare on reachable n"
            return "compare pure-orbit vs orbit+defect"

        lines.append(
            f"| {t} | {short(a['cardinality_status'])} | {short(b['cardinality_status'])} | "
            f"64:{a['defects_required_for_cardinality']}/100:{b['defects_required_for_cardinality']} | "
            f"{phase(a['cardinality_status'], b['cardinality_status'])} |"
        )
    lines.append("")
    lines.append("### Defect / Phase-2 classification (all 7 types)")
    lines.append("")
    req_def = []
    compare = []
    blocked = []
    for t in range(7):
        a = n64["types"][str(t)]
        b = n100["types"][str(t)]
        if a["cardinality_status"] == "mapping_semantics_blocked" or b[
            "cardinality_status"
        ] == "mapping_semantics_blocked":
            blocked.append(t)
        if a["defects_required_for_cardinality"] and b["defects_required_for_cardinality"]:
            req_def.append(t)
        elif (
            not a["defects_required_for_cardinality"]
            or not b["defects_required_for_cardinality"]
        ):
            # reachable on at least one target ⇒ Phase 2 must compare on that target
            compare.append(t)
    lines.append(
        f"- **Require defects for cardinality (both 113 and 165 unreachable)**: types {req_def or '∅'}"
    )
    lines.append(
        f"- **Compare pure-orbit vs orbit+defect** (cardinality reachable; legality open): types {compare or '∅'}"
    )
    lines.append(f"- **mapping_semantics_blocked**: types {blocked or '∅'}")
    lines.append("")
    lines.append(
        "Mathematical mandatory-defect theorem applies **only** to "
        "`cardinality_unreachable` types. Reachable types must still be searched "
        "both ways in Phase 2; cardinality ≠ legality."
    )
    lines.append("")
    lines.append("### Unreachability proofs (where applicable)")
    lines.append("")
    for label, rec in [("n=64 target 113", n64), ("n=100 target 165", n100)]:
        lines.append(f"**{label}**")
        lines.append("")
        for t in range(7):
            r = rec["types"][str(t)]["cardinality_reachability"]
            st = rec["types"][str(t)]["cardinality_status"]
            if st == "cardinality_unreachable":
                lines.append(f"- Type {t}: {r.get('proof_if_unreachable')}")
            else:
                lines.append(
                    f"- Type {t}: reachable via FULL-orbit subset-sum "
                    f"(max_sum={r.get('max_sum')}); legality open."
                )
        lines.append("")
    lines.append("## Files written")
    lines.append("")
    lines.append("- `scratch/audit/agent_b/orbit_parity_reachability.json`")
    lines.append("- `scratch/audit/agent_b/orbit_completeness_n64.json`")
    lines.append("- `scratch/audit/agent_b/orbit_completeness_n100.json`")
    lines.append("- `scratch/audit/agent_b/agent_b_report.md`")
    lines.append("- `scratch/audit/agent_b/scripts/orbit_audit.py`")
    lines.append("")

    report_path = OUT_DIR / "agent_b_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote", report_path)
    print("git", git_head)
    for t in range(7):
        print(
            f"type {t}: n64={n64['types'][str(t)]['cardinality_status']} "
            f"n100={n100['types'][str(t)]['cardinality_status']}"
        )


if __name__ == "__main__":
    main()
