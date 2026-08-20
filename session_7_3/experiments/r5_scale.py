# -*- coding: utf-8 -*-
"""Round 5, probe 5.3 -- does A(p)/p plateau, and is there an ALGEBRAIC family?

(a) randomized greedy lower bounds on A(p) for p up to ~400
(b) explicit families:  graph of a monomial {(t, t^k)}, the multiplicative-subgroup
    'circle' {x in F_p^2 : N(x)=c}, and Welch/Costas-style {(t, g^t)}.
    A family with 0 violations at size ~p would be a THEOREM: C(n) = Omega(n).
"""
import random, sys

def greedy_A(p, seed, order=None):
    pts = [(x, y) for x in range(p) for y in range(p)]
    rnd = random.Random(seed); rnd.shuffle(pts)
    S = []; seen = []
    for c in pts:
        sd = set(); ok = True
        for i, a in enumerate(S):
            v = ((a[0]-c[0])**2 + (a[1]-c[1])**2) % p
            if v in seen[i] or v in sd: ok = False; break
            sd.add(v)
        if not ok: continue
        for i, a in enumerate(S):
            seen[i].add(((a[0]-c[0])**2 + (a[1]-c[1])**2) % p)
        S.append(c); seen.append(sd)
    return S

PRIMES = [11, 19, 23, 31, 43, 47, 59, 67, 79, 83, 103, 127, 151, 199, 251, 307, 401]
print("(a) greedy lower bounds on A(p).   Does A(p)/p plateau?")
print("    p   p%4   greedy A(p)   /p")
for p in PRIMES:
    tries = 60 if p <= 103 else (20 if p <= 251 else 8)
    best = max((greedy_A(p, s) for s in range(tries)), key=len)
    print("%5d %5d %13d %6.3f" % (p, p % 4, len(best), len(best)/p))
    sys.stdout.flush()

print()
print("(b) explicit algebraic families -- violations (0 would be a theorem)")

def violations(p, pts):
    bad = 0
    for a in pts:
        seen = set()
        for b in pts:
            if a == b: continue
            v = ((a[0]-b[0])**2 + (a[1]-b[1])**2) % p
            if v in seen: bad += 1
            seen.add(v)
    return bad

for p in (11, 19, 23, 31, 43, 59, 79, 103):
    rows = []
    bestk, bestv = None, None
    for k in range(2, p-1):
        pts = [(t, pow(t, k, p)) for t in range(p)]
        v = violations(p, pts)
        if bestv is None or v < bestv: bestk, bestv = k, v
    # circle N(x)=1 : x^2+y^2 = 1
    circ = [(x, y) for x in range(p) for y in range(p) if (x*x+y*y) % p == 1]
    vc = violations(p, circ)
    # Welch/Costas style
    g = next(a for a in range(2, p) if len({pow(a, i, p) for i in range(1, p)}) == p-1)
    wel = [(i, pow(g, i, p)) for i in range(1, p)]
    vw = violations(p, wel)
    print("p=%3d  best monomial k=%-3d viol=%-6d | circle |C|=%-4d viol=%-6d | Welch viol=%d"
          % (p, bestk, bestv, len(circ), vc, vw))
    sys.stdout.flush()
