"""The (1+i)-adic tower: G(I) for ideals I of Z[i], and the doubling ratio.

WHY THIS IS THE TARGET.  Two facts combine.

(A) BOX <= TORUS.  For q > 4n, a set S in [0,n)^2 is square-corner-free in the box iff
    it is square-corner-free on the torus (Z_q)^2.  Reason: for b,u in S the difference
    w = u-b has both coordinates in (-n,n), so its reduction mod q is the honest
    difference; the honest third point b+i*w has coordinates in (-n,2n), and any
    coordinate that is negative reduces to something > q-n > 3n >= n, i.e. outside the
    box, while any coordinate in [n,2n) is already outside.  So a wraparound corner can
    never land inside the box, and the two notions coincide.  Hence

        Q_SQ(n) <= g(q)  for every q > 4n,   in particular for q a power of 2.

    Verified below as A1 (and the minimal usable q is measured, not assumed).

(B) THE TOWER HAS INDEX-2 STEPS.  (1+i) is prime in Z[i] with N((1+i)) = 2, and
    (1+i)^{2m} = (2^m).  So the chain of quotients Z[i]/(1+i)^j has index 2 at every
    step, and N((1+i)^j) = 2^j.  If

        G(I*(1+i)) <= c * G(I)   with c < 2

    for all I in the tower, then G((1+i)^j) = O(c^j) = O(N^{log_2 c}), so by (A)
    Q_SQ(n) = O(n^{2 log_2 c}) with 2 log_2 c < 2, i.e.

        C(n) = O(n^{2-eps}).

    THE WHOLE TARGET reduces to a doubling inequality with a factor-2 budget.
    Known values give ratios ~1.41-1.5 per step.  This script computes the ladder.

    Barrier B5 demanded "constant gain per constant scale ratio"; the (1+i) tower
    supplies exactly that, which is why this is not route D as previously framed.

NOTHING HERE IS A PROOF OF THE RECURRENCE.  The recurrence is the open problem; this
script measures its margin and hunts for the structure a proof would need.

F3 RULE: the exact solver's pair-completion table lists ALL SIX ordered assignments,
and (1-i) is a zero divisor on this tower so the "pair alone is forbidden" case is
handled explicitly -- both are the exact bugs that bit this campaign three times.
Every witness is re-checked by a definition-only verifier sharing no tables.
"""
import math
import sys
from itertools import combinations


# --------------------------------------------------------- ideals of Z[i] as lattices

def hnf_reducer(v1, v2):
    """canonical-representative map for Z^2 / L, L = <v1, v2>.

    Row-reduce to a basis w1 = (g, s), w2 = (0, t) with g = gcd of first coords.
    Returns (reduce, g, t) with g*t = |det|.
    """
    a1, b1 = v1
    a2, b2 = v2
    # extended gcd on first coordinates
    while a2 != 0:
        qq = a1 // a2
        a1, b1, a2, b2 = a2, b2, a1 - qq * a2, b1 - qq * b2
    if a1 < 0:
        a1, b1 = -a1, -b1
    g, s = a1, b1                      # w1 = (g, s)
    t = abs(b2)                        # w2 = (0, t)
    assert g > 0 and t > 0, (v1, v2, g, t)

    def red(z):
        x, y = z
        m = x // g
        x -= m * g
        y -= m * s
        return (x, y % t)
    return red, g, t


def build_quotient(alpha):
    """Z[i]/(alpha) as an explicit list of coset reps, with the action of i.

    The ideal (alpha) is the lattice spanned by alpha and i*alpha, which is closed
    under multiplication by i -- so i acts on the quotient.
    """
    a, b = alpha
    red, g, t = hnf_reducer((a, b), (-b, a))
    N = g * t
    reps = [red((x, y)) for x in range(g) for y in range(t)]
    reps = sorted(set(reps))
    assert len(reps) == N, (alpha, N, len(reps))
    idx = {r: j for j, r in enumerate(reps)}

    def add(p, q):
        return idx[red((reps[p][0] + reps[q][0], reps[p][1] + reps[q][1]))]

    def neg(p):
        return idx[red((-reps[p][0], -reps[p][1]))]

    def mul_i(p):
        return idx[red((-reps[p][1], reps[p][0]))]
    return reps, idx, N, add, neg, mul_i


