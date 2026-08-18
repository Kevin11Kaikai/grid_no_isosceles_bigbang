"""Fixed-K simulated annealing for maximum isosceles-free sets in [n] x [m].
State: K points. Energy E = sum over apex i, radius r of C(cnt[i,r],2)  (=# isosceles pairs).
E=0  <=>  isosceles-free.  Exact integer arithmetic throughout."""
import numpy as np, math, time, json, os, random

class Ann:
    def __init__(self,n,m,K,rng,forbid=None,allow=None,start=None):
        self.n=n; self.m=m; self.K=K; self.rng=rng
        self.R=(n-1)**2+(m-1)**2
        pts=np.array([(x,y) for x in range(n) for y in range(m)],np.int64)
        if allow is not None:
            keep=np.array([i for i,p in enumerate(pts) if tuple(p) in allow])
            pts=pts[keep]
        self.P=pts; self.N=len(pts)
        if start is not None:
            idmap={tuple(map(int,p)):i for i,p in enumerate(pts)}
            base=[idmap[tuple(p)] for p in start if tuple(p) in idmap]
            base=base[:K]
            rest=[i for i in range(self.N) if i not in set(base)]
            extra=list(rng.choice(rest,size=K-len(base),replace=False)) if K>len(base) else []
            self.S=np.array(base+[int(e) for e in extra],np.int64)
        else:
            self.S=rng.choice(self.N,size=K,replace=False)      # slot -> point index
        self.cnt=np.zeros((K,self.R+2),np.int32)
        self.inS=np.zeros(self.N,bool); self.inS[self.S]=True
        self._rebuild()
    def _d(self,ai,bi):
        A=self.P[ai]; B=self.P[bi]
        return (A[...,0]-B[...,0])**2+(A[...,1]-B[...,1])**2
    def _rebuild(self):
        K=self.K; self.cnt[:]=0
        C=self.P[self.S]
        D=(C[:,None,0]-C[None,:,0])**2+(C[:,None,1]-C[None,:,1])**2
        self.D=D
        for i in range(K):
            row=np.delete(D[i],i)
            np.add.at(self.cnt[i],row,1)
        self.E=int(np.sum(self.cnt.astype(np.int64)*(self.cnt-1)//2))
    def energy_check(self):
        C=self.P[self.S]
        D=(C[:,None,0]-C[None,:,0])**2+(C[:,None,1]-C[None,:,1])**2
        E=0
        for i in range(self.K):
            row=np.delete(D[i],i); u,c=np.unique(row,return_counts=True)
            E+=int(np.sum(c*(c-1)//2))
        return E
    def delta_swap(self,s,q):
        """energy change of replacing slot s by point index q. Returns (dE, dvec)."""
        K=self.K; D=self.D
        cur=D[:,s].copy(); cur[s]=-1
        # remove slot s
        dE=0
        idx=np.arange(K)
        mask=idx!=s
        c=self.cnt[idx[mask],cur[mask]]
        dE-= int(np.sum(c-1))
        dE-= int(np.sum(self.cnt[s].astype(np.int64)*(self.cnt[s]-1)//2))
        # add q at slot s
        C=self.P[self.S]; Q=self.P[q]
        dv=(C[:,0]-Q[0])**2+(C[:,1]-Q[1])**2
        dv[s]=-1
        # counts after removal
        c2=self.cnt[idx[mask],dv[mask]].copy()
        # correct for the removal we just did on the same (i,r) cells
        same=(dv[mask]==cur[mask])
        c2=c2-same.astype(np.int32)
        dE+= int(np.sum(c2))
        # new row for q
        row=dv[mask]
        u,cc=np.unique(row,return_counts=True)
        dE+= int(np.sum(cc.astype(np.int64)*(cc-1)//2))
        return dE,dv
    def apply(self,s,q,dv,dE):
        K=self.K; idx=np.arange(K); mask=idx!=s
        cur=self.D[:,s].copy(); cur[s]=-1
        np.add.at(self.cnt,(idx[mask],cur[mask]),-1)
        self.cnt[s]=0
        np.add.at(self.cnt,(idx[mask],dv[mask]),1)
        row=dv[mask]
        np.add.at(self.cnt[s],row,1)
        self.inS[self.S[s]]=False; self.S[s]=q; self.inS[q]=True
        self.D[:,s]=dv; self.D[s,:]=dv; self.D[s,s]=0
        self.E+=dE
    def run(self,T0,T1,steps,tl=None):
        rng=self.rng; t0=time.time()
        for t in range(steps):
            if self.E==0: return True
            T=T0*(T1/T0)**(t/steps)
            s=int(rng.integers(self.K))
            q=int(rng.integers(self.N))
            if self.inS[q]: continue
            dE,dv=self.delta_swap(s,q)
            if dE<=0 or rng.random()<math.exp(-dE/T):
                self.apply(s,q,dv,dE)
            if tl and (t&1023)==0 and time.time()-t0>tl: break
        return self.E==0

def solve(n,m=None,K0=None,tl=20.0,seed=0,allow=None,verbose=False,start=None):
    """Ladder search: warm-start each K from the previous solution."""
    m=n if m is None else m
    rng=np.random.default_rng(seed)
    from fastdk import greedy
    best=list(start) if start else None
    if best is None:
        for s_ in range(8):
            p=greedy(max(n,m),1,None,seed=seed*97+s_)
            p=[q for q in p if q[0]<n and q[1]<m]
            if allow is not None: p=[q for q in p if q in allow]
            if best is None or len(p)>len(best): best=p
    K=len(best)+1
    t0=time.time()
    while time.time()-t0<tl:
        rem=tl-(time.time()-t0)
        per=min(max(rem/3.0,2.0), 45.0)
        ok=False
        for attempt in range(4):
            if time.time()-t0>tl: break
            st = best if attempt<2 else None
            a=Ann(n,m,K,rng,allow=allow,start=st)
            if a.run(0.9 if attempt<2 else 1.8, 0.015, 10**9, tl=per/2):
                ok=True; break
        if ok:
            assert a.energy_check()==0
            best=[tuple(map(int,p)) for p in a.P[a.S]]
            if verbose: print(f"  n={n}x{m} K={K} OK  t={time.time()-t0:.0f}s",flush=True)
            K+=1
        else:
            break
    return best, len(best)

if __name__=="__main__":
    import core
    known={8:13,9:16,10:18,11:18,16:28,27:48,32:56}
    for n in [8,9,10,11,16,27,32]:
        S,K=solve(n,tl=45,seed=1,verbose=True)
        ok=core.verify_isofree(S)[0] and core.verify_isofree_ref(S)[0]
        print(f"n={n} found={K} known={known.get(n)} verified={ok}",flush=True)
