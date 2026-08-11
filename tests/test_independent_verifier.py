"""
Own tests for the independent verifier (src/verification_independent/independent_verifier.py).

These tests, including the brute-force reference implementation used for fuzzing,
are written from scratch by the independent-verifier agent. The brute-force checker
below is intentionally a *separate* algorithm (plain O(|S|^3) triple enumeration using
Python arbitrary-precision ints) from the numpy sort-based approach in the module under
test, so that agreement between the two is meaningful evidence of correctness.
"""

import json
import os
import random
import subprocess
import sys
from itertools import combinations, permutations

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "verification_independent"))
from independent_verifier import verify_independent, main, _validate_structure  # noqa: E402

MODULE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "src", "verification_independent", "independent_verifier.py"
)


# ---------------------------------------------------------------------------
# Separate, independently-written brute-force reference oracle (O(|S|^3)).
# ---------------------------------------------------------------------------
def brute_force_is_legal(points, n):
    """
    Reference oracle: explicitly enumerate all ordered triples (a, b, c) of pairwise
    distinct points and check squared_dist(a,b) == squared_dist(b,c) directly, using
    pure Python ints. This is a deliberately different code path (no numpy, no
    sorting, no matrix, plain triple-nested enumeration) from verify_independent.
    """
    # Structural checks mirrored independently (kept simple/naive on purpose).
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError("bad n")
    seen = set()
    pts = []
    for p in points:
        x, y = p[0], p[1]
        if not isinstance(x, int) or isinstance(x, bool):
            raise ValueError("bad coord")
        if not isinstance(y, int) or isinstance(y, bool):
            raise ValueError("bad coord")
        if not (0 <= x < n and 0 <= y < n):
            raise ValueError("out of range")
        if (x, y) in seen:
            raise ValueError("duplicate")
        seen.add((x, y))
        pts.append((x, y))

    m = len(pts)
    for b in range(m):
        for a in range(m):
            if a == b:
                continue
            for c in range(m):
                if c == b or c == a:
                    continue
                d_ab = (pts[a][0] - pts[b][0]) ** 2 + (pts[a][1] - pts[b][1]) ** 2
                d_bc = (pts[b][0] - pts[c][0]) ** 2 + (pts[b][1] - pts[c][1]) ** 2
                if d_ab == d_bc:
                    return False
    return True


# ---------------------------------------------------------------------------
# Basic legality tests
# ---------------------------------------------------------------------------
def test_ordinary_isosceles_triangle_rejected():
    # (0,0)-(1,0) dist^2=1 ; (1,0)-(0,1) dist^2=2 ; (0,0)-(0,1) dist^2 = 1
    # pivot (0,0): distances to (1,0)=1 and to (0,1)=1 -> repeated -> illegal.
    ok, witness = verify_independent([(0, 0), (1, 0), (0, 1)], 4)
    assert ok is False
    assert witness is not None
    assert witness["squared_distance"] == 1


def test_degenerate_collinear_equidistant_triple_rejected():
    ok, witness = verify_independent([(0, 0), (1, 0), (2, 0)], 4)
    assert ok is False
    assert witness["pivot"] == (1, 0)
    assert witness["squared_distance"] == 1


def test_legal_three_point_set_accepted():
    # squared distances: (0,0)-(1,0)=1, (0,0)-(0,2)=4, (1,0)-(0,2)=1+4=5 -> all distinct
    ok, witness = verify_independent([(0, 0), (1, 0), (0, 2)], 4)
    assert ok is True
    assert witness is None


def test_duplicate_points_rejected():
    with pytest.raises(ValueError):
        verify_independent([(0, 0), (1, 1), (0, 0)], 4)


def test_negative_coordinate_rejected():
    with pytest.raises(ValueError):
        verify_independent([(-1, 0), (1, 1)], 4)


def test_out_of_range_coordinate_rejected():
    with pytest.raises(ValueError):
        verify_independent([(0, 0), (4, 4)], 4)  # n=4 => valid range is 0..3


def test_float_coordinate_rejected():
    with pytest.raises(ValueError):
        verify_independent([(0, 0), (1.0, 1)], 4)


