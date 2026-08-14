"""Round 3 tournament judge / adversary harness.

Independent re-adjudication of every candidate produced by any Round 3 route.

Design stance (Section 9 + Section 10 of the campaign protocol): a route's own
report of its own result is not evidence. This harness re-loads every candidate
strictly from disk, ignores every self-reported status field, and re-derives the
verdict from the two independent verifiers plus a set of adversarial structural
checks that a route has no incentive to run against itself.

Adversarial checks performed here that a producing route typically does NOT:
  - size field vs actual point count (forged-size attack)      [via load_candidate]
  - duplicate points inside the set (inflates size silently)
  - coordinates outside [0, n-1] (set legal in a bigger grid, claimed for n)
  - claimed n vs the n implied by the coordinates
  - stored sha256 vs recomputed sha256 (candidate edited after hashing)
  - self-reported status vs re-derived verdict (status forgery / staleness)
  - THREE legality paths, not two, on sets small enough to afford the cubic one

Usage:
    python ROUND3_TOURNAMENT/judge.py [--root ROUND3_TOURNAMENT] [--json OUT]

Exit code is 0 if every candidate found is consistent, 1 if any candidate fails
verification or any adversarial check fires.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from typing import Any, Dict, List, Tuple

REPO_ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.verification import oracle_verifier as ov  # noqa: E402
from src.structures.candidate_io import (  # noqa: E402
    load_candidate,
    sha256_of_points,
)

sys.path.insert(0, os.path.join(REPO_ROOT, "src", "verification_independent"))
import independent_verifier as iv  # noqa: E402

# Records with these cardinalities are the bar. Strictly greater = breakthrough.
INCUMBENT = {64: 112, 100: 164}

# Cubic all-triples check is O(k^3); only affordable below this size.
BRUTEFORCE_MAX_SIZE = 60


def adjudicate(path: str) -> Dict[str, Any]:
    """Re-derive the verdict for one candidate file. Never trusts the file."""
    try:
        shown = os.path.relpath(path, REPO_ROOT)
    except ValueError:
        # different drive letter on Windows (e.g. fixtures under C:, repo on D:)
        shown = os.path.abspath(path)
    res: Dict[str, Any] = {
        "path": shown.replace("\\", "/"),
        "attacks_fired": [],
        "verdict": "UNKNOWN",
    }
    try:
        rec = load_candidate(path)
    except Exception as exc:  # includes the forged-size check
        res["verdict"] = "MALFORMED"
        res["error"] = f"{type(exc).__name__}: {exc}"
        res["attacks_fired"].append("load_candidate rejected the record")
        return res

    n = int(rec["n"])
    pts_raw = rec["points"]
    pts = [(int(p[0]), int(p[1])) for p in pts_raw]
    res["n"] = n
    res["claimed_size"] = int(rec["size"])
    res["actual_size"] = len(pts)
    res["self_reported_status"] = rec.get("status")
    res["search_method"] = rec.get("search_method")

    # --- adversarial structural attacks -------------------------------------
    if len(set(pts)) != len(pts):
        dupes = len(pts) - len(set(pts))
        res["attacks_fired"].append(f"{dupes} duplicate point(s) in the set")

    oob = [p for p in pts if not (0 <= p[0] < n and 0 <= p[1] < n)]
    if oob:
        res["attacks_fired"].append(
            f"{len(oob)} point(s) outside [0,{n-1}]^2, e.g. {oob[0]}"
        )

    if pts:
        implied = max(max(x, y) for x, y in pts) + 1
        res["implied_min_n"] = implied
        if implied > n:
            res["attacks_fired"].append(
                f"coordinates require n>={implied} but candidate claims n={n}"
            )

    recomputed = sha256_of_points(pts)
    res["sha256"] = recomputed
    stored = rec.get("sha256") or rec.get("candidate_hash") or rec.get("sha")
    if stored and stored != recomputed:
        res["attacks_fired"].append(
            f"stored sha {str(stored)[:12]}... != recomputed {recomputed[:12]}..."
        )

    # --- legality: three independent paths -----------------------------------
    try:
        ok_pivot, info_pivot = ov.verify(pts, n, method="pivot")
    except Exception as exc:
        ok_pivot, info_pivot = False, {"error": f"{type(exc).__name__}: {exc}"}
    res["oracle_pivot"] = bool(ok_pivot)
    if not ok_pivot:
        res["oracle_pivot_info"] = info_pivot

    try:
        # NOTE: verify_independent returns (is_legal, witness). Coercing the
        # tuple itself with bool() is always True and would silently rubber-stamp
        # an illegal candidate — unpack explicitly.
        ind_legal, ind_witness = iv.verify_independent(pts, n)
        ok_ind = bool(ind_legal)
        if not ok_ind and ind_witness:
            res["independent_witness"] = ind_witness
    except Exception as exc:
        ok_ind = False
        res["independent_error"] = f"{type(exc).__name__}: {exc}"
    res["independent"] = ok_ind

    if len(pts) <= BRUTEFORCE_MAX_SIZE:
        try:
            ok_bf, _ = ov.is_legal_bruteforce_triples(pts, n)
        except Exception as exc:
            ok_bf = False
            res["bruteforce_error"] = f"{type(exc).__name__}: {exc}"
        res["oracle_bruteforce_triples"] = bool(ok_bf)
    else:
        res["oracle_bruteforce_triples"] = None  # not affordable, not a failure

    paths = [res["oracle_pivot"], res["independent"]]
    if res["oracle_bruteforce_triples"] is not None:
        paths.append(res["oracle_bruteforce_triples"])

    if len(set(paths)) > 1:
        res["attacks_fired"].append(
            "VERIFIER DISAGREEMENT — this is a defect in the verification "
            "pipeline itself and outranks any search result"
        )
        res["verdict"] = "VERIFIER_DISAGREEMENT"
        return res

    legal = all(paths)
    res["legal"] = legal

    # --- status forgery / staleness ------------------------------------------
    claimed = (res["self_reported_status"] or "").upper()
    # "UNVERIFIED" contains the substring "VERIFIED"; exclude it explicitly.
    claims_verified = "VERIFIED" in claimed and "UNVERIFIED" not in claimed
    if claims_verified and not legal:
        res["attacks_fired"].append(
            f"self-reported status {claimed!r} but re-verification says ILLEGAL"
        )

    if not legal:
        res["verdict"] = "ILLEGAL"
        return res

    if res["attacks_fired"]:
        res["verdict"] = "LEGAL_BUT_FLAGGED"
    else:
        res["verdict"] = "DUAL_VERIFIED"

    bar = INCUMBENT.get(n)
    if bar is not None:
        res["incumbent"] = bar
        res["beats_incumbent"] = len(pts) > bar
        res["delta_vs_incumbent"] = len(pts) - bar
        res["ratio_size_over_n"] = round(len(pts) / n, 4)
    return res


def find_candidates(root: str) -> List[str]:
    out: List[str] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".json"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, "r", encoding="utf-8") as f:
                    head = json.load(f)
            except Exception:
                continue
            if isinstance(head, dict) and "points" in head and "n" in head:
                out.append(p)
    return sorted(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=os.path.join(REPO_ROOT, "ROUND3_TOURNAMENT"))
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args(argv)

    paths = find_candidates(args.root)
    if not paths:
        print(f"No candidate files found under {args.root}")
        return 0

    results = [adjudicate(p) for p in paths]

    print(f"{'verdict':<22} {'n':>5} {'|S|':>5} {'vs inc':>7}  path")
    print("-" * 100)
    for r in results:
        delta = r.get("delta_vs_incumbent")
        delta_s = f"{delta:+d}" if isinstance(delta, int) else "-"
        print(
            f"{r['verdict']:<22} {r.get('n','?'):>5} "
            f"{r.get('actual_size','?'):>5} {delta_s:>7}  {r['path']}"
        )
        for a in r["attacks_fired"]:
            print(f"    !! {a}")

    beaters = [r for r in results if r.get("beats_incumbent")]
    bad = [
        r
        for r in results
        if r["verdict"] not in ("DUAL_VERIFIED",) or r["attacks_fired"]
    ]

    print("-" * 100)
    print(f"candidates adjudicated : {len(results)}")
    print(f"clean dual-verified    : {sum(1 for r in results if r['verdict']=='DUAL_VERIFIED')}")
    print(f"flagged / failing      : {len(bad)}")
    if beaters:
        print()
        print("*** CANDIDATES BEATING AN INCUMBENT ***")
        for r in beaters:
            print(
                f"    n={r['n']} |S|={r['actual_size']} "
                f"(incumbent {r['incumbent']}, {r['delta_vs_incumbent']:+d}) "
                f"verdict={r['verdict']} sha={r['sha256'][:16]} {r['path']}"
            )
        print("    A beating candidate is NOT a record until an independent")
        print("    adversary has attacked it and the coordinates are published.")
    else:
        print("no candidate beats an incumbent (112 @ n=64, 164 @ n=100)")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nwrote {args.json_out}")

    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(2)
