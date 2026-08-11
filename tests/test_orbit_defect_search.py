"""Tests for Agent B orbit/core/defect search.

Run with solver venv for CP-SAT tests::

    .venv_solver/Scripts/python.exe -m pytest tests/test_orbit_defect_search.py -q
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.search.orbit_defect_search import (
    TARGETS,
    account_defects,
    baseline_points,
    cardinality_status_for_type,
    enumerate_orbits,
    find_violation_triples,
    full_orbit_size_multiset,
    get_symmetric_partners,
    offsets_for,
    solve_orbit_defect,
    SearchConfig,
)
from src.verification.oracle_verifier import is_legal_pivot_method

ortools = pytest.importorskip("ortools")

ROOT = Path(__file__).resolve().parents[1]
GATE1 = ROOT / "scratch" / "audit" / "agent_b" / "orbit_parity_reachability.json"


def test_offsets_match_notebook_formulas():
    for n in (64, 100):
        assert offsets_for(n) == [
            (n - 1, n - 1),
            (n - 2, n - 2),
            (n, n),
            (n, n - 1),
            (n - 2, n - 1),
            (n - 1, n),
            (n - 1, n - 2),
        ]


def test_partners_type0_central():
    n = 64
    p = (1, 2)
    partners = get_symmetric_partners(p, n, 0)
    # offset (63,63): rx=(62,2), ry=(1,61), rxy=(62,61)
    assert partners == {(62, 2), (1, 61), (62, 61)}


def test_partners_type1_oog_dropped():
    n = 64
    # x=63 → sym_x = 62-63 = -1 OOG
    p = (63, 10)
    partners = get_symmetric_partners(p, n, 1)
    # ry=(63, 52), rxy OOG or partial
    assert (63, 52) in partners
    assert all(0 <= x < n and 0 <= y < n for x, y in partners)


def test_enumerate_coverage_and_type0_sizes():
    for n in (8, 16):
        orbits = enumerate_orbits(n, 0)
        assert sum(o.size for o in orbits) == n * n
        assert all(o.is_full and o.size == 4 for o in orbits)


def test_cardinality_matches_gate1_table():
    assert GATE1.exists(), "Gate1 orbit_parity_reachability.json required"
    gate = json.loads(GATE1.read_text(encoding="utf-8"))
    for n, key in ((64, "n64"), (100, "n100")):
        for t in range(7):
            ours = cardinality_status_for_type(n, t)
            ref = gate[key][str(t)]
            assert ours["reachable"] == ref["cardinality_reachability"]["reachable"]
            assert ours["full_orbit_size_multiset"] == ref["full_orbit_size_multiset"]
            assert (
                ours["defects_required_for_cardinality"]
                == ref["defects_required_for_cardinality"]
            )


def test_baseline_defect_accounting_n100_type0():
    n = 100
    pts = baseline_points(n)
    acc = account_defects(pts, n, 0)
    # Gate1: fully symmetric Type0 core 164/164, 0 defects
    assert acc["core_size"] == 164
    assert acc["n_defect_points"] == 0
    assert acc["size_check"]


def test_baseline_defect_accounting_n64_type0_has_partials():
    n = 64
    pts = baseline_points(n)
    acc = account_defects(pts, n, 0)
    # Gate1: FULL core 108, 2 partial orbits (4 present / 4 missing) → 4 defects-ish
    assert acc["core_size"] == 108
    assert acc["n_defect_points"] == 4
    assert acc["n_partial_orbits"] == 2


def test_verifier_on_baseline_candidates():
    for n, pts in ((64, baseline_points(64)), (100, baseline_points(100))):
        ok, wit = is_legal_pivot_method(pts, n)
        assert ok, wit


def test_lazy_cuts_valid_on_illegal_triple():
    # Three points forming isosceles at pivot (0,0): (1,0) and (0,1) same dist? 
    # Better: (0,0), (2,0), (0,2) — equidistant from (0,0) with d2=4
    pts = [(0, 0), (2, 0), (0, 2)]
    triples = find_violation_triples(pts)
    assert any(t[0] == (0, 0) for t in triples)
    ok, _ = is_legal_pivot_method(pts, 8)
    assert not ok


def test_pure_mode_skipped_for_type0():
    cfg = SearchConfig(
        n=64,
        symmetry_type=0,
        mode="pure",
        target_size=113,
        time_budget_s=5,
        seed=1,
        num_workers=2,
    )
    result = solve_orbit_defect(cfg)
    assert result["solver_status"] == "SKIPPED_CARDINALITY_UNREACHABLE"


def test_short_defect_solve_returns_scoped_status():
    cfg = SearchConfig(
        n=64,
        symmetry_type=0,
        mode="defect",
        target_size=113,
        defect_budget_min=1,
        defect_budget_max=5,
        time_budget_s=20,
        per_round_time_limit_s=8,
        seed=2,
        num_workers=2,
        max_extra_orbits=30,
        max_defect_pool=40,
        halo_radius=5,
    )
    result = solve_orbit_defect(cfg)
    assert result["solver_status"] in (
        "FEASIBLE",
        "OPTIMAL",
        "INFEASIBLE",
        "TIMEOUT",
    )
    assert result["solver_status"] != "INFEASIBLE" or "infeasible_record" in result
    if result["solver_status"] == "INFEASIBLE":
        rec = result["infeasible_record"]
        for k in (
            "n",
            "axis",
            "mode",
            "defect_budget",
            "core_def",
            "universe",
            "time_s",
            "status",
            "model_hash",
        ):
            assert k in rec
    if result["points"]:
        ok, wit = is_legal_pivot_method(
            [tuple(p) for p in result["points"]], 64
        )
        assert ok, wit
        assert result["size"] == TARGETS[64]


def test_type1_pure_cardinality_reachable_flag():
    st = cardinality_status_for_type(64, 1)
    assert st["reachable"] is True
    assert st["full_orbit_size_multiset"].get("1") == 1
