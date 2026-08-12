import json,os,sys,time
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang")
sys.path.insert(0,r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737\SCRATCH")
from from_scratch_grow import grow
RUN=r"d:\others\grid_no_isosceles_bigbang\long_horizon_run_20260811_183737"
exp=os.path.join(RUN,"EXPERIMENTS","W3_from_scratch")
os.makedirs(exp,exist_ok=True)
rows=[]; t0=time.time()
for mode in ("boundary_first","spiral_mix","random","center_first"):
    for seed in (201,202,203):
        r=grow(100, seed, mode, seconds=180.0)
        row={k:v for k,v in r.items() if k!="points"}
        rows.append(row)
        print(json.dumps(row), flush=True)
        if r.get("size",0)>=165 and r.get("V",1)==0:
            open(os.path.join(RUN,"CANDIDATES",f"grow_{mode}_s{seed}.json"),"w").write(json.dumps(r,indent=2))
            break
    else:
        continue
    break
best=max(rows, key=lambda r: r.get("size",0))
out={"schema":"w3_from_scratch_grow_v3","rows":rows,"best_size":best.get("size"),"best":best,"wall_s":time.time()-t0}
path=os.path.join(exp,"grow_v3.json")
json.dump(out, open(path,"w"), indent=2); open(path,"a").write("\n")
print(json.dumps({"done":True,"best_size":out["best_size"]},indent=2), flush=True)
