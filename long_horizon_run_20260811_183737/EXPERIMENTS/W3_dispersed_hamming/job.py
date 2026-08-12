import json,os,sys,time
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
from data.baselines.official_raw import SOL_100
from src.search.hamming_shell_conflict import hamming_shell_search, universe_hash
from src.search.cpsat_lazy import cpsat_lazy_maximize
from src.verification.oracle_verifier import is_legal_pivot_method
from src.verification_independent.independent_verifier import verify_independent
from src.structures.candidate_io import sha256_of_points

N=100
RUN=r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737"
exp=os.path.join(RUN,"EXPERIMENTS","W3_dispersed_hamming")
os.makedirs(exp,exist_ok=True)
s0=[tuple(p) for p in SOL_100]
s0_set=set(s0)

def ring(p):
    x,y=p
    return min(x,y,N-1-x,N-1-y)

# Dispersed Rem: every stride-th point in S0 sorted by (x+y,x)
ordered=sorted(s0, key=lambda p:(p[0]+p[1],p[0],p[1]))
rows=[]
t0=time.time()
for stride,k,add_n in ((5,28,450),(7,24,450),(3,40,600)):
    rem=ordered[::stride][:k]
    # Add: empties with largest min-dist to Rem union fixed? simple: outer rings + corners
    add=[]
    for x in range(N):
        for y in range(N):
            p=(x,y)
            if p in s0_set: continue
            if ring(p)>=6:
                add.append(p)
    add=sorted(add, key=lambda p:(-ring(p),p))[:add_n]
    u_id=f"U_disp_str{stride}_k{k}_Add_outer{add_n}_r2"
    uh=universe_hash(rem,add)
    print(json.dumps({"start":u_id,"rem":len(rem),"add":len(add)}),flush=True)
    res=hamming_shell_search(n=N,s0=s0,removable=rem,addable=add,r=2,time_budget_s=100.0,seed=7,u_id=u_id,universe_hash_str=uh,per_round_time_limit_s=20.0)
    row={"u_id":u_id,"status":res.status,"rem":len(rem),"add":len(add),"uh":uh,"meta":{kk:res.meta.get(kk) for kk in ("rounds","wall_time_s") if isinstance(res.meta,dict)}}
    if res.points:
        oka,_=is_legal_pivot_method([tuple(p) for p in res.points],N)
        okb,_=verify_independent([tuple(p) for p in res.points],N)
        row["dual"]={"oracle":bool(oka),"indep":bool(okb),"size":len(res.points),"hash":sha256_of_points([tuple(p) for p in res.points])}
        open(os.path.join(RUN,"CANDIDATES",f"{u_id}_legal.json"),"w").write(json.dumps({"points":[list(p) for p in res.points],**row},indent=2))
    json.dump(row, open(os.path.join(exp,f"{u_id}.json"),"w"), indent=2)
    rows.append(row)
    print(json.dumps(row),flush=True)
    if res.points: break
summary={"schema":"w3_dispersed_hamming_v1","rows":rows,"any_feas":any(r["status"] in ("FEASIBLE","FEASIBLE_LEGAL") for r in rows),"wall_s":time.time()-t0}
json.dump(summary, open(os.path.join(exp,"summary.json"),"w"), indent=2)
print(json.dumps(summary,indent=2),flush=True)
