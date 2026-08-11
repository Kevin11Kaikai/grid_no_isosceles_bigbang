"""Wave-2 Agent A: conflict-driven multi-region comparative pilot.

Compares three destroy strategies once each (never treating the giant
blocker-projection CC as a small community):

1. pure_spatial — union of K random spatial boxes (lns_multiregion style)
2. conflict_driven — union of spatial-knn6 communities linked by a heavy
   far conflict bridge from Gate-1 audit artifacts
3. hybrid — spatial box ∪ knn communities touched by Agent-A easiest qs /
   Agent-C low-ΔV adds

Reuses exact_repair_region; does NOT modify lns_multiregion.py.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from typing import Dict, List, Optional, Sequence, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.search.lns_exact_repair import exact_repair_region  # noqa: E402
from src.search.sa_exact_repair import _random_region  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402

Point = Tuple[int, int]


def _as_points(seq: Sequence[Sequence[int]]) -> List[Point]:
    return [(int(p[0]), int(p[1])) for p in seq]


def load_spatial_knn_communities(
    n: int,
    path: Optional[str] = None,
) -> List[List[Point]]:
    if path is None:
        path = f"scratch/audit/agent_a/blocker_communities_n{n}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    communities = data["communities_spatial_knn6"]
    out: List[List[Point]] = []
    for c in sorted(communities, key=lambda x: int(x["community_id"])):
        out.append(_as_points(c["baseline_points"]))
    return out


def load_heaviest_far_bridge(n: int, path: Optional[str] = None) -> Tuple[int, int, float]:
    if path is None:
        path = f"scratch/audit/agent_a/blocker_communities_n{n}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    bridges = [
        b
        for b in data["conflict_bridges_spatial_knn6"]
        if b.get("spatially_far_but_conflict_coupled")
    ]
    if not bridges:
        bridges = list(data["conflict_bridges_spatial_knn6"])
    bridges.sort(key=lambda b: -int(b["conflict_bridge_weight"]))
    b0 = bridges[0]
    return int(b0["community_a"]), int(b0["community_b"]), float(b0["conflict_bridge_weight"])


def load_easiest_qs(n: int, top_m: int = 8) -> List[Point]:
    if n == 100:
        with open("scratch/audit/gate1_consistency_check.json", "r", encoding="utf-8") as f:
            g1 = json.load(f)
        return _as_points(g1["n100_deletion_bound"]["easiest_16_qs_exact_min_deletions_2"])[:top_m]
    with open("scratch/audit/gate1_consistency_check.json", "r", encoding="utf-8") as f:
        g1 = json.load(f)
    return _as_points(g1["n64_deletion_bound"]["easiest_qs"])[:top_m]


def load_low_delta_adds(n: int, top_m: int = 8) -> List[Point]:
    with open("scratch/audit/agent_c/universe_halo_diagnostics.json", "r", encoding="utf-8") as f:
        diag = json.load(f)
    add = diag["baselines"][f"n{n}"]["universes"]["U_small"]["addable_unselected_points"]
    return _as_points(add)[:top_m]


def _bbox_region(points: Sequence[Point], pad: int, n: int) -> List[Point]:
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0 = max(0, min(xs) - pad)
    x1 = min(n - 1, max(xs) + pad)
    y0 = max(0, min(ys) - pad)
    y1 = min(n - 1, max(ys) + pad)
    return [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]


def build_destroy_region(
    mode: str,
    n: int,
    s0: Sequence[Point],
    rng: random.Random,
    k_boxes: int = 2,
    box_cap: int = 120,
    pad: int = 2,
) -> Tuple[List[Point], dict]:
    """Return (region_cells, meta). Never uses giant projection CC."""
    s0_list = _as_points(s0)
    communities = load_spatial_knn_communities(n)
    meta: dict = {"mode": mode, "n_spatial_knn_communities": len(communities)}

    if mode == "pure_spatial":
        union: Set[Point] = set()
        for _ in range(k_boxes):
            union.update(_random_region(n, rng, box_cap))
        meta["k_boxes"] = k_boxes
        meta["region_size"] = len(union)
        return list(union), meta

    if mode == "conflict_driven":
        a, b, w = load_heaviest_far_bridge(n)
        meta["bridge"] = {"community_a": a, "community_b": b, "weight": w}
        # Cap community sizes for MILP tractability: take random subset if huge.
        pts_a = list(communities[a])
        pts_b = list(communities[b])
        rng.shuffle(pts_a)
        rng.shuffle(pts_b)
        cap_each = max(20, box_cap // 2)
        seed_pts = pts_a[:cap_each] + pts_b[:cap_each]
        region = set(_bbox_region(seed_pts, pad=pad, n=n))
        # Also free the seed baseline points themselves.
        region.update(seed_pts)
        meta["n_seed_baseline"] = len(seed_pts)
        meta["region_size"] = len(region)
        meta["note"] = "spatial_knn communities + bbox halo; NOT giant projection CC"
        return list(region), meta

    if mode == "hybrid":
        a, b, w = load_heaviest_far_bridge(n)
        easiest = load_easiest_qs(n)
        low_add = load_low_delta_adds(n)
        focus = easiest + low_add
        # Communities containing any baseline point near focus cells: use bridge pair
        # plus a spatial box around first focus cell.
        pts_a = list(communities[a])[: max(15, box_cap // 3)]
        pts_b = list(communities[b])[: max(15, box_cap // 3)]
        box = set(_random_region(n, rng, box_cap // 2))
        if focus:
            box.update(_bbox_region(focus[:4], pad=pad + 1, n=n))
        region = set(pts_a) | set(pts_b) | box
        meta["bridge"] = {"community_a": a, "community_b": b, "weight": w}
        meta["n_focus_qs"] = len(focus)
        meta["region_size"] = len(region)
        meta["note"] = "hybrid spatial box ∪ knn bridge communities ∪ easiest/low-ΔV halo"
        return list(region), meta

    raise ValueError(f"unknown mode {mode}")


def one_repair_iteration(
    n: int,
    current: Set[Point],
    region: Sequence[Point],
    milp_time_limit_s: float,
) -> Tuple[Set[Point], dict]:
    removed = [p for p in region if p in current]
    fixed = current - set(removed)
    candidates = [p for p in region if p not in fixed]
    selected, repair_meta = exact_repair_region(
        n, fixed, candidates, time_limit_s=milp_time_limit_s
    )
    new_set = fixed | set(selected)
    return new_set, repair_meta


def conflict_multiregion_pilot(
    n: int,
    initial_points: Sequence[Point],
    mode: str,
    time_budget_s: float,
    seed: int = 1,
    milp_time_limit_s: float = 8.0,
    k_boxes: int = 2,
    box_cap: int = 120,
) -> dict:
    rng = random.Random(seed)
    current: Set[Point] = set(_as_points(initial_points))
    ok, wit = is_legal_pivot_method(list(current), n)
    if not ok:
        raise ValueError(f"initial illegal: {wit}")

    best = set(current)
    best_size = len(best)
    t0 = time.time()
    iterations = 0
    improvements: List[dict] = []
    last_region_meta: dict = {}

    while time.time() - t0 < time_budget_s:
        iterations += 1
        region, region_meta = build_destroy_region(
            mode, n, list(current), rng, k_boxes=k_boxes, box_cap=box_cap
        )
        last_region_meta = region_meta
        new_set, repair_meta = one_repair_iteration(
            n, current, region, milp_time_limit_s=milp_time_limit_s
        )
        if len(new_set) > len(current) or (
            len(new_set) >= len(current) and rng.random() < 0.25
        ):
            current = new_set
        if len(current) > best_size:
            ok, wit = is_legal_pivot_method(list(current), n)
            if not ok:
                raise AssertionError(f"illegal improvement: {wit}")
            best = set(current)
            best_size = len(best)
            improvements.append(
                {
                    "iteration": iterations,
                    "size": best_size,
                    "t": time.time() - t0,
                    "region_size": region_meta.get("region_size"),
                }
            )

    ok, wit = is_legal_pivot_method(list(best), n)
    v = conflict_count(list(best), n)
    return {
        "mode": mode,
        "n": n,
        "seed": seed,
        "status": "COMPLETED",
        "wall_time_s": time.time() - t0,
        "iterations": iterations,
        "best_size": best_size,
        "baseline_size": len(initial_points),
        "improved": best_size > len(initial_points),
        "V_best": v,
        "oracle_legal": bool(ok),
        "improvements": improvements,
        "last_region_meta": last_region_meta,
        "claim_note": "pilot comparison only; no global UB; giant CC not used as community",
    }


if __name__ == "__main__":
    import argparse

    from data.baselines.official_raw import SOL_64, SOL_100
    from src.search.hamming_shell_conflict import append_manifest, atomic_write_json

    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--mode", type=str, required=True)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--time-budget-s", type=float, default=600.0)
    parser.add_argument("--out", type=str, required=True)
    args = parser.parse_args()
    s0 = SOL_100 if args.n == 100 else SOL_64
    meta = conflict_multiregion_pilot(
        args.n, s0, args.mode, args.time_budget_s, seed=args.seed
    )
    atomic_write_json(args.out, meta)
    append_manifest(
        "scratch/agent_a/manifest.jsonl",
        {"event": "multiregion_pilot", "out": args.out, **{k: meta[k] for k in ("mode", "n", "seed", "best_size", "wall_time_s")}},
    )
    print(json.dumps(meta, indent=2)[:2000])
