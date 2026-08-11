import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.search.symmetry_guided import reflect, symmetric_build_once, symmetric_multistart
from src.verification.oracle_verifier import is_legal_pivot_method


def test_reflect_is_involution():
    n = 20
    for p in [(0, 0), (5, 3), (19, 19), (0, 19)]:
        assert reflect(reflect(p, n), n) == p


def test_reflect_never_fixed_point_for_even_n():
    n = 20
    for x in range(0, n, 3):
        for y in range(0, n, 3):
            assert reflect((x, y), n) != (x, y)


def test_symmetric_build_once_legal_and_no_lone_broken_pair_at_break_prob_zero():
    n = 16
    pts, meta = symmetric_build_once(n, seed=3, break_prob=0.0, order="random")
    ok, witness = is_legal_pivot_method(pts, n)
    assert ok, witness
    # break_prob=0 => every accepted point's reflection should also be present
    pset = set(pts)
    for p in pts:
        assert reflect(p, n) in pset, f"{p} placed without its reflection at break_prob=0"


def test_symmetric_multistart_returns_legal_best():
    n = 14
    best, meta = symmetric_multistart(n, time_budget_s=3, seed=1)
    ok, witness = is_legal_pivot_method(best, n)
    assert ok, witness
    assert meta["final_size"] == len(best)
    assert meta["trials"] > 0
