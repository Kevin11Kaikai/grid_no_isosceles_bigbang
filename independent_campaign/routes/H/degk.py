"""Barriers (e) and (f): degree-<=k distance graphs, and radius-capped (r<=R) constraints.

Condition D(k,R): for every b in S and every squared distance r <= R,
   |{a in S\{b} : |a-b|^2 = r}| <= k.
k=1, R=inf  is the original isosceles-free problem.
"""
import numpy as np, json, os, sys
SD=os.path.join(os.path.dirname(os.path.abspath(__file__)),"sets"); os.makedirs(SD,exist_ok=True)

def violations(P, k, R=None):
    """P: (m,2) int64 array. Return list of (apex_idx, radius, [member idxs]) with count>k."""
    X=P[:,0]; Y=P[:,1]; m=len(P)
    out=[]
    for j in range(m):
        d=(X-X[j])**2+(Y-Y[j])**2
        d[j]=-1
        if R is not None:
            mask=(d>=0)&(d<=R)
        else:
            mask=(d>=0)
        dd=d[mask]; idx=np.nonzero(mask)[0]
        if len(dd)==0: continue
        o=np.argsort(dd,kind='stable'); dd=dd[o]; idx=idx[o]
        # group runs
        b=np.nonzero(np.diff(dd))[0]+1
        starts=np.concatenate(([0],b)); ends=np.concatenate((b,[len(dd)]))
        for s,e in zip(starts,ends):
            if e-s>k: out.append((j, int(dd[s]), idx[s:e].tolist()))
    return out

def verify_Dk(P,k,R=None):
    return len(violations(P,k,R))==0

def repair(P, k, R=None, rng=None, max_rounds=200):
    """Delete points until D(k,R) holds. Greedy: delete the point in most violations."""
    P=np.array(P,dtype=np.int64)
    alive=np.ones(len(P),bool)
    for _ in range(max_rounds):
        Q=P[alive]
        v=violations(Q,k,R)
        if not v: break
        gidx=np.nonzero(alive)[0]
        # score: count appearances as an EXCESS member (not the apex)
        score=np.zeros(len(Q),dtype=np.int64)
        for (j,r,mem) in v:
            for i in mem: score[i]+=1
        # delete top offenders (batch for speed), at least 1
        nviol=len(v)
        nd=max(1, nviol//4)
        order=np.argsort(-score)
        kill=order[:nd]
        alive[gidx[kill]]=False
    return P[alive]

def build_Dk(n, k, R=None, p=None, seed=0, addback=True):
    rng=np.random.default_rng(seed)
    if p is None:
        Rmax = R if R is not None else 2*(n-1)**2
        # theory: p ~ (n^2 * S_{k+1})^{-1/(k+1)} with S ~ Rmax*polylog ; tune empirically
        p=min(1.0, (1.0/(n*n))**(0.0) * ( (n*n)**(-1.0/(k+1)) ) * ( (2*(n-1)**2/max(Rmax,1))**(0.5) ) )
        p=min(1.0,p)
    m=int(p*n*n)
    allpts=np.stack(np.meshgrid(np.arange(n),np.arange(n),indexing='ij'),-1).reshape(-1,2)
    sel=rng.choice(len(allpts), size=min(m,len(allpts)), replace=False)
    P=allpts[sel].astype(np.int64)
    P=repair(P,k,R,rng)
    if addback:
        P=greedy_addback(P,n,k,R,rng)
    return P

def greedy_addback(P,n,k,R,rng):
    P=[tuple(map(int,q)) for q in P]
    have=set(P)
    allp=[(x,y) for x in range(n) for y in range(n) if (x,y) not in have]
    rng.shuffle(allp)
    A=np.array(P,dtype=np.int64) if P else np.zeros((0,2),np.int64)
    for q in allp:
        B=np.vstack([A,np.array([q],np.int64)])
        # cheap incremental check: only need to check apex=q and apexes affected
        if _ok_add(A,q,k,R):
            A=B
    return A

def _ok_add(A,q,k,R):
    if len(A)==0: return True
    d=(A[:,0]-q[0])**2+(A[:,1]-q[1])**2
    if (d==0).any(): return False
    m=(d<=R) if R is not None else np.ones(len(d),bool)
    dd=np.sort(d[m])
    if len(dd)>k:
        # q as apex: no radius may occur >k times
        u,c=np.unique(dd,return_counts=True)
        if (c>k).any(): return False
    # each existing a as apex: adding q must not push a's radius class over k
    for i in range(len(A)):
        r=d[i]
        if R is not None and r>R: continue
        e=(A[:,0]-A[i,0])**2+(A[:,1]-A[i,1])**2
        cnt=int(np.count_nonzero(e==r))-(1 if e[i]==r else 0)
        if cnt>=k: return False
    return True

if __name__=="__main__":
    # sanity: k=1 R=inf must be an ordinary isosceles-free set
    sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
    from core import verify_isofree, verify_isofree_ref
    for n in [8,12,16]:
        P=build_Dk(n,1,None,p=0.5,seed=1)
        pts=[tuple(map(int,q)) for q in P]
        ok1=verify_isofree(pts)[0]; ok2=verify_isofree_ref(pts)[0]; ok3=verify_Dk(P,1,None)
        print(f"n={n} k=1 size={len(P)} isofree={ok1},{ok2} Dk={ok3}",flush=True)
        assert ok1 and ok2 and ok3
    print("cross-check OK: D(1,inf) == isosceles-free")
