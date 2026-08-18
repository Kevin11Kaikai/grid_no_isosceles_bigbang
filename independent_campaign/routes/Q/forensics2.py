"""Forensics on any concrete Q4-feasible set."""
import numpy as np, sys, collections
from math import gcd
from qlib import q4_violations, iso_triples, prim_dir, bisector_has_lattice

def report(S, n, tag=''):
    m = len(S); P = S.astype(np.int64)
    v = q4_violations(S); nq = sum(len(t) for t in v.values())
    tri = iso_triples(S)
    print(f"=== {tag} n={n} |S|={m} Q4viol={nq} triples={len(tri)}")
    if not tri: return
    dirs = collections.Counter(); apex = collections.Counter()
    legs = collections.Counter(); r2c = collections.Counter()
    bl = []; ll = []; gcs = collections.Counter(); perp = 0
    pair = collections.Counter()
    for (ib, ia, ic, r2) in tri:
        A_, B_, C_ = P[ia], P[ib], P[ic]
        d = C_ - A_; e, g = prim_dir(d)
        dirs[e] += 1; gcs[g] += 1; apex[ib] += 1; r2c[r2] += 1
        pair[(min(ia, ic), max(ia, ic))] += 1
        bl.append(int(d[0]**2 + d[1]**2)); ll.append(int(r2))
        u = B_ - A_; w = C_ - B_
        legs[prim_dir(u)[0]] += 1; legs[prim_dir(w)[0]] += 1
        if int(u[0]*w[0] + u[1]*w[1]) == 0: perp += 1
        assert bisector_has_lattice(A_, C_)
    bl = np.array(bl); ll = np.array(ll)
    FIX = {(1,0),(0,1),(1,1),(1,-1)}
    inside = sum(c for e,c in dirs.items() if e in FIX)
    print(f" base dirs: {len(dirs)} distinct; in Q4 set: {inside} ({100*inside/len(tri):.2f}%)")
    print(f" top base dirs: {dirs.most_common(10)}")
    einf = collections.Counter(max(abs(e[0]),abs(e[1])) for e in dirs.elements())
    tot = sum(einf.values()); cum = 0
    s = []
    for k in sorted(einf):
        cum += einf[k]; s.append(f"{k}:{einf[k]}({100*cum/tot:.0f}%)")
        if k > 12: break
    print(f" |e|_inf histogram of base dirs: {' '.join(s)}")
    print(f" gcd g histogram: {sorted(gcs.items())[:10]}")
    print(f" |c-a|^2: min={bl.min()} q25={int(np.percentile(bl,25))} med={int(np.median(bl))}"
          f" q75={int(np.percentile(bl,75))} max={bl.max()}  (n^2={n*n})")
    print(f" |c-a|/n: med={np.sqrt(np.median(bl))/n:.3f} max={np.sqrt(bl.max())/n:.3f}")
    print(f" leg^2: min={ll.min()} med={int(np.median(ll))} max={ll.max()};"
          f" leg/n med={np.sqrt(np.median(ll))/n:.3f}")
    print(f" right-isosceles (legs perpendicular): {perp}/{len(tri)} = {100*perp/len(tri):.1f}%")
    ac = np.array(sorted(apex.values(), reverse=True))
    print(f" apexes: {len(apex)}/{m} points; top counts {ac[:6].tolist()};"
          f" top-10% carry {ac[:max(1,len(ac)//10)].sum()/ac.sum()*100:.1f}%;"
          f" mean {ac.mean():.2f}")
    pc = np.array(sorted(pair.values(), reverse=True))
    print(f" violating base pairs: {len(pair)} of {m*(m-1)//2} pairs"
          f" ({100*len(pair)/(m*(m-1)/2):.2f}%); max multiplicity {pc.max()}")
    print(f" distinct leg directions: {len(legs)}; top {legs.most_common(8)}")
    print(f" distinct leg r^2: {len(r2c)}; max mult {max(r2c.values())}")

if __name__ == '__main__':
    for n in [int(x) for x in sys.argv[1].split(',')]:
        S = np.load(f'q4best_{n}.npy')
        report(S, n, tag='greedyQ4')
        print()
