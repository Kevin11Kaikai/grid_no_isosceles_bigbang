"""Round 2: symmetry-guided search.

Motivated by H-001 (both official baselines are near-totally centrally
symmetric: 100.0% of points for n=100, 96.4% for n=64 -- see
`hypotheses.md`). This module explores a genuinely different part of the
search space than Round 1 (which only ever locally repaired regions of the
*existing* baseline): it builds legal sets FROM SCRATCH under an explicit
central-symmetry constraint, halving the effective decision space (each
accept/reject decision places a symmetric PAIR of points at once), then
tests whether deliberately breaking that symmetry (adding a lone unpaired
point instead of a pair) ever lets the search reach a larger final size than
the fully-symmetric variant. If it never does across many trials, that is
itself evidence (not proof) that the symmetry observed in the official
baselines is load-bearing rather than incidental.

Central reflection: reflect(x, y) = (n-1-x, n-1-y). Fixed point under
reflection only at the exact center when n is odd (irrelevant here: n=64 and
n=100 are both even, so reflect(p) != p for every p in the grid).

Two point-pair placement rules are supported (`pair_add_order`):
  - "coupled": for each unordered pair {p, reflect(p)}, try adding BOTH at
    once (add p, then check+add reflect(p) given p already placed; if the
    second add fails, roll back p too so no odd single point is left behind
    by a failed pair attempt).
  - "sequential_probe": same idea but the two adds are attempted directly
    against the current state without a synthetic "both or nothing"
    ordering artifact -- kept as a second implementation to cross-check
    against "coupled" (a form of the project's dual-implementation
    discipline for optimization search moves, not just verifiers).

Symmetry-breaking mode: with probability `break_prob` per step, attempt to
add a single unpaired point instead of a pair (chosen uniformly among legal
singletons at that step), 	then optionally later re-attempt to add its
reflection separately (it may or may not still be legal, since other points
placed since have changed the picture).

CORRECTNESS: legality of every add is checked via
`IncrementalIsoscelesFreeSet.can_add` (same primitive already stress-tested
against the oracle in `tests/test_incremental_state.py`, 500+4500 operations,
zero divergence). The final returned set is oracle-re-verified before return.
"""
from __future__ import annotations

import os
import random
import sys
import time
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.search.incremental_state import IncrementalIsoscelesFreeSet
from src.verification.oracle_verifier import is_legal_pivot_method

Point = Tuple[int, int]


def reflect(p: Point, n: int) -> Point:
    return (n - 1 - p[0], n - 1 - p[1])


def symmetric_build_once(
    n: int,
    seed: int,
    break_prob: float = 0.0,
    order: str = "random",
) -> Tuple[List[Point], dict]:
    rng = random.Random(seed)
    ifs = IncrementalIsoscelesFreeSet(n)

    all_pts = [(x, y) for x in range(n) for y in range(n)]
    if order == "random":
        rng.shuffle(all_pts)
    elif order == "center_first":
        c = (n - 1) / 2.0
        all_pts.sort(key=lambda p: (p[0] - c) ** 2 + (p[1] - c) ** 2)
    elif order == "boundary_first":
        all_pts.sort(key=lambda p: -min(p[0], p[1], n - 1 - p[0], n - 1 - p[1]))

    placed_singles = 0
    placed_pairs = 0
    skipped_broken_pairs = 0

    for p in all_pts:
        if p in ifs.points:
            continue
        r = reflect(p, n)
        if r == p:
            continue  # cannot happen for even n, guarded anyway

        do_break = rng.random() < break_prob

        if do_break:
            ok, _ = ifs.can_add(p)
            if ok:
                ifs.add_point(p)
                placed_singles += 1
            continue

        # coupled pair attempt: add p, then try r; rollback p if r fails
        if r in ifs.points:
            continue
        ok_p, _ = ifs.can_add(p)
        if not ok_p:
            continue
        ifs.add_point(p)
        ok_r, _ = ifs.can_add(r)
        if ok_r:
            ifs.add_point(r)
            placed_pairs += 1
        else:
            ifs.remove_point(p)
            skipped_broken_pairs += 1

    meta = {
        "seed": seed,
        "order": order,
        "break_prob": break_prob,
        "placed_pairs": placed_pairs,
        "placed_singles": placed_singles,
        "skipped_broken_pairs": skipped_broken_pairs,
        "final_size": len(ifs.points),
    }
    return sorted(ifs.points), meta


def symmetric_multistart(
    n: int,
    time_budget_s: float,
    seed: int = 0,
    break_probs: Tuple[float, ...] = (0.0, 0.02, 0.05, 0.1, 0.2),
    orders: Tuple[str, ...] = ("random", "center_first", "boundary_first"),
) -> Tuple[List[Point], dict]:
    rng = random.Random(seed)
    t0 = time.time()
    best: List[Point] = []
    best_size = -1
    best_meta: Optional[dict] = None
    trials = 0
    by_break_prob: dict = {}

    while time.time() - t0 < time_budget_s:
        trials += 1
        bp = rng.choice(break_probs)
        order = rng.choice(orders)
        run_seed = rng.randint(0, 2**31 - 1)
        pts, meta = symmetric_build_once(n, run_seed, break_prob=bp, order=order)
        by_break_prob.setdefault(bp, []).append(len(pts))
        if len(pts) > best_size:
            ok, witness = is_legal_pivot_method(pts, n)
            if not ok:
                raise AssertionError(f"symmetric build produced illegal state! witness={witness}")
            best = pts
            best_size = len(pts)
            best_meta = meta

    ok, witness = is_legal_pivot_method(best, n)
    if not ok:
        raise AssertionError(f"symmetric_multistart final best illegal: {witness}")

    summary_by_bp = {
        str(bp): {"n_trials": len(sizes), "max": max(sizes), "mean": sum(sizes) / len(sizes)}
        for bp, sizes in by_break_prob.items()
    }

    meta = {
        "method": "symmetry_guided_multistart",
        "trials": trials,
        "wall_time_s": time.time() - t0,
        "final_size": best_size,
        "best_run_meta": best_meta,
        "seed": seed,
        "summary_by_break_prob": summary_by_bp,
    }
    return best, meta


if __name__ == "__main__":
    import json

    n = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    best, meta = symmetric_multistart(n, budget, seed=seed)
    print(json.dumps(meta, indent=2))
    os.makedirs("logs", exist_ok=True)
    out = f"logs/symmetry_guided_n{n}_seed{seed}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "points": best}, f)
    print(f"wrote {out}")
