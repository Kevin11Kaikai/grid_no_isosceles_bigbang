"""Mandatory unit tests for src/verification/oracle_verifier.py.

Run with: python -m pytest tests/test_oracle_verifier.py -v
or, without pytest installed: python tests/test_oracle_verifier.py
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.verification.oracle_verifier import (
    ValidationError,
    check_structural_validity,
    full_cross_check,
    is_legal_bruteforce_triples,
    is_legal_pivot_method,
    verify,
)


def test_illegal_ordinary_isosceles():
    # (0,0)-(1,0)-(0,1): d((0,0),(1,0))^2=1, d((1,0),(0,1))^2=2, d((0,0),(0,1))^2=1
    # apex (0,0): distances to (1,0) and (0,1) are both 1 -> forbidden.
    pts = [(0, 0), (1, 0), (0, 1)]
    ok, w = is_legal_pivot_method(pts, n=2)
    assert ok is False, "ordinary isosceles triangle must be rejected"
    assert full_cross_check(pts, n=2) is False


def test_illegal_degenerate_collinear_equidistant():
    pts = [(0, 0), (1, 0), (2, 0)]
    ok, w = is_legal_pivot_method(pts, n=3)
    assert ok is False, "degenerate collinear equidistant triple must be rejected"
    assert w["pivot"] == (1, 0), f"expected pivot (1,0) (the midpoint), got {w['pivot']}"
    assert full_cross_check(pts, n=3) is False


def test_legal_small_set():
    # squared distances 1, 4, 5 -- all distinct as seen from every pivot.
    pts = [(0, 0), (1, 0), (0, 2)]
    ok, w = is_legal_pivot_method(pts, n=3)
    assert ok is True, f"expected legal, got witness {w}"
    assert full_cross_check(pts, n=3) is True


def test_duplicate_point_rejected():
    pts = [(0, 0), (1, 0), (1, 0)]
    try:
        is_legal_pivot_method(pts, n=2)
        assert False, "duplicate point must raise ValidationError"
    except ValidationError:
        pass


def test_negative_coordinate_rejected():
    pts = [(0, 0), (-1, 0), (0, 1)]
    try:
        is_legal_pivot_method(pts, n=5)
        assert False, "negative coordinate must raise ValidationError"
    except ValidationError:
        pass


def test_coordinate_equal_to_n_rejected():
    n = 4
    pts = [(0, 0), (n, 0)]  # x == n is out of [0, n-1]
    try:
        is_legal_pivot_method(pts, n=n)
        assert False, "coordinate == n must raise ValidationError (range is [0, n-1])"
    except ValidationError:
        pass


def test_float_coordinate_rejected():
    pts = [(0.0, 0), (1, 0)]
    try:
        is_legal_pivot_method(pts, n=5)
        assert False, "float coordinate must raise ValidationError"
    except ValidationError:
        pass


def test_bool_coordinate_rejected():
    # bool is a subclass of int in Python; must be explicitly excluded.
    pts = [(True, 0), (1, 1)]
    try:
        is_legal_pivot_method(pts, n=5)
        assert False, "bool coordinate must raise ValidationError"
    except ValidationError:
        pass


def test_empty_set_legal():
    ok, w = is_legal_pivot_method([], n=5)
    assert ok is True


def test_single_point_legal():
    ok, w = is_legal_pivot_method([(2, 2)], n=5)
    assert ok is True


def test_two_points_always_legal():
    # No three distinct points exist, so any 2-point set is trivially legal.
    ok, w = is_legal_pivot_method([(0, 0), (3, 4)], n=5)
    assert ok is True


def test_translation_invariance():
    # A legal set shifted by a constant vector (staying in range) stays legal;
    # an illegal set shifted stays illegal. Squared distances are
    # translation-invariant.
    legal = [(0, 0), (1, 0), (0, 2)]
    shifted = [(x + 2, y + 1) for x, y in legal]
    assert is_legal_pivot_method(legal, n=5)[0] is True
    assert is_legal_pivot_method(shifted, n=8)[0] is True

    illegal = [(0, 0), (1, 0), (2, 0)]
    shifted_illegal = [(x + 3, y + 3) for x, y in illegal]
    assert is_legal_pivot_method(illegal, n=5)[0] is False
    assert is_legal_pivot_method(shifted_illegal, n=8)[0] is False


def test_symmetry_transform_preserves_legality():
    # Reflection (x,y) -> (n-1-x, y) is an isometry of the grid, must preserve
    # squared-distance structure and hence legality.
    n = 5
    legal = [(0, 0), (1, 0), (0, 2)]
    reflected = [(n - 1 - x, y) for x, y in legal]
    check_structural_validity(reflected, n)
    assert is_legal_pivot_method(legal, n)[0] is True
    assert is_legal_pivot_method(reflected, n)[0] is True


def test_random_small_sets_fuzz():
    rng = random.Random(1234)
    n = 6
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    for trial in range(300):
        k = rng.randint(0, 7)
        pts = rng.sample(all_pts, k)
        # cross-check must never disagree
        r_pivot, w1 = is_legal_pivot_method(pts, n)
        r_brute, w2 = is_legal_bruteforce_triples(pts, n)
        assert r_pivot == r_brute, (
            f"trial {trial}: DISAGREEMENT pivot={r_pivot} brute={r_brute} "
            f"pts={pts} w1={w1} w2={w2}"
        )


def test_known_baseline_construction_legal_n64():
    # Smoke test against a small deterministic legal witness, not the full
    # 112-point baseline (that is checked separately in
    # tests/test_baseline_reproduction.py with size-appropriate methods).
    # Original fixture (0,0),(1,0),(0,2),(3,1) was WRONG: pivot (1,0) has
    # d^2=5 to both (0,2) and (3,1) -- it is actually illegal. Caught by this
    # test itself, which is exactly the point of running it. Replaced with a
    # hand-checked legal 4-point set.
    pts = [(0, 0), (1, 0), (0, 2), (4, 3)]
    ok, w = is_legal_pivot_method(pts, n=5)
    assert ok is True, f"witness {w}"
    assert full_cross_check(pts, n=5) is True


def _run_all():
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    _run_all()
