#!/usr/bin/env python3
"""Resume Wave-2 long pilots using existing smoke summaries under scratch/agent_b/."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.search.orbit_defect_search import (  # noqa: E402
    DEFAULT_WORKERS,
    SCRATCH,
    SearchConfig,
    TARGETS,
    _write_report,
    append_manifest,
    ensure_scratch,
    git_commit,
    run_long_pilot,
)

SCHEDULE = [
    dict(n=100, t=0, mode="defect", dmin=1, dmax=8, minutes=50, seed=21),
    dict(n=100, t=0, mode="partial", dmin=1, dmax=8, minutes=35, seed=22),
    dict(n=100, t=1, mode="pure", dmin=0, dmax=0, minutes=40, seed=31),
    dict(n=100, t=1, mode="defect", dmin=1, dmax=8, minutes=35, seed=32),
    dict(n=100, t=2, mode="pure", dmin=0, dmax=0, minutes=40, seed=33),
    dict(n=100, t=2, mode="defect", dmin=1, dmax=8, minutes=30, seed=34),
    dict(n=64, t=0, mode="defect", dmin=1, dmax=8, minutes=40, seed=41),
    dict(n=64, t=1, mode="pure", dmin=0, dmax=0, minutes=30, seed=42),
    dict(n=64, t=1, mode="defect", dmin=1, dmax=8, minutes=25, seed=43),
    dict(n=100, t=3, mode="defect", dmin=1, dmax=8, minutes=25, seed=51),
    dict(n=100, t=4, mode="defect", dmin=1, dmax=8, minutes=20, seed=52),
    dict(n=64, t=3, mode="defect", dmin=1, dmax=8, minutes=20, seed=53),
    dict(n=100, t=5, mode="defect", dmin=1, dmax=8, minutes=18, seed=54),
    dict(n=100, t=6, mode="defect", dmin=1, dmax=8, minutes=18, seed=55),
]


def _done_tags() -> set:
    done = set()
    man = SCRATCH / "manifest.jsonl"
    if not man.exists():
        return done
    for line in man.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("phase") == "long_pilot_final" and rec.get("tag"):
            done.add(rec["tag"])
    return done


def main() -> int:
    ensure_scratch()
    budget_s = float(os.environ.get("AGENT_B_BUDGET_HOURS", "5.0")) * 3600
    workers = int(os.environ.get("AGENT_B_WORKERS", str(DEFAULT_WORKERS)))
    t0 = time.time()
    done = _done_tags()
    n100_runs = []
    n64_runs = []

    smoke64 = json.loads((SCRATCH / "axis_smoke_n64.json").read_text(encoding="utf-8"))
    smoke100 = json.loads((SCRATCH / "axis_smoke_n100.json").read_text(encoding="utf-8"))

    for spec in SCHEDULE:
        rem = budget_s - (time.time() - t0)
        if rem < 120:
            break
        tag = (
            f"long_n{spec['n']}_t{spec['t']}_{spec['mode']}"
            f"_d{spec['dmin']}-{spec['dmax']}_s{spec['seed']}"
        )
        if tag in done:
            print(f"SKIP done {tag}", flush=True)
            continue
        budget = min(spec["minutes"] * 60.0, rem - 60)
        if budget < 90:
            break
        cfg = SearchConfig(
            n=spec["n"],
            symmetry_type=spec["t"],
            mode=spec["mode"],
            target_size=TARGETS[spec["n"]],
            defect_budget_min=spec["dmin"],
            defect_budget_max=spec["dmax"],
            time_budget_s=budget,
            per_round_time_limit_s=30.0,
            seed=spec["seed"],
            num_workers=workers,
            max_extra_orbits=100 if spec["n"] == 100 else 80,
            max_defect_pool=120 if spec["n"] == 100 else 80,
            halo_radius=8,
            agent_c_universe="U_medium",
        )
        print(f"START {tag} budget={budget:.0f}s", flush=True)
        result = run_long_pilot(cfg, tag)
        entry = {
            "tag": tag,
            "n": spec["n"],
            "symmetry_type": spec["t"],
            "mode": spec["mode"],
            "defect_budget": [spec["dmin"], spec["dmax"]],
            "status": result["solver_status"],
            "size": result.get("size", 0),
            "wall_time_s": result.get("pilot_wall_time_s", result.get("wall_time_s")),
            "model_hash": result.get("model_hash"),
            "universe_id": (result.get("universe") or {}).get("universe_id"),
            "candidate": result.get("candidate_path"),
            "verify": result.get("verify"),
            "infeasible_record": result.get("infeasible_record"),
            "scope": result.get("scope"),
        }
        if spec["n"] == 100:
            n100_runs.append(entry)
        else:
            n64_runs.append(entry)
        append_manifest({**entry, "phase": "long_pilot", "git_commit": git_commit()})
        print(
            f"DONE {tag} status={entry['status']} size={entry['size']} "
            f"wall={entry['wall_time_s']:.1f}",
            flush=True,
        )

    def best_of(runs):
        legal = [r for r in runs if (r.get("size") or 0) >= TARGETS.get(r["n"], 10**9)]
        if legal:
            return sorted(legal, key=lambda r: -r["size"])[0]
        return max(runs, key=lambda r: (r.get("size") or 0)) if runs else {}

    # Merge any prior long_pilot entries from manifest for complete summaries
    for line in (SCRATCH / "manifest.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("phase") != "long_pilot":
            continue
        entry = {k: rec.get(k) for k in (
            "tag", "n", "symmetry_type", "mode", "defect_budget", "status", "size",
            "wall_time_s", "model_hash", "universe_id", "candidate", "verify",
            "infeasible_record", "scope",
        )}
        if entry["n"] == 100 and entry not in n100_runs and not any(
            e.get("tag") == entry.get("tag") for e in n100_runs
        ):
            n100_runs.append(entry)
        if entry["n"] == 64 and not any(e.get("tag") == entry.get("tag") for e in n64_runs):
            n64_runs.append(entry)

    n100_summary = {
        "n": 100,
        "target": 165,
        "git_commit": git_commit(),
        "num_workers": workers,
        "smoke_ref": "axis_smoke_summary.json",
        "runs": n100_runs,
        "best": best_of(n100_runs),
        "wall_time_s": sum(r.get("wall_time_s") or 0 for r in n100_runs),
        "any_legal_plus1": any((r.get("size") or 0) >= 165 for r in n100_runs),
    }
    n64_summary = {
        "n": 64,
        "target": 113,
        "git_commit": git_commit(),
        "num_workers": workers,
        "runs": n64_runs,
        "best": best_of(n64_runs),
        "wall_time_s": sum(r.get("wall_time_s") or 0 for r in n64_runs),
        "any_legal_plus1": any((r.get("size") or 0) >= 113 for r in n64_runs),
    }
    (SCRATCH / "n100_orbit_defect_summary.json").write_text(
        json.dumps(n100_summary, indent=2), encoding="utf-8"
    )
    (SCRATCH / "n64_orbit_defect_summary.json").write_text(
        json.dumps(n64_summary, indent=2), encoding="utf-8"
    )
    report = _write_report(smoke64, smoke100, n100_summary, n64_summary, time.time() - t0)
    print(json.dumps({
        "report": str(report),
        "total_wall_time_s": time.time() - t0,
        "n100_best": n100_summary["best"],
        "n64_best": n64_summary["best"],
        "any_legal_n100": n100_summary["any_legal_plus1"],
        "any_legal_n64": n64_summary["any_legal_plus1"],
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
