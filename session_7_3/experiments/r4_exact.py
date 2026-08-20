# -*- coding: utf-8 -*-
"""Round 4, probe 4.5 -- EXACT C_H(n), to check that rho<1 is real and not a
greedy artefact.  Branch and bound over all of [n]^2 with both the isosceles
constraint and condition (H) for offset (1,1).

C_H(n) = max |S|, S c [n]^2, S isosceles-free, and for every s in S both maps
   s' -> G(s,s')  and  s' -> G(s',s)      G(s,s') = |2(s-s')+(1,1)|^2
are injective on S.   Theorem: C(2n) >= 2*C_H(n).
"""
import sys
sys.setrecursionlimit(100000)

KNOWN = {1:1,2:2,3:4,4:6,5:7,6:9,7:10,8:13,9:16,10:18}

def CH(n, a=1, b=1, need_H=True):
    pts = [(x, y) for x in range(n) for y in range(n)]
    N = len(pts)
    D  = [[0]*N for _ in range(N)]
    G  = [[0]*N for _ in range(N)]
    for i, p in enumerate(pts):
        for j, q in enumerate(pts):
            D[i][j] = (p[0]-q[0])**2 + (p[1]-q[1])**2
            G[i][j] = (2*(p[0]-q[0])+a)**2 + (2*(p[1]-q[1])+b)**2
    best = [0]; bw = [None]
    cur = []
    def feasible(c):
        for a_ in cur:
            if D[a_][c] in dset[a_]: return False
            if need_H:
                if G[a_][c] in grow[a_]: return False
                if G[c][a_] in gcol[a_]: return False
        sd = set(); sr = set(); sc = set()
        if need_H:
            g0 = a*a + b*b
            sr.add(g0); sc.add(g0)
        for a_ in cur:
            d = D[c][a_]
            if d in sd: return False
            sd.add(d)
            if need_H:
                if G[c][a_] in sr: return False
                sr.add(G[c][a_])
                if G[a_][c] in sc: return False
                sc.add(G[a_][c])
        return True
    dset = [set() for _ in range(N)]
    grow = [set() for _ in range(N)]
    gcol = [set() for _ in range(N)]
    def bb(start):
        if len(cur) + (N - start) <= best[0]: return
        if len(cur) > best[0]:
            best[0] = len(cur); bw[0] = [pts[i] for i in cur]
        for c in range(start, N):
            if feasible(c):
                saved = []
                for a_ in cur:
                    dset[a_].add(D[a_][c])
                    if need_H:
                        grow[a_].add(G[a_][c]); gcol[a_].add(G[c][a_])
                    saved.append(a_)
                dset[c] = set(D[c][a_] for a_ in cur)
                if need_H:
                    g0 = a*a + b*b
                    grow[c] = set([g0]) | set(G[c][a_] for a_ in cur)
                    gcol[c] = set([g0]) | set(G[a_][c] for a_ in cur)
                cur.append(c)
                bb(c+1)
                cur.pop()
                for a_ in saved:
                    dset[a_].discard(D[a_][c])
                    if need_H:
                        grow[a_].discard(G[a_][c]); gcol[a_].discard(G[c][a_])
                dset[c] = set(); grow[c] = set(); gcol[c] = set()
    bb(0)
    return best[0], bw[0]

print("EXACT values.  rho_exact = C_H(n)/C(n), against known optimal C(n).")
print("   n   C(n)   C_H(n) exact   rho_exact   2*C_H  vs  C(2n)")
for n in (3, 4, 5, 6, 7):
    m, w = CH(n)
    c = KNOWN[n]
    c2 = KNOWN.get(2*n, '?')
    print("%4d %6d %12d %13.3f %6d  vs  %s" % (n, c, m, m/c, 2*m, str(c2)))
    sys.stdout.flush()
