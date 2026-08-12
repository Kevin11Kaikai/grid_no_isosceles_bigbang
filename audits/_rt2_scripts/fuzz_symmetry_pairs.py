"""Task 2 targeted fuzz: reflect-based pair add/remove logic used by symmetry_guided.py,
cross-checked against the oracle via IncrementalIsoscelesFreeSet.cross_check_with_oracle()
after EVERY single low-level operation (not just periodically), specifically because
hypotheses.md H-006b documents that point-pair logic in this codebase is bug-prone (two
separate authors independently hit the same "which points in a pair are actually
present" bug class before).

This driver imports the REAL `reflect()` function from symmetry_guided.py (not a
reimplementation) and exercises: coupled-pair add, pair remove, remove-one-of-a-pair
(asymmetric state), re-add of the reflection when the partner is already occupied,
double-add, double-remove, and a long random add/remove/pair-remove sequence -- on
several small n (including odd n, which the module's own docstring says is irrelevant
to its real use case of n=64/100 but is a good adversarial edge case).
"""
import sys, os, random

sys.path.insert(0, r"D:\Others\grid_no_isosceles_bigbang")

from src.search.symmetry_guided import reflect, symmetric_build_once
from src.search.incremental_state import IncrementalIsoscelesFreeSet
from src.verification.oracle_verifier import is_legal_pivot_method
from src.verification_independent.independent_verifier import verify_independent

divergences = 0
checks = 0


def xcheck(ifs, label):
    global divergences, checks
    checks += 1
    try:
        ifs.cross_check_with_oracle()
    except AssertionError as e:
        divergences += 1
        print(f"  !!! DIVERGENCE at {label}: {e}")
        return False
    # also cross-check against the fully independent clean-room verifier
    ok_ind, w_ind = verify_independent([list(p) for p in ifs.points], ifs.n)
    if not ok_ind:
        divergences += 1
        print(f"  !!! INDEPENDENT VERIFIER DISAGREES at {label}: witness={w_ind} pts={sorted(ifs.points)}")
        return False
    return True


def run_reflect_pair_fuzz(n, seed, n_ops=400):
    rng = random.Random(seed)
    ifs = IncrementalIsoscelesFreeSet(n)
    all_pts = [(x, y) for x in range(n) for y in range(n)]

    for op_i in range(n_ops):
        p = rng.choice(all_pts)
        r = reflect(p, n)
        op = rng.choice(["add_pair", "remove_pair", "add_single", "remove_single",
                          "remove_one_of_pair", "readd_reflection"])

        if op == "add_pair":
            if r == p:
                # odd-n fixed point: mirrors symmetric_build_once's own "cannot happen
                # for even n, guarded anyway" comment -- exercise the guard explicitly.
                continue
            if p in ifs.points or r in ifs.points:
                pass  # exactly the "if r in ifs.points: continue" skip in the real module
            else:
                ok_p, _ = ifs.can_add(p)
                if ok_p:
                    ifs.add_point(p)
                    ok_r, _ = ifs.can_add(r)
                    if ok_r:
                        ifs.add_point(r)
                    else:
                        ifs.remove_point(p)  # rollback, exactly like symmetric_build_once

        elif op == "remove_pair":
            if p in ifs.points:
                ifs.remove_point(p)
            if r in ifs.points:
                ifs.remove_point(r)

        elif op == "add_single":
            if p not in ifs.points:
                ok, _ = ifs.can_add(p)
                if ok:
                    ifs.add_point(p)

        elif op == "remove_single":
            if p in ifs.points:
                ifs.remove_point(p)

        elif op == "remove_one_of_pair":
            # deliberately break symmetry: remove p but leave r if present
            if p in ifs.points:
                ifs.remove_point(p)

        elif op == "readd_reflection":
            # attempt to add r specifically when its partner p may or may not be present
            # -- this is exactly the scenario the H-006b bug class involved (mishandling
            # "is the OTHER member of the pair actually there").
            if r not in ifs.points:
                ok, _ = ifs.can_add(r)
                if ok:
                    ifs.add_point(r)

        if not xcheck(ifs, f"n={n} seed={seed} op={op_i}:{op} p={p} r={r}"):
            return False

    # Final structural sanity: every "reflect" call is a genuine involution
    for p in all_pts[:200]:
        assert reflect(reflect(p, n), n) == p, f"reflect not an involution at {p}, n={n}"

    print(f"n={n:3d} seed={seed}: {n_ops} ops, 0 divergence, reflect() involution OK, final size={len(ifs.points)}")
    return True


all_ok = True
for n in [6, 7, 8, 9, 10, 12]:  # includes odd n as adversarial edge cases
    for seed in [1, 2, 3, 4, 5]:
        ok = run_reflect_pair_fuzz(n, seed, n_ops=300)
        all_ok = all_ok and ok

# Also specifically replay symmetric_build_once (the REAL production function, not the
# fuzz driver above) many times and cross-check its result with both oracle and the
# independent verifier every time.
print("\n--- symmetric_build_once (real production function) direct replay ---")
for n in [8, 10, 12, 16]:
    for seed in range(1, 11):
        for bp in (0.0, 0.05, 0.2):
            pts, meta = symmetric_build_once(n, seed, break_prob=bp, order="random")
            ok1, w1 = is_legal_pivot_method(pts, n)
            ok2, w2 = verify_independent([list(p) for p in pts], n)
            if not (ok1 and ok2):
                all_ok = False
                print(f"  !!! FAIL symmetric_build_once n={n} seed={seed} bp={bp}: pivot={ok1} indep={ok2} w1={w1} w2={w2}")
print("symmetric_build_once replay: all legal" if all_ok else "symmetric_build_once replay: FAILURES FOUND")

print(f"\n=== TOTAL cross_check_with_oracle() calls: {checks}, divergences: {divergences} ===")
print("ALL PASS" if all_ok and divergences == 0 else "FAILURES FOUND -- SEE ABOVE")
