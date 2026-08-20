# -*- coding: utf-8 -*-
"""Measure the two Bennett-Bohman hypotheses for the isosceles hypergraph on [n]^2.
  Delta_2 = max over pairs {p,q} of #edges containing both        need < D^{1/2-eps}
  Gamma   = max over pairs {p,q} of #{ {a,b} : {p,a,b},{q,a,b} in H }  need < D^{1-eps}
"""
import math
from collections import defaultdict
from itertools import combinations

def d2(p,q): return (p[0]-q[0])**2 + (p[1]-q[1])**2

def run(n):
    pts=[(x,y) for x in range(n) for y in range(n)]
    idx={p:i for i,p in enumerate(pts)}
    N=len(pts)
    # W(a,b) = { v : {v,a,b} is an isosceles triple }
    gamma=defaultdict(int)
    delta2=defaultdict(int)
    for ia in range(N):
        a=pts[ia]
        for ib in range(ia+1,N):
            b=pts[ib]
            dab=d2(a,b)
            W=[]
            for v in pts:
                if v==a or v==b: continue
                da,db=d2(v,a),d2(v,b)
                if da==db or da==dab or db==dab: W.append(v)
            # edge {v,a,b}: contributes to Delta_2 of pairs (v,a),(v,b),(a,b)
            for v in W:
                delta2[(min(idx[v],ia),max(idx[v],ia))]+=1
                delta2[(min(idx[v],ib),max(idx[v],ib))]+=1
            delta2[(ia,ib)]+=len(W)
            for p,q in combinations(W,2):
                gamma[(min(idx[p],idx[q]),max(idx[p],idx[q]))]+=1
    return max(delta2.values()), max(gamma.values())

print(" n   Delta_2   Gamma    D_avg    Delta_2/n   Gamma/n^2   Gamma/D")
for n in range(4,15):
    D2,G=run(n)
    D = 1.66*n*n*math.log(n)   # measured fit from degree.py
    print("%2d %8d %8d %9.0f %10.3f %11.3f %9.3f" % (n,D2,G,D,D2/n,G/(n*n),G/D))
