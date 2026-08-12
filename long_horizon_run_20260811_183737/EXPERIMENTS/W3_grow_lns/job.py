import json,os,sys,time,random
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\SCRATCH")
from from_scratch_grow import grow
from src.search.lns_exact_repair import lns_exact_run
from src.verification.oracle_verifier import is_legal_pivot_method
from src.verification_independent.independent_verifier import verify_independent
from src.structures.candidate_io import sha256_of_points

RUN=r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737"
exp=os.path.join(RUN,"EXPERIMENTS","W3_grow_lns")
os.makedirs(exp,exist_ok=True)
rows=[]
t0=time.time()
for seed,mode,gsec,lsec in ((202,"boundary_first",120.0,900.0),(203,"spiral_mix",120.0,720.0),(204,"center_first",90.0,600.0)):
    g=grow(100, seed, mode, seconds=gsec)
    start=[tuple(p) for p in g.get("points") or []]
    if not start:
        # grow may omit points below threshold — rebuild via size field only if points present
        print(json.dumps({"seed":seed,"mode":mode,"grow_size":g.get("size"),"has_points":False}),flush=True)
        # re-run grow storing points: monkey by reading incremental — call grow and force keep
        from src.search.incremental_state import IncrementalIsoscelesFreeSet
        from from_scratch_grow import order_candidates
        rng=random.Random(seed)
        st=IncrementalIsoscelesFreeSet(100)
        for p in order_candidates(100,rng,mode):
            if st.can_add(p)[0]:
                st.add_point(p)
        start=sorted(st.points)
    print(json.dumps({"seed":seed,"mode":mode,"start":len(start)}),flush=True)
    best,meta=lns_exact_run(n=100,initial_points=start,time_budget_s=lsec,seed=5000+seed)
    pts=[tuple(p) for p in best] if best else []
    oka,_=is_legal_pivot_method(pts,100) if pts else (False,None)
    okb,_=verify_independent(pts,100) if pts else (False,None)
    row={"seed":seed,"mode":mode,"start_size":len(start),"final_size":len(pts),"oracle":bool(oka),"indep":bool(okb),"beats_164":len(pts)>164 and oka and okb,"hash":sha256_of_points(pts) if pts else None,"meta":{k:meta.get(k) for k in ("iterations","improvements","best_size","wall_time_s") if isinstance(meta,dict)}}
    rows.append(row)
    print(json.dumps(row),flush=True)
    if row["beats_164"]:
        open(os.path.join(RUN,"CANDIDATES",f"grow_lns_{mode}_s{seed}_legal.json"),"w").write(json.dumps({"points":[list(p) for p in pts],**row},indent=2))
        break
out={"schema":"w3_grow_lns_v1","rows":rows,"best_final":max((r["final_size"] for r in rows),default=0),"wall_s":time.time()-t0}
json.dump(out, open(os.path.join(exp,"summary.json"),"w"), indent=2)
print(json.dumps(out,indent=2),flush=True)
