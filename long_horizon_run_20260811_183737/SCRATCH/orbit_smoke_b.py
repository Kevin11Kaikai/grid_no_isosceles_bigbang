#!/usr/bin/env python3
"""LH-2 Route B cheap smoke: short orbit-defect pilots, new seeds, no TIMEOUT grind."""
from __future__ import annotations

import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RUN = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)


def main():
    t0 = time.time()
    # Import module; run small smokes if CLI/helpers exist
    from src.search import orbit_defect_search as ods

    exp = os.path.join(RUN, "EXPERIMENTS", "LH2_orbit_smoke")
    os.makedirs(exp, exist_ok=True)
    results = []

    # Discover callable entrypoints
    attrs = [a for a in dir(ods) if not a.startswith("_")]
    entry = None
    for name in (
        "run_orbit_defect_search",
        "orbit_defect_search",
        "run_pilot",
        "main",
        "search",
    ):
        if hasattr(ods, name) and callable(getattr(ods, name)):
            entry = name
            break

    meta = {"module_attrs_sample": attrs[:40], "entry": entry}

    if entry == "main":
        # Avoid full CLI; try programmatic API via inspect
        import inspect

        src = inspect.getsource(ods)
        meta["source_len"] = len(src)
        # Prefer documented run function patterns from wave2
        if hasattr(ods, "run_search"):
            entry = "run_search"

    # Wave2 style: look for OrbitConfig / solve
    if hasattr(ods, "run_scoped_search"):
        fn = ods.run_scoped_search
    elif hasattr(ods, "run_orbit_pilot"):
        fn = ods.run_orbit_pilot
    else:
        fn = None

    if fn is None:
        # Fallback: read module docstring / argparse and invoke subprocess short
        import subprocess

        py = os.path.join(ROOT, ".venv_solver", "Scripts", "python.exe")
        if not os.path.exists(py):
            py = sys.executable
        # Try --help
        help_out = subprocess.run(
            [py, "-m", "src.search.orbit_defect_search", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        meta["help_rc"] = help_out.returncode
        meta["help_stdout"] = help_out.stdout[:2000]
        meta["help_stderr"] = help_out.stderr[:1000]
        # Attempt a very short n100 type1 pure smoke if CLI matches wave2
        cmd_candidates = []
        helptext = help_out.stdout + help_out.stderr
        if "--n" in helptext or "n=" in helptext or "usage" in helptext.lower():
            # parse common flags from wave2 checkpoints naming
            for args in (
                ["--n", "100", "--type", "1", "--mode", "pure", "--seed", "41", "--budget", "30"],
                ["--n", "100", "--axis", "1", "--defect", "0", "--seed", "41", "--time", "30"],
                ["n100", "t1", "pure", "30"],
            ):
                cmd_candidates.append(args)

        for args in cmd_candidates:
            proc = subprocess.run(
                [py, "-m", "src.search.orbit_defect_search", *args],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=90,
            )
            results.append(
                {
                    "args": args,
                    "rc": proc.returncode,
                    "stdout_tail": proc.stdout[-1500:],
                    "stderr_tail": proc.stderr[-800:],
                }
            )
            if proc.returncode == 0:
                break
    else:
        # Call with short budget if signature allows
        import inspect

        sig = inspect.signature(fn)
        meta["fn"] = fn.__name__
        meta["params"] = list(sig.parameters)
        kwargs = {}
        for k, v in {
            "n": 100,
            "axis_type": 1,
            "type_id": 1,
            "mode": "pure",
            "defect_budget": 0,
            "seed": 41,
            "time_limit_s": 30,
            "budget_s": 30,
            "time_budget_s": 30,
        }.items():
            if k in sig.parameters:
                kwargs[k] = v
        try:
            out = fn(**kwargs)
            results.append({"call_kwargs": kwargs, "result": out if not callable(out) else str(type(out))})
        except TypeError as e:
            results.append({"call_kwargs": kwargs, "TypeError": str(e)})

    payload = {
        "schema": "lh2_orbit_smoke_v1",
        "meta": meta,
        "results": results,
        "wall_s": time.time() - t0,
        "note": "Cheap smoke only; TIMEOUT not treated as INFEASIBLE.",
    }
    path = os.path.join(exp, "orbit_smoke.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True, default=str)
        f.write("\n")
    print(json.dumps({"path": path, "entry": entry, "n_results": len(results), "wall_s": payload["wall_s"]}, indent=2))


if __name__ == "__main__":
    main()
