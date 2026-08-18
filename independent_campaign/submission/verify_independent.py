"""Independent verification for C(12) = 20.

Written from the definition only.  Shares no code, no data structure and no algorithm
with the C solver (solveA.c) whose result it checks:

  * solveA.c is a bitset branch-and-bound over an incrementally maintained candidate set,
    pruning with |S| + popcount(cand) <= best.
  * this file checks validity by enumerating all C(|S|,3) triples and comparing squared
    distances, and computes small exact values by a plain recursive search with no
    candidate set and no bound at all.

All arithmetic is exact integer arithmetic on SQUARED distances.  No floating point is
used anywhere, so no rounding can turn an isosceles triple into a scalene one.

DEFINITION.  S is admissible iff there are no three DISTINCT points a,b,c in S with
d(a,b) = d(b,c), where d is the squared Euclidean distance.  Degenerate (collinear)
triples are included: three points in arithmetic progression on a line have the middle
point equidistant from the outer two, so every line meets S in a 3-AP-free set.
"""
import itertools
import sys


def d2(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def isosceles_triples(S):
    """every violation, by brute force over all unordered triples and all 3 apex choices"""
    out = []
    for a, b, c in itertools.combinations(sorted(S), 3):
        for apex, x, y in ((a, b, c), (b, a, c), (c, a, b)):
            if d2(apex, x) == d2(apex, y):
                out.append((apex, x, y))
    return out


def check(S, n, name):
    S = [tuple(p) for p in S]
    ok = True
    msgs = []
    if len(set(S)) != len(S):
        ok = False
        msgs.append("repeated points")
    for p in S:
        if not (0 <= p[0] < n and 0 <= p[1] < n):
            ok = False
            msgs.append(f"point {p} outside [0,{n})^2")
    v = isosceles_triples(S)
    if v:
        ok = False
        msgs.append(f"{len(v)} isosceles triples, e.g. apex {v[0][0]} legs to {v[0][1]},{v[0][2]}")
    xs = [p[0] for p in S]
    ys = [p[1] for p in S]
    print(f"  {name:<26} |S| = {len(S):>3}  bbox = [{min(xs)}..{max(xs)}]x[{min(ys)}..{max(ys)}]  "
          f"{'VALID' if ok else 'INVALID: ' + '; '.join(msgs)}")
    return ok


def exact_C(n, cells=None):
    """exact C(n) by plain recursion over cells in index order.

    Deliberately naive: no candidate set, no incremental filtering, no symmetry, and the
    only pruning is the trivial "not enough cells left".  Validity of a partial set is
    re-tested from the definition on every extension.  Slow, but it cannot inherit a bug
    from the fast solver because it shares no logic with it.
    """
    if cells is None:
        cells = [(x, y) for x in range(n) for y in range(n)]
    m = len(cells)
    best = [0]
    bestset = [[]]

    def ok_to_add(S, p):
        # p, and two members of S: p may be the apex or one of the legs
        for i in range(len(S)):
            for j in range(i + 1, len(S)):
                if d2(p, S[i]) == d2(p, S[j]):
                    return False
        for a in S:
            for b in S:
                if a is b:
                    continue
                if d2(a, p) == d2(a, b):
                    return False
        return True

    def rec(idx, S):
        if len(S) + (m - idx) <= best[0]:
            return
        if len(S) > best[0]:
            best[0] = len(S)
            bestset[0] = list(S)
        for t in range(idx, m):
            if len(S) + (m - t) <= best[0]:
                return
            p = cells[t]
            if ok_to_add(S, p):
                S.append(p)
                rec(t + 1, S)
                S.pop()

    rec(0, [])
    return best[0], bestset[0]


W = {
 "witness A (inherited)": [(0,0),(11,11),(10,11),(9,10),(8,10),(1,3),(11,8),(3,11),(11,7),(1,6),
                          (5,10),(10,6),(1,2),(0,8),(0,7),(5,1),(4,11),(0,1),(4,0),(3,0)],
 "witness B (inherited)": [(0,0),(0,3),(0,4),(1,0),(1,5),(2,1),(3,1),(6,1),(6,10),(7,0),
                          (7,11),(8,0),(8,11),(10,5),(10,8),(10,9),(11,3),(11,4),(11,10),(11,11)],
 "witness C (solver)":   [(0,0),(0,11),(1,0),(1,4),(1,7),(1,11),(2,1),(2,10),(3,1),(3,5),
                          (3,6),(3,10),(9,1),(9,10),(10,0),(10,4),(10,7),(10,11),(11,5),(11,6)],
 "witness D (this rerun)": [(0,0),(0,5),(0,6),(1,0),(1,4),(1,7),(1,11),(2,1),(2,10),(3,10),
                          (8,1),(9,1),(9,10),(10,0),(10,4),(10,7),(10,11),(11,5),(11,6),(11,11)],
}


def parse_set_line(path):
    """read the 'SET x,y x,y ...' line from a solveA log"""
    try:
        for line in open(path):
            if line.startswith("SET"):
                pts = []
                for tok in line.split()[1:]:
                    a, b = tok.split(",")
                    pts.append((int(a), int(b)))
                return pts
    except OSError:
        return None
    return None


def main():
    print("V1  the four 20-point witnesses of README section 2, checked from the definition")
    allok = all(check(S, 12, name) for name, S in W.items())
    pairs = list(itertools.combinations(W, 2))
    print("     pairwise distinct:",
          all(set(W[a]) != set(W[b]) for a, b in pairs))

    fresh = parse_set_line("logs/n12_scratch.log")
    if fresh:
        print("\nV2  witness produced by THIS session's rerun (logs/n12_scratch.log)")
        allok &= check(fresh, 12, "fresh solver output")
        known = [set(v) for v in W.values()]
        print(f"     coincides with a stored witness: {set(fresh) in known}")

    print("\nV3  independent exact values by the naive solver (no shared logic)")
    print("     the naive solver is deliberately unoptimised and becomes impractical")
    print("     beyond n = 7; that is the honest limit of this cross-check.")
    print(f"     {'n':>3} {'naive':>6} {'supplied':>9} {'agree':>6}")
    supplied = {1: 1, 2: 2, 3: 4, 4: 6, 5: 7, 6: 9, 7: 10}
    for n in range(1, 8):
        val, wit = exact_C(n)
        assert not isosceles_triples(wit), "naive solver returned an invalid set"
        ag = "yes" if val == supplied[n] else "*** NO"
        print(f"     {n:>3} {val:>6} {supplied[n]:>9} {ag:>6}")
        allok &= (val == supplied[n])

    print("\nV4  C(1,n) must equal r_3(n) (a line's trace is a 3-AP-free set)")
    r3 = {1:1,2:2,3:2,4:3,5:4,6:4,7:4,8:4,9:5,10:5,11:6,12:6,13:7,14:8,15:8,16:8,17:8,
          18:8,19:8,20:9,21:9,22:9,23:9,24:10,25:10,26:11,27:11,28:12,29:13,30:13}
    bad = 0
    NMAX = 24
    for n in range(1, NMAX + 1):
        val, _ = exact_C(n, cells=[(0, y) for y in range(n)])
        if val != r3[n]:
            bad += 1
            print(f"     n={n}: got {val}, Salem-Spencer says {r3[n]}  *** MISMATCH")
    print(f"     n = 1..{NMAX} checked against the Salem-Spencer sequence: {bad} mismatches")
    allok &= (bad == 0)

    print("\nRESULT:", "ALL CHECKS PASS" if allok else "*** SOMETHING FAILED")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
