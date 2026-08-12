import json,os,sys
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
from src.search.orbit_defect_search import SearchConfig,solve_orbit_defect,save_checkpoint,maybe_save_candidate
cfg=SearchConfig(n=100,symmetry_type=0,mode="defect",target_size=165,defect_budget_min=1,defect_budget_max=20,time_budget_s=5400.0,seed=841,num_workers=5,max_extra_orbits=360,max_defect_pool=360,halo_radius=20,agent_c_universe="U_large",defect_rank="cert_lb2",soft_core=True,fix_core=False)
print(json.dumps({"start":"mega_certlb2","seed":841,"time":5400}),flush=True)
res=solve_orbit_defect(cfg)
ck=save_checkpoint(res,"w3_mega_certlb2_n100_t0_s841")
cand=maybe_save_candidate(res)
out={"status":res.get("solver_status"),"size":res.get("size"),"universe_id":(res.get("universe") or {}).get("universe_id"),"model_hash":res.get("model_hash"),"wall_time_s":res.get("wall_time_s"),"rounds":res.get("rounds"),"final_cuts":res.get("final_cuts"),"defect_rank":"cert_lb2","checkpoint":str(ck),"candidate":str(cand) if cand else None}
open(r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\EXPERIMENTS\W3_orbit_enlarge\mega_certlb2_t0_s841_90m.json","w",encoding="utf-8").write(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2),flush=True)
