# -*- coding: utf-8 -*-
"""Round 4, probe 4.1 -- PARITY-SEPARATED DOUBLING (candidate FAR-C005).

Mechanism.  Split [2n]^2 by coordinate parity.  For p-q = (even,even),
|p-q|^2 = 0 mod 4;  for p-q = (odd,odd), |p-q|^2 = 2 mod 4.  Hence in

        T = 2S  u  (2S + (a,b)) ,      a,b both ODD

every apex sees its own class at 0 mod 4 and the other class at 2 mod 4:
those two families can NEVER collide.  So T is isosceles-free iff

   (i)  S is isosceles-free                        [both same-class families]
   (ii) for each s in S, the map s' -> G(s,s') is injective
   (iv) for each s in S, the map s' -> G(s',s) is injective
        where  G(s,s') = |2(s-s') + (a,b)|^2 .

(ii)+(iv) = "condition (H)": every ROW and every COLUMN of the matrix G is
injective.  Geometrically: each half-integer point s +- (a,b)/2 must be off
every perpendicular bisector of a pair of S.

If C_H(n) = C(n) then C(2n) >= 2*C(n) and iterating gives C(n) = Omega(n).
So the whole question is how much (H) costs.  Measure it.
"""
import random, sys

def isofree_bruteforce(P):
    P = list(P)
    for i, p in enumerate(P):
        seen = set()
        for j, q in enumerate(P):
            if i == j: continue
            d = (p[0]-q[0])**2 + (p[1]-q[1])**2
            if d in seen: return False, (p, q)
            seen.add(d)
    return True, None

def greedy(n, ab=None, seed=0):
    """random greedy over a shuffled grid; if ab is given also enforce (H)."""
    rnd = random.Random(seed)
    order = [(x, y) for x in range(n) for y in range(n)]
    rnd.shuffle(order)
    S, dist, Hrow, Hcol = [], [], [], []
    if ab: a, b = ab
    for p in order:
        dp = set()
        hr = set(); hc = set()
        if ab:
            g0 = a*a + b*b          # G(p,p)
            hr.add(g0); hc.add(g0)
        ok = True
        for i, s in enumerate(S):
            d = (s[0]-p[0])**2 + (s[1]-p[1])**2
            if d in dist[i] or d in dp: ok = False; break
            dp.add(d)
            if ab:
                gsp = (2*(s[0]-p[0])+a)**2 + (2*(s[1]-p[1])+b)**2   # G(s,p)
                gps = (2*(p[0]-s[0])+a)**2 + (2*(p[1]-s[1])+b)**2   # G(p,s)
                if gsp in Hrow[i] or gsp in hc: ok = False; break
                if gps in Hcol[i] or gps in hr: ok = False; break
                hc.add(gsp); hr.add(gps)
        if not ok: continue
        for i, s in enumerate(S):
            d = (s[0]-p[0])**2 + (s[1]-p[1])**2
            dist[i].add(d)
            if ab:
                Hrow[i].add((2*(s[0]-p[0])+a)**2 + (2*(s[1]-p[1])+b)**2)
                Hcol[i].add((2*(p[0]-s[0])+a)**2 + (2*(p[1]-s[1])+b)**2)
        S.append(p); dist.append(dp); Hrow.append(hr); Hcol.append(hc)
    return S

KNOWN = {1:1,2:2,3:4,4:6,5:7,6:9,7:10,8:13,9:16,10:18,11:18,12:20,13:22,
         16:28, 21:36, 23:40, 25:44, 27:48, 32:56}

print("C_H(n) = max isosceles-free S in [n]^2 ALSO satisfying (H) for offset (a,b).")
print("Doubling theorem: C(2n) >= 2*C_H(n).   Linearity needs C_H(n)/C(n) -> 1.")
print()
print("  n   plain-greedy   C_H (a,b)=(1,1)   best over odd (a,b)   known C(n)   2*C_H  vs C(2n)")
SEEDS = 400
for n in (4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16):
    plain = max(len(greedy(n, None, s)) for s in range(SEEDS))
    h11   = max(len(greedy(n, (1,1), s)) for s in range(SEEDS))
    best, bestab = h11, (1,1)
    for a in range(1, min(2*n, 12), 2):
        for b in range(-min(2*n,12)+1, min(2*n,12), 2):
            if (a,b) == (1,1): continue
            v = max(len(greedy(n, (a,b), s)) for s in range(60))
            if v > best: best, bestab = v, (a,b)
    kn  = KNOWN.get(n, '?')
    k2n = KNOWN.get(2*n, '?')
    print("%3d %10d %14d %16d %-8s %8s %6d  vs %s"
          % (n, plain, h11, best, str(bestab), str(kn), 2*best, str(k2n)))
    sys.stdout.flush()
