"""Barrier constructions (a)-(d): large sets satisfying RELAXATIONS of isosceles-freeness."""
import json,os,sys,itertools
from ap3 import best_3apfree, is_3apfree, max_3apfree_weighted

SD=os.path.join(os.path.dirname(os.path.abspath(__file__)),"sets")
os.makedirs(SD,exist_ok=True)

# ---------------- independent verifiers for each relaxation ----------------
def ver_a(S,n):
    """every axis-parallel line meets S in a 3-AP-free set"""
    from collections import defaultdict
    rows=defaultdict(list); cols=defaultdict(list)
    for (x,y) in S: rows[y].append(x); cols[x].append(y)
    for d in (rows,cols):
        for k,v in d.items():
            s=set(v)
            for a in v:
                for b in v:
                    if b!=a and 2*b-a in s and 2*b-a!=b: return False,(k,a,b)
    return True,None

def ver_b(S,n):
    """no 3-term AP p, p+v, p+2v in Z^2 (v != 0)"""
    Ss=set(S)
    L=list(S)
    for p in L:
        for q in L:
            if q==p: continue
            r=(2*q[0]-p[0], 2*q[1]-p[1])
            if r!=q and r in Ss: return False,(p,q,r)
    return True,None

def ver_c(S,n):
    """no corner (x,y),(x+d,y),(x,y+d), d != 0"""
    Ss=set(S)
    for (x,y) in S:
        for (x2,y2) in S:
            if y2==y and x2!=x:
                d=x2-x
                if (x,y+d) in Ss: return False,((x,y),(x2,y2),(x,y+d))
    return True,None

def ver_d(S, apexes):
    """all squared distances from each fixed apex are distinct"""
    for b in apexes:
        seen={}
        for p in S:
            if tuple(p)==tuple(b): continue
            r=(p[0]-b[0])**2+(p[1]-b[1])**2
            if r in seen: return False,(b,seen[r],p,r)
            seen[r]=p
    return True,None

# ---------------- constructions ----------------
def build_a(n):
    """S = {(x,y): x+y in W}, W 3AP-free in [0,2n-2], weight-optimised."""
    N=2*n-1
    wt=[min(w+1, N-w) for w in range(N)]      # #lattice pts on antidiagonal x+y=w
    if n<=14:
        val,W,exact=max_3apfree_weighted(N,wt,10**6)
    else:
        exact=False
        # heuristic: translate best 3AP-free set of [0,n) into the fat middle
        base=best_3apfree(n); W=None; val=-1
        for sh in range(0,N-max(base)):
            WW=[b+sh for b in base]
            if max(WW)>=N: break
            v=sum(wt[w] for w in WW)
            if v>val: val=v; W=WW
    S=[(x,w-x) for w in W for x in range(max(0,w-n+1), min(n-1,w)+1)]
    return S, exact, W

def build_b(n):
    """S = {(x,y): x+y in W1, x-y in W2}, both 3AP-free -> no 3AP in Z^2."""
    # sums s=x+y in [0,2n-2], diffs d=x-y in [-(n-1),n-1]; need s==d mod 2
    N=2*n-1
    W1=set(best_3apfree(N))
    W2=set(w-(n-1) for w in best_3apfree(N))
    S=[(x,y) for x in range(n) for y in range(n) if (x+y) in W1 and (x-y) in W2]
    # also the plain product for comparison
    Wp=best_3apfree(n)
    S2=[(x,y) for x in Wp for y in Wp]
    return (S if len(S)>=len(S2) else S2), (len(S)>=len(S2))

def build_c(n):
    """S = {(x,y): x-y in W}, W 3AP-free -> corner-free."""
    N=2*n-1
    wt=[n-abs(d) for d in range(-(n-1),n)]   # index i <-> d=i-(n-1)
    if n<=14:
        val,Widx,exact=max_3apfree_weighted(N,wt,10**6)
    else:
        exact=False; base=best_3apfree(n); Widx=None; val=-1
        for sh in range(0,N-max(base)):
            WW=[b+sh for b in base]
            if max(WW)>=N: break
            v=sum(wt[w] for w in WW)
            if v>val: val=v; Widx=WW
    W=[i-(n-1) for i in Widx]
    S=[(x,x-d) for d in W for x in range(max(0,d), min(n-1,n-1+d)+1)]
    return S, exact, W

def build_d(n, apexes):
    """greedy max set with distinct distances from each fixed apex.
       Exact for k=1 (=#distinct radii). Greedy+bipartite-matching for k>=2."""
    pts=[(x,y) for x in range(n) for y in range(n)]
    k=len(apexes)
    if k==1:
        b=apexes[0]; seen={}
        for p in pts:
            r=(p[0]-b[0])**2+(p[1]-b[1])**2
            if r not in seen: seen[r]=p
        return list(seen.values()), True   # EXACT optimum
    used=[set() for _ in apexes]; S=[]
    # order points by rarity: fewer collisions first
    from collections import Counter
    cnt=[Counter() for _ in apexes]
    for p in pts:
        for i,b in enumerate(apexes): cnt[i][(p[0]-b[0])**2+(p[1]-b[1])**2]+=1
    pts.sort(key=lambda p: sum(cnt[i][(p[0]-apexes[i][0])**2+(p[1]-apexes[i][1])**2] for i in range(k)))
    for p in pts:
        rs=[(p[0]-b[0])**2+(p[1]-b[1])**2 for b in apexes]
        if any(r in used[i] for i,r in enumerate(rs)): continue
        for i,r in enumerate(rs): used[i].add(r)
        S.append(p)
    return S, False

if __name__=="__main__":
    out={}
    print(f"{'n':>5} {'(a)':>8} {'(b)':>8} {'(c)':>8}  n^2   (a)/n^2 (b)/n^2 (c)/n^2")
    for n in [8,11,16,27,32,45,64,90,128]:
        Sa,ea,_=build_a(n); Sb,_=build_b(n); Sc,ec,_=build_c(n)
        assert ver_a(Sa,n)[0], ("a fail",n)
        assert ver_b(Sb,n)[0], ("b fail",n)
        assert ver_c(Sc,n)[0], ("c fail",n)
        # sanity: all in box, distinct
        for S in (Sa,Sb,Sc):
            assert len(set(S))==len(S) and all(0<=x<n and 0<=y<n for x,y in S)
        sys.stdout.flush()
        print(f"{n:>5} {len(Sa):>8} {len(Sb):>8} {len(Sc):>8} {n*n:>6} {len(Sa)/n**2:7.3f} {len(Sb)/n**2:7.3f} {len(Sc)/n**2:7.3f}  exact_a={ea} exact_c={ec}",flush=True)
        out[n]=dict(a=len(Sa),b=len(Sb),c=len(Sc),n2=n*n)
        for nm,S in (("a",Sa),("b",Sb),("c",Sc)):
            json.dump(dict(name=f"barrier_{nm}_n{n}",n=n,size=len(S),relaxation=nm,
                           status="VERIFIED_COMPUTATIONAL_RESULT",points=sorted(map(list,S))),
                      open(os.path.join(SD,f"barrier_{nm}_n{n}.json"),"w"))
    json.dump(out,open(os.path.join(SD,"barrier_abc_summary.json"),"w"),indent=1)
