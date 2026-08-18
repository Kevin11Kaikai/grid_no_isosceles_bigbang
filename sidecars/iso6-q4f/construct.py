"""Algebraic construction battery against Q4.

Each family: generate a candidate point set, repair to Q4-feasibility, verify,
record |S|/n. Does not import iso6.
"""
from __future__ import annotations

import json
import os
import random
from math import gcd

from q4 import greedy_from, verify

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def base3_no_two(N):
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


def three_ap_free_greedy(n, rng):
    xs = list(range(n))
    rng.shuffle(xs)
    B = []
    Bs = set()
    for x in xs:
        ok = True
        for a in B:
            if (x + a) % 2 == 0 and (x + a) // 2 in Bs:
                ok = False
                break
            if (2 * x - a) in Bs:
                ok = False
                break
        if ok:
            B.append(x)
            Bs.add(x)
    return sorted(B)


def sidon_greedy(n, rng):
    """All pairwise sums a+b (a<=b) distinct."""
    xs = list(range(n))
    rng.shuffle(xs)
    B = []
    sums = set()
    for x in xs:
        new = []
        ok = True
        for a in B:
            s = a + x
            if s in sums:
                ok = False
                break
            new.append(s)
        if not ok:
            continue
        dbl = x + x
        if dbl in sums:
            continue
        for s in new:
            sums.add(s)
        sums.add(dbl)
        B.append(x)
    return sorted(B)


def product(A, B):
    return [(x, y) for x in A for y in B]


def repair_random(n, pts, rng, rounds=40):
    best = set()
    for _ in range(rounds):
        s = greedy_from(n, pts, rng)
        if len(s) > len(best):
            best = s
    return best


def _violation_scores(n, pts):
    P = list(pts)
    occ_col = {p[0] for p in P}
    occ_row = {p[1] for p in P}
    occ_dia = {p[0] - p[1] for p in P}
    occ_ant = {p[0] + p[1] for p in P}
    score = {p: 0 for p in P}
    for i in range(len(P)):
        x1, y1 = P[i]
        for j in range(i + 1, len(P)):
            x2, y2 = P[j]
            bad = False
            if y1 == y2 and (x1 + x2) % 2 == 0 and (x1 + x2) // 2 in occ_col:
                bad = True
            elif x1 == x2 and (y1 + y2) % 2 == 0 and (y1 + y2) // 2 in occ_row:
                bad = True
            elif x1 - y1 == x2 - y2 and ((x1 + y1) + (x2 + y2)) // 2 in occ_ant:
                bad = True
            elif x1 + y1 == x2 + y2 and ((x1 - y1) + (x2 - y2)) // 2 in occ_dia:
                bad = True
            if bad:
                score[P[i]] += 1
                score[P[j]] += 1
    return score


def repair_delete_worst(n, pts):
    S = set(pts)
    while S and not verify(n, S):
        scores = _violation_scores(n, S)
        victim = max(S, key=lambda p: (scores[p], p))
        if scores[victim] == 0:
            break
        S.remove(victim)
    return S if verify(n, S) else set()


def repair_best(n, pts, rng, rounds=40):
    a = repair_random(n, pts, rng, rounds=rounds)
    if len(pts) > 400:
        return a
    b = repair_delete_worst(n, pts)
    return a if len(a) >= len(b) else b


def rec_ok(n, name, pts, extra=None):
    pts = set(map(tuple, pts))
    ok = verify(n, pts)
    ratio = (len(pts) / n) if n else 0.0
    # n^{1.1} < 2n for all n < 1024, so that line is not a kill at these sizes.
    # Practical flags at this scale: beat 2n, or beat 2.5n (clear n^{1+c} smell).
    out = {
        "family": name,
        "n": n,
        "size": len(pts),
        "size_over_n": round(ratio, 4),
        "n_to_1_1": round(n ** 1.1, 2) if n else None,
        "above_2n": bool(ok and len(pts) > 2 * n),
        "above_2_5n": bool(ok and len(pts) >= 2.5 * n),
        "verify": ok,
    }
    if extra:
        out.update(extra)
    out["set"] = [list(p) for p in sorted(pts)]
    assert ok, (name, n, "verify failed")
    return out


# --- families ---

def fam_bxb_thin(n, rng):
    B = base3_no_two(n)
    raw = product(B, B)
    kept = repair_best(n, raw, rng, rounds=60)
    return rec_ok(
        n,
        "Bxb_thin_base3",
        kept,
        extra={"raw": len(raw), "|B|": len(B), "raw_over_n": round(len(raw) / n, 4)},
    )