def corner_data(N, add, neg, mul_i):
    """third(b,u) = i*u + (1-i)*b, as an index table.  Complete, from the definition."""
    third = [[0] * N for _ in range(N)]
    for b in range(N):
        ib = mul_i(b)
        omi_b = add(b, neg(ib))                    # (1-i)*b
        for u in range(N):
            third[b][u] = add(mul_i(u), omi_b)
    return third


def verify_free(S, third):
    """definition-only check: no b != u in S with third[b][u] in S.  Shares no tables
    with the solver's pair/triple structures."""
    Sset = set(S)
    bad = 0
    for b in Sset:
        for u in Sset:
            if u == b:
                continue
            if third[b][u] in Sset:
                bad += 1
    return bad


# ------------------------------------------------------------------ exact solver

def exact_G(N, third, node_cap=None):
    """max square-corner-free subset of a quotient with N elements, exhaustively.

    Constraints, derived from the definition with all six orderings:
      * pairbad{a,b}: forbidden with only two distinct elements, i.e. third[a][b] == b
        or third[b][a] == a.  Non-empty exactly when (1-i) is a zero divisor.
      * triples: {a,b,c} distinct with third[p][r] == the remaining element for SOME
        ordered (p,r) drawn from the three.
    """
    pairbad = [[False] * N for _ in range(N)]
    for a in range(N):
        for b in range(N):
            if a == b:
                continue
            if third[a][b] == b or third[b][a] == a:
                pairbad[a][b] = pairbad[b][a] = True

    # completion lists: for each pair, which x completes a forbidden distinct triple
    comp = [[[] for _ in range(N)] for _ in range(N)]
    for a in range(N):
        for b in range(N):
            if a == b or pairbad[a][b]:
                continue
            for x in range(N):
                if x == a or x == b:
                    continue
                if (third[a][b] == x or third[b][a] == x or
                        third[a][x] == b or third[x][a] == b or
                        third[b][x] == a or third[x][b] == a):
                    comp[a][b].append(x)

    pbmask = [0] * N
    for a in range(N):
        m = 0
        for b in range(N):
            if pairbad[a][b]:
                m |= 1 << b
        pbmask[a] = m

    best = [0]
    bestset = [[]]
    nodes = [0]
    full = (1 << N) - 1

    def rec(cand, chosen, size):
        nodes[0] += 1
        if node_cap and nodes[0] > node_cap:
            raise TimeoutError
        if size + bin(cand).count("1") <= best[0]:
            return
        if cand == 0:
            if size > best[0]:
                best[0] = size
                bestset[0] = list(chosen)
            return
        v = (cand & -cand).bit_length() - 1
        # branch: include v
        nc = cand & ~(1 << v) & ~pbmask[v]
        for w in chosen:
            for x in comp[v][w]:
                nc &= ~(1 << x)
        rec(nc, chosen + [v], size + 1)
        # branch: exclude v
        rec(cand & ~(1 << v), chosen, size)

    # translations act transitively, so WLOG element 0 is chosen (N >= 1)
    nc = full & ~1 & ~pbmask[0]
    rec(nc, [0], 1)
    return best[0], bestset[0], nodes[0]


def greedy_G(N, third, restarts, seed):
    import random
    rng = random.Random(seed)
    order = list(range(N))
    best = []
    for _ in range(restarts):
        rng.shuffle(order)
        S, Sset = [], set()
        for x in order:
            ok = True
            for y in S:
                if third[x][y] in Sset or third[y][x] in Sset:
                    ok = False
                    break
                # x as the third point of a pair already inside
                if third[y][x] == x or third[x][y] == x:
                    ok = False
                    break
            if ok:
                for y in S:
                    for z in S:
                        if y != z and third[y][z] == x:
                            ok = False
                            break
                    if not ok:
                        break
            if ok:
                S.append(x)
                Sset.add(x)
        if len(S) > len(best):
            best = list(S)
    return best


# ---------------------------------------------------------------------- A1: box <= torus

