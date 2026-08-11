"""Candidate serialization: the single canonical JSON schema for this project.

Schema (see section 11 of the project brief):
{
  "problem": "grid_no_isosceles",
  "n": int,
  "size": int,                       # must equal len(points); checked on load
  "coordinate_convention": "0_to_n_minus_1",
  "points": [[x, y], ...],
  "search_method": str,
  "seed": int or null,
  "timestamp_utc": iso8601 str,
  "source_commit": str or null,
  "parent_candidate": str or null,   # filename of parent, or null
  "status": "UNVERIFIED" | "SINGLE_VERIFIED" | "DUAL_VERIFIED" | "REJECTED",
}

Certified candidates additionally carry:
  verifier_A_pass, verifier_B_pass, duplicate_check_pass, bounds_check_pass,
  hash (sha256 of the canonical points list), verification_commands,
  verification_timestamp.

All read paths here re-parse from disk; no code path is allowed to certify
an in-memory object without a save+reload round trip (Attack 4 in the
project brief: serialization attack).
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

Point = Tuple[int, int]


def canonical_points_string(points: Sequence[Sequence[int]]) -> str:
    """Deterministic string form used for hashing: sorted, fixed formatting.

    Sorting removes any dependence on insertion/serialization order so the
    hash is a function of the SET of points, not the list order.
    """
    pts = sorted((int(p[0]), int(p[1])) for p in points)
    return json.dumps(pts, separators=(",", ":"))


def sha256_of_points(points: Sequence[Sequence[int]]) -> str:
    s = canonical_points_string(points)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def save_candidate(
    path: str,
    n: int,
    points: Sequence[Sequence[int]],
    search_method: str,
    seed: Optional[int],
    parent_candidate: Optional[str],
    status: str = "UNVERIFIED",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    pts = [[int(x), int(y)] for x, y in points]
    record = {
        "problem": "grid_no_isosceles",
        "n": int(n),
        "size": len(pts),
        "coordinate_convention": "0_to_n_minus_1",
        "points": pts,
        "search_method": search_method,
        "seed": seed,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": None,
        "parent_candidate": parent_candidate,
        "status": status,
    }
    if extra:
        record.update(extra)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    return record


def load_candidate(path: str) -> Dict[str, Any]:
    """Reload a candidate strictly from disk (never trust a cached object)."""
    with open(path, "r", encoding="utf-8") as f:
        record = json.load(f)
    if "points" not in record or "size" not in record or "n" not in record:
        raise ValueError(f"{path}: missing required fields")
    if record["size"] != len(record["points"]):
        raise ValueError(
            f"{path}: size field {record['size']} != actual point count "
            f"{len(record['points'])} (Attack: size field forged)"
        )
    return record
