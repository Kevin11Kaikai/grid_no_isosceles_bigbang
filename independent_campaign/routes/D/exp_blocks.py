"""Do near-extremal blocks coexist?  Exact answers on unions of 2 blocks."""
import sys, time
from iso import Exact, is_legal
from search import LS

CK = {1:1,2:2,3:4,4:6,5:7,6:9,7:10,8:13,9:16,10:18,11:18,16:28,27:48,32:56}

def quad(n, which):
    """contiguous quadrant of [2n]^2: which=(i,j) in {0,1}^2"""
    i, j = which
    return [(i*n+x, j*n+y) for x in range(n) for y in range(n)]

def resid(n, which, k=2):
    """residue class {(x,y): x=i, y=j mod k} inside [k n]^2 -- a scaled copy."""
    i, j = which
    return [(i+k*x, j+k*y) for x in range(n) for y in range(n)]

def exact_max(pts, lb=0):
    e = Exact(pts)
    v, s = e.solve(lb=lb)
    return v, s, e.nodes

def heur_max(pts, seed=0, iters=30000, restarts=2, tries=4):
    best, BS = -1, None
    for sd in range(tries):
        ls = LS(pts, seed=seed+sd)
        v, S = ls.run(iters=iters, restarts=restarts)
        if v > best:
            best, BS = v, ls.to_pts(S)
    return int(best), BS

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'exact'
    ns = [int(x) for x in sys.argv[2:]] or [2,3,4]
    print(f"{'n':>3} {'C(n)':>5} {'2C':>4} | {'contig-diag':>11} {'contig-adj':>10} | {'res-diag':>8} {'res-adj':>8}")
    for n in ns:
        c = CK.get(n)
        sets = {
          'contig-diag': quad(n,(0,0)) + quad(n,(1,1)),
          'contig-adj' : quad(n,(0,0)) + quad(n,(0,1)),
          'res-diag'   : resid(n,(0,0)) + resid(n,(1,1)),
          'res-adj'    : resid(n,(0,0)) + resid(n,(0,1)),
        }
        out = {}
        for k, pts in sets.items():
            t = time.time()
            if mode == 'exact':
                v, s, nd = exact_max(pts)
            else:
                v, s = heur_max(pts)
            ok, _ = is_legal(s)
            assert ok, k
            out[k] = v
            print(f"   [{k}] n={n}: {v}  ({time.time()-t:.1f}s)", flush=True)
        print(f"{n:>3} {c!s:>5} {2*c if c else '?':>4} | "
              f"{out['contig-diag']:>11} {out['contig-adj']:>10} | "
              f"{out['res-diag']:>8} {out['res-adj']:>8}", flush=True)
