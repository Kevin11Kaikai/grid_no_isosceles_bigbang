import ls, fastcore, time, sys
for n in [16,27,32]:
    t=time.time(); b=ls.best_in_box(n, time_budget=100, seed=n)
    print('n=%2d best=%3d verified=%s %.1fs'%(n,len(b),fastcore.verify_np(b)[0],time.time()-t), flush=True)
