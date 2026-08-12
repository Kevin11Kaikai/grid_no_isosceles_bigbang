"""Wave-2 Agent B: orbit / core / defect search with lazy conflict separation.

Exclusive module for Search Agent B. Encodes notebook 7-axis reflection
symmetries as orbit variables, with optional asymmetric defects and partial
orbit breaking. Uses CP-SAT with lazy isosceles cuts (same discipline as
`cpsat_lazy.py`).

Run with the solver venv only::

    .venv_solver/Scripts/python.exe -m src.search.orbit_defect_search ...

Hard rules (Wave 2):
- Scoped statuses only; TIMEOUT is never reported as INFEASIBLE.
- Restricted-model INFEASIBLE is not a global upper bound.
- Do not write results/certified; candidates go under scratch/agent_b/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from data.baselines.official_raw import SOL_100, SOL_64  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402

try:
    from ortools.sat.python import cp_model
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "ortools required; run via .venv_solver/Scripts/python.exe"
    ) from exc

Point = Tuple[int, int]
ROOT = Path(__file__).resolve().parents[2]
SCRATCH = ROOT / "scratch" / "agent_b"
DEFAULT_WORKERS = max(1, (os.cpu_count() or 4) // 4)  # ~25% logical cores
TARGETS = {64: 113, 100: 165}
BASELINE_HASH = {
    64: "47d42165b7804493a847e064494ef067e97bc8ac12121cd04ac19f23fee9c292",
    100: "8a84216d28f5afbbbd6b06301b159eab1b57c85bb814d78dd708da2be65cbdc1",
}
TYPE_COMMENTS = {
    0: "Reflection about (n-1)/2 axes (standard for n even, axes at X.5, Y.5)",
    1: "Reflection about n/2-1 axes (e.g. 31 for n=64, axes at X.0, Y.0)",
    2: "Reflection about n/2 axes (e.g. 32 for n=64, axes at X.0, Y.0)",
    3: "Mixed symmetry: x-axis at n/2, y-axis at (n-1)/2",
    4: "Mixed symmetry: x-axis at n/2-1, y-axis at (n-1)/2",
    5: "Mixed symmetry: x-axis at (n-1)/2, y-axis at n/2",
    6: "Mixed symmetry: x-axis at (n-1)/2, y-axis at n/2-1",
}

# Phase-2 policy ranking (phase0_neighborhood_policy.md §2.3)
AXIS_RANK = [0, 1, 2, 3, 4, 5, 6]
DEFECT_MANDATORY_TYPES = {0, 3, 4, 5, 6}
COMPARE_PURE_TYPES = {1, 2}


# ---------------------------------------------------------------------------
# Notebook transforms / orbit enumeration (Gate-1-compatible)
# ---------------------------------------------------------------------------


def offsets_for(n: int) -> List[Tuple[int, int]]:
    return [
        (n - 1, n - 1),
        (n - 2, n - 2),
        (n, n),
        (n, n - 1),
        (n - 2, n - 1),
        (n - 1, n),
        (n - 1, n - 2),
    ]


def get_symmetric_partners(p: Point, n: int, symmetry_type: int) -> Set[Point]:
    """Notebook `get_symmetric_partners` logic (verbatim)."""
    x, y = p
    ox, oy = offsets_for(n)[symmetry_type]
    sym_x, sym_y = ox - x, oy - y
    partners: Set[Point] = set()
    for px, py in ((sym_x, y), (x, sym_y), (sym_x, sym_y)):
        if (px, py) != p and 0 <= px < n and 0 <= py < n:
            partners.add((px, py))
    return partners


def formal_images(p: Point, ox: int, oy: int) -> Dict[str, Point]:
    x, y = p
    return {
        "id": (x, y),
        "rx": (ox - x, y),
        "ry": (x, oy - y),
        "rxy": (ox - x, oy - y),
    }


def in_grid(p: Point, n: int) -> bool:
    return 0 <= p[0] < n and 0 <= p[1] < n


def git_commit() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=str(ROOT), stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


def baseline_points(n: int) -> List[Point]:
    raw = SOL_64 if n == 64 else SOL_100
    return [(int(x), int(y)) for x, y in raw]


@dataclass
class Orbit:
    orbit_id: int
    repr: Point
    points: Tuple[Point, ...]
    size: int
    size_bucket: str  # "1"|"2"|"4"|"special"
    is_full: bool
    is_boundary_truncated: bool
    is_fixed_point_orbit: bool
    on_axis_x: bool
    on_axis_y: bool

    def as_public(self) -> Dict[str, Any]:
        return {
            "orbit_id": self.orbit_id,
            "repr": list(self.repr),
            "size": self.size,
            "size_bucket": self.size_bucket,
            "is_full": self.is_full,
            "is_boundary_truncated": self.is_boundary_truncated,
            "is_fixed_point_orbit": self.is_fixed_point_orbit,
            "on_axis_x": self.on_axis_x,
            "on_axis_y": self.on_axis_y,
            "points": [list(p) for p in self.points],
        }


def enumerate_orbits(n: int, symmetry_type: int) -> List[Orbit]:
    """Connected components under notebook partner relation (Gate-1 def)."""
    ox, oy = offsets_for(n)[symmetry_type]
    visited: Set[Point] = set()
    orbits: List[Orbit] = []
    oid = 0
    for x in range(n):
        for y in range(n):
            start = (x, y)
            if start in visited:
                continue
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
            for u in list(comp):
                for v in get_symmetric_partners(u, n, symmetry_type):
                    if v not in comp:
                        comp.add(v)
                        visited.add(v)
            rep = min(comp)
            formal = formal_images(rep, ox, oy)
            formal_in = {q for q in formal.values() if in_grid(q, n)}
            formal_all_in = all(in_grid(q, n) for q in formal.values())
            closed = True
            for u in comp:
                for v in get_symmetric_partners(u, n, symmetry_type):
                    if v not in comp:
                        closed = False
            is_full = formal_all_in and closed and (comp == formal_in)
            size = len(comp)
            if size in (1, 2, 4):
                bucket = str(size)
            else:
                bucket = "special"
            on_axis_x = any((ox % 2 == 0) and (p[0] == ox // 2) for p in comp)
            on_axis_y = any((oy % 2 == 0) and (p[1] == oy // 2) for p in comp)
            orbits.append(
                Orbit(
                    orbit_id=oid,
                    repr=rep,
                    points=tuple(sorted(comp)),
                    size=size,
                    size_bucket=bucket,
                    is_full=is_full,
                    is_boundary_truncated=not formal_all_in,
                    is_fixed_point_orbit=(size == 1),
                    on_axis_x=on_axis_x,
                    on_axis_y=on_axis_y,
                )
            )
            oid += 1
    assert sum(o.size for o in orbits) == n * n
    return orbits


def full_orbit_size_multiset(orbits: Sequence[Orbit]) -> Dict[str, int]:
    c = Counter(o.size for o in orbits if o.is_full)
    return {str(k): v for k, v in sorted(c.items())}


def subset_sum_reachable(sizes: Sequence[int], target: int) -> bool:
    if target < 0:
        return False
    if target == 0:
        return True
    dp = [False] * (target + 1)
    dp[0] = True
    for s in sizes:
        if s > target:
            continue
        for t in range(target - s, -1, -1):
            if dp[t]:
                dp[t + s] = True
        if dp[target]:
            return True
    return dp[target]


def cardinality_status_for_type(n: int, symmetry_type: int) -> Dict[str, Any]:
    orbits = enumerate_orbits(n, symmetry_type)
    full = [o for o in orbits if o.is_full]
    sizes = [o.size for o in full]
    target = TARGETS[n]
    even_only = all(s % 2 == 0 for s in sizes) and sizes
    reachable = subset_sum_reachable(sizes, target)
    if even_only and target % 2 == 1:
        proof = "All FULL orbit sizes are even, target is odd ⇒ impossible by parity."
        reachable = False
    else:
        proof = None if reachable else "FULL-orbit subset-sum cannot reach target."
    return {
        "n": n,
        "symmetry_type": symmetry_type,
        "offset": list(offsets_for(n)[symmetry_type]),
        "full_orbit_size_multiset": full_orbit_size_multiset(orbits),
        "num_full_orbits": len(full),
        "target": target,
        "reachable": reachable,
        "cardinality_status": (
            "cardinality_reachable_but_legality_open"
            if reachable
            else "cardinality_unreachable"
        ),
        "defects_required_for_cardinality": not reachable,
        "phase2_guidance": (
            "compare_pure_orbit_vs_orbit_plus_defect"
            if reachable
            else "defects_mandatory_for_target_cardinality"
        ),
        "proof_if_unreachable": proof,
    }


# ---------------------------------------------------------------------------
# Universe construction
# ---------------------------------------------------------------------------


def _load_agent_c_pools(n: int, universe_id: str = "U_medium") -> Dict[str, List[Point]]:
    path = ROOT / "scratch" / "audit" / "agent_c" / "universe_halo_diagnostics.json"
    if not path.exists():
        return {"addable": [], "removable": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    key = f"n{n}"
    u = data["baselines"][key]["universes"].get(universe_id, {})
    addable = [tuple(p) for p in u.get("addable_unselected_points", [])]
    removable = [tuple(p) for p in u.get("removable_baseline_points", [])]
    return {"addable": addable, "removable": removable}


def _cert_lb2_defect_freq(n: int) -> Dict[Point, int]:
    """Frequency of baseline-involved points / easy qs from Agent-A blocker detail.

    Used only to *rank* the defect pool (same pool family, different truncation order).
    """
    path = ROOT / "scratch" / "audit" / "agent_a" / f"blocker_detail_n{n}.json.gz"
    if not path.exists():
        return {}
    import gzip

    with gzip.open(path, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    freq: Dict[Point, int] = {}
    for r in detail.get("top_k_full_records", []):
        if int(r.get("lower_bound_min_deletions", 99)) > 2:
            continue
        q = (int(r["q"][0]), int(r["q"][1]))
        freq[q] = freq.get(q, 0) + 3
        for p in r.get("involved_baseline_points", []):
            pt = (int(p[0]), int(p[1]))
            freq[pt] = freq.get(pt, 0) + 1
    return freq


def _chebyshev(a: Point, b: Point) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _orbit_near_set(orbit: Orbit, seeds: Set[Point], radius: int) -> bool:
    for p in orbit.points:
        for s in seeds:
            if _chebyshev(p, s) <= radius:
                return True
    return False


@dataclass
class Universe:
    universe_id: str
    n: int
    symmetry_type: int
    core_orbit_ids: List[int]
    free_orbit_ids: List[int]  # may include core (soft)
    defect_points: List[Point]
    partial_orbit_ids: List[int]
    notes: Dict[str, Any] = field(default_factory=dict)

    def model_fingerprint(self) -> str:
        payload = {
            "universe_id": self.universe_id,
            "n": self.n,
            "symmetry_type": self.symmetry_type,
            "core": self.core_orbit_ids,
            "free": self.free_orbit_ids,
            "defects": [list(p) for p in self.defect_points],
            "partial": self.partial_orbit_ids,
        }
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()


def classify_baseline_orbits(
    n: int, symmetry_type: int, orbits: Sequence[Orbit]
) -> Dict[str, Any]:
    S = set(baseline_points(n))
    fully: List[int] = []
    partial: List[int] = []
    empty: List[int] = []
    for o in orbits:
        present = [p for p in o.points if p in S]
        if len(present) == o.size:
            fully.append(o.orbit_id)
        elif present:
            partial.append(o.orbit_id)
        else:
            empty.append(o.orbit_id)
    by_id = {o.orbit_id: o for o in orbits}
    return {
        "fully_present": fully,
        "partial": partial,
        "empty": empty,
        "core_points": sum(
            by_id[oid].size for oid in fully if by_id[oid].is_full
        ),
    }


def build_universe(
    n: int,
    symmetry_type: int,
    orbits: Sequence[Orbit],
    *,
    mode: str,
    halo_radius: int = 8,
    max_extra_orbits: int = 80,
    max_defect_pool: int = 96,
    agent_c_universe: str = "U_medium",
    include_truncated_as_partial: bool = True,
    defect_rank: str = "agent_c",
) -> Universe:
    """Build a scoped orbit/defect universe around the official baseline."""
    classif = classify_baseline_orbits(n, symmetry_type, orbits)
    by_id = {o.orbit_id: o for o in orbits}
    S = set(baseline_points(n))
    pools = _load_agent_c_pools(n, agent_c_universe)
    seed_pts = set(S) | set(pools["addable"]) | set(pools["removable"])

    core_full = [
        oid
        for oid in classif["fully_present"]
        if by_id[oid].is_full
    ]
    # Candidate empty FULL orbits near baseline / Agent-C pools
    empty_full_near: List[Tuple[int, int]] = []
    for oid in classif["empty"]:
        o = by_id[oid]
        if not o.is_full:
            continue
        # Prefer orbits intersecting Agent-C addable points
        hit_add = sum(1 for p in o.points if p in set(pools["addable"]))
        if hit_add or _orbit_near_set(o, seed_pts, halo_radius):
            # score: closer + more addable hits first
            mind = min((_chebyshev(p, s) for p in o.points for s in S), default=10**9)
            empty_full_near.append((-(hit_add), mind, oid))
    empty_full_near.sort()
    extra_ids = [oid for _, _, oid in empty_full_near[:max_extra_orbits]]

    free_ids = sorted(set(core_full) | set(extra_ids))
    # Always include FULL fixed-point orbits (size-1) for types 1/2
    for o in orbits:
        if o.is_full and o.is_fixed_point_orbit and o.orbit_id not in free_ids:
            free_ids.append(o.orbit_id)
    free_ids = sorted(set(free_ids))

    # Grow until cardinality can reach target (restricted universe still scoped).
    target = TARGETS[n]
    by_size_sum = sum(by_id[i].size for i in free_ids)
    if by_size_sum < target:
        ranked = []
        for oid in classif["empty"]:
            if oid in free_ids:
                continue
            o = by_id[oid]
            if not o.is_full:
                continue
            mind = min((_chebyshev(p, s) for p in o.points for s in S), default=10**9)
            ranked.append((mind, o.size, oid))
        ranked.sort()
        for mind, sz, oid in ranked:
            free_ids.append(oid)
            by_size_sum += sz
            if by_size_sum >= target + 32:
                break
        free_ids = sorted(set(free_ids))

    # Cap free orbit count for CP-SAT size, preferring closer orbits + core
    if len(free_ids) > max_extra_orbits + len(core_full) + 5:
        core_set = set(core_full)
        extras = [oid for oid in free_ids if oid not in core_set]
        # keep fixed-point / size-1/2 first
        extras.sort(
            key=lambda oid: (
                0 if by_id[oid].is_fixed_point_orbit else 1,
                by_id[oid].size,
                min((_chebyshev(p, s) for p in by_id[oid].points for s in S), default=10**9),
            )
        )
        keep = list(core_full) + extras[: max(max_extra_orbits, 40)]
        free_ids = sorted(set(keep))

    # Defect pool: Agent-C addables + points from partial orbits + halo of rem
    defect_set: Set[Point] = set()
    for p in pools["addable"]:
        defect_set.add(p)
    for oid in classif["partial"]:
        for p in by_id[oid].points:
            defect_set.add(p)
    # Halo around removable baseline points
    for r in pools["removable"]:
        for dx in range(-halo_radius, halo_radius + 1):
            for dy in range(-halo_radius, halo_radius + 1):
                if max(abs(dx), abs(dy)) > halo_radius:
                    continue
                q = (r[0] + dx, r[1] + dy)
                if in_grid(q, n) and q not in S:
                    defect_set.add(q)
    # Points from empty free orbits can also be single-point defects when that
    # orbit is not selected (disjointness). Prefer Agent-C / near-baseline.
    for oid in free_ids:
        if by_id[oid].orbit_id in core_full:
            continue
        for p in by_id[oid].points:
            defect_set.add(p)

    free_point_set = set()
    for oid in free_ids:
        free_point_set.update(by_id[oid].points)

    partial_ids: List[int] = []
    if mode in ("partial", "defect_partial"):
        cand = list(classif["partial"]) + [
            oid for oid in free_ids if oid not in core_full
        ][:24]
        for oid in cand:
            o = by_id[oid]
            if o.size >= 2:
                partial_ids.append(oid)
        partial_ids = sorted(set(partial_ids))[:40]

    if mode == "pure":
        defect_points: List[Point] = []
    else:
        # Keep defects even if they lie in some free orbit; disjointness constraints
        # prevent double-counting. Filtering them out made odd targets with a full
        # Type-0 core cardinality-infeasible (no exterior defect vars left).
        add_set = set(pools["addable"])
        cert_freq = _cert_lb2_defect_freq(n) if defect_rank == "cert_lb2" else {}
        cleaned = sorted(
            defect_set,
            key=lambda p: (
                -cert_freq.get(p, 0),
                0 if p in add_set else 1,
                0 if p not in free_point_set else 1,
                p[0],
                p[1],
            ),
        )
        defect_points = cleaned[:max_defect_pool]

    rank_tag = "" if defect_rank in ("", "agent_c") else f"_rk{defect_rank}"
    uid = (
        f"orb_t{symmetry_type}_{mode}_core{len(core_full)}_free{len(free_ids)}"
        f"_def{len(defect_points)}_part{len(partial_ids)}_h{halo_radius}{rank_tag}"
    )
    return Universe(
        universe_id=uid,
        n=n,
        symmetry_type=symmetry_type,
        core_orbit_ids=core_full,
        free_orbit_ids=free_ids,
        defect_points=defect_points,
        partial_orbit_ids=partial_ids,
        notes={
            "halo_radius": halo_radius,
            "max_extra_orbits": max_extra_orbits,
            "max_defect_pool": max_defect_pool,
            "agent_c_universe": agent_c_universe,
            "defect_rank": defect_rank,
            "baseline_fully_present_full": len(core_full),
            "baseline_partial": len(classif["partial"]),
            "include_truncated_as_partial": include_truncated_as_partial,
            "core_points": classif["core_points"],
        },
    )


# ---------------------------------------------------------------------------
# Lazy conflict helpers
# ---------------------------------------------------------------------------


def _sq_dist(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def find_violation_triples(points: Sequence[Point]) -> List[Tuple[Point, Point, Point]]:
    """Return (pivot, a, c) for every isosceles conflict (pivot uniqueness)."""
    pts = list(points)
    triples: List[Tuple[Point, Point, Point]] = []
    for p in pts:
        groups: Dict[int, List[Point]] = {}
        for q in pts:
            if q == p:
                continue
            groups.setdefault(_sq_dist(p, q), []).append(q)
        for members in groups.values():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    triples.append((p, members[i], members[j]))
    return triples


def conflict_kind(
    pivot: Point,
    a: Point,
    c: Point,
    point_to_orbit: Dict[Point, int],
    orbits: Sequence[Orbit],
) -> str:
    ids = {point_to_orbit.get(pivot), point_to_orbit.get(a), point_to_orbit.get(c)}
    ids.discard(None)
    if len(ids) <= 1:
        return "intra_orbit"
    if len(ids) == 2:
        return "two_orbit"
    return "three_orbit"


# ---------------------------------------------------------------------------
# CP-SAT orbit/defect search
# ---------------------------------------------------------------------------


@dataclass
class SearchConfig:
    n: int
    symmetry_type: int
    mode: str  # pure | defect | partial
    target_size: int
    defect_budget_min: int = 0
    defect_budget_max: int = 0
    time_budget_s: float = 60.0
    per_round_time_limit_s: float = 20.0
    seed: int = 0
    num_workers: int = DEFAULT_WORKERS
    halo_radius: int = 8
    max_extra_orbits: int = 80
    max_defect_pool: int = 96
    agent_c_universe: str = "U_medium"
    defect_rank: str = "agent_c"  # agent_c | cert_lb2 (defect pool truncation order)
    max_cuts_per_round: int = 50000
    soft_core: bool = True  # core orbits hintable / preferred, not hard-fixed
    fix_core: bool = False  # if True, force all baseline FULL orbits on


def _model_hash(cfg: SearchConfig, universe: Universe, extra: Dict[str, Any]) -> str:
    payload = {
        "cfg": asdict(cfg),
        "universe_fp": universe.model_fingerprint(),
        "extra": extra,
        "module": "orbit_defect_search",
        "version": 1,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


def solve_orbit_defect(cfg: SearchConfig) -> Dict[str, Any]:
    """Feasibility search for |S|=target under orbit/defect/partial encoding."""
    t0 = time.time()
    orbits = enumerate_orbits(cfg.n, cfg.symmetry_type)
    by_id = {o.orbit_id: o for o in orbits}
    point_to_orbit = {p: o.orbit_id for o in orbits for p in o.points}

    mode = cfg.mode
    if mode == "pure" and cfg.symmetry_type in DEFECT_MANDATORY_TYPES:
        # Cardinality unreachable — refuse pure mode with explicit status.
        card = cardinality_status_for_type(cfg.n, cfg.symmetry_type)
        return {
            "schema": "grid_no_isosceles.search_result.v1",
            "method": "orbit_defect_search",
            "n": cfg.n,
            "target_size": cfg.target_size,
            "symmetry_type": cfg.symmetry_type,
            "axis_offset": list(offsets_for(cfg.n)[cfg.symmetry_type]),
            "mode": mode,
            "defect_budget": [cfg.defect_budget_min, cfg.defect_budget_max],
            "solver_status": "SKIPPED_CARDINALITY_UNREACHABLE",
            "cardinality": card,
            "wall_time_s": time.time() - t0,
            "seed": cfg.seed,
            "git_commit": git_commit(),
            "points": [],
            "size": 0,
            "note": "Pure FULL-orbit cardinality cannot reach odd target; use defect/partial.",
        }

    universe = build_universe(
        cfg.n,
        cfg.symmetry_type,
        orbits,
        mode=mode,
        halo_radius=cfg.halo_radius,
        max_extra_orbits=cfg.max_extra_orbits,
        max_defect_pool=cfg.max_defect_pool,
        agent_c_universe=cfg.agent_c_universe,
        defect_rank=cfg.defect_rank,
    )

    free_orbit_ids = list(universe.free_orbit_ids)
    partial_ids = set(universe.partial_orbit_ids) if mode in ("partial", "defect_partial") else set()
    # Orbits selected all-or-nothing (not partially broken)
    atomic_ids = [oid for oid in free_orbit_ids if oid not in partial_ids]
    defect_pts = list(universe.defect_points) if mode != "pure" else []

    # Point variables for partial orbits + defects
    partial_points: Dict[int, List[Point]] = {
        oid: list(by_id[oid].points) for oid in partial_ids
    }

    model_extra = {
        "atomic_orbit_ids": atomic_ids,
        "partial_orbit_ids": sorted(partial_ids),
        "n_defect_vars": len(defect_pts),
        "fix_core": cfg.fix_core,
        "soft_core": cfg.soft_core,
    }
    mhash = _model_hash(cfg, universe, model_extra)

    cuts: Set[Tuple[str, Tuple[Any, ...]]] = set()
    # Cut encoding: ("orbit", (o1,o2,o3)) or ("point", (p1,p2,p3)) with sorted ids/points
    round_log: List[Dict[str, Any]] = []
    best_legal: List[Point] = []
    terminal_status = "TIMEOUT"
    rounds = 0
    last_ckpt = t0
    ckpt_every_s = 300.0  # 5 min cadence during long solves

    def _maybe_mid_checkpoint(force: bool = False) -> None:
        nonlocal last_ckpt
        now = time.time()
        if not force and (now - last_ckpt) < ckpt_every_s:
            return
        last_ckpt = now
        ensure_scratch()
        mid = {
            "phase": "solve_mid_checkpoint",
            "n": cfg.n,
            "symmetry_type": cfg.symmetry_type,
            "mode": mode,
            "defect_budget": [cfg.defect_budget_min, cfg.defect_budget_max],
            "seed": cfg.seed,
            "rounds": rounds,
            "cuts": len(cuts),
            "elapsed_s": now - t0,
            "model_hash": mhash,
            "universe_id": universe.universe_id,
            "git_commit": git_commit(),
            "best_legal_size": len(best_legal),
        }
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = (
            SCRATCH
            / "checkpoints"
            / f"mid_n{cfg.n}_t{cfg.symmetry_type}_{mode}_s{cfg.seed}_{ts}.json"
        )
        path.write_text(json.dumps(mid, indent=2), encoding="utf-8")
        append_manifest(mid)

    def rebuild_and_solve(remaining_s: float) -> Tuple[str, Optional[List[Point]], Dict[str, Any]]:
        nonlocal rounds
        rounds += 1
        model = cp_model.CpModel()
        y = {oid: model.NewBoolVar(f"y{oid}") for oid in atomic_ids}
        z: Dict[Point, Any] = {}
        for p in defect_pts:
            z[p] = model.NewBoolVar(f"z{p[0]}_{p[1]}")
        # Partial: per-point vars; optional "all" var linking
        w: Dict[Point, Any] = {}
        for oid, pts in partial_points.items():
            for p in pts:
                w[p] = model.NewBoolVar(f"w{p[0]}_{p[1]}")

        # Size expression
        size_terms = []
        for oid, var in y.items():
            size_terms.append(by_id[oid].size * var)
        for p, var in z.items():
            size_terms.append(var)
        for p, var in w.items():
            size_terms.append(var)
        model.Add(sum(size_terms) == cfg.target_size)

        # Defect budget on asymmetric points z (not partial w — those are breaking)
        if z:
            dsum = sum(z.values())
            model.Add(dsum >= cfg.defect_budget_min)
            model.Add(dsum <= cfg.defect_budget_max)
        elif mode == "defect" and cfg.defect_budget_min > 0:
            # No defect vars available in universe — immediate scoped infeasible
            return "INFEASIBLE", None, {"reason": "empty_defect_pool"}

        # Disjointness: defect point cannot also be covered by a selected atomic orbit
        pt_to_atomic = {}
        for oid in atomic_ids:
            for p in by_id[oid].points:
                pt_to_atomic[p] = oid
        for p, var in z.items():
            if p in pt_to_atomic:
                model.Add(var + y[pt_to_atomic[p]] <= 1)
            if p in w:
                model.Add(var + w[p] <= 1)

        # Partial orbit: cannot also select as atomic (already excluded)
        # Optional: at most size-1 less than full for "breaking" signal
        for oid, pts in partial_points.items():
            # Allow any subset; encourage incompleteness when mode is partial
            model.Add(sum(w[p] for p in pts) <= by_id[oid].size)

        if cfg.fix_core:
            for oid in universe.core_orbit_ids:
                if oid in y:
                    model.Add(y[oid] == 1)

        # Apply accumulated cuts
        for kind, payload in cuts:
            if kind == "orbit":
                oids = [oid for oid in payload if oid in y]
                if len(oids) >= 2:
                    model.Add(sum(y[oid] for oid in oids) <= len(oids) - 1)
                elif len(oids) == 1:
                    model.Add(y[oids[0]] == 0)
            elif kind == "point":
                bools = []
                for pt in payload:
                    p = (pt[0], pt[1])
                    if p in z:
                        bools.append(z[p])
                    if p in w:
                        bools.append(w[p])
                    # If point is inside an atomic orbit, the orbit var covers it
                    if p in pt_to_atomic and pt_to_atomic[p] in y:
                        bools.append(y[pt_to_atomic[p]])
                # Unique bools
                uniq = []
                seen = set()
                for b in bools:
                    if id(b) not in seen:
                        seen.add(id(b))
                        uniq.append(b)
                if len(uniq) >= 2:
                    model.Add(sum(uniq) <= 2)
                elif len(uniq) == 1:
                    model.Add(uniq[0] == 0)
            elif kind == "nogood":
                # payload: tuple of ("orbit", oid) / ("def", point)
                lits = []
                for item in payload:
                    if item[0] == "orbit" and item[1] in y:
                        lits.append(y[item[1]])
                    elif item[0] == "def":
                        p = item[1]
                        if p in z:
                            lits.append(z[p])
                        if p in w:
                            lits.append(w[p])
                if lits:
                    model.Add(sum(lits) <= len(lits) - 1)

        # Hints from baseline core (optional; never required for correctness)
        if cfg.soft_core and universe.core_orbit_ids:
            try:
                for oid in universe.core_orbit_ids:
                    if oid in y:
                        model.AddHint(y[oid], 1)
            except Exception:
                pass

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max(0.5, remaining_s)
        solver.parameters.random_seed = cfg.seed + rounds
        solver.parameters.num_search_workers = max(1, cfg.num_workers)
        status_code = solver.Solve(model)
        name = solver.StatusName(status_code)
        info = {"round": rounds, "cpsat_status": name, "t": time.time() - t0}

        if status_code == cp_model.INFEASIBLE:
            return "INFEASIBLE", None, info
        if status_code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return "TIMEOUT", None, info

        selected: List[Point] = []
        for oid, var in y.items():
            if solver.Value(var) == 1:
                selected.extend(by_id[oid].points)
        for p, var in z.items():
            if solver.Value(var) == 1:
                selected.append(p)
        for p, var in w.items():
            if solver.Value(var) == 1:
                selected.append(p)
        # Unique
        selected = sorted(set(selected))
        info["selected_size"] = len(selected)
        return name, selected, info

    while time.time() - t0 < cfg.time_budget_s:
        _maybe_mid_checkpoint()
        remaining = cfg.time_budget_s - (time.time() - t0)
        # Escalate per-round time as the cut set grows / late search.
        round_limit = min(
            max(cfg.per_round_time_limit_s, 15.0 + 0.01 * len(cuts)),
            remaining,
            120.0,
        )
        if round_limit < 0.5:
            break
        status_name, selected, info = rebuild_and_solve(round_limit)
        info["cuts"] = len(cuts)
        round_log.append(info)

        if status_name == "INFEASIBLE":
            terminal_status = "INFEASIBLE"
            break
        if selected is None:
            # Round-level UNKNOWN/TIMEOUT: keep spending remaining wall budget.
            if time.time() - t0 >= cfg.time_budget_s - 0.5:
                terminal_status = "TIMEOUT"
                break
            continue

        triples = find_violation_triples(selected)
        info["violations"] = len(triples)
        if not triples:
            ok, witness = is_legal_pivot_method(selected, cfg.n)
            if not ok:
                raise AssertionError(
                    f"lazy cuts empty but oracle illegal: {witness}"
                )
            best_legal = selected
            # Distinguish OPTIMAL vs FEASIBLE from last CP-SAT status
            last = info.get("cpsat_status", "FEASIBLE")
            terminal_status = "OPTIMAL" if last == "OPTIMAL" else "FEASIBLE"
            break

        added = 0
        for pivot, a, c in triples:
            if added >= cfg.max_cuts_per_round:
                break
            kind = conflict_kind(pivot, a, c, point_to_orbit, orbits)
            oids = []
            for p in (pivot, a, c):
                oid = point_to_orbit.get(p)
                if oid is not None and oid in atomic_ids:
                    oids.append(oid)
            oids_u = tuple(sorted(set(oids)))
            # Prefer orbit-level cut when all three points are covered by atomic orbits
            pts_u = tuple(sorted([(pivot[0], pivot[1]), (a[0], a[1]), (c[0], c[1])]))
            if len(oids_u) >= 1 and all(
                point_to_orbit.get(p) in atomic_ids for p in (pivot, a, c)
            ):
                cut = ("orbit", oids_u)
            else:
                cut = ("point", pts_u)
            if cut not in cuts:
                cuts.add(cut)
                added += 1
                _ = kind  # kinds covered: intra/2/3-orbit + fixed via orbit cuts
        info["cuts_added"] = added
        if added == 0:
            # Incumbent still illegal but produced no new conflict cuts (duplicate
            # mapping). Add a no-good on the current atomic orbit support so search
            # must diversify, then continue within wall budget.
            support = []
            # Rebuild support from selected points via atomic orbits / defects
            selected_set = set(selected)
            for oid in atomic_ids:
                pts = by_id[oid].points
                if pts and all(p in selected_set for p in pts):
                    support.append(("orbit", oid))
            for p in defect_pts:
                if p in selected_set:
                    support.append(("def", p))
            nogood = ("nogood", tuple(support))
            if nogood not in cuts and support:
                cuts.add(nogood)
                info["nogood_added"] = True
            elif time.time() - t0 >= cfg.time_budget_s - 0.5:
                terminal_status = "TIMEOUT"
                break
            # If we cannot diversify further, keep trying until budget (solver seed changes)
            continue

    _maybe_mid_checkpoint(force=True)

    wall = time.time() - t0
    # Defect accounting on best_legal
    defect_account = None
    if best_legal:
        defect_account = account_defects(
            best_legal, cfg.n, cfg.symmetry_type, orbits
        )

    verify_A = None
    verify_B = None
    if best_legal:
        ok_a, wit_a = is_legal_pivot_method(best_legal, cfg.n)
        verify_A = {"pass": ok_a, "witness": None if ok_a else wit_a}
        try:
            from src.verification_independent.independent_verifier import (
                verify_independent,
            )

            ok_b, wit_b = verify_independent(best_legal, cfg.n)
            verify_B = {"pass": ok_b, "witness": wit_b}
        except Exception as exc:  # pragma: no cover
            verify_B = {"pass": False, "error": str(exc)}

    result = {
        "schema": "grid_no_isosceles.search_result.v1",
        "method": "orbit_defect_search",
        "n": cfg.n,
        "target_size": cfg.target_size,
        "symmetry_type": cfg.symmetry_type,
        "axis_offset": list(offsets_for(cfg.n)[cfg.symmetry_type]),
        "axis_comment": TYPE_COMMENTS[cfg.symmetry_type],
        "mode": mode,
        "defect_budget": {
            "min": cfg.defect_budget_min,
            "max": cfg.defect_budget_max,
        },
        "core_def": {
            "soft_core": cfg.soft_core,
            "fix_core": cfg.fix_core,
            "n_core_orbits": len(universe.core_orbit_ids),
            "core_orbit_ids": universe.core_orbit_ids,
            "core_points_note": universe.notes.get("core_points"),
        },
        "universe": {
            "universe_id": universe.universe_id,
            "fingerprint": universe.model_fingerprint(),
            "n_free_orbits": len(universe.free_orbit_ids),
            "n_defect_points": len(universe.defect_points),
            "n_partial_orbits": len(universe.partial_orbit_ids),
            "notes": universe.notes,
        },
        "model_hash": mhash,
        "solver_status": terminal_status,
        "wall_time_s": wall,
        "time_budget_s": cfg.time_budget_s,
        "seed": cfg.seed,
        "num_workers": cfg.num_workers,
        "git_commit": git_commit(),
        "rounds": rounds,
        "final_cuts": len(cuts),
        "round_log": round_log,
        "points": [list(p) for p in best_legal],
        "size": len(best_legal),
        "points_hash": sha256_of_points(best_legal) if best_legal else None,
        "parent_hash": BASELINE_HASH.get(cfg.n),
        "defect_accounting": defect_account,
        "verify": {"A": verify_A, "B": verify_B},
        "scope": {
            "n": cfg.n,
            "symmetry_type": cfg.symmetry_type,
            "mode": mode,
            "defect_budget": [cfg.defect_budget_min, cfg.defect_budget_max],
            "universe_id": universe.universe_id,
            "time_limit_s": cfg.time_budget_s,
            "seed": cfg.seed,
            "model_hash": mhash,
        },
    }
    # Explicit INFEASIBLE field bundle (required by Wave-2 contract)
    if terminal_status == "INFEASIBLE":
        result["infeasible_record"] = {
            "n": cfg.n,
            "axis": cfg.symmetry_type,
            "mode": mode,
            "defect_budget": [cfg.defect_budget_min, cfg.defect_budget_max],
            "core_def": result["core_def"],
            "universe": universe.universe_id,
            "time_s": wall,
            "status": "INFEASIBLE",
            "model_hash": mhash,
            "note": "Scoped to this universe/mode only; not a global upper bound.",
        }
    return result


def account_defects(
    points: Sequence[Point],
    n: int,
    symmetry_type: int,
    orbits: Optional[Sequence[Orbit]] = None,
) -> Dict[str, Any]:
    """Classify selected points into full orbits vs asymmetric defects."""
    if orbits is None:
        orbits = enumerate_orbits(n, symmetry_type)
    S = set(tuple(p) for p in points)
    full_selected = []
    partial_selected = []
    for o in orbits:
        present = [p for p in o.points if p in S]
        if not present:
            continue
        if len(present) == o.size and o.is_full:
            full_selected.append(o.orbit_id)
        else:
            partial_selected.append(
                {
                    "orbit_id": o.orbit_id,
                    "size": o.size,
                    "present": len(present),
                    "is_full_type": o.is_full,
                    "points": [list(p) for p in present],
                }
            )
    core_pts = set()
    by_id = {o.orbit_id: o for o in orbits}
    for oid in full_selected:
        core_pts.update(by_id[oid].points)
    defects = sorted(S - core_pts)
    return {
        "n_full_orbits_selected": len(full_selected),
        "core_size": len(core_pts),
        "n_partial_orbits": len(partial_selected),
        "n_defect_points": len(defects),
        "defect_points": [list(p) for p in defects],
        "partial_orbits": partial_selected[:20],
        "size_check": len(core_pts) + len(defects) == len(S),
    }


# ---------------------------------------------------------------------------
# I/O / checkpoints / dual verify to scratch
# ---------------------------------------------------------------------------


def ensure_scratch() -> Path:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    (SCRATCH / "checkpoints").mkdir(parents=True, exist_ok=True)
    (SCRATCH / "candidates").mkdir(parents=True, exist_ok=True)
    return SCRATCH


def append_manifest(record: Dict[str, Any]) -> None:
    ensure_scratch()
    path = SCRATCH / "manifest.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def save_checkpoint(result: Dict[str, Any], tag: str) -> Path:
    ensure_scratch()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = SCRATCH / "checkpoints" / f"{tag}_{ts}.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return path


def maybe_save_candidate(result: Dict[str, Any]) -> Optional[Path]:
    """If legal and size >= target, dual-verify and save under scratch (not certified)."""
    n = result["n"]
    target = result["target_size"]
    pts = [tuple(p) for p in result.get("points") or []]
    if len(pts) < target:
        return None
    ok_a, _ = is_legal_pivot_method(pts, n)
    if not ok_a:
        return None
    from src.verification_independent.independent_verifier import verify_independent

    ok_b, wit_b = verify_independent(pts, n)
    ensure_scratch()
    path = (
        SCRATCH
        / "candidates"
        / f"n{n}_k{len(pts)}_t{result['symmetry_type']}_{result['mode']}_seed{result['seed']}.json"
    )
    payload = {
        "problem": "grid_no_isosceles",
        "n": n,
        "size": len(pts),
        "coordinate_convention": "0_to_n_minus_1",
        "points": [list(p) for p in pts],
        "search_method": "orbit_defect_search",
        "seed": result["seed"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": result.get("git_commit"),
        "status": "DUAL_VERIFIED_SCRATCH" if (ok_a and ok_b) else "SINGLE_OR_FAIL",
        "verifier_A_pass": ok_a,
        "verifier_B_pass": ok_b,
        "verifier_B_witness": wit_b,
        "points_hash": sha256_of_points(pts),
        "parent_hash": BASELINE_HASH.get(n),
        "model_hash": result.get("model_hash"),
        "scope": result.get("scope"),
        "note": "Scratch dual-verify only; NOT certified. Do not promote without Main certify.",
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Pilots
# ---------------------------------------------------------------------------


def run_axis_smoke(
    n: int = 64,
    time_per_axis_s: float = 45.0,
    seed: int = 1,
    num_workers: int = DEFAULT_WORKERS,
    summary_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Short smoke across all 7 axis types."""
    ensure_scratch()
    target = TARGETS[n]
    rows = []
    t0 = time.time()
    for t in range(7):
        if t in COMPARE_PURE_TYPES:
            modes = [("pure", 0, 0), ("defect", 1, 5)]
        else:
            # Odd targets need d ≡ target (mod gcd); keep budget up to 8.
            modes = [("defect", 1, 8)]
        for mode, dmin, dmax in modes:
            cfg = SearchConfig(
                n=n,
                symmetry_type=t,
                mode=mode,
                target_size=target,
                defect_budget_min=dmin,
                defect_budget_max=dmax,
                time_budget_s=time_per_axis_s,
                per_round_time_limit_s=min(20.0, time_per_axis_s),
                seed=seed,
                num_workers=num_workers,
                max_extra_orbits=60 if n == 64 else 80,
                max_defect_pool=64 if n == 64 else 96,
                halo_radius=8,
            )
            result = solve_orbit_defect(cfg)
            ck = save_checkpoint(
                result, f"smoke_n{n}_t{t}_{mode}_d{dmin}-{dmax}_s{seed}"
            )
            cand = maybe_save_candidate(result)
            row = {
                "n": n,
                "symmetry_type": t,
                "mode": mode,
                "defect_budget": [dmin, dmax],
                "status": result["solver_status"],
                "size": result.get("size", 0),
                "wall_time_s": result.get("wall_time_s"),
                "model_hash": result.get("model_hash"),
                "universe_id": (result.get("universe") or {}).get("universe_id"),
                "infeasible_record": result.get("infeasible_record"),
                "checkpoint": str(ck),
                "candidate": str(cand) if cand else None,
            }
            rows.append(row)
            append_manifest({**row, "phase": "smoke", "git_commit": git_commit()})
    summary = {
        "phase": "axis_smoke",
        "n": n,
        "target": target,
        "seed": seed,
        "num_workers": num_workers,
        "git_commit": git_commit(),
        "wall_time_s": time.time() - t0,
        "rows": rows,
    }
    out = summary_path or (SCRATCH / f"axis_smoke_n{n}.json")
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_long_pilot(cfg: SearchConfig, tag: str) -> Dict[str, Any]:
    """One scoped solve with full pilot budget; checkpoint start/final (~5–10 min cadence via wall)."""
    ensure_scratch()
    t0 = time.time()
    start_meta = {
        "phase": "long_pilot_start",
        "tag": tag,
        "n": cfg.n,
        "symmetry_type": cfg.symmetry_type,
        "mode": cfg.mode,
        "defect_budget": [cfg.defect_budget_min, cfg.defect_budget_max],
        "time_budget_s": cfg.time_budget_s,
        "seed": cfg.seed,
        "git_commit": git_commit(),
        "axis_type": cfg.symmetry_type,
    }
    append_manifest(start_meta)
    (SCRATCH / "checkpoints" / f"{tag}_start.json").write_text(
        json.dumps(start_meta, indent=2), encoding="utf-8"
    )

    last = solve_orbit_defect(cfg)
    cand = maybe_save_candidate(last)
    last["candidate_path"] = str(cand) if cand else None
    last["pilot_tag"] = tag
    last["pilot_wall_time_s"] = time.time() - t0
    ck = save_checkpoint(last, f"{tag}_final")
    append_manifest(
        {
            "phase": "long_pilot_final",
            "tag": tag,
            "status": last["solver_status"],
            "size": last.get("size", 0),
            "wall_time_s": last.get("pilot_wall_time_s"),
            "model_hash": last.get("model_hash"),
            "checkpoint": str(ck),
            "candidate": last.get("candidate_path"),
            "n": cfg.n,
            "symmetry_type": cfg.symmetry_type,
            "mode": cfg.mode,
            "defect_budget": [cfg.defect_budget_min, cfg.defect_budget_max],
            "git_commit": git_commit(),
            "seed": cfg.seed,
        }
    )
    return last


