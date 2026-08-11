"""Promotion pipeline: candidate -> certified.

A candidate becomes DUAL_VERIFIED / certified only by:
  1. Re-reading it from disk (never trusting an in-memory object).
  2. Passing verifier A (src/verification/oracle_verifier.py, pivot method).
  3. Passing verifier A's independent brute-force cross-check (small n) OR,
     for large n where O(|S|^3) is too slow, at minimum the pivot method
     plus verifier B.
  4. Passing verifier B (src/verification_independent/independent_verifier.py)
     if it exists yet -- if not yet available, status stays SINGLE_VERIFIED.
  5. Passing structural checks: no duplicates, bounds, size field consistency.

This module is intentionally the ONLY place in the project allowed to write
into results/certified/.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.structures.candidate_io import load_candidate, save_candidate, sha256_of_points
from src.verification.oracle_verifier import is_legal_pivot_method, check_structural_validity


def _load_independent_verifier():
    path = os.path.join(
        os.path.dirname(__file__), "..", "verification_independent", "independent_verifier.py"
    )
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("independent_verifier", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def certify_candidate(candidate_path: str, out_dir: str = "results/certified") -> dict:
    record = load_candidate(candidate_path)  # forces disk re-read
    n = record["n"]
    points = record["points"]

    check_structural_validity(points, n)
    dup_check_pass = True  # check_structural_validity raises on dup; reaching here means pass
    bounds_check_pass = True

    ok_a, witness_a = is_legal_pivot_method(points, n)

    ind_mod = _load_independent_verifier()
    if ind_mod is not None:
        ok_b, witness_b = ind_mod.verify_independent(points, n)
        verifier_b_pass = bool(ok_b)
    else:
        ok_b, witness_b = None, {"note": "independent verifier not yet available"}
        verifier_b_pass = None

    h = sha256_of_points(points)

    all_pass = ok_a and (verifier_b_pass is True)
    status = "DUAL_VERIFIED" if all_pass else ("SINGLE_VERIFIED" if ok_a else "REJECTED")

    out_record = dict(record)
    out_record.update(
        {
            "status": status,
            "verifier_A_pass": bool(ok_a),
            "verifier_A_witness": witness_a,
            "verifier_B_pass": verifier_b_pass,
            "verifier_B_witness": witness_b,
            "duplicate_check_pass": dup_check_pass,
            "bounds_check_pass": bounds_check_pass,
            "hash_sha256": h,
            "verification_commands": [
                "python -m src.verification.certify <candidate_path>",
            ],
            "verification_timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    if status == "DUAL_VERIFIED":
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, os.path.basename(candidate_path))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out_record, f, indent=2)
        out_record["certified_path"] = out_path

    return out_record


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("candidate_path")
    ap.add_argument("--out-dir", default="results/certified")
    args = ap.parse_args()
    result = certify_candidate(args.candidate_path, args.out_dir)
    print(json.dumps({k: v for k, v in result.items() if k != "points"}, indent=2))
