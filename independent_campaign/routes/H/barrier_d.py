"""Barrier (d): distinct distances required only from a FIXED small apex set."""
import numpy as np, itertools, json, os, sys
from barriers import ver_d
SD=os.path.join(os.path.dirname(os.path.abspath(__file__)),"sets"); os.makedirs(SD,exist_ok=True)

def radii(n,b):
    x=np.arange(n); X,Y=np.meshgrid(x,x,indexing='ij')
    return ((X-b[0])**2+(Y-b[1])**2).ravel()

def k1_exact(n,b):
    r=radii(n,b); return len(np.unique(r))

def hopcroft_karp(adj, nL, nR):
    import collections
    INF=float('inf')
    matchL=[-1]*nL; matchR=[-1]*nR
    while True:
        dist=[INF]*nL; q=collections.deque()
        for u in range(nL):
            if matchL[u]==-1: dist[u]=0; q.append(u)
        found=False
        while q:
            u=q.popleft()
            for v in adj[u]:
                w=matchR[v]
                if w==-1: found=True
                elif dist[w]==INF: dist[w]=dist[u]+1; q.append(w)
        if not found: return matchL,matchR
        def dfs(u):
            for v in adj[u]:
                w=matchR[v]
                if w==-1 or (dist[w]==dist[u]+1 and dfs(w)):
                    matchL[u]=v; matchR[v]=u; return True
            dist[u]=INF; return False
        for u in range(nL):
            if matchL[u]==-1: dfs(u)

def k2_exact(n,b1,b2):
    """max set with distinct radii from b1 AND from b2 = max bipartite matching."""
    r1=radii(n,b1); r2=radii(n,b2)
    u1,i1=np.unique(r1,return_inverse=True); u2,i2=np.unique(r2,return_inverse=True)
    adj=[set() for _ in range(len(u1))]
    pt_of={}
    for p in range(n*n):
        adj[i1[p]].add(i2[p]); pt_of[(i1[p],i2[p])]=p
    adj=[sorted(s) for s in adj]
    mL,mR=hopcroft_karp(adj,len(u1),len(u2))
    S=[]
    for L,Rv in enumerate(mL):
        if Rv>=0:
            p=pt_of[(L,Rv)]; S.append((p//n,p%n))
    return S

def kgreedy(n,apexes):
    R=[radii(n,b) for b in apexes]
    used=[set() for _ in apexes]
    # order by product of class sizes (rarest first)
    from collections import Counter
    cs=[Counter(r.tolist()) for r in R]
    order=sorted(range(n*n), key=lambda p: sum(cs[i][int(R[i][p])] for i in range(len(apexes))))
    S=[]
    for p in order:
        rs=[int(R[i][p]) for i in range(len(apexes))]
        if any(rs[i] in used[i] for i in range(len(apexes))): continue
        for i in range(len(apexes)): used[i].add(rs[i])
        S.append((p//n,p%n))
    return S

if __name__=="__main__":
    print("k=1 EXACT optimum (= #distinct squared radii from apex b):",flush=True)
    print(f"{'n':>5} {'best-b':>8} {'worst-b':>8} {'center':>8} {'n^2':>8} {'best/n^2':>9} {'worst/n^2':>10}")
    for n in [8,16,32,64,128,181,256]:
        cand=[(x,y) for x in range(0,n,max(1,n//8)) for y in range(0,n,max(1,n//8))]
        cand+= [(0,0),(n-1,n-1),(n//2,n//2),(0,n//2),(n//2,0)]
        vals={b:k1_exact(n,b) for b in set(cand)}
        bb=max(vals,key=vals.get); wb=min(vals,key=vals.get)
        print(f"{n:>5} {vals[bb]:>8} {vals[wb]:>8} {k1_exact(n,(n//2,n//2)):>8} {n*n:>8} {vals[bb]/n**2:9.4f} {vals[wb]/n**2:10.4f}",flush=True)
    print()
    print("k=2 EXACT optimum (max bipartite matching), apexes = two grid corners / adversarial:",flush=True)
    for n in [8,16,32,64,90,128]:
        pairs=[((0,0),(n-1,n-1)),((0,0),(n-1,0)),((n//2,n//2),(n//2+1,n//2)),((0,0),(1,1))]
        best=0;worst=10**9
        for (b1,b2) in pairs:
            S=k2_exact(n,b1,b2)
            ok,w=ver_d(S,[b1,b2]); assert ok,(n,b1,b2,w)
            best=max(best,len(S)); worst=min(worst,len(S))
        print(f"n={n:4d}  best={best:7d} worst={worst:7d}  n^2={n*n:7d}  worst/n^2={worst/n**2:.4f}",flush=True)
    print()
    print("k=3 greedy lower bound (adversarial apex triples):",flush=True)
    for n in [8,16,32,64,90,128]:
        trips=[((0,0),(n-1,n-1),(0,n-1)),((n//2,n//2),(n//2+1,n//2),(n//2,n//2+1)),((0,0),(1,0),(0,1))]
        worst=10**9;best=0
        for T in trips:
            S=kgreedy(n,list(T)); ok,w=ver_d(S,list(T)); assert ok,(n,T,w)
            worst=min(worst,len(S)); best=max(best,len(S))
        print(f"n={n:4d}  best={best:7d} worst={worst:7d}  n^2={n*n:7d}  worst/n^2={worst/n**2:.4f}",flush=True)
    print()
    print("k apexes, greedy, adversarial (k nearby points):",flush=True)
    for n in [64,128]:
        for k in [1,2,3,4,6,8,12,16,24,32]:
            ap=[(n//2+i%6, n//2+i//6) for i in range(k)]
            S=kgreedy(n,ap); ok,w=ver_d(S,ap); assert ok,(n,k,w)
            print(f"n={n} k={k:3d} size={len(S):7d} /n^2={len(S)/n**2:.4f}",flush=True)
