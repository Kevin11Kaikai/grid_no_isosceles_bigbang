# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Wave3. Incumbents **112/164**. No legal +1. FunSearch held. C S0+1 blocked.

## Key Wave3 outcomes

- Ranking: R1 orbit TIMEOUT; R2 cert Hamming/HS micros SCOPED INFEAS (LH-F015–F022).
- **fix_core=True → SCOPED INFEAS** (LH-F033); soft_core required for open TIMEOUT path.
- Two 2h Type0 runs TIMEOUT size=0: mega s811 (free401/h20, 121k cuts) and s901 (free361/h18, 92k cuts).

## Live

- **s841 mega+cert_lb2** 90min (`…/mega_certlb2_job.py`) — new combo U.

## Resume

1. Collect `mega_certlb2_t0_s841_90m.json`.
2. If TIMEOUT: invent new formulation (not more same soft Type0 agent_c enlargements).
3. Dual-verify any ≥165 before promote.

Push; no force-push; ignore `.venv_solver`.
