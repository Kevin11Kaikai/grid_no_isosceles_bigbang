"""Explicit ALGEBRAIC candidate constructions, and how isosceles-free they actually are.
For each family F subset [n]^2 we report |F| and the largest isosceles-free subset of F
we can extract (greedy over many random orders) -- an honest LOWER bound."""
import numpy as np, math, json, os, sys
from core import verify_isofree, verify_isofree_ref
from ap3 import best_3apfree, is_3apfree
SD=os.path.join(os.path.dirname(os.path.abspath(__file__)),"sets")

def isofree_subset(F, tries=40, seed=0):
    F=[tuple(map(int,p)) for p in F]
    rng=np.random.default_rng(seed); best=[]
    Fa=np.array(F,np.int64)
    for t in range(tries):
        o=rng.permutation(len(F))
        X=np.zeros(0,np.int64);Y=np.zeros(0,np.int64); used=[]; S=[]
        for i in o:
            px,py=Fa[i]
            if len(S):
                d=(X-px)**2+(Y-py)**2
                if (d==0).any(): continue
                if len(np.unique(d))!=len(d): continue
                bad=False
                for j,dj in enumerate(d.tolist()):
                    if dj in used[j]: bad=True;break
                if bad: continue
                for j,dj in enumerate(d.tolist()): used[j].add(dj)
                used.append(set(d.tolist()))
            else:
                used.append(set())
            X=np.append(X,px);Y=np.append(Y,py);S.append((int(px),int(py)))
        if len(S)>len(best): best=S
    return best

def is_prime(p):
    if p<2: return False
    for q in range(2,int(p**.5)+1):
        if p%q==0: return False
    return True

def families(n):
    F={}
    W=best_3apfree(n)
    F["line_Behrend  {(w,0):w 3AP-free}"]=[(w,0) for w in W]
    F["diag_Behrend  {(w,w)}"]=[(w,w) for w in W]
    p=n
    while not is_prime(p): p-=1
    F[f"parabola x^2 mod {p}"]=[(x,(x*x)%p) for x in range(p)]
    F[f"cube x^3 mod {p}"]=[(x,pow(x,3,p)) for x in range(p)]
    F[f"inverse x^-1 mod {p}"]=[(x,pow(x,p-2,p)) for x in range(1,p)]
    g=2
    while pow(g,(p-1)//2,p)==1 or any(pow(g,(p-1)//q,p)==1 for q in set(f for f in range(2,p) if (p-1)%f==0 and is_prime(f))):
        g+=1
        if g>p: break
    if g<p: F[f"power {g}^x mod {p}"]=[(x,pow(g,x,p)) for x in range(p-1)]
    # Sidon (Singer/Erdos-Turan mod p): {(i, i^2 mod p)} is Sidon-in-Zp x Zp; use Erdos-Turan
    F[f"ErdosTuran Sidon {{2pi+ (i^2 mod p)}}"]=[(i,(i*i)%p) for i in range(p//2)]
    # circle: lattice points on a circle
    best=None
    for r in range(2,2*n*n):
        pts=[(x,y) for x in range(n) for y in range(n) if (x-n//2)**2+(y-n//2)**2==r]
        if best is None or len(pts)>len(best): best=pts
    F["max lattice circle"]=best
    # Behrend sphere in 2D digits
    for d in [3,4,5]:
        k=1
        while d**k<n: k+=1
        half=(d+1)//2
        from collections import defaultdict
        buck=defaultdict(list)
        for x in range(n):
            dx=[];t=x
            for _ in range(k): dx.append(t%d); t//=d
            if any(v>=half for v in dx): continue
            for y in range(n):
                dy=[];t=y
                for _ in range(k): dy.append(t%d); t//=d
                if any(v>=half for v in dy): continue
                s=sum(v*v for v in dx)+sum(v*v for v in dy)
                buck[s].append((x,y))
        if buck:
            b=max(buck.values(),key=len)
            F[f"2D Behrend sphere base {d}"]=b
    # random baseline of the same nature
    return F

if __name__=="__main__":
    for n in [32,64]:
        print(f"===== n={n}  (C(n) known: {'56' if n==32 else '?'}) =====",flush=True)
        F=families(n)
        for name,pts in F.items():
            pts=[p for p in pts if 0<=p[0]<n and 0<=p[1]<n]
            pts=sorted(set(pts))
            if not pts: continue
            S=isofree_subset(pts,tries=25,seed=1)
            ok=verify_isofree(S)[0] and (verify_isofree_ref(S)[0] if len(S)<=200 else True)
            whole = verify_isofree(pts)[0]
            print(f"  {name:38s} |F|={len(pts):5d}  wholeF_isofree={whole}  max_isofree_subset>={len(S):4d}  ok={ok}",flush=True)
