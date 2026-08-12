import json, os, sys
sys.path.insert(0, r"d:\others\grid_no_isosceles_bigbang")
from src.search.orbit_defect_search import SearchConfig, solve_orbit_defect, save_checkpoint, maybe_save_candidate
cfg=SearchConfig(n=100, symmetry_type=1, mode="defect", target_size=165, defect_budget_min=1, defect_budget_max=16, time_budget_s=2400.0, seed=521, num_workers=4, max_extra_orbits=320, max_defect_pool=320, halo_radius=18, agent_c_universe="U_large")
print(json.dumps({"start":"t1_xlarge","seed":521,"time":2400}), flush=True)
res=solve_orbit_defect(cfg)
ck=save_checkpoint(res,"w3_xlarge_n100_t1_defect_s521")
cand=maybe_save_candidate(res)
out={"status":res.get("solver_status"),"size":res.get("size"),"universe_id":(res.get("universe") or {}).get("universe_id"),"n_free":(res.get("universe") or {}).get("n_free_orbits"),"n_def":(res.get("universe") or {}).get("n_defect_points"),"model_hash":res.get("model_hash"),"wall_time_s":res.get("wall_time_s"),"rounds":res.get("rounds"),"final_cuts":res.get("final_cuts"),"checkpoint":str(ck),"candidate":str(cand) if cand else None}
open(os.path.join(r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\EXPERIMENTS\W3_orbit_enlarge","long_t1_defect_s521_xlarge.json"),"w",encoding="utf-8").write(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2), flush=True)
