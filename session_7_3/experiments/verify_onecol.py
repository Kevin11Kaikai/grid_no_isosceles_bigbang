# -*- coding: utf-8 -*-
"""Independent verifier: naive triple loop over ALL ordered (apex, pair) combinations.
Shares no logic with the search."""
import sys, itertools
for path in sys.argv[1:]:
    f=[int(x) for x in open(path).read().split()]
    n=len(f)
    pts=[(i,f[i]) for i in range(n)]
    assert len(set(p[0] for p in pts))==n, "not one per column"
    assert all(0<=v<n for v in f), "out of range"
    bad=0; checked=0
    for a in range(n):
        for b in range(n):
            for c in range(b+1,n):
                if a==b or a==c: continue
                checked+=1
                pa,pb,pc=pts[a],pts[b],pts[c]
                d1=(pa[0]-pb[0])**2+(pa[1]-pb[1])**2
                d2=(pa[0]-pc[0])**2+(pa[1]-pc[1])**2
                if d1==d2: bad+=1
    print("%s  n=%d  points=%d  distinct columns=%d  triples checked=%d  VIOLATIONS=%d  %s"
          % (path,n,len(pts),len(set(p[0] for p in pts)),checked,bad,"OK" if bad==0 else "FAIL"))
