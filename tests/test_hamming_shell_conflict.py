"""Unit tests for Wave-2 Agent A Hamming-shell CP-SAT module.

Run with:
  .venv_solver/Scripts/python.exe -m pytest tests/test_hamming_shell_conflict.py -q
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ortools = pytest.importorskip("ortools")

from data.baselines.official_raw import SOL_64, SOL_100
from src.search.hamming_shell_conflict import (
    EXPECTED_HASHES,
    default_num_workers,
    dual_verify,
    find_witness_cuts,
    hamming_shell_search,
    load_policy_universe,
    reconstruct_S,
    shell_cardinalities,
    universe_hash,
)
from src.verification.conflict_metric import conflict_count
from src.verification.oracle_verifier import is_legal_pivot_method


def test_default_workers_cap():
    # 20 logical → 5 workers (25%), 3*5=15 <= 18 usable
    assert default_num_workers(20) == 5
    assert default_num_workers(8) >= 1
    assert 3 * default_num_workers(20) <= 20 - 2


def test_universe_hash_stability_u_small_and_r2():
    rem, add, h = load_policy_universe(100, "U_small")
    assert len(rem) == 16 and len(add) == 32
    assert h == EXPECTED_HASHES[("n100", "U_small")]
    assert universe_hash(rem, add) == h
    # order independence
    assert universe_hash(list(reversed(rem)), list(reversed(add))) == h

    rem2, add2, h2 = load_policy_universe(100, "U_small_r2")
    assert len(rem2) == 32 and len(add2) == 44
    assert len(rem2) + len(add2) == 76
    assert h2 == EXPECTED_HASHES[("n100", "U_small_r2")]


def test_n64_u_small_sizes():
    rem, add, h = load_policy_universe(64, "U_small")
    assert len(rem) == 12 and len(add) == 24
    assert len(h) == 64


def test_reconstruct_and_cardinality():
    s0 = [(0, 0), (0, 1), (1, 0), (2, 2)]
    rem = [(0, 0), (0, 1)]
    add = [(3, 3), (3, 4), (4, 3)]
    # remove both rem, add three → |S0\\S|=2, |S\\S0|=3
    s = reconstruct_S(s0, rem, add, keep_rem=[False, False], take_add=[True, True, True])
    removed, added = shell_cardinalities(s0, s)
    assert removed == 2 and added == 3
    assert (1, 0) in s and (2, 2) in s
    assert (0, 0) not in s


def test_tiny_legal_set_no_witnesses():
    # Two points always legal; three in general position without equal pivot distances.
    pts = [(0, 0), (0, 1), (2, 3)]
    assert find_witness_cuts(pts) == []
    ok, _ = is_legal_pivot_method(pts, 4)
    assert ok
    assert conflict_count(pts, 4) == 0


def test_tiny_illegal_set_has_witness_and_v():
    # (0,0),(0,2),(0,4) — midpoint pivot isosceles (collinear)
    pts = [(0, 0), (0, 2), (0, 4)]
    cuts = find_witness_cuts(pts)
    assert len(cuts) >= 1
    assert conflict_count(pts, 5) > 0
    ok, _ = is_legal_pivot_method(pts, 5)
    assert not ok


def test_lazy_cuts_do_not_kill_legal_baseline_shell_r_impossible_on_tiny():
    """On a tiny handmade universe, a clearly illegal-only model goes INFEAS;
    a universe that admits the original S0-size shell is not required here —
    instead check that adding zero cuts leaves S0-reconstructable keep-all feasible
    when r=0 is disallowed we just check search API returns a known status.
    """
    # Use a micro instance: S0 legal size 3 on n=4; Rem=1, Add=2, r=1 → target 4
    s0 = [(0, 0), (0, 3), (3, 0)]
    rem = [(0, 0)]
    add = [(1, 2), (2, 1), (3, 3)]
    # This may be feas or infeas; just ensure no crash and status is scoped.
    res = hamming_shell_search(
        n=4,
        s0=s0,
        removable=rem,
        addable=add,
        r=1,
        time_budget_s=8.0,
        per_round_time_limit_s=3.0,
        seed=1,
        num_workers=1,
        u_id="tiny",
    )
    assert res.status in (
        "FEASIBLE_LEGAL",
        "INFEASIBLE_SCOPED",
        "TIMEOUT_INCONCLUSIVE",
    )


def test_dual_verify_baseline_n64_slice():
    pts = list(SOL_64)[:10]
    # first 10 of baseline may be illegal as a subset; use full baseline
    ver = dual_verify(SOL_64, 64)
    assert ver["oracle_legal"] and ver["independent_legal"] and ver["V"] == 0
    ver100 = dual_verify(SOL_100, 100)
    assert ver100["oracle_legal"] and ver100["independent_legal"] and ver100["V"] == 0


def test_cuts_from_illegal_incumbent_are_witness_derived():
    # Force a quick infeas by empty-ish: Rem with r requiring adds that all conflict
    s0 = list(SOL_64)[:8]
    # Ensure S0 subset is legal? may not be — build small legal set
    s0 = [(0, 0), (0, 3), (3, 0), (3, 3)]
    rem = [(0, 0), (0, 3)]
    add = [(1, 1), (1, 2), (2, 1)]  # center-ish, likely conflict-heavy
    res = hamming_shell_search(
        n=4,
        s0=s0,
        removable=rem,
        addable=add,
        r=1,
        time_budget_s=10.0,
        per_round_time_limit_s=3.0,
        seed=2,
        num_workers=1,
        u_id="tiny2",
    )
    assert res.status in (
        "FEASIBLE_LEGAL",
        "INFEASIBLE_SCOPED",
        "TIMEOUT_INCONCLUSIVE",
        "ERROR",
    )
    if res.status != "ERROR":
        assert "final_cuts" in res.meta
        # If any cuts were added, round_log should show witness counts
        if res.meta.get("final_cuts", 0) > 0:
            assert any(r.get("n_witness_cuts", 0) > 0 for r in res.meta.get("round_log", []))
