"""Validate the MILP-based exact_repair_region against brute-force enumeration on
tiny synthetic instances, to catch any bug in the constraint derivation itself
(distinct from the "does search improve on baseline" question tested elsewhere).
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.search.lns_exact_repair import exact_repair_region
from src.verification.oracle_verifier import is_legal_pivot_method


def _brute_force_best_repair(n, fixed_points, region_candidates):
    """Try every subset of region_candidates, return the largest one such that
    fixed_points | subset is legal. O(2^|region_candidates|) -- only for tiny cases.
    """
    best = []
    for r in range(len(region_candidates), -1, -1):
        found = None
        for combo in itertools.combinations(region_candidates, r):
            trial = list(fixed_points) + list(combo)
            ok, _ = is_legal_pivot_method(trial, n)
            if ok:
                found = list(combo)
                break
        if found is not None:
            best = found
            break
    return best


def test_synthetic_case_1_small_region_matches_brute_force():
    n = 8
    fixed = {(0, 0), (7, 7)}  # legal pair (only 2 points, trivially legal)
    region_candidates = [(1, 0), (0, 1), (2, 0), (0, 2), (1, 1)]

    ok, _ = is_legal_pivot_method(list(fixed), n)
    assert ok

    selected, meta = exact_repair_region(n, fixed, region_candidates, time_limit_s=5.0)
    trial = list(fixed) + list(selected)
    ok, witness = is_legal_pivot_method(trial, n)
    assert ok, f"MILP result itself illegal! witness={witness}"

    brute_best = _brute_force_best_repair(n, fixed, region_candidates)
    assert len(selected) == len(brute_best), (
        f"MILP found {len(selected)} points {selected}, brute force optimum is "
        f"{len(brute_best)} points {brute_best} -- MILP encoding is suboptimal or buggy"
    )


def test_synthetic_case_2_region_with_forced_exclusions():
    n = 6
    # Fixed set hand-checked legal: pairwise sq-distances (0,0)-(4,0)=16,
    # (0,0)-(0,3)=9, (4,0)-(0,3)=25 -- all distinct per pivot, so no isosceles triple.
    fixed = {(0, 0), (4, 0), (0, 3)}
    ok, witness = is_legal_pivot_method(list(fixed), n)
    assert ok, f"fixture fixed set itself illegal: {witness}"

    region_candidates = [(1, 1), (2, 2), (3, 3), (1, 0), (0, 1), (2, 0), (0, 2)]

    selected, meta = exact_repair_region(n, fixed, region_candidates, time_limit_s=5.0)
    trial = list(fixed) + list(selected)
    ok, witness = is_legal_pivot_method(trial, n)
    assert ok, f"MILP result itself illegal! witness={witness}"

    brute_best = _brute_force_best_repair(n, fixed, region_candidates)
    assert len(selected) == len(brute_best), (
        f"MILP found {len(selected)}, brute force optimum is {len(brute_best)} "
        f"({brute_best}) -- MILP encoding is suboptimal or buggy"
    )


def test_prefilter_removes_individually_conflicting_candidates():
    n = 5
    # (0,0) and (2,0) both fixed at distance^2=4 from (1,0)... so (1,0) as a
    # candidate would become an apex with two equal-distance fixed arms? Let's
    # construct directly: fixed = {(0,0)}. Candidate (2,0) individually is fine
    # alone, but with another candidate (4,0) sharing distance 4 from (0,0)... test
    # that at least one of a conflicting candidate pair is excluded.
    fixed = {(0, 0)}
    region_candidates = [(2, 0), (0, 2)]  # both at squared distance 4 from (0,0)
    # If both selected: pivot (0,0), arms (2,0) and (0,2), both distance^2=4 -> illegal.
    selected, meta = exact_repair_region(n, fixed, region_candidates, time_limit_s=5.0)
    assert len(selected) <= 1, f"MILP allowed an illegal pair through: {selected}"
    trial = list(fixed) + list(selected)
    ok, witness = is_legal_pivot_method(trial, n)
    assert ok, f"witness={witness}"


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