def test_bool_coordinate_rejected():
    with pytest.raises(ValueError):
        verify_independent([(0, 0), (True, 1)], 4)


def test_non_positive_n_rejected():
    with pytest.raises(ValueError):
        verify_independent([(0, 0)], 0)
    with pytest.raises(ValueError):
        verify_independent([(0, 0)], -5)


def test_empty_set_accepted():
    ok, witness = verify_independent([], 5)
    assert ok is True
    assert witness is None


def test_single_point_accepted():
    ok, witness = verify_independent([(2, 3)], 5)
    assert ok is True
    assert witness is None


def test_two_points_always_accepted():
    # No three distinct points exist, so this is vacuously legal regardless of distance.
    ok, witness = verify_independent([(0, 0), (1, 0)], 5)
    assert ok is True


# ---------------------------------------------------------------------------
# Cross-check against the brute-force oracle on the same fixed cases.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "points,n",
    [
        ([(0, 0), (1, 0), (0, 1)], 4),
        ([(0, 0), (1, 0), (2, 0)], 4),
        ([(0, 0), (1, 0), (0, 2)], 4),
        ([], 5),
        ([(2, 3)], 5),
        ([(0, 0), (1, 0)], 5),
    ],
)
def test_matches_brute_force_on_fixed_cases(points, n):
    fast_ok, _ = verify_independent(points, n)
    slow_ok = brute_force_is_legal(points, n)
    assert fast_ok == slow_ok


# ---------------------------------------------------------------------------
# Randomized fuzz test: verify_independent vs brute_force_is_legal on many random
# subsets of a small grid.
# ---------------------------------------------------------------------------
def test_randomized_fuzz_against_brute_force():
    rng = random.Random(20260811)  # fixed seed for reproducibility
    n = 6
    all_cells = [(x, y) for x in range(n) for y in range(n)]
    num_trials = 200
    mismatches = []

    for trial in range(num_trials):
        k = rng.randint(0, 8)
        subset = rng.sample(all_cells, k)
        fast_ok, fast_witness = verify_independent(subset, n)
        slow_ok = brute_force_is_legal(subset, n)
        if fast_ok != slow_ok:
            mismatches.append((trial, subset, fast_ok, slow_ok))

    assert not mismatches, f"verify_independent disagreed with brute force: {mismatches}"


def test_fuzz_witness_is_always_genuine_when_illegal():
    """When verify_independent reports illegal, the witness triple it returns must
    itself independently satisfy the forbidden-distance condition (checked here with
    a third, standalone computation, not reusing any helper from the module)."""
    rng = random.Random(999)
    n = 6
    all_cells = [(x, y) for x in range(n) for y in range(n)]
    checked_at_least_one_failure = False

    for _ in range(200):
        k = rng.randint(3, 10)
        subset = rng.sample(all_cells, k)
        ok, witness = verify_independent(subset, n)
        if not ok:
            checked_at_least_one_failure = True
            b = witness["pivot"]
            a = witness["a"]
            c = witness["c"]
            d_ab = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            d_cb = (c[0] - b[0]) ** 2 + (c[1] - b[1]) ** 2
            assert d_ab == d_cb == witness["squared_distance"]
            assert a != b and c != b and a != c
            assert a in subset and b in subset and c in subset

    assert checked_at_least_one_failure, "fuzz run never produced an illegal example to check"


# ---------------------------------------------------------------------------
# CLI test: reads JSON from disk independently.
# ---------------------------------------------------------------------------
def test_cli_pass_and_fail_via_subprocess(tmp_path):
    legal_path = tmp_path / "legal.json"
    legal_path.write_text(json.dumps({"n": 4, "points": [[0, 0], [1, 0], [0, 2]]}))
    result = subprocess.run(
        [sys.executable, MODULE_PATH, str(legal_path)], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "PASS" in result.stdout

    illegal_path = tmp_path / "illegal.json"
    illegal_path.write_text(json.dumps({"n": 4, "points": [[0, 0], [1, 0], [0, 1]]}))
    result = subprocess.run(
        [sys.executable, MODULE_PATH, str(illegal_path)], capture_output=True, text=True
    )
    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "witness" in result.stdout
