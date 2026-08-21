# -*- coding: utf-8 -*-
"""Round 4, probe 4.4b -- M(q) under the EXACT separation criterion.

Probe 4.4 used only |qu+w|^2 = |w|^2 (mod q).  That is sound but not sharp:
for q=2 the finer invariant (even,even)->0 mod 4 vs (odd,odd)->2 mod 8 separates
a pair the mod-2 test cannot see.  So recompute with the exact criterion:

    classes v', v'' are separable at apex v
      <=>  Val(v-v') n Val(v-v'') = empty,   Val(w) = { |q*u + w|^2 : u in Z^2 }.

Val is tested up to a bound B; disjointness up to B is reported as separable
(EMPIRICAL -- a genuine collision above B would only make M(q) smaller, so the
resulting M(q) is an UPPER-friendly estimate: it can only over-state M).
"""
import sys
B = 300000     # test all |q*u+w|^2 <= B
from math import isqrt

def valset(q, w, B):
    S = set()
    lim = isqrt(B)
    u0lo = -(lim + abs(w[0])) // q - 2
    u0hi = (lim + abs(w[0])) // q + 2
    for ux in range(u0lo, u0hi + 1):
        X = q*ux + w[0]
        if X*X > B: continue
        rem = B - X*X
        lo = -(isqrt(rem) + abs(w[1])) // q - 2
        hi = (isqrt(rem) + abs(w[1])) // q + 2
        for uy in range(lo, hi + 1):
            Y = q*uy + w[1]
            v = X*X + Y*Y
            if v <= B: S.add(v)
    return S

def M_exact(q):
    reps = [(x, y) for x in range(q) for y in range(q)]
    V = {w: valset(q, w, B) for w in reps}
    # sep[w1][w2] = True if Val(w1) and Val(w2) are disjoint
    sep = {}
    for i, w1 in enumerate(reps):
        for w2 in reps[i:]:
            ok = V[w1].isdisjoint(V[w2])
            sep[(w1, w2)] = ok; sep[(w2, w1)] = ok
    N = len(reps)
    def diff(a, b):
        return ((reps[a][0]-reps[b][0]) % q, (reps[a][1]-reps[b][1]) % q)
    best = [0]; bw = [None]
    def ok(cur, c):
        for a in cur + [c]:
            others = [x for x in cur + [c] if x != a]
            ds = [diff(a, o) for o in others]
            for i in range(len(ds)):
                for j in range(i+1, len(ds)):
                    if not sep[(ds[i], ds[j])]: return False
        return True
    def bb(start, cur):
        if len(cur) + (N - start) <= best[0]: return
        if len(cur) > best[0]: best[0] = len(cur); bw[0] = list(cur)
        for c in range(start, N):
            if ok(cur, c):
                cur.append(c); bb(c+1, cur); cur.pop()
    bb(0, [])
    return best[0], [reps[i] for i in bw[0]]

print("M(q) under the EXACT criterion (Val sets tested to %d)." % B)
print("Density is preserved only if M(q) >= q.")
print("  q   M(q)   q    verdict            witness")
for q in range(2, 10):
    m, w = M_exact(q)
    verdict = "PRESERVES" if m >= q else "loses factor %.3f" % (m/q)
    print("%3d %5d %4d   %-18s %s" % (q, m, q, verdict, w))
    sys.stdout.flush()
