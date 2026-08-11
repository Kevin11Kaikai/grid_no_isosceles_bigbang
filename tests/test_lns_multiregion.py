import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.search.lns_multiregion import lns_multiregion_run
from src.verification.oracle_verifier import is_legal_pivot_method


def test_multiregion_returns_legal_nonshrinking_set():
    n = 10
    # NOTE: an earlier fixture [(0,0),(1,2),(2,4),(9,9)] was actually ILLEGAL
    # (pivot (1,2) has squared distance 5 to both (0,0) and (2,4)). Replaced
    # with a hand-verified-legal set (all four pairwise-pivot distance sets
    # checked distinct by hand).
    seed_points = [(0, 0), (1, 0), (0, 2), (9, 9)]
    ok, _ = is_legal_pivot_method(seed_points, n)
    assert ok

    best, meta = lns_multiregion_run(n, seed_points, time_budget_s=3, seed=1, k_regions=2)
    ok, witness = is_legal_pivot_method(best, n)
    assert ok, witness
    assert len(best) >= len(seed_points)
    assert meta["final_size"] == len(best)


def test_multiregion_k1_is_at_least_as_capable_as_single_region_case():
    n = 12
    # NOTE: an earlier fixture [(0,0),(0,5),(5,0),(11,11)] was actually ILLEGAL
    # (pivot (0,0) has squared distance 25 to both (0,5) and (5,0)). Replaced
    # with a hand-verified-legal set.
    seed_points = [(0, 0), (0, 5), (6, 0), (11, 11)]
    ok, _ = is_legal_pivot_method(seed_points, n)
    assert ok
    best, meta = lns_multiregion_run(n, seed_points, time_budget_s=3, seed=7, k_regions=1)
    ok, witness = is_legal_pivot_method(best, n)
    assert ok, witness
    assert len(best) >= len(seed_points)
