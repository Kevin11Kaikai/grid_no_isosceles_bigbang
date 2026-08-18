import time,sys
import ls, core
for n in [8,11,16,27,32]:
    t0=time.time()
    S=ls.best_in_box(n,time_budget=12.0,seed=0,restarts=2)
    S=list(S) if not isinstance(S,tuple) else list(S[0])
    ok1=core.verify_isofree(S)[0]; ok2=core.verify_isofree_ref(S)[0]
    print(f"n={n} ls={len(S)} verified={ok1},{ok2} t={time.time()-t0:.1f}",flush=True)
