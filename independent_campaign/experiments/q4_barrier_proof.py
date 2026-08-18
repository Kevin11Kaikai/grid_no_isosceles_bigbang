"""VERIFICATION OF THE Q4 BARRIER (averaging over shifts).

THEOREM (root).  Q4(n) >= r_3(n)^2 * r_3(2n)^2 / (64 n^2) = n^2 exp(-c sqrt(log n)).
Hence Q4(n) = n^{2-o(1)} and NO upper bound proved from Q4 alone can reach n^{2-eps}.

Two ingredients, both checked here:

(L) SUFFICIENCY.  If A,B,W,Z are 3-AP-free then
        S = {(x,y) in [n]^2 : x in A, y in B, x+y in W, x-y in Z}
    satisfies all four Q4 constraints.

(M) AVERAGING.  Summing |S(a,b,w,z)| over the shift box
        a,b in (-n,n),  w,z in (-2n,2n)
    gives exactly n^2 * t^2 * t'^2 where t=|T|, t'=|T'|, because for each of the n^2
    points (x,y) the number of admissible a is exactly t, of b exactly t, of w exactly t',
    of z exactly t'.  The shift box has (2n-1)^2 (4n-1)^2 < 64 n^4 elements, so some shift
    tuple achieves |S| >= t^2 t'^2 / (64 n^2).

Exact integer arithmetic only.
"""
import numpy as np
from four_direction_linekill import verify as q4_verify_independent
from q4_falsify_root import base3_no_two, is_3ap_free, count_S


def brute_sum_over_shifts(n, T, Tp):
    """Directly sum |S| over the whole shift box -- checks identity (M)."""
    ra, rb, rw, rz = shift_ranges(n)
    total = 0
    best = 0
    for a in ra:
        for b in rb:
            for w in rw:
                for z in rz:
                    c, _ = count_S(n, T + a, T + b, Tp + w, Tp + z)
                    total += c
                    best = max(best, c)
    return total, best


def shift_ranges(n):
    """Exact ranges containing EVERY admissible shift.

    a = x - tau, x in [0,n), tau in T subset [0,n)          -> a in [-(n-1), n-1]
    b likewise.
    w = (x+y) - tau', x+y in [0,2n-2], tau' in [0,2n-1]     -> w in [-(2n-1), 2n-2]
    z = (x-y) - tau', x-y in [-(n-1),n-1], tau' in [0,2n-1] -> z in [-(3n-2), n-1]

    Truncating any of these breaks the identity -- an earlier version clipped z and the
    identity failed, which is why the ranges are spelled out explicitly here.
    """
    return (range(-(n - 1), n),
            range(-(n - 1), n),
            range(-(2 * n - 1), 2 * n - 1),
            range(-(3 * n - 2), n))


def sum_over_shifts_fast(n, T, Tp):
    """Same sum, computed by the per-point counting argument."""
    Ts, Tps = set(int(v) for v in T), set(int(v) for v in Tp)
    ra, rb, rw, rz = shift_ranges(n)
    total = 0
    for x in range(n):
        na = sum(1 for a in ra if (x - a) in Ts)
        for y in range(n):
            nb = sum(1 for b in rb if (y - b) in Ts)
            nw = sum(1 for w in rw if (x + y - w) in Tps)
            nz = sum(1 for z in rz if (x - y - z) in Tps)
            total += na * nb * nw * nz
    return total


def check_sufficiency(n, trials, rng):
    """Check (L): every S built this way is Q4-feasible, per the INDEPENDENT verifier."""
    T, Tp = base3_no_two(n), base3_no_two(2 * n)
    assert is_3ap_free(T) and is_3ap_free(Tp)
    tested = nonempty = bad = 0
    biggest = 0
    for _ in range(trials):
        a, b = int(rng.integers(-n, n)), int(rng.integers(-n, n))
        w, z = int(rng.integers(-2 * n, 2 * n)), int(rng.integers(-2 * n, 2 * n))
        c, ok = count_S(n, T + a, T + b, Tp + w, Tp + z)
        if c == 0:
            continue
        pts = [(int(x), int(y)) for x, y in zip(*np.nonzero(ok))]
        tested += 1
        nonempty += 1
        biggest = max(biggest, c)
        if not q4_verify_independent(n, pts):
            bad += 1
    return tested, bad, biggest


if __name__ == "__main__":
    rng = np.random.default_rng(7)

    print("=== (L) sufficiency: are these sets Q4-feasible? ===")
    for n in (9, 16, 27, 40):
        tested, bad, big = check_sufficiency(n, 300, rng)
        print(f"  n={n:3d}  nonempty sets tested={tested:4d}  Q4 VIOLATIONS={bad}  "
              f"largest={big}")

    print("\n=== (M) averaging identity: sum over all shifts ===")
    for n in (5, 6, 7, 9):
        T, Tp = base3_no_two(n), base3_no_two(2 * n)
        t, tp = len(T), len(Tp)
        pred = n * n * t * t * tp * tp
        fast = sum_over_shifts_fast(n, T, Tp)
        ra, rb, rw, rz = shift_ranges(n)
        box = len(ra) * len(rb) * len(rw) * len(rz)
        brute = best = None
        if n <= 6:
            brute, best = brute_sum_over_shifts(n, T, Tp)
        print(f"  n={n}: t={t} t'={tp}  n^2 t^2 t'^2={pred}  per-point sum={fast}  "
              f"identity holds={pred == fast}  brute={brute} "
              f"(brute matches={brute == fast if brute else 'n/a'})")
        print(f"        box={box} <= 64n^4={64*n**4}: {box <= 64*n**4}   "
              f"avg={pred/box:.3f}  guaranteed max |S| >= {pred/box:.3f}"
              + (f"   actual max over box = {best}" if best is not None else ""))

    print("\n=== asymptotic consequence ===")
    print("  With Behrend sets t = r_3(n) >= n exp(-C sqrt(log n)):")
    print("    Q4(n) >= t^2 t'^2 / (64 n^2) >= n^2 exp(-c sqrt(log n)) = n^{2-o(1)}")
    print("  => Q4 CANNOT yield C(n) = O(n^{2-eps}).  Route FALSIFIED.")
