#!/usr/bin/env python3
"""Gate 1 / Audit Agent A — insertion blockers & conflict communities.

Structural audit only for official baselines n=64 (112) and n=100 (164).
Does NOT search for 165/113. Writes only under scratch/audit/agent_a/.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_64, SOL_100  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402

Point = Tuple[int, int]

SCHEMA_VERSION = "agent_a_blockers_v1"
DETERMINISTIC_SEED = 0
EXACT_BITSET_MAX = 18
EXACT_BB_MAX = 40
TOP_K_FULL = 200
EXPECTED_HASH = {
    64: "47d42165b7804493a847e064494ef067e97bc8ac12121cd04ac19f23fee9c292",
    100: "8a84216d28f5afbbbd6b06301b159eab1b57c85bb814d78dd708da2be65cbdc1",
}

BLOCKER_DEFINITION = {
    "Type1_q_as_pivot": (
        "For unselected q and distinct p1,p2 in S0 with |p1-q|^2 = |p2-q|^2, "
        "certificate deletion-set / blocker edge is {p1,p2} (must hit at least one)."
    ),
    "Type2_existing_pivot": (
        "For unselected q and b,p in S0 with |q-b|^2 = |p-b|^2, "
        "certificate deletion-set / blocker edge is {b,p} (must hit at least one)."
    ),
    "min_deletions": (
        "Minimum deletions from S0 so no Type1/Type2 certificate remains "
        "= minimum vertex cover of the union of blocker edges "
        "(keep ≤1 point per Type1 distance class from q, and hit every Type2 edge)."
    ),
    "exact_vs_approximate": (
        "exact_min_hitting_set is set only when (a) LB==UB from sound bounds, or "
        "(b) bitset MIS DP finishes (involved≤EXACT_BITSET_MAX), or "
        "(c) branch-and-bound MIS finishes (involved≤EXACT_BB_MAX). "
        "Otherwise exact is null with lower_bound/upper_bound only. "
        "Greedy heuristics are NEVER labeled exact by themselves."
    ),
}


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception as e:
        return f"ERROR:{e}"


def sq(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def ring_depth(p: Point, n: int) -> int:
    x, y = p
    return min(x, y, n - 1 - x, n - 1 - y)


def zone_label(p: Point, n: int) -> str:
    d = ring_depth(p, n)
    if d <= max(1, n // 32):
        return "boundary_frame"
    lo, hi = n // 4, n - n // 4
    if lo <= p[0] < hi and lo <= p[1] < hi:
        return "center_box"
    return "mid_band"


def precompute_pivot_maps(pts: Sequence[Point]) -> List[Dict[int, int]]:
    m = len(pts)
    maps: List[Dict[int, int]] = [{} for _ in range(m)]
    for bi in range(m):
        dmap: Dict[int, int] = {}
        b = pts[bi]
        for ai in range(m):
            if ai == bi:
                continue
            d = sq(pts[ai], b)
            if d in dmap:
                raise RuntimeError(
                    f"baseline not legal: pivot {pts[bi]} has two points at d2={d}"
                )
            dmap[d] = ai
        maps[bi] = dmap
    return maps


def maximal_matching_lb(n_verts: int, edges: List[Tuple[int, int]]) -> int:
    if not edges:
        return 0
    used = [False] * n_verts
    matched = 0
    for u, v in edges:
        if not used[u] and not used[v]:
            used[u] = used[v] = True
            matched += 1
    return matched


def build_full_adj_masks(
    n: int, class_of: List[int], type2_edges: List[Tuple[int, int]]
) -> List[int]:
    """Adjacency masks: Type2 edges + within-class Type1 cliques."""
    adj = [0] * n
    classes: Dict[int, List[int]] = defaultdict(list)
    for i, c in enumerate(class_of):
        classes[c].append(i)
    for members in classes.values():
        if len(members) < 2:
            continue
        mask = 0
        for i in members:
            mask |= 1 << i
        for i in members:
            adj[i] |= mask & ~(1 << i)
    for u, v in type2_edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def greedy_mis_size(adj: List[int], n: int, order: List[int]) -> int:
    taken = 0
    forbidden = 0
    for v in order:
        bit = 1 << v
        if forbidden & bit:
            continue
        taken += 1
        forbidden |= bit | adj[v]
    return taken


def upper_bound_vc(adj: List[int], n: int) -> int:
    """Sound UB on VC via several deterministic greedy MIS constructions."""
    if n == 0:
        return 0
    deg = [(adj[i].bit_count(), i) for i in range(n)]
    orders = [
        list(range(n)),
        sorted(range(n), key=lambda i: (deg[i][0], i)),
        sorted(range(n), key=lambda i: (-deg[i][0], i)),
        sorted(range(n), key=lambda i: (deg[i][0] % 3, deg[i][0], i)),
    ]
    best_mis = 0
    for order in orders:
        best_mis = max(best_mis, greedy_mis_size(adj, n, order))
    return n - best_mis


def exact_mis_bitset(adj: List[int], n: int) -> int:
    """Exact MIS size by enumerating independent sets (n small)."""
    best = 0
    full = 1 << n
    for mask in range(full):
        ok = True
        m = mask
        while m:
            v = (m & -m).bit_length() - 1
            if adj[v] & mask:
                ok = False
                break
            m &= m - 1
        if ok:
            c = mask.bit_count()
            if c > best:
                best = c
    return best


def exact_mis_bb(adj: List[int], n: int) -> int:
    """Exact MIS via classic branch-and-bound on bitmasks (n <= EXACT_BB_MAX)."""
    best = [0]

    def bound(mask: int) -> int:
        # greedy packing lower-bound on MIS in induced subgraph
        taken = 0
        forbidden = 0
        m = mask
        while m:
            v = (m & -m).bit_length() - 1
            bit = 1 << v
            m &= m - 1
            if forbidden & bit:
                continue
            taken += 1
            forbidden |= bit | (adj[v] & mask)
        return taken

    def rec(mask: int, taken: int) -> None:
        if taken + bound(mask) <= best[0]:
            return
        if mask == 0:
            if taken > best[0]:
                best[0] = taken
            return
        # choose vertex of minimum degree in induced subgraph
        m = mask
        best_v = -1
        best_deg = 10**9
        while m:
            v = (m & -m).bit_length() - 1
            d = (adj[v] & mask).bit_count()
            if d < best_deg or (d == best_deg and v < best_v):
                best_deg = d
                best_v = v
            m &= m - 1
        v = best_v
        bit = 1 << v
        # take v
        rec(mask & ~bit & ~adj[v], taken + 1)
        # skip v
        rec(mask & ~bit, taken)

    rec((1 << n) - 1, 0)
    return best[0]


def analyze_q(
    q: Point,
    pts: Sequence[Point],
    pivot_maps: List[Dict[int, int]],
    n_grid: int,
) -> Dict[str, Any]:
    m = len(pts)
    by_d: Dict[int, List[int]] = defaultdict(list)
    for i, p in enumerate(pts):
        by_d[sq(p, q)].append(i)

    type1_edges: List[Tuple[int, int]] = []
    class_sizes: List[int] = []
    # Map global point index -> temporary class id (distance key)
    global_class: Dict[int, int] = {}
    for ci, (d, idxs) in enumerate(by_d.items()):
        class_sizes.append(len(idxs))
        for i in idxs:
            global_class[i] = ci
        if len(idxs) >= 2:
            for a in range(len(idxs)):
                for b in range(a + 1, len(idxs)):
                    u, v = idxs[a], idxs[b]
                    type1_edges.append((u, v) if u < v else (v, u))

    type2_edges_g: List[Tuple[int, int]] = []
    for bi, bpt in enumerate(pts):
        d = sq(q, bpt)
        other = pivot_maps[bi].get(d)
        if other is not None:
            u, v = (bi, other) if bi < other else (other, bi)
            type2_edges_g.append((u, v))

    edge_set = set(type1_edges)
    edge_set.update(type2_edges_g)
    edges = sorted(edge_set)

    involved = sorted({x for e in edges for x in e})
    inv_index = {g: li for li, g in enumerate(involved)}
    n_inv = len(involved)

    # Local class ids remapped to 0.. 
    class_of = [0] * n_inv
    remap_c: Dict[int, int] = {}
    next_c = 0
    for li, g in enumerate(involved):
        gc = global_class[g]
        if gc not in remap_c:
            remap_c[gc] = next_c
            next_c += 1
        class_of[li] = remap_c[gc]

    type2_local = [
        (inv_index[u], inv_index[v])
        for u, v in set(type2_edges_g)
        if u in inv_index and v in inv_index
    ]
    all_local = [(inv_index[u], inv_index[v]) for u, v in edges]

    t1_lb = sum(max(0, s - 1) for s in class_sizes)
    match_lb = maximal_matching_lb(n_inv, all_local)

    if n_inv == 0:
        return {
            "q": [int(q[0]), int(q[1])],
            "zone": zone_label(q, n_grid),
            "ring_depth": ring_depth(q, n_grid),
            "blocker_edge_count": 0,
            "type1_edge_count": 0,
            "type2_edge_count": 0,
            "type1_multiplicity_classes": 0,
            "type1_forced_lb": 0,
            "involved_baseline_count": 0,
            "involved_baseline_points": [],
            "blocker_edges": [],
            "lower_bound_min_deletions": 0,
            "upper_bound_min_deletions": 0,
            "exact_min_hitting_set": 0,
            "exact_status": "exact_empty",
            "matching_lb": 0,
            "_involved_indices": [],
            "_edges_idx": [],
            "_type2_edges_idx": [],
        }

    adj = build_full_adj_masks(n_inv, class_of, type2_local)
    ub = upper_bound_vc(adj, n_inv)
    lb = max(t1_lb, match_lb)
    # LB cannot exceed UB; if matching/type1 overshoots due to... they shouldn't.
    if lb > ub:
        # Soundness: VC >= matching and constructive UB from MIS; fix by raising UB
        ub = lb

    exact: Optional[int] = None
    exact_status = "unknown_bounds_only"

    if lb == ub:
        exact = lb
        exact_status = "exact_bounds_coincide"
    elif n_inv <= EXACT_BITSET_MAX:
        mis = exact_mis_bitset(adj, n_inv)
        exact = n_inv - mis
        lb = ub = exact
        exact_status = "exact_bitset_dp"
    elif n_inv <= EXACT_BB_MAX:
        mis = exact_mis_bb(adj, n_inv)
        exact = n_inv - mis
        lb = ub = exact
        exact_status = "exact_branch_and_bound"
    else:
        exact_status = "intractable_mark_bounds_only"

    certificates = [
        [[int(pts[u][0]), int(pts[u][1])], [int(pts[v][0]), int(pts[v][1])]]
        for u, v in edges
    ]
    involved_pts = [[int(pts[i][0]), int(pts[i][1])] for i in involved]
    type2_unique = sorted(set(type2_edges_g))

    return {
        "q": [int(q[0]), int(q[1])],
        "zone": zone_label(q, n_grid),
        "ring_depth": ring_depth(q, n_grid),
        "blocker_edge_count": len(edges),
        "type1_edge_count": len(set(type1_edges)),
        "type2_edge_count": len(set(type2_edges_g)),
        "type1_multiplicity_classes": sum(1 for s in class_sizes if s >= 2),
        "type1_forced_lb": t1_lb,
        "involved_baseline_count": n_inv,
        "involved_baseline_points": involved_pts,
        "blocker_edges": certificates,
        "lower_bound_min_deletions": int(lb),
        "upper_bound_min_deletions": int(ub),
        "exact_min_hitting_set": exact,
        "exact_status": exact_status,
        "matching_lb": int(match_lb),
        "_involved_indices": involved,
        "_edges_idx": edges,
        "_type2_edges_idx": type2_unique,
    }


def union_find_components(n: int, edges: Sequence[Tuple[int, int]]) -> List[List[int]]:
    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        elif rank[ra] > rank[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rank[ra] += 1

    for u, v in edges:
        union(u, v)
    buckets: Dict[int, List[int]] = defaultdict(list)
    for i in range(n):
        buckets[find(i)].append(i)
    return [sorted(v) for _, v in sorted(buckets.items(), key=lambda kv: (len(kv[1]), kv[1][0]))]


def spatial_span(pts: Sequence[Point], idxs: Sequence[int]) -> Dict[str, Any]:
    if not idxs:
        return {"bbox": None, "bbox_diag2": 0, "max_pairwise_d2": 0, "centroid": None}
    xs = [pts[i][0] for i in idxs]
    ys = [pts[i][1] for i in idxs]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    diag2 = (maxx - minx) ** 2 + (maxy - miny) ** 2
    max_d2 = 0
    L = len(idxs)
    # Cap pairwise for huge comps: sample corners via bbox only if L large
    if L <= 80:
        for a in range(L):
            for b in range(a + 1, L):
                d2 = sq(pts[idxs[a]], pts[idxs[b]])
                if d2 > max_d2:
                    max_d2 = d2
    else:
        max_d2 = diag2
    return {
        "bbox": [[minx, miny], [maxx, maxy]],
        "bbox_diag2": int(diag2),
        "max_pairwise_d2": int(max_d2),
        "centroid": [float(np.mean(xs)), float(np.mean(ys))],
    }


def label_propagation(
    n: int,
    adj: List[Set[int]],
    n_iters: int = 20,
) -> List[int]:
    """Deterministic synchronous-ish label propagation (modularity-free)."""
    labels = list(range(n))
    rng_order = list(range(n))
    # Fixed shuffle from seed
    rs = np.random.RandomState(DETERMINISTIC_SEED)
    for _ in range(n_iters):
        rs.shuffle(rng_order)
        changed = 0
        for v in rng_order:
            if not adj[v]:
                continue
            counts: Dict[int, int] = defaultdict(int)
            for u in adj[v]:
                counts[labels[u]] += 1
            # majority; tie -> smallest label id
            best_label = min(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
            if best_label != labels[v]:
                labels[v] = best_label
                changed += 1
        if changed == 0:
            break
    # Relabel to 0..k-1 by first appearance in index order
    remap: Dict[int, int] = {}
    out = [0] * n
    nxt = 0
    for i, lab in enumerate(labels):
        if lab not in remap:
            remap[lab] = nxt
            nxt += 1
        out[i] = remap[lab]
    return out


def spatial_knn_components(pts: Sequence[Point], k: int = 6) -> List[List[int]]:
    """Connected components of undirected k-NN graph on baseline points (spatial)."""
    m = len(pts)
    edges: List[Tuple[int, int]] = []
    for i in range(m):
        dists = []
        for j in range(m):
            if i == j:
                continue
            dists.append((sq(pts[i], pts[j]), j))
        dists.sort()
        for _, j in dists[:k]:
            u, v = (i, j) if i < j else (j, i)
            edges.append((u, v))
    return union_find_components(m, edges)


def ring_band_components(pts: Sequence[Point], n_grid: int) -> List[List[int]]:
    """Partition baseline points into ring-depth bands (spatial, modularity-free)."""
    # bands: [0,1], [2 .. n//8], [n//8+1 .. n//4], [n//4+1 ..]
    bands: Dict[int, List[int]] = defaultdict(list)
    for i, p in enumerate(pts):
        d = ring_depth(p, n_grid)
        if d <= 1:
            b = 0
        elif d <= max(2, n_grid // 8):
            b = 1
        elif d <= n_grid // 4:
            b = 2
        else:
            b = 3
        bands[b].append(i)
    return [sorted(bands[b]) for b in sorted(bands.keys()) if bands[b]]


def conflict_bridges(
    comps: List[List[int]],
    point_to_comm: Dict[int, int],
    edge_counts: Counter,
    pts: Sequence[Point],
    n_grid: int,
) -> List[Dict[str, Any]]:
    """Aggregate projection edges that cross spatial/community boundaries."""
    bridge: Counter = Counter()
    for (u, v), freq in edge_counts.items():
        cu, cv = point_to_comm[u], point_to_comm[v]
        if cu == cv:
            continue
        a, b = (cu, cv) if cu < cv else (cv, cu)
        bridge[(a, b)] += freq
    far = (0.35 * n_grid) ** 2
    out = []
    centroids = []
    for members in comps:
        if members:
            cx = float(np.mean([pts[i][0] for i in members]))
            cy = float(np.mean([pts[i][1] for i in members]))
        else:
            cx = cy = 0.0
        centroids.append((cx, cy))
    for (a, b), w in sorted(bridge.items(), key=lambda kv: -kv[1]):
        dx = centroids[a][0] - centroids[b][0]
        dy = centroids[a][1] - centroids[b][1]
        d2 = dx * dx + dy * dy
        out.append(
            {
                "community_a": a,
                "community_b": b,
                "conflict_bridge_weight": int(w),
                "centroid_d2": float(d2),
                "spatially_far_but_conflict_coupled": bool(d2 >= far),
            }
        )
    return out


def community_records(
    pts: Sequence[Point],
    n_grid: int,
    comps: List[List[int]],
    proj_edges: List[Tuple[int, int]],
    edge_vertices: Set[int],
    point_to_comm: Dict[int, int],
    records: List[Dict[str, Any]],
    method: str,
) -> List[Dict[str, Any]]:
    far_thresh = (0.45 * n_grid) ** 2 + (0.45 * n_grid) ** 2
    out = []
    point_to_comm.clear()
    for cid, members in enumerate(comps):
        for i in members:
            point_to_comm[i] = cid

    for cid, members in enumerate(comps):
        span = spatial_span(pts, members)
        member_set = set(members)
        internal = sum(1 for u, v in proj_edges if u in member_set and v in member_set)
        external = sum(
            1 for u, v in proj_edges if (u in member_set) ^ (v in member_set)
        )
        touch = 0
        for rec in records:
            inv = rec["_involved_indices"]
            if any(point_to_comm.get(i) == cid for i in inv):
                touch += 1
        is_iso = len(members) == 1 and members[0] not in edge_vertices
        spatially_far = (
            len(members) >= 2
            and not is_iso
            and span["bbox_diag2"] >= far_thresh
        )
        out.append(
            {
                "community_id": cid,
                "partition_method": method,
                "size": len(members),
                "is_isolate_singleton": is_iso,
                "baseline_points": [
                    [int(pts[i][0]), int(pts[i][1])] for i in members
                ],
                "spatial_span": span,
                "internal_projection_edges": internal,
                "external_projection_edges": external,
                "n_candidate_qs_touching": touch,
                "spatially_far_but_conflict_coupled": bool(spatially_far),
            }
        )
    return out


def run_for_n(n: int, sol: Sequence[Sequence[int]], out_dir: str) -> Dict[str, Any]:
    t0 = time.time()
    pts: List[Point] = [(int(p[0]), int(p[1])) for p in sol]
    Sset = set(pts)
    baseline_hash = sha256_of_points(pts)
    expected = EXPECTED_HASH[n]
    if baseline_hash != expected:
        raise RuntimeError(
            f"hash mismatch n={n}: got {baseline_hash}, expected {expected}"
        )
    V = conflict_count(pts, n)
    if V != 0:
        raise RuntimeError(f"baseline V(S)={V} != 0 for n={n}")

    pivot_maps = precompute_pivot_maps(pts)
    m = len(pts)

    candidates: List[Point] = [
        (x, y) for x in range(n) for y in range(n) if (x, y) not in Sset
    ]

    records: List[Dict[str, Any]] = []
    global_edge_counts: Counter = Counter()
    type2_edge_counts: Counter = Counter()
    cert_to_qs: Dict[Tuple[Point, Point], List[int]] = defaultdict(list)

    for qi, q in enumerate(candidates):
        rec = analyze_q(q, pts, pivot_maps, n)
        records.append(rec)
        for u, v in rec["_edges_idx"]:
            global_edge_counts[(u, v)] += 1
            pu, pv = pts[u], pts[v]
            key = (pu, pv) if pu <= pv else (pv, pu)
            cert_to_qs[key].append(qi)
        for u, v in rec["_type2_edges_idx"]:
            type2_edge_counts[(u, v)] += 1
        if (qi + 1) % 1000 == 0:
            n_ex = sum(1 for r in records if r["exact_min_hitting_set"] is not None)
            print(
                f"  n={n} {qi+1}/{len(candidates)} "
                f"exact_so_far={n_ex}/{len(records)} "
                f"elapsed={time.time()-t0:.1f}s",
                flush=True,
            )

    proj_edges = sorted(global_edge_counts.keys())
    type2_edges = sorted(type2_edge_counts.keys())
    edge_vertices = {x for e in proj_edges for x in e}
    comps_cc = union_find_components(m, proj_edges)
    comps_type2 = union_find_components(m, type2_edges)

    # Frequency-thresholded edges for secondary CC partitions
    freqs = list(global_edge_counts.values())
    med = int(np.median(freqs)) if freqs else 1
    thr_levels = sorted(set([1, 2, 5, 10, max(1, med)]))
    thr_partitions = {}
    for thr in thr_levels:
        e_thr = [e for e, c in global_edge_counts.items() if c >= thr]
        comps_thr = union_find_components(m, e_thr)
        n_non_iso = sum(
            1
            for c in comps_thr
            if len(c) >= 2
            or (len(c) == 1 and c[0] in {x for ee in e_thr for x in ee})
        )
        thr_partitions[str(thr)] = {
            "min_edge_frequency": thr,
            "n_edges": len(e_thr),
            "n_cc_including_isolates": len(comps_thr),
            "n_non_isolate_communities": n_non_iso,
            "largest_cc_size": max(len(c) for c in comps_thr) if comps_thr else 0,
        }

    # Label propagation on projection adjacency
    adj_sets: List[Set[int]] = [set() for _ in range(m)]
    for u, v in proj_edges:
        adj_sets[u].add(v)
        adj_sets[v].add(u)
    lp_labels = label_propagation(m, adj_sets, n_iters=25)
    lp_buckets: Dict[int, List[int]] = defaultdict(list)
    for i, lab in enumerate(lp_labels):
        lp_buckets[lab].append(i)
    comps_lp = [
        sorted(v) for _, v in sorted(lp_buckets.items(), key=lambda kv: -len(kv[1]))
    ]

    # Spatial partitions (primary useful multi-community view when conflict CC is giant)
    comps_knn = spatial_knn_components(pts, k=6)
    comps_ring = ring_band_components(pts, n)

    point_to_comm: Dict[int, int] = {}
    communities_cc = community_records(
        pts,
        n,
        comps_cc,
        proj_edges,
        edge_vertices,
        point_to_comm,
        records,
        "connected_components_full_projection",
    )

    point_to_lp: Dict[int, int] = {}
    communities_lp = community_records(
        pts,
        n,
        comps_lp,
        proj_edges,
        edge_vertices,
        point_to_lp,
        records,
        "label_propagation",
    )

    point_to_knn: Dict[int, int] = {}
    communities_knn = community_records(
        pts,
        n,
        comps_knn,
        proj_edges,
        edge_vertices,
        point_to_knn,
        records,
        "spatial_knn6_cc",
    )
    knn_bridges = conflict_bridges(
        comps_knn, point_to_knn, global_edge_counts, pts, n
    )

    point_to_ring: Dict[int, int] = {}
    communities_ring = community_records(
        pts,
        n,
        comps_ring,
        proj_edges,
        edge_vertices,
        point_to_ring,
        records,
        "ring_band_partition",
    )
    ring_bridges = conflict_bridges(
        comps_ring, point_to_ring, global_edge_counts, pts, n
    )

    point_to_t2: Dict[int, int] = {}
    communities_t2 = community_records(
        pts,
        n,
        comps_type2,
        type2_edges,
        {x for e in type2_edges for x in e},
        point_to_t2,
        records,
        "type2_only_projection_cc",
    )

    # Attach community touches; spatial knn is the operational multi-community label
    for rec in records:
        inv = rec["_involved_indices"]
        cset = sorted({point_to_comm[i] for i in inv}) if inv else []
        lpset = sorted({point_to_lp[i] for i in inv}) if inv else []
        knnset = sorted({point_to_knn[i] for i in inv}) if inv else []
        ringset = sorted({point_to_ring[i] for i in inv}) if inv else []
        t2set = sorted({point_to_t2[i] for i in inv}) if inv else []
        rec["communities_touched"] = cset
        rec["n_communities_touched"] = len(cset)
        rec["lp_communities_touched"] = lpset
        rec["n_lp_communities_touched"] = len(lpset)
        rec["spatial_knn_communities_touched"] = knnset
        rec["n_spatial_knn_communities_touched"] = len(knnset)
        rec["ring_band_communities_touched"] = ringset
        rec["n_ring_band_communities_touched"] = len(ringset)
        rec["type2_communities_touched"] = t2set
        rec["n_type2_communities_touched"] = len(t2set)
        del rec["_involved_indices"]
        del rec["_edges_idx"]
        del rec["_type2_edges_idx"]

    edge_counts = np.array([r["blocker_edge_count"] for r in records], dtype=np.int32)
    lbs = np.array([r["lower_bound_min_deletions"] for r in records], dtype=np.int32)
    ubs = np.array([r["upper_bound_min_deletions"] for r in records], dtype=np.int32)
    exacts = [r["exact_min_hitting_set"] for r in records]
    n_exact = sum(1 for e in exacts if e is not None)
    zones = Counter(r["zone"] for r in records)
    multi_comm = sum(1 for r in records if r["n_communities_touched"] >= 2)
    multi_lp = sum(1 for r in records if r["n_lp_communities_touched"] >= 2)
    multi_knn = sum(1 for r in records if r["n_spatial_knn_communities_touched"] >= 2)
    multi_ring = sum(1 for r in records if r["n_ring_band_communities_touched"] >= 2)

    def pct(arr: np.ndarray, ps: Sequence[float]) -> Dict[str, float]:
        return {f"p{int(p)}": float(np.percentile(arr, p)) for p in ps}

    order = sorted(
        range(len(records)),
        key=lambda i: (
            records[i]["lower_bound_min_deletions"],
            records[i]["blocker_edge_count"],
            records[i]["upper_bound_min_deletions"],
            records[i]["q"][0],
            records[i]["q"][1],
        ),
    )
    easiest = []
    for rank, i in enumerate(order[:TOP_K_FULL]):
        r = dict(records[i])
        r["ease_rank"] = rank
        easiest.append(r)

    easiest100_zones = Counter(records[i]["zone"] for i in order[:100])
    multi_comm_easiest = []
    for i in order:
        r = records[i]
        if r["n_spatial_knn_communities_touched"] >= 2:
            multi_comm_easiest.append(
                {
                    "q": r["q"],
                    "n_spatial_knn_communities_touched": r[
                        "n_spatial_knn_communities_touched"
                    ],
                    "spatial_knn_communities_touched": r[
                        "spatial_knn_communities_touched"
                    ],
                    "n_ring_band_communities_touched": r[
                        "n_ring_band_communities_touched"
                    ],
                    "lower_bound_min_deletions": r["lower_bound_min_deletions"],
                    "blocker_edge_count": r["blocker_edge_count"],
                    "exact_min_hitting_set": r["exact_min_hitting_set"],
                }
            )
        if len(multi_comm_easiest) >= 50:
            break

    compact_all = [
        {
            "q": r["q"],
            "zone": r["zone"],
            "ring_depth": r["ring_depth"],
            "blocker_edge_count": r["blocker_edge_count"],
            "type1_edge_count": r["type1_edge_count"],
            "type2_edge_count": r["type2_edge_count"],
            "involved_baseline_count": r["involved_baseline_count"],
            "lower_bound_min_deletions": r["lower_bound_min_deletions"],
            "upper_bound_min_deletions": r["upper_bound_min_deletions"],
            "exact_min_hitting_set": r["exact_min_hitting_set"],
            "exact_status": r["exact_status"],
            "n_communities_touched": r["n_communities_touched"],
            "communities_touched": r["communities_touched"],
            "n_spatial_knn_communities_touched": r[
                "n_spatial_knn_communities_touched"
            ],
            "spatial_knn_communities_touched": r["spatial_knn_communities_touched"],
            "n_ring_band_communities_touched": r["n_ring_band_communities_touched"],
            "ring_band_communities_touched": r["ring_band_communities_touched"],
        }
        for r in records
    ]

    detail_name = f"blocker_detail_n{n}.json.gz"
    detail_path = os.path.join(out_dir, detail_name)
    with gzip.open(detail_path, "wt", encoding="utf-8") as gz:
        json.dump(
            {
                "schema_version": SCHEMA_VERSION,
                "n": n,
                "note": (
                    "Full blocker_edges for top-K easiest only; "
                    "all_qs_compact has bounds without edge lists."
                ),
                "top_k_full_records": easiest,
                "all_qs_compact": compact_all,
            },
            gz,
            separators=(",", ":"),
        )

    cert_catalog = []
    for (p1, p2), qlist in sorted(
        cert_to_qs.items(), key=lambda kv: (-len(kv[1]), kv[0])
    ):
        cert_catalog.append(
            {
                "certificate_edge": [[p1[0], p1[1]], [p2[0], p2[1]]],
                "n_qs_blocked_by_this_edge": len(qlist),
            }
        )
    cert_catalog_top = cert_catalog[:500]

    far_comms = [
        c
        for c in communities_cc
        if c["spatially_far_but_conflict_coupled"] and not c["is_isolate_singleton"]
    ]
    far_knn_bridges = [b for b in knn_bridges if b["spatially_far_but_conflict_coupled"]]
    far_ring_bridges = [
        b for b in ring_bridges if b["spatially_far_but_conflict_coupled"]
    ]
    n_conflict_comms = sum(1 for c in communities_cc if not c["is_isolate_singleton"])
    n_lp_noniso = sum(1 for c in communities_lp if not c["is_isolate_singleton"])
    n_knn = len(comps_knn)
    n_t2_noniso = sum(1 for c in communities_t2 if not c["is_isolate_singleton"])

    elapsed = time.time() - t0
    commit = git_commit()

    communities_doc = {
        "schema_version": SCHEMA_VERSION,
        "n": n,
        "baseline_size": m,
        "baseline_hash": baseline_hash,
        "git_commit": commit,
        "deterministic_seed": DETERMINISTIC_SEED,
        "blocker_definition": BLOCKER_DEFINITION,
        "exact_vs_approximate": BLOCKER_DEFINITION["exact_vs_approximate"],
        "EXACT_BITSET_MAX": EXACT_BITSET_MAX,
        "EXACT_BB_MAX": EXACT_BB_MAX,
        "partition_methods": {
            "full_projection_cc": (
                "CC of union of all Type1/Type2 blocker edges. Often one giant "
                "component ⇒ entire S0 is conflict-coupled (RH-3)."
            ),
            "spatial_knn6_cc": (
                "Operational multi-community partition: CC of undirected 6-NN "
                "spatial graph on S0; conflict bridges between these communities "
                "measure non-local coupling."
            ),
            "ring_band_partition": "Baseline points bucketed by ring-depth bands.",
            "type2_only_projection_cc": "CC using only Type2 blocker edges.",
            "label_propagation": "Deterministic LP on full projection adjacency.",
            "frequency_threshold_cc": "CC after keeping edges with frequency >= thr.",
        },
        "bipartite_incidence": {
            "left": "unselected_cells_q",
            "right": "certificates_blocker_edges_as_2sets",
            "n_left": len(candidates),
            "n_right_unique_certificates": len(cert_to_qs),
            "top_certificates_by_q_frequency": cert_catalog_top,
        },
        "projection_graph": {
            "n_vertices_baseline": m,
            "n_edges": len(proj_edges),
            "n_type2_edges": len(type2_edges),
            "edge_frequency_percentiles": {
                f"p{p}": float(np.percentile(freqs, p)) for p in [0, 50, 90, 99, 100]
            }
            if freqs
            else {},
            "n_connected_components_including_isolates": len(comps_cc),
            "n_non_isolate_communities": n_conflict_comms,
            "frequency_threshold_partitions": thr_partitions,
            "type2_only_n_cc": len(comps_type2),
            "type2_only_n_non_isolate": n_t2_noniso,
        },
        "communities_connected_components": communities_cc,
        "communities_label_propagation": communities_lp,
        "communities_spatial_knn6": communities_knn,
        "communities_ring_band": communities_ring,
        "communities_type2_only": communities_t2,
        "conflict_bridges_spatial_knn6": knn_bridges,
        "conflict_bridges_ring_band": ring_bridges,
        "spatially_far_but_conflict_coupled_communities_cc": far_comms,
        "spatially_far_conflict_bridges_knn": far_knn_bridges,
        "spatially_far_conflict_bridges_ring": far_ring_bridges,
        "summary": {
            "n_communities_total_cc": len(comps_cc),
            "n_non_isolate_communities_cc": n_conflict_comms,
            "n_communities_lp": len(comps_lp),
            "n_non_isolate_communities_lp": n_lp_noniso,
            "n_spatial_knn_communities": n_knn,
            "n_ring_band_communities": len(comps_ring),
            "n_type2_communities": len(comps_type2),
            "n_spatially_far_coupled_cc": len(far_comms),
            "n_spatially_far_knn_bridges": len(far_knn_bridges),
            "n_spatially_far_ring_bridges": len(far_ring_bridges),
            "largest_community_size_cc": max(c["size"] for c in communities_cc),
            "largest_community_size_knn": max(c["size"] for c in communities_knn),
            "multi_community_q_count_cc": multi_comm,
            "multi_community_q_count_lp": multi_lp,
            "multi_community_q_count_spatial_knn": multi_knn,
            "multi_community_q_count_ring": multi_ring,
            "note_giant_projection_cc": (
                "If n_communities_total_cc==1, full blocker projection couples all "
                "of S0; use spatial_knn6 + conflict bridges for multi-region design."
            ),
        },
        "paths": {
            "blocker_stats": f"scratch/audit/agent_a/blocker_stats_n{n}.json",
            "detail_gz": f"scratch/audit/agent_a/{detail_name}",
        },
        "run_commands": [
            f"python scratch/audit/agent_a/scripts/blocker_audit.py --n {n}",
            "python scratch/audit/agent_a/scripts/blocker_audit.py --n all",
        ],
        "search_for_165_or_113": False,
        "elapsed_sec": round(elapsed, 3),
    }

    min_lb = int(lbs.min())
    easiest_min = [records[i] for i in order[:20]]
    exact_status_hist = Counter(r["exact_status"] for r in records)

    stats_doc = {
        "schema_version": SCHEMA_VERSION,
        "n": n,
        "baseline_size": m,
        "baseline_hash": baseline_hash,
        "expected_hash": expected,
        "hash_ok": baseline_hash == expected,
        "git_commit": commit,
        "V_baseline": V,
        "deterministic_seed": DETERMINISTIC_SEED,
        "blocker_definition": BLOCKER_DEFINITION,
        "exact_vs_approximate": BLOCKER_DEFINITION["exact_vs_approximate"],
        "EXACT_BITSET_MAX": EXACT_BITSET_MAX,
        "EXACT_BB_MAX": EXACT_BB_MAX,
        "n_unselected_cells": len(candidates),
        "summary_stats": {
            "blocker_edge_count": {
                "min": int(edge_counts.min()),
                "max": int(edge_counts.max()),
                "mean": float(edge_counts.mean()),
                "percentiles": pct(
                    edge_counts, [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100]
                ),
            },
            "lower_bound_min_deletions": {
                "min": int(lbs.min()),
                "max": int(lbs.max()),
                "mean": float(lbs.mean()),
                "percentiles": pct(lbs, [0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100]),
                "histogram": {
                    str(k): int(v) for k, v in sorted(Counter(lbs.tolist()).items())
                },
            },
            "upper_bound_min_deletions": {
                "min": int(ubs.min()),
                "max": int(ubs.max()),
                "mean": float(ubs.mean()),
                "percentiles": pct(ubs, [0, 50, 90, 100]),
            },
            "exact_min_hitting_set": {
                "n_with_exact": n_exact,
                "n_unknown": len(records) - n_exact,
                "fraction_exact": float(n_exact) / len(records),
                "status_histogram": dict(exact_status_hist),
                "note": (
                    "exact set only via bounds-coincide / bitset / branch-and-bound; "
                    "never a lone heuristic"
                ),
            },
            "zone_counts_all_unselected": dict(zones),
            "multi_community_q_count_cc": multi_comm,
            "multi_community_q_count_lp": multi_lp,
            "multi_community_q_count_spatial_knn": multi_knn,
            "multi_community_q_count_ring": multi_ring,
            "easiest100_zone_distribution": dict(easiest100_zones),
        },
        "easiest_to_insert_candidates": {
            "ranking_key": (
                "lower_bound_min_deletions ASC, blocker_edge_count ASC, "
                "upper_bound_min_deletions ASC, q lexicographic"
            ),
            "disclaimer": (
                "Structural insertion-difficulty ranks only. "
                "Does NOT claim any +1 construction exists; "
                "does NOT search for size 113/165."
            ),
            "top_20_summary": [
                {
                    "q": r["q"],
                    "zone": r["zone"],
                    "ring_depth": r["ring_depth"],
                    "blocker_edge_count": r["blocker_edge_count"],
                    "lower_bound_min_deletions": r["lower_bound_min_deletions"],
                    "upper_bound_min_deletions": r["upper_bound_min_deletions"],
                    "exact_min_hitting_set": r["exact_min_hitting_set"],
                    "exact_status": r["exact_status"],
                    "involved_baseline_count": r["involved_baseline_count"],
                    "n_communities_touched": r["n_communities_touched"],
                    "communities_touched": r["communities_touched"],
                    "n_spatial_knn_communities_touched": r[
                        "n_spatial_knn_communities_touched"
                    ],
                    "spatial_knn_communities_touched": r[
                        "spatial_knn_communities_touched"
                    ],
                    "n_ring_band_communities_touched": r[
                        "n_ring_band_communities_touched"
                    ],
                    "ring_band_communities_touched": r["ring_band_communities_touched"],
                }
                for r in easiest_min
            ],
            "min_lower_bound": min_lb,
            "n_at_min_lower_bound": int(np.sum(lbs == min_lb)),
            "multi_spatial_community_among_easiest": multi_comm_easiest,
        },
        "paths": {
            "full_detail_gz": f"scratch/audit/agent_a/{detail_name}",
            "communities": f"scratch/audit/agent_a/blocker_communities_n{n}.json",
            "top_k_full_in_gz": TOP_K_FULL,
        },
        "run_commands": [
            f"python scratch/audit/agent_a/scripts/blocker_audit.py --n {n}",
            "python scratch/audit/agent_a/scripts/blocker_audit.py --n all",
        ],
        "search_for_165_or_113": False,
        "elapsed_sec": round(elapsed, 3),
    }

    stats_path = os.path.join(out_dir, f"blocker_stats_n{n}.json")
    comm_path = os.path.join(out_dir, f"blocker_communities_n{n}.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats_doc, f, indent=2)
    with open(comm_path, "w", encoding="utf-8") as f:
        json.dump(communities_doc, f, indent=2)

    print(
        f"n={n} done in {elapsed:.1f}s | qs={len(candidates)} | "
        f"min_lb={min_lb} | proj_edges={len(proj_edges)} | "
        f"CC={len(comps_cc)} | knn_comms={n_knn} | "
        f"multi_knn_q={multi_knn} | exact_frac={n_exact/len(records):.3f}",
        flush=True,
    )
    return {
        "n": n,
        "stats_path": stats_path,
        "comm_path": comm_path,
        "detail_path": detail_path,
        "min_lb": min_lb,
        "n_at_min_lb": int(np.sum(lbs == min_lb)),
        "n_communities_cc": len(comps_cc),
        "n_non_isolate_cc": n_conflict_comms,
        "n_communities_lp": len(comps_lp),
        "n_non_isolate_lp": n_lp_noniso,
        "n_spatial_knn": n_knn,
        "multi_knn_q": multi_knn,
        "n_far_knn_bridges": len(far_knn_bridges),
        "top5": stats_doc["easiest_to_insert_candidates"]["top_20_summary"][:5],
        "easiest100_zones": dict(easiest100_zones),
        "exact_frac": n_exact / len(records),
        "elapsed_sec": elapsed,
        "hash": baseline_hash,
        "far_cc": len(far_comms),
        "far_lp": 0,
    }


def write_report(summaries: List[Dict[str, Any]], out_dir: str) -> str:
    lines = [
        "# Audit Agent A — Insertion Blockers & Conflict Communities",
        "",
        "**Scope:** Wave 1 / Gate 1 structural audit only.",
        "**No search** for constructions of size 113 (n=64) or 165 (n=100).",
        "**No modifications** to verifiers, baselines, `conflict_metric.py`, or `results/certified`.",
        "",
        f"- Git commit: `{git_commit()}`",
        f"- Schema: `{SCHEMA_VERSION}`",
        f"- Deterministic seed: `{DETERMINISTIC_SEED}`",
        (
            f"- Exact hitting-set only when bounds coincide, bitset DP "
            f"(≤{EXACT_BITSET_MAX} verts), or branch-and-bound (≤{EXACT_BB_MAX}). "
            "Heuristics alone are never labeled exact."
        ),
        "",
        "## Blocker definition",
        "",
        "- **Type1** (q as pivot): each pair `p1,p2 ∈ S0` with `|p1−q|²=|p2−q|²` → edge `{p1,p2}`.",
        "- **Type2** (existing pivot `b`): each `b,p ∈ S0` with `|q−b|²=|p−b|²` → edge `{b,p}`.",
        "- Min deletions = min vertex cover of the union of these blocker edges.",
        "",
        "## Hashes used",
        "",
    ]
    for s in summaries:
        lines.append(
            f"- n={s['n']}: `{s['hash']}` (matches `phase0_baseline_reverify.json`)."
        )
    lines += ["", "## Files written", ""]
    for s in summaries:
        lines.append(f"- `blocker_stats_n{s['n']}.json`")
        lines.append(f"- `blocker_communities_n{s['n']}.json`")
        lines.append(
            f"- `blocker_detail_n{s['n']}.json.gz` (top-{TOP_K_FULL} full edges + compact all-q)"
        )
    lines += [
        "- `agent_a_report.md` (this file)",
        "- `scripts/blocker_audit.py`",
        "",
        "## Top findings",
        "",
    ]
    for s in summaries:
        lines += [
            f"### n={s['n']}",
            "",
            f"- Runtime ≈ {s['elapsed_sec']:.1f}s; exact fraction ≈ {s['exact_frac']:.3f}.",
            (
                f"- Full blocker-projection CC: **{s['n_communities_cc']}** "
                f"(giant coupling of all S0 if 1). "
                f"Spatial 6-NN communities: **{s['n_spatial_knn']}**; "
                f"multi-spatial-community qs: **{s['multi_knn_q']}**; "
                f"spatially-far conflict bridges (knn): **{s['n_far_knn_bridges']}**."
            ),
            (
                f"- Min deletion LB over unselected q: **{s['min_lb']}** "
                f"({s['n_at_min_lb']} cells)."
            ),
            f"- Easiest-100 zone mix: `{s['easiest100_zones']}`.",
            "- Easiest-ranked q (structural only — **not** claimed insertable):",
            "",
        ]
        for i, t in enumerate(s["top5"]):
            exact = t["exact_min_hitting_set"]
            exact_s = (
                str(exact) if exact is not None else f"unknown/{t['exact_status']}"
            )
            knn_n = t.get("n_spatial_knn_communities_touched", "?")
            lines.append(
                f"  {i+1}. q={t['q']} zone={t['zone']} edges={t['blocker_edge_count']} "
                f"LB={t['lower_bound_min_deletions']} UB={t['upper_bound_min_deletions']} "
                f"exact={exact_s} spatial_knn_comms={knn_n}"
            )
        lines.append("")
    lines += [
        "## Interpretation constraints",
        "",
        "- Low blocker counts / low deletion LBs mark structurally least-obstructed cells for later shell universes.",
        "- Far-coupled communities support non-local conflict (RH-3); prefer multi-region variables over pure spatial boxes.",
        "- This report does **not** assert existence of any legal |S|=|S0|+1 set.",
        "",
        "## Run commands",
        "",
        "```bash",
        "python scratch/audit/agent_a/scripts/blocker_audit.py --n all",
        "```",
        "",
    ]
    path = os.path.join(out_dir, "agent_a_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", choices=["64", "100", "all"], default="all")
    args = parser.parse_args()
    out_dir = os.path.join(ROOT, "scratch", "audit", "agent_a")
    os.makedirs(out_dir, exist_ok=True)

    jobs = []
    if args.n in ("64", "all"):
        jobs.append((64, SOL_64))
    if args.n in ("100", "all"):
        jobs.append((100, SOL_100))

    summaries = []
    for n, sol in jobs:
        print(f"=== Auditing n={n} ===", flush=True)
        summaries.append(run_for_n(n, sol, out_dir))

    report = write_report(summaries, out_dir)
    print("Wrote report", report)
    print(
        json.dumps(
            {
                "summaries": [
                    {
                        **{k: v for k, v in s.items() if k != "top5"},
                        "top5_q": [t["q"] for t in s["top5"]],
                    }
                    for s in summaries
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
