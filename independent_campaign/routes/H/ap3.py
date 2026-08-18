"""3-AP-free subsets of [N] (exact for small N, good heuristics for large)."""
import sys, random
sys.setrecursionlimit(100000)

def is_3apfree(W):
    S=set(W); L=sorted(W)
    for i,a in enumerate(L):
        for b in L[i+1:]:
            if 2*b-a in S and 2*b-a!=b: return False
    return True

def max_3apfree_weighted(N, wt=None, time_budget_nodes=4*10**7):
    """Exact max-weight 3AP-free subset of {0..N-1} by DFS+bound. wt=None -> unit."""
    if wt is None: wt=[1]*N
    suff=[0]*(N+1)
    for i in range(N-1,-1,-1): suff[i]=suff[i+1]+max(wt[i],0)
    best=[-1]; bestS=[None]; nodes=[0]
    chosen=[]
    inS=[False]*N
    def dfs(i,val):
        nodes[0]+=1
        if nodes[0]>time_budget_nodes: raise TimeoutError
        if val+suff[i]<=best[0]: return
        if i==N:
            if val>best[0]: best[0]=val; bestS[0]=list(chosen)
            return
        # include i : need no 3AP.  i as right end: a,b,i with b-a=i-b -> a=2b-i
        ok=True
        for b in chosen:
            if 2*b-i>=0 and 2*b-i!=b and inS[2*b-i]: ok=False;break
        if ok:
            for a in chosen:  # i as middle: a, i, 2i-a  -> 2i-a already placed? no, >i. skip
                pass
        if ok:
            chosen.append(i); inS[i]=True
            dfs(i+1,val+wt[i])
            chosen.pop(); inS[i]=False
        dfs(i+1,val)
    try: dfs(0,0)
    except TimeoutError: pass
    return best[0], bestS[0], nodes[0]<=time_budget_nodes

def behrend(N, d=None, best_of=None):
    """Behrend set in [0,N): digit vectors base d, dim k, fixed norm."""
    bestW=[]
    ds = [d] if d else range(3, 40)
    for dd in ds:
        k=1
        while dd**k < N: k+=1
        if dd**k>N*dd: pass
        # vectors with digits < dd/2 in k digits, base dd
        half=(dd+1)//2
        from collections import defaultdict
        buck=defaultdict(list)
        # enumerate all digit vectors with digits in [0,half)
        tot=half**k
        if tot>3*10**6: continue
        for m in range(tot):
            v=[];t=m;s=0
            for _ in range(k):
                q=t%half; t//=half; v.append(q); s+=q*q
            val=0
            for q in reversed(v): val=val*dd+q
            if val<N: buck[s].append(val)
        if buck:
            b=max(buck.values(), key=len)
            if len(b)>len(bestW): bestW=b
    return sorted(bestW)

def greedy_noB2(N):
    """no digit '2' in base 3 (Szekeres) -- 3AP-free."""
    out=[]
    for x in range(N):
        t=x; ok=True
        while t: 
            if t%3==2: ok=False;break
            t//=3
        if ok: out.append(x)
    return out

def greedy_seq(N):
    """greedy: add x if creates no 3AP."""
    S=[];Sset=set()
    for x in range(N):
        ok=True
        for b in S:
            a=2*b-x
            if a in Sset and a!=b: ok=False;break
        if ok: S.append(x);Sset.add(x)
    return S

def best_3apfree(N):
    """best known-good 3AP-free subset of [0,N) from our heuristics."""
    cands=[greedy_noB2(N), greedy_seq(N), behrend(N)]
    # random-restart greedy
    rnd=random.Random(12345)
    order=list(range(N))
    for _ in range(60):
        rnd.shuffle(order); S=[];Ss=set()
        for x in order:
            ok=True
            for b in S:
                a=2*b-x
                if a in Ss and a!=b: ok=False;break
                c=2*x-b
                if c in Ss and c!=x: ok=False;break
            if ok: S.append(x);Ss.add(x)
        cands.append(sorted(S))
    cands=[c for c in cands if c and is_3apfree(c)]
    return max(cands,key=len)

if __name__=="__main__":
    print("exact r_3(N):")
    row=[]
    for N in range(1,41):
        v,S,exact=max_3apfree_weighted(N)
        row.append(v)
        assert is_3apfree(S)
    print(row)
    print("heuristic sizes:", [(N,len(best_3apfree(N))) for N in [16,27,32,64,128,256,512,1024]])
