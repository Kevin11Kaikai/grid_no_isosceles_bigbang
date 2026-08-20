# -*- coding: utf-8 -*-
"""Round 2, probes 2.3 and 2.4 for FAR-C002.

2.3  SLOPE REFORMULATION (representation shift).
     When column i is added with value v, the constraints split exactly two ways.
     (A) apex = the new column i.  For a,b < i:
             (i-a)^2 + (v-f(a))^2 = (i-b)^2 + (v-f(b))^2
         The v^2 cancels, leaving a LINEAR equation:
             2v (f(b)-f(a)) = phi_b - phi_a ,   phi_j := f(j)^2 + (i-j)^2
         i.e. 2v is the SLOPE of the line through P_a=(f(a),phi_a), P_b=(f(b),phi_b).
         So: v is legal for apex i  <=>  2v is not a slope determined by {P_j : j<i}.
     (B) apex = an old column a.  Needs d - (i-a)^2 to be a perfect square for some
         already-used distance d at a -- a sum-of-two-squares condition, hence rare.
     This script verifies (A) and (B) against the direct definition, then measures how
     many values stay available at each greedy step.

2.4  AVAILABILITY PROFILE.  If the count of legal values stays Omega(n) throughout,
     that is the structural reason backtracking succeeds even though the union bound
     over forbidden values is vacuous (it gives ~n^2/8 forbidden vs only n available).
"""
import random, sys
from fractions import Fraction

def legal_direct(f, i, v, n):
    """is value v legal for column i, given f[0..i-1]? (from the definition)"""
    pts = [(j, f[j]) for j in range(i)] + [(i, v)]
    for (a, fa) in pts:
        seen = set()
        for (b, fb) in pts:
            if a == b: continue
            d = (a-b)**2 + (fa-fb)**2
            if d in seen: return False
            seen.add(d)
    return True

def legal_slope(f, i, v, n, used):
    """same test via the (A)/(B) split.  `used[a]` = set of squared distances at apex a."""
    # (A) 2v must not be a slope of the phi-point set
    for a in range(i):
        for b in range(a+1, i):
            if f[a] == f[b]:
                # vertical: equation becomes 0 = phi_b - phi_a, independent of v
                if f[b]**2 + (i-b)**2 == f[a]**2 + (i-a)**2: return False
                continue
            pa = f[a]**2 + (i-a)**2
            pb = f[b]**2 + (i-b)**2
            if Fraction(pb - pa, 2*(f[b]-f[a])) == v: return False
    # (B) new distance from old apex a must not repeat one already used at a
    for a in range(i):
        d = (i-a)**2 + (v-f[a])**2
        if d in used[a]: return False
    return True

print("=== Probe 2.3  verifying the slope reformulation against the definition ===")
rnd = random.Random(7)
mismatch = tested = 0
for trial in range(300):
    n = rnd.choice([6, 8, 10, 12])
    i = rnd.randint(2, n-1)
    f = [rnd.randrange(n) for _ in range(i)]
    used = [set() for _ in range(i)]
    ok_prefix = True
    for a in range(i):
        for b in range(i):
            if a == b: continue
            d = (a-b)**2 + (f[a]-f[b])**2
            if d in used[a]: ok_prefix = False
            used[a].add(d)
    if not ok_prefix: continue          # only test valid prefixes
    for v in range(n):
        tested += 1
        if legal_direct(f, i, v, n) != legal_slope(f, i, v, n, used):
            mismatch += 1
print("  (value, prefix) pairs tested: %d   mismatches: %d   %s"
      % (tested, mismatch, "REFORMULATION VERIFIED" if mismatch == 0 else "WRONG"))

print()
print("=== Probe 2.4  availability profile along a successful greedy run ===")
def profile(n, seed=1, tries=200):
    rnd = random.Random(seed)
    for _ in range(tries):
        f = []; used = []; prof = []
        ok = True
        for i in range(n):
            cand = []
            for v in range(n):
                good = True
                for a in range(i):
                    d = (i-a)**2 + (v-f[a])**2
                    if d in used[a]: good = False; break
                if good:
                    seen = set();
                    for a in range(i):
                        d = (i-a)**2 + (v-f[a])**2
                        if d in seen: good = False; break
                        seen.add(d)
                if good: cand.append(v)
            prof.append(len(cand))
            if not cand: ok = False; break
            v = rnd.choice(cand)
            for a in range(i):
                used[a].add((i-a)**2 + (v-f[a])**2)
            used.append({(i-a)**2 + (v-f[a])**2 for a in range(i)})
            f.append(v)
        if ok: return f, prof
    return None, prof

for n in (32, 64, 96, 128):
    f, prof = profile(n, seed=n)
    if f is None:
        print("  n=%3d  no run completed; profile reached step %d, min avail %d"
              % (n, len(prof), min(prof)))
        continue
    q = [prof[int(len(prof)*t)] for t in (0.25, 0.5, 0.75, 0.9)]
    print("  n=%3d  avail at 25%%/50%%/75%%/90%% = %4d %4d %4d %4d   final=%3d   min=%3d  (min/n=%.3f)"
          % (n, q[0], q[1], q[2], q[3], prof[-1], min(prof), min(prof)/n))
