# -*- coding: utf-8 -*-
"""Round 2, probes 2.1 and 2.2 for FAR-C002.

2.1  Sub-barrier: how far can the STRENGTHENING "all pairwise distances distinct"
     (a 2-D Golomb/Sidon set) go?  Such a set is trivially isosceles-free, so if it
     could reach cn it would settle C(n)=Omega(n).  Counting cap:
        C(m,2) <= #distinct squared distances realised in [n]^2 =: Ndist(n)
     and Ndist(n) ~ K*2n^2/sqrt(log n)  (Landau-Ramanujan), so m = O(n/(log n)^{1/4}).
     SUBLINEAR -> the route cannot work.  Measured here exactly.

2.2  Explicit algebraic one-per-column maps f:[n]->[n].  The iso6 archive reports that
     no algebraic family it tried was isosceles-free as a grid subset; this re-tests the
     question in the ONE-PER-COLUMN setting, which is the shape C002 needs.
"""
import math, sys

def ndist(n):
    """number of distinct squared distances realised between points of [n]^2"""
    return len({dx*dx+dy*dy for dx in range(n) for dy in range(-n+1, n)} - {0})

def cap_from_count(N):
    """largest m with m(m-1)/2 <= N"""
    return int((1 + math.isqrt(1 + 8*N)) // 2)

print("=== Probe 2.1  all-distances-distinct sub-barrier ===")
print("  n   Ndist(n)   cap m   cap/n    n/(log n)^(1/4)")
for n in [8, 16, 32, 64, 128, 256, 512, 1024]:
    N = ndist(n)
    m = cap_from_count(N)
    ref = n/(math.log(n)**0.25)
    print("%5d %9d %7d %7.3f %14.1f" % (n, N, m, m/n, ref))
print("  -> cap/n is DECREASING; the strengthening is capped strictly below n.")

print()
print("=== Probe 2.2  explicit algebraic one-per-column maps ===")

def viol(f, n):
    """number of (apex, unordered pair) isosceles violations"""
    bad = 0
    for a in range(n):
        seen = {}
        for b in range(n):
            if a == b: continue
            d = (a-b)**2 + (f[a]-f[b])**2
            seen[d] = seen.get(d, 0) + 1
        bad += sum(c*(c-1)//2 for c in seen.values())
    return bad

def isprime(x):
    if x < 2: return False
    for p in range(2, int(x**0.5)+1):
        if x % p == 0: return False
    return True

fams = {
    "i^2 mod n":        lambda i, n: (i*i) % n,
    "i^3 mod n":        lambda i, n: (i*i*i) % n,
    "2^i mod n":        lambda i, n: pow(2, i, n),
    "3^i mod n":        lambda i, n: pow(3, i, n),
    "i^-1 mod n":       lambda i, n: pow(i, -1, n) if math.gcd(i, n) == 1 else 0,
    "floor(i^2/n)":     lambda i, n: (i*i)//n,
    "i*round(sqrt n)%n":lambda i, n: (i*round(n**0.5)) % n,
    "Costas Welch g^i": lambda i, n: pow(3, i, n+1) - 1 if isprime(n+1) else None,
}

for name, g in fams.items():
    row = []
    for n in (16, 32, 64, 128):
        try:
            f = [g(i, n) for i in range(n)]
            if any(v is None or not (0 <= v < n) for v in f): row.append("  n/a"); continue
            row.append("%5d" % viol(f, n))
        except Exception:
            row.append("  err")
    print("  %-20s violations at n=16,32,64,128: %s" % (name, " ".join(row)))
print("  (0 would mean an explicit construction; anything else is a failure)")
