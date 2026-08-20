# -*- coding: utf-8 -*-
"""Validate the k-row strip decomposition against brute force.

Claim: S subset [k]x[n] is isosceles-free iff, writing A_i for row i:
  (V)  for every i with A_i nonempty and every j != i with 0<=2i-j<k:
           A_j and A_{2i-j} are column-disjoint          [vertical mirror pairs]
  (M)  for every i, every a in A_i, every j with 0<=2i-j<k:
           a is not a midpoint of (b,b') with b in A_j, b' in A_{2i-j}, (j,b)!=(2i-j,b')
           [c = 0 collisions; j=i gives plain 3-AP inside A_i]
  (D)  for every i, a in A_i, and every pair of row-offsets (u,u') with u^2 != u'^2:
           no s,s' with s^2 - s'^2 = u'^2 - u^2, a-s in A_{i-u}, a-s' in A_{i-u'}
           [divisor-type, rigid]
"""
import itertools, sys

def isofree(pts):
    P = list(pts)
    for i, p in enumerate(P):
        seen = set()
        for j, q in enumerate(P):
            if i == j: continue
            d = (p[0]-q[0])**2 + (p[1]-q[1])**2
            if d in seen: return False
            seen.add(d)
    return True

def by_cond(pts, k, n):
    A = [set() for _ in range(k)]
    for (i, a) in pts: A[i].add(a)
    # (V)
    for i in range(k):
        if not A[i]: continue
        for j in range(k):
            m = 2*i - j
            if j == i or not (0 <= m < k): continue
            if A[j] & A[m]: return False
    # (M) c=0 collisions: |i-j| = |i-j'| means j'=j or j'=2i-j
    for i in range(k):
        if not A[i]: continue
        for a in A[i]:
            for j in range(k):
                for jp in set([j, 2*i-j]):
                    if not (0 <= jp < k): continue
                    for b in A[j]:
                        bp = 2*a - b
                        if bp in A[jp] and (j,b)!=(jp,bp) and (j,b)!=(i,a) and (jp,bp)!=(i,a):
                            return False
    # (D)
    for i in range(k):
        for a in A[i]:
            for u in range(-(k-1), k):
                for up in range(-(k-1), k):
                    if u*u == up*up: continue
                    ri, rip = i-u, i-up
                    if not (0 <= ri < k and 0 <= rip < k): continue
                    c = up*up - u*u
                    for b in A[ri]:
                        s = a-b
                        # s^2 - s'^2 = c  ->  s'^2 = s^2 - c
                        t = s*s - c
                        if t < 0: continue
                        r = int(t**0.5)
                        for cand in (r-1, r, r+1):
                            if cand >= 0 and cand*cand == t:
                                for sp in ({cand, -cand}):
                                    bp = a - sp
                                    if bp in A[rip] and (ri,b)!=(i,a) and (rip,bp)!=(i,a) \
                                       and (ri,b)!=(rip,bp):
                                        return False
    return True

bad = 0; tested = 0
for k in (1,2,3):
    for n in range(1, 7):
        cells = [(i,a) for i in range(k) for a in range(n)]
        for m in range(0, min(len(cells), 7)+1):
            for sub in itertools.combinations(cells, m):
                tested += 1
                if isofree(sub) != by_cond(sub, k, n):
                    bad += 1
                    if bad <= 5: print("MISMATCH k=%d n=%d %s def=%s cond=%s"
                                       % (k,n,sub,isofree(sub),by_cond(sub,k,n)))
print("tested", tested, "mismatches", bad)
