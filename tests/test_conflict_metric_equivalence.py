"""Gate 0: V(S) <-> verifier A <-> verifier B equivalence tests.

Main-owned. Compares conflict_count == 0 against both formal verifiers.
"""
from __future__ import annotations

import itertools
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.verification.conflict_metric import (
    ConflictMetricError,
    conflict_count,
    conflict_witnesses,
)
from src.verification.oracle_verifier import (
    ValidationError as ValidationErrorA,
    is_legal_pivot_method,
)
from src.verification_independent.independent_verifier import verify_independent
from data.baselines.official_raw import SOL_64, SOL_100


def _triple(points, n):
    """Return (V_is_zero, A_legal, B_legal) or raise if structural handling disagrees."""
    struct_errs = []
    v_zero = None
    a_ok = None
    b_ok = None
    try:
        v_zero = conflict_count(points, n) == 0
    except ConflictMetricError as e:
        struct_errs.append(("V", type(e).__name__, str(e)))
    try:
        a_ok, _ = is_legal_pivot_method(points, n)
    except ValidationErrorA as e:
        struct_errs.append(("A", type(e).__name__, str(e)))
    try:
        b_ok, _ = verify_independent(points, n)
    except Exception as e:
        # independent verifier may raise ValueError/TypeError on structure
        struct_errs.append(("B", type(e).__name__, str(e)))

    if struct_errs:
        # All three must reject structurally invalid input
        if len(struct_errs) != 3:
            raise AssertionError(
                f"structural disagreement on points={points} n={n}: {struct_errs}"
            )
        return None  # all rejected structurally — OK
    if not (v_zero is a_ok is (bool(b_ok))):
        raise AssertionError(
            f"DISAGREEMENT points={list(points)} n={n}: "
            f"V_zero={v_zero} A={a_ok} B={b_ok}"
        )
    return v_zero, a_ok, bool(b_ok)


class TestConflictMetricEquivalence(unittest.TestCase):
    def test_empty_singleton_pair(self):
        self.assertEqual(_triple([], 3), (True, True, True))
        self.assertEqual(_triple([(0, 0)], 3), (True, True, True))
        self.assertEqual(_triple([(0, 0), (1, 0)], 3), (True, True, True))

    def test_legal_small(self):
        # No equal distances from any pivot among three non-isosceles points
        pts = [(0, 0), (1, 0), (0, 2)]
        self.assertEqual(_triple(pts, 4), (True, True, True))
        self.assertEqual(conflict_count(pts, 4), 0)

    def test_illegal_isosceles(self):
        pts = [(0, 0), (1, 0), (0, 1)]  # apex (0,0), d2=1 twice
        self.assertEqual(_triple(pts, 3), (False, False, False))
        self.assertGreater(conflict_count(pts, 3), 0)
        w = conflict_witnesses(pts, 3)
        self.assertTrue(any(t["pivot"] == (0, 0) for t in w))

    def test_illegal_collinear_midpoint(self):
        pts = [(0, 0), (1, 0), (2, 0)]  # apex (1,0)
        self.assertEqual(_triple(pts, 3), (False, False, False))
        self.assertGreater(conflict_count(pts, 3), 0)

    def test_duplicate_rejected(self):
        self.assertIsNone(_triple([(0, 0), (0, 0)], 2))

    def test_oob_rejected(self):
        self.assertIsNone(_triple([(0, 0), (2, 0)], 2))

    def test_exhaustive_n4(self):
        n = 4
        cells = [(x, y) for x in range(n) for y in range(n)]
        # Exhaust subsets up to size 5 (C(16,5)=4368; up to 4 is enough & fast)
        checked = 0
        for k in range(0, 5):
            for subset in itertools.combinations(cells, k):
                _triple(list(subset), n)
                checked += 1
        self.assertGreater(checked, 1000)

    def test_random_small_grids(self):
        for n, seed, trials in [(5, 11, 200), (6, 22, 200), (10, 33, 300)]:
            rng = random.Random(seed)
            cells = [(x, y) for x in range(n) for y in range(n)]
            for _ in range(trials):
                k = rng.randint(0, min(12, n * n))
                pts = rng.sample(cells, k)
                _triple(pts, n)

    def test_random_large_grids(self):
        for n, seed, trials, kmax in [
            (64, 101, 40, 40),
            (100, 202, 40, 50),
        ]:
            rng = random.Random(seed)
            for _ in range(trials):
                k = rng.randint(0, kmax)
                pts = [
                    (rng.randrange(n), rng.randrange(n)) for __ in range(k)
                ]
                # may have dups — filter unique
                pts = list(dict.fromkeys(pts))
                _triple(pts, n)

    def test_official_baselines(self):
        self.assertEqual(_triple(list(SOL_64), 64), (True, True, True))
        self.assertEqual(_triple(list(SOL_100), 100), (True, True, True))
        self.assertEqual(conflict_count(SOL_64, 64), 0)
        self.assertEqual(conflict_count(SOL_100, 100), 0)

    def test_baseline_perturbations(self):
        rng = random.Random(7)
        for n, sol in [(64, list(SOL_64)), (100, list(SOL_100))]:
            S = set(map(tuple, sol))
            # remove one
            p = rng.choice(list(S))
            _triple(list(S - {p}), n)
            # swap: remove one, try add a random empty
            q = (rng.randrange(n), rng.randrange(n))
            while q in S:
                q = (rng.randrange(n), rng.randrange(n))
            _triple(list((S - {p}) | {q}), n)
            # add one if possible (may be illegal)
            r = (rng.randrange(n), rng.randrange(n))
            while r in S:
                r = (rng.randrange(n), rng.randrange(n))
            _triple(list(S | {r}), n)

    def test_witness_cross_check(self):
        pts = [(0, 0), (2, 0), (1, 0), (1, 2)]
        n = 4
        v = conflict_count(pts, n)
        self.assertGreater(v, 0)
        ok_a, w_a = is_legal_pivot_method(pts, n)
        ok_b, w_b = verify_independent(pts, n)
        self.assertFalse(ok_a)
        self.assertFalse(ok_b)
        ws = conflict_witnesses(pts, n)
        self.assertTrue(ws)
        # A's witness pivot should appear among V witnesses
        self.assertTrue(any(t["pivot"] == tuple(w_a["pivot"]) for t in ws))


if __name__ == "__main__":
    unittest.main(verbosity=2)
