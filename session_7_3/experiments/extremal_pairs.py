# -*- coding: utf-8 -*-
"""Which pairs {p,q} attain max Delta_2 and max Gamma?  Tests the claim that the
obstruction is carried by AXIS-PARALLEL pairs (perpendicular bisector = a grid line
for Delta_2; axis-parallel mirror pairs for Gamma)."""
from collections import defaultdict
from itertools import combinations
def d2(p,q): return (p[0]-q[0])**2+(p[1]-q[1])**2

def run(n):
    pts=[(x,y) for x in range(n) for y in range(n)]; N=len(pts)
    idx={p:i for i,p in enumerate(pts)}
    D2=defaultdict(int); G=defaultdict(int)
    for ia in range(N):
        a=pts[ia]
        for ib in range(ia+1,N):
            b=pts[ib]; dab=d2(a,b); W=[]
            for v in pts:
                if v==a or v==b: continue
                da,db=d2(v,a),d2(v,b)
                if da==db or da==dab or db==dab: W.append(v)
            for v in W:
                D2[frozenset((v,a))]+=1; D2[frozenset((v,b))]+=1
            D2[frozenset((a,b))]+=len(W)
            for p,q in combinations(W,2): G[frozenset((p,q))]+=1
    md=max(D2.values()); mg=max(G.values())
    dpairs=[tuple(sorted(k)) for k,v in D2.items() if v==md]
    gpairs=[tuple(sorted(k)) for k,v in G.items() if v==mg]
    def kind(pr):
        (x1,y1),(x2,y2)=pr
        if x1==x2: return "same column"
        if y1==y2: return "same row"
        if abs(x1-x2)==abs(y1-y2): return "diagonal"
        return "generic"
    from collections import Counter
    return md//3, mg, Counter(kind(p) for p in dpairs), Counter(kind(p) for p in gpairs), dpairs[:2], gpairs[:2]

for n in (8,10,12):
    md,mg,kd,kg,de,ge = run(n)
    print("n=%d  max Delta_2=%d  (n=%d)   max Gamma=%d  (n(n-1)/2=%d)" % (n,md,n,mg,n*(n-1)//2))
    print("     Delta_2 extremal pair types:", dict(kd), " e.g.", de)
    print("     Gamma   extremal pair types:", dict(kg), " e.g.", ge)
