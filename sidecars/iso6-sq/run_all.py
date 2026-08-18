"""Negative controls + construction battery for Q_SQ. No iso6 import."""
from __future__ import annotations

import json
import random
from math import log
from pathlib import Path

from construct import (
    behrend_like_rows,
    bxB,
    classical_corner_free,
    convex_cubes,
    convex_squares,
    fourfold_freq,
    fourfold_greedy,
    graph_cubic,
    graph_linear,
    graph_parabola_embed,
    graph_quadratic,
    greedy_2_per_rowcol,
    greedy_3ap_free,
    greedy_sidon,
    greedy_sq_free,
    hyperbola,
    j1_embed_fourfold,
    product_set,
    quadratic_residues_graph,
    repair_record,
)
from iso import is_iso_free
from sq import is_sq_free

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)


def dump(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return p


def slopes(rows):
    """Log-log slopes of |S| vs n for consecutive rows with same family."""
    out = []
    for a, b in zip(rows, rows[1:]):
        if a["n"] == b["n"] or a["|S|"] <= 0 or b["|S|"] <= 0:
            continue
        s = log(b["|S|"] / a["|S|"]) / log(b["n"] / a["n"])
        out.append({"n0": a["n"], "n1": b["n"], "slope": s})
    return out


def run_sanity_iso_implies_sq():
    rng = random.Random(1)
    # a small iso-free greedy
    n = 16
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    S = []
    dists = {}
    for p in cells:
        ok, dp, newd = True, set(), {}
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
    assert is_iso_free(S)
    assert is_sq_free(S)
    return {"n": n, "|S|": len(S), "iso_free": True, "sq_free": True}


def run_neg_controls(seed=20260816):
    rows = []
    for n in (27, 81, 243):
        d, _ = bxB(n)
        rows.append(d)
        print(
            f"BxB n={n:4d} |S|={d['|S|']:5d} sq_free={d['sq_free']} corners={d.get('n_corners')}",
            flush=True,
        )
        assert d["sq_free"] is False, "BxB must have square corners"
    rng = random.Random(seed)
    for n in (16, 32, 48, 64):
        d, _ = fourfold_greedy(n, rng)
        rows.append(d)
        print(
            f"fourfold n={n:4d} |S|={d['|S|']:5d} sq_free={d['sq_free']} corners={d.get('n_corners')}",
            flush=True,
        )
        d, _ = fourfold_freq(n, rng)
        rows.append(d)
        print(
            f"fourfold_freq n={n:4d} |S|={d['|S|']:5d} sq_free={d['sq_free']} corners={d.get('n_corners')}",
            flush=True,
        )
    d, _ = j1_embed_fourfold(16)
    rows.append(d)
    print(
        f"J1_embed n={d['n']:4d} |S|={d['|S|']:5d} sq_free={d['sq_free']} corners={d.get('n_corners')} 3ap={d.get('3ap')}",
        flush=True,
    )
    dump("neg_controls.json", rows)
    return rows


def run_battery(seed=7):
    rng = random.Random(seed)
    rows = []

    def add(d):
        rows.append(d)
        nc = d.get("n_corners")
        print(
            f"{d['family']:28s} n={d['n']:4d} |S|={d['|S|']:5d} "
            f"|S|/n={d['|S|/n']:.3f} sq_free={d['sq_free']} corners={nc}",
            flush=True,
        )

    # 2. function graphs
    for n in (32, 64, 128):
        for fn in (
            lambda n: graph_linear(n, 1, 0),
            lambda n: graph_linear(n, 2, 3),
            lambda n: graph_quadratic(n, 1, 0, 0),
            lambda n: graph_cubic(n),
            graph_parabola_embed,
        ):
            d, pts = fn(n)
            add(d)
            if not d["sq_free"]:
                rd, _ = repair_record(d["family"], n, pts)
                add(rd)

    # 3. at most 2 per row/col, and greedy sq-free baseline
    for n in (16, 24, 32, 48):
        d, _ = greedy_2_per_rowcol(n, rng, also_sq=False)
        add(d)
        d, _ = greedy_2_per_rowcol(n, rng, also_sq=True)
        add(d)
        d, _ = greedy_sq_free(n, rng)
        add(d)

    # 4. Sidon / convex / 3-AP products
    for n in (32, 64, 128):
        A = greedy_sidon(n)
        d, pts = product_set(n, A, A, "sidon_x_sidon")
        add(d)
        if not d["sq_free"]:
            rd, _ = repair_record(d["family"], n, pts)
            add(rd)
        Sq = convex_squares(n)
        d, pts = product_set(n, Sq, Sq, "squares_x_squares")
        add(d)
        if not d["sq_free"]:
            rd, _ = repair_record(d["family"], n, pts)
            add(rd)
        Cu = convex_cubes(n)
        d, pts = product_set(n, Cu, Cu, "cubes_x_cubes")
        add(d)
        if not d["sq_free"]:
            rd, _ = repair_record(d["family"], n, pts)
            add(rd)
        T = greedy_3ap_free(range(n), rng)
        d, pts = product_set(n, T, T, "r3_x_r3")
        add(d)
        if not d["sq_free"]:
            rd, _ = repair_record(d["family"], n, pts, mode="participants")
            add(rd)

    # 5. classical-corner-free then repair; full 3-AP rows
    for n in (27, 81):
        d, pts = classical_corner_free(n)
        add(d)
        if not d["sq_free"]:
            rd, _ = repair_record(d["family"], n, pts, mode="participants")
            add(rd)
        d, pts = behrend_like_rows(n)
        add(d)
        if not d["sq_free"]:
            rd, _ = repair_record(d["family"], n, pts, mode="participants")
            add(rd)

    # 6. modular
    for n in (32, 64, 128):
        d, pts = hyperbola(n, k=1)
        add(d)
        if not d["sq_free"]:
            rd, _ = repair_record(d["family"], n, pts)
            add(rd)
        d, pts = quadratic_residues_graph(n)
        add(d)
        if not d["sq_free"]:
            rd, _ = repair_record(d["family"], n, pts)
            add(rd)

    dump("battery.json", rows)
    # per-family slopes on sq-free rows only
    by = {}
    for r in rows:
        if r["sq_free"]:
            by.setdefault(r["family"], []).append(r)
    slope_tab = {fam: slopes(sorted(v, key=lambda r: r["n"])) for fam, v in by.items()}
    dump("slopes_sq_free.json", slope_tab)
    return rows, slope_tab


if __name__ == "__main__":
    print("=== sanity: iso-free => sq-free ===")
    print(run_sanity_iso_implies_sq())
    print("=== negative controls ===")
    run_neg_controls()
    print("=== construction battery ===")
    run_battery()
    print("done")
