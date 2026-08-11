"""Wave-2 Agent A: Hamming-shell CP-SAT with iterative lazy conflict cuts.

Model (around baseline S0 of size k, seeking |S|=k+1):
  |S0 \\ S| = r
  |S \\ S0| = r + 1

Universe restriction: Rem ⊆ S0 (removable), Add ⊆ grid\\S0 (addable).
Fixed complement F = S0 \\ Rem is always present.
Variables: keep[p] for p in Rem; add[q] for q in Add.
Cardinality:
  sum_p (1 - keep[p]) = r
  sum_q add[q] = r + 1

Isosceles constraints are added lazily from oracle witnesses on each
incumbent reconstruction. Every cut is derived from a concrete witness
triple; no cut is invented without a witness.

Scoped INFEASIBLE/OPTIMAL is NEVER a global upper bound on C(n).
TIMEOUT is never reported as INFEASIBLE.

Requires OR-Tools via `.venv_solver/Scripts/python.exe`.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.structures.candidate_io import sha256_of_points  # noqa: E402
from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import (  # noqa: E402
    verify_independent,
)

Point = Tuple[int, int]

EXPECTED_HASHES = {
    ("n100", "U_small"): "0e3710582f4533b788ccfbb58f5b69d2b92ce5571041ad53688cda601d4caac2",
    ("n100", "U_small_r2"): "a100c8b65096256676e7959491c95b5868d3a71c7b43bdf0f27609e382d50e88",
}


def default_num_workers(logical_cpus: Optional[int] = None) -> int:
    """Cap Agent A at ~25% of logical cores (A+B+C <= 75%, leave >=2 free)."""
    n = int(logical_cpus if logical_cpus is not None else os.cpu_count() or 4)
    leave_free = 2
    usable = max(1, n - leave_free)
    per_agent = max(1, (usable * 25) // 100)  # ~25% of usable, or of total
    # Prefer explicit 25% of logical count when that still leaves >=2 free.
    cand = max(1, n // 4)
    if 3 * cand <= n - leave_free:
        return cand
    return max(1, min(per_agent, (n - leave_free) // 3))


def universe_hash(removable: Sequence[Sequence[int]], addable: Sequence[Sequence[int]]) -> str:
    """Gate-1 Main recipe: sha256(json({'rem':sorted tuples,'add':sorted tuples}))."""
    canon = json.dumps(
        {
            "rem": sorted(map(tuple, removable)),
            "add": sorted(map(tuple, addable)),
        },
        separators=(",", ":"),
    )
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _as_points(seq: Sequence[Sequence[int]]) -> List[Point]:
    return [(int(p[0]), int(p[1])) for p in seq]


def _sq_dist(a: Point, b: Point) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def load_policy_universe(
    n: int,
    u_id: str,
    diagnostics_path: str = "scratch/audit/agent_c/universe_halo_diagnostics.json",
    consistency_path: str = "scratch/audit/gate1_consistency_check.json",
) -> Tuple[List[Point], List[Point], str]:
    """Return (removable, addable, universe_hash) for a policy U_id."""
    with open(diagnostics_path, "r", encoding="utf-8") as f:
        diag = json.load(f)
    key = f"n{n}"
    if u_id == "U_small_r2":
        if n != 100:
            raise ValueError("U_small_r2 is defined only for n=100")
        with open(consistency_path, "r", encoding="utf-8") as f:
            g1 = json.load(f)
        rem = _as_points(
            diag["baselines"]["n100"]["universes"]["U_medium"]["removable_baseline_points"]
        )
        e16 = _as_points(g1["n100_deletion_bound"]["easiest_16_qs_exact_min_deletions_2"])
        add_small = _as_points(
            diag["baselines"]["n100"]["universes"]["U_small"]["addable_unselected_points"]
        )
        add = sorted(set(e16) | set(add_small))
    else:
        u = diag["baselines"][key]["universes"][u_id]
        rem = _as_points(u["removable_baseline_points"])
        add = _as_points(u["addable_unselected_points"])
    h = universe_hash(rem, add)
    expected = EXPECTED_HASHES.get((key, u_id))
    if expected is not None and h != expected:
        raise ValueError(
            f"universe hash mismatch for {key}/{u_id}: got {h}, expected {expected}"
        )
    return rem, add, h


def reconstruct_S(
    s0: Sequence[Point],
    removable: Sequence[Point],
    addable: Sequence[Point],
    keep_rem: Sequence[bool],
    take_add: Sequence[bool],
) -> List[Point]:
    rem_set = set(map(tuple, removable))
    s0_set = set(map(tuple, s0))
    if not rem_set <= s0_set:
        raise ValueError("removable must be subset of S0")
    fixed = s0_set - rem_set
    kept = {tuple(p) for p, k in zip(removable, keep_rem) if k}
    added = {tuple(p) for p, t in zip(addable, take_add) if t}
    return sorted(fixed | kept | added)


def shell_cardinalities(s0: Sequence[Point], s: Sequence[Point]) -> Tuple[int, int]:
    s0_set = set(map(tuple, s0))
    s_set = set(map(tuple, s))
    removed = len(s0_set - s_set)
    added = len(s_set - s0_set)
    return removed, added


def find_witness_cuts(
    points: Sequence[Point],
) -> List[Tuple[Point, Point, Point]]:
    """Return witness triples (pivot, a, b) with |pivot-a|^2 = |pivot-b|^2."""
    cuts: List[Tuple[Point, Point, Point]] = []
    pts = [tuple(p) for p in points]  # type: ignore[misc]
    for pivot in pts:
        groups: Dict[int, List[Point]] = {}
        for q in pts:
            if q == pivot:
                continue
            groups.setdefault(_sq_dist(pivot, q), []).append(q)  # type: ignore[arg-type]
        for members in groups.values():
            if len(members) < 2:
                continue
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    a, b = members[i], members[j]
                    # canonical order for set membership of cuts
                    trip = tuple(sorted([pivot, a, b]))  # type: ignore[arg-type]
                    cuts.append((trip[0], trip[1], trip[2]))  # type: ignore[misc]
    # unique
    return sorted(set(cuts))


def dual_verify(points: Sequence[Point], n: int) -> dict:
    pts = [tuple(p) for p in points]
    ok_a, wit_a = is_legal_pivot_method(pts, n)  # type: ignore[arg-type]
    ok_b, wit_b = verify_independent(pts, n)
    v = conflict_count(pts, n)  # type: ignore[arg-type]
    return {
        "oracle_legal": bool(ok_a),
        "oracle_witness": wit_a if not ok_a else None,
        "independent_legal": bool(ok_b),
        "independent_meta": wit_b if not ok_b else None,
        "V": int(v),
        "size": len(pts),
        "points_hash": sha256_of_points(pts),
    }


def atomic_write_json(path: str, obj: object) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        prefix=".tmp_", suffix=".json", dir=os.path.dirname(path) or "."
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=2, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


@dataclass
class Scope:
    n: int
    r: int
    u_id: str
    universe_hash: str
    halo: str = "none"
    symmetry_mode: str = "asymmetric"
    time_limit_s: float = 0.0
    seed: int = 0

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "r": self.r,
            "U_id": self.u_id,
            "universe_hash": self.universe_hash,
            "halo": self.halo,
            "symmetry_mode": self.symmetry_mode,
            "time_limit_s": self.time_limit_s,
            "seed": self.seed,
        }


@dataclass
class ShellResult:
    status: str  # FEASIBLE_LEGAL | INFEASIBLE_SCOPED | TIMEOUT_INCONCLUSIVE | ERROR
    points: Optional[List[Point]] = None
    meta: dict = field(default_factory=dict)


def hamming_shell_search(
    n: int,
    s0: Sequence[Point],
    removable: Sequence[Point],
    addable: Sequence[Point],
    r: int,
    time_budget_s: float,
    seed: int = 1,
    u_id: str = "custom",
    universe_hash_str: Optional[str] = None,
    per_round_time_limit_s: float = 30.0,
    num_workers: Optional[int] = None,
    symmetry_mode: str = "asymmetric",
    max_cuts_per_round: int = 50000,
    checkpoint_path: Optional[str] = None,
    checkpoint_every_s: float = 300.0,
    git_commit: Optional[str] = None,
) -> ShellResult:
    """Feasibility search for a legal Hamming-shell +1 set under Rem/Add.

    Returns scoped status only. INFEASIBLE_SCOPED means infeasible under the
    declared (n,r,U) model with the accumulated cut set — if the cut set is
    incomplete this is still sound for infeasibility of the true model
    (fewer constraints ⇒ larger region; INFEAS under subset ⇒ INFEAS under full).
    """
    try:
        from ortools.sat.python import cp_model
    except ImportError as e:
        return ShellResult(
            status="ERROR",
            meta={"error": f"ortools not available: {e}", "hint": "use .venv_solver"},
        )

    rem = _as_points(removable)
    add = _as_points(addable)
    s0_pts = _as_points(s0)
    s0_set = set(s0_pts)
    rem_set = set(rem)
    add_set = set(add)
    if len(rem) != len(rem_set) or len(add) != len(add_set):
        return ShellResult(status="ERROR", meta={"error": "duplicate points in Rem/Add"})
    if not rem_set <= s0_set:
        return ShellResult(status="ERROR", meta={"error": "Rem not subset of S0"})
    if add_set & s0_set:
        return ShellResult(status="ERROR", meta={"error": "Add intersects S0"})
    if rem_set & add_set:
        return ShellResult(status="ERROR", meta={"error": "Rem intersects Add"})
    if r < 1:
        return ShellResult(status="ERROR", meta={"error": "r must be >= 1"})
    if r > len(rem):
        return ShellResult(status="ERROR", meta={"error": "r exceeds |Rem|"})
    if r + 1 > len(add):
        return ShellResult(status="ERROR", meta={"error": "r+1 exceeds |Add|"})

    uhash = universe_hash_str or universe_hash(rem, add)
    workers = int(num_workers if num_workers is not None else default_num_workers())
    fixed = s0_set - rem_set
    k = len(s0_pts)
    target_size = k + 1

    # Optional symmetry: force central-180 paired keeps on Rem when both present.
    partner = lambda p: (n - 1 - p[0], n - 1 - p[1])
    rem_index = {p: i for i, p in enumerate(rem)}
    add_index = {p: i for i, p in enumerate(add)}

    # Cuts stored as frozenset of variable keys: ("k", i) keep, ("a", j) add,
    # plus an integer constant_ones for fixed points in the triple.
    # Constraint: sum(vars) + constant_ones <= 2.
    Cut = Tuple[frozenset, int]
    cuts: Set[Cut] = set()

    def encode_triple(a: Point, b: Point, c: Point) -> Optional[Cut]:
        const = 0
        vars_: List[Tuple[str, int]] = []
        for p in (a, b, c):
            if p in fixed:
                const += 1
            elif p in rem_index:
                vars_.append(("k", rem_index[p]))
            elif p in add_index:
                vars_.append(("a", add_index[p]))
            else:
                # Point outside model cannot appear in a reconstructed S.
                return None
        if const > 2:
            # Impossible selection (would require fixed illegal triple); S0 legal ⇒ never.
            return None
        return (frozenset(vars_), const)

    t0 = time.time()
    last_ckpt = t0
    rounds = 0
    round_log: List[dict] = []
    best_illegal: Optional[List[Point]] = None
    best_illegal_v: Optional[int] = None
    time_to_best_illegal: Optional[float] = None
    legal_points: Optional[List[Point]] = None
    status_out = "TIMEOUT_INCONCLUSIVE"

    scope = Scope(
        n=n,
        r=r,
        u_id=u_id,
        universe_hash=uhash,
        symmetry_mode=symmetry_mode,
        time_limit_s=time_budget_s,
        seed=seed,
    )

    def checkpoint(force: bool = False) -> None:
        nonlocal last_ckpt
        now = time.time()
        if checkpoint_path and (force or now - last_ckpt >= checkpoint_every_s):
            payload = {
                "scope": scope.as_dict(),
                "git_commit": git_commit,
                "rounds": rounds,
                "n_cuts": len(cuts),
                "status_so_far": status_out,
                "wall_time_s": now - t0,
                "best_illegal_V": best_illegal_v,
                "time_to_best_illegal_s": time_to_best_illegal,
                "round_log_tail": round_log[-20:],
            }
            atomic_write_json(checkpoint_path, payload)
            last_ckpt = now

    while time.time() - t0 < time_budget_s:
        rounds += 1
        model = cp_model.CpModel()
        keep = [model.NewBoolVar(f"k{i}") for i in range(len(rem))]
        take = [model.NewBoolVar(f"a{i}") for i in range(len(add))]

        # |S0\\S|=r and |S\\S0|=r+1
        model.Add(sum(keep) == len(rem) - r)
        model.Add(sum(take) == r + 1)

        if symmetry_mode == "symmetric":
            for p, i in rem_index.items():
                q = partner(p)
                if q in rem_index and rem_index[q] > i:
                    model.Add(keep[i] == keep[rem_index[q]])
            for p, i in add_index.items():
                q = partner(p)
                if q in add_index and add_index[q] > i:
                    model.Add(take[i] == take[add_index[q]])

        for vars_fs, const in cuts:
            expr = []
            for kind, idx in vars_fs:
                expr.append(keep[idx] if kind == "k" else take[idx])
            model.Add(sum(expr) + const <= 2)

        # Seed-dependent random objective diversifies incumbents among the
        # current lazy relaxation (feasibility-only would return the same
        # witness loop every seed). Does not change the feasible region.
        import random as _random

        rng_obj = _random.Random(int(seed) * 1000003 + rounds)
        weights_k = [rng_obj.randint(1, 1000) for _ in keep]
        weights_a = [rng_obj.randint(1, 1000) for _ in take]
        model.Maximize(
            sum(weights_k[i] * keep[i] for i in range(len(keep)))
            + sum(weights_a[i] * take[i] for i in range(len(take)))
        )

        solver = cp_model.CpSolver()
        remaining = max(0.5, time_budget_s - (time.time() - t0))
        solver.parameters.max_time_in_seconds = min(per_round_time_limit_s, remaining)
        solver.parameters.random_seed = int(seed) + rounds
        solver.parameters.num_search_workers = workers
        status = solver.Solve(model)
        status_name = solver.StatusName(status)
        elapsed = time.time() - t0

        if status == cp_model.INFEASIBLE:
            status_out = "INFEASIBLE_SCOPED"
            round_log.append(
                {
                    "round": rounds,
                    "solver_status": status_name,
                    "n_cuts": len(cuts),
                    "t": elapsed,
                }
            )
            checkpoint(force=True)
            return ShellResult(
                status=status_out,
                meta={
                    "scope": scope.as_dict(),
                    "git_commit": git_commit,
                    "rounds": rounds,
                    "final_cuts": len(cuts),
                    "wall_time_s": elapsed,
                    "num_workers": workers,
                    "round_log": round_log,
                    "claim_note": (
                        "INFEASIBLE under declared scope only; not a global upper bound"
                    ),
                    "best_illegal_V": best_illegal_v,
                    "time_to_best_illegal_s": time_to_best_illegal,
                },
            )

        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            # TIMEOUT / UNKNOWN mid-round
            round_log.append(
                {
                    "round": rounds,
                    "solver_status": status_name,
                    "n_cuts": len(cuts),
                    "t": elapsed,
                }
            )
            status_out = "TIMEOUT_INCONCLUSIVE"
            checkpoint(force=True)
            break

        keep_bits = [solver.Value(keep[i]) == 1 for i in range(len(rem))]
        take_bits = [solver.Value(take[i]) == 1 for i in range(len(add))]
        selected = reconstruct_S(s0_pts, rem, add, keep_bits, take_bits)
        removed, added = shell_cardinalities(s0_pts, selected)
        assert removed == r and added == r + 1, (removed, added, r)
        assert len(selected) == target_size

        witnesses = find_witness_cuts(selected)
        v = conflict_count(selected, n)

        round_info = {
            "round": rounds,
            "solver_status": status_name,
            "selected_size": len(selected),
            "V": v,
            "n_witness_cuts": len(witnesses),
            "n_cuts_total": len(cuts),
            "t": elapsed,
        }
        round_log.append(round_info)

        if best_illegal_v is None or v < best_illegal_v:
            best_illegal_v = v
            best_illegal = selected
            time_to_best_illegal = elapsed

        if not witnesses:
            # Zero witnesses ⇒ should be legal; dual-check.
            ver = dual_verify(selected, n)
            if not (ver["oracle_legal"] and ver["independent_legal"] and ver["V"] == 0):
                return ShellResult(
                    status="ERROR",
                    meta={
                        "error": "MODEL_BUG_zero_witness_but_illegal",
                        "verification": ver,
                        "scope": scope.as_dict(),
                        "round_log": round_log,
                    },
                )
            legal_points = selected
            status_out = "FEASIBLE_LEGAL"
            checkpoint(force=True)
            return ShellResult(
                status=status_out,
                points=legal_points,
                meta={
                    "scope": scope.as_dict(),
                    "git_commit": git_commit,
                    "rounds": rounds,
                    "final_cuts": len(cuts),
                    "wall_time_s": time.time() - t0,
                    "num_workers": workers,
                    "round_log": round_log,
                    "verification": ver,
                    "points_hash": ver["points_hash"],
                    "time_to_best_s": time.time() - t0,
                },
            )

        added_cuts = 0
        for trip in witnesses[:max_cuts_per_round]:
            enc = encode_triple(*trip)
            if enc is None:
                continue
            if enc not in cuts:
                cuts.add(enc)
                added_cuts += 1
        round_info["cuts_added"] = added_cuts
        if added_cuts == 0:
            # All witnesses mapped to cuts already present — should not happen.
            return ShellResult(
                status="ERROR",
                meta={
                    "error": "MODEL_BUG_no_new_cuts_from_witnesses",
                    "witnesses_sample": [list(map(list, w)) for w in witnesses[:5]],
                    "scope": scope.as_dict(),
                    "round_log": round_log,
                },
            )
        checkpoint()

    checkpoint(force=True)
    return ShellResult(
        status=status_out,
        points=None,
        meta={
            "scope": scope.as_dict(),
            "git_commit": git_commit,
            "rounds": rounds,
            "final_cuts": len(cuts),
            "wall_time_s": time.time() - t0,
            "num_workers": workers,
            "round_log": round_log,
            "best_illegal_V": best_illegal_v,
            "time_to_best_illegal_s": time_to_best_illegal,
            "best_illegal_points": [list(p) for p in best_illegal] if best_illegal else None,
            "claim_note": "TIMEOUT is not INFEASIBLE; scope inconclusive",
        },
    )


def append_manifest(path: str, record: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hamming-shell CP-SAT pilot")
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--r", type=int, required=True)
    parser.add_argument("--u-id", type=str, required=True)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--time-budget-s", type=float, default=300.0)
    parser.add_argument("--per-round-s", type=float, default=30.0)
    parser.add_argument("--symmetry-mode", type=str, default="asymmetric")
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--checkpoint", type=str, default=None)
    parser.add_argument("--manifest", type=str, default="scratch/agent_a/manifest.jsonl")
    args = parser.parse_args()

    from data.baselines.official_raw import SOL_64, SOL_100

    s0 = SOL_100 if args.n == 100 else SOL_64
    rem, add, uhash = load_policy_universe(args.n, args.u_id)
    try:
        import subprocess

        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        commit = None

    ckpt = args.checkpoint or args.out.replace(".json", ".ckpt.json")
    t_wall0 = time.time()
    result = hamming_shell_search(
        n=args.n,
        s0=s0,
        removable=rem,
        addable=add,
        r=args.r,
        time_budget_s=args.time_budget_s,
        seed=args.seed,
        u_id=args.u_id,
        universe_hash_str=uhash,
        per_round_time_limit_s=args.per_round_s,
        num_workers=args.workers,
        symmetry_mode=args.symmetry_mode,
        checkpoint_path=ckpt,
        git_commit=commit,
    )
    out = {
        "status": result.status,
        "points": [list(p) for p in result.points] if result.points else None,
        "meta": result.meta,
        "command": " ".join(sys.argv),
        "wall_time_s": time.time() - t_wall0,
        "universe_hash": uhash,
        "n_rem": len(rem),
        "n_add": len(add),
        "n_vars": len(rem) + len(add),
    }
    atomic_write_json(args.out, out)
    append_manifest(
        args.manifest,
        {
            "event": "hamming_shell_run",
            "out": args.out,
            "status": result.status,
            "n": args.n,
            "r": args.r,
            "U_id": args.u_id,
            "seed": args.seed,
            "universe_hash": uhash,
            "wall_time_s": out["wall_time_s"],
            "git_commit": commit,
        },
    )
    print(json.dumps({"status": result.status, "out": args.out, "uhash": uhash}, indent=2))
