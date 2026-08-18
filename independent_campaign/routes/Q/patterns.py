"""Exact pattern-level forensics.

An isosceles triple is a,b,c with u=b-a, v=c-b, |u|^2=|v|^2, u!=0, v!=0, u+v!=0.
For a linear form psi the three values are 0, psi(u), psi(u)+psi(v) (relative to psi(a)).
A 3-AP-free set W containing psi(S) is violated by the triple iff one of
   (P1) U=V!=0                (b is the psi-midpoint of a,c)   <-> u+v parallel to e
   (P2) U+2V=0 and U!=0       (c is the psi-midpoint of a,b)
   (P3) 2U+V=0 and V!=0       (a is the psi-midpoint of b,c)
where U=psi(u), V=psi(v).

The pure line-kill relaxation for direction e kills exactly (P1).
The intersection construction with 3-AP-free W_e kills (P1)+(P2)+(P3).
"""
import numpy as np, sys, collections
from math import gcd

def norm_dir(e):
    a, b = int(e[0]), int(e[1])
    g = gcd(abs(a), abs(b))
    a, b = a // g, b // g
    if a < 0 or (a == 0 and b < 0): a, b = -a, -b
    return (a, b)

def killed_by(u, v, e, mode='construction'):
    U = u[0] * e[0] + u[1] * e[1]
    V = v[0] * e[0] + v[1] * e[1]
    if U == V and U != 0: return 'P1'
    if mode == 'construction':
        if U + 2 * V == 0 and U != 0: return 'P2'
        if 2 * U + V == 0 and V != 0: return 'P3'
    return None

def patterns(R):
    """All (u,v) with coords in [-R,R], |u|^2=|v|^2, u,v!=0, u+v!=0.
    Deduplicated up to nothing (raw), returned as list."""
    vecs = [(a, b) for a in range(-R, R + 1) for b in range(-R, R + 1) if (a, b) != (0, 0)]
    byn = collections.defaultdict(list)
    for w in vecs: byn[w[0] ** 2 + w[1] ** 2].append(w)
    out = []
    for r2, L in byn.items():
        for u in L:
            for v in L:
                if (u[0] + v[0], u[1] + v[1]) != (0, 0):
                    out.append((u, v))
    return out

def dirset(name):
    if name == 'Q4': return [(1, 0), (0, 1), (1, 1), (1, -1)]
    if name == 'axis': return [(1, 0), (0, 1)]
    # all primitive directions with |e|_inf <= B
    B = int(name)
    D = set()
    for a in range(-B, B + 1):
        for b in range(-B, B + 1):
            if (a, b) != (0, 0): D.add(norm_dir((a, b)))
    return sorted(D)

def analyse(R, E, mode='construction', verbose=True):
    pats = patterns(R)
    surv = []
    reason = collections.Counter()
    for (u, v) in pats:
        why = None
        for e in E:
            k = killed_by(u, v, e, mode)
            if k: why = k; break
        if why is None: surv.append((u, v))
        else: reason[why] += 1
    if verbose:
        print(f"R={R} |E|={len(E)} mode={mode}: patterns={len(pats)} "
              f"survivors={len(surv)} ({100.0*len(surv)/len(pats):.2f}%) killed_by={dict(reason)}")
    return pats, surv

if __name__ == '__main__':
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    for name in ['axis', 'Q4', '2', '3', '4']:
        E = dirset(name)
        for mode in ['linekill', 'construction']:
            analyse(R, E, mode)
    # structure of survivors for Q4
    pats, surv = analyse(R, dirset('Q4'), 'construction', verbose=False)
    cnt = collections.Counter(norm_dir((u[0] + v[0], u[1] + v[1])) for u, v in surv)
    print("\nsurvivor base directions dir(c-a) (Q4, construction), top 20:")
    for d, c in cnt.most_common(20): print("   ", d, c)
    print("num distinct base directions among survivors:", len(cnt))
    r2c = collections.Counter(u[0] ** 2 + u[1] ** 2 for u, v in surv)
    print("survivor leg |u|^2 (smallest 15):", sorted(r2c.items())[:15])
    print("\nsmallest survivors (by |u|^2 then |u+v|^2):")
    ss = sorted(surv, key=lambda p: (p[0][0] ** 2 + p[0][1] ** 2,
                                     (p[0][0] + p[1][0]) ** 2 + (p[0][1] + p[1][1]) ** 2))
    for u, v in ss[:15]:
        print(f"   u={u} v={v} |u|^2={u[0]**2+u[1]**2} c-a={(u[0]+v[0], u[1]+v[1])}")
