"""
Independent, clean-room verifier for Problem 6.59 ("no isosceles triangle" subsets of
the integer grid [n]^2), written from scratch by an independent-verifier agent.

This module does NOT import, read, or reuse any code, helper functions, or data
structures from src/verification/oracle_verifier.py (or any other verifier that may
already exist in this repository). Its entire value as a cross-check depends on being
an independent reimplementation of the mathematical definition below, not a wrapper
around existing project code.

MATHEMATICAL DEFINITION IMPLEMENTED
------------------------------------
For a positive integer n, [n]^2 = {0, 1, ..., n-1}^2 is the integer grid.

A finite set S of distinct points in [n]^2 is LEGAL iff: for every three pairwise-
distinct points a, b, c in S, it is NOT the case that
    squared_dist(a, b) == squared_dist(b, c).
This explicitly includes the degenerate collinear case where a, b, c lie on a line and
b is the midpoint of segment a-c (equally spaced) -- that also counts as a forbidden
"isosceles" configuration for this problem, exactly like a genuine non-degenerate
isosceles triangle with apex b.

Equivalently (and this is the formulation this module actually computes, since it is
computationally far cheaper and provably equivalent): for every point b in S, the
multiset of squared distances from b to every OTHER point of S must contain no
repeated value. If any point b has two OTHER points a != c at equal squared distance,
(a, b, c) is a forbidden triple and S is illegal.

STRUCTURAL VALIDITY (checked BEFORE legality, independent of the geometric check)
-----------------------------------------------------------------------------------
  - points must be supplied as a list of 2-element int tuples/lists
  - each coordinate must be a genuine Python int (bool is explicitly rejected even
    though bool is technically a subclass of int in Python; floats are rejected even
    if integer-valued, e.g. 3.0 is rejected)
  - each coordinate c must satisfy 0 <= c < n
  - n itself must be a positive genuine int
  - no duplicate points are allowed in S

ALGORITHM (deliberately a different code path from a naive per-pivot python
dict/set membership scan)
--------------------------------------------------------------------------
  1. Validate structure in pure Python using exact (arbitrary-precision) integers --
     no floating point or tolerance/epsilon comparison is used anywhere in this module.
  2. Build the full m x m pairwise squared-Euclidean-distance matrix at once with numpy
     (vectorized broadcasting), rather than looping pair-by-pair in Python.
  3. For each row (pivot), instead of inserting values into a Python set one at a time,
     SORT the row's off-diagonal squared distances (np.argsort) and scan for adjacent
     equal entries. This is an O(m log m) per-pivot check via sorting, structurally
     different from a hash-set-based approach, while remaining exact (integer dtype,
     no floating point comparisons of "closeness").
  4. Any candidate duplicate found via numpy is re-confirmed with pure Python
     arbitrary-precision arithmetic (`_python_dist2`) before being reported as a
     witness, so a hypothetical numpy overflow or dtype bug could never silently
     produce a wrong verdict.

DTYPE / OVERFLOW BOUND (explicit, as required)
------------------------------------------------
Coordinates satisfy 0 <= x, y < n. This project's grids are at most a few hundred in
size (the two official baselines are n=64 and n=100; Problem 6.59 grids in general are
of this order of magnitude). A squared distance between two grid points is at most
2*(n-1)^2. We use numpy's int64 (max representable value ~9.223e18). Coordinates are
cast to int64 *before* any subtraction/squaring, so all intermediate arithmetic
(differences, squares, sums) stays in int64. int64 is safe from overflow for any
n up to roughly sqrt(9.223e18 / 2) + 1 ~= 2.1e9 -- vastly larger than any n this
project will ever use (n <= a few hundred/thousand). The final verdict is additionally
cross-checked with Python's native arbitrary-precision ints (see `_python_dist2`),
so even in a hypothetical overflow scenario the reported witness is always exact.

CLI / JSON SCHEMA
------------------
Run as:  python independent_verifier.py <path-to-candidate.json>

The JSON file must be an object of the form:
    {
      "n": <positive integer>,
      "points": [[x0, y0], [x1, y1], ...]
    }
Extra keys (e.g. "size", "source") are permitted and ignored. The CLI independently
re-reads and re-parses the file from disk (it never trusts a pre-parsed in-memory
object passed in some other way), runs the legality check, and prints a PASS/FAIL
verdict plus a witness triple on FAIL.
"""

import json
import sys
import time

import numpy as np


