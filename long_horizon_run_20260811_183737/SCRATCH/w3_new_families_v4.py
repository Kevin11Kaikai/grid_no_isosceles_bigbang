#!/usr/bin/env python3
"""Newfam v4 — destroy+refill / exact micros OUTSIDE closed basins.

Closed (do not reopen): S0-snap, midset/forbid<=139, avoid-S0, lattice-mod3,
ring/col/diag/rowband, n64 frozen-core rem-k, killed Hamming U_ids, rem2, S0+1.

Families:
  M) Forced 180-asymm half-S0 + twin blacklist maximize (cheap)
  N) Empty-row inject Hamming (new U_ids; Rem-as-variables)
  O) Pattern grow: knight / quadratic / permutation / staircase (not lattice-mod3)
  P) n64 geometric Hamming (empty-row + interior Add)
  Q) n100 corner-Rem x interior-Add Hamming
"""
from __future__ import annotations

import json
import os
import random
import sys
import time
from collections import Counter
from typing import List, Optional, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(__file__))

from data.baselines.official_raw import SOL_64, SOL_100  # noqa: E402
from src.search.hamming_shell_conflict import (  # noqa: E402
    hamming_shell_search,
    universe_hash,
)
from src.search.incremental_state import IncrementalIsoscelesFreeSet  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402
from w3_new_families_v1 import dual, grow_from_seed, maximize_core, ring  # noqa: E402

Point = Tuple[int, int]
EXP = os.path.join(RUN, "EXPERIMENTS", "W3_new_families")
CAND = os.path.join(RUN, "CANDIDATES")
S0_HASH_100 = "8a84216d"
S0_HASH_64 = "47d42165"


