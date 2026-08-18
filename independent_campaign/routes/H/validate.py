import itertools, sys
from core import verify_isofree, verify_isofree_ref, IsoSet

# independent verifier #3: numpy-free, uses sorted distance lists
def verify3(pts):
    pts=[tuple(p) for p in pts]
    if len(set(pts))!=len(pts): return False
    for b in pts:
        ds=[(a[0]-b[0])**2+(a[1]-b[1])**2 for a in pts if a!=b]
        if len(ds)!=len(set(ds)): return False
    return True

# brute force C(n) for tiny n via exhaustive maximal-clique-ish DFS
def brute_C(n):
    P=[(x,y) for x in range(n) for y in range(n)]
    N=len(P)
    best=[0]; bestS=[None]
    def dfs(i, S):
        if len(S)+ (N-i) <= best[0]: return
        if i==N:
            if len(S)>best[0]: best[0]=len(S); bestS[0]=list(S)
            return
        # try include
        p=P[i]
        ok=True
        # check p as apex and as leg
        ds={}
        for q in S:
            d=(p[0]-q[0])**2+(p[1]-q[1])**2
            if d in ds: ok=False;break
            ds[d]=q
        if ok:
            for q in S:
                d=(p[0]-q[0])**2+(p[1]-q[1])**2
                for r in S:
                    if r is q: continue
                    if (r[0]-q[0])**2+(r[1]-q[1])**2==d: ok=False;break
                if not ok: break
        if ok:
            S.append(p); dfs(i+1,S); S.pop()
        dfs(i+1,S)
    dfs(0,[])
    return best[0], bestS[0]

known={1:1,2:2,3:4,4:6,5:7,6:9,7:10}
for n in range(1,8):
    c,S=brute_C(n)
    a=verify_isofree(S)[0]; b=verify_isofree_ref(S)[0]; c3=verify3(S)
    print(f"n={n} bruteC={c} known={known[n]} match={c==known[n]} verifiers={a},{b},{c3}")
    assert a and b and c3

# adversarial: verifiers must REJECT known-bad sets
bad=[(0,0),(1,0),(2,0)]  # AP
print("reject AP:", verify_isofree(bad)[0], verify_isofree_ref(bad)[0], verify3(bad))
bad2=[(0,0),(3,0),(0,3)] # corner
print("reject corner:", verify_isofree(bad2)[0], verify_isofree_ref(bad2)[0], verify3(bad2))
bad3=[(0,0),(1,2),(2,1)] # apex (0,0) dist 5,5
print("reject 5,5:", verify_isofree(bad3)[0], verify_isofree_ref(bad3)[0], verify3(bad3))
# random consistency
import random
random.seed(1)
for t in range(3000):
    n=random.randint(2,6); k=random.randint(2,6)
    P=random.sample([(x,y) for x in range(n) for y in range(n)], min(k,n*n))
    assert verify_isofree(P)[0]==verify_isofree_ref(P)[0]==verify3(P)
print("3000 random cross-checks OK")
