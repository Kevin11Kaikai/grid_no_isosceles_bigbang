"""Task 3(a): is F-005's `accepted_worse_moves: 0` (n=64/n=100, 30-min runs) evidence
of a genuinely-dead code branch, or a real empirical fact about those specific runs?

sa_exact_repair.py's acceptance logic (lines ~140-146):
    if delta >= 0: accept = True
    else:
        p_accept = math.exp(delta / max(T, 1e-9))
        if rng.random() < p_accept: accept = True; accepted_worse += 1

This script deliberately engineers conditions under which delta < 0 should be common
(tiny MILP time limit so HiGHS is starved and returns weak incumbents; large regions
relative to a sparse grid so repairs frequently shrink the region's occupancy; high
initial temperature) and checks whether `accepted_worse_moves` becomes > 0. If it can
be made to fire here, that proves the branch is live code, not dead, and the 0 seen in
F-005 is a real property of the specific (well-tuned, large-N, generous-MILP-time-limit)
production runs, not a masked bug.
"""
import sys, os

sys.path.insert(0, r"D:\Others\grid_no_isosceles_bigbang")

from src.search.sa_exact_repair import sa_exact_repair_run
from src.search.greedy import greedy_once
from src.verification.oracle_verifier import is_legal_pivot_method

print("=== Adversarial parameter sweep to try to force accepted_worse_moves > 0 ===")
any_fired = False
for n in [10, 12, 14]:
    for seed in [1, 2, 3, 4, 5]:
        init_pts, _ = greedy_once(n, seed=seed, order="random")
        best, meta = sa_exact_repair_run(
            n, init_pts,
            time_budget_s=4.0,
            seed=seed,
            T0=8.0,                 # high temperature -> lenient acceptance
            alpha=0.999,
            milp_time_limit_s=0.01,  # starve HiGHS -> weak/suboptimal incumbents more likely
            region_size_cap=n * n,   # whole-grid regions -> big, hard sub-instances
            reheat_after=50,
            oracle_check_every=10,
        )
        fired = meta["accepted_worse_moves"]
        any_fired = any_fired or fired > 0
        ok, w = is_legal_pivot_method(best, n)
        print(f"n={n:2d} seed={seed}: iterations={meta['iterations']:5d} "
              f"accepted_worse_moves={fired:4d} final_size={meta['final_size']:3d} "
              f"initial_size={meta['initial_size']:3d} final_legal={ok}")
        if not ok:
            print("  !!! FINAL BEST FAILED ORACLE CHECK", w)

print()
if any_fired:
    print("RESULT: accepted_worse_moves > 0 achieved under adversarial params -- "
          "the delta<0 branch is LIVE code, confirming F-005's 'accepted_worse_moves: 0' "
          "at production parameters (large region caps notwithstanding, generous MILP "
          "time limit, T0=3.0) is a real empirical property of THOSE runs, not evidence "
          "of dead/unreachable code.")
else:
    print("RESULT: could NOT trigger accepted_worse_moves > 0 even under adversarial "
          "params -- would need deeper investigation into whether the branch is reachable "
          "at all under this project's exact_repair_region formulation.")
