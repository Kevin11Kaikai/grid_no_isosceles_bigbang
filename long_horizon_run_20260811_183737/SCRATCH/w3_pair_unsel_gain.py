#!/usr/bin/env python3
"""Deletion-pair GAIN over unselected cells only (exclude re-adding Rem).

F081 counted can_add(S0\\T) including T itself. For easiest covers that
'free=3' is exactly {q} ∪ T, so unselected surplus is 1 = just q; net
delete-2-add-1 cannot increase cardinality.

True r=2 +1 needs >=3 unselected addables after deleting T.
This scan measures that gain for: (a) easiest-q covers, (b) top certificate
edges, (c) sampled high-degree S0 pairs, (d) random S0 pairs.

If some T has n_unsel>=3 and cap>=165, run exact target CP-SAT.
"""
from __future__ import annotations

import gzip
import importlib.util
import itertools
import json
import os
import random
import sys
import time
from collections import Counter, defaultdict
from typing import List, Sequence, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from data.baselines.official_raw import SOL_100  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402

Point = Tuple[int, int]
EXP = os.path.join(RUN, "EXPERIMENTS", "W3_pair_unsel_gain")
os.makedirs(EXP, exist_ok=True)
AUDIT = os.path.join(ROOT, "scratch", "audit", "agent_a", "scripts", "blocker_audit.py")
COMM = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_communities_n100.json")


def load_ba():
    spec = importlib.util.spec_from_file_location("ba_ug", AUDIT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def unselected_addables(n: int, s0_set, T: Sequence[Point]) -> List[Point]:
    core = [p for p in s0_set if p not in T]
    st = IncrementalIsoscelesFreeSet(n)
    for p in core:
        if not st.add_point(p):
            return []  # shouldn't happen
    Tset = set(T)
    out = []
    for x in range(n):
        for y in range(n):
            p = (x, y)
            if p in st.points or p in Tset:
                continue
            if st.can_add(p)[0]:
                out.append(p)
    return out


def hitting_sets(edges, k):
    verts = sorted({p for e in edges for p in e})
    out = []
    for comb in itertools.combinations(verts, k):
        s = set(comb)
        if all(s & e for e in edges):
            out.append(tuple(sorted(s)))
    return out


def eval_T(n, s0_set, T, tag):
    t = tuple(sorted(T))
    uns = unselected_addables(n, s0_set, t)
    return {
        "T": [list(p) for p in t],
        "tag": tag,
        "n_unsel": len(uns),
        "unsel": [list(p) for p in uns[:12]],
        "gain": len(uns) - 2,
        "cap_if_take_all_unsel": (164 - 2) + len(uns),
    }


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    n = 100
    ba = load_ba()
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0_set = set(s0)
    maps = ba.precompute_pivot_maps(s0)
    t0 = time.time()
    rows = []
    seen = set()

    def add_row(T, tag):
        t = tuple(sorted(T))
        if t in seen or len(t) != 2:
            return
        seen.add(t)
        row = eval_T(n, s0_set, t, tag)
        rows.append(row)
        print(json.dumps({k: row[k] for k in ("tag", "T", "n_unsel", "gain")}), flush=True)

    # (a) easiest exact-2 covers
    path = os.path.join(ROOT, "scratch", "audit", "agent_a", "blocker_detail_n100.json.gz")
    with gzip.open(path, "rt", encoding="utf-8") as f:
        detail = json.load(f)
    easy = []
    for r in detail["all_qs_compact"]:
        if r.get("exact_min_hitting_set") == 2 or (
            r.get("lower_bound_min_deletions") == 2
            and r.get("upper_bound_min_deletions") == 2
        ):
            easy.append(tuple(r["q"]))
    for q in easy:
        rec = ba.analyze_q(q, s0, maps, n)
        edges = [frozenset((tuple(a), tuple(b))) for a, b in rec["blocker_edges"]]
        for cov in hitting_sets(edges, 2):
            add_row(cov, "easy_cover")

    # (b) top certificate edges
    with open(COMM, "r", encoding="utf-8") as f:
        comm = json.load(f)
    top = comm["bipartite_incidence"]["top_certificates_by_q_frequency"][:40]
    for item in top:
        e = item["certificate_edge"]
        add_row((tuple(e[0]), tuple(e[1])), "top_cert")

    # (c) high vertex frequency among top certs
    freq = Counter()
    for item in comm["bipartite_incidence"]["top_certificates_by_q_frequency"][:200]:
        a, b = item["certificate_edge"]
        freq[tuple(a)] += item["n_qs_blocked_by_this_edge"]
        freq[tuple(b)] += item["n_qs_blocked_by_this_edge"]
    topv = [p for p, _c in freq.most_common(12)]
    for a, b in itertools.combinations(topv, 2):
        add_row((a, b), "top_degree_pair")

    # (d) random S0 pairs
    rng = random.Random(7)
    for i in range(80):
        a, b = rng.sample(s0, 2)
        add_row((a, b), "random")

    rows.sort(key=lambda r: -r["n_unsel"])
    best = rows[0] if rows else None
    n_ge3 = sum(1 for r in rows if r["n_unsel"] >= 3)
    summary = {
        "schema": "w3_pair_unsel_gain_v1",
        "n_pairs": len(rows),
        "n_unsel_ge3": n_ge3,
        "max_n_unsel": best["n_unsel"] if best else 0,
        "max_gain": best["gain"] if best else None,
        "best": best,
        "by_tag_max": {},
        "top10": rows[:10],
        "wall_s": time.time() - t0,
    }
    for tag in ("easy_cover", "top_cert", "top_degree_pair", "random"):
        sub = [r for r in rows if r["tag"] == tag]
        summary["by_tag_max"][tag] = {
            "n": len(sub),
            "max_n_unsel": max((r["n_unsel"] for r in sub), default=0),
            "n_ge3": sum(1 for r in sub if r["n_unsel"] >= 3),
        }
    with open(os.path.join(EXP, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    with open(os.path.join(EXP, "all_pairs.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f)
        f.write("\n")
    print(json.dumps({k: summary[k] for k in ("n_pairs", "n_unsel_ge3", "max_n_unsel", "by_tag_max", "wall_s")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
