import json, sys, time, os
sys.path.insert(0, ".")
from data.baselines.official_raw import SOL_64, SOL_100
from src.search.conflict_multiregion import conflict_multiregion_pilot
from src.search.hamming_shell_conflict import atomic_write_json, append_manifest

runs = []
for n, s0, budget in [(64, SOL_64, 720), (100, SOL_100, 600)]:
    for mode in ["pure_spatial", "conflict_driven", "hybrid"]:
        print(f"=== multiregion n={n} mode={mode} budget={budget} ===", flush=True)
        t0 = time.time()
        meta = conflict_multiregion_pilot(n, s0, mode, time_budget_s=budget, seed=1, milp_time_limit_s=6.0, box_cap=100)
        meta["wall_time_s_outer"] = time.time() - t0
        out = f"scratch/agent_a/multiregion/n{n}_{mode}_seed1.json"
        atomic_write_json(out, meta)
        append_manifest("scratch/agent_a/manifest.jsonl", {"event":"multiregion", "out":out, "mode":mode, "n":n, "best_size":meta["best_size"], "improved":meta["improved"], "wall":meta["wall_time_s"]})
        runs.append({"n":n, "mode":mode, "best_size":meta["best_size"], "baseline_size":meta["baseline_size"], "improved":meta["improved"], "iterations":meta["iterations"], "wall_time_s":meta["wall_time_s"], "V_best":meta["V_best"]})
        print("->", meta["best_size"], "improved", meta["improved"], "iters", meta["iterations"], flush=True)

atomic_write_json("scratch/agent_a/multiregion_pilot_summary.json", {
    "schema": "agent_a_multiregion_pilot_v1",
    "note": "Giant projection CC never used as a small community; conflict_driven uses spatial_knn6 far bridges.",
    "runs": runs,
})
print("MULTIREGION DONE", flush=True)
