"""Falsification: (d, α) products D × (a* ± Δ) against Q4.

Does not import iso6. Frozen checker in q4.py.

Families:
  1. Disjoint differences (D-D) ∩ (A-A) = {0}: Q4-feasible by lemma if
     D and A are 3-AP-free (constraints 1–2 vacuous, 3–4 from AP-free).
  2. Scaled: Δ lives in an interval of length m, D is 3-AP-free in mZ.
  3. FourDir-greedy fibres: allow difference overlap if the checker accepts.

Kill line: |S|/n clearly growing, or |S| >= 2.5 n with verify True.
"""
from __future__ import annotations

import json
import os
import random
from collections import defaultdict

from q4 import FourDir, verify
from lemma3_search import overlap_stats

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "da_product")


def three_ap_free_greedy(values, rng=None):
    vals = list(values)
    if rng is not None:
        rng.shuffle(vals)
    B, Bs = [], set()
    for x in vals:
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


def symmetric_apfree_deltas(limit, parity, rng=None):
    """Positive δ of given parity such that {±δ} is 3-AP-free."""
    cand = list(range(parity if parity else 2, limit + 1, 2))
    if rng is not None:
        rng.shuffle(cand)
    s = []
    for x in cand:
        trial = s + [x]
        vals = [-d for d in trial] + trial
        ss = set(vals)
        ok = True
        for i, a in enumerate(vals):
            for b in vals[i + 1 :]:
                if (a + b) % 2 == 0 and (a + b) // 2 in ss:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            s.append(x)
    return sorted(s)


def powers(base, limit):
    out, p = [], 1
    while p <= limit:
        out.append(p)
        p *= base
    return out


def difference_set(A):
    A = list(A)
    diffs = {0}
    for i, a in enumerate(A):
        for b in A[i + 1 :]:
            diffs.add(b - a)
            diffs.add(a - b)
    return diffs


def fibre_point(n, a_star, d, alpha):
    if (alpha + d) % 2:
        return None
    x = (alpha + d) // 2
    y = (alpha - d) // 2
    if 0 <= x < n and 0 <= y < n:
        return (x, y)
    return None


def product_points(n, a_star, D, deltas):
    pts = []
    for d in D:
        for delta in deltas:
            for alpha in (a_star + delta, a_star - delta):
                p = fibre_point(n, a_star, d, alpha)
                if p is not None:
                    pts.append(p)
    return pts


def q4_place(n, pts):
    st = FourDir(n)
    placed = []
    for p in pts:
        if p in st.pts:
            continue
        ks = st.can_add(*p)
        if ks is None:
            return None
        st.add(*p, ks)
        placed.append(p)
    return placed


def greedy_place(n, pts, rng):
    st = FourDir(n)
    order = list(pts)
    rng.shuffle(order)
    for p in order:
        if p in st.pts:
            continue
        ks = st.can_add(*p)
        if ks is not None:
            st.add(*p, ks)
    return list(st.pts)


def disjoint_diff_D(n, A, rng):
    """Greedy 3-AP-free D whose differences miss A-A except 0."""
    forbidden = difference_set(A) - {0}
    cand = list(range(1 - n, n))
    rng.shuffle(cand)
    D, Ds = [], set()
    diffsD = {0}
    for d in cand:
        if any((d - x) in forbidden or (x - d) in forbidden for x in D):
            continue
        ok = True
        for x in D:
            if (d + x) % 2 == 0 and (d + x) // 2 in Ds:
                ok = False
                break
            if (2 * d - x) in Ds:
                ok = False
                break
        if not ok:
            continue
        D.append(d)
        Ds.add(d)
        for x in D[:-1]:
            diffsD.add(d - x)
            diffsD.add(x - d)
    return sorted(D)


