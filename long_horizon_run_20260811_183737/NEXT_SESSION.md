# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`  
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Gate2 CLOSED. Wave3 active. Incumbents still 112/164. No legal +1.

## In flight / just finished

- **DONE TIMEOUT:** n100 Type0 enlarged s401 45min size=0; n64 Type0 enlarge s641 20min size=0.
- **RUNNING:** n100 Type0 **xlarge** s501 (320/h18/U_large, 60min); Type0 **partial** s511 (20min).
- **R2 killed:** cert/cross/HS2 micros SCOPED INFEAS (LH-F015–F020); joint-HS pairs running/next.

## Resume

1. Collect `EXPERIMENTS/W3_orbit_enlarge/long_t0_defect_s501_xlarge.json` + `partial_t0_s511.json`.
2. If TIMEOUT: next orbit policy change (larger defect, unfix core variants, Type1 xlarge) — still TIMEOUT≠INFEAS.
3. Read `EXPERIMENTS/W3_joint_hs/summary.json`; do not reopen single-HS2 family.
4. Keep C S0+1 blocked; FunSearch held.

## Standing order

Commit+push after checkpoints. No force-push. Ignore `.venv_solver`.
