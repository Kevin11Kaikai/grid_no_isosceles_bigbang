"""Gate 0 environment / I/O smoke (writes scratch/audit/gate0_environment.json)."""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.structures.candidate_io import load_candidate, save_candidate, sha256_of_points


def main() -> None:
    pts = [[1, 2], [3, 4], [0, 0]]
    os.makedirs("scratch/audit", exist_ok=True)
    path = "scratch/audit/_io_roundtrip_tmp.json"
    save_candidate(path, 5, pts, "gate0_io_smoke", 0, None)
    rec = load_candidate(path)
    h1 = sha256_of_points(pts)
    h2 = sha256_of_points(rec["points"])
    io_ok = (
        h1 == h2
        and rec["size"] == 3
        and rec["coordinate_convention"] == "0_to_n_minus_1"
    )

    milp_ok = False
    milp_err = None
    try:
        import numpy as np
        from scipy.optimize import Bounds, LinearConstraint, milp

        c = -np.ones(2)
        bounds = Bounds(0, 1)
        res = milp(
            c=c,
            integrality=np.ones(2),
            bounds=bounds,
            constraints=LinearConstraint([[1, 1]], -np.inf, 1),
        )
        milp_ok = bool(res.success)
    except Exception as e:
        milp_err = str(e)

    ortools_ok = False
    ortools_err = None
    venv_py = os.path.join(".venv_solver", "Scripts", "python.exe")
    try:
        code = (
            "from ortools.sat.python import cp_model; "
            "m=cp_model.CpModel(); x=m.NewBoolVar('x'); m.Maximize(x); "
            "s=cp_model.CpSolver(); st=s.Solve(m); print(int(st), s.Value(x))"
        )
        r = subprocess.run(
            [venv_py, "-c", code],
            capture_output=True,
            text=True,
            timeout=30,
        )
        ortools_ok = r.returncode == 0 and "1" in r.stdout
        if not ortools_ok:
            ortools_err = (r.stdout or "") + (r.stderr or "")
    except Exception as e:
        ortools_err = str(e)

    default_has_ortools = False
    try:
        import ortools  # noqa: F401

        default_has_ortools = True
    except Exception:
        default_has_ortools = False

    env = {
        "python_default": sys.version,
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "venv_solver_exists": os.path.isdir(".venv_solver"),
        "venv_solver_python": venv_py if os.path.isfile(venv_py) else None,
        "scipy_milp_smoke": {"ok": milp_ok, "error": milp_err},
        "ortools_cpsat_smoke": {
            "ok": ortools_ok,
            "error": ortools_err,
            "interpreter": ".venv_solver",
        },
        "candidate_io_roundtrip": {"ok": io_ok, "hash": h1, "path": path},
        "default_python_has_ortools": default_has_ortools,
        "note": "OR-Tools is available via .venv_solver; default Anaconda python may lack ortools. MILP via scipy is available in default python.",
    }
    out = "scratch/audit/gate0_environment.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(env, f, indent=2)
    print(json.dumps(env, indent=2))


if __name__ == "__main__":
    main()
