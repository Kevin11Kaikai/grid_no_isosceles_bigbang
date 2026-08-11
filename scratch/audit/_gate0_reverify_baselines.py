"""Gate 0 helper: re-verify baselines into scratch/audit (does not overwrite certified)."""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from data.baselines.official_raw import SOL_64, SOL_100
from src.structures.candidate_io import (
    load_candidate,
    save_candidate,
    sha256_of_points,
)
from src.verification.certify import certify_candidate
from src.verification.conflict_metric import conflict_count
from src.verification.oracle_verifier import (
    check_structural_validity,
    is_legal_pivot_method,
)
from src.verification_independent.independent_verifier import verify_independent


def audit(n: int, sol, cert_path: str) -> dict:
    pts = [tuple(p) for p in sol]
    expected = 112 if n == 64 else 164
    out = {
        "n": n,
        "source": f"data.baselines.official_raw.SOL_{n}",
        "size": len(pts),
        "size_ok": len(pts) == expected,
        "all_int": all(isinstance(x, int) and isinstance(y, int) for x, y in pts),
        "in_bounds": all(0 <= x < n and 0 <= y < n for x, y in pts),
        "no_duplicates": len(pts) == len(set(pts)),
    }
    check_structural_validity(pts, n)
    ok_a, w_a = is_legal_pivot_method(pts, n)
    ok_b, w_b = verify_independent(pts, n)
    out["verifier_A"] = {"pass": bool(ok_a), "witness": w_a}
    out["verifier_B"] = {"pass": bool(ok_b), "witness": w_b}
    out["V"] = conflict_count(pts, n)
    h = sha256_of_points(pts)
    out["hash_from_raw"] = h
    cert = load_candidate(cert_path)
    out["certified_hash"] = cert.get("hash_sha256")
    out["hash_matches_certified"] = h == cert.get("hash_sha256")
    out["certified_size"] = cert.get("size")

    os.makedirs("scratch/audit/certify_scratch", exist_ok=True)
    scratch_cand = f"scratch/audit/certify_scratch/n{n}_from_raw.json"
    save_candidate(scratch_cand, n, pts, "gate0_reverify_from_raw", None, None)
    cert_out = certify_candidate(scratch_cand, out_dir="scratch/audit/certify_scratch")
    out["certify_status"] = cert_out["status"]
    out["certify_hash"] = cert_out["hash_sha256"]
    out["commands"] = [
        f"python scratch/audit/_gate0_reverify_baselines.py  # n={n} from official_raw",
        "certify_candidate(..., out_dir='scratch/audit/certify_scratch')",
    ]
    out["gate0_ok"] = bool(
        out["size_ok"]
        and out["all_int"]
        and out["in_bounds"]
        and out["no_duplicates"]
        and ok_a
        and ok_b
        and out["V"] == 0
        and out["hash_matches_certified"]
        and cert_out["status"] == "DUAL_VERIFIED"
    )
    return out


def main() -> None:
    report = {
        "git_commit": None,
        "n64": audit(64, SOL_64, "results/certified/n64_k112_baseline_official.json"),
        "n100": audit(100, SOL_100, "results/certified/n100_k164_baseline_official.json"),
    }
    try:
        import subprocess

        report["git_commit"] = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        )
    except Exception as e:
        report["git_commit_error"] = str(e)
    report["both_ok"] = report["n64"]["gate0_ok"] and report["n100"]["gate0_ok"]
    os.makedirs("scratch/audit", exist_ok=True)
    path = "scratch/audit/phase0_baseline_reverify.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps({"both_ok": report["both_ok"], "wrote": path}, indent=2))
    print("n64_ok", report["n64"]["gate0_ok"], "hash", report["n64"]["hash_from_raw"])
    print("n100_ok", report["n100"]["gate0_ok"], "hash", report["n100"]["hash_from_raw"])


if __name__ == "__main__":
    main()
