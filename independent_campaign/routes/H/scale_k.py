import numpy as np, json, os, sys, time, math
from fastdk import greedy, verify
SD=os.path.join(os.path.dirname(os.path.abspath(__file__)),"sets")
ns=[8,11,16,22,32,45,64,90,128,181,256,362]
res={}
for k in [1,2,3]:
    for n in ns:
        if k>=2 and n>256: continue
        if k==3 and n>181: continue
        t0=time.time(); best=[]; tries = 12 if n<=64 else (5 if n<=181 else 2)
        for s in range(tries):
            p=greedy(n,k,None,seed=1000*k+s)
            if len(p)>len(best): best=p
        ok,w=verify(best,k,None,n)
        assert ok,(k,n,w)
        res[(k,n)]=len(best)
        print(f"k={k} n={n:4d} size={len(best):6d}  n^2={n*n:8d}  size/n^{{2-2/(k+1)}}={len(best)/n**(2-2/(k+1)):8.3f}  t={time.time()-t0:.1f}s",flush=True)
        json.dump(dict(name=f"deg{k}_n{n}",n=n,k=k,size=len(best),
                       status="VERIFIED_COMPUTATIONAL_RESULT",
                       note=f"random greedy, D({k},inf), verified",points=sorted(map(list,best))),
                  open(os.path.join(SD,f"deg{k}_n{n}.json"),"w"))
json.dump({f"{k}_{n}":v for (k,n),v in res.items()},open(os.path.join(SD,"degk_summary.json"),"w"),indent=1)
