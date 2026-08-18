"""EXP1.  (a) Observed C(kn)/C(n) and implied alpha from the sealed exact data.
       (b) The SAME statistic for r_3, where the recurrence is PROVABLY false.
Everything here is arithmetic on known/computed exact values.
"""
import sys, math, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import KNOWN

R3 = {}
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'r3.txt')
if os.path.exists(p):
    for line in open(p):
        f = line.split()
        if len(f) >= 2:
            R3[int(f[0])] = int(f[1])

print("=" * 78)
print("TABLE 1.  C(kn)/C(n) from the exact values, and alpha_obs = log_k(ratio)")
print("=" * 78)
print(f"{'k':>2} {'n':>3} {'kn':>4} {'C(n)':>5} {'C(kn)':>6} {'ratio':>7} {'k^2':>4} "
      f"{'delta_obs':>9} {'alpha_obs':>9} {'eff=ratio/k^2':>13}")
rows = []
for k in (2, 3, 4, 8, 16):
    for n in sorted(KNOWN):
        m = k * n
        if m not in KNOWN:
            continue
        r = KNOWN[m] / KNOWN[n]
        al = math.log(r) / math.log(k)
        rows.append((k, n, m, r, al))
        print(f"{k:>2} {n:>3} {m:>4} {KNOWN[n]:>5} {KNOWN[m]:>6} {r:>7.4f} {k*k:>4} "
              f"{k*k-r:>9.4f} {al:>9.4f} {r/k**2:>13.4f}")

print()
print("=" * 78)
print("TABLE 2.  CALIBRATION: identical statistic for r_3 (1-D), where the")
print("          recurrence r_3(kn) <= (k-delta) r_3(n) is PROVABLY FALSE")
print("          (it would force r_3(n)=O(n^beta), beta<1, contra Behrend).")
print("=" * 78)
if R3:
    print(f"{'k':>2} {'n':>3} {'kn':>4} {'r3(n)':>6} {'r3(kn)':>7} {'ratio':>7} {'k':>3} "
          f"{'delta_obs':>9} {'beta_obs':>9} {'eff=ratio/k':>12}")
    for k in (2, 3, 4):
        for n in sorted(R3):
            m = k * n
            if m not in R3:
                continue
            if n < 4:
                continue
            r = R3[m] / R3[n]
            be = math.log(r) / math.log(k)
            print(f"{k:>2} {n:>3} {m:>4} {R3[n]:>6} {R3[m]:>7} {r:>7.4f} {k:>3} "
                  f"{k-r:>9.4f} {be:>9.4f} {r/k:>12.4f}")
        print()
else:
    print("  (r3.txt not present)")

print("=" * 78)
print("TABLE 3.  delta needed for a target alpha:  lambda = k^alpha, delta=k^2-lambda")
print("=" * 78)
for k in (2, 3, 4, 8):
    line = f"  k={k}: "
    for al in (1.999, 1.99, 1.9, 1.5, 1.2, 1.0):
        line += f"a={al}:d>={k*k-k**al:7.4f}   "
    print(line)

print()
print("=" * 78)
print("TABLE 4.  is the exact data anywhere near the n^2 regime?")
print("=" * 78)
for n in sorted(KNOWN):
    print(f"  n={n:>2}  C={KNOWN[n]:>3}  C/n={KNOWN[n]/n:6.3f}  C/n^2={KNOWN[n]/n**2:7.4f}"
          f"  log_n C={math.log(KNOWN[n])/math.log(n) if n > 1 else float('nan'):7.4f}")
if R3:
    print()
    for n in sorted(R3):
        if n in (4, 8, 16, 32, 64, 6, 12, 24, 48):
            print(f"  n={n:>2}  r3={R3[n]:>3}  r3/n={R3[n]/n:6.3f}"
                  f"  log_n r3={math.log(R3[n])/math.log(n):7.4f}")
