import json,os,sys
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
from src.search.orbit_defect_search import SearchConfig,solve_orbit_defect,save_checkpoint,maybe_save_candidate
rows=[]
for st,seed in ((5,851),(6,861)):
  cfg=SearchConfig(n=100,symmetry_type=st,mode="defect",target_size=165,defect_budget_min=1,defect_budget_max=16,time_budget_s=1800.0,seed=seed,num_workers=5,max_extra_orbits=320,max_defect_pool=320,halo_radius=18,agent_c_universe="U_large",soft_core=True)
  print(json.dumps({"start":f"t{st}_xlarge","seed":seed}),flush=True)
  res=solve_orbit_defect(cfg)
  ck=save_checkpoint(res,f"w3_xlarge_n100_t{st}_defect_s{seed}")
  cand=maybe_save_candidate(res)
  row={"symmetry_type":st,"seed":seed,"status":res.get("solver_status"),"size":res.get("size"),"universe_id":(res.get("universe") or {}).get("universe_id"),"model_hash":res.get("model_hash"),"wall_time_s":res.get("wall_time_s"),"rounds":res.get("rounds"),"final_cuts":res.get("final_cuts"),"checkpoint":str(ck),"candidate":str(cand) if cand else None}
  rows.append(row)
  open(os.path.join(r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\EXPERIMENTS\W3_orbit_enlarge",f"long_t{st}_defect_s{seed}_xlarge.json"),"w",encoding="utf-8").write(json.dumps(row,indent=2)+"\n")
  print(json.dumps(row,indent=2),flush=True)
  if (row.get("size") or 0)>=165: break
open(os.path.join(r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\EXPERIMENTS\W3_orbit_enlarge","t56_summary.json"),"w",encoding="utf-8").write(json.dumps({"schema":"w3_t56_v1","rows":rows},indent=2)+"\n")
