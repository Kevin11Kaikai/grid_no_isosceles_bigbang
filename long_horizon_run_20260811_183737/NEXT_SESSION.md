# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`  
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Wave3 active post-Gate2. Incumbents **112 / 164**. No legal +1. FunSearch held. C S0+1 blocked.

## Orbit R1 (TIMEOUT open, not empty)

Finished TIMEOUT size=0: s401, s641(n64), s511 partial, **s501 Type0 xlarge 60min (86k cuts)**, s521/s601 Type1 xlarge.  
**Live:** Type2 xlarge (`SCRATCH/w3_orbit_t2_xlarge.py`).  
**Next:** Type3/4 xlarge (`SCRATCH/w3_orbit_t34_xlarge.py`) then consider ≥2h Type0 or new defect policy.

## R2

Cert/cross/HS2/joint-HS micros all `INFEASIBLE_SCOPED` (LH-F015–F022). Do not reopen without new Rem/Add.

## Resume commands

```text
.venv_solver\Scripts\python.exe -u long_horizon_run_20260811_183737\SCRATCH\w3_orbit_t34_xlarge.py
```

Dual-verify any |S|≥165 before promote. Push checkpoints; no force-push; ignore `.venv_solver`.
