import json,os,sys,time,random
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\SCRATCH")
from pattern_constructions import legalize, pattern_annulus, pattern_checker_thick, pattern_diag_bands
from src.search.lns_exact_repair import lns_exact_run
from src.verification.oracle_verifier import is_legal_pivot_method
from src.verification_independent.independent_verifier import verify_independent
from src.structures.candidate_io import sha256_of_points
from src.search.incremental_state import IncrementalIsoscelesFreeSet

RUN=r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737"
exp=os.path.join(RUN,"EXPERIMENTS","W3_pattern_lns")
n=100
specs=[
 ("annulus",{"r0":2,"r1":8},pattern_annulus(n,2,8)),
 ("checker",{"period":5,"phase":1},pattern_checker_thick(n,5,1)),
 ("checker",{"period":4,"phase":1},pattern_checker_thick(n,4,1)),
 ("diag",{"width":2},pattern_diag_bands(n,2)),
 ("annulus",{"r0":4,"r1":12},pattern_annulus(n,4,12)),
]
rows=[]; t0=time.time()
for rank,(kind,params,cells) in enumerate(specs):
    rng=random.Random(7000+rank)
    order=list(cells); rng.shuffle(order)
    st=IncrementalIsoscelesFreeSet(n)
    for p in order:
        if st.can_add(p)[0]: st.add_point(p)
    # quick improve
    r=legalize(n,cells,seconds=30.0,seed=7100+rank)
    start=sorted(st.points)
    if r.get("size",0)>len(start):
        # rebuild best from legalize if points missing
        st2=IncrementalIsoscelesFreeSet(n); order2=list(cells); random.Random(7200+rank).shuffle(order2)
        for p in order2:
            if st2.can_add(p)[0]: st2.add_point(p)
        if len(st2.points)>len(start): start=sorted(st2.points)
    print(json.dumps({"rank":rank,"kind":kind,"params":params,"start":len(start)}),flush=True)
    best,meta=lns_exact_run(n=n,initial_points=start,time_budget_s=600.0,seed=8000+rank)
    pts=[tuple(p) for p in best] if best else []
    oka,_=is_legal_pivot_method(pts,n) if pts else (False,None)
    okb,_=verify_independent(pts,n) if pts else (False,None)
    row={"rank":rank,"kind":kind,"params":params,"start_size":len(start),"final_size":len(pts),"oracle":bool(oka),"indep":bool(okb),"beats_164":len(pts)>164 and oka and okb,"hash":sha256_of_points(pts) if pts else None,"meta":{k:meta.get(k) for k in ("iterations","improvements","best_size","wall_time_s") if isinstance(meta,dict)}}
    rows.append(row); print(json.dumps(row),flush=True)
    if row["beats_164"]:
        open(os.path.join(RUN,"CANDIDATES",f"pattern_lns2_{kind}_r{rank}.json"),"w").write(json.dumps({"points":[list(p) for p in pts],**row},indent=2)); break
out={"schema":"w3_pattern_lns_v2","rows":rows,"best_final":max((r["final_size"] for r in rows),default=0),"wall_s":time.time()-t0}
json.dump(out, open(os.path.join(exp,"summary_v2.json"),"w"), indent=2)
print(json.dumps(out,indent=2),flush=True)
