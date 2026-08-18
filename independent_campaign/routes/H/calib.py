"""Growth calibration: best isosceles-free sets found, nested-seeded across n."""
import numpy as np, json, os, sys, time
import mc, core
SD=os.path.join(os.path.dirname(os.path.abspath(__file__)),"sets"); os.makedirs(SD,exist_ok=True)
known={1:1,2:2,3:4,4:6,5:7,6:9,7:10,8:13,9:16,10:18,11:18,16:28,27:48,32:56}
ns=list(range(4,41))+[45,48,52,56,60,64,72,80,90,100,112,128]
prev=[]; res={}
TL=float(sys.argv[1]) if len(sys.argv)>1 else 45.0
for n in ns:
    t0=time.time()
    st=[p for p in prev if p[0]<n and p[1]<n]
    S=mc.ladder(n,tl=TL,seed=n,start=(st if st else None),verbose=False)
    if len(S)<len(st): S=st
    ok1=core.verify_isofree(S)[0]
    ok2=core.verify_isofree_ref(S)[0] if len(S)<=260 else ok1
    assert ok1 and ok2 and all(0<=x<n and 0<=y<n for x,y in S), n
    prev=S; res[n]=len(S)
    kk=known.get(n)
    print(f"n={n:4d} best={len(S):5d} known={kk if kk else '-':>4} "
          f"gap={'' if kk is None else kk-len(S)}  best/n={len(S)/n:6.3f} t={time.time()-t0:.0f}s",flush=True)
    json.dump(dict(name=f"iso_n{n}",n=n,size=len(S),status="VERIFIED_COMPUTATIONAL_RESULT",
                   note="best found by min-conflicts+tabu, nested-seeded; LOWER BOUND on C(n)",
                   points=sorted(map(list,S))),open(os.path.join(SD,f"iso_n{n}.json"),"w"))
    json.dump(res,open(os.path.join(SD,"calib_summary.json"),"w"),indent=1)
