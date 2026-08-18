"""Route Q -- INDEPENDENT Q4 verifiers, written from the definition.

Q4 constraint system for S subset of {0,..,n-1}^2.  M(A) = { (a+a')/2 : a != a' in A,
a == a' mod 2 } (same-parity midpoints -- an integer set).

  U_col = { x : (x,y) in S }        occupied columns
  U_row = { y : (x,y) in S }        occupied rows
  U_dia = { x-y : (x,y) in S }      occupied diagonals
  U_ant = { x+y : (x,y) in S }      occupied anti-diagonals

  (1) every row y        : M(X_y) cap U_col = empty,  X_y = { x : (x,y) in S }
  (2) every column x     : M(Y_x) cap U_row = empty,  Y_x = { y : (x,y) in S }
  (3) every diagonal d   : M(A_d) cap U_ant = empty,  A_d = { x+y : (x,y) in S, x-y=d }
  (4) every antidiag a   : M(D_a) cap U_dia = empty,  D_a = { x-y : (x,y) in S, x+y=a }

TWO independent implementations, cross-checked against each other.
Exact integer arithmetic only.  No dependency on experiments/four_direction_linekill.py.
"""
from itertools import combinations


# ----------------------------------------------------------------------------
# V1 : brute force over unordered pairs, direct transcription of the definition
# ----------------------------------------------------------------------------
def violations_v1(n, S):
    """Return list of violations (constraint_id, p, q, killed_line_value).

    Pure pair loop.  For each pair of points sharing a line, form the midpoint of
    the transversal coordinate and test membership in the corresponding occupied set.
    """
    P = sorted(set(S))
    for (x, y) in P:
        if not (0 <= x < n and 0 <= y < n):
            raise ValueError(f"point {(x,y)} outside grid [0,{n})^2")
    Ucol = {p[0] for p in P}
    Urow = {p[1] for p in P}
    Udia = {p[0] - p[1] for p in P}
    Uant = {p[0] + p[1] for p in P}
    bad = []
    for p, q in combinations(P, 2):
        x1, y1 = p
        x2, y2 = q
        # (1) common row -> kills a column
        if y1 == y2 and (x1 + x2) % 2 == 0:
            mid = (x1 + x2) // 2
            if mid in Ucol:
                bad.append((1, p, q, mid))
        # (2) common column -> kills a row
        if x1 == x2 and (y1 + y2) % 2 == 0:
            mid = (y1 + y2) // 2
            if mid in Urow:
                bad.append((2, p, q, mid))
        # (3) common diagonal (x-y equal) -> kills an anti-diagonal
        if x1 - y1 == x2 - y2:
            s1, s2 = x1 + y1, x2 + y2
            assert (s1 + s2) % 2 == 0, "same diagonal must give equal parity of x+y"
            mid = (s1 + s2) // 2
            if mid in Uant:
                bad.append((3, p, q, mid))
        # (4) common anti-diagonal (x+y equal) -> kills a diagonal
        if x1 + y1 == x2 + y2:
            d1, d2 = x1 - y1, x2 - y2
            assert (d1 + d2) % 2 == 0, "same anti-diagonal must give equal parity of x-y"
            mid = (d1 + d2) // 2
            if mid in Udia:
                bad.append((4, p, q, mid))
    return bad


# ----------------------------------------------------------------------------
# V2 : line-by-line, builds M(.) explicitly and intersects with the occupied set
# ----------------------------------------------------------------------------
def midpoints(A):
    """M(A) = same-parity midpoints of distinct pairs of the integer set A."""
    A = sorted(set(A))
    out = set()
    ev = [a for a in A if a % 2 == 0]
    od = [a for a in A if a % 2 == 1]
    for cls in (ev, od):
        for i in range(len(cls)):
            for j in range(i + 1, len(cls)):
                out.add((cls[i] + cls[j]) // 2)
    return out


def violations_v2(n, S):
    """Return dict constraint_id -> sorted list of (line_label, offending_midpoint)."""
    P = set(S)
    rows, cols, dias, ants = {}, {}, {}, {}
    for (x, y) in P:
        rows.setdefault(y, set()).add(x)
        cols.setdefault(x, set()).add(y)
        dias.setdefault(x - y, set()).add(x + y)
        ants.setdefault(x + y, set()).add(x - y)
    Ucol = set(cols)
    Urow = set(rows)
    Udia = set(dias)
    Uant = set(ants)
    out = {1: [], 2: [], 3: [], 4: []}
    for y, X in rows.items():
        for v in sorted(midpoints(X) & Ucol):
            out[1].append((y, v))
    for x, Y in cols.items():
        for v in sorted(midpoints(Y) & Urow):
            out[2].append((x, v))
    for d, A in dias.items():
        for v in sorted(midpoints(A) & Uant):
            out[3].append((d, v))
    for a, D in ants.items():
        for v in sorted(midpoints(D) & Udia):
            out[4].append((a, v))
    return out


def is_feasible(n, S, cross_check=True):
    """True iff S is Q4-feasible.  Runs V2 always; V1 too when cross_check and |S| small."""
    v2 = violations_v2(n, S)
    ok2 = all(len(v) == 0 for v in v2.values())
    if cross_check and len(S) <= 2500:
        v1 = violations_v1(n, S)
        ok1 = (len(v1) == 0)
        if ok1 != ok2:
            raise AssertionError(f"VERIFIER DISAGREEMENT: v1={ok1} v2={ok2}")
        # deeper cross-check: same set of (constraint, line, midpoint) incidences
        inc1 = {(c, (p[1] if c == 1 else p[0] if c == 2 else
                     p[0] - p[1] if c == 3 else p[0] + p[1]), mid)
                for (c, p, q, mid) in v1}
        inc2 = {(c, ln, mid) for c in v2 for (ln, mid) in v2[c]}
        if inc1 != inc2:
            raise AssertionError("VERIFIER DISAGREEMENT on violation incidences")
    return ok2


# ----------------------------------------------------------------------------
# also: exact isosceles-freeness, used to re-confirm soundness C(n) <= Q4(n)
# ----------------------------------------------------------------------------
def is_isosceles_free(S):
    P = list(set(S))
    for b in P:
        seen = set()
        for a in P:
            if a == b:
                continue
            r = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            if r in seen:
                return False
            seen.add(r)
    return True


if __name__ == "__main__":
    import random
    rng = random.Random(7)
    # sanity: the two verifiers agree on random sets
    disagree = 0
    for trial in range(400):
        n = rng.randint(3, 12)
        k = rng.randint(1, 10)
        S = set()
        while len(S) < k:
            S.add((rng.randrange(n), rng.randrange(n)))
        is_feasible(n, S)          # raises on disagreement
        disagree += 0
    print("V1/V2 cross-check on 400 random sets: OK")

    # soundness spot check: brute-force isosceles-free sets must be Q4-feasible
    bad = 0
    tested = 0
    for trial in range(3000):
        n = rng.randint(4, 9)
        S = set()
        cells = [(x, y) for x in range(n) for y in range(n)]
        rng.shuffle(cells)
        for c in cells:
            T = S | {c}
            if is_isosceles_free(T):
                S = T
        tested += 1
        if not is_feasible(n, S):
            bad += 1
    print(f"soundness: {tested} greedy-maximal isosceles-free sets, Q4 violations in {bad}")
