# -*- coding: utf-8 -*-
"""Round 4, probe 4.4 -- is parity (q=2) the BEST dilation, or is there a better q?

Dilation construction:  T = union over v in V of (q*S + v)  contained in [qn]^2.
Since |q*u + w|^2 = |w|^2 (mod q), two different class-pairs (v,v') can only
collide if |v-v'|^2 = |v-v''|^2 (mod q).  So the classes are pairwise separated
exactly when

    V is ISOSCELES-FREE IN Z_q^2 under the mod-q squared distance,

i.e. for every v in V the map v' -> |v-v'|^2 mod q is injective on V.
The construction is self-similar: the same problem, one level up.

|T| = |V|*|S| inside [qn]^2.  Exact maximum M(q) computed by branch and bound.
"""
import sys
sys.setrecursionlimit(10000)

def M(q):
    pts = [(x, y) for x in range(q) for y in range(q)]
    N = len(pts)
    # dsq[i][j] = |p_i - p_j|^2 mod q
    d = [[((pts[i][0]-pts[j][0])**2 + (pts[i][1]-pts[j][1])**2) % q
          for j in range(N)] for i in range(N)]
    best = [0]; bestset = [None]
    def ok(cur, c):
        # adding c: every apex must keep injectivity
        for a in cur:                      # apex a sees c
            dac = d[a][c]
            for b in cur:
                if b != a and d[a][b] == dac: return False
        seen = set()                       # apex c sees all of cur
        for b in cur:
            if d[c][b] in seen: return False
            seen.add(d[c][b])
        return True
    def bb(start, cur):
        if len(cur) + (N - start) <= best[0]: return
        if len(cur) > best[0]:
            best[0] = len(cur); bestset[0] = list(cur)
        for c in range(start, N):
            if ok(cur, c):
                cur.append(c); bb(c+1, cur); cur.pop()
    bb(0, [])
    return best[0], [pts[i] for i in bestset[0]]

print("M(q) = max classes with mod-q separation.   Density multiplier needs M(q) large.")
print("  q   M(q)   M(q) vs q   witness")
for q in range(2, 12):
    m, w = M(q)
    print("%3d %5d      %-6s  %s" % (q, m, "M>=q" if m >= q else "M<q", w if len(w) <= 6 else str(w[:6])+"..."))
    sys.stdout.flush()
