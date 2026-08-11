"""Only runs meaningfully under the project-local venv (`.venv_solver`) that has
ortools installed; skipped under the main/global interpreter used for the rest
of the test suite. Run explicitly with:
  .venv_solver/Scripts/python.exe -m pytest tests/test_cpsat_lazy.py -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

ortools = pytest.importorskip("ortools")

from src.search.cpsat_lazy import cpsat_lazy_maximize, cpsat_prove_upper_bound
from src.verification.oracle_verifier import is_legal_pivot_method


def test_cpsat_lazy_maximize_returns_legal_set():
    best, meta = cpsat_lazy_maximize(8, time_budget_s=15, per_round_time_limit_s=5, seed=1)
    ok, witness = is_legal_pivot_method(best, 8)
    assert ok, witness
    assert meta["best_legal_size"] == len(best)


def test_cpsat_prove_upper_bound_terminal_states_are_consistent():
    status, meta = cpsat_prove_upper_bound(6, target=8, time_budget_s=10, per_round_time_limit_s=3)
    assert status in ("INFEASIBLE_PROVEN", "FEASIBLE_FOUND", "INCONCLUSIVE")
    if status == "FEASIBLE_FOUND":
        pts = meta["points"]
        ok, witness = is_legal_pivot_method(pts, 6)
        assert ok, witness
        assert len(pts) >= 8


def test_cpsat_trivial_infeasible_target_beyond_grid_size():
    # target strictly greater than n^2 must be infeasible immediately (no cuts needed)
    status, meta = cpsat_prove_upper_bound(4, target=17, time_budget_s=5, per_round_time_limit_s=3)
    assert status == "INFEASIBLE_PROVEN"
