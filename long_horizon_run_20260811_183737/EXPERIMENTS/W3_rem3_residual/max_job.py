import json,os,sys,time
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
from ortools.sat.python import cp_model
from src.search.incremental_state import IncrementalIsoscelesFreeSet
from src.verification.oracle_verifier import is_legal_pivot_method
from src.verification_independent.independent_verifier import verify_independent
from src.structures.candidate_io import sha256_of_points
from src.verification.conflict_metric import conflict_count
from collections import defaultdict

N=100
RUN=r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737"
exp=os.path.join(RUN,"EXPERIMENTS","W3_rem3_residual")
# wait for elite
elite_path=None
for _ in range(60):
    cands=[p for p in os.listdir(exp) if p.startswith("elite_s802")]
    if cands:
        elite_path=os.path.join(exp,cands[0]); break
    time.sleep(2)
if not elite_path:
    print(json.dumps({"error":"no elite"}),flush=True); raise SystemExit(0)
elite=json.load(open(elite_path,encoding="utf-8"))
pts=[tuple(p) for p in elite["points"]]

def sq(a,b):
    return (a[0]-b[0])**2+(a[1]-b[1])**2

def witnesses(points):
    out=[]
    for pivot in points:
        groups=defaultdict(list)
        for q in points:
            if q==pivot: continue
            groups[sq(pivot,q)].append(q)
        for members in groups.values():
            if len(members)<2: continue
            for i in range(len(members)):
                for j in range(i+1,len(members)):
                    out.append((pivot,members[i],members[j]))
    return out

wits=witnesses(pts)
involved=set()
for a,b,c in wits:
    involved.update((a,b,c))
core=sorted(p for p in pts if p not in involved)
st=IncrementalIsoscelesFreeSet(N)
for p in core:
    assert st.add_point(p)
# free = all empties that individually can_add
free=[]
occ=set(core)
for x in range(N):
    for y in range(N):
        p=(x,y)
        if p in occ: continue
        if st.can_add(p)[0]:
            free.append(p)
print(json.dumps({"core":len(core),"free":len(free),"elite_V":elite["best_V"]}),flush=True)

# maximize |core|+sum free with lazy cuts, budget 20min
t0=time.time(); budget=1200.0
cuts=set(); rounds=0; best_size=len(core); best=None; status="TIMEOUT"
while time.time()-t0 < budget:
    rounds+=1
    model=cp_model.CpModel()
    z={p:model.NewBoolVar(f"z{p[0]}_{p[1]}") for p in free}
    model.Maximize(sum(z.values()))
    for trip in cuts:
        free_in=[z[p] for p in trip if p in z]
        if not free_in: continue
        model.Add(sum(free_in) <= len(free_in)-1)
    solver=cp_model.CpSolver()
    rem=max(0.5, budget-(time.time()-t0))
    solver.parameters.max_time_in_seconds=min(45.0, rem)
    solver.parameters.num_search_workers=8
    solver.parameters.random_seed=4400+rounds
    code=solver.Solve(model)
    if code==cp_model.INFEASIBLE:
        status="INFEASIBLE_SCOPED"; break
    if code not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        status="TIMEOUT"; break
    sel=list(core)+[p for p,v in z.items() if solver.Value(v)==1]
    w=witnesses(sel)
    if not w:
        best=sel; best_size=len(sel); status="FEASIBLE_LEGAL"
        # continue a bit to try larger? already max objective — done
        break
    before=len(cuts)
    for trip in w:
        cuts.add(tuple(sorted(trip)))
    if len(cuts)==before:
        status="TIMEOUT"; break
    if len(sel)>best_size:
        best_size=len(sel)  # illegal size marker only
    if rounds%20==0:
        print(json.dumps({"round":rounds,"cuts":len(cuts),"obj_size":len(sel),"elapsed":time.time()-t0}),flush=True)

out={"schema":"w3_rem3_core_maximize_v1","core":len(core),"free":len(free),"status":status,"rounds":rounds,"cuts":len(cuts),"best_legal_size":len(best) if best else None,"wall_s":time.time()-t0}
if best:
    oka,_=is_legal_pivot_method(best,N); okb,_=verify_independent(best,N)
    out["dual"]={"oracle":bool(oka),"indep":bool(okb),"size":len(best),"V":conflict_count(best,N),"hash":sha256_of_points(best)}
    if len(best)>164 and oka and okb:
        open(os.path.join(RUN,"CANDIDATES","rem3_core_max_s802_legal.json"),"w").write(json.dumps({"points":[list(p) for p in best],**out},indent=2))
json.dump(out, open(os.path.join(exp,"core_maximize_s802.json"),"w"), indent=2)
print(json.dumps(out,indent=2),flush=True)