def fam_axb(n, rng):
    A = base3_no_two(n)
    B = sidon_greedy(n, rng)
    if len(B) < 2:
        B = three_ap_free_greedy(n, rng)
    raw = product(A, B)
    kept = repair_best(n, raw, rng, rounds=40)
    return rec_ok(
        n,
        "AxB_base3_x_sidon",
        kept,
        extra={"raw": len(raw), "|A|": len(A), "|B|": len(B)},
    )


def fam_ap_x_ap(n, rng):
    A = three_ap_free_greedy(n, random.Random(rng.random()))
    B = three_ap_free_greedy(n, random.Random(rng.random()))
    raw = product(A, B)
    kept = repair_best(n, raw, rng, rounds=40)
    return rec_ok(n, "AxB_greedy3AP", kept, extra={"raw": len(raw), "|A|": len(A), "|B|": len(B)})


def fam_thick_function(n, rng):
    """Column support C 3-AP-free; each occupied row places k=2 points from C."""
    C = three_ap_free_greedy(n, rng)
    R = three_ap_free_greedy(n, random.Random(rng.randint(0, 10**9)))
    raw = []
    for y in R:
        take = list(C)
        rng.shuffle(take)
        for x in take[:2]:
            raw.append((x, y))
    kept = repair_best(n, raw, rng, rounds=40)
    return rec_ok(n, "thick_fn_2_per_row", kept, extra={"raw": len(raw), "|C|": len(C), "|R|": len(R)})


def fam_curves(n, rng):
    """Unions of modular curves (size O(n) each). k copies -> hope n^{1+c}."""
    raw = set()
    for a in range(1, min(n, 12)):
        for x in range(n):
            raw.add((x, (a * x * x) % n))  # parabolas
            raw.add((x, (a * x) % n))  # lines
            if gcd(x, n) == 1:
                inv = pow(x, -1, n)
                raw.add((x, (a * inv) % n))  # hyperbolas
            raw.add((x, pow(2, x, n) if n > 1 else 0))
    kept = repair_best(n, raw, rng, rounds=30)
    return rec_ok(n, "curve_union", kept, extra={"raw": len(raw)})


def fam_random_bxb_sample(n, rng, exponent=1.2):
    B = base3_no_two(n)
    universe = product(B, B)
    target = max(1, int(n ** exponent))
    if len(universe) <= target:
        sample = universe
    else:
        sample = rng.sample(universe, target)
    kept = repair_best(n, sample, rng, rounds=50)
    return rec_ok(
        n,
        f"sample_Bxb_n^{exponent}",
        kept,
        extra={"sampled": len(sample), "universe": len(universe), "target": target},
    )


def fam_random_grid_sample(n, rng, exponent=1.2):
    target = min(n * n, max(1, int(n ** exponent)))
    cells = [(x, y) for x in range(n) for y in range(n)]
    sample = rng.sample(cells, target)
    kept = repair_best(n, sample, rng, rounds=50)
    return rec_ok(n, f"sample_grid_n^{exponent}", kept, extra={"sampled": len(sample)})


def fam_one_row_r3(n, rng):
    B = three_ap_free_greedy(n, rng)
    pts = [(x, 0) for x in B]
    assert verify(n, pts)
    return rec_ok(n, "single_row_3AP_free", pts, extra={"|B|": len(B)})


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(20260816)
    ns = (9, 16, 27, 32, 48, 64, 81)
    rows = []
    families = [
        fam_bxb_thin,
        fam_axb,
        fam_ap_x_ap,
        fam_thick_function,
        fam_curves,
        fam_random_bxb_sample,
        fam_random_grid_sample,
        fam_one_row_r3,
    ]
    for n in ns:
        print(f"=== n={n} ===", flush=True)
        for fam in families:
            rec = fam(n, rng)
            rows.append(rec)
            if rec["above_2_5n"]:
                mark = ">2.5n"
            elif rec["above_2n"]:
                mark = ">2n"
            else:
                mark = "<=2n"
            print(
                f"  {rec['family']:<28}  |S|={rec['size']:5d}  /n={rec['size_over_n']:.3f}  "
                f"{mark}  verify={rec['verify']}",
                flush=True,
            )
    with open(os.path.join(OUT, "construct_table.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    # larger Behrend-like N for thinning only (the original B3 scale)
    extra = []
    for n in (81, 243):
        print(f"=== extra Bxb thin n={n} ===", flush=True)
        rec = fam_bxb_thin(n, rng)
        extra.append(rec)
        print(
            f"  {rec['family']:<28}  |S|={rec['size']:5d}  /n={rec['size_over_n']:.3f}  "
            f"raw={rec['raw']}",
            flush=True,
        )
    with open(os.path.join(OUT, "construct_bxb_extra.json"), "w", encoding="utf-8") as f:
        json.dump(extra, f, indent=2)
    print("wrote out/construct_table.json")


if __name__ == "__main__":
    main()
