import sys, time
sys.path.insert(0, ".")
from data.baselines.official_raw import SOL_100, SOL_64
from src.search.hamming_shell_conflict import load_policy_universe, hamming_shell_search, universe_hash

rem, add, h = load_policy_universe(100, "U_medium")
print("U_medium", len(rem), len(add), h)
t0=time.time()
res = hamming_shell_search(100, SOL_100, rem, add, r=2, time_budget_s=120, seed=1, u_id="U_medium", universe_hash_str=h, per_round_time_limit_s=20, num_workers=5)
print("status", res.status, "rounds", res.meta["rounds"], "cuts", res.meta["final_cuts"], "bestV", res.meta.get("best_illegal_V"), "wall", time.time()-t0)

rem64, add64, h64 = load_policy_universe(64, "U_small")
print("n64", len(rem64), len(add64), h64)
t0=time.time()
res64 = hamming_shell_search(64, SOL_64, rem64, add64, r=1, time_budget_s=120, seed=1, u_id="U_small", universe_hash_str=h64, per_round_time_limit_s=20, num_workers=5)
print("n64 status", res64.status, "rounds", res64.meta["rounds"], "cuts", res64.meta["final_cuts"], "bestV", res64.meta.get("best_illegal_V"), "wall", time.time()-t0)
