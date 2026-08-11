import sys, json, time
sys.path.insert(0, ".")
from data.baselines.official_raw import SOL_100
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash, atomic_write_json, append_manifest, load_policy_universe
import subprocess
commit = subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
s0 = list(SOL_100)
# r=3 with full rem + U_large add (after r=2 scoped empty on same add pool)
rem_large, add_large, _ = load_policy_universe(100, "U_large")
rem = sorted(set(map(tuple,s0)))
add = sorted(set(map(tuple, add_large)))
h = universe_hash(rem, add)
uid = "U_fullrem_Alarge_r3"
print("start", uid, "vars", len(rem)+len(add), h, flush=True)
res = hamming_shell_search(100, s0, rem, add, r=3, time_budget_s=2400, seed=1, u_id=uid, universe_hash_str=h, per_round_time_limit_s=60, num_workers=5, checkpoint_path=f"scratch/agent_a/checkpoints/{uid}_seed1.ckpt.json", git_commit=commit)
out = f"scratch/agent_a/hamming/r3_n100_{uid}_seed1.json"
atomic_write_json(out, {"status":res.status,"meta":res.meta,"points":[list(p) for p in res.points] if res.points else None,"universe_hash":h,"n_vars":len(rem)+len(add),"U_id":uid})
append_manifest("scratch/agent_a/manifest.jsonl", {"event":"hamming_r3","out":out,"status":res.status,"U_id":uid,"universe_hash":h})
print("DONE", res.status, res.meta.get("rounds"), res.meta.get("final_cuts"), res.meta.get("best_illegal_V"), flush=True)
