"""g(q) = max square-corner-free subset of the TORUS (Z_q)^2.

Why this is the decisive quantity.

TENSOR LEMMA (proved, no carry conditions needed).  Let T subset (Z_q)^2 be
square-corner-free on the torus.  Put S = { sum_j d_j q^j : d_j in T } subset [q^d]^2.
Then S is square-corner-free and |S| = |T|^d.
  Proof.  Let b,u,v in S with v = i*u + (1-i)*b, u != b.  Reducing mod q gives
  v_0 = i*u_0 + (1-i)*b_0 with b_0,u_0,v_0 in T, which is a torus square corner unless
  u_0 = b_0; so u_0 = b_0, hence v_0 = b_0 as well.  Then w = u-b = 0 mod q, so
  w = q w', and dividing the equation by q leaves the same configuration on the
  d-1 higher digits.  Induction on d.  QED

Hence   Q_SQ(n) >= n^{log g(q) / log q}   for every q,   so the exponent
        gamma = lim log Q_SQ(n)/log n   satisfies   gamma >= sup_q log g(q)/log q.

A LINE {(t, a t) : t in Z_q} with 1 + a^2 invertible mod q is torus square-corner-free
(w and i*w both on the line forces (1+a^2) w = 0), so g(q) >= q always, giving
gamma >= 1 -- which is only the trivial bound.  The decisive question is therefore

        IS g(q) > q FOR SOME q ?

If yes, square-corner-free sets are provably SUPERLINEAR and the relaxation cannot
prove C(n) = O(n^{1+o(1)}).  If g(q) = q for all q, that is strong evidence the
relaxation is tight at n^{1+o(1)} and the route survives.

Exhaustive branch and bound, exact integer arithmetic on the torus.
"""
import sys
from time import time


def build(q):
    """cells, and for each ordered pair (b,u) the third cell v = b + i*(u-b)."""
    N = q * q
    idx = lambda x, y: (x % q) * q + (y % q)
    third = [[0] * N for _ in range(N)]
    for bx in range(q):
        for by in range(q):
            b = idx(bx, by)
            for ux in range(q):
                for uy in range(q):
                    u = idx(ux, uy)
                    wx, wy = ux - bx, uy - by
                    third[b][u] = idx(bx - wy, by + wx)
    return N, third


def solve(q, verbose=True, best_known=None):
    """exact max square-corner-free subset of (Z_q)^2"""
    N, third = build(q)
    # forb[b][u] = bitmask of cells that become illegal once both b and u are chosen.
    # A square corner needs an apex and two legs; with S known, adding p can create a
    # corner in three ways (p as apex, p as first leg, p as second leg).  We handle it
    # by the direct incremental test below instead of precomputed masks, which keeps
    # the code obviously correct.
    best = [0 if best_known is None else best_known]
    bestset = [None]
    nodes = [0]

    def addable(S, p):
        """is S+{p} still square-corner-free?  Checks every triple containing p."""
        Sset = S[1]
        for b in S[0]:
            # p as a leg with apex b, other leg must not be present
            if third[b][p] in Sset:
                return False
            # p as apex
            if third[p][b] in Sset:
                return False
            # b as a leg with apex p handled by third[p][b]; p as the SECOND leg:
            # need b' with third[b'][b] == p  -> scan
        for b in S[0]:
            for c in S[0]:
                if third[b][c] == p:
                    return False
        return True

    order = list(range(N))

    def rec(S, cand):
        nodes[0] += 1
        if len(S[0]) + len(cand) <= best[0]:
            return
        if not cand:
            if len(S[0]) > best[0]:
                best[0] = len(S[0])
                bestset[0] = list(S[0])
            return
        if len(S[0]) > best[0]:
            best[0] = len(S[0])
            bestset[0] = list(S[0])
        for k, p in enumerate(cand):
            if len(S[0]) + len(cand) - k <= best[0]:
                return
            S[0].append(p)
            S[1].add(p)
            rest = [x for x in cand[k + 1:] if addable(S, x)]
            rec(S, rest)
            S[0].pop()
            S[1].discard(p)

    t0 = time()
    # symmetry: fix that cell 0 = (0,0) is in S (the problem is translation invariant
    # on the torus, so every nonempty solution has a translate containing (0,0))
    S = [[0], {0}]
    cand = [p for p in order[1:] if addable(S, p)]
    rec(S, cand)
    dt = time() - t0
    if verbose:
        print(f"q={q:3d}  g(q) = {best[0]:4d}   (q = {q})   "
              f"log g/log q = {__import__('math').log(best[0])/__import__('math').log(q):.5f}   "
              f"nodes={nodes[0]:,}  {dt:.1f}s")
        if best[0] > q:
            print(f"      *** g({q}) > {q}: SUPERLINEAR.  witness = "
                  f"{sorted((c//q, c%q) for c in bestset[0])}")
    return best[0], bestset[0]


if __name__ == "__main__":
    qs = [int(a) for a in sys.argv[1:]] or [2, 3, 4, 5, 6, 7, 8, 9]
    for q in qs:
        solve(q)
