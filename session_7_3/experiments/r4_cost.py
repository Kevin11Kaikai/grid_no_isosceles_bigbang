# -*- coding: utf-8 -*-
"""Round 4, probe 4.3 -- what does condition (H) actually COST?

For a recurrence into [2n]^2 the offset must be (+-1,+-1) (larger offsets
overflow the box), and all four are equivalent under reflection.  So measure

        rho(n) = C_H(n) / C_greedy(n)      offset (1,1)

with the SAME greedy on both sides, so the comparison is fair.

Prediction.  Isosceles-freeness imposes, per apex, injectivity of ONE
r_2-type quadratic form on S.  Condition (H) adds the rows and the columns of
G(s,s') = |2(s-s')+(1,1)|^2 -- and by (2w+1)^2+(2z+1)^2 = 8(T(w)+T(z))+2 that
form has the SAME representation statistics as r_2.  So (H) triples the
constraint count.  A greedy whose size solves m^3/D ~ m gives m ~ sqrt(D),
hence

        rho(n) -> 1/sqrt(3) = 0.5774 .

If rho really converges to a constant < 1, iterating the doubling gives
density rho^k -> 0 and the route CANNOT reach Omega(n).
"""
import sys
from r4_double import greedy

SEEDS = 300
print("rho(n) = C_H(n)/C_greedy(n), offset (1,1), %d seeds each" % SEEDS)
print("   n   C_greedy   C_H     rho     1/sqrt(3)=0.5774")
for n in (6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48):
    sd = SEEDS if n <= 24 else (120 if n <= 32 else 40)
    plain = max(len(greedy(n, None, s)) for s in range(sd))
    h     = max(len(greedy(n, (1,1), s)) for s in range(sd))
    print("%4d %9d %6d %8.3f" % (n, plain, h, h/plain))
    sys.stdout.flush()
