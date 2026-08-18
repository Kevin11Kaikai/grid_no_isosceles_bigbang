"""Barrier (e): D(1,R) -- degree<=1 only for squared distances r <= R."""
import numpy as np, math, json, os, time
from fastdk import greedy, verify
SD=os.path.join(os.path.dirname(os.path.abspath(__file__)),"sets")
print(f"{'n':>5} {'R':>8} {'size':>8} {'size/n^2':>10} {'pred n^2/(2*sqrt(2R lnR))':>26} {'ratio':>7}",flush=True)
rows=[]
for n in [64,128,256]:
    Rmax=2*(n-1)**2
    Rs=[1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536,131072]
    Rs=[r for r in Rs if r<=Rmax]+[Rmax]
    for R in Rs:
        tries=6 if n<=128 else 2
        best=[]
        for s in range(tries):
            p=greedy(n,1,R,seed=7*s+R%97)
            if len(p)>len(best): best=p
        ok,w=verify(best,1,R,n); assert ok,(n,R,w)
        pred=n*n/(2*math.sqrt(2*R*max(math.log(max(R,3)),1)))
        print(f"{n:>5} {R:>8} {len(best):>8} {len(best)/n**2:10.4f} {pred:26.1f} {len(best)/pred:7.2f}",flush=True)
        rows.append(dict(n=n,R=R,size=len(best)))
        json.dump(dict(name=f"e_n{n}_R{R}",n=n,R=R,k=1,size=len(best),
                  status="VERIFIED_COMPUTATIONAL_RESULT",points=sorted(map(list,best))),
                  open(os.path.join(SD,f"e_n{n}_R{R}.json"),"w"))
json.dump(rows,open(os.path.join(SD,"barrier_e_summary.json"),"w"),indent=1)
