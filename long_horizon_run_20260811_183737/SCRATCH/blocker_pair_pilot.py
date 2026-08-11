#!/usr/bin/env python3
"""LH-1 Route A: blocker-pair → multi-add exact microproblems (n=100, r=2).

Necessary condition for co-inserting q1,q2 with |R|=2 deletions from official S0:
  joint vertex-cover number of union(blocker_edges(q1), blocker_edges(q2)) <= 2.

If joint VC <= 2, enumerate size-2 covers, test legality of S0\\R ∪ {q1,q2},
then scan third add-cells for a legal size-165 set.

Scoped claims only. Never writes to results/certified/.
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import os
import sys
import time
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.search.hamming_shell_conflict import universe_hash  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import (  # noqa: E402
    verify_independent,
)

Point = Tuple[int, int]
N = 100

AUDIT_SCRIPT = os.path.join(
    ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py"
)


def load_blocker_audit():
    spec = importlib.util.spec_from_file_location("blocker_audit_lh", AUDIT_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def sq(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def edges_as_frozensets(rec: dict) -> List[frozenset]:
    out = []
    for e in rec["blocker_edges"]:
        p1, p2 = tuple(e[0]), tuple(e[1])
        out.append(frozenset((p1, p2)))
    return out


def exact_min_vc_and_covers(
    edges: Sequence[frozenset], universe: Sequence[Point], max_k: int = 3
) -> Tuple[Optional[int], List[List[Point]]]:
    """Exact min vertex cover for tiny edge sets via subset enum on involved verts."""
    if not edges:
        return 0, [[]]
    involved = sorted({p for e in edges for p in e})
    # Prefer full involved set; if large, still OK for easiest qs (~5 each).
    n_inv = len(involved)
    if n_inv > 24:
        # fallback: only search covers of size <= max_k among involved
        best = None
        covers: List[List[Point]] = []
        for k in range(0, max_k + 1):
            for comb in itertools.combinations(involved, k):
                C = set(comb)
                if all(e & C for e in edges):
                    best = k
                    covers.append(sorted(comb))
            if best is not None:
                return best, covers
        return None, []

    # Exact via MIS on clique-expanded? Edges are already 2-uniform VC instance.
    # Enumerate all subsets by size.
    best = None
    covers = []
    for k in range(0, n_inv + 1):
        found = []
        for comb in itertools.combinations(involved, k):
            C = set(comb)
            if all(e & C for e in edges):
                found.append(sorted(comb))
        if found:
            return k, found
    return None, []


def legal_vs(points: Sequence[Point]) -> bool:
    ok, _ = is_legal_pivot_method(list(points), N)
    return bool(ok)


def third_candidates(
    s0: Set[Point],
    rem: Set[Point],
    forced_add: Sequence[Point],
    easiest: Sequence[Point],
    halo_radius: int = 3,
) -> List[Point]:
    """Priority pool for third add: other easiest + chebyshev halo around Rem∪forced."""
    pool: Set[Point] = set()
    for q in easiest:
        t = tuple(q)
        if t not in s0 and t not in forced_add:
            pool.add(t)  # type: ignore[arg-type]
    anchors = list(rem) + list(forced_add)
    for ax, ay in anchors:
        for dx in range(-halo_radius, halo_radius + 1):
            for dy in range(-halo_radius, halo_radius + 1):
                x, y = ax + dx, ay + dy
                if 0 <= x < N and 0 <= y < N:
                    p = (x, y)
                    if p not in s0 and p not in forced_add:
                        pool.add(p)
    # Also include Agent-C U_small addables if available
    diag_path = os.path.join(
        ROOT, "scratch", "audit", "agent_c", "universe_halo_diagnostics.json"
    )
    if os.path.exists(diag_path):
        with open(diag_path, "r", encoding="utf-8") as f:
            diag = json.load(f)
        for p in diag["baselines"]["n100"]["universes"]["U_small"]["addable_unselected_points"]:
            t = (int(p[0]), int(p[1]))
            if t not in s0 and t not in forced_add:
                pool.add(t)
        for p in diag["baselines"]["n100"]["universes"]["U_medium"]["addable_unselected_points"]:
            t = (int(p[0]), int(p[1]))
            if t not in s0 and t not in forced_add:
                pool.add(t)
    return sorted(pool)


def dual_check(points: Sequence[Point]) -> dict:
    pts = [tuple(p) for p in points]
    ok_a, wit_a = is_legal_pivot_method(pts, N)  # type: ignore[arg-type]
    ok_b, meta_b = verify_independent(pts, N)
    v = conflict_count(pts, N)  # type: ignore[arg-type]
    return {
        "oracle_legal": bool(ok_a),
        "independent_legal": bool(ok_b),
        "V": int(v),
        "size": len(pts),
        "hash": sha256_of_points(pts),
        "oracle_witness": wit_a if not ok_a else None,
    }


def main() -> None:
    t0 = time.time()
    ba = load_blocker_audit()
    s0_list: List[Point] = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0_list)
    assert len(s0_list) == 164
    pivot_maps = ba.precompute_pivot_maps(s0_list)

    with open(
        os.path.join(ROOT, "scratch", "audit", "gate1_consistency_check.json"),
        "r",
        encoding="utf-8",
    ) as f:
        g1 = json.load(f)
    easiest = [tuple(p) for p in g1["n100_deletion_bound"]["easiest_16_qs_exact_min_deletions_2"]]
    assert len(easiest) == 16

    # Precompute blocker records
    recs: Dict[Point, dict] = {}
    edge_sets: Dict[Point, List[frozenset]] = {}
    for q in easiest:
        rec = ba.analyze_q(q, s0_list, pivot_maps, N)
        assert rec["exact_min_hitting_set"] == 2
        recs[q] = rec
        edge_sets[q] = edges_as_frozensets(rec)

    pair_rows = []
    legal_pair_after_rem = []
    feasible_165 = []
    joint_vc_hist: Dict[str, int] = defaultdict(int)

    # All C(16,2)=120 pairs
    for q1, q2 in itertools.combinations(easiest, 2):
        edges = sorted(set(edge_sets[q1]) | set(edge_sets[q2]), key=lambda e: sorted(e))
        involved = sorted({p for e in edges for p in e})
        joint_k, covers = exact_min_vc_and_covers(edges, involved, max_k=4)
        key = str(joint_k) if joint_k is not None else "unknown"
        joint_vc_hist[key] += 1
        row = {
            "q1": list(q1),
            "q2": list(q2),
            "n_union_edges": len(edges),
            "n_involved": len(involved),
            "joint_exact_vc": joint_k,
            "n_min_covers": len(covers) if joint_k is not None else 0,
        }
        if joint_k is None or joint_k > 2:
            row["r2_necessary_ok"] = False
            pair_rows.append(row)
            continue
        row["r2_necessary_ok"] = True

        # Enumerate all size-2 covers (if joint_k < 2, pad by adding any involved)
        covers2: List[List[Point]] = []
        if joint_k == 2:
            covers2 = covers
        elif joint_k < 2:
            base = covers[0] if covers else []
            need = 2 - len(base)
            extras = [p for p in involved if p not in base] or [p for p in s0_list if p not in base]
            for comb in itertools.combinations(extras, need):
                covers2.append(sorted(base + list(comb)))
            # also allow deleting any 2 from a larger optional set: keep small
            covers2 = covers2[:50]

        pair_hits = []
        for rem in covers2:
            rem_set = set(map(tuple, rem))
            core = [p for p in s0_list if p not in rem_set]
            # individual add legality
            ok1 = legal_vs(core + [q1])
            ok2 = legal_vs(core + [q2])
            ok12 = legal_vs(core + [q1, q2]) if (ok1 and ok2) else False
            entry = {
                "rem": [list(p) for p in rem],
                "ok_q1": ok1,
                "ok_q2": ok2,
                "ok_pair": ok12,
                "V_pair": conflict_count(core + [q1, q2], N) if (ok1 and ok2) else None,
            }
            if ok12:
                # search third
                thirds = third_candidates(s0_set, rem_set, [q1, q2], easiest, halo_radius=4)
                entry["n_third_scanned"] = len(thirds)
                found = None
                best_v = 10**9
                best_q3 = None
                for q3 in thirds:
                    pts = core + [q1, q2, q3]
                    v = conflict_count(pts, N)
                    if v < best_v:
                        best_v = v
                        best_q3 = q3
                    if v == 0 and legal_vs(pts):
                        found = q3
                        break
                entry["best_third_V"] = best_v if best_q3 is not None else None
                entry["best_third"] = list(best_q3) if best_q3 is not None else None
                if found is not None:
                    pts = sorted(core + [q1, q2, found])
                    dv = dual_check(pts)
                    entry["FEASIBLE_LEGAL"] = True
                    entry["dual"] = dv
                    feasible_165.append(
                        {
                            "q1": list(q1),
                            "q2": list(q2),
                            "q3": list(found),
                            "rem": [list(p) for p in rem],
                            "dual": dv,
                            "points": [list(p) for p in pts],
                        }
                    )
                else:
                    entry["FEASIBLE_LEGAL"] = False
                pair_hits.append(entry)
                legal_pair_after_rem.append(
                    {
                        "q1": list(q1),
                        "q2": list(q2),
                        "rem": entry["rem"],
                        "best_third_V": entry.get("best_third_V"),
                        "best_third": entry.get("best_third"),
                        "n_third_scanned": entry.get("n_third_scanned"),
                    }
                )
            else:
                pair_hits.append(entry)
        row["n_covers_checked"] = len(covers2)
        row["n_pair_legal_cores"] = sum(1 for e in pair_hits if e.get("ok_pair"))
        row["any_165"] = any(e.get("FEASIBLE_LEGAL") for e in pair_hits)
        # keep compact detail only for promising pairs
        if row["n_pair_legal_cores"] or row["any_165"]:
            row["cover_details"] = pair_hits
        pair_rows.append(row)

    # Also: single-q exact-2 covers → can we add that q + 2 other easiest with same Rem?
    # (r=2, three adds) — for each easiest q, enumerate its exact size-2 covers
    single_expand = []
    for q in easiest:
        edges = edge_sets[q]
        k, covers = exact_min_vc_and_covers(edges, [], max_k=2)
        assert k == 2
        for rem in covers:
            rem_set = set(map(tuple, rem))
            core = [p for p in s0_list if p not in rem_set]
            if not legal_vs(core + [q]):
                continue
            # choose 2 more from remaining easiest + medium add pool
            others = [p for p in easiest if p != q]
            # expand with U_small addables
            diag_path = os.path.join(
                ROOT, "scratch", "audit", "agent_c", "universe_halo_diagnostics.json"
            )
            with open(diag_path, "r", encoding="utf-8") as f:
                diag = json.load(f)
            add_pool = sorted(
                set(others)
                | {
                    (int(p[0]), int(p[1]))
                    for p in diag["baselines"]["n100"]["universes"]["U_small"][
                        "addable_unselected_points"
                    ]
                    if (int(p[0]), int(p[1])) not in s0_set
                }
            )
            best = None
            checked = 0
            # Cap combinations: prefer pairs from easiest first
            cand_pairs = list(itertools.combinations(others, 2))
            # add some mixed pairs (easiest + pool)
            extra = [p for p in add_pool if p not in others][:40]
            for a in others:
                for b in extra:
                    cand_pairs.append((a, b))
            # dedupe
            seen = set()
            uniq = []
            for a, b in cand_pairs:
                key = tuple(sorted((a, b)))
                if key in seen:
                    continue
                seen.add(key)
                uniq.append(key)
            for a, b in uniq:
                if len({q, a, b}) < 3:
                    continue
                if a in rem_set or b in rem_set or a in s0_set or b in s0_set:
                    continue
                checked += 1
                pts = core + [q, a, b]
                if conflict_count(pts, N) == 0 and legal_vs(pts):
                    best = (a, b)
                    break
            single_expand.append(
                {
                    "q": list(q),
                    "rem": [list(p) for p in rem],
                    "pairs_checked": checked,
                    "found": [list(best[0]), list(best[1])] if best else None,
                }
            )
            if best:
                pts = sorted(core + [q, best[0], best[1]])
                feasible_165.append(
                    {
                        "mode": "single_q_cover_plus_two",
                        "q1": list(q),
                        "q2": list(best[0]),
                        "q3": list(best[1]),
                        "rem": [list(p) for p in rem],
                        "dual": dual_check(pts),
                        "points": [list(p) for p in pts],
                    }
                )

    # Build a certificate-driven universe from all size-2 covers of easiest singles
    rem_pool: Set[Point] = set()
    add_pool: Set[Point] = set(easiest)
    for q in easiest:
        _, covers = exact_min_vc_and_covers(edge_sets[q], [], max_k=2)
        for rem in covers:
            rem_pool.update(map(tuple, rem))
    # include partners from covers of pairs with joint_k<=2
    for row in pair_rows:
        if row.get("r2_necessary_ok") and row.get("cover_details"):
            for det in row["cover_details"]:
                rem_pool.update(tuple(p) for p in det["rem"])

    rem_list = sorted(rem_pool)
    add_list = sorted(add_pool)
    uhash = universe_hash(rem_list, add_list)

    out = {
        "schema": "lh1_blocker_pair_pilot_v1",
        "n": 100,
        "baseline_size": 164,
        "baseline_hash": sha256_of_points(s0_list),
        "easiest_16": [list(q) for q in easiest],
        "n_pairs": len(pair_rows),
        "joint_vc_histogram": dict(joint_vc_hist),
        "n_pairs_r2_necessary_ok": sum(1 for r in pair_rows if r.get("r2_necessary_ok")),
        "n_pair_legal_after_some_rem": len(legal_pair_after_rem),
        "n_feasible_165": len(feasible_165),
        "feasible_165": feasible_165,
        "legal_pair_examples": legal_pair_after_rem[:40],
        "pair_rows_compact": [
            {
                k: r[k]
                for k in (
                    "q1",
                    "q2",
                    "n_union_edges",
                    "n_involved",
                    "joint_exact_vc",
                    "r2_necessary_ok",
                    "n_pair_legal_cores",
                    "any_165",
                    "n_covers_checked",
                    "n_min_covers",
                )
                if k in r
            }
            for r in pair_rows
        ],
        "certificate_universe_from_covers": {
            "U_id": "U_blocker_cover_e16",
            "n_rem": len(rem_list),
            "n_add": len(add_list),
            "n_vars": len(rem_list) + len(add_list),
            "universe_hash": uhash,
            "rem": [list(p) for p in rem_list],
            "add": [list(p) for p in add_list],
            "note": "Rem=union of exact size-2 covers of easiest-16 (+ pair covers); Add=easiest-16. Distinct from score U_small_r2.",
        },
        "single_q_expand_summary": {
            "n_cover_trials": len(single_expand),
            "n_found": sum(1 for s in single_expand if s["found"]),
            "trials": single_expand,
        },
        "wall_time_s": time.time() - t0,
        "claim_discipline": "No global UB. feasible_165 requires dual verify before promotion.",
    }

    exp_dir = os.path.join(RUN, "EXPERIMENTS", "LH1_blocker_pair")
    os.makedirs(exp_dir, exist_ok=True)
    out_path = os.path.join(exp_dir, "blocker_pair_pilot_n100.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")

    # Freeze universe separately for CP-SAT follow-up
    uni_path = os.path.join(exp_dir, "U_blocker_cover_e16.json")
    with open(uni_path, "w", encoding="utf-8") as f:
        json.dump(out["certificate_universe_from_covers"], f, indent=2, sort_keys=True)
        f.write("\n")

    print(json.dumps({
        "out_path": out_path,
        "joint_vc_histogram": out["joint_vc_histogram"],
        "n_pairs_r2_necessary_ok": out["n_pairs_r2_necessary_ok"],
        "n_pair_legal_after_some_rem": out["n_pair_legal_after_some_rem"],
        "n_feasible_165": out["n_feasible_165"],
        "universe": {
            "n_rem": len(rem_list),
            "n_add": len(add_list),
            "hash": uhash,
        },
        "single_found": out["single_q_expand_summary"]["n_found"],
        "wall_time_s": out["wall_time_s"],
    }, indent=2))


if __name__ == "__main__":
    main()
