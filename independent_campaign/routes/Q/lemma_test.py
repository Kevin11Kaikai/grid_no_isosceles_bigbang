"""Route Q -- exhaustive/randomised test of the KEY LEMMA.

KEY LEMMA (claim).  If S subset [0,n)^2 has all four projections
    x(S),  y(S),  (x+y)(S),  (x-y)(S)
3-AP-free as sets of integers, then S is Q4-feasible.

We test it two ways:
  (A) brute force over ALL S in small grids (n <= 4) -- exhaustive.
  (B) randomised over larger grids, including sets built as
      { (x,y) : x in B1, y in B2, x+y in C, x-y in D } for random 3-AP-free B1,B2,C,D.
Also tests the CONVERSE (it is false, and we record how false) -- the lemma is only
a sufficient condition, which is all a lower-bound construction needs.
"""
import random
import sys
from itertools import combinations, chain

sys.path.insert(0, __file__.replace("\\", "/").rsplit("/", 1)[0])
from q4_verify import is_feasible, violations_v1, violations_v2


def is_3ap_free(A):
    A = set(A)
    L = sorted(A)
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            if (L[i] + L[j]) % 2 == 0 and (L[i] + L[j]) // 2 in A:
                return False
    return True


def four_projections_3apfree(S):
    return (is_3ap_free({p[0] for p in S}) and
            is_3ap_free({p[1] for p in S}) and
            is_3ap_free({p[0] + p[1] for p in S}) and
            is_3ap_free({p[0] - p[1] for p in S}))


def exhaustive(n):
    cells = [(x, y) for x in range(n) for y in range(n)]
    tot = 0
    hyp = 0
    counter = 0
    maxfeas = 0
    for k in range(len(cells) + 1):
        for S in combinations(cells, k):
            S = set(S)
            tot += 1
            f = is_feasible(n, S)
            if f:
                maxfeas = max(maxfeas, len(S))
            if four_projections_3apfree(S):
                hyp += 1
                if not f:
                    counter += 1
                    print("   COUNTEREXAMPLE TO LEMMA:", sorted(S))
                    print("     v1:", violations_v1(n, S))
    return tot, hyp, counter, maxfeas


def random_3apfree(lo, hi, rng, target):
    """Greedy random 3-AP-free subset of [lo,hi)."""
    pool = list(range(lo, hi))
    rng.shuffle(pool)
    A = set()
    for a in pool:
        ok = True
        for b in A:
            if (a + b) % 2 == 0 and (a + b) // 2 in A:
                ok = False
                break
            if 2 * a - b in A or 2 * b - a in A:
                ok = False
                break
        if ok:
            A.add(a)
        if len(A) >= target:
            break
    return A


def main():
    print("== (A) exhaustive over all subsets of small grids ==")
    for n in (2, 3, 4):
        tot, hyp, counter, mx = exhaustive(n)
        print(f"  n={n}: {tot} subsets, {hyp} satisfy the 4-projection hypothesis, "
              f"{counter} counterexamples;  exact Q4({n}) = {mx}")

    print("== (B) randomised: S = {x in B1, y in B2, x+y in C, x-y in D} ==")
    rng = random.Random(2024)
    bad = 0
    trials = 0
    sizes = []
    for _ in range(600):
        n = rng.randint(6, 40)
        B1 = random_3apfree(0, n, rng, rng.randint(2, n))
        B2 = random_3apfree(0, n, rng, rng.randint(2, n))
        C = random_3apfree(0, 2 * n, rng, rng.randint(2, 2 * n))
        D = random_3apfree(-n, n, rng, rng.randint(2, 2 * n))
        S = {(x, y) for x in B1 for y in B2 if (x + y) in C and (x - y) in D}
        if not S:
            continue
        trials += 1
        sizes.append(len(S))
        assert four_projections_3apfree(S), "projections should be 3-AP-free"
        if not is_feasible(n, S):
            bad += 1
            print("   COUNTEREXAMPLE:", n, sorted(S))
    print(f"  {trials} nonempty instances, max |S| = {max(sizes)}, VIOLATIONS = {bad}")

    print("== (C) randomised: arbitrary S with all four projections 3-AP-free ==")
    bad = 0
    trials = 0
    for _ in range(4000):
        n = rng.randint(4, 30)
        cells = [(x, y) for x in range(n) for y in range(n)]
        rng.shuffle(cells)
        S = set()
        for c in cells[: 400]:
            T = S | {c}
            if four_projections_3apfree(T):
                S = T
        trials += 1
        if not is_feasible(n, S, cross_check=(len(S) <= 60)):
            bad += 1
            print("   COUNTEREXAMPLE:", n, sorted(S))
    print(f"  {trials} greedy-maximal 4-projection sets, VIOLATIONS = {bad}")


if __name__ == "__main__":
    main()
