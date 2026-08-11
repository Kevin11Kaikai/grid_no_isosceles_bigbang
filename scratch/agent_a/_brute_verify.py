import sys, itertools, time
sys.path.insert(0, ".")
from data.baselines.official_raw import SOL_64, SOL_100
from src.search.hamming_shell_conflict import load_policy_universe, reconstruct_S
from src.verification.conflict_metric import conflict_count
from src.verification.oracle_verifier import is_legal_pivot_method

def brute(n, s0, rem, add, r, limit=None):
    t0=time.time(); checked=0; best_v=10**9; legal=[]
    for rem_drop in itertools.combinations(range(len(rem)), r):
        keep = [True]*len(rem)
        for i in rem_drop: keep[i]=False
        for add_take in itertools.combinations(range(len(add)), r+1):
            take = [False]*len(add)
            for j in add_take: take[j]=True
            S = reconstruct_S(s0, rem, add, keep, take)
            v = conflict_count(S, n)
            checked += 1
            if v < best_v: best_v = v
            if v == 0:
                ok,_ = is_legal_pivot_method(S, n)
                legal.append((S, ok))
                if ok:
                    return {"checked":checked, "legal":True, "best_v":0, "wall":time.time()-t0}
            if limit and checked >= limit:
                return {"checked":checked, "legal":False, "best_v":best_v, "wall":time.time()-t0, "truncated":True}
    return {"checked":checked, "legal":bool(legal), "n_legal":len(legal), "best_v":best_v, "wall":time.time()-t0}

rem, add, h = load_policy_universe(64, "U_small")
print("n64 brute", brute(64, SOL_64, rem, add, r=1))

rem, add, h = load_policy_universe(100, "U_small")
print("n100 r1 U_small brute", brute(100, SOL_100, rem, add, r=1))

# U_small_r2 full enum ~6.5M — may take a few minutes; run with progress
rem, add, h = load_policy_universe(100, "U_small_r2")
print("starting U_small_r2 brute C(32,2)*C(44,3)=", 496*13244)
t0=time.time(); checked=0; best_v=10**9; found=False
s0=SOL_100
for rem_drop in itertools.combinations(range(len(rem)), 2):
    keep = [True]*len(rem)
    for i in rem_drop: keep[i]=False
    for add_take in itertools.combinations(range(len(add)), 3):
        take = [False]*len(add)
        for j in add_take: take[j]=True
        S = reconstruct_S(s0, rem, add, keep, take)
        v = conflict_count(S, 100)
        checked += 1
        if v < best_v: best_v = v
        if v == 0:
            ok,_=is_legal_pivot_method(S,100)
            print("FOUND V=0", ok, "checked", checked)
            found=True
            break
        if checked % 500000 == 0:
            print("progress", checked, "best_v", best_v, "t", round(time.time()-t0,1))
    if found: break
print("U_small_r2 brute done", {"checked":checked, "found":found, "best_v":best_v, "wall":time.time()-t0})
