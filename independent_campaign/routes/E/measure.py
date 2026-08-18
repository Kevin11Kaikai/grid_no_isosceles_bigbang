"""Strip-survivor measurements + Master Lemma checks on near-extremal sets."""
import sys, json, random, time
from collections import defaultdict
from iso import (State, is_iso_free, local_search, strip_cells, survivors,
                 max_addable)


def midpoints(T):
    """Integer midpoints of distinct pairs of T (a set/list of ints)."""
    T = sorted(set(T))
    M = set()
    for i in range(len(T)):
        for j in range(i + 1, len(T)):
            if (T[i] + T[j]) % 2 == 0:
                M.add((T[i] + T[j]) // 2)
    return M


def lemma_check(S, n):
    """Verify M(T_j) cap X = empty for all rows, and the derived size bound."""
    rows = defaultdict(list)
    cols = defaultdict(list)
    for (x, y) in S:
        rows[y].append(x)
        cols[x].append(y)
    X = set(x for (x, y) in S)
    Y = set(y for (x, y) in S)
    viol = 0
    maxrow = 0
    for j, T in rows.items():
        M = midpoints(T)
        if M & X:
            viol += 1
        maxrow = max(maxrow, len(T))
    maxcol = 0
    for i, U in cols.items():
        M = midpoints(U)
        if M & Y:
            viol += 1
        maxcol = max(maxcol, len(U))
    return dict(k=len(X), l=len(Y), maxrow=maxrow, maxcol=maxcol,
                viol=viol,
                bound_row=n - len(X) + 3, bound_col=n - len(Y) + 3,
                prod_bound=len(X) * len(Y),
                quarter_bound=(n + 3) ** 2 // 4, m=len(S))


def run(nlist, iters, restarts, seedbase=0):
    res = {}
    for n in nlist:
        t = time.time()
        S = local_search(n, n, iters=iters, restarts=restarts, seed=seedbase + n)
        assert is_iso_free(S)
        lc = lemma_check(S, n)
        surv = survivors(S, n)
        ma, maset, nsurv = max_addable(S, n, tries=300, seed=n)
        # also: survivors against a *random maximal* (not near-extremal) set, for contrast
        d = dict(lc); d.update(strip=2 * n + 1, nsurv=nsurv,
                 max_addable=ma, secs=round(time.time() - t, 1))
        res[n] = d
        print(n, res[n], flush=True)
    return res


if __name__ == "__main__":
    nlist = [int(x) for x in sys.argv[1].split(",")]
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    r = run(nlist, iters, restarts)
    json.dump({str(k): v for k, v in r.items()}, open(sys.argv[4] if len(sys.argv) > 4 else "measure.json", "w"), indent=1)
