#!/usr/bin/env python3
"""Wave3: 2h Type0 mega enlarge after 60min TIMEOUT (same class, longer wall)."""
from __future__ import annotations
import json, os, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from src.search.orbit_defect_search import SearchConfig, solve_orbit_defect, save_checkpoint, maybe_save_candidate

def main():
    try: sys.stdout.reconfigure(line_buffering=True)
    except Exception: pass
    time_s=float(os.environ.get("W3_ORBIT_TIME","7200"))
    seed=int(os.environ.get("W3_ORBIT_SEED","801"))
    workers=int(os.environ.get("W3_ORBIT_WORKERS","5"))
    exp=os.path.join(RUN,"EXPERIMENTS","W3_orbit_enlarge"); os.makedirs(exp,exist_ok=True)
    cfg=SearchConfig(n=100,symmetry_type=0,mode="defect",target_size=165,defect_budget_min=1,defect_budget_max=20,time_budget_s=time_s,seed=seed,num_workers=workers,max_extra_orbits=360,max_defect_pool=360,halo_radius=20,agent_c_universe="U_large")
    print(json.dumps({"start":"t0_mega_2h","time_s":time_s,"seed":seed,"max_extra":360,"halo":20}),flush=True)
    res=solve_orbit_defect(cfg)
    ck=save_checkpoint(res,f"w3_mega_n100_t0_defect_s{seed}")
    cand=maybe_save_candidate(res)
    out={"status":res.get("solver_status"),"size":res.get("size"),"universe_id":(res.get("universe") or {}).get("universe_id"),"n_free":(res.get("universe") or {}).get("n_free_orbits"),"n_def":(res.get("universe") or {}).get("n_defect_points"),"model_hash":res.get("model_hash"),"wall_time_s":res.get("wall_time_s"),"rounds":res.get("rounds"),"final_cuts":res.get("final_cuts"),"checkpoint":str(ck),"candidate":str(cand) if cand else None,"cfg":{"max_extra":360,"halo":20,"dmax":20,"time_s":time_s,"seed":seed}}
    open(os.path.join(exp,f"mega_t0_defect_s{seed}_2h.json"),"w",encoding="utf-8").write(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2),flush=True)
if __name__=="__main__": main()
