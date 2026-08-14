#!/usr/bin/env python3
"""n=64 keepbl matching tournament.

Same universe family as S/S2 (half of official S0 180-twins + blacklist the
other twin) but the matching is NOT lex/west-all. Stock LNS on the 91 basin
is closed (F104/F105). Screen many matchings by capacity, then maximize_core
the best cap>=113 cores.

Does import official S0 (unsealed, orchestrator route).
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from typing import Dict, List, Optional, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from data.baselines.official_raw import SOL_64  # noqa: E402
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.search.lns import lns_run  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from w3_new_families_v1 import dual, maximize_core  # noqa: E402

Point = Tuple[int, int]
N = 64
TARGET = 113
EXP = os.path.join(RUN, "EXPERIMENTS", "W3_n64_matching")
CAND = os.path.join(RUN, "CANDIDATES")
os.makedirs(EXP, exist_ok=True)
os.makedirs(CAND, exist_ok=True)


def rot180(p: Point) -> Point:
    return (N - 1 - p[0], N - 1 - p[1])


def ring(p: Point) -> int:
    return min(p[0], p[1], N - 1 - p[0], N - 1 - p[1])


def s0_pairs() -> Tuple[List[Tuple[Point, Point]], List[Point]]:
    s0 = set((int(x), int(y)) for x, y in SOL_64)
    pairs: List[Tuple[Point, Point]] = []
    unpaired: List[Point] = []
    seen: Set[Point] = set()
    for p in sorted(s0):
        if p in seen:
            continue
        q = rot180(p)
        if q == p:
            unpaired.append(p)
            seen.add(p)
            continue
        if q in s0:
            a, b = (p, q) if p <= q else (q, p)
            pairs.append((a, b))
            seen.add(a)
            seen.add(b)
        else:
            unpaired.append(p)
            seen.add(p)
    return pairs, unpaired


def apply_matching(
    pairs: Sequence[Tuple[Point, Point]],
    unpaired: Sequence[Point],
    bits: Sequence[int],
) -> Tuple[List[Point], Set[Point]]:
    keep: List[Point] = list(unpaired)
    bl: Set[Point] = set()
    for (a, b), bit in zip(pairs, bits):
        if bit:
            keep.append(b)
            bl.add(a)
        else:
            keep.append(a)
            bl.add(b)
    # also forbid geometric twins of unpaired (keepbl discipline)
    for p in unpaired:
        q = rot180(p)
        if q != p:
            bl.add(q)
    return sorted(keep), bl


def measure(keep: Sequence[Point], bl: Set[Point]) -> dict:
    st = IncrementalIsoscelesFreeSet(N)
    for p in keep:
        if not st.add_point(p):
            return {"core": len(keep), "free": -1, "cap": -1, "illegal_core": True}
    free = [
        (x, y)
        for x in range(N)
        for y in range(N)
        if (x, y) not in st.points and (x, y) not in bl and st.can_add((x, y))[0]
    ]
    return {"core": len(st.points), "free": len(free), "cap": len(st.points) + len(free), "illegal_core": False}


def greedy_max_cap(pairs, unpaired, rng: random.Random) -> List[int]:
    bits = [0] * len(pairs)
    order = list(range(len(pairs)))
    rng.shuffle(order)
    decided = set()
    for i in order:
        best_bit, best_cap = 0, -1
        for bit in (0, 1):
            bits[i] = bit
            trial = list(bits)
            keep, bl = apply_matching(pairs, unpaired, trial)
            # undecided pairs: temporarily keep lex-a (bit 0) so core stays legal
            m = measure(keep, bl)
            if m["cap"] > best_cap:
                best_cap, best_bit = m["cap"], bit
        bits[i] = best_bit
        decided.add(i)
    return bits


def screen_matchings(pairs, unpaired, rng: random.Random) -> List[dict]:
    n_pairs = len(pairs)
    recipes: List[Tuple[str, List[int]]] = []
    recipes.append(("lex_a", [0] * n_pairs))
    recipes.append(("lex_b", [1] * n_pairs))
    recipes.append(("boundary", [0 if ring(a) <= ring(b) else 1 for a, b in pairs]))
    recipes.append(("interior", [0 if ring(a) >= ring(b) else 1 for a, b in pairs]))
    recipes.append(("west_x", [0 if a[0] <= b[0] else 1 for a, b in pairs]))
    recipes.append(("south_y", [0 if a[1] <= b[1] else 1 for a, b in pairs]))
    recipes.append(("greedy_cap", greedy_max_cap(pairs, unpaired, rng)))
    for k in (4, 8, 12, 16, 20, 24):
        for t in range(8):
            bits = [0] * n_pairs
            flips = rng.sample(range(n_pairs), k=min(k, n_pairs))
            for i in flips:
                bits[i] = 1
            recipes.append((f"flip{k}_t{t}", bits))
    for t in range(16):
        recipes.append((f"rand_t{t}", [rng.randrange(2) for _ in range(n_pairs)]))

    rows = []
    seen_hash = set()
    for name, bits in recipes:
        keep, bl = apply_matching(pairs, unpaired, bits)
        kh = sha256_of_points(keep)
        if kh in seen_hash:
            continue
        seen_hash.add(kh)
        m = measure(keep, bl)
        row = {"name": name, "keep_hash": kh, **m, "n_bits": sum(bits)}
        rows.append(row)
        print(json.dumps(row), flush=True)
        with open(os.path.join(EXP, f"match_{kh[:12]}.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "name": name,
                    "bits": bits,
                    "keep": [list(p) for p in keep],
                    "bl": [list(p) for p in sorted(bl)],
                    **m,
                    "keep_hash": kh,
                },
                f,
            )
            f.write("\n")
    rows.sort(key=lambda r: (r["cap"], r["free"]), reverse=True)
    return rows


def dump(path: str, obj: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    rng = random.Random(64)
    pairs, unpaired = s0_pairs()
    print(json.dumps({"n_pairs": len(pairs), "n_unpaired": len(unpaired), "s0": len(SOL_64)}), flush=True)

    t0 = time.time()
    screen = screen_matchings(pairs, unpaired, rng)
    dump(os.path.join(EXP, "screen.json"), {"schema": "n64_matching_screen_v1", "rows": screen, "wall_s": time.time() - t0})
    viable = [r for r in screen if r["cap"] >= TARGET and not r.get("illegal_core")]
    print(json.dumps({"n_screen": len(screen), "n_viable": len(viable), "best_cap": screen[0]["cap"] if screen else 0}), flush=True)

    # reload bits for top viable (diverse: skip near-duplicate caps if same free)
    top = viable[:6] if viable else screen[:3]
    max_rows = []
    best_pts: Optional[List[Point]] = None
    best_sz = -1
    best_name = None
    workers = 8
    cheap_s = float(os.environ.get("MATCH_CHEAP_S", "45"))
    for i, row in enumerate(top):
        path = os.path.join(EXP, f"match_{row['keep_hash'][:12]}.json")
        with open(path, encoding="utf-8") as f:
            spec = json.load(f)
        keep = [tuple(p) for p in spec["keep"]]
        bl = {tuple(p) for p in spec["bl"]}
        print(json.dumps({"maximize": row["name"], "cap": row["cap"], "cheap_s": cheap_s}), flush=True)
        res = maximize_core(
            N, keep, cheap_s, workers, seed=64000 + i, target=TARGET, blacklist=bl, keep_points=True, round_s=20.0
        )
        out = {k: v for k, v in res.items() if k != "points"}
        out["plan"] = row["name"]
        out["keep_hash"] = row["keep_hash"]
        max_rows.append(out)
        print(json.dumps(out), flush=True)
        sz = int(res.get("best_legal_size") or 0)
        if res.get("points") and sz > best_sz:
            best_sz = sz
            best_pts = [tuple(p) for p in res["points"]]
            best_name = row["name"]
            dump(
                os.path.join(EXP, "best.json"),
                {"points": res["points"], **out, "from": "cheap_max"},
            )
            d = res.get("dual") or dual(best_pts, N)
            if d.get("oracle") and d.get("indep") and d.get("size", 0) >= TARGET:
                dump(os.path.join(CAND, f"n64_k{d['size']}_matching_{d['hash'][:12]}.json"), {"points": res["points"], **d, "plan": row["name"]})
                dump(os.path.join(EXP, "summary.json"), {"schema": "n64_matching_v1", "screen": screen[:20], "max_rows": max_rows, "best": best_sz, "any_plus": True})
                print(json.dumps({"PROMOTE": True, **d}), flush=True)
                return

    esc_s = float(os.environ.get("MATCH_ESC_S", "360"))
    if best_pts and best_sz < TARGET and best_name:
        # re-maximize the winning matching with longer budget
        path = None
        for row in top:
            if row["name"] == best_name:
                path = os.path.join(EXP, f"match_{row['keep_hash'][:12]}.json")
                break
        if path:
            with open(path, encoding="utf-8") as f:
                spec = json.load(f)
            keep = [tuple(p) for p in spec["keep"]]
            bl = {tuple(p) for p in spec["bl"]}
            print(json.dumps({"escalate": best_name, "start": best_sz, "esc_s": esc_s}), flush=True)
            res = maximize_core(
                N, keep, esc_s, workers, seed=64999, target=TARGET, blacklist=bl, keep_points=True, round_s=40.0
            )
            out = {k: v for k, v in res.items() if k != "points"}
            out["plan"] = f"{best_name}_esc"
            max_rows.append(out)
            print(json.dumps(out), flush=True)
            sz = int(res.get("best_legal_size") or 0)
            if res.get("points") and sz >= best_sz:
                best_sz = sz
                best_pts = [tuple(p) for p in res["points"]]
                dump(os.path.join(EXP, "best.json"), {"points": res["points"], **out, "from": "esc"})
                d = res.get("dual") or dual(best_pts, N)
                if d.get("oracle") and d.get("indep") and d.get("size", 0) >= TARGET:
                    dump(os.path.join(CAND, f"n64_k{d['size']}_matching_{d['hash'][:12]}.json"), {"points": res["points"], **d, "plan": out["plan"]})

    lns_s = float(os.environ.get("MATCH_LNS_S", "180"))
    if best_pts and best_sz < TARGET and lns_s > 0:
        print(json.dumps({"lns": True, "start": best_sz, "from": best_name}), flush=True)
        pts, meta = lns_run(N, list(best_pts), lns_s, seed=65001, destroy_frac_range=(0.12, 0.40))
        d = dual(pts, N)
        lns_row = {"plan": "lns_from_best_matching", **{k: v for k, v in meta.items() if k != "improvements"}, **d}
        max_rows.append(lns_row)
        print(json.dumps(lns_row), flush=True)
        if d["oracle"] and d["indep"] and d["size"] >= best_sz:
            best_sz = d["size"]
            best_pts = pts
            dump(os.path.join(EXP, "best.json"), {"points": [list(p) for p in pts], **d, "from": "lns", "lns": meta})
            if d["size"] >= TARGET:
                dump(os.path.join(CAND, f"n64_k{d['size']}_matching_{d['hash'][:12]}.json"), {"points": [list(p) for p in pts], **d})

    dump(
        os.path.join(EXP, "summary.json"),
        {
            "schema": "n64_matching_v1",
            "n_pairs": len(pairs),
            "n_unpaired": len(unpaired),
            "n_screen": len(screen),
            "n_viable": len(viable),
            "best_cap_screen": screen[0]["cap"] if screen else 0,
            "max_rows": max_rows,
            "best": best_sz,
            "best_name": best_name,
            "any_plus": bool(best_sz >= TARGET),
            "wall_s": time.time() - t0,
        },
    )
    print(json.dumps({"done": True, "best": best_sz, "any_plus": best_sz >= TARGET, "name": best_name}), flush=True)


if __name__ == "__main__":
    main()
