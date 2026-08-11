import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.search.sa_exact_repair import sa_exact_repair_run
from src.verification.oracle_verifier import is_legal_pivot_method


def test_sa_returns_legal_set_and_never_shrinks_below_initial():
    n = 12
    from data.baselines.official_raw import SOL_64

    init = [p for p in SOL_64 if p[0] < n and p[1] < n]
    # trim to a legal subset for a smaller synthetic grid
    legal_init = []
    for p in init:
        trial = legal_init + [p]
        ok, _ = is_legal_pivot_method(trial, n)
        if ok:
            legal_init = trial
    assert len(legal_init) >= 3

    best, meta = sa_exact_repair_run(n, legal_init, time_budget_s=3, seed=1)
    ok, witness = is_legal_pivot_method(best, n)
    assert ok, witness
    assert len(best) >= len(legal_init)
    assert meta["final_size"] == len(best)


def test_sa_final_state_matches_returned_points():
    n = 10
    # NOTE: an earlier version of this fixture, [(0,0),(1,2),(2,4)], was actually
    # ILLEGAL (pivot (1,2) has squared distance 5 to both (0,0) and (2,4)) --
    # same class of test-fixture bug caught repeatedly in Round 1. Replaced with
    # a hand-verified-legal set: pivot (0,0) sees d^2=1,4; pivot (1,0) sees
    # d^2=1,5; pivot (0,2) sees d^2=4,5 -- all distinct.
    seed_points = [(0, 0), (1, 0), (0, 2)]
    ok, _ = is_legal_pivot_method(seed_points, n)
    assert ok
    best, meta = sa_exact_repair_run(n, seed_points, time_budget_s=2, seed=42)
    ok, witness = is_legal_pivot_method(best, n)
    assert ok, witness
    assert len(best) >= len(seed_points)
