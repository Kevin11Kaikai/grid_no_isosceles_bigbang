# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`  
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Wave3 post-Gate2. Incumbents **112/164**. No legal +1. FunSearch held. C S0+1 blocked.

## Live

- **s811 Type0 mega 2h** (`SCRATCH/w3_orbit_t0_mega_2h.py`, 360/h20) — still running (~40min in / 2h).  
- **s821 Type1 cert_lb2** 30min — launched after s801 TIMEOUT.

## Just finished

- **s801 Type0 cert_lb2** 45min → **TIMEOUT size=0** (50113 cuts; universe `…_rkcert_lb2`).  
- Types 0–4 xlarge/partial all TIMEOUT size=0 (see RESEARCH_STATE).

## R2

LH-F015–F022 scoped INFEAS (cert/cross/HS micros). Do not reopen.

## Resume

1. Collect `EXPERIMENTS/W3_orbit_enlarge/mega_t0_defect_s811_2h.json` + `certlb2_t1_defect_s821.json`.  
2. FEASIBLE → dual-verify + certificate bundle.  
3. Else: new ranking/core policy (not same U); keep FunSearch held.

Push checkpoints; no force-push; ignore `.venv_solver`.
