"""THE EXTREMAL-SET vs OPTIMUM GAP, measured exactly.

C(n+1) - C(n) is NOT "max points addable to an optimal n-set".  Define

    E(n) = max over ALL maximum iso-free S0 in [n]^2 of  ( |S0| + maxadd(S0) )
           where maxadd(S0) = max number of L-strip cells jointly addable to S0.

Then E(n) <= C(n+1) always, and E(n) < C(n+1) means no optimal (n+1)-set
restricts to an optimal n-set: the "extend an extremal interior" statement is
strictly weaker than the increment statement.  We compute both exactly.

Also computed: R(n) = max over ALL maximum iso-free S in [n+1]^2 of |S cap [n]^2|,
the largest interior an optimal (n+1)-set can have.  R(n) < C(n) is the same gap
seen from the other side.
"""
import sys, json, time, itertools
from iso import State, is_iso_free, strip_cells


def all_max_sets(W, H, target=None, cap=10**9):
    """Enumerate every maximum iso-free subset of [W]x[H] (as sorted tuples).
    If target is given it is used as the known optimum (still verified: the search
    proves nothing bigger exists)."""
    cells = [(x, y) for x in range(W) for y in range(H)]
    best = [0 if target is None else target]
    found = []
    st = State()

    def rec(cands):
        if len(st.pts) + len(cands) < best[0]:
            return
        if len(st.pts) + len(cands) == best[0] and cands:
            pass
        if not cands:
            if len(st.pts) > best[0]:
                best[0] = len(st.pts); found.clear()
            if len(st.pts) == best[0]:
                found.append(tuple(sorted(st.pts)))
            return
        for idx in range(len(cands)):
            if len(st.pts) + len(cands) - idx < best[0]:
                return
            p = cands[idx]
            if not st.can_add(p):
                continue
            st.add(p)
            if len(st.pts) > best[0]:
                best[0] = len(st.pts); found.clear()
            if len(st.pts) == best[0]:
                found.append(tuple(sorted(st.pts)))
            sub = [q for q in cands[idx + 1:] if st.can_add(q)]
            rec(sub)
            st.pop()

    rec(cells)
    return best[0], sorted(set(found))


def maxadd_exact(S0, n):
    """Exact max number of strip cells (row y=n and column x=n) jointly addable."""
    base = State()
    for p in S0:
        base.add(p)
    cand0 = [p for p in strip_cells(n) if base.can_add(p)]
    best = [0]
    bestset = [[]]
    st = base

    def rec(cands, taken):
        if len(taken) + len(cands) <= best[0]:
            return
        if not cands:
            if len(taken) > best[0]:
                best[0] = len(taken); bestset[0] = list(taken)
            return
        for idx in range(len(cands)):
            if len(taken) + len(cands) - idx <= best[0]:
                return
            p = cands[idx]
            if not st.can_add(p):
                continue
            st.add(p); taken.append(p)
            if len(taken) > best[0]:
                best[0] = len(taken); bestset[0] = list(taken)
            rec([q for q in cands[idx + 1:] if st.can_add(q)], taken)
            st.pop(); taken.pop()

    rec(cand0, [])
    return best[0], bestset[0], len(cand0)


if __name__ == "__main__":
    sealed = {1: 1, 2: 2, 3: 4, 4: 6, 5: 7, 6: 9, 7: 10, 8: 13, 9: 16, 10: 18, 11: 18}
    ns = [int(x) for x in sys.argv[1].split(",")]
    out = {}
    for n in ns:
        t0 = time.time()
        Cn, sets = all_max_sets(n, n, target=sealed.get(n))
        assert Cn == sealed.get(n, Cn), (n, Cn, sealed.get(n))
        for S in sets[:50]:
            assert is_iso_free(S) and len(S) == Cn
        bestE, arg = 0, None
        surv_stats = []
        for S in sets:
            m, ms, nsurv = maxadd_exact(list(S), n)
            surv_stats.append((nsurv, m))
            if Cn + m > bestE:
                bestE, arg = Cn + m, (S, ms)
        E = bestE
        Cn1 = sealed.get(n + 1)
        out[n] = dict(C=Cn, n_opt_sets=len(sets), E=E,
                      max_maxadd=max(s[1] for s in surv_stats),
                      max_nsurv=max(s[0] for s in surv_stats),
                      mean_nsurv=round(sum(s[0] for s in surv_stats) / len(sets), 2),
                      Cnext=Cn1, gap=(Cn1 - E) if Cn1 else None,
                      secs=round(time.time() - t0, 1))
        print(n, out[n], flush=True)
        json.dump(out, open("gap.json", "w"), indent=1)