def scaled_family(n, a_star, m, rng):
    """Δ ⊂ [1, m], D = m * (3-AP-free in compressed range)."""
    par = 0 if a_star % 2 else 1
    deltas = symmetric_apfree_deltas(max(2, m // 2), par, rng)
    compressed = three_ap_free_greedy(range((2 * n) // m + 3), rng)
    D = []
    for k in compressed:
        for sign in (1, -1, 0):
            d = sign * m * k
            if 1 - n <= d <= n - 1 and d not in D:
                D.append(d)
    D = three_ap_free_greedy(D, rng)
    return D, deltas


def portrait(n, pts, family, extra=None):
    rec = overlap_stats(n, pts)
    rec["family"] = family
    rec["verify"] = True
    if extra:
        rec.update(extra)
    return rec


def run_n(n, rng):
    rows = []
    a_star = n - 1
    par = 0 if a_star % 2 else 1

    # --- disjoint-difference products ---
    for name, deltas in (
        ("geom2", [x for x in powers(2, n // 2) if x % 2 == par]),
        ("geom3", [x for x in powers(3, n // 2) if x % 2 == par]),
        ("sym_greedy", symmetric_apfree_deltas(n // 2, par, rng)),
    ):
        deltas = [d for d in deltas if d > 0 and a_star + d <= 2 * n - 2 and a_star - d >= 0]
        if len(deltas) < 1:
            continue
        # use prefixes of various lengths
        for t in sorted(set([1, 2, 3, min(4, len(deltas)), len(deltas)])):
            if t < 1 or t > len(deltas):
                continue
            Del = deltas[:t]
            A = [a_star + d for d in Del] + [a_star - d for d in Del]
            D = disjoint_diff_D(n, A, rng)
            if len(D) < 1:
                continue
            pts = product_points(n, a_star, D, Del)
            if not pts:
                continue
            placed = q4_place(n, pts)
            if placed is None:
                rows.append(
                    {
                        "n": n,
                        "family": f"disjoint_{name}_t{t}",
                        "status": "q4_reject",
                        "|D|": len(D),
                        "|Δ|": t,
                    }
                )
                continue
            assert verify(n, placed)
            rows.append(
                portrait(
                    n,
                    placed,
                    f"disjoint_{name}_t{t}",
                    {
                        "|D|": len(D),
                        "|Δ|": t,
                        "diff_disjoint": True,
                        "status": "ok",
                    },
                )
            )

    # --- scaled m ---
    for m in (3, 4, 5, 8, 16, max(3, int(n ** 0.5))):
        if m >= n:
            continue
        D, Del = scaled_family(n, a_star, m, rng)
        if not D or not Del:
            continue
        for t in (1, 2, min(3, len(Del)), len(Del)):
            if t > len(Del) or t < 1:
                continue
            pts = product_points(n, a_star, D, Del[:t])
            if not pts:
                continue
            placed = q4_place(n, pts)
            tag = f"scaled_m{m}_t{t}"
            if placed is None:
                # repair: greedy subset
                placed = greedy_place(n, pts, rng)
                if not placed:
                    continue
                assert verify(n, placed)
                rows.append(
                    portrait(
                        n,
                        placed,
                        tag + "_repair",
                        {"|D|": len(D), "|Δ|": t, "m": m, "status": "repaired"},
                    )
                )
                continue
            assert verify(n, placed)
            rows.append(
                portrait(
                    n,
                    placed,
                    tag,
                    {"|D|": len(D), "|Δ|": t, "m": m, "status": "ok"},
                )
            )

    # --- FourDir greedy biclique: grow D then Δ ---
    Del = symmetric_apfree_deltas(n // 2, par, rng)
    for t in (1, 2, 3, 4, min(6, len(Del))):
        if t > len(Del) or t < 1:
            continue
        st = FourDir(n)
        nd = 0
        for d in range(1 - n, n):
            pts = []
            good = True
            for delta in Del[:t]:
                for alpha in (a_star + delta, a_star - delta):
                    p = fibre_point(n, a_star, d, alpha)
                    if p is None:
                        good = False
                        break
                    pts.append(p)
                if not good:
                    break
            if not good:
                continue
            recs = []
            ok = True
            for p in pts:
                if p in st.pts:
                    continue
                ks = st.can_add(*p)
                if ks is None:
                    ok = False
                    break
                recs.append(st.push(*p, ks))
            if not ok:
                for rec in reversed(recs):
                    st.pop(rec)
                continue
            nd += 1
        pts = list(st.pts)
        if not pts:
            continue
        assert verify(n, pts)
        rows.append(
            portrait(
                n,
                pts,
                f"fd_biclique_t{t}",
                {"|D|": nd, "|Δ|": t, "status": "ok"},
            )
        )

    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(0)
    all_rows = []
    best = None
    print(
        f"{'n':>4} {'family':<28} {'|S|':>5} {'|S|/n':>7} {'max_r':>6} {'status':<10}",
        flush=True,
    )
    for n in (16, 24, 32, 48, 64, 81, 128, 243):
        rows = run_n(n, rng)
        all_rows.extend(rows)
        ok = [r for r in rows if r.get("|S|")]
        if not ok:
            print(f"{n:4d} (no placed set)", flush=True)
            continue
        top = max(ok, key=lambda r: r["|S|"])
        print(
            f"{n:4d} {top['family']:<28} {top['|S|']:5d} {top['size_over_n']:7.3f} "
            f"{top.get('max_r', 0):6d} {top.get('status', ''):<10}",
            flush=True,
        )
        if best is None or top["size_over_n"] > best["size_over_n"]:
            best = top
        # kill line
        if top["size_over_n"] >= 2.5:
            print("Q4 DIES: |S|/n >= 2.5", top, flush=True)

    json.dump(all_rows, open(os.path.join(OUT, "table.json"), "w"), indent=2)
    summary = []
    by_n = defaultdict(list)
    for r in all_rows:
        if r.get("|S|"):
            by_n[r["n"]].append(r)
    for n, rs in sorted(by_n.items()):
        top = max(rs, key=lambda r: r["|S|"])
        summary.append(
            {
                "n": n,
                "best_|S|": top["|S|"],
                "best_|S|/n": top["size_over_n"],
                "best_family": top["family"],
                "max_r": top.get("max_r"),
            }
        )
    json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=2)
    print("best overall", best["family"] if best else None, best, flush=True)


if __name__ == "__main__":
    main()
