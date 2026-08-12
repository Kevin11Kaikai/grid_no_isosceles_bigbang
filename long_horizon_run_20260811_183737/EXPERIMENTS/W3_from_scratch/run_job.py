import json,os,sys,time,random
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
from data.baselines.official_raw import SOL_100
from src.search.incremental_state import IncrementalIsoscelesFreeSet
from src.search.lns_exact_repair import lns_exact_run
from src.structures.candidate_io import sha256_of_points
from src.verification.oracle_verifier import is_legal_pivot_method
from src.verification_independent.independent_verifier import verify_independent

def build(seed, keep_frac=0.0, ring_bias=True):
    rng=random.Random(seed)
    st=IncrementalIsoscelesFreeSet(100)
    if keep_frac>0:
        s0=[tuple(p) for p in SOL_100]
        for p in rng.sample(s0, int(len(s0)*keep_frac)):
            st.add_point(p)
    cells=[(x,y) for x in range(100) for y in range(100) if (x,y) not in set(st.points)]
    def key(p):
        rd=min(p[0],p[1],99-p[0],99-p[1])
        return (abs(rd-12) if ring_bias else 0, rng.random())
    cells.sort(key=key)
    for p in cells:
        if st.can_add(p)[0]:
            st.add_point(p)
    return sorted(st.points)

rows=[]
exp=r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\EXPERIMENTS\W3_from_scratch"
for seed,frac,bias,budget in [(91,0.0,True,600),(92,0.25,True,600),(93,0.0,False,600),(94,0.35,False,900)]:
    start=build(seed,frac,bias)
    print(json.dumps({"seed":seed,"start":len(start),"frac":frac,"bias":bias}),flush=True)
    best,meta=lns_exact_run(n=100,initial_points=start,time_budget_s=budget,seed=seed)
    pts=[tuple(p) for p in best] if best else []
    oka,_=is_legal_pivot_method(pts,100) if pts else (False,None)
    okb,_=verify_independent(pts,100) if pts else (False,None)
    row={"seed":seed,"keep_frac":frac,"ring_bias":bias,"start_size":len(start),"final_size":len(pts),"oracle":bool(oka),"indep":bool(okb),"beats_164":len(pts)>164 and oka and okb,"meta":{k:meta.get(k) for k in ("iterations","improvements","best_size","wall_time_s") if isinstance(meta,dict)}}
    rows.append(row)
    print(json.dumps(row),flush=True)
    if row["beats_164"]:
        open(os.path.join(r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\CANDIDATES",f"from_scratch_s{seed}_legal.json"),"w",encoding="utf-8").write(json.dumps({"points":[list(p) for p in pts],**row},indent=2))
        break
open(os.path.join(exp,"summary.json"),"w",encoding="utf-8").write(json.dumps({"schema":"w3_from_scratch_v1","rows":rows},indent=2)+"\n")
print("done",flush=True)
