"""Can S' after a large a*-matching still have R' > n^{3/4}?"""
from __future__ import annotations

import random

from q4 import FourDir, verify
from lemma3_search import overlap_stats, sigma, in_grid


def place_matching(st, n, a, rng, limit=None):
    """Place as many sigma_a pairs as possible."""
    cands = []
    seen = set()
    for x in range(n):
        for y in range(n):
            if x + y == a:
                continue
            sx, sy = a - y, a - x
            if not in_grid(n, sx, sy) or (sx, sy) == (x, y):
                continue
            key = tuple(sorted(((x, y), (sx, sy))))
            if key in seen:
                continue
            seen.add(key)
            cands.append(key)
    rng.shuffle(cands)
    placed = 0
    for p, q in cands:
        if limit is not None and placed >= limit:
            break
        ks = st.can_add(*p)
        if ks is None:
            continue
        rec1 = st.push(*p, ks)
        ks2 = st.can_add(*q)
        if ks2 is None:
            st.pop(rec1)
            continue
        st.push(*q, ks2)
        placed += 1
    return placed


def rest_max_r(n, pts, a):
    pts = {tuple(p) for p in pts}
    star = {p for p in pts if sigma(a, *p) in pts and sigma(a, *p) != p}
    rest = pts - star
    from collections import defaultdict

    dia = defaultdict(list)
    ua = {x + y for x, y in rest}
    for x, y in rest:
        dia[x - y].append(x + y)
    r = defaultdict(set)
    for d, A in dia.items():
        A = sorted(A)
        for i, u in enumerate(A):
            for v in A[i + 1 :]:
                mid = (u + v) // 2
                if mid not in ua:
                    r[mid].add(d)
    return max((len(s) for s in r.values()), default=0), len(rest), len(star)


def main():
    rng = random.Random(0)
    print(f"{'n':>4} {'a':>4} {'c':>4} {'pairs_a':>7} {'pairs_c':>7} {'R\'':>4} {'|S|':>4} {'|S*|':>5} {'th':>6} {'beat':>5}", flush=True)
    best = None
    for n in (32, 48, 81, 128):
        thresh = n ** 0.75
        for trial in range(40):
            a = n - 1
            # second centre: another empty anti, not a
            c = rng.randrange(0, 2 * n - 1)
            if c == a:
                continue
            st = FourDir(n)
            pa = place_matching(st, n, a, rng)
            pc = place_matching(st, n, c, rng)
            pts = set(st.pts)
            if not pts:
                continue
            assert verify(n, pts)
            stt = overlap_stats(n, pts)
            a_used = stt["a_star"]
            Rp, nrest, nstar = rest_max_r(n, pts, a_used)
            beat = Rp > thresh
            if beat or (best is None) or Rp > best[0]:
                rec = (Rp, n, a, c, pa, pc, stt["|S|"], nstar, nrest, round(thresh, 1), beat)
                if best is None or Rp > best[0]:
                    best = rec
                if beat:
                    print("BEAT", rec, flush=True)
        print(
            f"{n:4d} best R' so far {best}",
            flush=True,
        )
    print("BEST", best, flush=True)


if __name__ == "__main__":
    main()
