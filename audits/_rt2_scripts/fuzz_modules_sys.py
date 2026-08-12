import sys, os, json

sys.path.insert(0, r"D:\Others\grid_no_isosceles_bigbang")

from src.search.sa_exact_repair import sa_exact_repair_run
from src.search.lns_multiregion import lns_multiregion_run
from src.search.symmetry_guided import symmetric_multistart
from src.search.greedy import greedy_once
from src.verification.oracle_verifier import is_legal_pivot_method, is_legal_bruteforce_triples
from src.verification_independent.independent_verifier import verify_independent

results = []


def check_all(name, pts, n, meta=None):
    pts = [tuple(p) for p in pts]
    ok1, w1 = is_legal_pivot_method(pts, n)
    if len(pts) <= 80:
        ok2, w2 = is_legal_bruteforce_triples(pts, n)
    else:
        ok2, w2 = None, None
    ok3, w3 = verify_independent([list(p) for p in pts], n)
    status = "PASS" if ok1 and ok3 and (ok2 is None or ok2) else "FAIL"
    results.append({"name": name, "n": n, "size": len(pts), "pivot": ok1, "bruteforce": ok2,
                     "independent": ok3, "status": status})
    print(f"{name:20s} n={n:3d} size={len(pts):4d} pivot={ok1} bruteforce={ok2} independent={ok3} -> {status}")
    if status == "FAIL":
        print("  WITNESS pivot:", w1)
        print("  WITNESS bruteforce:", w2)
        print("  WITNESS independent:", w3)
    return status == "PASS"


for n in [8, 10, 12, 16]:
    for seed in [1, 2, 3]:
        init_pts, _ = greedy_once(n, seed=seed, order="random")
        best, meta = sa_exact_repair_run(
            n, init_pts, time_budget_s=3.0, seed=seed,
            region_size_cap=n * n, milp_time_limit_s=1.0, oracle_check_every=25,
        )
        check_all(f"sa_exact_repair(seed={seed})", best, n, meta)

        best2, meta2 = lns_multiregion_run(
            n, init_pts, time_budget_s=3.0, seed=seed, k_regions=2,
            size_cap_each=n * n, milp_time_limit_s=1.0, oracle_check_every=25,
        )
        check_all(f"lns_multiregion(seed={seed})", best2, n, meta2)

    best3, meta3 = symmetric_multistart(n, time_budget_s=3.0, seed=1)
    check_all("symmetry_guided_multistart", best3, n, meta3)

# Degenerate tiny-n edge cases
for n in [1, 2, 3]:
    init_pts = []
    best, meta = sa_exact_repair_run(n, init_pts, time_budget_s=1.0, seed=1, region_size_cap=n * n)
    check_all(f"sa_exact_repair(tiny n={n})", best, n, meta)
    best2, meta2 = lns_multiregion_run(n, init_pts, time_budget_s=1.0, seed=1, k_regions=2, size_cap_each=n * n)
    check_all(f"lns_multiregion(tiny n={n})", best2, n, meta2)
    best3, meta3 = symmetric_multistart(n, time_budget_s=1.0, seed=1)
    check_all(f"symmetry_guided(tiny n={n})", best3, n, meta3)

n_fail = sum(1 for r in results if r["status"] == "FAIL")
print(f"\n=== SUMMARY: {len(results)} runs, {n_fail} FAILED ===")
print("ALL PASS" if n_fail == 0 else "SOME FAILED -- SEE ABOVE")
