"""Ruin-and-recreate search for maximum isosceles-free sets. Exact integer arithmetic."""
import numpy as np, time, json, os, sys
from fastdk import DkGreedy, verify

def build(n,m,pts,allow=None):
    g=DkGreedy(max(n,m),1,None)
    for p in pts: 
        ok=g.try_add(p[0],p[1]); assert ok, p
    return g

def rr(n,m=None,tl=30.0,seed=0,start=None,allow=None,verbose=False):
    m=n if m is None else m
    rng=np.random.default_rng(seed)
    if allow is None:
        cands=[(x,y) for x in range(n) for y in range(m)]
    else:
        cands=[tuple(p) for p in allow]
    C=np.array(cands,np.int64)
    S=[tuple(p) for p in (start or [])]
    if not S:
        g=DkGreedy(max(n,m),1,None)
        for i in rng.permutation(len(C)): g.try_add(int(C[i][0]),int(C[i][1]))
        S=list(g.pts)
    best=list(S); t0=time.time(); it=0
    while time.time()-t0<tl:
        it+=1
        k=len(S)
        r=int(rng.integers(1,max(2,k//6)+1))
        if rng.random()<0.35:
            # spatial ruin: remove all points near a random centre
            c=C[int(rng.integers(len(C)))]
            d=np.array([(p[0]-c[0])**2+(p[1]-c[1])**2 for p in S])
            keep=np.argsort(d)[r:]
            S2=[S[i] for i in sorted(keep)]
        else:
            drop=set(rng.choice(k,size=min(r,k),replace=False).tolist())
            S2=[p for i,p in enumerate(S) if i not in drop]
        g=DkGreedy(max(n,m),1,None)
        for p in S2: g.try_add(p[0],p[1])
        for i in rng.permutation(len(C)):
            g.try_add(int(C[i][0]),int(C[i][1]))
        S2=list(g.pts)
        if len(S2)>len(S) or (len(S2)==len(S) and rng.random()<0.6):
            S=S2
        if len(S)>len(best):
            best=list(S)
            if verbose: print(f"    {n}x{m} -> {len(best)}  (it {it}, t={time.time()-t0:.0f}s)",flush=True)
    return best

if __name__=="__main__":
    import core
    known={8:13,9:16,10:18,11:18,16:28,27:48,32:56}
    tl=float(sys.argv[1]) if len(sys.argv)>1 else 25.0
    for n in [8,9,10,11,16,27,32]:
        S=rr(n,tl=tl,seed=n)
        ok=core.verify_isofree(S)[0] and core.verify_isofree_ref(S)[0]
        k=known.get(n)
        print(f"n={n:3d} RR={len(S):4d} known={k}  gap={k-len(S) if k else '-'}  verified={ok}",flush=True)
