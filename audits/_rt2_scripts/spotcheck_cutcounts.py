"""Task 3(c): spot-check F-009's claim: 'seed_cuts_from_points ... 773812 cuts for n=64
in 0.6s, 2000000 (capped) for n=100 in 2.7s'. Run with the project-local venv
(.venv_solver, has ortools) since cpsat_lazy.py imports ortools at module level.

Also flags whether the SEEDED n=64 maximize run this number is allegedly drawn from
was ever actually saved to logs/ (it was not found there during this audit --
logs/cpsat_maximize_n64_seed1.json instead contains the OLD, unseeded, 4-round/994s
run per its own round_log starting from total_cuts=0)."""
import sys, os, time

sys.path.insert(0, r"D:\Others\grid_no_isosceles_bigbang")

from src.search.cpsat_lazy import seed_cuts_from_points
from data.baselines.official_raw import SOL_64, SOL_100

for n, sol, max_cuts in [(64, SOL_64, 2_000_000), (100, SOL_100, 2_000_000)]:
    all_pts = [(x, y) for x in range(n) for y in range(n)]
    idx = {p: i for i, p in enumerate(all_pts)}
    seed_points = list(sol)
    t0 = time.time()
    cuts = seed_cuts_from_points(n, seed_points, idx, max_cuts=max_cuts)
    dt = time.time() - t0
    print(f"n={n}: seed_points={len(seed_points)} -> {len(cuts)} cuts in {dt:.3f}s "
          f"(capped at {max_cuts})")
