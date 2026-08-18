"""Upper-bound experiments for Q4 (sidecar). Does not import iso6.

1. Portrait: supports, rectangle density, per-line occupancies, killed anti-diagonals.
2. Product sanity: full A×B is never Q4-feasible once some diagonal has 2 points;
   Q4-repair of a product has size <= 2n-1 (lemma 1).
3. Dense-rectangle search: maximise |S| inside R×T with |R|,|T| large, to try
   to break candidate lemma-3 statements.
"""
from __future__ import annotations

import json
import os
import random
from collections import Counter, defaultdict

from q4 import FourDir, greedy_from, verify

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "upperbound")
EXACT_DIR = os.path.join(HERE, "out")


def supports(pts):
    pts = [tuple(p) for p in pts]
    uc = {p[0] for p in pts}
    ur = {p[1] for p in pts}
    ud = {p[0] - p[1] for p in pts}
    ua = {p[0] + p[1] for p in pts}
    n_rect = max(1, len(uc) * len(ur))
    rows = defaultdict(list)
    cols = defaultdict(list)
    dia = defaultdict(list)
    ant = defaultdict(list)
    for x, y in pts:
        rows[y].append(x)
        cols[x].append(y)
        dia[x - y].append(x + y)
        ant[x + y].append(x - y)
    m_dia = [len(v) for v in dia.values()]
    m_ant = [len(v) for v in ant.values()]
    m_row = [len(v) for v in rows.values()]
    killed_ant = set()
    for A in dia.values():
        A = sorted(A)
        for i, a in enumerate(A):
            for b in A[i + 1 :]:
                killed_ant.add((a + b) // 2)
    return {
        "|S|": len(pts),
        "|U_col|": len(uc),
        "|U_row|": len(ur),
        "|U_dia|": len(ud),
        "|U_ant|": len(ua),
        "delta": round(len(pts) / n_rect, 6),
        "max_row": max(m_row) if m_row else 0,
        "max_col": max(len(v) for v in cols.values()) if cols else 0,
        "max_dia": max(m_dia) if m_dia else 0,
        "max_ant": max(m_ant) if m_ant else 0,
        "n_dia_ge2": sum(1 for m in m_dia if m >= 2),
        "n_ant_ge2": sum(1 for m in m_ant if m >= 2),
        "|K_ant|": len(killed_ant),
        "K_meets_U": len(killed_ant & ua),
    }


def portrait_exact():
    rows = []
    for n in range(1, 11):
        path = os.path.join(EXACT_DIR, f"exact_n{n}.json")
        if not os.path.isfile(path):
            continue
        rec = json.load(open(path, encoding="utf-8"))
        pts = [tuple(p) for p in rec["set"]]
        assert verify(n, pts)
        s = supports(pts)
        s.update(n=n, exact=rec["exact"], source="exact")
        rows.append(s)
    return rows


def portrait_construct():
    path = os.path.join(EXACT_DIR, "construct_table.json")
    if not os.path.isfile(path):
        return []
    rows = []
    for rec in json.load(open(path, encoding="utf-8")):
        pts = [tuple(p) for p in rec["set"]]
        n = rec["n"]
        assert verify(n, pts)
        s = supports(pts)
        s.update(n=n, family=rec["family"], source="construct")
        rows.append(s)
    return rows


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


def product_sanity(ns, rng):
    """Lemma 1: any Q4-feasible subset of a product with a 2-point diagonal
    is impossible for the FULL product; repaired subset <= 2n-1."""
    out = []
    for n in ns:
        B = base3_no_two(n)
        if len(B) < 2:
            A = list(range(min(n, 4)))
            C = list(range(min(n, 5)))
        else:
            A, C = B, B
        raw = [(x, y) for x in A for y in C]
        full_ok = verify(n, raw)
        # count diagonals with >=2 points in the raw product
        dia = Counter(x - y for x, y in raw)
        n_ge2 = sum(1 for v in dia.values() if v >= 2)
        kept = greedy_from(n, raw, rng)
        assert verify(n, kept)
        out.append(
            {
                "n": n,
                "|A|": len(A),
                "|C|": len(C),
                "raw": len(raw),
                "full_product_Q4": full_ok,
                "raw_diagonals_ge2": n_ge2,
                "repaired": len(kept),
                "2n-1": 2 * n - 1,
                "repaired_le_2n-1": len(kept) <= 2 * n - 1,
            }
        )
    return out


def random_subset(n, k, rng):
    xs = list(range(n))
    rng.shuffle(xs)
    return sorted(xs[:k])


def dense_rectangle_search(n, r_size, t_size, rng, restarts=80, force_frac=0.0):
    """Maximise a Q4-feasible subset of a random R×T rectangle.

    force_frac: try to keep at least that fraction of the rectangle (rejection
    among greedy outputs — we still report the largest feasible subset found).
    """
    best = set()
    best_R, best_T = None, None
    for _ in range(restarts):
        R = random_subset(n, min(r_size, n), rng)
        T = random_subset(n, min(t_size, n), rng)
        universe = [(x, y) for x in R for y in T]
        kept = greedy_from(n, universe, rng)
        if len(kept) > len(best):
            best, best_R, best_T = kept, R, T
    assert verify(n, best)
    port = supports(best)
    port["n"] = n
    port["|R|"] = len(best_R) if best_R else 0
    port["|T|"] = len(best_T) if best_T else 0
    port["rect"] = (len(best_R) * len(best_T)) if best_R else 0
    port["restarts"] = restarts
    port["force_frac"] = force_frac
    return port, [list(p) for p in sorted(best)]


def dense_from_ap_free_rectangle(n, rng, restarts=60):
    """B3 rectangle: 3-AP-free × 3-AP-free, then Q4-greedy. Density starts at 1."""
    from construct import three_ap_free_greedy

    B = three_ap_free_greedy(n, rng)
    universe = [(x, y) for x in B for y in B]
    best = set()
    for _ in range(restarts):
        kept = greedy_from(n, universe, rng)
        if len(kept) > len(best):
            best = kept
    assert verify(n, best)
    port = supports(best)
    port["n"] = n
    port["|B|"] = len(B)
    port["raw"] = len(universe)
    port["family"] = "3AP_rect_repair"
    return port


def search_high_density(n, rng, restarts=40):
    """Among random-order greedy Q4 sets on the full grid, keep those with
    largest δ (most product-like). Not a size maximiser — a density maximiser."""
    from q4 import greedy

    best_d, best_port, best_pts = -1, None, None
    for _ in range(restarts):
        pts = greedy(n, rng)
        port = supports(pts)
        if port["delta"] > best_d:
            best_d, best_port, best_pts = port["delta"], port, pts
    best_port.update(n=n, family="greedy_max_delta")
    return best_port, [list(p) for p in sorted(best_pts)]


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(20260816)

    print("=== portrait: exact ===", flush=True)
    exact = portrait_exact()
    for s in exact:
        print(
            f"  n={s['n']:2d} |S|={s['|S|']:3d}  Uc,Ur,Ud,Ua="
            f"{s['|U_col|'], s['|U_row|'], s['|U_dia|'], s['|U_ant|']}  "
            f"δ={s['delta']:.4f}  max_dia={s['max_dia']}  K={s['|K_ant|']}  "
            f"K∩U={s['K_meets_U']}",
            flush=True,
        )
    json.dump(exact, open(os.path.join(OUT, "portrait_exact.json"), "w"), indent=2)

    print("=== portrait: construct (summary max |S|/n per family) ===", flush=True)
    cons = portrait_construct()
    json.dump(cons, open(os.path.join(OUT, "portrait_construct.json"), "w"), indent=2)
    print(f"  {len(cons)} rows", flush=True)

    print("=== product sanity (lemma 1) ===", flush=True)
    san = product_sanity((9, 16, 27, 32, 81), rng)
    for s in san:
        print(
            f"  n={s['n']:3d} raw={s['raw']:5d} full_Q4={s['full_product_Q4']}  "
            f"diag>=2: {s['raw_diagonals_ge2']:4d}  repaired={s['repaired']:4d}  "
            f"<=2n-1:{s['repaired_le_2n-1']}",
            flush=True,
        )
    json.dump(san, open(os.path.join(OUT, "product_sanity.json"), "w"), indent=2)

    print("=== 3-AP rectangle repair ===", flush=True)
    ap_rows = []
    for n in (16, 27, 32, 48, 64, 81):
        rec = dense_from_ap_free_rectangle(n, rng)
        ap_rows.append(rec)
        print(
            f"  n={n:3d} |B|={rec['|B|']:3d} raw={rec['raw']:5d} "
            f"kept={rec['|S|']:4d} /n={rec['|S|']/n:.3f} δ={rec['delta']:.4f}",
            flush=True,
        )
    json.dump(ap_rows, open(os.path.join(OUT, "ap_rect_repair.json"), "w"), indent=2)

    print("=== dense random rectangles ===", flush=True)
    dense_rows = []
    configs = [
        (16, 8, 8, 120),
        (24, 12, 12, 80),
        (32, 12, 12, 60),
        (32, 16, 16, 60),
        (48, 16, 16, 40),
        (48, 24, 24, 40),
        (64, 20, 20, 30),
        (64, 32, 32, 30),
        (81, 27, 27, 20),
    ]
    for n, rs, ts, restarts in configs:
        port, pts = dense_rectangle_search(n, rs, ts, rng, restarts=restarts)
        dense_rows.append(port)
        print(
            f"  n={n:3d} |R|×|T|={rs}×{ts}  kept={port['|S|']:4d}  "
            f"/n={port['|S|']/n:.3f}  δ={port['delta']:.4f}  "
            f"max_dia={port['max_dia']}",
            flush=True,
        )
        json.dump(
            {"portrait": port, "set": pts},
            open(os.path.join(OUT, f"dense_n{n}_r{rs}_t{ts}.json"), "w"),
        )
    json.dump(dense_rows, open(os.path.join(OUT, "dense_rectangles.json"), "w"), indent=2)

    print("=== greedy max-δ ===", flush=True)
    g_rows = []
    for n in (16, 32, 48, 64):
        port, _ = search_high_density(n, rng, restarts=40)
        g_rows.append(port)
        print(
            f"  n={n:3d} |S|={port['|S|']:4d} /n={port['|S|']/n:.3f} "
            f"δ={port['delta']:.4f} Uc={port['|U_col|']}",
            flush=True,
        )
    json.dump(g_rows, open(os.path.join(OUT, "greedy_max_delta.json"), "w"), indent=2)
    print("wrote out/upperbound/", flush=True)


if __name__ == "__main__":
    main()
