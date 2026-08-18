"""Portrait of S': max r, where it lives, partner in-grid?"""
from __future__ import annotations

import json
import os
from collections import defaultdict

from lemma3_search import overlap_stats, sigma, in_grid
from q4 import verify

HERE = os.path.dirname(os.path.abspath(__file__))


def sprime_portrait(n, pts):
    pts = {tuple(p) for p in pts}
    st = overlap_stats(n, pts)
    a = st["a_star"]
    star = {p for p in pts if sigma(a, *p) in pts and sigma(a, *p) != p}
    rest = pts - star
    dstar = {x - y for x, y in star}
    dia_rest = defaultdict(list)
    for x, y in rest:
        dia_rest[x - y].append(x + y)
    r_rest = defaultdict(set)
    ua_rest = {x + y for x, y in rest}
    for d, A in dia_rest.items():
        A = sorted(A)
        for i, u in enumerate(A):
            for v in A[i + 1 :]:
                mid = (u + v) // 2
                if mid not in ua_rest:
                    r_rest[mid].add(d)
    max_r_rest = max((len(s) for s in r_rest.values()), default=0)
    on_dstar = sum(1 for x, y in rest if (x - y) in dstar)
    off = len(rest) - on_dstar
    partner_ingrid = 0
    partner_occ_ant = ua_s = {x + y for x, y in pts}
    for x, y in rest:
        sx, sy = sigma(a, x, y)
        if in_grid(n, sx, sy):
            partner_ingrid += 1
    max_on_dia_rest = max((len(A) for A in dia_rest.values()), default=0)
    thresh = n ** 0.75
    st.update(
        max_r_rest=max_r_rest,
        S_rest_on_Dstar=on_dstar,
        S_rest_fresh=off,
        partner_ingrid=partner_ingrid,
        n_fresh_dia=sum(1 for d in dia_rest if d not in dstar),
        max_dia_rest=max_on_dia_rest,
        rest_caseB=max_r_rest <= thresh,
        thresh=round(thresh, 2),
    )
    return st


def main():
    print(
        f"{'src':<8} {'n':>4} {'|S*|':>5} {'|S|':>4} {'R\'':>4} {'md\'':>4} "
        f"{'onD*':>5} {'fresh':>5} {'B\'?':>5}",
        flush=True,
    )
    rows = []
    for n in (7, 8, 16, 32, 81, 128, 243):
        if n <= 10:
            path = os.path.join(HERE, "out", f"exact_n{n}.json")
            src = "exact"
        else:
            path = os.path.join(HERE, "out", "lemma3", f"forced_n{n}.json")
            src = "forced"
        if not os.path.isfile(path):
            continue
        rec = json.load(open(path, encoding="utf-8"))
        pts = [tuple(p) for p in rec["set"]]
        assert verify(n, pts)
        st = sprime_portrait(n, pts)
        rows.append({k: v for k, v in st.items() if k != "r_hist"})
        print(
            f"{src:<8} {n:4d} {st['|S_star|']:5d} {st['|S_rest|']:4d} "
            f"{st['max_r_rest']:4d} {st['max_dia_rest']:4d} "
            f"{st['S_rest_on_Dstar']:5d} {st['S_rest_fresh']:5d} "
            f"{str(st['rest_caseB']):>5}",
            flush=True,
        )
    json.dump(rows, open(os.path.join(HERE, "out", "lemma3", "sprime.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
