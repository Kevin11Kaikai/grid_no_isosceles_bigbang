# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`  
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Wave3. Incumbents **112/164**. No legal +1. FunSearch held. C S0+1 blocked.
rem2 residual family dead (LH-F038–F040). rem3 soft swap plateau best_V=42 (LH-F041).

## Live (venv_solver only)

1. `SCRATCH/w3_rem3_exact_residual.py` → `EXPERIMENTS/W3_rem3_residual/`
2. `SCRATCH/w3_pattern_lns.py` → `EXPERIMENTS/W3_pattern_lns/`
3. `EXPERIMENTS/W3_from_scratch/run_job.py` (exact LNS from non-S0 starts)
4. `EXPERIMENTS/W3_from_scratch/grow_v3_job.py` + orphan grow_v2 partial
5. `SCRATCH/w3_spatial_hamming.py` → `EXPERIMENTS/W3_spatial_hamming/` (new R2 U_ids)

## Resume

1. If any FEASIBLE/legal ≥165 → dual-verify + certificate bundle before promote.
2. Read rem3 residual / pattern / spatial summaries; log FAILED with scoped labels.
3. Avoid replaying orbit same-U, rem2 residual, S0+1 soft, killed Hamming U_ids.
4. Continue Explore→CheapKill→Compute→Verify.

Push; no force-push; ignore `.venv_solver`.
