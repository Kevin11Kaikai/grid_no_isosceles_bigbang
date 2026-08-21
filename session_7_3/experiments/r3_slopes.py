# -*- coding: utf-8 -*-
"""Round 3, probe 3.1 -- is the union bound REALLY vacuous?

Round 2 counted ~i^2/2 slope-pairs and concluded the union bound loses a factor n.
But that count assumed every pair forbids a value.  It does not:

  phi_j = f(j)^2 + (i-j)^2 ,  P_j = (f(j), phi_j)
  slope(a,b) = (x_a + x_b) + (b'^2 - a'^2)/(x_b - x_a),   a' = i-a, b' = i-b

A pair forbids a value only if the slope is an EVEN INTEGER LANDING IN [0,2n).
Since x_a + x_b is already in [0,2n), the correction term must be small AND the
division must be exact.  Most pairs fail both.  Measure the EFFECTIVE count.

Note the structure: P_j sits on the parabola y = x^2 translated up by (i-j)^2, so for
points with equal (i-j) the slope is exactly x_a + x_b -- the plain 3-AP/midpoint case.
"""
import random, sys
from math import isqrt

def measure(n, seed=0, frac_points=(0.25, 0.5, 0.75, 0.9)):
    """build a valid prefix by random greedy, and at chosen fractions report
       (pairs, pairs_effective, distinct_forbidden_A, distinct_forbidden_B, avail)"""
    rnd = random.Random(seed)
    f = []; used = []
    marks = sorted(set(int(n*t) for t in frac_points))
    out = []
    for i in range(n):
        forbA = set(); forbB = set()
        pairs = 0; pairs_eff = 0
        for a in range(i):
            off = (i-a)**2; fa = f[a]
            for d in used[a]:
                t = d - off
                if t < 0: continue
                r = isqrt(t)
                if r*r == t:
                    forbB.add(fa + r); forbB.add(fa - r)
        phi = [f[j]*f[j] + (i-j)**2 for j in range(i)]
        for a in range(i):
            fa, pa = f[a], phi[a]
            for b in range(a+1, i):
                fb, pb = f[b], phi[b]
                pairs += 1
                if fa == fb: continue
                num, den = pb - pa, 2*(fb - fa)
                if num % den: continue          # not an integer -> forbids nothing
                v = num // den
                pairs_eff += 1                  # integer slope
                if 0 <= v < n: forbA.add(v)
        allforb = forbA | set(x for x in forbB if 0 <= x < n)
        if i in marks:
            out.append((i, pairs, pairs_eff, len(forbA), len(forbB & set(range(n))),
                        n - len(allforb)))
        cand = [v for v in range(n) if v not in allforb]
        if not cand:
            out.append((i, pairs, pairs_eff, len(forbA), -1, 0))
            return out, i
        v = rnd.choice(cand)
        nd = set()
        for a in range(i):
            d = (i-a)**2 + (v-f[a])**2
            used[a].add(d); nd.add(d)
        used.append(nd); f.append(v)
    return out, n

print("Effective slope-pair count vs the naive i^2/2, and distinct forbidden values.")
print("  n    i     pairs=i^2/2   integer-slope   ratio     |forbA|  |forbB|  avail")
for n in (48, 64, 96, 128):
    rows, reach = measure(n, seed=n)
    for (i, pr, pe, fa, fb, av) in rows:
        ratio = pe/pr if pr else 0
        print("%4d %4d %13d %15d %8.4f %8s %8s %6s"
              % (n, i, pr, pe, ratio, fa, fb if fb >= 0 else "-", av))
    print("      -> greedy reached %d/%d = %.3f" % (reach, n, reach/n))
    sys.stdout.flush()
