"""
Exact maximum-set search for:
  (A) isosceles-free sets in the integer grid [n]^2       -> C(n)
  (B) 3-AP-free sets in the integer grid [n]^2 (all directions)
  (C) isosceles-free sets in F_q^2 with Q(x,y)=x^2+y^2

Branch and bound over a 3-uniform hypergraph independent set.
"""
import sys, itertools, time

sys.setrecursionlimit(100000)


# ---------------------------------------------------------------- generic BnB
def maximum_set(V, addable_factory, verbose=False):
    """V vertices 0..V-1.  addable_factory returns (addable, push, pop) closures
    over a mutable state describing the current chosen set."""
    addable, push, pop = addable_factory()
    best = [0]
    best_set = [None]
    chosen = []

    def rec(cand):
        if len(chosen) + len(cand) <= best[0]:
            return
        if len(chosen) > best[0]:
            best[0] = len(chosen)
            best_set[0] = list(chosen)
            if verbose:
                print("   new best", best[0], best_set[0], flush=True)
        for idx in range(len(cand)):
            if len(chosen) + len(cand) - idx <= best[0]:
                return
            p = cand[idx]
            if not addable(p, chosen):
                continue
            push(p, chosen)
            chosen.append(p)
            rest = [x for x in cand[idx + 1:] if addable(x, chosen)]
            rec(rest)
            chosen.pop()
            pop(p, chosen)

    rec(list(range(V)))
    return best[0], best_set[0]


# ---------------------------------------------------------------- isosceles
def isosceles_factory(D, V, zero_forbidden=False):
    """D[i][j] = 'squared distance'.  Condition: for every chosen b the values
    D[b][x] over chosen x != b are pairwise distinct."""
    used = [set() for _ in range(V)]

    def addable(p, chosen):
        seen = set()
        for c in chosen:
            d = D[p][c]
            if zero_forbidden and d == 0:
                return False
            if d in seen:
                return False
            seen.add(d)
            if d in used[c]:
                return False
        return True

    def push(p, chosen):
        s = used[p]
        for c in chosen:
            d = D[p][c]
            used[c].add(d)
            s.add(d)

    def pop(p, chosen):
        for c in chosen:
            used[c].discard(D[p][c])
        used[p].clear()

    return addable, push, pop


def grid_points(n):
    return [(x, y) for x in range(n) for y in range(n)]


def C_exact(n, verbose=False):
    pts = grid_points(n)
    V = len(pts)
    D = [[0] * V for _ in range(V)]
    for i in range(V):
        for j in range(V):
            D[i][j] = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
    b, s = maximum_set(V, lambda: isosceles_factory(D, V), verbose)
    return b, [pts[i] for i in s]


# ---------------------------------------------------------------- 3-AP free
def ap_factory(pts, index):
    def addable(p, chosen):
        px, py = pts[p]
        for c in chosen:
            cx, cy = pts[c]
            m = (2 * px - cx, 2 * py - cy)          # p midpoint of c and m
            if m in index and index[m] in chosen:
                return False
            m2 = (2 * cx - px, 2 * cy - py)          # c midpoint of p and m2
            if m2 in index and index[m2] in chosen:
                return False
        return True

    return addable, (lambda p, ch: None), (lambda p, ch: None)


def AP_exact(n, verbose=False):
    pts = grid_points(n)
    index = {p: i for i, p in enumerate(pts)}
    b, s = maximum_set(len(pts), lambda: ap_factory(pts, index), verbose)
    return b, [pts[i] for i in s]


# ---------------------------------------------------------------- F_q^2 model
def fq_elements(q):
    """only prime q here (prime fields)."""
    return list(range(q))


def Fq_exact(q, zero_forbidden=False, verbose=False):
    pts = [(x, y) for x in range(q) for y in range(q)]
    V = len(pts)
    D = [[0] * V for _ in range(V)]
    for i in range(V):
        for j in range(V):
            dx = (pts[i][0] - pts[j][0]) % q
            dy = (pts[i][1] - pts[j][1]) % q
            D[i][j] = (dx * dx + dy * dy) % q
    b, s = maximum_set(V, lambda: isosceles_factory(D, V, zero_forbidden), verbose)
    return b, [pts[i] for i in s]


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "C":
        for n in range(1, int(sys.argv[2]) + 1):
            t = time.time()
            b, s = C_exact(n)
            print(f"C({n}) = {b}   [{time.time()-t:.1f}s]  {sorted(s)}", flush=True)
    elif what == "AP":
        for n in range(1, int(sys.argv[2]) + 1):
            t = time.time()
            b, s = AP_exact(n)
            print(f"A2({n}) = {b}   [{time.time()-t:.1f}s]", flush=True)
    elif what == "FQ":
        for q in [3, 5, 7, 11, 13]:
            if q > int(sys.argv[2]):
                break
            for zf in [False, True]:
                t = time.time()
                b, s = Fq_exact(q, zf)
                print(f"F_{q}^2  zero_forbidden={zf}: max = {b}  (q={q}, q+1={q+1})"
                      f"  [{time.time()-t:.1f}s]", flush=True)
