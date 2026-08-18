"""Frozen isosceles-freeness checker. Exact integer squared distances.

S is isosceles-free iff no three distinct a,b,c have |a-b|^2 = |b-c|^2
(degenerate collinear midpoints included). Equivalent: for every apex b,
squared distances to other points of S are pairwise distinct (RF3).
"""


def iso_triples(pts):
    """List (b, a, c, r2) with a != c, |a-b|^2 = |c-b|^2 = r2 > 0."""
    P = [tuple(p) for p in pts]
    out = []
    for i, b in enumerate(P):
        by_r = {}
        for j, a in enumerate(P):
            if j == i:
                continue
            r2 = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            by_r.setdefault(r2, []).append(a)
        for r2, group in by_r.items():
            if len(group) < 2:
                continue
            for ia in range(len(group)):
                for ic in range(ia + 1, len(group)):
                    out.append((b, group[ia], group[ic], r2))
    return out


def is_iso_free(pts):
    P = [tuple(p) for p in pts]
    for b in P:
        seen = set()
        for a in P:
            if a == b:
                continue
            r2 = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            if r2 in seen:
                return False
            seen.add(r2)
    return True
