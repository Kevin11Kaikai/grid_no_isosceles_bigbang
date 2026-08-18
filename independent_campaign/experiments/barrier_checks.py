"""Verification of the barrier constructions in docs/barriers.md.

B2 : B x B is 3-AP-free in Z^2 whenever B is 3-AP-free in Z.
B3': B x B satisfies every row/column line-kill constraint (L2b, axis directions),
     yet is very far from isosceles-free -- so the axis line-kill mechanism alone
     cannot prove better than n^{2-o(1)}.
     It DOES violate the diagonal line-kill constraint, showing the diagonal /
     multi-direction content of L2 is strictly stronger than rows+columns.

Exact integer arithmetic only.
"""
from itertools import combinations


def three_ap_free(B):
    Bs = set(B)
    for a in B:
        for c in B:
            if a < c and (a + c) % 2 == 0 and (a + c) // 2 in Bs:
                return False
    return True


def base3_no_two(N):
    """Classic 3-AP-free set: integers < N whose base-3 expansion omits the digit 2."""
    out = []
    for x in range(N):
        t, ok = x, True
        while t:
            if t % 3 == 2:
                ok = False
                break
            t //= 3
        if ok:
            out.append(x)
    return out


def is_isosceles_free(S):
    S = list(S)
    for b in S:
        seen = set()
        for a in S:
            if a == b:
                continue
            r = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            if r in seen:
                return False, (b, a, r)
            seen.add(r)
    return True, None


def midpoints_same_parity(A):
    return {(a + c) // 2 for a, c in combinations(sorted(A), 2) if (a + c) % 2 == 0}


def check_axis_linekill(S):
    """L2b for e=(1,0),(0,1): row pairs of equal x-parity must kill a wholly empty column,
    and symmetrically. Returns list of violations."""
    pts = set(S)
    occ_cols = {p[0] for p in pts}
    occ_rows = {p[1] for p in pts}
    viol = []
    rows = {}
    for x, y in pts:
        rows.setdefault(y, []).append(x)
    for y, X in rows.items():
        for k in midpoints_same_parity(X):
            if k in occ_cols:
                viol.append(("row", y, k))
    cols = {}
    for x, y in pts:
        cols.setdefault(x, []).append(y)
    for x, Y in cols.items():
        for k in midpoints_same_parity(Y):
            if k in occ_rows:
                viol.append(("col", x, k))
    return viol


def check_diag_linekill(S):
    """L2b for e=(1,1): pairs on a common diagonal (x-y const) kill the anti-diagonal
    at the mean of their x+y values (no parity condition)."""
    pts = set(S)
    occ_anti = {p[0] + p[1] for p in pts}
    diags = {}
    for x, y in pts:
        diags.setdefault(x - y, []).append(x + y)
    viol = []
    for d, A in diags.items():
        for a, c in combinations(sorted(A), 2):
            if (a + c) // 2 in occ_anti:
                viol.append((d, a, c, (a + c) // 2))
    return viol


if __name__ == "__main__":
    for N in (9, 27, 81):
        B = base3_no_two(N)
        assert three_ap_free(B), N
        S = [(x, y) for x in B for y in B]
        ok, wit = is_isosceles_free(S)
        av = check_axis_linekill(S)
        dv = check_diag_linekill(S)
        print(f"N={N:3d}  |B|={len(B):3d}  |BxB|={len(S):5d}  "
              f"isosceles-free={ok}  axis-linekill violations={len(av)}  "
              f"diagonal-linekill violations={len(dv)}")
        if not ok:
            print(f"        witness (apex, point, sq.dist) = {wit}")
