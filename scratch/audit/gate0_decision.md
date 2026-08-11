# Gate 0 Decision

## 1. Final verdict

**Gate 0: PASS**

Wave 1 `/multitask` (Gate 1 structural audit only) is **allowed**. Formal breakthrough search (Hamming-shell / orbit-defect / fixed-cardinality / multi-region aiming at 165/113) remains **forbidden until Gate 1 policy exists**.

## 2. Baseline dual re-verification (from `official_raw`, not status fields alone)

| Grid | Size | A | B | V | hash (raw) | matches certified | certify→scratch |
|---|---|---|---|---|---|---|---|
| n=64 | 112 | PASS | PASS | 0 | `47d42165b7804493a847e064494ef067e97bc8ac12121cd04ac19f23fee9c292` | yes | DUAL_VERIFIED |
| n=100 | 164 | PASS | PASS | 0 | `8a84216d28f5afbbbd6b06301b159eab1b57c85bb814d78dd708da2be65cbdc1` | yes | DUAL_VERIFIED |

- Integers / bounds / no duplicates: OK for both.
- Existing `results/certified/*` baselines were **not** overwritten; certify used `out_dir=scratch/audit/certify_scratch`.
- Artifact: `scratch/audit/phase0_baseline_reverify.json`

## 3. Legality / coordinate definition audit

| Topic | Conclusion |
|---|---|
| Coordinate convention | `0_to_n_minus_1` (candidate_io, certified JSON, verifiers) |
| Legality | For every pivot `b ∈ S`, squared distances from `b` to all other points of `S` are pairwise distinct |
| Pivot membership | Pivot must be in `S` |
| Directions / degenerate midpoints | Included (equal squared distance from apex; collinear midpoint is the same condition) |
| Distance arithmetic | Exact integer squared Euclidean distance only |
| Extra row/column constraints | **None** in A, B, or project docs (unused rows/cols are empirical occupancy only) |
| A vs B same proposition | **Yes** — A: per-pivot dict; B: distance matrix + sort; same mathematical claim |

No material definition mismatch found → not a FAIL.

## 4. V(S) equivalence

- Module (Main-owned): `src/verification/conflict_metric.py`
- Tests: `tests/test_conflict_metric_equivalence.py` — **12 methods, 0 failures, 0 errors**
- Seeds recorded in `scratch/audit/gate0_conflict_equivalence.json`
- Claim held on exhaustive n=4 (k≤4), random n=5/6/10/64/100, official baselines, perturbations, witness cross-check

## 5. Solver environment

| Backend | Status |
|---|---|
| Default Python 3.12.7 (Anaconda) | OK |
| `scipy.optimize.milp` | smoke PASS |
| `.venv_solver` + OR-Tools CP-SAT | smoke PASS (use venv interpreter; default env has **no** ortools) |
| candidate_io round-trip | PASS |

Artifact: `scratch/audit/gate0_environment.json`

## 6. candidate I/O

Round-trip save/load preserved points, size, `0_to_n_minus_1`, and stable sha256.

## 7. Files created or modified (Gate 0)

**Created**

- `src/verification/conflict_metric.py`
- `tests/test_conflict_metric_equivalence.py`
- `scratch/audit/phase0_baseline_reverify.json`
- `scratch/audit/gate0_conflict_equivalence.json`
- `scratch/audit/gate0_environment.json`
- `scratch/audit/gate0_decision.md` (this file)
- `scratch/audit/_gate0_reverify_baselines.py` (helper)
- `scratch/audit/_gate0_env_audit.py` (helper)
- `scratch/audit/certify_scratch/*` (non-canonical certify copies)
- `logs/lns_exact_n64_replay_9001.json` (optional new replay)

**Not modified:** verifier A/B judgment logic; baselines; `results/certified/` canonical baselines.

## 8. Commands actually run

```text
git rev-parse HEAD   # 148808f422cba7e8ca232ebb4710b84782086342
git status --short
python --version
python scratch/audit/_gate0_reverify_baselines.py
python tests/test_conflict_metric_equivalence.py
python scratch/audit/_gate0_env_audit.py
python -c "... lns_exact_run(64, SOL_64, 20s, seed=9001) ..."
```

## 9. Open issues (non-blocking for Gate 0)

- Historical `logs/lns_exact_n64_*.json` for the documented 8613-iter run remains missing; optional **new** replay `logs/lns_exact_n64_replay_9001.json` (20s, 2829 iters, size stayed 112) is explicitly `replay_not_original_8613: true` and does **not** restore historical evidence grade.
- Default Python lacks ortools; Gate 1+ CP-SAT work must use `.venv_solver\Scripts\python.exe`.
- Worktree already had unrelated dirty/untracked files; left untouched.

## 10. May enter Wave 1 `/multitask`?

**Yes — Gate 1 structural audit only** (Audit Agents A/B/C + Main policy memo).

**No** automatic start of breakthrough search or Gate 2.
