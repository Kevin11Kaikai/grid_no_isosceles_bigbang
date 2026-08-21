# -*- coding: utf-8 -*-
"""Round 5, probe 5.4 -- THE UNIFYING FORMULA.

For an apex a let N_a(d) = #{b : |a-b|^2 = d}.  The probability that two random
other points are equidistant from a common random apex is

    P  =  E_a[ Sum_d N_a(d)^2 ] / (V-1)^2 ,      V = #points in the ambient.

Alteration/greedy: bad triples ~ m^3 P, repairable while m^3 P < m, i.e.

    m  <  P^{-1/2}          <<< THE THRESHOLD EVERY ROUND HAS HIT >>>

Claim:  P^{-1/2} = n/sqrt(c log n) in [n]^2  (= the KNOWN bound), and
        P^{-1/2} = sqrt(p)                    in F_p^2  (= probe 5.3's measurement).
Measure both.
"""
import sys, math

def P_grid(n):
    tot = 0.0; V = n*n
    for ax in range(n):
        for ay in range(n):
            cnt = {}
            for bx in range(n):
                dx2 = (ax-bx)**2
                for by in range(n):
                    d = dx2 + (ay-by)**2
                    cnt[d] = cnt.get(d, 0) + 1
            s = sum(c*c for c in cnt.values()) - 1     # drop b == a
            tot += s
    return tot / V / (V-1)**2

def P_fp(p):
    tot = 0.0; V = p*p
    for ax in range(p):
        for ay in range(p):
            cnt = {}
            for bx in range(p):
                dx2 = (ax-bx)**2
                for by in range(p):
                    d = (dx2 + (ay-by)**2) % p
                    cnt[d] = cnt.get(d, 0) + 1
            s = sum(c*c for c in cnt.values()) - 1
            tot += s
    return tot / V / (V-1)**2

print("AMBIENT [n]^2 :  threshold P^{-1/2}  vs  the known bound n/sqrt(log n)")
print("    n         P        P^-1/2    n/sqrt(ln n)   ratio    P*n^2/ln n")
for n in (8, 12, 16, 24, 32, 48, 64):
    P = P_grid(n)
    th = P**-0.5
    kn = n/math.sqrt(math.log(n))
    print("%5d %10.3e %9.2f %13.2f %8.3f %11.3f"
          % (n, P, th, kn, th/kn, P*n*n/math.log(n)))
    sys.stdout.flush()

print()
print("AMBIENT F_p^2 :  threshold P^{-1/2}  vs  sqrt(p)   and vs measured A(p)")
AMEAS = {11:7, 19:10, 23:11, 31:13, 43:16, 59:19, 79:22, 103:26}
print("    p         P        P^-1/2    sqrt(p)   P*p     A(p)   A(p)/P^-1/2")
for p in (11, 19, 23, 31, 43, 59, 79, 103):
    P = P_fp(p)
    th = P**-0.5
    print("%5d %10.3e %9.2f %9.2f %6.3f %6d %11.3f"
          % (p, P, th, math.sqrt(p), P*p, AMEAS[p], AMEAS[p]/th))
    sys.stdout.flush()
