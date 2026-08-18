"""Fast greedy for D(k,R): for every b in S and every squared distance r<=R,
   at most k points of S at squared distance r from b.
Maintains, for each point index i and radius r, cnt[(i,r)]; a key (i,r) is SATURATED
when cnt==k.  Candidate q is rejected iff some existing i has (i, |q-p_i|^2) saturated,
or q itself would see some radius > k times.
Lookup is vectorised via searchsorted on a sorted saturated-key array."""
import numpy as np, json, os, sys, time

class DkGreedy:
    def __init__(self, n, k, R=None, M=None):
        self.n=n; self.k=k; self.R=(R if R is not None else 2*(n-1)**2)
        self.M=self.R+2
        self.X=np.zeros(0,np.int64); self.Y=np.zeros(0,np.int64)
        self.cnt={}                 # (i,r) -> count
        self.sat_sorted=np.zeros(0,np.int64)
        self.sat_pend=set()
        self.pts=[]
    def _refresh(self):
        if self.sat_pend:
            self.sat_sorted=np.sort(np.concatenate([self.sat_sorted,
                              np.fromiter(self.sat_pend,np.int64,len(self.sat_pend))]))
            self.sat_pend=set()
    def can_add(self,qx,qy):
        m=len(self.pts)
        if m==0: return True,(np.zeros(0,np.int64),np.zeros(0,bool),np.zeros(0,np.int64),np.zeros(0,np.int64),np.zeros(0,np.int64))
        d=(self.X-qx)**2+(self.Y-qy)**2
        if (d==0).any(): return False,None
        m_in=d<=self.R
        di=d[m_in]
        if len(di):
            # q as apex
            u,c=np.unique(di,return_counts=True)
            if (c>self.k).any(): return False,None
            idx=np.nonzero(m_in)[0]
            keys=idx*self.M+di
            if len(self.sat_sorted):
                pos=np.searchsorted(self.sat_sorted,keys)
                pos=np.minimum(pos,len(self.sat_sorted)-1)
                if (self.sat_sorted[pos]==keys).any(): return False,None
            if self.sat_pend:
                for kk in keys.tolist():
                    if kk in self.sat_pend: return False,None
            return True,(d,m_in,idx,di,keys)
        return True,(d,m_in,np.zeros(0,np.int64),di,np.zeros(0,np.int64))
    def add(self,qx,qy,info=None):
        if info is None:
            ok,info=self.can_add(qx,qy)
            if not ok: return False
        d,m_in,idx,di,keys=info
        j=len(self.pts); M=self.M; k=self.k; cnt=self.cnt
        for i,r,kk in zip(idx.tolist(),di.tolist(),keys.tolist()):
            c=cnt.get(kk,0)+1; cnt[kk]=c
            if c==k: self.sat_pend.add(kk)
            kk2=j*M+r
            c2=cnt.get(kk2,0)+1; cnt[kk2]=c2
            if c2==k: self.sat_pend.add(kk2)
        self.X=np.append(self.X,qx); self.Y=np.append(self.Y,qy)
        self.pts.append((int(qx),int(qy)))
        if len(self.sat_pend)>512: self._refresh()
        return True
    def try_add(self,qx,qy):
        ok,info=self.can_add(qx,qy)
        if ok: self.add(qx,qy,info); return True
        return False

def greedy(n,k,R=None,seed=0,order=None,tl=None):
    g=DkGreedy(n,k,R)
    rng=np.random.default_rng(seed)
    if order is None:
        order=np.arange(n*n); rng.shuffle(order)
    t0=time.time()
    for t in order:
        g.try_add(int(t//n), int(t%n))
        if tl and time.time()-t0>tl: break
    return g.pts

# ---------------- independent verifier (numpy, fresh logic) ----------------
def verify(pts,k,R=None,n=None):
    P=np.array(sorted(map(tuple,pts)),np.int64)
    if len(set(map(tuple,pts)))!=len(pts): return False,"dupes"
    if n is not None and ((P<0).any() or (P>=n).any()): return False,"outofbox"
    RR = R if R is not None else 10**18
    for j in range(len(P)):
        d=(P[:,0]-P[j,0])**2+(P[:,1]-P[j,1])**2
        d=np.delete(d,j)
        d=d[d<=RR]
        if len(d)==0: continue
        u,c=np.unique(d,return_counts=True)
        if (c>k).any(): return False,(j,int(u[np.argmax(c)]),int(c.max()))
    return True,None

if __name__=="__main__":
    from core import verify_isofree, verify_isofree_ref
    # cross-validate greedy k=1 against the original verifiers
    for n in [8,12,16,20]:
        best=[];
        for s in range(30):
            p=greedy(n,1,None,seed=s)
            if len(p)>len(best): best=p
        ok1=verify_isofree(best)[0]; ok2=verify_isofree_ref(best)[0]; ok3=verify(best,1,None,n)[0]
        print(f"n={n} greedy k=1 best={len(best)} isofree={ok1},{ok2},{ok3}",flush=True)
        assert ok1 and ok2 and ok3
    # k=2 cross-check vs brute force on tiny n
    import itertools
    def brute_k(n,k):
        P=[(x,y) for x in range(n) for y in range(n)]
        best=0
        for m in range(len(P),0,-1):
            found=False
            for S in itertools.combinations(P,m):
                if verify(list(S),k,None,n)[0]: found=True;break
            if found: return m
        return 0
    for n in [3,4]:
        for k in [1,2]:
            print(f"brute n={n} k={k} -> {brute_k(n,k)}",flush=True)
