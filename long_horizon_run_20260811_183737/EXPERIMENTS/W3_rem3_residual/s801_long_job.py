import json,os,sys,time
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\SCRATCH")
from w3_rem3_exact_residual import make_elite, soft_core, addable_pool, exact_extend, dual
RUN=r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737"
exp=os.path.join(RUN,"EXPERIMENTS","W3_rem3_residual")
elite_path=os.path.join(exp,"elite_s801_V45.json")
if os.path.exists(elite_path):
    elite=json.load(open(elite_path,encoding="utf-8"))
else:
    elite=make_elite(801, 120.0, r_min=3)
    json.dump(elite, open(elite_path,"w"), indent=2)
pts=[tuple(p) for p in elite["points"]]
core, involved, nw = soft_core(pts)
pool=addable_pool(core)
print(json.dumps({"core":len(core),"free":len(pool),"need":165-len(core),"witnesses":nw}),flush=True)
a=exact_extend(core, pool, 1800.0, tag="soft_s801_long", workers=8)
json.dump({k:v for k,v in a.items() if k!="points"}, open(os.path.join(exp,"soft_extend_s801_long.json"),"w"), indent=2)
print(json.dumps({k:v for k,v in a.items() if k!="points"},indent=2),flush=True)
if a.get("status")=="FEASIBLE_LEGAL" and a.get("points"):
    open(os.path.join(RUN,"CANDIDATES","rem3_soft_s801_long_legal.json"),"w").write(json.dumps(a,indent=2))
