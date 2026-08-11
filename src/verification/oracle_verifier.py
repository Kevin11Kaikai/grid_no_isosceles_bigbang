"""Primary oracle verifier for Problem 6.59 (isosceles-triangle-free grid subsets).

Design goal: obviously correct, not fast. This is the reference implementation
against which every other verifier, incremental cache, and search heuristic is
cross-checked. It uses exact Python arbitrary-precision integers throughout --
no floating point distances are ever computed for a legality decision.

Definition (must match exactly):
  Given S subset of [n]^2 = {0,...,n-1}^2, S is LEGAL iff for every three
  DISTINCT points a, b, c in S, it is NOT the case that |a-b| = |b-c|
  (squared distances compared as integers). This includes the degenerate
  case of three distinct collinear equally-spaced points (b is the midpoint
  of segment a-c), which is a real isosceles triangle with apex b (a
  "triangle" of zero area is still covered by the "at least two of the three
  pairwise distances are equal" reading used in the source paper).

  Equivalently: for every point b in S, the multiset of squared distances
  from b to every OTHER point in S must have no repeated value.

  IMPORTANT: this is a per-pivot uniqueness condition, not a global
  all-pairs-distinct condition. Two disjoint pairs of points are allowed to
  share a squared distance, as long as they do not share an endpoint that
  would make one of them a repeated distance from a common pivot.
"""

from __future__ import annotations

import itertools
from typing import Iterable, List, Sequence, Tuple

Point = Tuple[int, int]


class ValidationError(ValueError):
    """Raised for structurally invalid input (not a legality verdict)."""


def _sq_dist(a: Point, b: Point) -> int:
    dx = int(a[0]) - int(b[0])
    dy = int(a[1]) - int(b[1])
    return dx * dx + dy * dy


def check_structural_validity(points: Sequence[Point], n: int) -> None:
    """Raises ValidationError if the input is not even a well-formed candidate.

    This is deliberately separate from isosceles-legality: a structurally
    invalid input (duplicate point, out-of-range coordinate, non-integer,
    wrong arity) must never silently be "corrected" -- it must be rejected.
    """
    if not isinstance(points, (list, tuple)):
        raise ValidationError(f"points must be a list/tuple, got {type(points)}")
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValidationError(f"n must be a positive int, got {n!r}")

    seen = set()
    for i, p in enumerate(points):
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            raise ValidationError(f"point index {i}: expected a 2-tuple, got {p!r}")
        x, y = p
        for coord_name, c in (("x", x), ("y", y)):
            if isinstance(c, bool) or not isinstance(c, int):
                raise ValidationError(
                    f"point index {i}: coordinate {coord_name}={c!r} is not an int "
                    f"(floats / bools are rejected -- exact integer grid points only)"
                )
            if not (0 <= c < n):
                raise ValidationError(
                    f"point index {i}: coordinate {coord_name}={c} out of range [0, {n - 1}]"
                )
        key = (int(x), int(y))
        if key in seen:
            raise ValidationError(f"duplicate point {key} at index {i}")
        seen.add(key)


def is_legal_pivot_method(points: Sequence[Point], n: int) -> Tuple[bool, dict]:
    """Reference oracle: pivot-distance-uniqueness check.

    For each point b in `points`, compute squared distances to every other
    point. If any value repeats, a forbidden (possibly degenerate) isosceles
    configuration with apex b exists.

    Returns (is_legal, witness) where witness is {} if legal, else contains
    the offending pivot and the two "base" points forming the equal-distance
    pair, plus the shared squared distance.
    """
    check_structural_validity(points, n)
    pts = [(int(x), int(y)) for x, y in points]

    for bi, b in enumerate(pts):
        seen_d2 = {}
        for ai, a in enumerate(pts):
            if ai == bi:
                continue
            d2 = _sq_dist(a, b)
            if d2 in seen_d2:
                return False, {
                    "pivot": b,
                    "point_1": seen_d2[d2],
                    "point_2": a,
                    "squared_distance": d2,
                }
            seen_d2[d2] = a
    return True, {}


def is_legal_bruteforce_triples(points: Sequence[Point], n: int) -> Tuple[bool, dict]:
    """Independent-logic cross-check: literal triple enumeration.

    For every ordered choice of 3 distinct points (a, b, c) -- i.e. every way
    to designate one of the three as the candidate apex b -- reject if
    d^2(a,b) == d^2(b,c). This is algorithmically distinct from the pivot
    method above (it does not build a per-pivot dict; it is the direct
    translation of "no three distinct points form an isosceles triangle,
    including degenerate/collinear ones") and is intentionally O(|S|^3) to
    stay maximally simple and auditable. Used only for fuzz cross-checking
    on small sets -- NOT for large-scale certification (too slow).
    """
    check_structural_validity(points, n)
    pts = [(int(x), int(y)) for x, y in points]
    m = len(pts)
    for bi in range(m):
        b = pts[bi]
        for ai in range(m):
            if ai == bi:
                continue
            a = pts[ai]
            d_ab = _sq_dist(a, b)
            for ci in range(m):
                if ci == bi or ci == ai:
                    continue
                c = pts[ci]
                if _sq_dist(b, c) == d_ab:
                    return False, {
                        "pivot": b,
                        "point_1": a,
                        "point_2": c,
                        "squared_distance": d_ab,
                    }
    return True, {}


def verify(points: Sequence[Point], n: int, method: str = "pivot") -> Tuple[bool, dict]:
    if method == "pivot":
        return is_legal_pivot_method(points, n)
    elif method == "bruteforce":
        return is_legal_bruteforce_triples(points, n)
    else:
        raise ValueError(f"unknown method {method!r}")


def full_cross_check(points: Sequence[Point], n: int) -> bool:
    """Runs both algorithms and raises AssertionError if they disagree.

    Only intended for small |S| (bruteforce is O(|S|^3)).
    """
    r1, w1 = is_legal_pivot_method(points, n)
    r2, w2 = is_legal_bruteforce_triples(points, n)
    if r1 != r2:
        raise AssertionError(
            f"VERIFIER DISAGREEMENT: pivot={r1} (witness {w1}) vs "
            f"bruteforce={r2} (witness {w2}) on points={points}, n={n}"
        )
    return r1
