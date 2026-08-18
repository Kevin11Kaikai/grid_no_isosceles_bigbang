"""Exact maxima for small n: isosceles-free C(n), square-corner-free Q_SQ(n),
corner-free, and Q4-feasible."""
import sys, time
from itertools import combinations

def cells(n):
    return [(x, y) for x in range(n) for y in range(n)]

def bad_triples_sq(n):
    """all {b, b+w, b+wperp} inside [n]^2, as frozensets of indices"""
    C = cells(n); idx = {p: i for i, p in enumerate(C)}
    out = set()
    for (bx, by) in C:
        for w1 in range(-n, n + 1):
            for w2 in range(-n, n + 1):
                if (w1, w2) == (0, 0): continue
                a = (bx + w1, by + w2); c = (bx - w2, by + w1)
                if a in idx and c in idx:
                    out.add(frozenset((idx[(bx, by)], idx[a], idx[c])))
    return [tuple(sorted(t)) for t in out]

def bad_triples_iso(n):
    C = cells(n); idx = {p: i for i, p in enumerate(C)}
    out = set()
    for bi, b in enumerate(C):
        for i in range(len(C)):
            for j in range(i + 1, len(C)):
                if i == bi or j == bi: continue
                a, c = C[i], C[j]
                if (a[0]-b[0])**2 + (a[1]-b[1])**2 == (c[0]-b[0])**2 + (c[1]-b[1])**2:
                    out.add(frozenset((bi, i, j)))
    return [tuple(sorted(t)) for t in out]

def maxset(N, triples, tlimit=60):
    """max subset of [N] hitting no triple; DFS with simple bound."""
    inc = [[] for _ in range(N)]
    for t in triples:
        for v in t: inc[v].append(t)
    best = [0]; chosen = [False] * N
    t0 = time.time(); timeout = [False]
    def viol(v):
        for t in inc[v]:
            if all(chosen[u] for u in t if u != v): return True
        return False
    def dfs(i, cnt):
        if timeout[0]: return
        if time.time() - t0 > tlimit: timeout[0] = True; return
        if cnt + (N - i) <= best[0]: return
        if i == N:
            best[0] = max(best[0], cnt); return
        if not viol(i):
            chosen[i] = True; dfs(i + 1, cnt + 1); chosen[i] = False
        dfs(i + 1, cnt)
    dfs(0, 0)
    return best[0], timeout[0]

if __name__ == '__main__':
    for n in [int(v) for v in sys.argv[1].split(',')]:
        N = n * n
        r = {}
        for nm, f in [('iso', bad_triples_iso), ('sq', bad_triples_sq)]:
            T = f(n)
            v, to = maxset(N, T, tlimit=float(sys.argv[2]) if len(sys.argv) > 2 else 60)
            r[nm] = (v, to, len(T))
        print(f"n={n}  C(n)={r['iso'][0]}{'*' if r['iso'][1] else ''} (#triples {r['iso'][2]})"
              f"   Q_SQ(n)={r['sq'][0]}{'*' if r['sq'][1] else ''} (#triples {r['sq'][2]})",
              flush=True)
