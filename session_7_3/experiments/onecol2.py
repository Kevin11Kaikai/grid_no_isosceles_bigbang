# -*- coding: utf-8 -*-
"""Proper backtracking: one point per column, isosceles-free.
Incremental, bitmask distance sets, random value order, node cap + restarts."""
import random, sys, time

def solve(n, cap=3_000_000, seed=0, restarts=6):
    rnd = random.Random(seed)
    for rs in range(restarts):
        used = [0]*n          # used[i] = bitmask of squared distances from column i's point
        f = [-1]*n
        nodes = [0]
        orders = [rnd.sample(range(n), n) for _ in range(n)]
        def dfs(i):
            if i == n: return True
            for v in orders[i]:
                nodes[0] += 1
                if nodes[0] > cap: return False
                ds = []
                mine = 0
                ok = True
                for j in range(i):
                    d = (i-j)**2 + (v-f[j])**2
                    if (used[j] >> d) & 1: ok = False; break
                    if (mine >> d) & 1: ok = False; break
                    mine |= (1 << d)
                    ds.append((j, d))
                if not ok: continue
                f[i] = v
                old = used[i]
                used[i] = mine
                for (j, d) in ds: used[j] |= (1 << d)
                if dfs(i+1): return True
                for (j, d) in ds: used[j] &= ~(1 << d)
                used[i] = old
                f[i] = -1
            return False
        sys.setrecursionlimit(10000)
        t0 = time.time()
        if dfs(0): return f, nodes[0], time.time()-t0
    return None, nodes[0], 0.0

import os
NS=[int(x) for x in os.environ.get("NS","40").split(",")]
for n in NS:
    f, nd, t = solve(n, seed=n)
    print("n=%4d  %-9s nodes=%-10d %.1fs" % (n, "FOUND" if f else "no", nd, t))
    sys.stdout.flush()