def run_wave2_pilots(
    total_budget_s: float = 5 * 3600,
    num_workers: int = DEFAULT_WORKERS,
    seed_base: int = 11,
) -> Dict[str, Any]:
    """Policy-ranked pilots: Type0 defects → Types1–2 pure/defect → 3–6 defects."""
    ensure_scratch()
    t0 = time.time()
    smoke64 = run_axis_smoke(
        n=64, time_per_axis_s=30.0, seed=seed_base, num_workers=num_workers
    )
    smoke100 = run_axis_smoke(
        n=100, time_per_axis_s=25.0, seed=seed_base + 1, num_workers=num_workers
    )
    combined_smoke = {
        "phase": "axis_smoke_combined",
        "git_commit": git_commit(),
        "num_workers": num_workers,
        "n64": smoke64,
        "n100": smoke100,
    }
    (SCRATCH / "axis_smoke_summary.json").write_text(
        json.dumps(combined_smoke, indent=2), encoding="utf-8"
    )

    n100_runs: List[Dict[str, Any]] = []
    n64_runs: List[Dict[str, Any]] = []

    def remaining() -> float:
        return total_budget_s - (time.time() - t0)

    # Long pilot schedule (approx minutes)
    schedule = [
        # n100 Type0 defects (primary)
        dict(n=100, t=0, mode="defect", dmin=1, dmax=8, minutes=50, seed=seed_base + 10),
        dict(n=100, t=0, mode="partial", dmin=1, dmax=8, minutes=35, seed=seed_base + 11),
        # n100 Types 1–2 pure then defect
        dict(n=100, t=1, mode="pure", dmin=0, dmax=0, minutes=40, seed=seed_base + 20),
        dict(n=100, t=1, mode="defect", dmin=1, dmax=8, minutes=35, seed=seed_base + 21),
        dict(n=100, t=2, mode="pure", dmin=0, dmax=0, minutes=40, seed=seed_base + 22),
        dict(n=100, t=2, mode="defect", dmin=1, dmax=8, minutes=30, seed=seed_base + 23),
        # n64 Type0 defects (secondary target)
        dict(n=64, t=0, mode="defect", dmin=1, dmax=8, minutes=40, seed=seed_base + 30),
        dict(n=64, t=1, mode="pure", dmin=0, dmax=0, minutes=30, seed=seed_base + 31),
        dict(n=64, t=1, mode="defect", dmin=1, dmax=8, minutes=25, seed=seed_base + 32),
        # Types 3–6 defect-mandatory (shorter)
        dict(n=100, t=3, mode="defect", dmin=1, dmax=8, minutes=25, seed=seed_base + 40),
        dict(n=100, t=4, mode="defect", dmin=1, dmax=8, minutes=20, seed=seed_base + 41),
        dict(n=64, t=3, mode="defect", dmin=1, dmax=8, minutes=20, seed=seed_base + 42),
        dict(n=100, t=5, mode="defect", dmin=1, dmax=8, minutes=18, seed=seed_base + 43),
        dict(n=100, t=6, mode="defect", dmin=1, dmax=8, minutes=18, seed=seed_base + 44),
    ]

    for spec in schedule:
        if remaining() < 120:
            break
        minutes = spec["minutes"]
        budget = min(minutes * 60.0, remaining() - 60)
        if budget < 90:
            break
        cfg = SearchConfig(
            n=spec["n"],
            symmetry_type=spec["t"],
            mode=spec["mode"],
            target_size=TARGETS[spec["n"]],
            defect_budget_min=spec["dmin"],
            defect_budget_max=spec["dmax"],
            time_budget_s=budget,
            per_round_time_limit_s=30.0,
            seed=spec["seed"],
            num_workers=num_workers,
            max_extra_orbits=100 if spec["n"] == 100 else 80,
            max_defect_pool=120 if spec["n"] == 100 else 80,
            halo_radius=8,
            agent_c_universe="U_medium",
        )
        tag = f"long_n{spec['n']}_t{spec['t']}_{spec['mode']}_d{spec['dmin']}-{spec['dmax']}_s{spec['seed']}"
        result = run_long_pilot(cfg, tag)
        entry = {
            "tag": tag,
            "n": spec["n"],
            "symmetry_type": spec["t"],
            "mode": spec["mode"],
            "defect_budget": [spec["dmin"], spec["dmax"]],
            "status": result["solver_status"],
            "size": result.get("size", 0),
            "wall_time_s": result.get("pilot_wall_time_s", result.get("wall_time_s")),
            "model_hash": result.get("model_hash"),
            "universe_id": (result.get("universe") or {}).get("universe_id"),
            "candidate": result.get("candidate_path"),
            "verify": result.get("verify"),
            "infeasible_record": result.get("infeasible_record"),
            "scope": result.get("scope"),
        }
        if spec["n"] == 100:
            n100_runs.append(entry)
        else:
            n64_runs.append(entry)
        append_manifest({**entry, "phase": "long_pilot", "git_commit": git_commit()})

    def best_of(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        legal = [r for r in runs if (r.get("size") or 0) >= TARGETS.get(r["n"], 10**9)]
        if legal:
            legal.sort(key=lambda r: -r["size"])
            return legal[0]
        # else best status preference
        if not runs:
            return {}
        return max(runs, key=lambda r: (r.get("size") or 0, r.get("wall_time_s") or 0))

    n100_summary = {
        "n": 100,
        "target": 165,
        "git_commit": git_commit(),
        "num_workers": num_workers,
        "smoke_ref": "axis_smoke_summary.json",
        "runs": n100_runs,
        "best": best_of(n100_runs),
        "wall_time_s": sum(r.get("wall_time_s") or 0 for r in n100_runs),
        "any_legal_plus1": any((r.get("size") or 0) >= 165 for r in n100_runs),
    }
    n64_summary = {
        "n": 64,
        "target": 113,
        "git_commit": git_commit(),
        "num_workers": num_workers,
        "runs": n64_runs,
        "best": best_of(n64_runs),
        "wall_time_s": sum(r.get("wall_time_s") or 0 for r in n64_runs),
        "any_legal_plus1": any((r.get("size") or 0) >= 113 for r in n64_runs),
    }
    (SCRATCH / "n100_orbit_defect_summary.json").write_text(
        json.dumps(n100_summary, indent=2), encoding="utf-8"
    )
    (SCRATCH / "n64_orbit_defect_summary.json").write_text(
        json.dumps(n64_summary, indent=2), encoding="utf-8"
    )

    report = _write_report(smoke64, smoke100, n100_summary, n64_summary, time.time() - t0)
    return {
        "smoke64": smoke64,
        "smoke100": smoke100,
        "n100": n100_summary,
        "n64": n64_summary,
        "report_path": str(report),
        "total_wall_time_s": time.time() - t0,
    }


def _write_report(
    smoke64: Dict[str, Any],
    smoke100: Dict[str, Any],
    n100: Dict[str, Any],
    n64: Dict[str, Any],
    wall: float,
) -> Path:
    ensure_scratch()
    lines = [
        "# Agent B Wave-2 Report — Orbit / Core / Defect Search",
        "",
        f"- **git_commit**: `{git_commit()}`",
        f"- **workers**: ~25% cores → default `{DEFAULT_WORKERS}`",
        f"- **total_wall_time_s**: {wall:.1f}",
        f"- **targets**: n100→165, n64→113",
        "",
        "## Hard constraints observed",
        "",
        "- Exclusive writes: `src/search/orbit_defect_search.py`, tests, `scratch/agent_b/`.",
        "- No verifier/baseline/certified/claim_registry edits; no global UB from scoped UNSAT.",
        "- TIMEOUT ≠ INFEASIBLE; every INFEASIBLE carries scope+model_hash.",
        "- Types 0,3–6: defect/partial only. Types 1–2: pure AND defect compared.",
        "",
        "## Axis smoke",
        "",
        f"- n64 smoke wall: {smoke64.get('wall_time_s'):.1f}s; rows={len(smoke64.get('rows') or [])}",
        f"- n100 smoke wall: {smoke100.get('wall_time_s'):.1f}s; rows={len(smoke100.get('rows') or [])}",
        "",
        "### n64 smoke statuses",
        "",
    ]
    for r in smoke64.get("rows") or []:
        lines.append(
            f"- t{r['symmetry_type']} {r['mode']} d{r['defect_budget']}: "
            f"**{r['status']}** size={r['size']} ({r['wall_time_s']:.1f}s) hash=`{r.get('model_hash','')[:12]}`"
        )
    lines += ["", "### n100 smoke statuses", ""]
    for r in smoke100.get("rows") or []:
        lines.append(
            f"- t{r['symmetry_type']} {r['mode']} d{r['defect_budget']}: "
            f"**{r['status']}** size={r['size']} ({r['wall_time_s']:.1f}s)"
        )

    lines += [
        "",
        "## n100 long pilots",
        "",
        f"- any_legal_plus1: {n100.get('any_legal_plus1')}",
        f"- best: `{json.dumps(n100.get('best') or {}, sort_keys=True)[:500]}`",
        "",
    ]
    for r in n100.get("runs") or []:
        lines.append(
            f"- {r['tag']}: **{r['status']}** size={r['size']} "
            f"wall={r.get('wall_time_s'):.1f}s cand={r.get('candidate')}"
        )

    lines += [
        "",
        "## n64 long pilots",
        "",
        f"- any_legal_plus1: {n64.get('any_legal_plus1')}",
        f"- best: `{json.dumps(n64.get('best') or {}, sort_keys=True)[:500]}`",
        "",
    ]
    for r in n64.get("runs") or []:
        lines.append(
            f"- {r['tag']}: **{r['status']}** size={r['size']} "
            f"wall={r.get('wall_time_s'):.1f}s cand={r.get('candidate')}"
        )

    lines += [
        "",
        "## Files",
        "",
        "- `scratch/agent_b/manifest.jsonl`",
        "- `scratch/agent_b/axis_smoke_summary.json`",
        "- `scratch/agent_b/n100_orbit_defect_summary.json`",
        "- `scratch/agent_b/n64_orbit_defect_summary.json`",
        "- `scratch/agent_b/checkpoints/`",
        "- `scratch/agent_b/candidates/` (only if legal +1 found; dual-verified in scratch, not certified)",
        "",
        "## Note on claims",
        "",
        "No new lower bound is announced here. Scoped INFEASIBLE/TIMEOUT only.",
        "",
    ]
    path = SCRATCH / "agent_b_wave2_report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Orbit/core/defect Wave-2 search (Agent B)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_smoke = sub.add_parser("smoke", help="Short smoke on all 7 axes")
    s_smoke.add_argument("--n", type=int, default=64, choices=[64, 100])
    s_smoke.add_argument("--time-per-axis", type=float, default=30.0)
    s_smoke.add_argument("--seed", type=int, default=1)
    s_smoke.add_argument("--workers", type=int, default=DEFAULT_WORKERS)

    s_solve = sub.add_parser("solve", help="Single scoped solve")
    s_solve.add_argument("--n", type=int, required=True, choices=[64, 100])
    s_solve.add_argument("--type", type=int, required=True, choices=range(7))
    s_solve.add_argument(
        "--mode", type=str, required=True, choices=["pure", "defect", "partial"]
    )
    s_solve.add_argument("--target", type=int, default=None)
    s_solve.add_argument("--dmin", type=int, default=0)
    s_solve.add_argument("--dmax", type=int, default=0)
    s_solve.add_argument("--time", type=float, default=60.0)
    s_solve.add_argument("--seed", type=int, default=0)
    s_solve.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    s_solve.add_argument("--fix-core", action="store_true")

    s_wave = sub.add_parser("wave2", help="Full Wave-2 pilot schedule")
    s_wave.add_argument("--budget-hours", type=float, default=5.0)
    s_wave.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    s_wave.add_argument("--seed-base", type=int, default=11)

    s_card = sub.add_parser("cardinality", help="Print Gate1-style cardinality table")
    s_card.add_argument("--n", type=int, required=True, choices=[64, 100])

    args = p.parse_args(argv)
    ensure_scratch()

    if args.cmd == "smoke":
        summary = run_axis_smoke(
            n=args.n,
            time_per_axis_s=args.time_per_axis,
            seed=args.seed,
            num_workers=args.workers,
        )
        print(json.dumps(summary, indent=2))
        return 0

    if args.cmd == "cardinality":
        rows = [cardinality_status_for_type(args.n, t) for t in range(7)]
        print(json.dumps(rows, indent=2))
        return 0

    if args.cmd == "solve":
        cfg = SearchConfig(
            n=args.n,
            symmetry_type=args.type,
            mode=args.mode,
            target_size=args.target or TARGETS[args.n],
            defect_budget_min=args.dmin,
            defect_budget_max=args.dmax,
            time_budget_s=args.time,
            seed=args.seed,
            num_workers=args.workers,
            fix_core=args.fix_core,
        )
        result = solve_orbit_defect(cfg)
        ck = save_checkpoint(
            result,
            f"solve_n{args.n}_t{args.type}_{args.mode}_s{args.seed}",
        )
        cand = maybe_save_candidate(result)
        append_manifest(
            {
                "phase": "solve",
                "checkpoint": str(ck),
                "candidate": str(cand) if cand else None,
                "status": result["solver_status"],
                "n": args.n,
                "symmetry_type": args.type,
                "mode": args.mode,
                "model_hash": result.get("model_hash"),
                "git_commit": git_commit(),
            }
        )
        print(json.dumps({k: result[k] for k in result if k != "round_log"}, indent=2))
        return 0

    if args.cmd == "wave2":
        out = run_wave2_pilots(
            total_budget_s=args.budget_hours * 3600,
            num_workers=args.workers,
            seed_base=args.seed_base,
        )
        print(
            json.dumps(
                {
                    "total_wall_time_s": out["total_wall_time_s"],
                    "report": out["report_path"],
                    "n100_best": out["n100"].get("best"),
                    "n64_best": out["n64"].get("best"),
                    "any_legal_n100": out["n100"].get("any_legal_plus1"),
                    "any_legal_n64": out["n64"].get("any_legal_plus1"),
                },
                indent=2,
            )
        )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
