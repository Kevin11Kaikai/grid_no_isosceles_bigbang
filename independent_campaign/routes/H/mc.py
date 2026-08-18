"""Vectorised min-conflicts + tabu search for maximum isosceles-free sets.
Fixed K.  Energy E = #{(apex b, unordered pair {p,q}) : |p-b|^2=|q-b|^2}.  E=0 <=> valid.
Move: pick a conflicted slot s, evaluate a large batch of replacement candidates
simultaneously with exact integer arithmetic, take the best non-tabu one."""
import numpy as np, time, math, json, os

class MC:
    def __init__(self,n,m,K,rng,allow=None):
        self.n=n;self.m=m;self.K=K;self.rng=rng
        P=np.array([(x,y) for x in range(n) for y in range(m)],np.int64)
        if allow is not None:
            A=set(map(tuple,allow)); P=np.array([p for p in P if tuple(p) in A],np.int64)
        self.P=P; self.N=len(P); self.R=(n-1)**2+(m-1)**2
        self.tabu=np.zeros(self.N,np.int64)
    def init(self,start=None):
        K=self.K; rng=self.rng
        if start is not None and len(start):
            idm={tuple(map(int,p)):i for i,p in enumerate(self.P)}
            base=[idm[tuple(p)] for p in start if tuple(p) in idm][:K]
        else: base=[]
        rest=np.setdiff1d(np.arange(self.N),np.array(base,np.int64))
        extra=rng.choice(rest,size=K-len(base),replace=False) if K>len(base) else np.zeros(0,np.int64)
        self.S=np.concatenate([np.array(base,np.int64),extra.astype(np.int64)])
        self._rebuild()
    def _rebuild(self):
        C=self.P[self.S]; K=self.K
        self.D=(C[:,None,0]-C[None,:,0])**2+(C[:,None,1]-C[None,:,1])**2
        self.cnt=np.zeros((K,self.R+2),np.int32)
        for i in range(K):
            row=np.delete(self.D[i],i); np.add.at(self.cnt[i],row,1)
        self.E=int(np.sum(self.cnt.astype(np.int64)*(self.cnt-1)//2))
    def energy_check(self):
        C=self.P[self.S]
        D=(C[:,None,0]-C[None,:,0])**2+(C[:,None,1]-C[None,:,1])**2
        E=0
        for i in range(self.K):
            row=np.delete(D[i],i); u,c=np.unique(row,return_counts=True); E+=int(np.sum(c*(c-1)//2))
        return E
    def slot_conflicts(self):
        """per-slot conflict load: contributions where the slot is an apex or a member."""
        K=self.K; w=np.zeros(K,np.int64)
        cs=(self.cnt.astype(np.int64)*(self.cnt-1)//2).sum(axis=1)
        w+=cs
        for i in range(K):
            row=self.D[i].copy(); row[i]=-1
            c=self.cnt[i][row]; c[i]=0
            w+= (c>=2).astype(np.int64)*0 + (c-1).clip(0)   # member load
        return w
    def step(self,batch,tstep):
        K=self.K; rng=self.rng
        w=self.slot_conflicts()
        if w.sum()==0: return
        s=int(rng.choice(K,p=w/w.sum()))
        ii=np.array([i for i in range(K) if i!=s],np.int64)
        cur=self.D[ii,s]
        cnt2=self.cnt.copy()
        np.add.at(cnt2,(ii,cur),-1); cnt2[s]=0
        dE_rem = -int(np.sum(self.cnt[ii,cur]-1)) - int(np.sum(self.cnt[s].astype(np.int64)*(self.cnt[s]-1)//2))
        E2=self.E+dE_rem
        cand=rng.choice(self.N,size=min(batch,self.N),replace=False)
        inS=np.zeros(self.N,bool); inS[self.S]=True
        cand=cand[~inS[cand]]
        if len(cand)==0: return
        Mx=self.P[self.S[ii],0]; My=self.P[self.S[ii],1]
        Qx=self.P[cand,0][:,None]; Qy=self.P[cand,1][:,None]
        DV=(Qx-Mx[None,:])**2+(Qy-My[None,:])**2
        t1=cnt2[ii[None,:],DV].sum(axis=1)
        SS=np.sort(DV,axis=1)
        eq=np.zeros(SS.shape,bool); eq[:,1:]=SS[:,1:]==SS[:,:-1]
        ar=np.arange(SS.shape[1])
        st=np.where(eq,0,ar[None,:]); st=np.maximum.accumulate(st,axis=1)
        t2=(ar[None,:]-st).sum(axis=1)
        newE=E2+t1+t2
        pen=np.where(self.tabu[cand]>tstep, 10**6, 0)
        sc=newE+pen
        mn=sc.min()
        ties=np.nonzero(sc<=mn+(1 if rng.random()<0.25 else 0))[0]
        j=int(rng.choice(ties))
        q=int(cand[j])
        self.tabu[self.S[s]]=tstep+int(rng.integers(4,3+2*K))
        # apply
        np.add.at(self.cnt,(ii,cur),-1); self.cnt[s]=0
        Q=self.P[q]; dv=(self.P[self.S,0]-Q[0])**2+(self.P[self.S,1]-Q[1])**2
        dvi=dv[ii]
        np.add.at(self.cnt,(ii,dvi),1)
        np.add.at(self.cnt[s],dvi,1)
        self.S[s]=q
        dv[s]=0
        self.D[:,s]=dv; self.D[s,:]=dv; self.D[s,s]=0
        self.E=int(newE[j])
    def solve(self,tl,batch=768,start=None,restarts=6):
        t0=time.time(); t=0
        for r in range(restarts):
            self.init(start if r<2 else None); self.tabu[:]=0
            best=self.E; stall=0
            while time.time()-t0<tl:
                for _ in range(40):
                    t+=1; self.step(batch,t)
                    if self.E==0:
                        assert self.energy_check()==0
                        return [tuple(map(int,p)) for p in self.P[self.S]]
                if self.E<best: best=self.E; stall=0
                else:
                    stall+=1
                    if stall>150: break
            if time.time()-t0>=tl: break
        return None

def ladder(n,m=None,tl=60.0,seed=0,start=None,allow=None,verbose=False,K0=None):
    m=n if m is None else m
    rng=np.random.default_rng(seed)
    if start is None:
        from fastdk import greedy
        best=[]
        for s in range(6):
            p=greedy(max(n,m),1,None,seed=seed*131+s)
            p=[q for q in p if q[0]<n and q[1]<m]
            if allow is not None:
                A=set(map(tuple,allow)); p=[q for q in p if q in A]
            if len(p)>len(best): best=p
    else: best=list(start)
    K=len(best)+1; t0=time.time()
    while time.time()-t0<tl:
        rem=tl-(time.time()-t0)
        mc=MC(n,m,K,rng,allow=allow)
        r=mc.solve(min(rem,max(6.0,tl/4)),start=best)
        if r is None: break
        best=r
        if verbose: print(f"   {n}x{m} K={K} ok t={time.time()-t0:.0f}s",flush=True)
        K+=1
    return best

if __name__=="__main__":
    import core
    known={8:13,9:16,10:18,11:18,16:28,27:48,32:56}
    for n in [8,9,10,11,16]:
        S=ladder(n,tl=30,seed=1)
        ok=core.verify_isofree(S)[0] and core.verify_isofree_ref(S)[0]
        print(f"n={n} MC={len(S)} known={known.get(n)} verified={ok}",flush=True)
