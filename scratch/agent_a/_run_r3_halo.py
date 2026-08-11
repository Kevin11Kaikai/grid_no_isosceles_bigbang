import sys, json, time, subprocess
sys.path.insert(0, ".")
from data.baselines.official_raw import SOL_100
from src.search.hamming_shell_conflict import (
    hamming_shell_search, universe_hash, atomic_write_json, append_manifest, load_policy_universe
)
# Broader add pool: U_large add union Chebyshev-2 halo of easiest_16 and U_small adds, uncapped
from scratch.agent_a.run_halo_pilots import chebyshev_halo  # may fail if not package
exec(open("scratch/agent_a/run_halo_pilots.py", encoding="utf-8").read().split("def build_universes")[0])

commit = subprocess.check_output(["git","rev-parse","HEAD"], text=True).strip()
s0 = [tuple(p) for p in SOL_100]
s0_set = set(s0)
_, add_large, _ = load_policy_universe(100, "U_large")
with open("scratch/audit/gate1_consistency_check.json", encoding="utf-8") as f:
    e16 = [tuple(p) for p in json.load(f)["n100_deletion_bound"]["easiest_16_qs_exact_min_deletions_2"]]
with open("scratch/audit/agent_c/universe_halo_diagnostics.json", encoding="utf-8") as f:
    us = json.load(f)["baselines"]["n100"]["universes"]["U_small"]["addable_unselected_points"]
seeds = list(map(tuple, add_large)) + e16 + [tuple(p) for p in us]
add = sorted({p for p in chebyshev_halo(seeds, 100, 2) if p not in s0_set})
rem = sorted(s0)
# Cap add at 400 by keeping seed points first then halo by distance-to-seed
if len(add) > 400:
    seed_set = set(seeds)
    core = [p for p in add if p in seed_set]
    extra = [p for p in add if p not in seed_set]
    add = sorted(core + extra[: max(0, 400 - len(core))])
h = universe_hash(rem, add)
uid = "U_fullrem_Ahalo2_r3"
print(uid, "vars", len(rem)+len(add), "add", len(add), h, flush=True)
atomic_write_json("scratch/agent_a/hamming/U_fullrem_Ahalo2_r3_universe.json", {
    "U_id": uid, "n_removable": len(rem), "n_addable": len(add), "n_vars": len(rem)+len(add),
    "universe_hash": h, "r": 3
})
res = hamming_shell_search(100, list(SOL_100), rem, add, r=3, time_budget_s=3600, seed=1, u_id=uid, universe_hash_str=h, per_round_time_limit_s=90, num_workers=5, checkpoint_path=f"scratch/agent_a/checkpoints/{uid}_seed1.ckpt.json", checkpoint_every_s=300, git_commit=commit)
out = f"scratch/agent_a/hamming/r3_n100_{uid}_seed1.json"
payload = {"status":res.status,"meta":res.meta,"points":[list(p) for p in res.points] if res.points else None,"universe_hash":h,"n_vars":len(rem)+len(add),"U_id":uid,"n_add":len(add),"n_rem":len(rem)}
atomic_write_json(out, payload)
append_manifest("scratch/agent_a/manifest.jsonl", {"event":"hamming_r3_halo","out":out,"status":res.status,"universe_hash":h,"n_vars":len(rem)+len(add)})
print("DONE", res.status, "rounds", res.meta.get("rounds"), "cuts", res.meta.get("final_cuts"), "bestV", res.meta.get("best_illegal_V"), "wall", res.meta.get("wall_time_s"), flush=True)
if res.status == "FEASIBLE_LEGAL":
    from src.search.hamming_shell_conflict import dual_verify
    ver = dual_verify(res.points, 100)
    atomic_write_json(f"scratch/agent_a/candidates/n100_k165_{uid}_seed1.json", {
        "points_unsorted":[list(p) for p in res.points],
        "points_sorted":[list(p) for p in sorted(res.points)],
        "verification":ver,"method":"hamming_shell_conflict","seed":1,"U_id":uid,"git_commit":commit,"universe_hash":h
    })
    print("CANDIDATE", ver, flush=True)
