# -*- coding: utf-8 -*-
"""Can an isosceles-free set take exactly one point per column?
That would give C(n) >= n outright (the open linear lower bound).
Condition on f:[n]->[n]:  for every i, the values (i-j)^2+(f(i)-f(j))^2 are
distinct over j != i.  Backtracking with random value order + restarts."""
import random, sys

def search(n, tries=400, seed=0):
    rnd=random.Random(seed)
    for t in range(tries):
        f=[-1]*n
        order=list(range(n))
        ok=True
        for i in order:
            vals=list(range(n)); rnd.shuffle(vals)
            placed=False
            for v in vals:
                f[i]=v
                good=True
                # check every apex among placed columns
                P=[(j,f[j]) for j in range(n) if f[j]>=0]
                for (a,fa) in P:
                    seen=set()
                    for (b,fb) in P:
                        if a==b: continue
                        d=(a-b)**2+(fa-fb)**2
                        if d in seen: good=False; break
                        seen.add(d)
                    if not good: break
                if good: placed=True; break
                f[i]=-1
            if not placed: ok=False; break
        if ok: return f
    return None

for n in [8,12,16,20,24,28,32,40,48,64]:
    r=search(n, tries=60, seed=n)
    print("n=%3d  one-per-column isosceles-free set: %s" % (n, "FOUND" if r else "not found"))
    sys.stdout.flush()
