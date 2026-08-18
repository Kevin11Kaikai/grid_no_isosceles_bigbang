"""Control experiment: can a small-scale doubling ratio distinguish survival from death?

The (1+i)-tower ratios for square corners look reassuring (~1.5 against a budget of 2).
Before that is allowed to count as evidence, the instrument must be calibrated against a
relation whose fate is ALREADY KNOWN.

    target   : square corners,  third(b,u) = i*u + (1-i)*b,  tower Z[i]/(1+i)^j, index 2
    control  : 3-term APs,      third(b,u) = 2*u - b,        tower Z/3^m,        index 3

For the control the answer is known: Behrend gives 3-AP-free subsets of [N] of size
N^{1-o(1)}, so the local exponent  lambda_local = log(ratio)/log(index)  MUST tend to 1
and the ratio MUST creep up to the full budget.  But the creep is only exp(-c*sqrt(log N)),
which at N = 81 or 243 is a factor of order one.

SO THE QUESTION THIS SCRIPT ANSWERS IS ABOUT MY OWN INSTRUMENT, NOT ABOUT THE PROBLEM:
if the control also reads lambda_local ~ 0.6 at these scales, then the target's ~1.5
ratios are worth nothing, and the (1+i)-tower ratio data must be recorded as
uninformative rather than as support.  This is failure-ledger F1 applied to new evidence
instead of to old evidence.

Same solver for both relations, so the comparison is not confounded by the search.
"""
import math


def solve(N, third, node_cap=200_000_000):
    """max subset of Z/N (as index set 0..N-1) with no b != u and third(b,u) inside.

    All six ordered assignments are enumerated for the pair-completion table, and the
    two-distinct-element case (third(b,u) in {b,u}) is handled separately -- the exact
    two omissions that produced three wrong results earlier in this campaign.
    """
    T = [[third(b, u) for u in range(N)] for b in range(N)]

    pairbad = [[False] * N for _ in range(N)]
    for a in range(N):
        for b in range(N):
            if a != b and (T[a][b] == b or T[b][a] == a or
                           T[a][b] == a or T[b][a] == b):
                pairbad[a][b] = pairbad[b][a] = True

    comp = [[[] for _ in range(N)] for _ in range(N)]
    for a in range(N):
        for b in range(N):
            if a == b or pairbad[a][b]:
                continue
            for x in range(N):
                if x == a or x == b:
                    continue
                if (T[a][b] == x or T[b][a] == x or T[a][x] == b or
                        T[x][a] == b or T[b][x] == a or T[x][b] == a):
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

    def rec(cand, chosen, size):
        nodes[0] += 1
        if nodes[0] > node_cap:
            raise TimeoutError
        if size + bin(cand).count("1") <= best[0]:
            return
        if cand == 0:
            if size > best[0]:
                best[0] = size
                bestset[0] = list(chosen)
            return
        v = (cand & -cand).bit_length() - 1
        nc = cand & ~(1 << v) & ~pbmask[v]
        for w in chosen:
            for x in comp[v][w]:
                nc &= ~(1 << x)
        rec(nc, chosen + [v], size + 1)
        rec(cand & ~(1 << v), chosen, size)

    rec(((1 << N) - 1) & ~1 & ~pbmask[0], [0], 1)   # translations: WLOG 0 in S
    return best[0], bestset[0], nodes[0]


def check(S, N, third):
    """definition-only verifier, no tables shared with solve()"""
    Ss = set(S)
    bad = 0
    for b in Ss:
        for u in Ss:
            if u != b and third(b, u) in Ss:
                bad += 1
    return bad


def main():
    print("CONTROL: 3-term APs in Z/3^m.  third(b,u) = 2u - b.  index 3, budget 3.")
    print("         Behrend forces lambda_local -> 1, i.e. ratio -> 3.")
    print(f"    {'m':>3} {'N':>6} {'r3':>5} {'ratio':>7} {'lambda_local':>13} "
          f"{'log r3/log N':>13} {'viol':>5}")
    prev = None
    ctrl = []
    for m in range(1, 6):
        N = 3 ** m
        try:
            val, wit, nodes = solve(N, lambda b, u: (2 * u - b) % N,
                                    node_cap=60_000_000)
        except TimeoutError:
            print(f"    {m:>3} {N:>6}   node cap hit -- exact search abandoned")
            break
        v = check(wit, N, lambda b, u: (2 * u - b) % N)
        r = None if prev is None else val / prev
        ll = float("nan") if r is None else math.log(r) / math.log(3)
        print(f"    {m:>3} {N:>6} {val:>5} "
              f"{('%.4f' % r) if r else '':>7} "
              f"{ll:>13.4f} {math.log(val)/math.log(N):>13.4f} {v:>5}")
        ctrl.append((N, val, ll))
        prev = val

    print("\nCONTROL 2: 3-term APs in Z/2^m.  same tower index as the target (2).")
    print(f"    {'m':>3} {'N':>6} {'r3':>5} {'ratio':>7} {'lambda_local':>13} "
          f"{'viol':>5}")
    prev = None
    ctrl2 = []
    for m in range(2, 9):
        N = 2 ** m
        try:
            val, wit, nodes = solve(N, lambda b, u: (2 * u - b) % N,
                                    node_cap=60_000_000)
        except TimeoutError:
            print(f"    {m:>3} {N:>6}   node cap hit")
            break
        v = check(wit, N, lambda b, u: (2 * u - b) % N)
        r = None if prev is None else val / prev
        ll = float("nan") if r is None else math.log(r) / math.log(2)
        print(f"    {m:>3} {N:>6} {val:>5} "
              f"{('%.4f' % r) if r else '':>7} {ll:>13.4f} {v:>5}")
        ctrl2.append((N, val, ll))
        prev = val

    print("\nVERDICT ON THE INSTRUMENT")
    good = [ll for _, _, ll in ctrl if not math.isnan(ll)]
    good2 = [ll for _, _, ll in ctrl2 if not math.isnan(ll)]
    for nm, gs in (("Z/3^m", good), ("Z/2^m", good2)):
        if gs:
            print(f"    control {nm}: lambda_local = "
                  f"{[f'{x:.3f}' for x in gs]}  (truth: -> 1.000)")
    allg = good + good2
    if allg and max(allg) < 0.95:
        print("\n    The control reads WELL BELOW its own true limit of 1 at these")
        print("    scales.  Therefore small-scale tower ratios CANNOT distinguish a")
        print("    surviving relation from a dying one, and the (1+i)-tower ratios")
        print("    must be recorded as UNINFORMATIVE, not as support for route SQ.")
    else:
        print("\n    The control already reads near its true limit, so the target's")
        print("    ratios staying low WOULD be meaningful.  Report the margin.")


if __name__ == "__main__":
    main()
