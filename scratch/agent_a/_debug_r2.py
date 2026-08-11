import sys
sys.path.insert(0, ".")
from ortools.sat.python import cp_model
from data.baselines.official_raw import SOL_100
from src.search.hamming_shell_conflict import load_policy_universe, reconstruct_S, find_witness_cuts, dual_verify
from src.verification.conflict_metric import conflict_count

rem, add, h = load_policy_universe(100, "U_small_r2")
print("hash", h, "rem", len(rem), "add", len(add))
r = 2
model = cp_model.CpModel()
keep = [model.NewBoolVar(f"k{i}") for i in range(len(rem))]
take = [model.NewBoolVar(f"a{i}") for i in range(len(add))]
model.Add(sum(keep) == len(rem) - r)
model.Add(sum(take) == r + 1)
solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 1
st = solver.Solve(model)
print("cardinality-only status", solver.StatusName(st))
if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    keep_bits = [solver.Value(keep[i])==1 for i in range(len(rem))]
    take_bits = [solver.Value(take[i])==1 for i in range(len(add))]
    S = reconstruct_S(SOL_100, rem, add, keep_bits, take_bits)
    print("size", len(S), "V", conflict_count(S, 100), "witnesses", len(find_witness_cuts(S)))

# Now run search with verbose - check how many rounds
from src.search.hamming_shell_conflict import hamming_shell_search
res = hamming_shell_search(100, SOL_100, rem, add, r=2, time_budget_s=60, seed=1, u_id="U_small_r2", universe_hash_str=h, per_round_time_limit_s=10, num_workers=5)
print("status", res.status)
print("rounds", res.meta.get("rounds"), "cuts", res.meta.get("final_cuts"))
print("round_log", res.meta.get("round_log", [])[:10])
