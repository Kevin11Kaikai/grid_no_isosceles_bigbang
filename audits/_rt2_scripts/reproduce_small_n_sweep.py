"""Task 4: independently reproduce C(4)=6 and C(5)=7 with a DIFFERENT seed than the
original sweep (which used seed=1; logs/cpsat_small_n_sweep.json). Calls the `sweep()`
function directly (rather than running the module as __main__) so the output is written
to this audits/ directory instead of overwriting the project's logs/cpsat_small_n_sweep.json
-- this Red Team session is scoped to only write inside audits/.

Equivalent to: .venv_solver/Scripts/python.exe -m src.search.cpsat_small_n_sweep "4,5" 30 120 2
but with output redirected.
"""
import sys, os, json, time

sys.path.insert(0, r"D:\Others\grid_no_isosceles_bigbang")

from src.search.cpsat_small_n_sweep import sweep

t0 = time.time()
results = sweep([4, 5], lb_budget_s=30.0, ub_budget_s=120.0, per_round_time_limit_s=30.0, seed=2)
print(f"\ntotal wall time: {time.time()-t0:.1f}s")

out = r"D:\Others\grid_no_isosceles_bigbang\audits\_rt2_scripts\small_n_reproduction_seed2.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"wrote {out}")

print("\n=== COMPARISON vs original seed=1 sweep (logs/cpsat_small_n_sweep.json) ===")
orig_path = r"D:\Others\grid_no_isosceles_bigbang\logs\cpsat_small_n_sweep.json"
with open(orig_path, "r", encoding="utf-8") as f:
    orig = json.load(f)

for n in [4, 5]:
    orig_entry = orig[str(n)]
    new_entry = results[n]
    match = (orig_entry["status"] == new_entry["status"] == "INFEASIBLE_PROVEN"
             and orig_entry["lower_bound_found"] == new_entry["lower_bound_found"])
    print(f"n={n}: original(seed=1) lb={orig_entry['lower_bound_found']} status={orig_entry['status']} | "
          f"reproduction(seed=2) lb={new_entry['lower_bound_found']} status={new_entry['status']} | "
          f"MATCH={match}")
