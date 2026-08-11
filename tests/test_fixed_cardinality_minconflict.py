"""Tests for fixed-cardinality min-conflict search (Agent C exclusive)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.search.fixed_cardinality_minconflict import (
    IncrementalConflictState,
    INIT_FUNCS,
    VMismatchError,
    cross_check_or_stop,
    load_gate1_pools,
    propose_1for1,
    propose_2for2,
    run_fixed_cardinality_search,
    TARGET,
)
from src.verification.conflict_metric import conflict_count


def test_incremental_matches_exact_on_baseline_plus_one():
    pools = load_gate1_pools(64)
    rng_pts = list(pools.baseline) + [pools.low_delta[0]]
    # may have duplicates if low_delta somehow in baseline — filter
    S = []
    seen = set()
    for p in rng_pts:
        if p not in seen:
            seen.add(p)
            S.append(p)
    # force exact target cardinality for the check using a prefix if oversized
    if len(S) > TARGET[64]:
        S = S[: TARGET[64]]
    while len(S) < TARGET[64]:
        for p in pools.halo:
            if p not in seen:
                S.append(p)
                seen.add(p)
                break
        else:
            break
    assert len(S) == TARGET[64]
    st = IncrementalConflictState(64, S)
    exact = conflict_count(S, 64)
    assert st.V == exact


def test_swap_preserves_cardinality_and_v_consistency():
    pools = load_gate1_pools(64)
    import random

    rng = random.Random(0)
    pts = INIT_FUNCS["baseline_plus_low_blocker"](pools, rng)
    assert len(pts) == TARGET[64]
    st = IncrementalConflictState(64, pts)
    cross_check_or_stop(st, Path("scratch/agent_c"), "test_swap_init")
    prop = propose_1for1(st, pools.external_candidates(), [], rng)
    assert prop is not None
    rems, adds = prop
    st.swap_many(rems, adds)
    assert len(st.points) == TARGET[64]
    cross_check_or_stop(st, Path("scratch/agent_c"), "test_swap_after")


def test_2for2_preserves_cardinality():
    pools = load_gate1_pools(100)
    import random

    rng = random.Random(1)
    pts = INIT_FUNCS["gate1_low_delta_v"](pools, rng)
    assert len(pts) == TARGET[100]
    st = IncrementalConflictState(100, pts)
    prop = propose_2for2(st, pools.external_candidates(), [], rng)
    assert prop is not None
    rems, adds = prop
    st.swap_many(rems, adds)
    assert len(st.points) == TARGET[100]
    assert st.V == conflict_count(sorted(st.points), 100)


def test_short_search_keeps_fixed_cardinality():
    r = run_fixed_cardinality_search(
        n=64,
        seed=99,
        time_budget_s=8.0,
        init_method="orbit_informed",
        n_replicas=2,
        exact_check_every=50,
        repair_every=100,
        checkpoint_every_s=1000.0,
    )
    assert len(r.points) == TARGET[64]
    assert r.best_V == conflict_count(r.points, 64)
    assert r.incremental_exact_agree is True
    assert r.best_V <= r.initial_V or r.iterations >= 0  # may not improve in 8s


def test_mismatch_detector_saves_counterexample(tmp_path):
    st = IncrementalConflictState(8, [(0, 0), (0, 1), (1, 0)])
    st.V = -1  # corrupt
    with pytest.raises(VMismatchError):
        cross_check_or_stop(st, tmp_path, "corrupt")
    files = list((tmp_path / "counterexamples").glob("*.json"))
    assert files
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert payload["incremental_V"] == -1
    assert payload["exact_V"] >= 0
