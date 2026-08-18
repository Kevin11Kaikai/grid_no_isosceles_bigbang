"""Try to place many long 3-AP-free diagonals (the remaining heavy-line GAP)."""
from __future__ import annotations

import random

from q4 import FourDir, verify


def greedy_apfree_on_diagonal(n, d, rng):
    """Anti-values on diagonal d that fit in the grid, greedy 3-AP-free."""
    cands = []
    for x in range(n):
        y = x - d
        if 0 <= y < n:
            cands.append(x + y)
    rng.shuffle(cands)
    A, As = [], set()
    for a in cands:
        ok = True
        for b in A:
            if (a + b) % 2 == 0 and (a + b) // 2 in As:
                ok = False
                break
            if (2 * a - b) in As:
                ok = False
                break
        if ok:
            A.append(a)
            As.add(a)
    return A


def place_diagonals(n, diags, rng):
    st = FourDir(n)
    placed_d = 0
    for d in diags:
        A = greedy_apfree_on_diagonal(n, d, rng)
        recs = []
        ok_any = False
        for a in A:
            x = (a + d) // 2
            y = (a - d) // 2
            if (a + d) % 2 or not (0 <= x < n and 0 <= y < n):
                continue
            ks = st.can_add(x, y)
            if ks is None:
                continue
            recs.append(st.push(x, y, ks))
            ok_any = True
        if ok_any:
            placed_d += 1
        # keep whatever fitted; do not roll back a partial diagonal
    return st, placed_d


def portrait(n, pts):
    from collections import Counter

    dia = Counter(x - y for x, y in pts)
    ant = Counter(x + y for x, y in pts)
    th = n ** 0.75
    th2 = n ** 0.875
    return {
        "|S|": len(pts),
        "max_dia": max(dia.values()) if dia else 0,
        "max_ant": max(ant.values()) if ant else 0,
        "|H|": sum(1 for c in dia.values() if c > th),
        "|J|": sum(1 for c in ant.values() if c > th),
        "|H78|": sum(1 for c in dia.values() if c > th2),
        "th": round(th, 1),
        "th2": round(th2, 1),
    }


def main():
    rng = random.Random(0)
    print("n |S| md ma |H| |J| H78 th th2", flush=True)
    best = None
    for n in (32, 81, 128, 243):
        diags = list(range(1 - n, n))
        local = None
        for trial in range(20):
            rng.shuffle(diags)
            st, _ = place_diagonals(n, diags, rng)
            # fill leftovers
            cells = [(x, y) for x in range(n) for y in range(n)]
            rng.shuffle(cells)
            for x, y in cells:
                ks = st.can_add(x, y)
                if ks is not None:
                    st.push(x, y, ks)
            assert verify(n, st.pts)
            p = portrait(n, st.pts)
            p["n"] = n
            if local is None or (p["|H|"], p["|S|"]) > (local["|H|"], local["|S|"]):
                local = p
            if p["|H|"] > p["th"] and p["|J|"] > p["th"]:
                print("BOTH_HEAVY", p, flush=True)
        print(
            f"{n} {local['|S|']} {local['max_dia']} {local['max_ant']} "
            f"{local['|H|']} {local['|J|']} {local['|H78|']} "
            f"{local['th']} {local['th2']}",
            flush=True,
        )
        if best is None or local["|H|"] > best["|H|"]:
            best = local
    print("BEST_H", best, flush=True)


if __name__ == "__main__":
    main()
