"""Frozen square-corner checker. Exact integer arithmetic. No iso6 import.

A square-corner is three points {b, b+w, b+R(w)} with w ≠ 0 and
R = rotate ±90° on Z^2: R_+(p,q)=(-q,p), R_-(p,q)=(q,-p).

This is Cursor J1 / Claude's square-corner. Implied by isosceles-freeness
because |w|^2 = |R(w)|^2.
"""


def rot90_pm(w):
    p, q = w
    return ((-q, p), (q, -p))


def square_corners(pts, cap=None):
    """Unique unordered triples that form a square-corner. Apex listed first in recs."""
    P = set(map(tuple, pts))
    seen = set()
    hits = []
    for b in P:
        bx, by = b
        for a in P:
            if a == b:
                continue
            w = (a[0] - bx, a[1] - by)
            for rw in rot90_pm(w):
                c = (bx + rw[0], by + rw[1])
                if c in P and c != a and c != b:
                    tri = frozenset((b, a, c))
                    if tri in seen:
                        continue
                    seen.add(tri)
                    hits.append({"apex": b, "w": w, "rw": rw, "pts": tri})
                    if cap is not None and len(hits) >= cap:
                        return hits
    return hits


def count_square_corners(pts, cap=20000):
    hits = square_corners(pts, cap=cap)
    return len(hits)


def is_sq_free(pts):
    P = set(map(tuple, pts))
    for b in P:
        bx, by = b
        for a in P:
            if a == b:
                continue
            w = (a[0] - bx, a[1] - by)
            for rw in rot90_pm(w):
                c = (bx + rw[0], by + rw[1])
                if c in P and c != a and c != b:
                    return False
    return True


def can_add(P, p):
    """P is a set of points already sq-free. True iff P ∪ {p} is sq-free."""
    px, py = p
    if p in P:
        return False
    for b in P:
        w = (px - b[0], py - b[1])
        for rw in rot90_pm(w):
            c = (b[0] + rw[0], b[1] + rw[1])
            if c == p:
                continue
            if c in P:
                return False
        # p as apex: legs to b and to some c = p+R(b-p)
        w2 = (b[0] - px, b[1] - py)
        for rw in rot90_pm(w2):
            c = (px + rw[0], py + rw[1])
            if c in P and c != b:
                return False
    return True


def repair_delete_participants(pts):
    """One-shot: drop every point that sits in any square-corner. Remaining is sq-free."""
    P = set(map(tuple, pts))
    if len(P) > 5000:
        return repair_sq_free(pts, max_rounds=120)
    corners = square_corners(P)
    if not corners:
        return P, 0, 0
    bad = set()
    for h in corners:
        bad |= set(h["pts"])
    Q = P - bad
    return Q, len(bad), count_square_corners(Q)


def repair_sq_free(pts, max_rounds=40):
    """Delete a max-degree hitting vertex per round until sq-free or cap.

    Lower bound: remaining set is sq-free (or we report leftover corners).
    """
    from collections import Counter

    P = set(map(tuple, pts))
    deleted = 0
    for _ in range(max_rounds):
        corners = square_corners(P)
        if not corners:
            return P, deleted, 0
        deg = Counter()
        for h in corners:
            for q in h["pts"]:
                deg[q] += 1
        victim = max(deg, key=deg.get)
        P.remove(victim)
        deleted += 1
    leftover = count_square_corners(P)
    return P, deleted, leftover
