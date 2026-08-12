# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Wave3 post-Gate2. Incumbents **112/164**. No legal +1. FunSearch held. C S0+1 blocked.

## Major result

**s811 Type0 mega 2h** (free401/def360/h20) → **TIMEOUT size=0** (121106 cuts). Still TIMEOUT≠INFEASIBLE.

## Live

- **s901 Type0 2h** (parallel; free361/h18 agent_c) — still running (~85min).

## Finished (all TIMEOUT size=0 unless noted)

Types 0–4 xlarge; cert_lb2 t0/t1; partial; n64 enlarge; mega s811. R2 Hamming/HS micros SCOPED INFEAS (LH-F015–F022).

## Resume

1. Collect s901 final.
2. If TIMEOUT: **new formulation** (not more same-U 30–60min) — e.g. different defect_rank, unfixed-core variants, or residual nonlocal exact with remove≥2 outside killed U_ids.
3. Dual-verify any |S|≥165 before promote.

Push checkpoints; no force-push; ignore `.venv_solver`.
