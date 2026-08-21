# -*- coding: utf-8 -*-
"""Round 7, probe 7.1 -- does greedy/n tend to a POSITIVE CONSTANT or to ZERO?

Round 6 measured alpha ~ 0.09 in  g/n = c (log n)^{-alpha}  and could not tell whether
that decay is real (=> the conjectured route FAILS) or a finite-size artefact.

Theory supplies the discriminating functional form.  Availability ~ exp(-D m^2/N^2)
gives  Int_0^M e^{a m^2} dm = N  with a = D/N^2, hence a M^2 = ln(2 a M N), and with
M = gamma*n, D = K n^2 ln n, N = n^2:

        K gamma^2 ln n = ln n + lnln n + O(1)
   =>   gamma^2 = A + B * (lnln n / ln n) + C / ln n          <-- LINEAR in A,B,C
   with gamma -> sqrt(A) > 0.

Rival:  gamma = c (ln n)^{-alpha}  =>  ln gamma = ln c - alpha * lnln n   -> 0.

Both are linear least squares.  Fit, compare residuals, and read off A.
"""
import math

DATA = [  # n, greedy mean, #seeds
    (64,     68.00, 20), (128,  135.35, 20), (256,  268.00, 20),
    (512,   532.85, 20), (1024,1056.00, 20), (2048, 2088.20, 10),
    (4096, 4137.50,  6), (8192, 8214.00,  1),
]

def lstsq(A, y):
    """normal equations, small dense"""
    p = len(A[0]); n = len(A)
    M = [[sum(A[i][r]*A[i][c] for i in range(n)) for c in range(p)] for r in range(p)]
    b = [sum(A[i][r]*y[i] for i in range(n)) for r in range(p)]
    for c in range(p):                      # gaussian elimination
        piv = max(range(c, p), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]; b[c], b[piv] = b[piv], b[c]
        for r in range(p):
            if r == c: continue
            f = M[r][c]/M[c][c]
            for k in range(c, p): M[r][k] -= f*M[c][k]
            b[r] -= f*b[c]
    return [b[r]/M[r][r] for r in range(p)]

def report(name, pred, params):
    ss = 0.0; print("  %-34s" % name, end="")
    for (n, g, _) in DATA:
        r = g/n - pred(n)
        ss += r*r
    print("RSS(g/n) = %.3e   params = %s" % (ss, ["%.4f" % p for p in params]))
    return ss

for label, subset in (("ALL n=64..8192", DATA), ("n>=128 only", DATA[1:])):
    print("\n=== %s ===" % label)
    D = subset
    L = [math.log(n) for (n, _, _) in D]
    LL = [math.log(math.log(n)) for (n, _, _) in D]
    G = [g/n for (n, g, _) in D]

    # Model L2: gamma^2 = A + B*(lnln/ln)
    A2 = [[1.0, LL[i]/L[i]] for i in range(len(D))]
    y2 = [g*g for g in G]
    pL2 = lstsq(A2, y2)
    # Model L3: gamma^2 = A + B*(lnln/ln) + C/ln
    A3 = [[1.0, LL[i]/L[i], 1.0/L[i]] for i in range(len(D))]
    pL3 = lstsq(A3, y2)
    # Model P: ln gamma = ln c - alpha*lnln
    AP = [[1.0, -LL[i]] for i in range(len(D))]
    yP = [math.log(g) for g in G]
    pP = lstsq(AP, yP)

    DATA_bak = DATA
    globals()['DATA'] = D
    report("L2: gamma^2 = A + B lnln/ln", lambda n: math.sqrt(max(1e-9, pL2[0] + pL2[1]*math.log(math.log(n))/math.log(n))), pL2)
    report("L3: + C/ln n",                lambda n: math.sqrt(max(1e-9, pL3[0] + pL3[1]*math.log(math.log(n))/math.log(n) + pL3[2]/math.log(n))), pL3)
    report("P : gamma = c (ln n)^-alpha", lambda n: math.exp(pP[0] - pP[1]*math.log(math.log(n))), pP)
    globals()['DATA'] = DATA_bak
    print("     -> L2 limit gamma_inf = sqrt(A) = %.4f      (implied K = 1/A = %.3f)" % (math.sqrt(pL2[0]), 1/pL2[0]))
    print("     -> L3 limit gamma_inf = sqrt(A) = %.4f" % (math.sqrt(pL3[0]) if pL3[0] > 0 else float('nan')))
    print("     -> P  says gamma -> 0, with alpha = %.4f" % pP[1])

# ---------------------------------------------------------------- out-of-sample
print("\n=== OUT-OF-SAMPLE TEST: fit on n<=4096, predict n=8192 (measured 1.00269) ===")
TRAIN = [d for d in DATA if d[0] <= 4096]
L=[math.log(n) for (n,_,_) in TRAIN]; LL=[math.log(math.log(n)) for (n,_,_) in TRAIN]
G=[g/n for (n,g,_) in TRAIN]
u8=math.log(math.log(8192))/math.log(8192); w8=1.0/math.log(8192); ll8=math.log(math.log(8192))
pL2=lstsq([[1.0,LL[i]/L[i]] for i in range(len(TRAIN))],[g*g for g in G])
pL3=lstsq([[1.0,LL[i]/L[i],1.0/L[i]] for i in range(len(TRAIN))],[g*g for g in G])
pP =lstsq([[1.0,-LL[i]] for i in range(len(TRAIN))],[math.log(g) for g in G])
meas=1.00269
for nm,val in (("L2",math.sqrt(pL2[0]+pL2[1]*u8)),
               ("L3",math.sqrt(pL3[0]+pL3[1]*u8+pL3[2]*w8)),
               ("P ",math.exp(pP[0]-pP[1]*ll8))):
    print("   %s predicts g/n(8192) = %.5f   error %+.2f%%" % (nm,val,100*(val-meas)/meas))

print("\n=== AIC (k = #params, 8 points) ===")
import math as _m
for nm,rss,k in (("L2",5.804e-05,2),("L3",8.193e-06,3),("P ",1.040e-04,2)):
    print("   %s  AIC = %.1f" % (nm, 8*_m.log(rss/8)+2*k))
