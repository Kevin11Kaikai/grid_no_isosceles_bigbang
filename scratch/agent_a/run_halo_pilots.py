"""Build Agent-A halo-enlarged universes and run longer Hamming pilots.

New U_ids (not Gate-1 frozen lists):
  U_fullrem_Asmall_r2 — Rem=all S0 (164), Add=U_small_r2 add (44)
  U_fullrem_Alarge_r2 — Rem=all S0 (164), Add=U_large add (128)
  U_score_spatial_halo_r2 — Rem=U_large rem ∪ spatial Chebyshev-1 halo of rem in S0;
                            Add=U_large add ∪ easiest_16 ∪ Chebyshev-1 of those adds
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from data.baselines.official_raw import SOL_100
from src.search.hamming_shell_conflict import (
    append_manifest,
    atomic_write_json,
    hamming_shell_search,
    load_policy_universe,
    universe_hash,
)


def chebyshev_halo(points, n: int, radius: int):
    out = set()
    for x, y in points:
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if max(abs(dx), abs(dy)) <= radius:
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < n and 0 <= yy < n:
                        out.add((xx, yy))
    return out


def build_universes():
    s0 = [tuple(p) for p in SOL_100]
    s0_set = set(s0)
    _, add_r2, _ = load_policy_universe(100, "U_small_r2")
    rem_large, add_large, _ = load_policy_universe(100, "U_large")
    with open("scratch/audit/gate1_consistency_check.json", encoding="utf-8") as f:
        e16 = [tuple(p) for p in json.load(f)["n100_deletion_bound"]["easiest_16_qs_exact_min_deletions_2"]]

    universes = {}
    universes["U_fullrem_Asmall_r2"] = {
        "rem": sorted(s0),
        "add": sorted(set(map(tuple, add_r2))),
    }
    universes["U_fullrem_Alarge_r2"] = {
        "rem": sorted(s0),
        "add": sorted(set(map(tuple, add_large))),
    }

    rem_halo = set(map(tuple, rem_large))
    rem_halo |= {p for p in chebyshev_halo(rem_large, 100, 1) if p in s0_set}
    add_halo = set(map(tuple, add_large)) | set(e16)
    add_halo |= {p for p in chebyshev_halo(list(add_halo), 100, 1) if p not in s0_set}
    universes["U_score_spatial_halo_r2"] = {
        "rem": sorted(rem_halo),
        "add": sorted(add_halo),
    }

    out = {}
    for uid, u in universes.items():
        h = universe_hash(u["rem"], u["add"])
        out[uid] = {
            "removable": [list(p) for p in u["rem"]],
            "addable": [list(p) for p in u["add"]],
            "n_removable": len(u["rem"]),
            "n_addable": len(u["add"]),
            "n_vars": len(u["rem"]) + len(u["add"]),
            "universe_hash": h,
        }
        print(uid, out[uid]["n_vars"], h)
    atomic_write_json("scratch/agent_a/hamming/halo_universes.json", out)
    return {uid: (universes[uid]["rem"], universes[uid]["add"], out[uid]["universe_hash"]) for uid in universes}


def main():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        commit = None
    us = build_universes()
    s0 = list(SOL_100)
    # Longer pilots on enlarged universes
    configs = [
        ("U_fullrem_Asmall_r2", 1, 1800, "asymmetric"),
        ("U_fullrem_Asmall_r2", 2, 1800, "asymmetric"),
        ("U_fullrem_Alarge_r2", 1, 2400, "asymmetric"),
        ("U_score_spatial_halo_r2", 1, 1800, "asymmetric"),
    ]
    summary = []
    for uid, seed, budget, sym in configs:
        rem, add, h = us[uid]
        out_path = f"scratch/agent_a/hamming/r2_n100_{uid}_seed{seed}.json"
        ckpt = f"scratch/agent_a/checkpoints/r2_n100_{uid}_seed{seed}.ckpt.json"
        print(f"=== {uid} seed={seed} vars={len(rem)+len(add)} budget={budget} ===")
        t0 = time.time()
        res = hamming_shell_search(
            n=100,
            s0=s0,
            removable=rem,
            addable=add,
            r=2,
            time_budget_s=budget,
            seed=seed,
            u_id=uid,
            universe_hash_str=h,
            per_round_time_limit_s=60.0,
            num_workers=5,
            symmetry_mode=sym,
            checkpoint_path=ckpt,
            checkpoint_every_s=300.0,
            git_commit=commit,
        )
        wall = time.time() - t0
        payload = {
            "status": res.status,
            "points": [list(p) for p in res.points] if res.points else None,
            "meta": res.meta,
            "universe_hash": h,
            "n_rem": len(rem),
            "n_add": len(add),
            "n_vars": len(rem) + len(add),
            "wall_time_s": wall,
            "U_id": uid,
            "seed": seed,
        }
        atomic_write_json(out_path, payload)
        append_manifest(
            "scratch/agent_a/manifest.jsonl",
            {
                "event": "hamming_halo_pilot",
                "out": out_path,
                "status": res.status,
                "U_id": uid,
                "seed": seed,
                "universe_hash": h,
                "wall_time_s": wall,
                "n_vars": len(rem) + len(add),
            },
        )
        summary.append(
            {
                "U_id": uid,
                "seed": seed,
                "status": res.status,
                "wall_time_s": wall,
                "rounds": res.meta.get("rounds"),
                "final_cuts": res.meta.get("final_cuts"),
                "best_illegal_V": res.meta.get("best_illegal_V"),
                "universe_hash": h,
                "n_vars": len(rem) + len(add),
            }
        )
        print("->", res.status, "wall", round(wall, 2), "cuts", res.meta.get("final_cuts"), "bestV", res.meta.get("best_illegal_V"))
        if res.status == "FEASIBLE_LEGAL" and res.points:
            # dual already inside; save candidate
            from src.search.hamming_shell_conflict import dual_verify

            ver = dual_verify(res.points, 100)
            cpath = f"scratch/agent_a/candidates/n100_k{len(res.points)}_{uid}_seed{seed}.json"
            atomic_write_json(
                cpath,
                {
                    "points_unsorted": [list(p) for p in res.points],
                    "points_sorted": [list(p) for p in sorted(res.points)],
                    "verification": ver,
                    "method": "hamming_shell_conflict",
                    "seed": seed,
                    "scope": res.meta.get("scope"),
                    "git_commit": commit,
                },
            )
            print("SAVED CANDIDATE", cpath, ver)
    atomic_write_json("scratch/agent_a/hamming/halo_pilot_summary.json", {"runs": summary})
    print("HALO DONE")


if __name__ == "__main__":
    main()
