"""Overnight run: peeling kill-switch, lemmas, power-attempt identities."""
from __future__ import annotations

import json
import random
from math import log
from pathlib import Path

from lemmas import (
    lemma_one_row_free,
    lemma_three_full_rows_not_free,
    lemma_two_full_rows_not_free,
    lemma_zi_iff_j1,
    three_rows_analytic_witness,
)
from peel import build_Am
from power import cs_row_bound, random_set, try_n32_argument
from sq import is_sq_free

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)


def dump(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    print("wrote", p)


def run_peel():
    rows = []
    for m in range(3, 11):
        rec = build_Am(m)
        pts = rec["set"]
        rec["sq_free"] = is_sq_free(pts)
        rec["unique"] = rec["|S|"] == rec["n_words"]
        pub = {k: v for k, v in rec.items() if k != "set"}
        rows.append(pub)
        print(
            f"peel m={m:2d} |S|={pub['|S|']:5d} n={pub['n']:5d} "
            f"|S|/n={pub['|S|/n']:.4f} exp={pub['exponent']:.4f} "
            f"sq_free={pub['sq_free']} unique={pub['unique']}",
            flush=True,
        )
        assert pub["sq_free"], f"peeling m={m} is not sq-free"
        assert pub["unique"], f"phi not injective at m={m}"
    dump("peel.json", rows)
    return rows


def run_lemmas():
    zi = lemma_zi_iff_j1(8)
    print("Z[i] iff J1", zi, flush=True)
    assert zi["ok"]
    one = lemma_one_row_free()
    print("one row/col free", one["ok"], flush=True)
    assert one["ok"]
    two = lemma_two_full_rows_not_free()
    print("two full rows dirty", two["ok"], two["rows"][0]["witness"], flush=True)
    assert two["ok"]
    three = lemma_three_full_rows_not_free(16)
    print(
        "three full rows n=16 tested",
        three["triples_tested"],
        "sq_free",
        three["n_sq_free"],
        "ok_all_dirty",
        three["ok"],
        flush=True,
    )
    # analytic witness for a close triple
    w = three_rows_analytic_witness(16, 0, 1, 2)
    print("analytic 0,1,2", w, flush=True)
    far = three_rows_analytic_witness(16, 0, 1, 15)
    print("analytic 0,1,15", far, flush=True)
    out = {
        "zi": zi,
        "one_row": one,
        "two_rows": two,
        "three_rows": three,
        "witness_close": w,
        "witness_far": far,
    }
    dump("lemmas.json", out)
    return out


def run_power(peel_rows):
    rng = random.Random(0)
    reports = []

    def consider(name, n, pts):
        pts = list(map(tuple, pts))
        d = {
            "name": name,
            "n": n,
            "sq_free": is_sq_free(pts),
            **try_n32_argument(pts, n),
            **cs_row_bound(pts, n),
        }
        reports.append(d)
        print(
            f"{name:20s} n={n:4d} m={d['m']:5d} G/P={d['G/P']:.3f} "
            f"G<=m n? {d['G <= m*n']} I={d['I']} m<=n^1.5? {d['m <= n**1.5']}",
            flush=True,
        )
        return d

    # peeling sets (true sq-free superlinear-in-theory)
    for m in (6, 8, 9):
        rec = build_Am(m)
        consider(f"peel_m{m}", rec["n"], rec["set"])

    # one full row: sq-free, m=n
    for n in (16, 32, 64):
        consider(f"full_row_{n}", n, [(x, 0) for x in range(n)])

    # random dense (many corners)
    for n, m in ((16, 40), (32, 80), (24, 60)):
        consider(f"random_{n}_{m}", n, random_set(n, m, rng))

    # greedy-ish linear graph
    for n in (16, 32, 64):
        consider(f"diag_{n}", n, [(x, x % n) for x in range(n)])

    dump("power_counts.json", reports)

    # Diagnose the O(n^{3/2}) hole
    hole = {
        "attempt": "Q_SQ = O(n^{3/2}) via G ≥ c P and G ≤ m n ⇒ m = O(n)",
        "note": "G ≤ m n would actually give O(n), which Phase 0 falsifies. "
        "The measured G/P is the fraction of pair-completions that stay in-grid.",
        "observation": [],
    }
    for d in reports:
        hole["observation"].append(
            {
                "name": d["name"],
                "G/P": d["G/P"],
                "G <= m*n": d["G <= m*n"],
                "sq_free": d["sq_free"],
                "m": d["m"],
                "n": d["n"],
            }
        )
    dump("power_hole.json", hole)
    return reports, hole


if __name__ == "__main__":
    print("=== Phase 0 peel ===", flush=True)
    peel_rows = run_peel()
    print("=== Phase 1 lemmas ===", flush=True)
    run_lemmas()
    print("=== Phase 2 power counts ===", flush=True)
    run_power(peel_rows)
    print("done", flush=True)
