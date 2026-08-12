# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`  
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Gate2 CLOSED. Wave3 active. Incumbents 112/164. No legal +1.

## Orbit R1

| Job | Result |
|---|---|
| s401 Type0 45min def220/h14 | TIMEOUT size=0 |
| s641 n64 Type0 enlarge | TIMEOUT size=0 |
| s511 Type0 partial xlarge 20min | TIMEOUT size=0 (71759 cuts) |
| s501 Type0 xlarge 60min free361/def320/h18 | **RUNNING** (~20min mid: 68400 cuts, size=0) |
| s521 Type1 xlarge 40min | **RUNNING** |

## R2 cert micros

All cheap-killed SCOPED INFEAS: cert-involved, certfreq, cross-knn r2/r3, forced HS2 (8/8), joint HS pairs (10/10). Near-full Add TIMEOUT deprioritized. C S0+1 blocked. FunSearch held.

## Resume

1. Collect s501 + s521 finals. TIMEOUT≠INFEAS; if still open, next policy: still-larger defect / alternate symmetry / longer wall.
2. Do not reopen LH-F015–F022 U_ids without new Rem/Add reason.
3. Dual-verify any size≥165 before promote.

## Standing order

Commit+push checkpoints. No force-push. Ignore `.venv_solver`.
