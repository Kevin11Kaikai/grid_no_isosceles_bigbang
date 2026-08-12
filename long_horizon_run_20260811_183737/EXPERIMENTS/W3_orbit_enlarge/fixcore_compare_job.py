import json,os,sys
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
from src.search.orbit_defect_search import SearchConfig,solve_orbit_defect,save_checkpoint,maybe_save_candidate
# Cheap smoke: fix_core True vs soft on enlarged Type0
rows=[]
for fix,seed,tag in [(True,831,"fixcore"),(False,832,"softcore")]:
  cfg=SearchConfig(n=100,symmetry_type=0,mode="defect",target_size=165,defect_budget_min=1,defect_budget_max=12,time_budget_s=600.0,seed=seed,num_workers=3,max_extra_orbits=200,max_defect_pool=200,halo_radius=14,agent_c_universe="U_large",fix_core=fix,soft_core=not fix)
  print(json.dumps({"start":tag,"fix_core":fix,"seed":seed}),flush=True)
  res=solve_orbit_defect(cfg)
  ck=save_checkpoint(res,f"w3_{tag}_n100_t0_s{seed}")
  row={"tag":tag,"fix_core":fix,"status":res.get("solver_status"),"size":res.get("size"),"universe_id":(res.get("universe") or {}).get("universe_id"),"model_hash":res.get("model_hash"),"wall_time_s":res.get("wall_time_s"),"rounds":res.get("rounds"),"final_cuts":res.get("final_cuts"),"checkpoint":str(ck)}
  rows.append(row); print(json.dumps(row,indent=2),flush=True)
open(r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\EXPERIMENTS\W3_orbit_enlarge\fixcore_compare.json","w",encoding="utf-8").write(json.dumps({"schema":"w3_fixcore_compare_v1","rows":rows},indent=2)+"\n")
