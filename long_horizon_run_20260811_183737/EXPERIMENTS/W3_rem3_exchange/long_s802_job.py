import json,os,sys,time
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\SCRATCH")
from fixedcard_forced_exchange import run_seed
exp=r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\EXPERIMENTS\W3_rem3_exchange"
os.makedirs(exp,exist_ok=True)
r=run_seed(802, seconds=900.0, r_min=3)
out={k:v for k,v in r.items() if k!="points"}
open(os.path.join(exp,"rem3_long_s802.json"),"w",encoding="utf-8").write(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2),flush=True)
if r.get("status")=="V0_LEGAL" and r.get("points"):
    open(os.path.join(r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\CANDIDATES","rem3_long_s802_legal.json"),"w",encoding="utf-8").write(json.dumps(r,indent=2))
