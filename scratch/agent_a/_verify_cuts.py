import sys
sys.path.insert(0, ".")
from ortools.sat.python import cp_model
from data.baselines.official_raw import SOL_100
from src.search.hamming_shell_conflict import (
    load_policy_universe, reconstruct_S, find_witness_cuts, hamming_shell_search, universe_hash
)
from src.verification.oracle_verifier import is_legal_pivot_method
from src.verification.conflict_metric import conflict_count

rem, add, h = load_policy_universe(100, "U_small_r2")
s0 = list(SOL_100)
s0_set = set(map(tuple, s0))
rem_set = set(rem)
add_set = set(add)
fixed = s0_set - rem_set
rem_index = {p:i for i,p in enumerate(rem)}
add_index = {p:i for i,p in enumerate(add)}

# Get first incumbent
r=2
model = cp_model.CpModel()
keep = [model.NewBoolVar(f"k{i}") for i in range(len(rem))]
take = [model.NewBoolVar(f"a{i}") for i in range(len(add))]
model.Add(sum(keep) == len(rem)-r)
model.Add(sum(take) == r+1)
solver = cp_model.CpSolver()
solver.Solve(model)
keep_bits = [solver.Value(keep[i])==1 for i in range(len(rem))]
take_bits = [solver.Value(take[i])==1 for i in range(len(add))]
S = reconstruct_S(s0, rem, add, keep_bits, take_bits)
witnesses = find_witness_cuts(S)
print("V", conflict_count(S,100), "n_wit", len(witnesses), "legal", is_legal_pivot_method(S,100)[0])

def encode(a,b,c):
    const=0; vars_=[]
    for p in (a,b,c):
        if p in fixed: const+=1
        elif p in rem_index: vars_.append(("k", rem_index[p]))
        elif p in add_index: vars_.append(("a", add_index[p]))
        else: return None
    return (frozenset(vars_), const)

# Check each cut is violated by S
violations_ok = 0
for trip in witnesses:
    enc = encode(*trip)
    assert enc is not None, trip
    vars_fs, const = enc
    # evaluate on S
    val = const
    for kind, idx in vars_fs:
        p = rem[idx] if kind=="k" else add[idx]
        val += 1 if p in set(map(tuple,S)) else 0
    assert val >= 3, (trip, enc, val)  # must be violated (all 3 present)
    # cut says val_expr <= 2, so violated when val>=3
    violations_ok += 1
print("all witness cuts violated by incumbent:", violations_ok)

# Also verify: if we had a legal shell set, cuts wouldn't remove it.
# Synthetic: take S0 itself - not in shell. Build legal by taking S0 and... can't easily.
# Check negative control and r2 seeds with different seeds still INFEAS
for seed in [1,2,3,7,99]:
    res = hamming_shell_search(100, s0, rem, add, r=2, time_budget_s=30, seed=seed, u_id="U_small_r2", universe_hash_str=h, per_round_time_limit_s=10, num_workers=5)
    print("seed", seed, res.status, "rounds", res.meta["rounds"], "cuts", res.meta["final_cuts"], "bestV", res.meta.get("best_illegal_V"))
