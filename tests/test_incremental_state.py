"""Stress tests for src/search/incremental_state.py against the slow oracle.

Runs randomized add/remove/swap sequences and cross-checks the incremental
cache against the oracle verifier after every move (small n, so oracle calls
are cheap) to catch stale-cache bugs, off-by-one errors, etc.
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.search.incremental_state import IncrementalIsoscelesFreeSet
from src.verification.oracle_verifier import is_legal_pivot_method


def test_add_remove_swap_random_sequence_matches_oracle():
    rng = random.Random(777)
    n = 7
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    ifs = IncrementalIsoscelesFreeSet(n)

    for step in range(500):
        move = rng.choice(["add", "remove", "swap"])
        if move == "add" or not ifs.points:
            p = rng.choice(all_pts)
            ifs.add_point(p)
        elif move == "remove":
            p = rng.choice(list(ifs.points))
            ifs.remove_point(p)
        else:  # swap
            if ifs.points:
                rem = rng.choice(list(ifs.points))
            else:
                rem = rng.choice(all_pts)
            add = rng.choice(all_pts)
            ifs.swap(rem, add)

        # Full oracle cross-check after every move (n is tiny, cheap).
        ok_oracle, witness = is_legal_pivot_method(list(ifs.points), n)
        assert ok_oracle, f"step {step}: incremental state diverged from oracle: {witness}"
        ifs.cross_check_with_oracle()  # also checks internal cache consistency

    print(f"final size after 500 random moves: {ifs.size()}")


def test_multi_swap_chain():
    n = 6
    ifs = IncrementalIsoscelesFreeSet(n)
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    rng = random.Random(42)
    # Build up a legal set greedily first.
    rng.shuffle(all_pts)
    for p in all_pts:
        ifs.add_point(p)
    ifs.cross_check_with_oracle()
    base_size = ifs.size()

    # Now do a chain of swaps (ejection-chain style) and verify each step.
    pts_snapshot = list(ifs.points)
    rng.shuffle(pts_snapshot)
    for i in range(min(10, len(pts_snapshot))):
        rem = pts_snapshot[i]
        cand = rng.choice(all_pts)
        ifs.swap(rem, cand)
        ok_oracle, witness = is_legal_pivot_method(list(ifs.points), n)
        assert ok_oracle, f"multi-swap step {i}: {witness}"
    ifs.cross_check_with_oracle()


def test_checkpoint_restore_roundtrip():
    n = 8
    ifs = IncrementalIsoscelesFreeSet(n)
    rng = random.Random(9)
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(all_pts)
    for p in all_pts[:60]:
        ifs.add_point(p)
    ifs.cross_check_with_oracle()

    snapshot = set(ifs.points)

    # Simulate "checkpoint restore": build a fresh incremental set from the
    # saved point list and confirm it reaches an identical, oracle-legal state.
    restored = IncrementalIsoscelesFreeSet(n)
    for p in snapshot:
        added = restored.add_point(p)
        assert added, f"restore failed to re-add {p} -- checkpoint was not self-consistent"
    assert restored.points == snapshot
    restored.cross_check_with_oracle()


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
