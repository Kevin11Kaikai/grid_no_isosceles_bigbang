"""Wave 2 / Phase 3 — fixed-cardinality minimum-conflict soft search (Agent C).

Exclusive ownership: this file + tests/test_fixed_cardinality_minconflict.py
+ scratch/agent_c/**.

Primary objective: fix |S| = target (165 on n=100, 113 on n=64) and minimize
exact V(S) from src.verification.conflict_metric.conflict_count. Cardinality
is never reduced to cut V.

Moves: 1-for-1, 2-for-2, ejection / large-k swaps, reheating & parallel
tempering, elite archive, multi-seed Gate-1-informed inits.

Incremental V is used for speed; periodically recomputed via conflict_metric.
On mismatch: STOP and save a counterexample under scratch/agent_c/.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import time
from collections import Counter, deque
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

# ProcessPoolExecutor retained for optional in-process use; campaign uses subprocesses.

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from data.baselines.official_raw import SOL_64, SOL_100
from src.search.lns_exact_repair import exact_repair_region
from src.structures.candidate_io import save_candidate, sha256_of_points
from src.verification.conflict_metric import conflict_count, ConflictMetricError
from src.verification.oracle_verifier import is_legal_pivot_method
from src.verification_independent.independent_verifier import verify_independent

Point = Tuple[int, int]

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRATCH = REPO_ROOT / "scratch" / "agent_c"
AUDIT_C = REPO_ROOT / "scratch" / "audit" / "agent_c"
AUDIT_A = REPO_ROOT / "scratch" / "audit" / "agent_a"
GATE1 = REPO_ROOT / "scratch" / "audit" / "gate1_consistency_check.json"

TARGET = {64: 113, 100: 165}
BASELINE = {64: SOL_64, 100: SOL_100}


# ---------------------------------------------------------------------------
# Incremental V (authoritative cross-check: conflict_count)
# ---------------------------------------------------------------------------


def _sq(a: Point, b: Point) -> int:
    return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])


def _binom2(m: int) -> int:
    return m * (m - 1) // 2 if m >= 2 else 0


class IncrementalConflictState:
    """Maintain V(S) with O(|S|) add/remove. Never changes cardinality itself."""

    __slots__ = ("n", "points", "dist_counts", "V", "moves")

    def __init__(self, n: int, points: Optional[Iterable[Point]] = None):
        self.n = n
        self.points: Set[Point] = set()
        self.dist_counts: Dict[Point, Counter] = {}
        self.V = 0
        self.moves = 0
        if points is not None:
            for p in points:
                self.add(tuple(p))  # type: ignore[arg-type]

    def copy(self) -> "IncrementalConflictState":
        other = IncrementalConflictState(self.n)
        other.points = set(self.points)
        other.dist_counts = {p: Counter(c) for p, c in self.dist_counts.items()}
        other.V = self.V
        other.moves = self.moves
        return other

    def add(self, p: Point) -> None:
        if p in self.points:
            raise ValueError(f"duplicate add {p}")
        if not (0 <= p[0] < self.n and 0 <= p[1] < self.n):
            raise ValueError(f"oob {p}")
        for q in self.points:
            d2 = _sq(p, q)
            c = self.dist_counts[q]
            m = c[d2]
            self.V += m
            c[d2] = m + 1
        cp: Counter = Counter()
        for q in self.points:
            cp[_sq(p, q)] += 1
        self.V += sum(_binom2(m) for m in cp.values())
        self.dist_counts[p] = cp
        self.points.add(p)
        self.moves += 1

    def remove(self, p: Point) -> None:
        if p not in self.points:
            raise ValueError(f"missing remove {p}")
        cp = self.dist_counts.pop(p)
        self.V -= sum(_binom2(m) for m in cp.values())
        self.points.remove(p)
        for q in self.points:
            d2 = _sq(p, q)
            c = self.dist_counts[q]
            m = c[d2]
            self.V -= m - 1
            if m == 1:
                del c[d2]
            else:
                c[d2] = m - 1
        self.moves += 1

    def pivot_contrib(self, p: Point) -> int:
        return sum(_binom2(m) for m in self.dist_counts[p].values())

    def swap_one(self, rem: Point, add: Point) -> int:
        """1-for-1; returns new V. Caller must ensure rem in S, add not in S."""
        self.remove(rem)
        self.add(add)
        return self.V

    def swap_many(self, rems: Sequence[Point], adds: Sequence[Point]) -> int:
        if len(rems) != len(adds):
            raise ValueError("fixed-cardinality requires |rems|==|adds|")
        for r in rems:
            self.remove(r)
        for a in adds:
            self.add(a)
        return self.V

    def exact_V(self) -> int:
        return conflict_count(sorted(self.points), self.n)


class VMismatchError(RuntimeError):
    """Incremental V disagreed with conflict_metric.conflict_count."""


def cross_check_or_stop(
    state: IncrementalConflictState,
    scratch_dir: Path,
    tag: str,
) -> int:
    exact = state.exact_V()
    if exact != state.V:
        path = scratch_dir / "counterexamples" / f"v_mismatch_{tag}_{int(time.time())}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "tag": tag,
            "n": state.n,
            "incremental_V": state.V,
            "exact_V": exact,
            "size": len(state.points),
            "points": [list(p) for p in sorted(state.points)],
            "moves": state.moves,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        raise VMismatchError(
            f"INCREMENTAL/EXACT V MISMATCH: inc={state.V} exact={exact}; "
            f"saved {path}"
        )
    return exact


# ---------------------------------------------------------------------------
# Gate-1 pools
# ---------------------------------------------------------------------------


@dataclass
class Gate1Pools:
    n: int
    target: int
    baseline: List[Point]
    rem_pool: List[Point]
    add_pool: List[Point]
    low_delta: List[Point]
    easiest_blockers: List[Point]
    halo: List[Point]
    unpaired: List[Point]
    partners: List[Point]

    def external_candidates(self) -> List[Point]:
        seen = set()
        out: List[Point] = []
        for src in (
            self.add_pool,
            self.low_delta,
            self.easiest_blockers,
            self.halo,
            self.partners,
        ):
            for p in src:
                t = (int(p[0]), int(p[1]))
                if t not in seen:
                    seen.add(t)
                    out.append(t)
        return out


def _as_point(p: Sequence[int]) -> Point:
    return (int(p[0]), int(p[1]))


def _spatial_halo(seeds: Iterable[Point], n: int, radius: int = 2) -> List[Point]:
    out: Set[Point] = set()
    for x, y in seeds:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                xx, yy = x + dx, y + dy
                if 0 <= xx < n and 0 <= yy < n:
                    out.add((xx, yy))
    return sorted(out)


def load_gate1_pools(n: int) -> Gate1Pools:
    if n not in (64, 100):
        raise ValueError(f"unsupported n={n}")
    uni = json.loads((AUDIT_C / "universe_halo_diagnostics.json").read_text(encoding="utf-8"))
    key = f"n{n}"
    u_small = uni["baselines"][key]["universes"]["U_small"]
    u_med = uni["baselines"][key]["universes"]["U_medium"]
    rem = [_as_point(p) for p in u_med["removable_baseline_points"]]
    add = [_as_point(p) for p in u_small["addable_unselected_points"]]
    add_med = [_as_point(p) for p in u_med["addable_unselected_points"]]
    for p in add_med:
        if p not in add:
            add.append(p)

    dens = json.loads(
        (AUDIT_C / f"density_hamming_diagnostics_n{n}.json").read_text(encoding="utf-8")
    )
    top20 = dens["C1_density"]["direct_insertion"]["top20_lowest_delta"]
    low_delta = [_as_point(e["point"]) for e in top20]

    easiest: List[Point] = []
    a_path = AUDIT_A / f"blocker_stats_n{n}.json"
    if a_path.exists():
        a = json.loads(a_path.read_text(encoding="utf-8"))
        for e in a.get("easiest_to_insert_candidates", {}).get("top_20_summary", []):
            easiest.append(_as_point(e["q"]))
    g1 = json.loads(GATE1.read_text(encoding="utf-8"))
    if n == 100:
        for p in g1["n100_deletion_bound"]["easiest_16_qs_exact_min_deletions_2"]:
            t = _as_point(p)
            if t not in easiest:
                easiest.append(t)
    else:
        for p in g1["n64_deletion_bound"]["easiest_qs"]:
            t = _as_point(p)
            if t not in easiest:
                easiest.append(t)

    baseline = [_as_point(p) for p in BASELINE[n]]
    sym = dens["C1_density"]["central_180_symmetry"]
    unpaired_raw = sym.get("unpaired_examples") or sym.get("unpaired_present_points") or []
    if isinstance(unpaired_raw, int):
        unpaired_raw = []
    unpaired = [_as_point(p) for p in unpaired_raw]
    partners: List[Point] = []
    for x, y in unpaired:
        partners.append((n - 1 - x, n - 1 - y))

    halo_seeds = rem + add + easiest + low_delta
    halo = _spatial_halo(halo_seeds, n, radius=2)
    # keep halo as external-ish: not only baseline
    return Gate1Pools(
        n=n,
        target=TARGET[n],
        baseline=baseline,
        rem_pool=rem,
        add_pool=add,
        low_delta=low_delta,
        easiest_blockers=easiest,
        halo=halo,
        unpaired=unpaired,
        partners=partners,
    )


# ---------------------------------------------------------------------------
# Initializations (always |S|=target)
# ---------------------------------------------------------------------------


def _ensure_cardinality(
    n: int,
    points: Set[Point],
    target: int,
    fill_from: Sequence[Point],
    rng: random.Random,
) -> Set[Point]:
    S = set(points)
    if len(S) > target:
        # Prefer removing baseline rem-pool / unpaired first when present
        extra = list(S)
        rng.shuffle(extra)
        while len(S) > target:
            S.remove(extra.pop())
    if len(S) < target:
        cands = [p for p in fill_from if p not in S]
        rng.shuffle(cands)
        # also allow random grid fill if needed
        gi = 0
        grid = [(x, y) for x in range(n) for y in range(n)]
        rng.shuffle(grid)
        pool = cands + [p for p in grid if p not in S and p not in cands]
        for p in pool:
            if len(S) >= target:
                break
            S.add(p)
            gi += 1
        if len(S) != target:
            raise RuntimeError(f"could not reach target |S|={target}, got {len(S)}")
    return S


def init_baseline_plus_low_blocker(pools: Gate1Pools, rng: random.Random) -> List[Point]:
    S = set(pools.baseline)
    inject = list(pools.easiest_blockers) + list(pools.low_delta) + list(pools.add_pool)
    inject = [p for p in inject if p not in S]
    if not inject:
        inject = [p for p in pools.halo if p not in S]
    S.add(rng.choice(inject))
    S = _ensure_cardinality(pools.n, S, pools.target, inject + pools.halo, rng)
    return sorted(S)


def init_gate1_low_delta_v(pools: Gate1Pools, rng: random.Random) -> List[Point]:
    S = set(pools.baseline)
    # remove 1–2 rem-pool, add 2–3 low-delta to hit target
    need = pools.target - len(S)
    rem_cands = [p for p in pools.rem_pool if p in S] or list(S)
    n_rem = min(len(rem_cands), max(0, 1 - need) + 1)  # if need=1, rem 0 or more via swap style
    # Standard: need == 1 for both grids from baselines
    adds = [p for p in (pools.low_delta + pools.add_pool + pools.easiest_blockers) if p not in S]
    rng.shuffle(adds)
    if need >= 1:
        for a in adds[:need]:
            S.add(a)
    else:
        # overshot somehow
        pass
    # diversify: optionally swap one rem with one add
    if rem_cands and adds and rng.random() < 0.7:
        r = rng.choice(rem_cands)
        a = rng.choice(adds)
        if r in S and a not in S:
            S.remove(r)
            S.add(a)
    S = _ensure_cardinality(pools.n, S, pools.target, adds + pools.halo, rng)
    return sorted(S)


def init_orbit_informed(pools: Gate1Pools, rng: random.Random) -> List[Point]:
    S = set(pools.baseline)
    # Break / complete 180°: inject missing partner or displace unpaired
    if pools.unpaired:
        u = rng.choice(pools.unpaired)
        partner = (pools.n - 1 - u[0], pools.n - 1 - u[1])
        if partner not in S:
            S.add(partner)
        elif pools.partners:
            # displace an unpaired, add a halo defect
            if u in S and rng.random() < 0.5:
                S.remove(u)
            extras = [p for p in pools.add_pool + pools.halo if p not in S]
            if extras:
                S.add(rng.choice(extras))
    else:
        # fully symmetric n100: inject easiest blocker as deliberate defect
        extras = [p for p in pools.easiest_blockers + pools.low_delta if p not in S]
        if extras:
            S.add(rng.choice(extras))
            # optionally remove a rem-pool point to keep diversity at same time as fill
            rem_cands = [p for p in pools.rem_pool if p in S]
            if rem_cands and rng.random() < 0.4:
                S.remove(rng.choice(rem_cands))
                extras2 = [p for p in pools.add_pool if p not in S]
                if extras2:
                    S.add(rng.choice(extras2))
    S = _ensure_cardinality(
        pools.n, S, pools.target, pools.add_pool + pools.halo + pools.partners, rng
    )
    return sorted(S)


def init_random_fixed_card(pools: Gate1Pools, rng: random.Random, radius: int = 3) -> List[Point]:
    S = set(pools.baseline)
    r = rng.randint(1, radius)
    rem_cands = [p for p in pools.rem_pool if p in S] or list(S)
    adds = [p for p in pools.add_pool + pools.halo + pools.easiest_blockers if p not in S]
    rng.shuffle(rem_cands)
    rng.shuffle(adds)
    rems = rem_cands[:r]
    # remove r, add r + (target - |baseline|)
    need_net = pools.target - (len(S) - len(rems))
    for p in rems:
        S.remove(p)
    for p in adds[:need_net]:
        S.add(p)
    S = _ensure_cardinality(pools.n, S, pools.target, adds + pools.halo, rng)
    return sorted(S)


INIT_FUNCS = {
    "baseline_plus_low_blocker": init_baseline_plus_low_blocker,
    "gate1_low_delta_v": init_gate1_low_delta_v,
    "orbit_informed": init_orbit_informed,
    "random_fixed_card": init_random_fixed_card,
}


# ---------------------------------------------------------------------------
# Neighborhood operators (cardinality-preserving)
# ---------------------------------------------------------------------------


def _conflict_weights(state: IncrementalConflictState) -> Dict[Point, float]:
    w = {}
    for p in state.points:
        # pivot contrib + how often this point appears as a repeated-distance partner
        # Approximate partner pressure via degree in dist multiset: sum (m-1)_+ over distances at other pivots is expensive;
        # use pivot contrib + small noise proxy: number of distances with m>=2 involving recount via local.
        w[p] = float(state.pivot_contrib(p)) + 0.1
    # boost points that sit in crowded distance bins of others: O(|S|^2) too heavy;
    # cheap boost: high pivot contrib already correlates with conflict involvement.
    return w


def _weighted_sample(rng: random.Random, items: List[Point], weights: Dict[Point, float], k: int) -> List[Point]:
    if k <= 0 or not items:
        return []
    k = min(k, len(items))
    # sequential weighted without replacement
    pool = list(items)
    chosen: List[Point] = []
    for _ in range(k):
        ws = [max(1e-9, weights.get(p, 1.0)) for p in pool]
        total = sum(ws)
        r = rng.random() * total
        acc = 0.0
        idx = 0
        for i, w in enumerate(ws):
            acc += w
            if acc >= r:
                idx = i
                break
        chosen.append(pool.pop(idx))
    return chosen


def propose_1for1(
    state: IncrementalConflictState,
    external: Sequence[Point],
    recently_deleted: Sequence[Point],
    rng: random.Random,
) -> Optional[Tuple[List[Point], List[Point]]]:
    outs = [p for p in (list(external) + list(recently_deleted)) if p not in state.points]
    if not outs or not state.points:
        return None
    weights = _conflict_weights(state)
    rem = _weighted_sample(rng, list(state.points), weights, 1)[0]
    add = rng.choice(outs)
    return [rem], [add]


def propose_2for2(
    state: IncrementalConflictState,
    external: Sequence[Point],
    recently_deleted: Sequence[Point],
    rng: random.Random,
) -> Optional[Tuple[List[Point], List[Point]]]:
    outs = [p for p in (list(external) + list(recently_deleted)) if p not in state.points]
    if len(outs) < 2 or len(state.points) < 2:
        return None
    weights = _conflict_weights(state)
    rems = _weighted_sample(rng, list(state.points), weights, 2)
    adds = rng.sample(outs, 2)
    return rems, adds


def propose_large_swap(
    state: IncrementalConflictState,
    external: Sequence[Point],
    recently_deleted: Sequence[Point],
    rng: random.Random,
    k: Optional[int] = None,
) -> Optional[Tuple[List[Point], List[Point]]]:
    outs = [p for p in (list(external) + list(recently_deleted)) if p not in state.points]
    if len(outs) < 3 or len(state.points) < 3:
        return None
    k = k or rng.randint(3, min(8, len(outs), len(state.points)))
    weights = _conflict_weights(state)
    rems = _weighted_sample(rng, list(state.points), weights, k)
    adds = rng.sample(outs, k)
    return rems, adds


def propose_ejection_chain(
    state: IncrementalConflictState,
    external: Sequence[Point],
    recently_deleted: Sequence[Point],
    rng: random.Random,
) -> Optional[Tuple[List[Point], List[Point]]]:
    """Ejection-ish: remove a conflict cluster near a seed, refill from halo."""
    if len(state.points) < 4:
        return None
    weights = _conflict_weights(state)
    seed = _weighted_sample(rng, list(state.points), weights, 1)[0]
    # Chebyshev neighborhood inside S
    neigh = [
        p
        for p in state.points
        if max(abs(p[0] - seed[0]), abs(p[1] - seed[1])) <= 3
    ]
    k = min(len(neigh), rng.randint(2, 5))
    if k < 2:
        return None
    rems = rng.sample(neigh, k)
    outs = [p for p in (list(external) + list(recently_deleted)) if p not in state.points]
    if len(outs) < k:
        return None
    # Prefer outs near removed centroid
    cx = sum(p[0] for p in rems) / k
    cy = sum(p[1] for p in rems) / k
    outs_sorted = sorted(outs, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
    pool = outs_sorted[: max(k * 4, k)]
    if len(pool) < k:
        pool = outs
    adds = rng.sample(pool, k)
    return rems, adds


# ---------------------------------------------------------------------------
# Exact repair with expanded pool (never S'-only)
# ---------------------------------------------------------------------------


def expanded_repair_pool(
    S: Set[Point],
    pools: Gate1Pools,
    recently_deleted: Sequence[Point],
    destroyed: Sequence[Point],
) -> List[Point]:
    seen = set()
    out: List[Point] = []
    for src in (
        destroyed,
        recently_deleted,
        pools.add_pool,
        pools.low_delta,
        pools.easiest_blockers,
        pools.halo,
        pools.partners,
    ):
        for p in src:
            t = _as_point(p)
            if t in S and t not in destroyed:
                continue
            if t not in seen:
                seen.add(t)
                out.append(t)
    return out


def _greedy_legal_core(n: int, points: Set[Point], rng: random.Random) -> Set[Point]:
    """Build a legal subset of `points` (order randomized)."""
    from src.search.incremental_state import IncrementalIsoscelesFreeSet

    ifs = IncrementalIsoscelesFreeSet(n)
    order = list(points)
    rng.shuffle(order)
    for p in order:
        ifs.add_point(p)
    return set(ifs.points)


def exact_repair_fixed_cardinality(
    n: int,
    S: Set[Point],
    target: int,
    pools: Gate1Pools,
    recently_deleted: Sequence[Point],
    rng: random.Random,
    destroy_k: int = 6,
    milp_time_s: float = 4.0,
) -> Tuple[Optional[List[Point]], dict]:
    """Repair toward lower V at fixed |S|=target using an expanded pool.

    Never uses S'-only deletion as the sole operator: candidates always include
    Gate-1 halo / low-blocker / recently deleted / add-pool cells.
    """
    meta: Dict[str, Any] = {
        "destroy_k": destroy_k,
        "pool_policy": "S_cup_halo_cup_deleted_cup_lowblocker",
    }
    # Legal core of current S (soft states may be illegal)
    core = _greedy_legal_core(n, S, rng)
    # Also force-drop up to destroy_k high-conflict points from a soft view
    state = IncrementalConflictState(n, S)
    weights = _conflict_weights(state)
    drop = set(_weighted_sample(rng, list(S), weights, min(destroy_k, len(S))))
    fixed = core - drop
    # Re-verify fixed legality (drop may have been outside core)
    fixed = _greedy_legal_core(n, fixed, rng)
    if len(fixed) >= target:
        # Too large a legal core: trim randomly to target-need_room
        trim = list(fixed)
        rng.shuffle(trim)
        keep = target - rng.randint(3, max(3, destroy_k))
        keep = max(1, min(keep, target - 1))
        fixed = set(trim[:keep])
        fixed = _greedy_legal_core(n, fixed, rng)

    need = target - len(fixed)
    meta["need"] = need
    meta["fixed_size"] = len(fixed)
    if need <= 0:
        meta["status"] = "fixed_too_large"
        return sorted(list(fixed)[:target]) if len(fixed) >= target else None, meta

    cand = expanded_repair_pool(S, pools, recently_deleted, list(drop | (S - fixed)))
    cand = [p for p in cand if p not in fixed]
    meta["n_candidates"] = len(cand)
    if not cand:
        meta["status"] = "empty_pool"
        return None, meta

    selected_set: Set[Point] = set()
    try:
        selected, milp_meta = exact_repair_region(n, fixed, cand, time_limit_s=milp_time_s)
        meta["milp"] = milp_meta
        selected_set = set(map(_as_point, selected))
    except Exception as e:
        meta["milp_error"] = repr(e)
        # Soft greedy fill only from expanded pool
        selected_set = set()

    chosen: Set[Point] = set()
    if len(selected_set) >= need:
        chosen = set(rng.sample(sorted(selected_set), need))
        meta["mode"] = "legal_subset_of_milp"
    else:
        chosen = set(selected_set)
        remaining = need - len(chosen)
        meta["mode"] = "milp_plus_soft_fill" if selected_set else "soft_fill_only"
        fill_pool = [p for p in cand if p not in fixed and p not in chosen]
        trial = IncrementalConflictState(n, fixed | chosen)
        for _ in range(max(0, remaining)):
            best_p = None
            best_v = None
            sample = fill_pool if len(fill_pool) <= 80 else rng.sample(fill_pool, 80)
            for p in sample:
                trial.add(p)
                v = trial.V
                trial.remove(p)
                if best_v is None or v < best_v:
                    best_v = v
                    best_p = p
            if best_p is None:
                break
            trial.add(best_p)
            chosen.add(best_p)
            fill_pool.remove(best_p)

    new_S = fixed | chosen
    if len(new_S) != target:
        new_S = _ensure_cardinality(n, new_S, target, cand + pools.halo, rng)
    meta["final_size"] = len(new_S)
    meta["final_V"] = conflict_count(sorted(new_S), n)
    meta["status"] = "ok"
    return sorted(new_S), meta


# ---------------------------------------------------------------------------
# Search core (reheating SA + optional parallel tempering within seed)
# ---------------------------------------------------------------------------


@dataclass
class SearchResult:
    n: int
    target: int
    seed: int
    init_method: str
    points: List[Point]
    initial_V: int
    best_V: int
    time_to_best_s: float
    wall_s: float
    iterations: int
    exact_checks: int
    incremental_exact_agree: bool
    v0_found: bool
    verify_A: Optional[bool] = None
    verify_B: Optional[bool] = None
    path: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


def _accept(delta: int, T: float, rng: random.Random) -> bool:
    if delta <= 0:
        return True
    if T <= 1e-12:
        return False
    return rng.random() < math.exp(-delta / T)


def run_fixed_cardinality_search(
    n: int,
    seed: int,
    time_budget_s: float,
    init_method: str = "baseline_plus_low_blocker",
    n_replicas: int = 3,
    exact_check_every: int = 200,
    repair_every: int = 400,
    checkpoint_every_s: float = 300.0,
    scratch_dir: Optional[Path] = None,
) -> SearchResult:
    scratch_dir = scratch_dir or SCRATCH
    scratch_dir.mkdir(parents=True, exist_ok=True)
    (scratch_dir / "elite_archive").mkdir(parents=True, exist_ok=True)
    (scratch_dir / "checkpoints" / "candidates").mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)
    pools = load_gate1_pools(n)
    init_fn = INIT_FUNCS[init_method]
    init_pts = init_fn(pools, rng)
    if len(init_pts) != pools.target:
        raise AssertionError(f"init cardinality {len(init_pts)} != {pools.target}")

    external = pools.external_candidates()
    recently_deleted: deque = deque(maxlen=400)

    # Parallel tempering replicas (warmer schedule for soft V landscape)
    temps = [0.6 * (2.6 ** i) for i in range(n_replicas)]
    replicas = [IncrementalConflictState(n, init_pts) for _ in range(n_replicas)]
    for r in replicas:
        cross_check_or_stop(r, scratch_dir, f"init_n{n}_s{seed}")

    initial_V = replicas[0].V
    best_V = initial_V
    best_points = sorted(replicas[0].points)
    time_to_best = 0.0
    t0 = time.time()
    last_ckpt = t0
    iterations = 0
    exact_checks = 1
    agree = True
    plateau = 0
    reheat_T0 = temps[:]
    repairs = 0
    move_stats = Counter()

    # Seed recently_deleted with rem-pool for repair diversity
    for p in pools.rem_pool:
        recently_deleted.append(p)

    def consider_best(state: IncrementalConflictState, now: float) -> None:
        nonlocal best_V, best_points, time_to_best, plateau
        if state.V < best_V:
            best_V = state.V
            best_points = sorted(state.points)
            time_to_best = now - t0
            plateau = 0
            _save_elite(scratch_dir, n, seed, best_points, best_V, init_method)

    consider_best(replicas[0], t0)

    while time.time() - t0 < time_budget_s:
        iterations += 1
        plateau += 1
        ri = iterations % n_replicas
        state = replicas[ri]
        T = temps[ri]
        local_rng = random.Random(seed * 1000003 + iterations * 17 + ri)

        move_kind = local_rng.choices(
            ["1for1", "2for2", "large", "eject"],
            weights=[0.45, 0.25, 0.18, 0.12],
            k=1,
        )[0]
        if move_kind == "1for1":
            prop = propose_1for1(state, external, recently_deleted, local_rng)
        elif move_kind == "2for2":
            prop = propose_2for2(state, external, recently_deleted, local_rng)
        elif move_kind == "large":
            prop = propose_large_swap(state, external, recently_deleted, local_rng)
        else:
            prop = propose_ejection_chain(state, external, recently_deleted, local_rng)

        if prop is None:
            continue
        rems, adds = prop
        if any(a in state.points for a in adds) or any(r not in state.points for r in rems):
            continue
        if len(set(rems)) != len(rems) or len(set(adds)) != len(adds):
            continue

        old_V = state.V
        pre_points = sorted(state.points)
        # apply
        for r in rems:
            state.remove(r)
        for a in adds:
            state.add(a)
        if len(state.points) != pools.target:
            replicas[ri] = IncrementalConflictState(n, pre_points)
            continue
        new_V = state.V
        delta = new_V - old_V
        if _accept(delta, T, local_rng):
            move_stats[move_kind] += 1
            for r in rems:
                recently_deleted.append(r)
            consider_best(state, time.time())
        else:
            # rollback
            for a in reversed(adds):
                state.remove(a)
            for r in reversed(rems):
                state.add(r)
            if state.V != old_V or len(state.points) != pools.target:
                replicas[ri] = IncrementalConflictState(n, pre_points)
                state = replicas[ri]

        # Parallel tempering neighbor swap
        if n_replicas >= 2 and iterations % 25 == 0:
            i = local_rng.randrange(n_replicas - 1)
            j = i + 1
            Vi, Vj = replicas[i].V, replicas[j].V
            Ti, Tj = temps[i], temps[j]
            # swap acceptance
            log_acc = (Vi - Vj) * (1.0 / Ti - 1.0 / Tj)
            if log_acc >= 0 or local_rng.random() < math.exp(log_acc):
                replicas[i], replicas[j] = replicas[j], replicas[i]
                move_stats["pt_swap"] += 1

        # Reheat cold replicas on long plateau
        if plateau > 2500:
            temps = [t * 1.8 for t in reheat_T0]
            plateau = 0
            move_stats["reheat"] += 1
        elif iterations % 800 == 0:
            # cool back toward schedule
            temps = [0.92 * t + 0.08 * t0_ for t, t0_ in zip(temps, reheat_T0)]

        # Periodic exact repair (expanded pool)
        if iterations % repair_every == 0:
            repairs += 1
            # repair the best replica
            best_i = min(range(n_replicas), key=lambda k: replicas[k].V)
            new_pts, rmeta = exact_repair_fixed_cardinality(
                n,
                set(replicas[best_i].points),
                pools.target,
                pools,
                list(recently_deleted),
                local_rng,
                destroy_k=local_rng.randint(4, 8),
                milp_time_s=3.5,
            )
            if new_pts is not None and len(new_pts) == pools.target:
                cand_state = IncrementalConflictState(n, new_pts)
                cross_check_or_stop(cand_state, scratch_dir, f"repair_n{n}_s{seed}_{iterations}")
                exact_checks += 1
                if cand_state.V <= replicas[best_i].V:
                    replicas[best_i] = cand_state
                    consider_best(cand_state, time.time())
                    move_stats["repair_accept"] += 1

        # Periodic exact V check
        if iterations % exact_check_every == 0:
            for rstate in replicas:
                cross_check_or_stop(rstate, scratch_dir, f"periodic_n{n}_s{seed}_{iterations}")
                exact_checks += 1

        now = time.time()
        if now - last_ckpt >= checkpoint_every_s:
            last_ckpt = now
            _checkpoint(scratch_dir, n, seed, best_points, best_V, init_method, iterations, now - t0)

        if best_V == 0:
            break

    # Final exact check
    final_state = IncrementalConflictState(n, best_points)
    cross_check_or_stop(final_state, scratch_dir, f"final_n{n}_s{seed}")
    exact_checks += 1
    best_V = final_state.V

    v0 = best_V == 0
    verify_A = verify_B = None
    out_path = None
    if v0:
        ok_a, _wit_a = is_legal_pivot_method(best_points, n)
        ok_b, _wit_b = verify_independent(best_points, n)
        verify_A, verify_B = bool(ok_a), bool(ok_b)
        out_path = str(
            _save_v0_candidate(scratch_dir, n, seed, best_points, init_method, verify_A, verify_B)
        )

    wall = time.time() - t0
    result = SearchResult(
        n=n,
        target=pools.target,
        seed=seed,
        init_method=init_method,
        points=best_points,
        initial_V=initial_V,
        best_V=best_V,
        time_to_best_s=time_to_best,
        wall_s=wall,
        iterations=iterations,
        exact_checks=exact_checks,
        incremental_exact_agree=agree,
        v0_found=v0,
        verify_A=verify_A,
        verify_B=verify_B,
        path=out_path,
        meta={
            "temps_final": temps,
            "move_stats": dict(move_stats),
            "repairs": repairs,
            "n_replicas": n_replicas,
            "points_hash": sha256_of_points(best_points),
            "schema": "grid_no_isosceles.search_result.v1",
            "method": "fixed_cardinality_minconflict",
        },
    )
    _append_manifest(scratch_dir, result)
    _checkpoint(scratch_dir, n, seed, best_points, best_V, init_method, iterations, wall)
    return result


def _save_elite(
    scratch_dir: Path,
    n: int,
    seed: int,
    points: List[Point],
    V: int,
    init_method: str,
) -> Path:
    elite_dir = scratch_dir / "elite_archive"
    elite_dir.mkdir(parents=True, exist_ok=True)
    h = sha256_of_points(points)[:16]
    path = elite_dir / f"n{n}_V{V}_seed{seed}_{h}.json"
    save_candidate(
        str(path),
        n,
        points,
        search_method="fixed_cardinality_minconflict",
        seed=seed,
        parent_candidate="official_baseline",
        status="UNVERIFIED",
        extra={
            "target_size": TARGET[n],
            "V": V,
            "init_method": init_method,
            "schema": "grid_no_isosceles.search_result.v1",
        },
    )
    return path


def _checkpoint(
    scratch_dir: Path,
    n: int,
    seed: int,
    points: List[Point],
    V: int,
    init_method: str,
    iterations: int,
    wall_s: float,
) -> Path:
    ck = scratch_dir / "checkpoints" / "candidates"
    ck.mkdir(parents=True, exist_ok=True)
    path = ck / f"n{n}_seed{seed}_best.json"
    save_candidate(
        str(path),
        n,
        points,
        search_method="fixed_cardinality_minconflict",
        seed=seed,
        parent_candidate="official_baseline",
        status="UNVERIFIED",
        extra={
            "target_size": TARGET[n],
            "V": V,
            "init_method": init_method,
            "iterations": iterations,
            "wall_s": wall_s,
            "size_fixed": True,
            "schema": "grid_no_isosceles.search_result.v1",
        },
    )
    return path


def _save_v0_candidate(
    scratch_dir: Path,
    n: int,
    seed: int,
    points: List[Point],
    init_method: str,
    verify_A: bool,
    verify_B: bool,
) -> Path:
    d = scratch_dir / "v0_candidates"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"n{n}_k{len(points)}_seed{seed}_V0.json"
    # Do NOT certify / announce record — scratch only
    save_candidate(
        str(path),
        n,
        points,
        search_method="fixed_cardinality_minconflict",
        seed=seed,
        parent_candidate="official_baseline",
        status="UNVERIFIED",
        extra={
            "V": 0,
            "target_size": TARGET[n],
            "init_method": init_method,
            "verify": {"A": verify_A, "B": verify_B},
            "note": "V=0 candidate in scratch only; not certified; not a claimed record",
            "schema": "grid_no_isosceles.search_result.v1",
        },
    )
    return path


def _append_manifest(scratch_dir: Path, result: SearchResult) -> None:
    man = scratch_dir / "manifest.jsonl"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    rec = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "n": result.n,
        "target_size": result.target,
        "seed": result.seed,
        "init_method": result.init_method,
        "initial_V": result.initial_V,
        "best_V": result.best_V,
        "time_to_best_s": result.time_to_best_s,
        "wall_s": result.wall_s,
        "iterations": result.iterations,
        "exact_checks": result.exact_checks,
        "incremental_exact_agree": result.incremental_exact_agree,
        "v0_found": result.v0_found,
        "verify_A": result.verify_A,
        "verify_B": result.verify_B,
        "points_hash": result.meta.get("points_hash"),
        "path": result.path,
        "method": "fixed_cardinality_minconflict",
    }
    with man.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _result_to_dict(r: SearchResult) -> dict:
    return {
        "n": r.n,
        "target_size": r.target,
        "seed": r.seed,
        "init_method": r.init_method,
        "initial_V": r.initial_V,
        "best_V": r.best_V,
        "time_to_best_s": r.time_to_best_s,
        "wall_s": r.wall_s,
        "iterations": r.iterations,
        "exact_checks": r.exact_checks,
        "incremental_exact_agree": r.incremental_exact_agree,
        "v0_found": r.v0_found,
        "verify_A": r.verify_A,
        "verify_B": r.verify_B,
        "points_hash": r.meta.get("points_hash"),
        "move_stats": r.meta.get("move_stats"),
        "path": r.path,
        "points": [list(p) for p in r.points],
    }


def _worker(payload: dict) -> dict:
    r = run_fixed_cardinality_search(
        n=payload["n"],
        seed=payload["seed"],
        time_budget_s=payload["time_budget_s"],
        init_method=payload["init_method"],
        n_replicas=payload.get("n_replicas", 3),
        exact_check_every=payload.get("exact_check_every", 200),
        repair_every=payload.get("repair_every", 400),
        checkpoint_every_s=payload.get("checkpoint_every_s", 300.0),
        scratch_dir=Path(payload.get("scratch_dir", str(SCRATCH))),
    )
    return _result_to_dict(r)


def run_campaign(
    n: int,
    seeds: Sequence[int],
    time_per_seed_s: float,
    max_workers: int = 5,
    scratch_dir: Optional[Path] = None,
) -> List[dict]:
    """Run seeds via subprocesses (Windows-robust) with a worker cap."""
    import subprocess

    scratch_dir = scratch_dir or SCRATCH
    init_cycle = list(INIT_FUNCS.keys())
    jobs = []
    for i, seed in enumerate(seeds):
        jobs.append(
            {
                "n": n,
                "seed": seed,
                "time_budget_s": time_per_seed_s,
                "init_method": init_cycle[i % len(init_cycle)],
                "n_replicas": 2,
                "scratch_dir": str(scratch_dir),
                "checkpoint_every_s": 300.0,
                "repair_every": 600,
            }
        )

    results: List[dict] = []
    pending = list(jobs)
    active: Dict[subprocess.Popen, dict] = {}
    out_dir = scratch_dir / "seed_results"
    out_dir.mkdir(parents=True, exist_ok=True)

    def _launch(job: dict) -> subprocess.Popen:
        out_path = out_dir / f"n{job['n']}_seed{job['seed']}.json"
        job = dict(job)
        job["out_path"] = str(out_path)
        spec = json.dumps(job)
        # One-shot worker process; isolates crashes from the pool.
        cmd = [
            sys.executable,
            "-c",
            (
                "import json,sys; from pathlib import Path; "
                "from src.search.fixed_cardinality_minconflict import run_fixed_cardinality_search,_result_to_dict; "
                f"job=json.loads({spec!r}); "
                "r=run_fixed_cardinality_search(n=job['n'],seed=job['seed'],"
                "time_budget_s=job['time_budget_s'],init_method=job['init_method'],"
                "n_replicas=job.get('n_replicas',2),"
                "repair_every=job.get('repair_every',600),"
                "checkpoint_every_s=job.get('checkpoint_every_s',300.0),"
                "scratch_dir=Path(job['scratch_dir'])); "
                "Path(job['out_path']).write_text(json.dumps(_result_to_dict(r)),encoding='utf-8')"
            ),
        ]
        env = dict(os.environ)
        env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        return subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        ), job

    while pending or active:
        while pending and len(active) < max_workers:
            job = pending.pop(0)
            proc, jobmeta = _launch(job)
            active[proc] = jobmeta
        done = []
        for proc, job in list(active.items()):
            ret = proc.poll()
            if ret is None:
                continue
            done.append(proc)
            out_path = Path(job["out_path"])
            if ret == 0 and out_path.exists():
                results.append(json.loads(out_path.read_text(encoding="utf-8")))
            else:
                err = ""
                try:
                    err = (proc.stderr.read() or b"").decode("utf-8", errors="replace")[-2000:]
                except Exception:
                    pass
                results.append(
                    {
                        "n": job["n"],
                        "seed": job["seed"],
                        "error": f"exit={ret}: {err}",
                        "init_method": job["init_method"],
                        "best_V": None,
                    }
                )
        for proc in done:
            active.pop(proc, None)
        if active and not done:
            time.sleep(2.0)

    results.sort(key=lambda r: (r.get("best_V") is None, r.get("best_V", 10**9), r.get("seed", 0)))
    return results


def write_summary(n: int, results: List[dict], scratch_dir: Path, wall_total_s: float) -> Path:
    ok = [r for r in results if r.get("best_V") is not None]
    best = ok[0] if ok else None
    summary = {
        "schema": "agent_c_fixed_card_summary_v1",
        "n": n,
        "target_size": TARGET[n],
        "n_seeds": len(results),
        "wall_total_s": wall_total_s,
        "best_V": best.get("best_V") if best else None,
        "best_seed": best.get("seed") if best else None,
        "best_init_method": best.get("init_method") if best else None,
        "best_time_to_best_s": best.get("time_to_best_s") if best else None,
        "best_initial_V": best.get("initial_V") if best else None,
        "any_v0": any(r.get("v0_found") for r in ok),
        "incremental_exact_agree_all": all(r.get("incremental_exact_agree", False) for r in ok) if ok else None,
        "results": results,
        "note": "Fixed-cardinality min-V search; not a lower-bound claim; not certified.",
    }
    path = scratch_dir / (f"n{n}_fixed{TARGET[n]}_summary.json")
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[Sequence[str]] = None) -> None:
    import argparse

    p = argparse.ArgumentParser(description="Fixed-cardinality min-conflict (Agent C)")
    p.add_argument("--n", type=int, required=True, choices=[64, 100])
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--seeds", type=str, default=None, help="comma-separated")
    p.add_argument("--time", type=float, default=120.0)
    p.add_argument("--init", type=str, default="baseline_plus_low_blocker", choices=list(INIT_FUNCS))
    p.add_argument("--workers", type=int, default=5)
    p.add_argument("--campaign", action="store_true")
    args = p.parse_args(list(argv) if argv is not None else None)

    SCRATCH.mkdir(parents=True, exist_ok=True)

    if args.campaign or args.seeds:
        if args.seeds:
            seeds = [int(x) for x in args.seeds.split(",")]
        else:
            seeds = list(range(1, 9)) if args.n == 100 else list(range(1, 5))
        t0 = time.time()
        results = run_campaign(args.n, seeds, args.time, max_workers=args.workers)
        write_summary(args.n, results, SCRATCH, time.time() - t0)
        print(json.dumps({"n": args.n, "best_V": results[0].get("best_V") if results else None, "n_results": len(results)}, indent=2))
    else:
        seed = 1 if args.seed is None else args.seed
        r = run_fixed_cardinality_search(args.n, seed, args.time, init_method=args.init)
        print(json.dumps(_result_to_dict(r), indent=2)[:2000])


if __name__ == "__main__":
    main()
