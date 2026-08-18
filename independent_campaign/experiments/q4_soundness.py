"""SOUNDNESS CHECK for the four-direction line-kill relaxation (Q4).

Q4 is only useful if every isosceles-free set satisfies it.  This script generates
genuinely isosceles-free sets (greedy, many random orders, several n) with an exact
verifier, and checks each against all four Q4 constraint families.

Any violation would mean the L2b derivation is wrong and Q4 is NOT a valid relaxation.

Exact integer arithmetic only.
"""
import random
from four_direction_linekill import verify as q4_verify


def isosceles_free_greedy(n, rng):
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    S = []
    dists = {}          # point -> set of squared distances already used from it
    for p in cells:
        ok = True
        newd = {}
        dp = set()
        for q in S:
            r = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
            if r in dp or r in dists[q]:
                ok = False
                break
            dp.add(r)
            newd[q] = r
        if ok:
            for q, r in newd.items():
                dists[q].add(r)
            dists[p] = dp
            S.append(p)
    return S


def is_isosceles_free(S):
    for b in S:
        seen = set()
        for a in S:
            if a == b:
                continue
            r = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            if r in seen:
                return False
            seen.add(r)
    return True


if __name__ == "__main__":
    total = 0
    bad = 0
    for n in (8, 12, 16, 24, 32):
        rng = random.Random(999 + n)
        sizes = []
        for _ in range(25):
            S = isosceles_free_greedy(n, rng)
            assert is_isosceles_free(S), "generator produced a non-isosceles-free set"
            sizes.append(len(S))
            total += 1
            if not q4_verify(n, S):
                bad += 1
        print(f"n={n:3d}  isosceles-free greedy sizes: min={min(sizes)} max={max(sizes)}"
              f"  ({len(sizes)} sets, all Q4-feasible: {bad == 0})")
    print(f"\nTOTAL isosceles-free sets tested: {total}   Q4 VIOLATIONS: {bad}")
    print("Q4 is a valid relaxation of isosceles-freeness" if bad == 0
          else "*** Q4 DERIVATION IS WRONG ***")
