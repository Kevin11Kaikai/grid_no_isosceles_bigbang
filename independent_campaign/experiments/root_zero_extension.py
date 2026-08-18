"""Root verification of the boundary branch's partial claim.

CLAIM (from route E, terminated before writing it up):
  for n = 3,4,6 EVERY optimal isosceles-free set in [n]^2 admits ZERO additions from the
  L-strip, yet C(n+1) > C(n).

If true this is important: it means an optimal (n+1)-set never restricts to an optimal
n-set, so the naive induction "take an extremal interior and count addable strip cells"
is not merely lossy but measures the wrong quantity entirely.

We verify by exhaustive enumeration: all maximum isosceles-free subsets of [n]^2, then for
each, whether any single cell of the L-strip of [n+1]^2 can be added.

Exact integer arithmetic only.
"""
from itertools import combinations


def iso_free(pts):
    for b in pts:
        seen = set()
        for a in pts:
            if a == b:
                continue
            r = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            if r in seen:
                return False
            seen.add(r)
    return True


def max_sets(n, cap=None):
    """All maximum isosceles-free subsets of [n]^2 (exhaustive)."""
    cells = [(x, y) for x in range(n) for y in range(n)]
    best, out = 0, []
    # branch and bound on size, descending
    for size in range(len(cells), 0, -1):
        if cap is not None and size > cap:
            continue
        found = []
        for c in combinations(cells, size):
            if iso_free(c):
                found.append(c)
        if found:
            return size, found
    return 0, []


def strip(n):
    """cells of [n+1]^2 not in [n]^2"""
    return [(x, n) for x in range(n + 1)] + [(n, y) for y in range(n)]


if __name__ == "__main__":
    known = {1: 1, 2: 2, 3: 4, 4: 6, 5: 7, 6: 9, 7: 10}
    print(f"{'n':>3} {'C(n)':>5} {'#optima':>8} {'optima with >=1 strip addition':>32} "
          f"{'C(n+1)':>7}")
    for n in (3, 4, 5, 6):
        size, opts = max_sets(n, cap=known.get(n))
        assert size == known[n], f"C({n}) mismatch: got {size}, expected {known[n]}"
        st = strip(n)
        extendable = 0
        for S in opts:
            if any(iso_free(tuple(S) + (c,)) for c in st):
                extendable += 1
        print(f"{n:>3} {size:>5} {len(opts):>8} {extendable:>32} {known[n+1]:>7}")
        if extendable == 0:
            print(f"      -> CONFIRMED: no optimal {n}x{n} set extends into the strip, "
                  f"yet C({n+1})={known[n+1]} > C({n})={size}")
