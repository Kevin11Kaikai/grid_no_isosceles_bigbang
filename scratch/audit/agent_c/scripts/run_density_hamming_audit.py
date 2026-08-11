#!/usr/bin/env python3
"""Audit Agent C — density / Hamming / universe diagnostics (Gate 1).

Read-only inputs: official_raw baselines + conflict_metric import.
Writes only under scratch/audit/agent_c/.
Does NOT solve +1, does NOT search for target sizes, does NOT modify protected paths.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from typing import Any, Dict, List, Sequence, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_64, SOL_100  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402

Point = Tuple[int, int]
EXPECTED = {
    64: "47d42165b7804493a847e064494ef067e97bc8ac12121cd04ac19f23fee9c292",
    100: "8a84216d28f5afbbbd6b06301b159eab1b57c85bb814d78dd708da2be65cbdc1",
}
OUT_DIR = os.path.join(ROOT, "scratch", "audit", "agent_c")


def sha256_of_points(points: Sequence[Sequence[int]]) -> str:
    pts = sorted((int(p[0]), int(p[1])) for p in points)
    s = json.dumps(pts, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def git_head() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
    except Exception:
        return "UNKNOWN"


def ring_of(p: Point, n: int) -> int:
    x, y = p
    return min(x, y, n - 1 - x, n - 1 - y)


def central180(p: Point, n: int) -> Point:
    return (n - 1 - p[0], n - 1 - p[1])


def sq_dist(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def percentile(sorted_vals: List[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    pos = (len(sorted_vals) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(sorted_vals[lo])
    w = pos - lo
    return float(sorted_vals[lo] * (1 - w) + sorted_vals[hi] * w)


def summarize_counts(vals: List[int]) -> Dict[str, Any]:
    if not vals:
        return {"count": 0}
    s = sorted(vals)
    return {
        "count": len(s),
        "min": s[0],
        "max": s[-1],
        "mean": sum(s) / len(s),
        "median": percentile(s, 0.5),
        "p90": percentile(s, 0.9),
        "p99": percentile(s, 0.99),
        "sum": sum(s),
        "zeros": sum(1 for v in s if v == 0),
        "nonzero": sum(1 for v in s if v > 0),
    }


def binom(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def log10_binom(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("-inf")
    # Stirling-ish via math.lgamma for large values
    return (
        math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
    ) / math.log(10)


def comfort_label(n_vars: int, n_constraints_est: int) -> Dict[str, Any]:
    """Heuristic comfort ranges for CP-SAT vs MILP (diagnostic only)."""
    # Empirically: CP-SAT lazy encodings comfortable up to ~few thousand bools
    # with sparse cuts; MILP denser/quadratic-ish gets painful >~1–2k vars.
    if n_vars <= 80:
        cpsat, milp = "comfortable", "comfortable"
    elif n_vars <= 250:
        cpsat, milp = "comfortable", "moderate"
    elif n_vars <= 800:
        cpsat, milp = "moderate", "stressed"
    elif n_vars <= 2500:
        cpsat, milp = "stressed", "likely_impractical"
    else:
        cpsat, milp = "likely_impractical", "impractical"
    if n_constraints_est > 5e5 and cpsat == "comfortable":
        cpsat = "moderate"
    if n_constraints_est > 2e6 and cpsat in ("comfortable", "moderate"):
        cpsat = "stressed"
    return {
        "n_vars": n_vars,
        "n_constraints_est": n_constraints_est,
        "cpsat_comfort": cpsat,
        "milp_comfort": milp,
    }


def build_pivot_distance_maps(S: List[Point]) -> Dict[Point, Counter]:
    maps: Dict[Point, Counter] = {}
    for i, b in enumerate(S):
        c: Counter = Counter()
        for j, a in enumerate(S):
            if i == j:
                continue
            c[sq_dist(a, b)] += 1
        maps[b] = c
    return maps


def insertion_delta_V(q: Point, S: List[Point], pivot_maps: Dict[Point, Counter]) -> int:
    """Exact ΔV = V(S∪{q}) - V(S) for q not in S. Uses O(|S|) arithmetic."""
    # Increment at existing pivots
    delta = 0
    d_from_q: Counter = Counter()
    for b in S:
        d = sq_dist(q, b)
        m = pivot_maps[b][d]  # current multiplicity at (b,d)
        delta += m  # binom(m+1,2)-binom(m,2) = m
        d_from_q[d] += 1
    # Conflicts with q as pivot
    for m in d_from_q.values():
        if m >= 2:
            delta += m * (m - 1) // 2
    return delta


def distance_usage_pressure(
    b: Point,
    S: List[Point],
    pivot_maps: Dict[Point, Counter],
    unselected_sample_blocked: int,
) -> Dict[str, Any]:
    """Distance-spectrum pressure at pivot b.

    For a legal baseline, multiplicities are all 1 so usage_ratio==1.
    More informative: how many unselected cells collide with an already-used
    distance from b (blocked_by_b), and the min positive gap among used d2s.
    """
    c = pivot_maps[b]
    used = len(c)
    max_mult = max(c.values()) if c else 0
    local_V = sum(m * (m - 1) // 2 for m in c.values())
    others = len(S) - 1
    used_d2 = sorted(c.keys())
    min_gap = None
    if len(used_d2) >= 2:
        min_gap = min(used_d2[i + 1] - used_d2[i] for i in range(len(used_d2) - 1))
    return {
        "point": [b[0], b[1]],
        "distinct_distances": used,
        "others": others,
        "max_multiplicity": max_mult,
        "local_V_contrib": local_V,
        "usage_ratio": (used / others) if others else 0.0,
        "spectrum_fill": used,
        "min_used_d2_gap": min_gap,
        "n_unselected_blocked_by_this_pivot": unselected_sample_blocked,
    }


def local_crowding(p: Point, S_set: set, radii: Sequence[int] = (1, 2, 3, 5, 8)) -> Dict[str, int]:
    """Count other selected points within Chebyshev radius r."""
    out = {}
    for r in radii:
        cnt = 0
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if dx == 0 and dy == 0:
                    continue
                q = (p[0] + dx, p[1] + dy)
                if q in S_set:
                    cnt += 1
        out[f"chebyshev_r{r}"] = cnt
    return out


def region_label(ring: int, n: int) -> str:
    max_ring = (n - 1) // 2
    # Boundary: outer third of rings; mid: middle third; center: inner third
    b1 = max_ring // 3
    b2 = (2 * max_ring) // 3
    if ring <= b1:
        return "boundary"
    if ring <= b2:
        return "mid"
    return "center"


def analyze_baseline(n: int, points_raw: List[Tuple[int, int]]) -> Dict[str, Any]:
    t0 = time.time()
    S = [(int(x), int(y)) for x, y in points_raw]
    S_set = set(S)
    assert len(S) == len(S_set)
    h = sha256_of_points(S)
    expected = EXPECTED[n]
    assert h == expected, f"hash mismatch n={n}: got {h}, expected {expected}"

    V0 = conflict_count(S, n)
    assert V0 == 0, f"baseline V!=0 for n={n}: {V0}"

    max_ring = (n - 1) // 2
    row_occ = [0] * n
    col_occ = [0] * n
    ring_occ = [0] * (max_ring + 1)
    for x, y in S:
        row_occ[x] += 1
        col_occ[y] += 1
        ring_occ[ring_of((x, y), n)] += 1

    # Region densities
    region_cells = Counter()
    region_sel = Counter()
    for x in range(n):
        for y in range(n):
            lab = region_label(ring_of((x, y), n), n)
            region_cells[lab] += 1
            if (x, y) in S_set:
                region_sel[lab] += 1
    region_density = {
        lab: {
            "selected": region_sel[lab],
            "cells": region_cells[lab],
            "density": region_sel[lab] / region_cells[lab] if region_cells[lab] else 0.0,
        }
        for lab in ("boundary", "mid", "center")
    }

    # Max occupied ring / empty center
    occupied_rings = [r for r, c in enumerate(ring_occ) if c > 0]
    max_occupied_ring = max(occupied_rings) if occupied_rings else -1
    empty_inner_rings = [
        r for r in range(max_occupied_ring + 1, max_ring + 1) if ring_occ[r] == 0
    ]
    # Cells with ring > max_occupied_ring
    empty_center_cells = sum(
        1
        for x in range(n)
        for y in range(n)
        if ring_of((x, y), n) > max_occupied_ring
    )

    pivot_maps = build_pivot_distance_maps(S)

    # Insertion deltas for all unselected (needed for pressure + universe ranking)
    unselected = [(x, y) for x in range(n) for y in range(n) if (x, y) not in S_set]

    # Per-pivot: count unselected cells that hit an already-used distance from b
    blocked_counts: Dict[Point, int] = {b: 0 for b in S}
    for q in unselected:
        for b in S:
            if sq_dist(q, b) in pivot_maps[b]:
                blocked_counts[b] += 1

    # Per-selected pressure + crowding
    pressures = [
        distance_usage_pressure(b, S, pivot_maps, blocked_counts[b]) for b in S
    ]
    crowding = []
    for b in S:
        cr = local_crowding(b, S_set)
        crowding.append({"point": [b[0], b[1]], "ring": ring_of(b, n), **cr})

    pressure_usage = [p["usage_ratio"] for p in pressures]
    pressure_distinct = [p["distinct_distances"] for p in pressures]
    pressure_blocked = [p["n_unselected_blocked_by_this_pivot"] for p in pressures]
    crowd_r3 = [c["chebyshev_r3"] for c in crowding]
    crowd_r5 = [c["chebyshev_r5"] for c in crowding]
    insertion = []
    delta_hist = Counter()
    zero_delta = []
    low_delta = []  # delta <= 2
    for q in unselected:
        dV = insertion_delta_V(q, S, pivot_maps)
        delta_hist[dV] += 1
        rec = {
            "point": [q[0], q[1]],
            "ring": ring_of(q, n),
            "region": region_label(ring_of(q, n), n),
            "delta_V": dV,
        }
        insertion.append(rec)
        if dV == 0:
            zero_delta.append(rec)
        if dV <= 2:
            low_delta.append(rec)

    # Spot-check a few deltas vs full conflict_count
    spot_checks = []
    for rec in sorted(insertion, key=lambda r: r["delta_V"])[:5]:
        q = tuple(rec["point"])
        full = conflict_count(S + [q], n)
        spot_checks.append(
            {
                "point": rec["point"],
                "delta_V": rec["delta_V"],
                "full_V": full,
                "match": full == rec["delta_V"],
            }
        )
    assert all(s["match"] for s in spot_checks), spot_checks

    # Central 180 symmetry
    missing_images = []
    paired = 0
    self_maps = 0
    for p in S:
        img = central180(p, n)
        if img == p:
            self_maps += 1
            paired += 1
        elif img in S_set:
            paired += 1
        else:
            missing_images.append([p[0], p[1]])
    # Count unique unpaired (each broken pair counted once from the present side)
    unpaired_present = len(missing_images)
    symmetry = {
        "map": "(x,y)->(n-1-x,n-1-y)",
        "points_with_image_in_S": paired,
        "points_total": len(S),
        "fraction_with_image": paired / len(S),
        "self_symmetric_points": self_maps,
        "unpaired_present_points": unpaired_present,
        "unpaired_examples": missing_images[:16],
        "fully_symmetric": unpaired_present == 0,
    }

    # Rank selected points by "removability attractiveness" for universe construction:
    # high local crowding + outer ring preference for small universes; also
    # include unpaired symmetry defects.
    # Score for REMOVAL: prefer high crowd_r5, prefer boundary (low ring), unpaired.
    unpaired_set = {tuple(p) for p in missing_images}
    free = len(unselected)
    rem_scores = []
    for b, pr, cr in zip(S, pressures, crowding):
        ring = ring_of(b, n)
        score = (
            3.0 * cr["chebyshev_r5"]
            + 2.0 * cr["chebyshev_r3"]
            + (10.0 if b in unpaired_set else 0.0)
            + (max_ring - ring) * 0.5  # prefer boundary for small shells
            + pr["n_unselected_blocked_by_this_pivot"] / max(1, free) * 20.0
        )
        rem_scores.append(
            {
                "point": [b[0], b[1]],
                "ring": ring,
                "region": region_label(ring, n),
                "crowd_r5": cr["chebyshev_r5"],
                "blocked_unselected": pr["n_unselected_blocked_by_this_pivot"],
                "unpaired_symmetry": b in unpaired_set,
                "removal_score": score,
            }
        )
    rem_scores.sort(key=lambda r: -r["removal_score"])

    # Addable ranking: low delta_V first, then prefer mid/boundary over deep center for small U,
    # but include some center probes in larger U.
    add_ranked = sorted(
        insertion,
        key=lambda r: (r["delta_V"], -r["ring"] if r["region"] != "center" else 1000 + r["ring"]),
    )

    # Hamming scale diagnostics
    k = len(S)
    free = n * n - k
    hamming = {}
    for r in (1, 2, 3):
        raw = binom(k, r) * binom(free, r + 1)
        log10_raw = log10_binom(k, r) + log10_binom(free, r + 1)
        # After filtering add pool to low-conflict (delta_V <= t)
        filtered = {}
        for thr in (0, 1, 2, 3, 5, 10):
            add_pool = sum(1 for rec in insertion if rec["delta_V"] <= thr)
            rem_pool = k  # all removable in principle; later scored subsets
            scale = binom(rem_pool, r) * binom(add_pool, r + 1) if add_pool >= r + 1 else 0
            filtered[f"delta_V_le_{thr}"] = {
                "add_pool": add_pool,
                "rem_pool": rem_pool,
                "combinatorial_pairs": scale,
                "log10_combinatorial": (
                    log10_binom(rem_pool, r) + log10_binom(add_pool, r + 1)
                    if add_pool >= r + 1
                    else float("-inf")
                ),
            }

        # Variable counts for different universe pool sizes (diagnostic templates)
        var_scenarios = []
        for rem_n, add_n in [
            (8, 16),
            (12, 24),
            (16, 32),
            (24, 48),
            (32, 64),
            (48, 96),
            (64, 128),
            (k, min(free, 400)),
        ]:
            if rem_n > k or add_n > free:
                continue
            # Hamming shell encoding: choose exactly r to remove from Rem, r+1 to add from Add
            # Bool vars: rem_n + add_n; plus maybe indicators
            n_vars = rem_n + add_n
            # Rough constraint pressure: pairwise distance collisions among active points.
            # Active set size ≈ (k - r) + (r + 1) = k + 1. Number of potential
            # isosceles pivots ~ O((k+1)^2) distance pairs; lazy CP-SAT starts sparse.
            active = k + 1
            # Naive static cuts: for each triple ~ binom(active,3) is huge; report lazy estimate
            lazy_seed_cuts = active * binom(active - 1, 2)  # overestimate of pivot-distance pairs
            # More realistic: initial distance-equality potential among variables ~ O(n_vars^2)
            cut_pressure_est = n_vars * (n_vars - 1) // 2 + lazy_seed_cuts // 50
            comb_in_U = binom(rem_n, r) * binom(add_n, r + 1)
            var_scenarios.append(
                {
                    "rem_pool": rem_n,
                    "add_pool": add_n,
                    "exact_shell_combinations": comb_in_U,
                    "log10_shell_combinations": (
                        log10_binom(rem_n, r) + log10_binom(add_n, r + 1)
                    ),
                    **comfort_label(n_vars, cut_pressure_est),
                    "cut_pressure_est": cut_pressure_est,
                    "note": "vars = rem_pool + add_pool for choose-r / choose-(r+1) shell",
                }
            )

        hamming[f"r{r}"] = {
            "remove": r,
            "add": r + 1,
            "raw_combinatorial": raw if raw < 10**18 else None,
            "raw_combinatorial_scientific": f"{raw:.6e}" if raw < float("inf") else "inf",
            "log10_raw_combinatorial": log10_raw,
            "filtered_by_insertion_delta": filtered,
            "variable_scenarios": var_scenarios,
            "solver_guidance": {
                "prefer_cpsat_when": "n_vars<=800 and lazy conflict cuts; r=1 first",
                "prefer_milp_when": "n_vars<=200 with tight LP relaxation / branching on few rem vars",
                "avoid": "full-grid add pool at r>=2 (log10 scale >> 20)",
            },
        }

    # ---- Universe proposals ----
    def take_rem(n_rem: int, prefer_unpaired: bool = True) -> List[List[int]]:
        chosen = []
        if prefer_unpaired:
            for rec in rem_scores:
                if rec["unpaired_symmetry"] and len(chosen) < n_rem:
                    chosen.append(rec["point"])
        for rec in rem_scores:
            if rec["point"] in chosen:
                continue
            chosen.append(rec["point"])
            if len(chosen) >= n_rem:
                break
        return chosen

    def take_add(
        n_add: int,
        max_delta: int,
        include_center_frac: float = 0.0,
        force_center: int = 0,
    ) -> List[List[int]]:
        pool = [r for r in add_ranked if r["delta_V"] <= max_delta]
        non_center = [r for r in pool if r["region"] != "center"]
        center = [r for r in pool if r["region"] == "center"]
        # Also allow higher-delta center probes if force_center
        if force_center and len(center) < force_center:
            center_extra = [
                r
                for r in add_ranked
                if r["region"] == "center" and r not in center
            ]
            center = center + center_extra
        n_center = max(force_center, int(round(n_add * include_center_frac)))
        n_center = min(n_center, n_add, len(center))
        n_other = min(n_add - n_center, len(non_center))
        # If not enough non-center, fill from center
        selected = non_center[:n_other] + center[:n_center]
        if len(selected) < n_add:
            remaining = [r for r in pool if r not in selected]
            selected.extend(remaining[: n_add - len(selected)])
        if len(selected) < n_add:
            remaining = [r for r in add_ranked if r not in selected]
            selected.extend(remaining[: n_add - len(selected)])
        return [r["point"] for r in selected[:n_add]]

    # Sizes tuned by Hamming comfort + density structure
    if n == 64:
        specs = {
            "U_small": {
                "rem_n": 12,
                "add_n": 24,
                "max_delta": 5,
                "include_center_frac": 0.05,
                "force_center": 2,
                "applicable_r": [1],
                "selection_rule": (
                    "Remove: top removal_score (crowding+boundary+unpaired-symmetry+blocking). "
                    "Add: lowest delta_V among ΔV≤5 (only 6 cells have ΔV≤2), "
                    "mostly non-center, 2 center probes."
                ),
            },
            "U_medium": {
                "rem_n": 24,
                "add_n": 48,
                "max_delta": 5,
                "include_center_frac": 0.15,
                "force_center": 6,
                "applicable_r": [1, 2],
                "selection_rule": (
                    "Remove: top-24 removal_score. "
                    "Add: delta_V<=5, ~15% center / mid mix, 6 forced center cells."
                ),
            },
            "U_large": {
                "rem_n": 40,
                "add_n": 96,
                "max_delta": 10,
                "include_center_frac": 0.25,
                "force_center": 16,
                "applicable_r": [1, 2, 3],
                "selection_rule": (
                    "Remove: top-40 removal_score. "
                    "Add: delta_V<=10 with substantial center/mid inclusion for RH-6 ablation."
                ),
            },
        }
    else:
        specs = {
            "U_small": {
                "rem_n": 16,
                "add_n": 32,
                "max_delta": 5,
                "include_center_frac": 0.05,
                "force_center": 2,
                "applicable_r": [1],
                "selection_rule": (
                    "Remove: top removal_score (crowding+boundary+blocking; symmetry already full). "
                    "Add: lowest delta_V among ΔV≤5 (empirical min ΔV=3; 16 cells at ≤3), "
                    "mostly frame/mid, 2 center probes."
                ),
            },
            "U_medium": {
                "rem_n": 32,
                "add_n": 64,
                "max_delta": 5,
                "include_center_frac": 0.15,
                "force_center": 8,
                "applicable_r": [1, 2],
                "selection_rule": (
                    "Remove: top-32 removal_score. "
                    "Add: delta_V<=5, ~15% center, 8 forced center cells."
                ),
            },
            "U_large": {
                "rem_n": 48,
                "add_n": 128,
                "max_delta": 10,
                "include_center_frac": 0.25,
                "force_center": 24,
                "applicable_r": [1, 2, 3],
                "selection_rule": (
                    "Remove: top-48 removal_score. "
                    "Add: delta_V<=10 with heavy center/mid for empty-center necessity test."
                ),
            },
        }

    universes = {}
    for uid, sp in specs.items():
        rem = take_rem(sp["rem_n"])
        add = take_add(
            sp["add_n"],
            sp["max_delta"],
            sp["include_center_frac"],
            sp["force_center"],
        )
        rem_rings = Counter(ring_of(tuple(p), n) for p in rem)
        add_rings = Counter(ring_of(tuple(p), n) for p in add)
        add_regions = Counter(region_label(ring_of(tuple(p), n), n) for p in add)
        # deltas of chosen add
        add_set = {tuple(p) for p in add}
        add_deltas = [r["delta_V"] for r in insertion if tuple(r["point"]) in add_set]
        universes[uid] = {
            "id": uid,
            "n": n,
            "removable_baseline_points": rem,
            "addable_unselected_points": add,
            "sizes": {"n_removable": len(rem), "n_addable": len(add), "n_vars": len(rem) + len(add)},
            "selection_rule": sp["selection_rule"],
            "applicable_hamming_r": sp["applicable_r"],
            "add_delta_V_summary": summarize_counts(add_deltas),
            "rem_ring_histogram": {str(k): v for k, v in sorted(rem_rings.items())},
            "add_ring_histogram": {str(k): v for k, v in sorted(add_rings.items())},
            "add_region_counts": dict(add_regions),
            "misses_if_scoped_unsat": [
                "Any +1 whose removed set is outside Rem pool",
                "Any +1 whose added points need cells with delta_V above max_delta cutoff",
                "Improvements requiring deep-center mass beyond force_center allotment (esp. U_small)",
                "Moves that need blocker-graph neighbors not near spatial/score halo (await Agent A)",
            ],
            "how_to_enlarge": [
                "Grow rem pool down the removal_score list",
                "Raise max_delta threshold / include next percentile of insertion deltas",
                "Union spatial Chebyshev halo around current Rem∪Add",
                "Union future blocker-incidence-graph halo (graph distance ≤ h) from Agent A communities",
                "Increase r only after r=1 scoped pilots on U_small/U_medium",
            ],
            "comfort": comfort_label(
                len(rem) + len(add),
                (len(rem) + len(add)) * (len(rem) + len(add) - 1) // 2
                + (k + 1) * binom(k, 2) // 50,
            ),
        }

    # Halo combination notes (for universe_halo_diagnostics)
    halo_notes = {
        "spatial_halo": {
            "definition": "Chebyshev ball around Rem∪Add or around high-pressure selected points",
            "suggested_h": [1, 2, 3],
            "role": "recover local geometric neighbors missed by score cutoff",
        },
        "score_halo": {
            "definition": "Next band of insertion-delta / removal-score candidates beyond U cutoffs",
            "suggested_expansion": "add next 25–50% of ranked add list; next 25% rem list",
            "role": "recover near-miss almost-insertable cells",
        },
        "blocker_graph_halo_future": {
            "definition": "Graph-distance ≤ h in conflict/blocker incidence graph (Agent A)",
            "suggested_h": [1, 2],
            "role": "capture non-local coupling RH-3; combine as U := U_score ∪ spatial_halo ∪ blocker_halo",
            "warning": "Do not interpret scoped UNSAT on any finite U as a global upper bound",
        },
        "combination_recipe": (
            "Start U_small spatial+score; if quick UNSAT, enlarge by blocker halo then "
            "score band then spatial h+=1; never claim global from scoped UNSAT."
        ),
    }

    elapsed = time.time() - t0

    # Compact insertion distribution (don't dump all points into JSON — summarize + tops)
    delta_values = sorted(delta_hist.keys())
    insertion_summary = {
        "n_unselected": len(unselected),
        "delta_V_histogram": {str(k): delta_hist[k] for k in sorted(delta_hist.keys())[:40]},
        "delta_V_histogram_tail_omitted_keys_gt": (
            None if len(delta_values) <= 40 else delta_values[40]
        ),
        "delta_V_stats": summarize_counts([r["delta_V"] for r in insertion]),
        "n_zero_delta": len(zero_delta),
        "n_delta_le_1": sum(1 for r in insertion if r["delta_V"] <= 1),
        "n_delta_le_2": sum(1 for r in insertion if r["delta_V"] <= 2),
        "n_delta_le_3": sum(1 for r in insertion if r["delta_V"] <= 3),
        "n_delta_le_5": sum(1 for r in insertion if r["delta_V"] <= 5),
        "n_delta_le_10": sum(1 for r in insertion if r["delta_V"] <= 10),
        "zero_delta_points": [r["point"] for r in zero_delta[:50]],
        "zero_delta_region_counts": dict(
            Counter(r["region"] for r in zero_delta)
        ),
        "low_delta_le2_region_counts": dict(Counter(r["region"] for r in low_delta)),
        "top20_lowest_delta": [
            {"point": r["point"], "delta_V": r["delta_V"], "ring": r["ring"], "region": r["region"]}
            for r in add_ranked[:20]
        ],
        "spot_checks_vs_conflict_count": spot_checks,
    }

    return {
        "meta": {
            "n": n,
            "baseline_size": k,
            "hash_sha256": h,
            "hash_matches_expected": h == expected,
            "expected_hash": expected,
            "V_S0": V0,
            "git_rev": git_head(),
            "elapsed_sec": round(elapsed, 3),
            "note_row_col_ring": "DESCRIPTIVE only — not legality constraints",
            "no_plus1_solver_run": True,
            "no_target_size_search": True,
        },
        "C1_density": {
            "row_occupancy": {
                "per_row": row_occ,
                "summary": summarize_counts(row_occ),
                "empty_rows": [i for i, c in enumerate(row_occ) if c == 0],
                "n_empty_rows": sum(1 for c in row_occ if c == 0),
            },
            "column_occupancy": {
                "per_col": col_occ,
                "summary": summarize_counts(col_occ),
                "empty_cols": [i for i, c in enumerate(col_occ) if c == 0],
                "n_empty_cols": sum(1 for c in col_occ if c == 0),
            },
            "ring_occupancy": {
                "definition": "ring = min(x,y,n-1-x,n-1-y) Chebyshev-to-edge",
                "max_ring": max_ring,
                "per_ring": ring_occ,
                "max_occupied_ring": max_occupied_ring,
                "n_empty_center_cells_beyond_max_occupied": empty_center_cells,
                "empty_center_fraction": empty_center_cells / (n * n),
            },
            "region_densities": region_density,
            "local_crowding": {
                "radii": [1, 2, 3, 5, 8],
                "chebyshev_r3_summary": summarize_counts(crowd_r3),
                "chebyshev_r5_summary": summarize_counts(crowd_r5),
                "top10_most_crowded_r5": sorted(crowding, key=lambda c: -c["chebyshev_r5"])[:10],
            },
            "distance_usage_pressure": {
                "note": (
                    "Legal baselines have usage_ratio=1 (all distances unique). "
                    "Primary pressure signal is n_unselected_blocked_by_this_pivot."
                ),
                "usage_ratio_mean": sum(pressure_usage) / len(pressure_usage),
                "distinct_distances_summary": summarize_counts(pressure_distinct),
                "blocked_unselected_summary": summarize_counts(pressure_blocked),
                "top10_most_blocking_pivots": sorted(
                    pressures, key=lambda p: -p["n_unselected_blocked_by_this_pivot"]
                )[:10],
            },
            "direct_insertion": insertion_summary,
            "central_180_symmetry": symmetry,
        },
        "C2_hamming_scale": hamming,
        "C3_universes": universes,
        "halo_combination": halo_notes,
        "recommended_first_r1": {
            "universe_id": "U_small",
            "n_vars": universes["U_small"]["sizes"]["n_vars"],
            "n_removable": universes["U_small"]["sizes"]["n_removable"],
            "n_addable": universes["U_small"]["sizes"]["n_addable"],
            "rationale": (
                "r=1 shell on U_small stays in CP-SAT comfort; includes low-delta adds "
                "and high-pressure removers; enlarge only after scoped result."
            ),
        },
    }


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    results = {}
    for n, raw in ((64, SOL_64), (100, SOL_100)):
        print(f"Analyzing n={n} ...", flush=True)
        res = analyze_baseline(n, raw)
        path = os.path.join(OUT_DIR, f"density_hamming_diagnostics_n{n}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
            f.write("\n")
        print(
            f"  wrote {path}  size={res['meta']['baseline_size']}  "
            f"hash_ok={res['meta']['hash_matches_expected']}  "
            f"elapsed={res['meta']['elapsed_sec']}s",
            flush=True,
        )
        results[n] = res

    halo = {
        "git_rev": git_head(),
        "purpose": (
            "Candidate universe + halo diagnostics for Hamming-shell +1 search. "
            "Scoped UNSAT is NEVER a global upper bound."
        ),
        "no_plus1_solver_run": True,
        "no_search_for_165_or_113": True,
        "baselines": {
            "n64": {
                "hash": results[64]["meta"]["hash_sha256"],
                "size": results[64]["meta"]["baseline_size"],
                "recommended_first_r1": results[64]["recommended_first_r1"],
                "universes": {
                    uid: {
                        "sizes": u["sizes"],
                        "applicable_hamming_r": u["applicable_hamming_r"],
                        "selection_rule": u["selection_rule"],
                        "comfort": u["comfort"],
                        "misses_if_scoped_unsat": u["misses_if_scoped_unsat"],
                        "how_to_enlarge": u["how_to_enlarge"],
                        "add_region_counts": u["add_region_counts"],
                        "removable_baseline_points": u["removable_baseline_points"],
                        "addable_unselected_points": u["addable_unselected_points"],
                    }
                    for uid, u in results[64]["C3_universes"].items()
                },
                "halo_combination": results[64]["halo_combination"],
                "key_density_findings": {
                    "max_occupied_ring": results[64]["C1_density"]["ring_occupancy"][
                        "max_occupied_ring"
                    ],
                    "empty_center_fraction": results[64]["C1_density"]["ring_occupancy"][
                        "empty_center_fraction"
                    ],
                    "n_empty_rows": results[64]["C1_density"]["row_occupancy"]["n_empty_rows"],
                    "n_empty_cols": results[64]["C1_density"]["column_occupancy"]["n_empty_cols"],
                    "symmetry_fraction": results[64]["C1_density"]["central_180_symmetry"][
                        "fraction_with_image"
                    ],
                    "n_zero_delta_insertions": results[64]["C1_density"]["direct_insertion"][
                        "n_zero_delta"
                    ],
                    "n_delta_le_2": results[64]["C1_density"]["direct_insertion"]["n_delta_le_2"],
                },
            },
            "n100": {
                "hash": results[100]["meta"]["hash_sha256"],
                "size": results[100]["meta"]["baseline_size"],
                "recommended_first_r1": results[100]["recommended_first_r1"],
                "universes": {
                    uid: {
                        "sizes": u["sizes"],
                        "applicable_hamming_r": u["applicable_hamming_r"],
                        "selection_rule": u["selection_rule"],
                        "comfort": u["comfort"],
                        "misses_if_scoped_unsat": u["misses_if_scoped_unsat"],
                        "how_to_enlarge": u["how_to_enlarge"],
                        "add_region_counts": u["add_region_counts"],
                        "removable_baseline_points": u["removable_baseline_points"],
                        "addable_unselected_points": u["addable_unselected_points"],
                    }
                    for uid, u in results[100]["C3_universes"].items()
                },
                "halo_combination": results[100]["halo_combination"],
                "key_density_findings": {
                    "max_occupied_ring": results[100]["C1_density"]["ring_occupancy"][
                        "max_occupied_ring"
                    ],
                    "empty_center_fraction": results[100]["C1_density"]["ring_occupancy"][
                        "empty_center_fraction"
                    ],
                    "n_empty_rows": results[100]["C1_density"]["row_occupancy"]["n_empty_rows"],
                    "n_empty_cols": results[100]["C1_density"]["column_occupancy"]["n_empty_cols"],
                    "symmetry_fraction": results[100]["C1_density"]["central_180_symmetry"][
                        "fraction_with_image"
                    ],
                    "n_zero_delta_insertions": results[100]["C1_density"]["direct_insertion"][
                        "n_zero_delta"
                    ],
                    "n_delta_le_2": results[100]["C1_density"]["direct_insertion"]["n_delta_le_2"],
                },
            },
        },
        "cross_n_recommendations": {
            "first_pilots": [
                {
                    "n": 64,
                    "r": 1,
                    "universe": "U_small",
                    "n_vars": results[64]["C3_universes"]["U_small"]["sizes"]["n_vars"],
                },
                {
                    "n": 100,
                    "r": 1,
                    "universe": "U_small",
                    "n_vars": results[100]["C3_universes"]["U_small"]["sizes"]["n_vars"],
                },
            ],
            "escalation": (
                "U_small r=1 → U_medium r=1 → U_medium r=2 → U_large / blocker-halo merge. "
                "Label every result with scope=(n,r,U_id,halo,...)."
            ),
            "hard_rule": "Scoped UNSAT/OPT is not a global bound on C(n).",
        },
    }
    halo_path = os.path.join(OUT_DIR, "universe_halo_diagnostics.json")
    with open(halo_path, "w", encoding="utf-8") as f:
        json.dump(halo, f, indent=2)
        f.write("\n")
    print(f"wrote {halo_path}", flush=True)

    # Write report markdown
    report_path = os.path.join(OUT_DIR, "agent_c_report.md")
    write_report(report_path, results, halo)
    print(f"wrote {report_path}", flush=True)


def write_report(path: str, results: Dict[int, Any], halo: Dict[str, Any]) -> None:
    g = results[64]["meta"]["git_rev"]
    lines: List[str] = []
    lines.append("# Audit Agent C Report — Wave 1 / Gate 1")
    lines.append("")
    lines.append(f"- **git HEAD:** `{g}`")
    lines.append(
        f"- **n64 hash:** `{results[64]['meta']['hash_sha256']}` "
        f"(match={results[64]['meta']['hash_matches_expected']})"
    )
    lines.append(
        f"- **n100 hash:** `{results[100]['meta']['hash_sha256']}` "
        f"(match={results[100]['meta']['hash_matches_expected']})"
    )
    lines.append("- **Scope:** density / Hamming-scale / universe-halo diagnostics only.")
    lines.append(
        "- **Confirmations:** no formal +1 solver; no search for sizes 165 or 113; "
        "no writes outside `scratch/audit/agent_c/`; row/col/ring stats are descriptive only."
    )
    lines.append("")
    lines.append("## C1 — Density findings")
    lines.append("")
    for n in (64, 100):
        d = results[n]["C1_density"]
        m = results[n]["meta"]
        lines.append(f"### n={n} (size {m['baseline_size']}, V=0)")
        lines.append("")
        ro = d["row_occupancy"]
        co = d["column_occupancy"]
        rg = d["ring_occupancy"]
        sy = d["central_180_symmetry"]
        ins = d["direct_insertion"]
        lines.append(
            f"- Row occupancy: mean={ro['summary']['mean']:.3f}, "
            f"empty_rows={ro['n_empty_rows']}/{n} (descriptive)."
        )
        lines.append(
            f"- Col occupancy: mean={co['summary']['mean']:.3f}, "
            f"empty_cols={co['n_empty_cols']}/{n} (descriptive)."
        )
        lines.append(
            f"- Ring: max_occupied_ring={rg['max_occupied_ring']} / max_ring={rg['max_ring']}; "
            f"empty-center cells beyond that = {rg['n_empty_center_cells_beyond_max_occupied']} "
            f"({rg['empty_center_fraction']:.3%} of grid)."
        )
        rd = d["region_densities"]
        lines.append(
            f"- Region densities: boundary={rd['boundary']['density']:.4f}, "
            f"mid={rd['mid']['density']:.4f}, center={rd['center']['density']:.4f}."
        )
        lines.append(
            f"- Local crowding (Chebyshev r=5 among selected): "
            f"mean={d['local_crowding']['chebyshev_r5_summary']['mean']:.2f}, "
            f"max={d['local_crowding']['chebyshev_r5_summary']['max']}."
        )
        bp = d["distance_usage_pressure"]["blocked_unselected_summary"]
        lines.append(
            f"- Distance-usage pressure: usage_ratio mean="
            f"{d['distance_usage_pressure']['usage_ratio_mean']:.4f} (legal⇒1); "
            f"unselected cells blocked per pivot: mean={bp['mean']:.1f}, "
            f"max={bp['max']}."
        )
        lines.append(
            f"- Direct insertion: zero-ΔV cells={ins['n_zero_delta']}; "
            f"ΔV≤1: {ins['n_delta_le_1']}; ΔV≤2: {ins['n_delta_le_2']}; "
            f"ΔV≤3: {ins['n_delta_le_3']}; ΔV≤5: {ins['n_delta_le_5']}; "
            f"ΔV≤10: {ins['n_delta_le_10']}."
        )
        lines.append(
            f"- Central 180° symmetry: {sy['points_with_image_in_S']}/{sy['points_total']} "
            f"= {sy['fraction_with_image']:.4f}; fully_symmetric={sy['fully_symmetric']}."
        )
        lines.append("")

    lines.append("## C2 — Hamming neighborhood scale")
    lines.append("")
    lines.append(
        "For shell |S₀\\S|=r, |S\\S₀|=r+1. Raw full-grid scales are astronomical; "
        "low-ΔV add-pools and finite Rem/Add universes are required before exact search."
    )
    lines.append("")
    for n in (64, 100):
        lines.append(f"### n={n}")
        lines.append("")
        for r in (1, 2, 3):
            h = results[n]["C2_hamming_scale"][f"r{r}"]
            lines.append(
                f"- **r={r}** (remove {r}, add {r+1}): "
                f"log10(raw)≈{h['log10_raw_combinatorial']:.2f}; "
                f"raw≈{h['raw_combinatorial_scientific']}."
            )
            f2 = h["filtered_by_insertion_delta"]["delta_V_le_2"]
            lines.append(
                f"  - After add-pool ΔV≤2: add_pool={f2['add_pool']}, "
                f"log10(comb)≈{f2['log10_combinatorial']:.2f}."
            )
            # Pick a representative scenario near U_small / U_medium
            for sc in h["variable_scenarios"]:
                if sc["rem_pool"] in (12, 16, 24, 32) and sc["add_pool"] in (24, 32, 48, 64):
                    lines.append(
                        f"  - Scenario rem={sc['rem_pool']} add={sc['add_pool']}: "
                        f"vars={sc['n_vars']}, CP-SAT={sc['cpsat_comfort']}, "
                        f"MILP={sc['milp_comfort']}, "
                        f"log10(shell)≈{sc['log10_shell_combinations']:.2f}."
                    )
        lines.append("")
    lines.append(
        "Guidance: start CP-SAT lazy on ≤~50–80 vars (U_small r=1); "
        "MILP only for very small Rem; avoid full-grid add pools at r≥2."
    )
    lines.append("")

    lines.append("## C3 — Proposed universes")
    lines.append("")
    for n in (64, 100):
        lines.append(f"### n={n}")
        lines.append("")
        for uid, u in results[n]["C3_universes"].items():
            sz = u["sizes"]
            lines.append(
                f"- **{uid}**: rem={sz['n_removable']}, add={sz['n_addable']}, "
                f"vars={sz['n_vars']}; r∈{u['applicable_hamming_r']}; "
                f"CP-SAT={u['comfort']['cpsat_comfort']}."
            )
            lines.append(f"  - Rule: {u['selection_rule']}")
            lines.append(f"  - Add regions: {u['add_region_counts']}")
        rec = results[n]["recommended_first_r1"]
        lines.append(
            f"- **Recommended first r=1:** {rec['universe_id']} "
            f"({rec['n_vars']} vars)."
        )
        lines.append("")

    lines.append("## Halo combination")
    lines.append("")
    lines.append(
        "Combine spatial Chebyshev halo, score-band expansion, and (future) blocker-graph "
        "halo from Agent A: `U := U_score ∪ spatial_halo ∪ blocker_halo`. "
        "Escalate U_small→medium→large / grow h only after scoped pilots. "
        "**Never** treat scoped UNSAT as global."
    )
    lines.append("")
    lines.append("## Files written")
    lines.append("")
    lines.append("- `scratch/audit/agent_c/density_hamming_diagnostics_n64.json`")
    lines.append("- `scratch/audit/agent_c/density_hamming_diagnostics_n100.json`")
    lines.append("- `scratch/audit/agent_c/universe_halo_diagnostics.json`")
    lines.append("- `scratch/audit/agent_c/agent_c_report.md`")
    lines.append("- `scratch/audit/agent_c/scripts/run_density_hamming_audit.py`")
    lines.append("")
    lines.append("## Parent return summary")
    lines.append("")
    a64 = halo["baselines"]["n64"]["recommended_first_r1"]
    a100 = halo["baselines"]["n100"]["recommended_first_r1"]
    lines.append(
        f"- First r=1 universe sizes: n64 U_small → {a64['n_vars']} vars "
        f"({a64['n_removable']} rem + {a64['n_addable']} add); "
        f"n100 U_small → {a100['n_vars']} vars "
        f"({a100['n_removable']} rem + {a100['n_addable']} add)."
    )
    lines.append(
        "- Key density: both baselines are boundary-heavy with large empty centers; "
        "n100 is fully 180°-symmetric, n64 ≈96.4%; direct +1 insertions have "
        f"zero-ΔV count n64={results[64]['C1_density']['direct_insertion']['n_zero_delta']}, "
        f"n100={results[100]['C1_density']['direct_insertion']['n_zero_delta']}."
    )
    lines.append("- Confirmed: no 165/113 search performed.")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
