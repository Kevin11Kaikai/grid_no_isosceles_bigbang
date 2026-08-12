# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`  
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Wave3 post-Gate2. Incumbents **112/164**. No legal +1. FunSearch held. C S0+1 blocked.

## Live now

1. **s801** Type0 `cert_lb2` ranking (`SCRATCH/w3_orbit_certlb2_t0.py`, universe `…_rkcert_lb2`, ~45min budget).  
2. **s811** Type0 mega 2h (`SCRATCH/w3_orbit_t0_mega_2h.py`, max_extra=360, halo=20, seed **811** — not 801).

## Finished Wave3 orbit (all TIMEOUT size=0)

Types 0–4 xlarge/partial/n64 enlarge — see `EXPERIMENTS/W3_orbit_enlarge/` and `RESEARCH_STATE.md` table. TIMEOUT ≠ INFEASIBLE.

## R2 killed

LH-F015–F022 (cert/cross/HS2/joint-HS). Do not reopen without new Rem/Add.

## Resume

```text
# after live jobs finish:
# read EXPERIMENTS/W3_orbit_enlarge/mega_t0_defect_s811_2h.json
# and cert_lb2 output under EXPERIMENTS/W3_orbit_enlarge/
```

If FEASIBLE → dual verifiers + certificate bundle before promote.  
If TIMEOUT → change ranking/core policy; do not grind same U.

Push checkpoints; no force-push; ignore `.venv_solver`.
