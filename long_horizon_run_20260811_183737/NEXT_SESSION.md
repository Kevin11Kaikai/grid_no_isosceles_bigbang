# NEXT_SESSION (1 page)

**Run:** `long_horizon_run_20260811_183737/`  
**Read first:** `RESEARCH_STATE.md`, `LOGS/resource_exhausted.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status (paused)

Wave3 **paused** (2026-08-12): agents e1307832 / f14150c1 **resource_exhausted**. Incumbents **112/164**. **No legal +1.** FunSearch held. C S0+1 blocked.

- rem>=2 residual family **dead** (LH-F038-F040).
- rem3 soft swap plateau best_V=42 (LH-F041).
- Spatial-block Hamming r=2: **8/8 SCOPED INFEAS** (LH-F042).
- rem3 s802 soft/partial exact extend: **SCOPED INFEAS** (LH-F043).

Do **not** start long CP-SAT / orbit / Wave3 research loops until quota is OK.

## Artifacts to reconcile (not auto-resume)

| Area | Path |
|------|------|
| rem>=3 exchange / residual | `EXPERIMENTS/W3_rem3_residual/` (`run.log`, `max_run.log`, `elite_s801_V45.json`, `elite_s802_V42.json`, `partial_extend_s802.json`, `soft_extend_s802.json`, `core_maximize_s802.json`) |
| Pattern LNS | `EXPERIMENTS/W3_pattern_lns/run.log` |
| From-scratch grow / LNS | `EXPERIMENTS/W3_from_scratch/` (`run_job.py`, `grow_v3_job.py`, logs) |
| Spatial Hamming (killed family) | `EXPERIMENTS/W3_spatial_hamming/summary.json` (reference only) |
| Dispersed Hamming (optional next) | `EXPERIMENTS/W3_dispersed_hamming/` |

SCRATCH entrypoints (venv_solver only when resuming): `SCRATCH/w3_rem3_exact_residual.py`, `SCRATCH/w3_pattern_lns.py`, `SCRATCH/w3_spatial_hamming.py`.

## Resume steps (in order)

1. Read `RESEARCH_STATE.md` + `LOGS/resource_exhausted.md` + new lines in `FAILED.md` / `PROCESS_LESSONS.md`.
2. **rem>=3 exchange results:** parse `EXPERIMENTS/W3_rem3_residual/run.log` and `max_run.log`; record s801 outcome (was in flight); confirm s802 INFEAS (LH-F043). Update `RESEARCH_STATE.md` / `FAILED.md` if s801 finished INFEAS then deprioritize rem3 residual on these elites.
3. Check pattern LNS and from-scratch logs for any FEASIBLE/legal **>=165** (n=100) or **>=113** (n=64); if found, dual-verify + certificate bundle before promote.
4. **Avoid killed / deprioritized routes:** orbit Types0-6 same-U xlarge; rem>=2 residual seeds; spatial **knn-block** Hamming U_ids (LH-F042); rem3 s802 soft/partial extend replay; C S0+1 soft; FunSearch; previously killed Hamming U_ids (see `FAILED.md`).
5. If quota allows, prefer **Dispersed Rem Hamming** or **maximize-from-pattern** over replaying spatial knn-block Rem.
6. Continue Explore -> CheapKill -> Compute -> Verify; commit + `git push origin master` (no force-push; ignore `.venv_solver`).
