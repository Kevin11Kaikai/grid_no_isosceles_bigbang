"""Small-n exact (or timed) search for Q4(n).

Uses the frozen checker in q4.py. Writes tables to out/.
"""
from __future__ import annotations

import json
import os
import random
import sys
import time

from q4 import FourDir, greedy, verify

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def _seed_best(n, restarts=80):
    best_sz, best_set = 0, []
    rng = random.Random(12345 + n)
    for _ in range(restarts):
        s = greedy(n, rng)
        if len(s) > best_sz:
            best_sz = len(s)
            best_set = list(s)
    return best_sz, best_set


def exact_q4(n, time_limit=None, restarts=80):
    """Return dict: n, size, exact?, seconds, nodes, set.

    If time_limit is hit, size is a lower bound (best found, seeded by greedy).
    """
    t0 = time.perf_counter()
    best_sz, best_set = _seed_best(n, restarts=restarts)
    assert verify(n, best_set)

    st = FourDir(n)
    cells = [(x, y) for y in range(n) for x in range(n)]
    deadline = None if time_limit is None else (t0 + time_limit)
    timed_out = False
    nodes = 0

    def rec(cand):
        nonlocal best_sz, best_set, timed_out, nodes
        nodes += 1
        if deadline is not None and (nodes & 4095) == 0:
            if time.perf_counter() >= deadline:
                timed_out = True
                return
        k = len(st.pts)
        if k > best_sz:
            best_sz = k
            best_set = list(st.pts)
        if k + len(cand) <= best_sz or timed_out:
            return
        x, y = cand[0]
        rest = cand[1:]
        ks = st.can_add(x, y)
        if ks is not None:
            rec_id = st.push(x, y, ks)
            nxt = [q for q in rest if st.can_add(q[0], q[1]) is not None]
            rec(nxt)
            st.pop(rec_id)
            if timed_out:
                return
        rec(rest)

    rec(cells)
    elapsed = time.perf_counter() - t0
    assert verify(n, best_set)
    return {
        "n": n,
        "size": best_sz,
        "size_over_n": best_sz / n,
        "exact": not timed_out,
        "seconds": round(elapsed, 4),
        "nodes": nodes,
        "set": [list(p) for p in sorted(best_set)],
    }


def _self_check():
    """push/pop must restore; greedy sets must verify."""
    rng = random.Random(0)
    for n in (5, 8):
        s = greedy(n, rng)
        assert verify(n, s), n
        st = FourDir(n)
        stack = []
        for x, y in list(s):
            ks = st.can_add(x, y)
            assert ks is not None
            stack.append(st.push(x, y, ks))
        assert st.pts == set(s)
        while stack:
            st.pop(stack.pop())
        assert st.pts == set()
        assert st.kill_col == set()
        assert all(c == 0 for c in st.cnt_col)


def main():
    _self_check()
    os.makedirs(OUT, exist_ok=True)
    # n=1..6 should be exact quickly. n=7..10 get a time budget.
    limits = {
        1: None,
        2: None,
        3: None,
        4: None,
        5: None,
        6: 60.0,
        7: 90.0,
        8: 180.0,
        9: 180.0,
        10: 180.0,
    }
    rows = []
    for n in range(1, 11):
        print(f"search n={n} limit={limits[n]} ...", flush=True)
        rec = exact_q4(n, time_limit=limits[n])
        rows.append(rec)
        flag = "EXACT" if rec["exact"] else "LOWER_BOUND (timeout)"
        print(
            f"  n={n:2d}  Q4>={rec['size']:3d}  /n={rec['size_over_n']:.3f}  "
            f"{flag}  {rec['seconds']:.2f}s  nodes={rec['nodes']}",
            flush=True,
        )
        with open(os.path.join(OUT, f"exact_n{n}.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2)
    slim = [{k: r[k] for k in ("n", "size", "size_over_n", "exact", "seconds", "nodes")} for r in rows]
    with open(os.path.join(OUT, "exact_table.json"), "w", encoding="utf-8") as f:
        json.dump(slim, f, indent=2)
    print("wrote out/exact_table.json")


if __name__ == "__main__":
    sys.exit(main())
