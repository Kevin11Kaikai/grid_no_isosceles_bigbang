"""Finite-data tests of every recurrence C(kn) <= lam*C(n) against the exact
values, plus the exponent accounting alpha = log_k(lam)."""
import math

CK = {1:1,2:2,3:4,4:6,5:7,6:9,7:10,8:13,9:16,10:18,11:18,16:28,27:48,32:56}
LO = {12:20}; HI = {12:23}

def lo(n): return CK.get(n, LO.get(n))
def hi(n): return CK.get(n, HI.get(n))

print("=== Table 1: exact/known values ===")
for n in sorted(set(list(CK)+list(LO))):
    if n in CK: print(f"  C({n:>2}) = {CK[n]}")
    else: print(f"  C({n:>2}) in [{LO[n]},{HI[n]}]")

print("\n=== Table 2: observed ratio C(kn)/C(n), and implied alpha=log_k(ratio) ===")
print(f"{'k':>2} {'n':>3} {'kn':>3} {'C(n)':>6} {'C(kn)':>7} {'ratio':>8} {'k^2':>4} "
      f"{'delta_obs':>10} {'alpha_obs':>9}")
rows = []
for k in (2,3,4,5,6,8,16,27,32):
    for n in sorted(set(list(CK)+list(LO))):
        m = k*n
        a, b = hi(n), lo(m)          # ratio lower bd needs C(kn) low, C(n) high
        a2, b2 = lo(n), hi(m)
        if a is None or b is None: continue
        if k < 2: continue
        r_lo = b/a; r_hi = hi(m)/lo(n) if (hi(m) and lo(n)) else None
        exact = (n in CK and m in CK)
        rr = CK[m]/CK[n] if exact else None
        s = f"{k:>2} {n:>3} {m:>3} {CK.get(n,'?'):>6} {CK.get(m,'?'):>7} "
        if exact:
            al = math.log(rr)/math.log(k)
            s += f"{rr:>8.4f} {k*k:>4} {k*k-rr:>10.4f} {al:>9.4f}"
        else:
            s += f"[{r_lo:.3f},{r_hi:.3f}]".rjust(8) + f" {k*k:>4}"
        print(s)

print("\n=== Table 3: how much delta would be needed for a given target alpha ===")
for k in (2,3,4,5,8):
    for al in (1.99, 1.95, 1.9, 1.5, 1.2, 1.0):
        lam = k**al
        print(f"  k={k}: alpha={al}  needs lam=k^alpha={lam:8.4f}  i.e. delta >= k^2-lam = {k*k-lam:8.4f}")
    print()

print("=== Table 4: C(n)/n and C(n)/n^2 (is the data anywhere near the n^2 regime?) ===")
for n in sorted(CK):
    print(f"  n={n:>2}  C={CK[n]:>3}  C/n={CK[n]/n:6.3f}  C/n^2={CK[n]/n**2:7.4f}  "
          f"log_n C = {math.log(CK[n])/math.log(n) if n>1 else float('nan'):6.4f}")
