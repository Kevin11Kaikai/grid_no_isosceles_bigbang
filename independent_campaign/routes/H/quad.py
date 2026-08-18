"""Anti-recurrence stress test: isosceles-free S in [2n]^2 with EXACTLY t points in each
of the four n x n quadrants.  Ladder t upward.  Compares 4t against C(2n) and t vs C(n)."""
import numpy as np, time, json, os, sys
import mc, core
SD=os.path.join(os.path.dirname(os.path.abspath(__file__)),"sets")

class QMC(mc.MC):
    """slot-quadrant-constrained: replacement candidates must lie in the slot's quadrant"""
    def __init__(self,n2,K,rng,quad_of_slot,quad_pts):
        super().__init__(n2,n2,K,rng)
        self.qs=quad_of_slot; self.qp=quad_pts
    def init(self,start=None):
        K=self.K; rng=self.rng
        idm={tuple(map(int,p)):i for i,p in enumerate(self.P)}
        S=np.zeros(K,np.int64); used=set()
        base={}
        if start:
            for p in start:
                q=self._q(p)
                base.setdefault(q,[]).append(idm[tuple(p)])
        for s in range(K):
            q=self.qs[s]; pool=self.qp[q]
            got=None
            if base.get(q):
                cand=base[q].pop()
                if cand not in used: got=cand
            while got is None:
                c=int(rng.choice(pool))
                if c not in used: got=c
            S[s]=got; used.add(got)
        self.S=S; self._rebuild()
    def _q(self,p):
        h=self.n//2
        return (0 if p[0]<h else 1)*2+(0 if p[1]<h else 1)
    def step(self,batch,tstep):
        K=self.K; rng=self.rng
        w=self.slot_conflicts()
        if w.sum()==0: return
        s=int(rng.choice(K,p=w/w.sum()))
        ii=np.array([i for i in range(K) if i!=s],np.int64)
        cur=self.D[ii,s]
        cnt2=self.cnt.copy(); np.add.at(cnt2,(ii,cur),-1); cnt2[s]=0
        dE_rem=-int(np.sum(self.cnt[ii,cur]-1))-int(np.sum(self.cnt[s].astype(np.int64)*(self.cnt[s]-1)//2))
        E2=self.E+dE_rem
        pool=self.qp[self.qs[s]]
        cand=rng.choice(pool,size=min(batch,len(pool)),replace=False)
        inS=np.zeros(self.N,bool); inS[self.S]=True
        cand=cand[~inS[cand]]
        if len(cand)==0: return
        Mx=self.P[self.S[ii],0]; My=self.P[self.S[ii],1]
        DV=(self.P[cand,0][:,None]-Mx[None,:])**2+(self.P[cand,1][:,None]-My[None,:])**2
        t1=cnt2[ii[None,:],DV].sum(axis=1)
        SS=np.sort(DV,axis=1); eq=np.zeros(SS.shape,bool); eq[:,1:]=SS[:,1:]==SS[:,:-1]
        ar=np.arange(SS.shape[1]); st=np.where(eq,0,ar[None,:]); st=np.maximum.accumulate(st,axis=1)
        t2=(ar[None,:]-st).sum(axis=1)
        newE=E2+t1+t2
        pen=np.where(self.tabu[cand]>tstep,10**6,0)
        sc=newE+pen; mn=sc.min()
        ties=np.nonzero(sc<=mn+(1 if rng.random()<0.25 else 0))[0]
        j=int(rng.choice(ties)); q=int(cand[j])
        self.tabu[self.S[s]]=tstep+int(rng.integers(4,3+2*K))
        np.add.at(self.cnt,(ii,cur),-1); self.cnt[s]=0
        Q=self.P[q]; dv=(self.P[self.S,0]-Q[0])**2+(self.P[self.S,1]-Q[1])**2
        np.add.at(self.cnt,(ii,dv[ii]),1); np.add.at(self.cnt[s],dv[ii],1)
        self.S[s]=q; dv[s]=0
        self.D[:,s]=dv; self.D[s,:]=dv; self.D[s,s]=0
        self.E=int(newE[j])

def run(n, tl_per_t=25.0, seed=0):
    n2=2*n
    P=[(x,y) for x in range(n2) for y in range(n2)]
    idx={p:i for i,p in enumerate(P)}
    qp=[[],[],[],[]]
    for p in P: qp[(0 if p[0]<n else 1)*2+(0 if p[1]<n else 1)].append(idx[p])
    qp=[np.array(a,np.int64) for a in qp]
    rng=np.random.default_rng(seed)
    best_t=0; bestS=None; t=1; start=None
    while True:
        K=4*t
        qs=[i//t for i in range(K)]
        ok=None
        for att in range(3):
            m=QMC(n2,K,rng,qs,qp)
            r=m.solve(tl_per_t,batch=1024,start=(bestS if att<2 else None))
            if r: ok=r;break
        if ok is None: break
        assert core.verify_isofree(ok)[0]
        cs=[0,0,0,0]
        for p in ok: cs[(0 if p[0]<n else 1)*2+(0 if p[1]<n else 1)]+=1
        assert cs==[t]*4, cs
        best_t=t; bestS=ok; t+=1
    return best_t,bestS

if __name__=="__main__":
    known={3:4,4:6,5:7,6:9,7:10,8:13,9:16,10:18,11:18,16:28,27:48,32:56}
    for n in [4,5,6,8,11,16]:
        t0=time.time()
        t,S=run(n,tl_per_t=float(sys.argv[1]) if len(sys.argv)>1 else 20.0,seed=n)
        Cn=known.get(n); C2n=known.get(2*n)
        print(f"n={n:3d} -> 2n={2*n:3d}: max simultaneous t={t}  total 4t={4*t}  "
              f"C(n)={Cn} C(2n)={C2n}  t/C(n)={t/Cn:.3f}  "
              f"ceiling t<=C(2n)/4={'%.2f'%(C2n/4) if C2n else '?'}",flush=True)
        if S: json.dump(dict(name=f"quad_n{n}",n=2*n,size=len(S),t_per_quadrant=t,
              status="VERIFIED_COMPUTATIONAL_RESULT",points=sorted(map(list,S))),
              open(os.path.join(SD,f"quad_2n{2*n}.json"),"w"))
