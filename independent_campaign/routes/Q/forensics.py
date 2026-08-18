"""Verify the adversary and run forensics on its isosceles triples."""
import numpy as np, sys, json, collections
from math import gcd
from qlib import (is_3ap_free, q4_violations, iso_triples, is_iso_free,
                  prim_dir, bisector_has_lattice, build_S)
from build_adv import ind_from

def load(n):
    S = np.load(f'S_{n}.npy'); T = np.load(f'T_{n}.npy'); Tp = np.load(f'Tp_{n}.npy')
    meta = json.load(open(f'adv_{n}.json'))
    return S, T, Tp, meta

def main(n):
    S, T, Tp, meta = load(n)
    a, b, w, z = meta['shifts']
    A = np.array([v for v in T + a if 0 <= v < n])
    B = np.array([v for v in T + b if 0 <= v < n])
    W = np.array([v for v in Tp + w])
    Z = np.array([v for v in Tp + z])
    print(f"=== n={n}  |S|={len(S)}  shifts={meta['shifts']}")
    print(f"|A|={len(A)} |B|={len(B)} |W|={len(W)} |Z|={len(Z)}")
    # 1. 3-AP-freeness of the four sets
    for nm, arr in [('A', A), ('B', B), ('W', W), ('Z', Z)]:
        ok, wit = is_3ap_free(arr)
        print(f"  3-AP-free({nm}) = {ok}" + ("" if ok else f"  witness {wit}"))
    # 1b. cross-check S against a from-scratch rebuild
    S2 = build_S(n, A, B, W, Z)
    same = (len(S2) == len(S)) and set(map(tuple, S2.tolist())) == set(map(tuple, S.tolist()))
    print(f"  independent rebuild of S matches: {same}  (|S2|={len(S2)})")
    # 2. Q4 constraints
    v = q4_violations(S)
    print(f"  Q4 violations: rows={len(v[1])} cols={len(v[2])} diag={len(v[3])} anti={len(v[4])}")
    # 3. isosceles
    free = is_iso_free(S)
    tri = iso_triples(S)
    print(f"  isosceles-free: {free};  #isosceles triples = {len(tri)}")
    return S, tri

def forensics(S, tri, n, topk=12):
    m = len(S)
    P = S.astype(np.int64)
    dirs = collections.Counter()          # primitive direction of base pair c-a
    legdirs = collections.Counter()       # primitive directions of legs
    apex = collections.Counter()
    r2c = collections.Counter()
    gcounter = collections.Counter()
    norm_e = collections.Counter()
    baselen2 = []
    leglen2 = []
    for (ib, ia, ic, r2) in tri:
        A_, B_, C_ = P[ia], P[ib], P[ic]
        d = C_ - A_
        e, g = prim_dir(d)
        dirs[e] += 1
        gcounter[g] += 1
        norm_e[e[0] ** 2 + e[1] ** 2] += 1
        apex[ib] += 1
        r2c[r2] += 1
        baselen2.append(int(d[0] ** 2 + d[1] ** 2))
        leglen2.append(int(r2))
        for v in (B_ - A_, C_ - B_):
            legdirs[prim_dir(v)[0]] += 1
        assert bisector_has_lattice(A_, C_), "L1 criterion must hold"
    print(f"\n--- FORENSICS (n={n}, |S|={m}, {len(tri)} triples) ---")
    print(f"distinct base directions e: {len(dirs)}")
    print(f"top base directions: {dirs.most_common(topk)}")
    FIX = {(1, 0), (0, 1), (1, 1), (1, -1)}
    inside = sum(c for e, c in dirs.items() if e in FIX)
    print(f"triples whose base direction is one of the four fixed dirs: {inside} "
          f"({100.0*inside/max(1,len(tri)):.1f}%)")
    print(f"|e|^2 distribution (base dir): {sorted(norm_e.items())[:15]}")
    print(f"gcd g = |c-a|/|e| distribution: {sorted(gcounter.items())[:15]}")
    print(f"distinct leg directions: {len(legdirs)}; top: {legdirs.most_common(topk)}")
    bl = np.array(baselen2); ll = np.array(leglen2)
    print(f"base squared length: min={bl.min()} med={int(np.median(bl))} max={bl.max()};"
          f" as fraction of n^2: med={np.median(bl)/n**2:.4f} max={bl.max()/n**2:.4f}")
    print(f"leg squared length: min={ll.min()} med={int(np.median(ll))} max={ll.max()};"
          f" med/n^2={np.median(ll)/n**2:.4f}")
    ac = np.array(sorted(apex.values(), reverse=True))
    print(f"apex concentration: {len(apex)}/{m} points are apexes; "
          f"top counts {ac[:8].tolist()}; total {ac.sum()}; "
          f"top-10% of apexes carry {ac[:max(1,len(ac)//10)].sum()/ac.sum()*100:.1f}%")
    print(f"distinct squared leg-distances used: {len(r2c)}; "
          f"max multiplicity {max(r2c.values())}")
    return dirs, legdirs, apex, r2c

if __name__ == '__main__':
    n = int(sys.argv[1])
    S, tri = main(n)
    forensics(S, tri, n)