def a1_box_torus():
    """measure the smallest multiple of n for which box-freeness == torus-freeness"""
    import random
    rng = random.Random(7)

    def box_free(S):
        Ss = set(S)
        for b in Ss:
            for u in Ss:
                if u == b:
                    continue
                w = (u[0] - b[0], u[1] - b[1])
                if (b[0] - w[1], b[1] + w[0]) in Ss:
                    return False
        return True

    def torus_free(S, q):
        Ss = set((x % q, y % q) for x, y in S)
        for b in Ss:
            for u in Ss:
                if u == b:
                    continue
                wx, wy = (u[0] - b[0]) % q, (u[1] - b[1]) % q
                if ((b[0] - wy) % q, (b[1] + wx) % q) in Ss:
                    return False
        return True

    print("A1  box-corner-free  vs  torus-corner-free  for S inside [0,n)^2")
    print(f"    {'n':>3} " + " ".join(f"q={f:>2}n{d:+d}" for f, d in
                                     ((2, 0), (2, 1), (3, 0), (4, 1))))
    for n in range(3, 9):
        cells = [(x, y) for x in range(n) for y in range(n)]
        res = []
        for f, d in ((2, 0), (2, 1), (3, 0), (4, 1)):
            q = f * n + d
            dis = 0
            for _ in range(4000):
                S = rng.sample(cells, rng.randint(3, min(len(cells), 10)))
                if box_free(S) != torus_free(S, q):
                    dis += 1
            res.append(dis)
        print(f"    {n:>3} " + " ".join(f"{r:>8}" for r in res))
    print("    (0 = the two notions coincide; nonzero = wraparound corner bites)")


# ------------------------------------------------------------------------- main

def main():
    a1_box_torus()

    print("\nA2  cross-check: G((q)) must reproduce the known exact g(q)")
    known = {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 8, 8: 9}
    for q, gq in known.items():
        reps, idx, N, add, neg, mul_i = build_quotient((q, 0))
        third = corner_data(N, add, neg, mul_i)
        try:
            val, wit, nodes = exact_G(N, third, node_cap=40_000_000)
            v = verify_free(wit, third)
            ok = "OK" if val == gq and v == 0 else "*** MISMATCH"
            print(f"    q={q:>3}  N={N:>4}  G={val:>3}  known g={gq:>3}  "
                  f"viol={v}  nodes={nodes:>10}  {ok}")
        except TimeoutError:
            print(f"    q={q:>3}  N={N:>4}  node cap hit")

    print("\nA3  THE (1+i) TOWER.  alpha = (1+i)^j,  N = 2^j,  index 2 per step.")
    print(f"    {'j':>3} {'N':>6} {'G':>5} {'exact':>6} {'ratio':>7} "
          f"{'log G/log N':>12} {'viol':>5}")
    prev = None
    ladder = []
    a, b = 1, 0
    for j in range(1, 15):
        a, b = a - b, a + b                       # multiply by (1+i)
        reps, idx, N, add, neg, mul_i = build_quotient((a, b))
        third = corner_data(N, add, neg, mul_i)
        exact = True
        try:
            if N > 160:
                raise TimeoutError
            val, wit, nodes = exact_G(N, third, node_cap=120_000_000)
        except TimeoutError:
            exact = False
            wit = greedy_G(N, third, max(6, 200000 // N), 4242 + j)
            val = len(wit)
        v = verify_free(wit, third)
        r = "" if prev is None else f"{val/prev:.4f}"
        lam = math.log(val) / math.log(N) if val > 1 else float("nan")
        flag = "" if v == 0 else "   *** VIOLATIONS -- BUG"
        print(f"    {j:>3} {N:>6} {val:>5} {str(exact):>6} {r:>7} {lam:>12.4f} "
              f"{v:>5}{flag}")
        ladder.append((j, N, val, exact))
        prev = val
        if N > 4096:
            break

    print("\nA4  the doubling budget.  need every ratio < 2 (a bound of c gives")
    print("    C(n) = O(n^{2 log2 c}); c=2 is exactly the trivial n^2).")
    rs = [(ladder[t][2] / ladder[t - 1][2], ladder[t][0], ladder[t][3] and
           ladder[t - 1][3]) for t in range(1, len(ladder))]
    for r, j, ex in rs:
        tag = "exact" if ex else "lower bound only"
        print(f"    step {j-1}->{j}:  ratio {r:.4f}   "
              f"budget 2.0000   slack {2-r:+.4f}   ({tag})")
    exr = [r for r, _, ex in rs if ex]
    if exr:
        print(f"\n    worst exact ratio: {max(exr):.4f}   "
              f"implied exponent 2*log2(c) = {2*math.log2(max(exr)):.4f}")
        print("    (that exponent is what a PROOF of the recurrence would deliver;")
        print("     measured ratios are lower-bound evidence only, never a proof)")


if __name__ == "__main__":
    main()