def _dump(path: str, obj: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def _maybe_promote(n: int, target: int, pts: Sequence[Point], tag: str) -> Optional[str]:
    d = dual(list(pts), n)
    if d["size"] >= target and d["oracle"] and d["indep"]:
        os.makedirs(CAND, exist_ok=True)
        path = os.path.join(CAND, f"{tag}_legal.json")
        _dump(path, {"n": n, "points": [list(p) for p in pts], **d, "tag": tag})
        print(json.dumps({"PROMOTE": tag, **d}), flush=True)
        return path
    return None


def _hamming_row(
    n: int,
    s0: List[Point],
    rem: List[Point],
    add: List[Point],
    r: int,
    budget: float,
    seed: int,
    workers: int,
    u_id: str,
) -> dict:
    if r > len(rem) or r + 1 > len(add) or r < 1:
        return {
            "U_id": u_id,
            "status": "SKIP_CARD",
            "r": r,
            "n_rem": len(rem),
            "n_add": len(add),
        }
    uh = universe_hash(rem, add)
    t0 = time.time()
    result = hamming_shell_search(
        n=n,
        s0=s0,
        removable=rem,
        addable=add,
        r=r,
        time_budget_s=budget,
        seed=seed,
        u_id=u_id,
        universe_hash_str=uh,
        per_round_time_limit_s=min(20.0, budget),
        num_workers=workers,
        symmetry_mode="asymmetric",
    )
    row = {
        "U_id": u_id,
        "status": result.status,
        "r": r,
        "n_rem": len(rem),
        "n_add": len(add),
        "universe_hash": uh,
        "rounds": (result.meta or {}).get("rounds"),
        "final_cuts": (result.meta or {}).get("final_cuts"),
        "best_illegal_V": (result.meta or {}).get("best_illegal_V"),
        "wall_s": time.time() - t0,
    }
    if result.points:
        d = dual(result.points, n)
        row["dual"] = d
        tgt = 165 if n == 100 else 113
        if d["size"] >= tgt and d["oracle"] and d["indep"]:
            _maybe_promote(n, tgt, result.points, u_id)
            row["points"] = [list(p) for p in result.points]
    print(json.dumps({k: v for k, v in row.items() if k != "points"}), flush=True)
    return row


def empty_rows_cols(s0: Set[Point], n: int):
    used_r = {p[1] for p in s0}
    used_c = {p[0] for p in s0}
    er = [y for y in range(n) if y not in used_r]
    ec = [x for x in range(n) if x not in used_c]
    return er, ec


def family_M(workers: int, per: float) -> dict:
    """Keep lex-min of each 180 pair; blacklist twins so S0 cannot snap back."""
    n, target = 100, 165
    s0 = set((int(x), int(y)) for x, y in SOL_100)
    partner = lambda p: (n - 1 - p[0], n - 1 - p[1])
    keep, bl = set(), set()
    for p in s0:
        q = partner(p)
        if p <= q:
            keep.add(p)
            if q != p and q in s0:
                bl.add(q)
        else:
            bl.add(p)
    core = sorted(keep)
    rows = []
    plans = [
        ("asymm_west_bl_twins", core, bl),
        ("asymm_east_bl_twins", sorted(bl), keep),
    ]
    # Also keep only boundary-half (x < 50) of S0, blacklist the rest of S0
    west = sorted(p for p in s0 if p[0] < 50)
    east = s0 - set(west)
    plans.append(("geom_west_bl_eastS0", west, east))
    north = sorted(p for p in s0 if p[1] < 50)
    south = s0 - set(north)
    plans.append(("geom_north_bl_southS0", north, south))
    for i, (name, c, blacklist) in enumerate(plans):
        print(json.dumps({"M": name, "core": len(c), "bl": len(blacklist)}), flush=True)
        res = maximize_core(n, list(c), per, workers, seed=11000 + i, target=target, blacklist=set(blacklist))
        row = {k: v for k, v in res.items() if k != "points"}
        row["plan"] = name
        if res.get("best_hash", "").startswith(S0_HASH_100):
            row["s0_snap"] = True
        rows.append(row)
        print(json.dumps(row, indent=2), flush=True)
        if res.get("best_legal_size", 0) >= target and res.get("points"):
            _maybe_promote(n, target, [tuple(p) for p in res["points"]], f"famM_{name}")
            break
    out = {
        "schema": "w3_newfam_M_asymm_v1",
        "rows": rows,
        "best": max((r.get("best_legal_size") or 0) for r in rows) if rows else 0,
        "any_plus": any(r.get("best_legal_size", 0) >= target for r in rows),
    }
    _dump(os.path.join(EXP, "family_M_asymm.json"), out)
    return out


def family_N(workers: int, cheap: float) -> dict:
    """Empty-row / empty-col inject Hamming — Add lives on unused rows of S0."""
    n = 100
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0s = set(s0)
    er, ec = empty_rows_cols(s0s, n)
    # Prefer outer empty rows (frame-adjacent) and a few inner empty rows
    er_outer = sorted(er, key=lambda y: min(y, n - 1 - y))[:8]
    er_inner = sorted(er, key=lambda y: -min(y, n - 1 - y))[:6]
    ec_outer = sorted(ec, key=lambda x: min(x, n - 1 - x))[:8]
    occupied_adj = set()
    for y in er_outer:
        for yy in (y - 1, y + 1):
            occupied_adj.update(p for p in s0 if p[1] == yy)
    rem_adj = sorted(occupied_adj) or list(s0[:40])

    def cells_on_rows(rows: Sequence[int]) -> List[Point]:
        return [(x, y) for y in rows for x in range(n) if (x, y) not in s0s]

    def cells_on_cols(cols: Sequence[int]) -> List[Point]:
        return [(x, y) for x in cols for y in range(n) if (x, y) not in s0s]

    # Cap Add size for cheap-kill (avoid ~full-grid TIMEOUT)
    def cap_add(pts: List[Point], k: int, rng_seed: int) -> List[Point]:
        if len(pts) <= k:
            return pts
        rng = random.Random(rng_seed)
        # Keep outer-ring bias
        pts = sorted(pts, key=lambda p: (ring(p, n), rng.random()))
        return pts[:k]

    unis = [
        ("U_emptyrow_outer8_Add_adjRem", rem_adj, cap_add(cells_on_rows(er_outer), 400, 1)),
        ("U_emptyrow_inner6_Add_fullRem", s0, cap_add(cells_on_rows(er_inner), 400, 2)),
        ("U_emptycol_outer8_Add_fullRem", s0, cap_add(cells_on_cols(ec_outer), 400, 3)),
        (
            "U_emptyrow_outer4_tight",
            sorted(p for p in s0 if abs(p[1] - er_outer[0]) <= 3 or abs(p[1] - er_outer[1]) <= 3),
            cap_add(cells_on_rows(er_outer[:4]), 250, 4),
        ),
    ]
    rows = []
    for u_id, rem, add in unis:
        for r in (2, 3, 4):
            uid = f"{u_id}_r{r}"
            print(json.dumps({"N": uid, "n_rem": len(rem), "n_add": len(add)}), flush=True)
            row = _hamming_row(n, s0, rem, add, r, cheap, 1201 + r, workers, uid)
            rows.append(row)
            if row.get("status") == "FEASIBLE_LEGAL" and row.get("dual", {}).get("size", 0) >= 165:
                break
        else:
            continue
        break
    out = {
        "schema": "w3_newfam_N_emptyrow_hamming_v1",
        "rows": rows,
        "any_plus": any(
            r.get("status") == "FEASIBLE_LEGAL" and r.get("dual", {}).get("size", 0) >= 165 for r in rows
        ),
        "n_infeas": sum(1 for r in rows if r.get("status") == "INFEASIBLE_SCOPED"),
        "n_timeout": sum(1 for r in rows if r.get("status") == "TIMEOUT_INCONCLUSIVE"),
    }
    _dump(os.path.join(EXP, "family_N_emptyrow.json"), out)
    return out


def _filter_seed(n: int, seed_pts: Sequence[Point]) -> List[Point]:
    st = IncrementalIsoscelesFreeSet(n)
    kept = []
    for p in seed_pts:
        if st.can_add(p)[0]:
            st.add_point(p)
            kept.append(p)
    return kept


def family_O(workers: int, grow_s: float, max_s: float) -> dict:
    """Pattern seeds that are not lattice-mod3 / parity / avoid-S0 / ring."""
    n, target = 100, 165
    s0_hash_prefix = S0_HASH_100
    rng = random.Random(7)
    plans = []
    # Knight residue classes
    for r0 in (0, 1, 2):
        seed = [(x, y) for x in range(n) for y in range(n) if (x + 2 * y) % 5 == r0]
        plans.append((f"knight_r{r0}", _filter_seed(n, seed), "boundary_first"))
    # Quadratic permutation (one per x)
    for a, b in ((1, 0), (3, 7), (7, 13)):
        seed = [(x, (a * x * x + b) % n) for x in range(n)]
        plans.append((f"quad_a{a}_b{b}", _filter_seed(n, seed), "boundary_first"))
    # Staircase / coprime slope, several residues
    for k in (3, 7, 11):
        seed = [(x, (k * x) % n) for x in range(n)]
        seed += [(x, (k * x + n // 2) % n) for x in range(0, n, 2)]
        plans.append((f"stair_k{k}", _filter_seed(n, seed), "center_first"))
    # Random permutation on a 50-row subset mixing empty+used
    er, _ = empty_rows_cols(set((int(x), int(y)) for x, y in SOL_100), n)
    rows_sel = sorted(er[:20] + list(range(0, n, 5)))[:40]
    cols = list(range(n))
    rng.shuffle(cols)
    seed = [(cols[i], rows_sel[i]) for i in range(min(len(rows_sel), len(cols)))]
    plans.append(("perm40_emptybias", _filter_seed(n, seed), "random"))

    rows = []
    best = 0
    for i, (name, seed, mode) in enumerate(plans):
        print(json.dumps({"O_seed": name, "seed_kept": len(seed)}), flush=True)
        g = grow_from_seed(n, seed, mode, grow_s, rng_seed=13000 + i)
        grow_meta = {k: v for k, v in g.items() if k != "points"}
        grow_meta["plan"] = name
        grow_meta["s0_snap"] = str(g.get("hash", "")).startswith(s0_hash_prefix)
        print(json.dumps({"O_grow": grow_meta}), flush=True)
        if not (g.get("oracle") and g.get("indep")):
            rows.append({"plan": name, "status": "GROW_ILLEGAL", **grow_meta})
            continue
        core = [tuple(p) for p in g["points"]]
        # No S0 blacklist: mixing allowed, but we start far from S0. Snap is recorded.
        res = maximize_core(n, core, max_s, workers, seed=14000 + i, target=target, blacklist=None)
        row = {k: v for k, v in res.items() if k != "points"}
        row.update({"plan": name, "grow_size": g["size"], "grow_hash": g["hash"], "s0_snap": str(res.get("best_hash", g["hash"])).startswith(s0_hash_prefix)})
        rows.append(row)
        print(json.dumps({k: v for k, v in row.items() if k != "points"}, indent=2), flush=True)
        best = max(best, int(row.get("best_legal_size") or g["size"] or 0))
        if res.get("best_legal_size", 0) >= target and res.get("points"):
            _maybe_promote(n, target, [tuple(p) for p in res["points"]], f"famO_{name}")
            break
    out = {
        "schema": "w3_newfam_O_pattern_v1",
        "rows": rows,
        "best": best,
        "any_plus": any(r.get("best_legal_size", 0) >= target for r in rows),
        "any_s0_snap": any(r.get("s0_snap") for r in rows),
    }
    _dump(os.path.join(EXP, "family_O_pattern.json"), out)
    return out


def family_P(workers: int, cheap: float) -> dict:
    """n64 Hamming: empty-row inject + interior Add. Rem are variables (not frozen core)."""
    n = 64
    s0 = sorted((int(x), int(y)) for x, y in SOL_64)
    s0s = set(s0)
    er, ec = empty_rows_cols(s0s, n)
    er_outer = sorted(er, key=lambda y: min(y, n - 1 - y))[:6]
    add_er = [(x, y) for y in er_outer for x in range(n) if (x, y) not in s0s]
    add_er = sorted(add_er, key=lambda p: ring(p, n))[:300]
    add_interior = [(x, y) for x in range(n) for y in range(n) if (x, y) not in s0s and ring((x, y), n) >= 12]
    add_interior = sorted(add_interior, key=lambda p: -ring(p, n))[:350]
    rem_outer = [p for p in s0 if ring(p, n) <= 6]
    unis = [
        ("U64_emptyrow6_fullRem", s0, add_er),
        ("U64_interiorAdd_outerRem", rem_outer, add_interior),
        ("U64_emptycol6_fullRem", s0, [(x, y) for x in sorted(ec, key=lambda z: min(z, n - 1 - z))[:6] for y in range(n) if (x, y) not in s0s][:300]),
    ]
    rows = []
    for u_id, rem, add in unis:
        add = sorted(set(add))
        rem = sorted(set(rem))
        for r in (2, 3):
            uid = f"{u_id}_r{r}"
            print(json.dumps({"P": uid, "n_rem": len(rem), "n_add": len(add)}), flush=True)
            rows.append(_hamming_row(n, s0, rem, add, r, cheap, 1500 + r, workers, uid))
            if rows[-1].get("status") == "FEASIBLE_LEGAL" and rows[-1].get("dual", {}).get("size", 0) >= 113:
                break
    out = {
        "schema": "w3_newfam_P_n64_hamming_v1",
        "rows": rows,
        "any_plus": any(
            r.get("status") == "FEASIBLE_LEGAL" and r.get("dual", {}).get("size", 0) >= 113 for r in rows
        ),
        "n_infeas": sum(1 for r in rows if r.get("status") == "INFEASIBLE_SCOPED"),
        "n_timeout": sum(1 for r in rows if r.get("status") == "TIMEOUT_INCONCLUSIVE"),
    }
    _dump(os.path.join(EXP, "family_P_n64_hamming.json"), out)
    return out


def family_Q(workers: int, cheap: float) -> dict:
    """n100: delete outer-frame S0, add interior (H-002 empty center) — Hamming not LNS."""
    n = 100
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0s = set(s0)
    rem_outer = [p for p in s0 if ring(p, n) <= 5]
    rem_mid = [p for p in s0 if 6 <= ring(p, n) <= 12]
    add_in = [(x, y) for x in range(n) for y in range(n) if (x, y) not in s0s and ring((x, y), n) >= 22]
    add_in = sorted(add_in, key=lambda p: -ring(p, n))[:400]
    add_midin = [(x, y) for x in range(n) for y in range(n) if (x, y) not in s0s and 16 <= ring((x, y), n) <= 28]
    add_midin = sorted(add_midin, key=lambda p: ring(p, n))[:400]
    # Knight-neighborhood of a sample of S0 (not Chebyshev halo — killed)
    rng = random.Random(11)
    sample = rng.sample(s0, k=40)
    knight = []
    for x, y in sample:
        for dx, dy in ((1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n and (nx, ny) not in s0s:
                knight.append((nx, ny))
    knight = sorted(set(knight))
    rem_near = []
    for x, y in sample:
        rem_near.extend(p for p in s0 if max(abs(p[0] - x), abs(p[1] - y)) <= 2)
    rem_near = sorted(set(rem_near))
    unis = [
        ("U_outerRem_interiorAdd", rem_outer, add_in),
        ("U_midRem_midinteriorAdd", rem_mid, add_midin),
        ("U_knightAdd_nearRem", rem_near, knight),
    ]
    rows = []
    for u_id, rem, add in unis:
        for r in (2, 3, 4):
            uid = f"{u_id}_r{r}"
            print(json.dumps({"Q": uid, "n_rem": len(rem), "n_add": len(add)}), flush=True)
            rows.append(_hamming_row(n, s0, rem, add, r, cheap, 1600 + r, workers, uid))
            if rows[-1].get("status") == "FEASIBLE_LEGAL" and rows[-1].get("dual", {}).get("size", 0) >= 165:
                break
    out = {
        "schema": "w3_newfam_Q_corner_interior_v1",
        "rows": rows,
        "any_plus": any(
            r.get("status") == "FEASIBLE_LEGAL" and r.get("dual", {}).get("size", 0) >= 165 for r in rows
        ),
        "n_infeas": sum(1 for r in rows if r.get("status") == "INFEASIBLE_SCOPED"),
        "n_timeout": sum(1 for r in rows if r.get("status") == "TIMEOUT_INCONCLUSIVE"),
    }
    _dump(os.path.join(EXP, "family_Q_interior.json"), out)
    return out


def family_R(workers: int, cheap: float) -> dict:
    """Larger-r Hamming on N/Q-style universes. r=4 INFEAS does not imply r=8 INFEAS."""
    n = 100
    s0 = sorted((int(x), int(y)) for x, y in SOL_100)
    s0s = set(s0)
    er, ec = empty_rows_cols(s0s, n)
    er_outer = sorted(er, key=lambda y: min(y, n - 1 - y))[:8]
    add_er = [(x, y) for y in er_outer for x in range(n) if (x, y) not in s0s]
    add_er = sorted(add_er, key=lambda p: ring(p, n))[:500]
    add_in = [(x, y) for x in range(n) for y in range(n) if (x, y) not in s0s and ring((x, y), n) >= 20]
    add_in = sorted(add_in, key=lambda p: -ring(p, n))[:500]
    rem_outer = [p for p in s0 if ring(p, n) <= 6]
    unis = [
        ("U_emptyrow8_fullRem_rbig", s0, add_er),
        ("U_outerRem_interiorAdd_rbig", rem_outer, add_in),
        (
            "U_emptycol8_fullRem_rbig",
            s0,
            [
                (x, y)
                for x in sorted(ec, key=lambda z: min(z, n - 1 - z))[:8]
                for y in range(n)
                if (x, y) not in s0s
            ][:500],
        ),
    ]
    rows = []
    for u_id, rem, add in unis:
        rem, add = sorted(set(rem)), sorted(set(add))
        for r in (6, 8, 12):
            uid = f"{u_id}_r{r}"
            print(json.dumps({"R": uid, "n_rem": len(rem), "n_add": len(add)}), flush=True)
            rows.append(_hamming_row(n, s0, rem, add, r, cheap, 1700 + r, workers, uid))
            if rows[-1].get("status") == "FEASIBLE_LEGAL" and rows[-1].get("dual", {}).get("size", 0) >= 165:
                break
    out = {
        "schema": "w3_newfam_R_larger_r_v1",
        "rows": rows,
        "any_plus": any(
            r.get("status") == "FEASIBLE_LEGAL" and r.get("dual", {}).get("size", 0) >= 165 for r in rows
        ),
        "n_infeas": sum(1 for r in rows if r.get("status") == "INFEASIBLE_SCOPED"),
        "n_timeout": sum(1 for r in rows if r.get("status") == "TIMEOUT_INCONCLUSIVE"),
    }
    _dump(os.path.join(EXP, "family_R_largerr.json"), out)
    return out


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    os.makedirs(EXP, exist_ok=True)
    os.makedirs(CAND, exist_ok=True)
    workers = int(os.environ.get("W3_WORKERS", "4"))
    phase = os.environ.get("W3_PHASE", "all")
    cheap = float(os.environ.get("W3_CHEAP_S", "45"))
    m_s = float(os.environ.get("W3_M_S", "75"))
    grow_s = float(os.environ.get("W3_GROW_S", "50"))
    max_s = float(os.environ.get("W3_O_S", "90"))
    sum_path = os.path.join(EXP, "summary_v4.json")
    if os.path.exists(sum_path):
        try:
            summary = json.load(open(sum_path, encoding="utf-8"))
            summary.setdefault("schema", "w3_new_families_v4")
            summary.setdefault("phases", {})
        except Exception:
            summary = {"schema": "w3_new_families_v4", "phases": {}}
    else:
        summary = {"schema": "w3_new_families_v4", "phases": {}}

    order = [
        ("M", lambda: family_M(workers, m_s)),
        ("N", lambda: family_N(workers, cheap)),
        ("Q", lambda: family_Q(workers, cheap)),
        ("P", lambda: family_P(workers, cheap)),
        ("R", lambda: family_R(workers, cheap)),
        ("O", lambda: family_O(workers, grow_s, max_s)),
    ]
    for name, fn in order:
        if phase not in (name, "all", "cheap"):
            continue
        if phase == "cheap" and name == "O":
            continue  # O is grow+max; run after Hamming cheap-kill
        print(json.dumps({"start_phase": name}), flush=True)
        res = fn()
        summary["phases"][name] = {
            "best": res.get("best"),
            "any_plus": res.get("any_plus"),
            "n_infeas": res.get("n_infeas"),
            "n_timeout": res.get("n_timeout"),
        }
        _dump(os.path.join(EXP, "summary_v4.json"), summary)
        print(json.dumps({"done": name, **summary["phases"][name]}), flush=True)
        if res.get("any_plus"):
            break

    summary["any_plus"] = any(p.get("any_plus") for p in summary["phases"].values())
    _dump(os.path.join(EXP, "summary_v4.json"), summary)
    print(json.dumps({"done_v4": True, **summary}, indent=2), flush=True)


if __name__ == "__main__":
    main()
