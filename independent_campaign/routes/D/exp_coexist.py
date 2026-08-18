"""Rigorous one-sided test: CONSTRUCT a legal set inside a union of two
blocks of side n hitting the target 2*C(n).  A success is a PROOF that the
pairwise deficit for that decomposition is exactly 0 at that n.
Failure proves nothing (heuristic).
"""
import sys, time, json
from iso import is_legal
from search import LS

CK = {1:1,2:2,3:4,4:6,5:7,6:9,7:10,8:13,9:16,10:18,11:18,16:28,27:48,32:56}

def quad(n, ij):
    i, j = ij
    return [(i*n+x, j*n+y) for x in range(n) for y in range(n)]

def resid(n, ij, k=2):
    i, j = ij
    return [(i+k*x, j+k*y) for x in range(n) for y in range(n)]

LAYOUTS = {
  'contig-diag' : lambda n: quad(n,(0,0)) + quad(n,(1,1)),
  'contig-adj'  : lambda n: quad(n,(0,0)) + quad(n,(0,1)),
  'res-diag'    : lambda n: resid(n,(0,0)) + resid(n,(1,1)),
  'res-adj'     : lambda n: resid(n,(0,0)) + resid(n,(0,1)),
  'far-diag'    : lambda n: quad(n,(0,0)) + [(3*n+x,3*n+y) for x in range(n) for y in range(n)],
}

def attack(pts, target, budget_s=60, seed=0):
    best, BS = 0, None
    t0 = time.time()
    sd = seed
    while time.time()-t0 < budget_s and best < target:
        ls = LS(pts, seed=sd); sd += 1
        v, S = ls.run(iters=25000, restarts=1)
        if v > best:
            best, BS = int(v), ls.to_pts(S)
    return best, BS

if __name__ == '__main__':
    ns = [int(x) for x in sys.argv[1:]] or [4,5,6,7,8]
    budget = 45
    print(f"{'layout':>12} {'n':>3} {'2C(n)':>6} {'found':>6} {'ratio/C(n)':>10} {'verdict':>10}")
    for name, f in LAYOUTS.items():
        for n in ns:
            c = CK[n]; target = 2*c
            pts = f(n)
            b, S = attack(pts, target, budget_s=budget, seed=n*17)
            ok, w = is_legal(S)
            assert ok, (name, n, w)
            verdict = 'ZERO-DEF' if b >= target else ('over?!' if b > target else 'gap>=%d' % (target-b))
            print(f"{name:>12} {n:>3} {target:>6} {b:>6} {b/c:>10.3f} {verdict:>10}", flush=True)
