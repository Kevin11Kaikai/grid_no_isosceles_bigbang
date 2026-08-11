import sys, json, time, itertools
sys.path.insert(0, ".")
from data.baselines.official_raw import SOL_100, SOL_64
from src.search.hamming_shell_conflict import (
    load_policy_universe, hamming_shell_search, universe_hash, atomic_write_json, append_manifest, default_num_workers
)
from src.search.incremental_state import IncrementalIsoscelesFreeSet

# Fast enum confirm U_small_r2 using incremental state rebuild from fixed
rem, add, h = load_policy_universe(100, "U_small_r2")
s0 = list(SOL_100)
s0_set = set(map(tuple,s0))
fixed = sorted(s0_set - set(rem))
print("workers", default_num_workers(), "fixed", len(fixed))

def legal_shell(keep_idx_drop, add_idx_take):
    st = IncrementalIsoscelesFreeSet(100)
    for p in fixed:
        st._add_unchecked(p)
    for i,p in enumerate(rem):
        if i not in keep_idx_drop:
            ok,_ = st.can_add(p)
            if not ok: return False
            st._add_unchecked(p)
    for j in add_idx_take:
        ok,_ = st.can_add(add[j])
        if not ok: return False
        st._add_unchecked(add[j])
    return True

t0=time.time(); checked=0; found=False; best_partial=0
for rem_drop in itertools.combinations(range(len(rem)), 2):
    for add_take in itertools.combinations(range(len(add)), 3):
        checked += 1
        if legal_shell(set(rem_drop), add_take):
            found=True
            print("FOUND legal at", checked)
            break
    if found: break
    if checked % 200000 < 13244:
        print("progress", checked, "t", round(time.time()-t0,1))
print("fast brute", {"checked":checked, "found":found, "wall":time.time()-t0, "universe_hash":h})
atomic_write_json("scratch/agent_a/hamming/u_small_r2_brute_confirm.json", {
    "checked": checked, "found_legal": found, "wall_time_s": time.time()-t0,
    "universe_hash": h, "method": "incremental_can_add_enumeration",
    "note": "confirms CP-SAT INFEASIBLE_SCOPED for U_small_r2 r=2"
})