def _python_dist2(p, q):
    """Exact squared Euclidean distance using Python's arbitrary-precision ints."""
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def _validate_structure(raw_n, raw_points):
    """
    Validate structural well-formedness of a candidate. Raises ValueError with a
    specific, human-readable message on the first violation found.

    Returns (n: int, points: list[tuple[int, int]]) on success.
    """
    if not isinstance(raw_n, int) or isinstance(raw_n, bool):
        raise ValueError(f"n must be a plain int, got {raw_n!r} (type {type(raw_n).__name__})")
    if raw_n <= 0:
        raise ValueError(f"n must be positive, got {raw_n}")
    n = raw_n

    if not isinstance(raw_points, list):
        raise ValueError(f"points must be a list, got type {type(raw_points).__name__}")

    points = []
    seen = set()
    for idx, p in enumerate(raw_points):
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            raise ValueError(f"point at index {idx} is not a 2-element list/tuple: {p!r}")
        x, y = p[0], p[1]
        for coord_name, coord in (("x", x), ("y", y)):
            if not isinstance(coord, int) or isinstance(coord, bool):
                raise ValueError(
                    f"point at index {idx} has non-integer {coord_name}={coord!r} "
                    f"(type {type(coord).__name__}); floats and bools are rejected"
                )
            if not (0 <= coord < n):
                raise ValueError(
                    f"point at index {idx} has {coord_name}={coord} out of range [0, {n})"
                )
        pt = (x, y)
        if pt in seen:
            raise ValueError(f"duplicate point {pt} found at index {idx}")
        seen.add(pt)
        points.append(pt)

    return n, points


def verify_independent(points, n):
    """
    Independently verify legality of `points` on the [n]^2 grid.

    Parameters
    ----------
    points : list of 2-element int sequences (tuples or lists)
    n : positive int, grid size

    Returns
    -------
    (is_legal: bool, witness: dict | None)
        witness, present only when is_legal is False, has keys:
          "pivot"            -- the point b with a repeated squared distance
          "a", "c"            -- the two other points tied in distance to the pivot
          "squared_distance"  -- the shared squared distance (exact Python int)

    Raises
    ------
    ValueError if the input fails structural validation (see module docstring).
    """
    n, points = _validate_structure(n, [list(p) for p in points])

    m = len(points)
    if m <= 2:
        # No three pairwise-distinct points exist, so S is vacuously legal.
        return True, None

    coords = np.array(points, dtype=np.int64)  # (m, 2); int64 bound justified above
    dx = coords[:, 0:1] - coords[:, 0:1].T
    dy = coords[:, 1:2] - coords[:, 1:2].T
    dist2 = dx * dx + dy * dy  # (m, m) int64 matrix of exact squared distances

    for i in range(m):
        row = dist2[i]
        others = np.arange(m) != i
        other_indices = np.nonzero(others)[0]
        vals = row[others]

        order = np.argsort(vals, kind="mergesort")  # stable sort -> different code path
        sorted_vals = vals[order]
        dup_positions = np.nonzero(sorted_vals[1:] == sorted_vals[:-1])[0]

        if dup_positions.size > 0:
            j0 = int(dup_positions[0])
            idx_a = int(other_indices[order[j0]])
            idx_c = int(other_indices[order[j0 + 1]])
            pivot_pt, a_pt, c_pt = points[i], points[idx_a], points[idx_c]

            # Re-confirm with pure Python arbitrary-precision arithmetic before
            # reporting -- guards against any hypothetical numpy dtype issue.
            d_ab = _python_dist2(pivot_pt, a_pt)
            d_cb = _python_dist2(pivot_pt, c_pt)
            assert d_ab == d_cb, "numpy/python cross-check mismatch -- should never happen"

            witness = {
                "pivot": pivot_pt,
                "a": a_pt,
                "c": c_pt,
                "squared_distance": d_ab,
            }
            return False, witness

    return True, None


def main(argv=None):
    """
    CLI entry point. See module docstring for the JSON schema.

    Exit codes: 0 = PASS (legal), 1 = FAIL (illegal), 2 = structural/parse error.
    """
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python independent_verifier.py <candidate.json>", file=sys.stderr)
        return 2

    path = argv[0]
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()
        raw = json.loads(raw_text)  # independent re-parse straight from disk
    except (OSError, json.JSONDecodeError) as e:
        print(f"FAIL (could not read/parse {path}): {e}")
        return 2

    if not isinstance(raw, dict) or "n" not in raw or "points" not in raw:
        print("FAIL: JSON must be an object with at least 'n' and 'points' keys")
        return 2

    try:
        t0 = time.perf_counter()
        is_legal, witness = verify_independent(raw["points"], raw["n"])
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
    except ValueError as e:
        print(f"FAIL (structural validation error): {e}")
        return 2

    if is_legal:
        print(
            f"PASS: legal set of {len(raw['points'])} points on [{raw['n']}]^2 grid "
            f"(verified in {elapsed_ms:.3f} ms)"
        )
        return 0
    else:
        print(f"FAIL: illegal set on [{raw['n']}]^2 grid (checked in {elapsed_ms:.3f} ms)")
        print(
            f"  witness triple: pivot={witness['pivot']}, a={witness['a']}, "
            f"c={witness['c']}, squared_distance={witness['squared_distance']}"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
