"""Incremental isosceles-free set with O(|S|) add-check and full oracle cross-checks.

This mirrors (independently re-derived, not copy-pasted) the core idea used
in the official notebook's IsoscelesFreeSet: for every point q currently in
the set, maintain the set of squared distances from q to all other points
in the set ("forbidden_d2s[q]"). A candidate point p can be added iff:
  (a) no two points q1 != q2 already in S have d^2(p, q1) == d^2(p, q2)
      [p itself would become a pivot with a repeated distance], AND
  (b) for every q in S, d^2(p, q) is not already in forbidden_d2s[q]
      [q would become a pivot with a repeated distance once p is added].

Both conditions are checked in a single O(|S|) pass using a python dict
keyed by squared distance, mapping to the point that already realizes it
(so a violation is directly witnessed, not just detected).

CORRECTNESS DISCIPLINE (mandatory per project brief section 8): the
incremental cache is NOT trusted on its own. Every `best_so_far` checkpoint,
and periodically every N moves, this module's `.points` are re-verified
against the slow oracle in src/verification/oracle_verifier.py. Any
disagreement is a hard error (AssertionError), not a silent correction.
"""
from __future__ import annotations

import os
import sys
from typing import Dict, Optional, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.verification.oracle_verifier import is_legal_pivot_method

Point = Tuple[int, int]


def _sq_dist(a: Point, b: Point) -> int:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return dx * dx + dy * dy


class IncrementalIsoscelesFreeSet:
    def __init__(self, n: int):
        self.n = n
        self.points: Set[Point] = set()
        # forbidden_d2s[q] : dict {squared_distance -> some point p in S, p != q,
        #                          realizing that distance from q}
        self.forbidden_d2s: Dict[Point, Dict[int, Point]] = {}
        self._oracle_calls = 0
        self._moves_since_oracle_check = 0

    # ---- core queries -------------------------------------------------
    def can_add(self, p: Point) -> Tuple[bool, Optional[dict]]:
        if p in self.points:
            return False, {"reason": "already present", "point": p}
        if not (0 <= p[0] < self.n and 0 <= p[1] < self.n):
            return False, {"reason": "out of bounds", "point": p}

        seen_from_p: Dict[int, Point] = {}
        for q in self.points:
            d2 = _sq_dist(p, q)
            if d2 in seen_from_p:
                return False, {
                    "reason": "p_would_be_apex",
                    "pivot": p,
                    "point_1": seen_from_p[d2],
                    "point_2": q,
                    "squared_distance": d2,
                }
            seen_from_p[d2] = q
            if d2 in self.forbidden_d2s[q]:
                return False, {
                    "reason": "q_would_be_apex",
                    "pivot": q,
                    "point_1": self.forbidden_d2s[q][d2],
                    "point_2": p,
                    "squared_distance": d2,
                }
        return True, None

    def add_point(self, p: Point) -> bool:
        ok, witness = self.can_add(p)
        if not ok:
            return False
        self._add_unchecked(p)
        self._moves_since_oracle_check += 1
        return True

    def _add_unchecked(self, p: Point) -> None:
        d2s_from_p: Dict[int, Point] = {}
        for q in self.points:
            d2 = _sq_dist(p, q)
            self.forbidden_d2s[q][d2] = p
            d2s_from_p[d2] = q
        self.points.add(p)
        self.forbidden_d2s[p] = d2s_from_p

    def remove_point(self, p: Point) -> None:
        if p not in self.points:
            return
        self.points.remove(p)
        del self.forbidden_d2s[p]
        for q in self.points:
            d2 = _sq_dist(p, q)
            if d2 in self.forbidden_d2s[q]:
                del self.forbidden_d2s[q][d2]
        self._moves_since_oracle_check += 1

    def swap(self, remove_p: Point, add_p: Point) -> bool:
        """1-for-1 swap. Rolls back cleanly if add_p cannot legally be added."""
        had = remove_p in self.points
        if had:
            self.remove_point(remove_p)
        ok = self.add_point(add_p)
        if not ok and had:
            self._add_unchecked(remove_p)
        return ok

    # ---- correctness discipline ---------------------------------------
    def cross_check_with_oracle(self) -> None:
        self._oracle_calls += 1
        ok, witness = is_legal_pivot_method(list(self.points), self.n)
        if not ok:
            raise AssertionError(
                f"INCREMENTAL STATE BUG: oracle says ILLEGAL but incremental "
                f"cache thought it was legal. witness={witness} "
                f"points={sorted(self.points)}"
            )
        # Also check the forbidden_d2s cache itself is internally consistent:
        # recompute from scratch and compare.
        recomputed: Dict[Point, Dict[int, Point]] = {q: {} for q in self.points}
        for q in self.points:
            for r in self.points:
                if q == r:
                    continue
                d2 = _sq_dist(q, r)
                recomputed[q][d2] = r  # last writer; only need key set for our check
        for q in self.points:
            cached_keys = set(self.forbidden_d2s[q].keys())
            actual_keys = set(recomputed[q].keys())
            if cached_keys != actual_keys:
                raise AssertionError(
                    f"STALE CACHE BUG at pivot {q}: cached d2 keys {cached_keys} "
                    f"!= recomputed {actual_keys}"
                )
        self._moves_since_oracle_check = 0

    def size(self) -> int:
        return len(self.points)
