# -*- coding: utf-8 -*-
"""Round 5, probe 5.1/5.2 -- the mod-p reduction (candidate FAR-C006).

REDUCTION (rigorous, trivial).  Let S c [0,p)^2 be such that for every s in S the
map s' -> Q(s-s') mod p is injective on S\{s}, where Q(u) = u_x^2 + u_y^2.
Distinct mod p => distinct as integers => S is ISOSCELES-FREE IN Z^2.
Hence  C(p) >= A(p) := max such |S|.

WHY THIS IS DIFFERENT.  Mod p the representation function is FLAT: for p = 3 mod 4,
Q is the norm form of F_{p^2} and every nonzero value has exactly p+1 preimages.
The Sum r_2(d)^2 ~ X log X non-uniformity that killed rounds 1-4 does not exist here.

CEILING.  For p = 3 mod 4, Q(u)=0 iff u=0, so the p-1 nonzero values give |S| <= p.
For p = 1 mod 4 there are isotropic u != 0, giving |S| <= p+1.

Q: is A(p) = Omega(p)?   If yes -> C(n) = Omega(n) along the primes.
"""
import sys
from itertools import combinations

def build(p):
    pts = [(x, y) for x in range(p) for y in range(p)]
    idx = {q: i for i, q in enumerate(pts)}
    N = len(pts)
    Q = [[0]*N for _ in range(N)]
    for i, a in enumerate(pts):
        for j, b in enumerate(pts):
            Q[i][j] = ((a[0]-b[0])**2 + (a[1]-b[1])**2) % p
    return pts, idx, N, Q

def A_exact(p, timelimit_nodes=8_000_000):
    """max |S|; translation-invariant so fix 0 in S."""
    pts, idx, N, Q = build(p)
    z = idx[(0, 0)]
    best = [0]; bw = [None]; nodes = [0]
    cur = [z]
    seen = [None]*N          # seen[a] = set of Q values used at apex a
    seen[z] = set()
    def feasible(c):
        for a in cur:
            if Q[a][c] in seen[a]: return False
        sd = set()
        for a in cur:
            v = Q[c][a]
            if v in sd: return False
            sd.add(v)
        return True
    def bb(start):
        nodes[0] += 1
        if nodes[0] > timelimit_nodes: return True      # aborted
        if len(cur) + (N - start) <= best[0]: return False
        if len(cur) > best[0]:
            best[0] = len(cur); bw[0] = [pts[i] for i in cur]
        for c in range(start, N):
            if c == z: continue
            if feasible(c):
                added = []
                for a in cur:
                    seen[a].add(Q[a][c]); added.append(a)
                seen[c] = set(Q[c][a] for a in cur)
                cur.append(c)
                ab = bb(c+1)
                cur.pop()
                for a in added: seen[a].discard(Q[a][c])
                seen[c] = None
                if ab: return True
        return False
    aborted = bb(0)
    return best[0], bw[0], aborted, nodes[0]

print("A(p) = max S c F_p^2 with all same-apex norms distinct.  C(p) >= A(p).")
print("Ceiling: p (p=3 mod 4), p+1 (p=1 mod 4).")
print()
print("   p   p mod 4   A(p)   ceiling   A(p)/p   status")
for p in (3, 5, 7, 11, 13, 17, 19, 23):
    m, w, ab, nd = A_exact(p)
    ceil = p if p % 4 == 3 else p+1
    print("%4d %8d %6d %9d %8.3f   %s"
          % (p, p % 4, m, ceil, m/p, "ABORTED(nodes=%d) lower bd only" % nd if ab else "exact"))
    sys.stdout.flush()
