"""Measure Extra vs campaign quantities: r, μ=max_ant(S*), t_max, harmonic bound.

Does not import iso6.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

from lemma3_search import overlap_stats, sigma
from q4 import verify

HERE = os.path.dirname(os.path.abspath(__file__))


def extra_portrait(n, pts):
    pts = {tuple(p) for p in pts}
    st = overlap_stats(n, pts)
    a = st["a_star"]
    if a is None:
        return st
    star = {p for p in pts if sigma(a, *p) in pts and sigma(a, *p) != p}
    dia = defaultdict(list)
    ant = defaultdict(int)
    for x, y in star:
        dia[x - y].append(x + y)
        ant[x + y] += 1
    t_list = []
    extra = 0
    for d, A in dia.items():
        # S* points on a diagonal come in σ-pairs; t = |A|/2
        t = len(A) // 2
        t_list.append(t)
        extra += max(t - 1, 0)
    r = st["r_star"]
    mu = max(ant.values()) if ant else 0
    t_max = max(t_list) if t_list else 0
    T = sum(t_list)
    harm = (2 * n * r * mu / (r + mu)) if (r + mu) else 0
    eps = 0.25
    thresh = n ** (1 - eps)
    st.update(
        extra=extra,
        T=T,
        mu=mu,
        t_max=t_max,
        n_star=len(star),
        harmonic_bound=round(harm, 2),
        min_r_mu=min(r, mu) if r and mu else 0,
        thresh_n34=round(thresh, 2),
        caseA_campaign=r > thresh,
        both_large=r > thresh and mu > thresh,
        t_large=t_max > thresh,
        S_star_over_n=round(len(star) / n, 4) if n else 0,
    )
    return st


def load_pts(path):
    rec = json.load(open(path, encoding="utf-8"))
    return [tuple(p) for p in rec["set"]]


def main():
    rows = []
    print(
        f"{'src':<8} {'n':>4} {'r':>4} {'μ':>3} {'t':>2} {'Ex':>4} {'|S*|':>5} "
        f"{'2n min(r,μ)':>12} {'harm':>8} {'r>n^3/4':>8} {'μ>':>3} {'t>':>3}",
        flush=True,
    )
    for n in (7, 8, 16, 32, 81, 128, 243):
        if n <= 10:
            path = os.path.join(HERE, "out", f"exact_n{n}.json")
            src = "exact"
        else:
            path = os.path.join(HERE, "out", "lemma3", f"forced_n{n}.json")
            src = "forced"
        if not os.path.isfile(path):
            continue
        pts = load_pts(path)
        assert verify(n, pts)
        st = extra_portrait(n, pts)
        rows.append({"src": src, **{k: v for k, v in st.items() if k != "r_hist"}})
        print(
            f"{src:<8} {n:4d} {st['r_star']:4d} {st['mu']:3d} {st['t_max']:2d} "
            f"{st['extra']:4d} {st['|S_star|']:5d} {2*n*st['min_r_mu']:12.0f} "
            f"{st['harmonic_bound']:8.1f} {str(st['caseA_campaign']):>8} "
            f"{str(st['both_large']):>3} {str(st['t_large']):>3}",
            flush=True,
        )
    os.makedirs(os.path.join(HERE, "out", "lemma3"), exist_ok=True)
    json.dump(rows, open(os.path.join(HERE, "out", "lemma3", "extra_budget.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
