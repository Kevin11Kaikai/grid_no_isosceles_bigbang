# -*- coding: utf-8 -*-
"""FAR-C001 probe: measure degree and codegree of the isosceles 3-uniform hypergraph
on [n]^2, to test D  ~  c n^2 log n  and  maxcodeg ~ c n.
Everything exact integer arithmetic."""
import sys, math
from collections import defaultdict

def stats(n):
    pts = [(x,y) for x in range(n) for y in range(n)]
    N = len(pts)
    # apex-degree of p = sum_d C(m_p(d),2)
    apexdeg = {}
    mcount  = {}          # p -> dict d -> m_p(d)
    for p in pts:
        c = defaultdict(int)
        for q in pts:
            if q == p: continue
            c[(p[0]-q[0])**2 + (p[1]-q[1])**2] += 1
        mcount[p] = c
        apexdeg[p] = sum(m*(m-1)//2 for m in c.values())
    # base-degree of p = sum_{q!=p} (m_q(|qp|^2) - 1)
    deg = {}
    for p in pts:
        base = 0
        for q in pts:
            if q == p: continue
            base += mcount[q][(p[0]-q[0])**2 + (p[1]-q[1])**2] - 1
        deg[p] = apexdeg[p] + base
    E = sum(apexdeg.values())                       # each edge has a UNIQUE apex
    Dmax, Davg = max(deg.values()), sum(deg.values())/N
    # codegree: for each pair, # r with {p,q,r} isosceles
    maxcod = 0
    for i,p in enumerate(pts):
        for q in pts[i+1:]:
            dpq = (p[0]-q[0])**2 + (p[1]-q[1])**2
            s = set()
            for r in pts:
                if r == p or r == q: continue
                a = (p[0]-r[0])**2 + (p[1]-r[1])**2
                b = (q[0]-r[0])**2 + (q[1]-r[1])**2
                if a == dpq or b == dpq or a == b: s.add(r)
            maxcod = max(maxcod, len(s))
    return N, E, Davg, Dmax, maxcod

print(" n     N       E        Davg      Dmax   maxcod   Davg/(n^2 log n)  maxcod/n")
for n in range(3, 17):
    N,E,Da,Dm,mc = stats(n)
    nrm = Da/(n*n*math.log(n)) if n>1 else float('nan')
    print("%2d %6d %9d %10.1f %8d %6d %14.4f %10.4f" % (n,N,E,Da,Dm,mc,nrm,mc/n))
