"""Conflict metric V(S) for Problem 6.59 — Main Agent owned helper.

Owned by Main / Gate 0. Search agents may import and call; they must not modify.

Definition (exact integer arithmetic):
  V(S) = sum_{b in S} sum_d binom(m_{b,d}, 2)
  where m_{b,d} = #{p in S \\ {b} : ||p-b||_2^2 = d}.

Equivalence claim (audited by tests/test_conflict_metric_equivalence.py):
  V(S) == 0  iff  S is legal under the project pivot-distance definition
  (same proposition implemented by verifier A and verifier B).

Structural invalid inputs (duplicates, out-of-bounds, non-ints) raise
ConflictMetricError — they are not assigned a V value, matching the
verifiers' ValidationError / structural-fail behavior.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence, Tuple

Point = Tuple[int, int]


class ConflictMetricError(ValueError):
    """Structural invalidity: duplicates, bounds, or non-integer coordinates."""


def _sq_dist(a: Point, b: Point) -> int:
    dx = int(a[0]) - int(b[0])
    dy = int(a[1]) - int(b[1])
    return dx * dx + dy * dy


def _validate_structure(points: Sequence[Sequence[int]], n: int) -> List[Point]:
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ConflictMetricError(f"n must be a positive int, got {n!r}")
    if not isinstance(points, (list, tuple)):
        raise ConflictMetricError(f"points must be a list/tuple, got {type(points)}")
    seen = set()
    out: List[Point] = []
    for i, p in enumerate(points):
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            raise ConflictMetricError(f"point index {i}: expected a 2-tuple, got {p!r}")
        x, y = p
        for name, c in (("x", x), ("y", y)):
            if isinstance(c, bool) or not isinstance(c, int):
                raise ConflictMetricError(
                    f"point index {i}: {name}={c!r} is not an int"
                )
            if not (0 <= c < n):
                raise ConflictMetricError(
                    f"point index {i}: {name}={c} out of range [0, {n - 1}]"
                )
        key = (int(x), int(y))
        if key in seen:
            raise ConflictMetricError(f"duplicate point {key} at index {i}")
        seen.add(key)
        out.append(key)
    return out


def conflict_count(points: Sequence[Sequence[int]], n: int) -> int:
    """Return V(S). Raises ConflictMetricError on structural invalidity."""
    pts = _validate_structure(points, n)
    total = 0
    for bi, b in enumerate(pts):
        counts: Counter = Counter()
        for ai, a in enumerate(pts):
            if ai == bi:
                continue
            counts[_sq_dist(a, b)] += 1
        for m in counts.values():
            if m >= 2:
                total += m * (m - 1) // 2
    return total


def conflict_witnesses(points: Sequence[Sequence[int]], n: int) -> List[dict]:
    """Enumerate one witness triple per repeated (pivot, d2) pair (debug only)."""
    pts = _validate_structure(points, n)
    witnesses: List[dict] = []
    for bi, b in enumerate(pts):
        first_at_d2: Dict[int, Point] = {}
        for ai, a in enumerate(pts):
            if ai == bi:
                continue
            d2 = _sq_dist(a, b)
            if d2 in first_at_d2:
                witnesses.append(
                    {
                        "pivot": b,
                        "point_1": first_at_d2[d2],
                        "point_2": a,
                        "squared_distance": d2,
                    }
                )
            else:
                first_at_d2[d2] = a
    return witnesses
