# -*- coding: utf-8 -*-
"""Round 2, probe 2.5 -- the decisive test for FAR-C002.

Pure random greedy fills columns left to right.  Measure the fraction of columns it
reaches before availability hits zero.  Uses the verified (A)/(B) split so each step
costs O(i) per placed column instead of O(n*i).

  (A) forbidden v = slopes:  2v = (phi_b - phi_a)/(f(b)-f(a)),  phi_j = f(j)^2+(i-j)^2
  (B) forbidden v: (v-f(a))^2 = d - (i-a)^2 for d already used at apex a
                   -> requires d-(i-a)^2 to be a perfect square

If frontier/n decays to 0, one-per-column sets do NOT exist for large n and C002 is
FALSE.  If it plateaus at a constant, C002 stays alive.
"""
import random, math, sys
from math import isqrt

def greedy_frontier(n, seed):
    rnd = random.Random(seed)
    f = []
    used = []           # used[a] = set of squared distances at apex a
    for i in range(n):
        forb = set()
        # (B) old apexes
        for a in range(i):
            off = (i-a)**2
            fa = f[a]
            for d in used[a]:
                t = d - off
                if t < 0: continue
                r = isqrt(t)
                if r*r == t:
                    forb.add(fa + r); forb.add(fa - r)
        # (A) new apex: slopes
        phi = [f[j]*f[j] + (i-j)**2 for j in range(i)]
        for a in range(i):
            fa, pa = f[a], phi[a]
            for b in range(a+1, i):
                fb, pb = f[b], phi[b]
                if fa == fb:
                    continue                     # no v excluded unless pa==pb (prefix valid => not)
                num, den = pb - pa, 2*(fb - fa)
                if num % den == 0:
                    forb.add(num // den)
        cand = [v for v in range(n) if v not in forb]
        if not cand:
            return i
        v = rnd.choice(cand)
        newd = set()
        for a in range(i):
            d = (i-a)**2 + (v-f[a])**2
            used[a].add(d); newd.add(d)
        used.append(newd); f.append(v)
    return n

print("   n   seeds   max frontier   mean frontier   max/n    mean/n")
for n in (32, 48, 64, 96, 128, 160, 192):
    seeds = 12 if n <= 128 else 6
    res = [greedy_frontier(n, s) for s in range(seeds)]
    mx, mean = max(res), sum(res)/len(res)
    print("%5d %6d %13d %14.1f %8.3f %8.3f" % (n, seeds, mx, mean, mx/n, mean/n))
    sys.stdout.flush()
