"""Lemma 3 overlap search: r(a), S*, S', forced large-r and mixed-K.

Does not import iso6. Frozen checker in q4.py.
"""
from __future__ import annotations

import json
import os
import random
from collections import defaultdict

from q4 import FourDir, greedy_from, verify

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "lemma3")
EXACT = os.path.join(HERE, "out")


def sigma(a, x, y):
    return (a - y, a - x)


def in_grid(n, x, y):
    return 0 <= x < n and 0 <= y < n


def overlap_stats(n, pts):
    pts = {tuple(p) for p in pts}
    dia = defaultdict(list)
    ua = {x + y for x, y in pts}
    for x, y in pts:
        dia[x - y].append(x + y)
    r = defaultdict(set)
    for d, A in dia.items():
        A = sorted(A)
        for i, a in enumerate(A):
            for b in A[i + 1 :]:
                r[(a + b) // 2].add(d)
    r_kill = {a: s for a, s in r.items() if a not in ua}
    max_r = max((len(s) for s in r_kill.values()), default=0)
    a_star = None
    if r_kill:
        a_star = max(r_kill, key=lambda a: len(r_kill[a]))
    S_star = set()
    if a_star is not None:
        for x, y in pts:
            sx, sy = sigma(a_star, x, y)
            if (sx, sy) in pts and (sx, sy) != (x, y):
                S_star.add((x, y))
    S_rest = pts - S_star
    return {
        "n": n,
        "|S|": len(pts),
        "size_over_n": round(len(pts) / n, 4) if n else 0,
        "max_r": max_r,
        "sqrt_n": round(n ** 0.5, 3),
        "case": "B" if max_r <= n ** 0.5 else "A",
        "|K|": len(r_kill),
        "a_star": a_star,
        "r_star": len(r_kill[a_star]) if a_star is not None else 0,
        "|S_star|": len(S_star),
        "|S_rest|": len(S_rest),
        "r_hist": {int(a): len(s) for a, s in sorted(r_kill.items())},
    }


def partner_in_grid(n, a, x, y):
    sx, sy = sigma(a, x, y)
    return in_grid(n, sx, sy) and (sx, sy) != (x, y)


def greedy_forced_pairs(n, a, rng):
    """Seed with reflection pairs across empty anti-diagonal a, then fill."""
    candidates = []
    seen = set()
    for x in range(n):
        for y in range(n):
            if x + y == a:
                continue
            if not partner_in_grid(n, a, x, y):
                continue
            sx, sy = sigma(a, x, y)
            key = tuple(sorted(((x, y), (sx, sy))))
            if key in seen:
                continue
            seen.add(key)
            candidates.append(key)
    rng.shuffle(candidates)
    st = FourDir(n)
    for p, q in candidates:
        ks = st.can_add(*p)
        if ks is None:
            continue
        rec1 = st.push(*p, ks)
        ks2 = st.can_add(*q)
        if ks2 is None:
            st.pop(rec1)
            continue
        st.push(*q, ks2)
    cells = [(x, y) for x in range(n) for y in range(n)]
    rng.shuffle(cells)
    for x, y in cells:
        ks = st.can_add(x, y)
        if ks is not None:
            st.add(x, y, ks)
    pts = set(st.pts)
    assert verify(n, pts)
    return pts


def greedy_mixed(n, rng, target_k_ratio=0.3):
    """Random Q4 greedy, keep the restart with largest |K| * max_r (mixed)."""
    from q4 import greedy

    best, best_score = set(), -1
    stats = None
    for _ in range(40):
        pts = greedy(n, rng)
        stt = overlap_stats(n, pts)
        score = stt["|K|"] * (stt["max_r"] + 1)
        if score > best_score:
            best, best_score, stats = pts, score, stt
    return best, stats


def maximise_forced(n, restarts, rng):
    best_pts, best_st = set(), None
    lo, hi = 0, 2 * n - 2
    for _ in range(restarts):
        a = rng.randint(lo, hi)
        pts = greedy_forced_pairs(n, a, rng)
        stt = overlap_stats(n, pts)
        if best_st is None or stt["|S|"] > best_st["|S|"]:
            best_pts, best_st = pts, stt
        elif stt["|S|"] == best_st["|S|"] and stt["max_r"] > best_st["max_r"]:
            best_pts, best_st = pts, stt
    best_st["family"] = "forced_pairs"
    return best_pts, best_st


def portrait_exact():
    rows = []
    for n in range(1, 11):
        path = os.path.join(EXACT, f"exact_n{n}.json")
        if not os.path.isfile(path):
            continue
        rec = json.load(open(path, encoding="utf-8"))
        pts = [tuple(p) for p in rec["set"]]
        assert verify(n, pts)
        stt = overlap_stats(n, pts)
        stt["exact"] = rec["exact"]
        stt["family"] = "exact"
        rows.append(stt)
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(20260816)

    print("=== exact portraits (Case A/B) ===", flush=True)
    exact = portrait_exact()
    for s in exact:
        print(
            f"  n={s['n']:2d} |S|={s['|S|']:3d}  max_r={s['max_r']:2d}  "
            f"√n={s['sqrt_n']:5.2f}  case={s['case']}  |K|={s['|K|']:2d}  "
            f"|S*|={s['|S_star|']:3d} |S'|={s['|S_rest|']:3d}",
            flush=True,
        )
    json.dump(exact, open(os.path.join(OUT, "portrait_exact.json"), "w"), indent=2)

    print("=== forced large-r (seed reflection pairs) ===", flush=True)
    forced_rows = []
    for n in (16, 24, 32, 48, 64, 81, 128, 243):
        restarts = 80 if n <= 64 else 40 if n <= 128 else 16
        pts, stt = maximise_forced(n, restarts, rng)
        forced_rows.append(stt)
        flag = "SUPERLINEAR" if stt["|S|"] >= n ** 1.3 else ""
        print(
            f"  n={n:3d} |S|={stt['|S|']:5d} /n={stt['size_over_n']:.3f}  "
            f"max_r={stt['max_r']:3d}  case={stt['case']}  "
            f"|S*|={stt['|S_star|']:4d} |S'|={stt['|S_rest|']:4d}  {flag}",
            flush=True,
        )
        json.dump(
            {"stats": stt, "set": [list(p) for p in sorted(pts)]},
            open(os.path.join(OUT, f"forced_n{n}.json"), "w"),
        )
    json.dump(forced_rows, open(os.path.join(OUT, "forced_table.json"), "w"), indent=2)

    print("=== mixed |K| * max_r greedy ===", flush=True)
    mixed_rows = []
    for n in (16, 32, 48, 64, 81, 128):
        pts, stt = greedy_mixed(n, rng)
        stt["family"] = "mixed_greedy"
        mixed_rows.append(stt)
        print(
            f"  n={n:3d} |S|={stt['|S|']:5d} /n={stt['size_over_n']:.3f}  "
            f"max_r={stt['max_r']:3d} |K|={stt['|K|']:3d}  case={stt['case']}  "
            f"|S*|={stt['|S_star|']:4d} |S'|={stt['|S_rest|']:4d}",
            flush=True,
        )
    json.dump(mixed_rows, open(os.path.join(OUT, "mixed_table.json"), "w"), indent=2)
    print("wrote out/lemma3/", flush=True)


if __name__ == "__main__":
    main()
