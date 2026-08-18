import numpy as np
from anneal2 import Ann
rng=np.random.default_rng(0)
bad=0
for t in range(300):
    n=int(rng.integers(4,10)); K=int(rng.integers(3,min(9,n*n)))
    a=Ann(n,n,K,rng)
    assert a.E==a.energy_check(),("init",a.E,a.energy_check())
    for _ in range(20):
        s=int(rng.integers(K)); q=int(rng.integers(a.N))
        if a.inS[q]: continue
        dE,dv=a.delta_swap(s,q)
        E0=a.E; a.apply(s,q,dv,dE)
        if a.E!=a.energy_check(): bad+=1; print("MISMATCH",a.E,a.energy_check()); break
print("delta test done, mismatches =",bad)
