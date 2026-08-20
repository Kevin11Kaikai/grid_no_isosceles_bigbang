# -*- coding: utf-8 -*-
"""Round 3, probe 3.2 -- independent re-verification of the moment sums

    M_j(R) = sum_{r<=R} r_2(r)^j ,   r_2(r) = #{u in Z^2 : |u|^2 = r}

The iso6 archive claims M_j(R) ~ c_j * R * (log R)^{2^{j-1}-1}, i.e. exponents 0,1,3,7.
That exponent is the crux of the Round 3 kill, so it is recomputed here from scratch
(sieve over lattice points, no reuse of iso6 code).
"""
import math, sys

def r2_table(R):
    t = [0]*(R+1)
    m = math.isqrt(R)
    for x in range(-m, m+1):
        x2 = x*x
        if x2 > R: continue
        ymax = math.isqrt(R - x2)
        for y in range(-ymax, ymax+1):
            t[x2 + y*y] += 1
    return t

for R in (250_000, 1_000_000, 4_000_000):
    t = r2_table(R)
    M = [0]*5
    for r in range(1, R+1):
        v = t[r]
        if v:
            p = 1
            for j in range(1, 5):
                p *= v
                M[j] += p
    L = math.log(R)
    print("R = %d   max r_2 = %d" % (R, max(t)))
    for j in range(1, 5):
        e = 2**(j-1) - 1
        print("   M%d/(R*log^%d R) = %12.5f" % (j, e, M[j]/(R * L**e)))
    sys.stdout.flush()

print()
print("Consequence for the degree-k relaxation route (B6 sharp form):")
print("   |S_k| = Theta( n^{2-2/(k+1)} / (log n)^{(2^k-1)/(k+1)} )")
print("   k :  n-exponent   log-penalty exponent (2^k-1)/(k+1)")
for k in range(1, 13):
    print("  %2d :   %8.4f   %14.2f" % (k, 2 - 2/(k+1), (2**k - 1)/(k+1)))
