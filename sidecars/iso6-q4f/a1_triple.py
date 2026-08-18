"""Try to realise ρ, t_max, μ all > n^{3/4} on S* (the remaining campaign gap)."""
from __future__ import annotations

import random
from collections import defaultdict

from q4 import FourDir, verify
from lemma3_search import overlap_stats, sigma
from a1_construct import behrend_like
from a1_longrow import greedy_row_apfree


def fibre_pts(n, a, d, deltas):
    pts = []
    for v in list(deltas) + [-x for x in deltas]:
        alpha = a + v
        if (alpha + d) % 2:
            return None
        x = (alpha + d) // 2
        y = (alpha - d) // 2
        if not (0 <= x < n and 0 <= y < n):
            return None
        pts.append((x, y))
    return pts


def try_place(st, pts):
    recs = []
    for p in pts:
        if p in st.pts:
            continue
        ks = st.can_add(*p)
        if ks is None:
            for rec in reversed(recs):
                st.pop(rec)
            return False
        recs.append(st.push(*p, ks))
    return True


def star_maxes(n, pts):
    stt = overlap_stats(n, pts)
    a = stt["a_star"]
    star = set()
    if a is not None:
        for p in pts:
            q = sigma(a, *p)
            if q in pts and q != p:
                star.add(p)
    row = defaultdict(int)
    dia = defaultdict(int)
    ant = defaultdict(int)
    for x, y in star:
        row[y] += 1
        dia[x - y] += 1
        ant[x + y] += 1
    stt["rho"] = max(row.values()) if row else 0
    stt["lam"] = max(dia.values()) if dia else 0
    stt["mu"] = max(ant.values()) if ant else 0
    stt["t_max"] = stt["lam"] // 2
    stt["min3"] = min(stt["rho"], stt["t_max"], stt["mu"])
    return stt


def main():
    rng = random.Random(4)
    for n in (81, 128, 243):
        a = n - 1
        thresh = n ** 0.75
        best = None
        # heavy diagonal first with as many same-parity deltas as possible
        for trial in range(6):
            st = FourDir(n)
            raw = behrend_like(n // 2)
            par = 0 if a % 2 else 1
            deltas = []
            for x in raw:
                if x % 2 != par:
                    continue
                trial_d = deltas + [x]
                vals = [-d for d in trial_d] + trial_d
                A = [a + v for v in vals]
                if min(A) < 0 or max(A) > 2 * n - 2:
                    continue
                ss = set(A)
                ok = True
                for i, u in enumerate(A):
                    for v in A[i + 1 :]:
                        if (u + v) % 2 == 0 and (u + v) // 2 in ss:
                            ok = False
                            break
                    if not ok:
                        break
                if ok:
                    deltas.append(x)
            placed_heavy = False
            for d in range(1 - n, n):
                pts = fibre_pts(n, a, d, deltas)
                if pts and try_place(st, pts):
                    placed_heavy = True
                    break
            # long row
            ys = list(range(n))
            rng.shuffle(ys)
            for y in ys[:40]:
                for par_x in (0, 1):
                    xs = greedy_row_apfree(n, y, par_x)
                    for x in xs:
                        if x + y == a:
                            continue
                        sx, sy = a - y, a - x
                        if not (0 <= sx < n and 0 <= sy < n):
                            continue
                        for p in ((x, y), (sx, sy)):
                            if p in st.pts:
                                continue
                            ks = st.can_add(*p)
                            if ks is None:
                                break
                            st.push(*p, ks)
            # fill
            cells = [(x, y) for x in range(n) for y in range(n)]
            rng.shuffle(cells)
            for x, y in cells:
                ks = st.can_add(x, y)
                if ks is not None:
                    st.add(x, y, ks)
            pts = set(st.pts)
            assert verify(n, pts)
            stt = star_maxes(n, pts)
            stt["heavy_ok"] = placed_heavy
            stt["n_delta"] = len(deltas)
            if best is None or stt["min3"] > best["min3"]:
                best = stt
        print(
            f"n={n:3d} thresh={thresh:.1f} min3={best['min3']:2d} "
            f"ρ={best['rho']:2d} t={best['t_max']:2d} μ={best['mu']:2d} "
            f"|S*|={best['|S_star|']:4d} r={best['max_r']:3d} "
            f"deltas={best['n_delta']} heavy={best['heavy_ok']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
