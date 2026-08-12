# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`  
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Wave3. Incumbents **112/164**. No legal +1. FunSearch held. C S0+1 blocked.

## Killed / closed this Wave3

- Soft_core orbit Types **0–6** xlarge/mega/cert_lb2: TIMEOUT size=0 (deprioritize same-U).  
- `fix_core` Type0: SCOPED INFEAS (LH-F033).  
- Cert Hamming / HS2 / joint-HS / cross-knn: SCOPED INFEAS.  
- **rem≥2 residual** soft cores: capacity-fail / INFEAS (LH-F038–F040) — **family dead for sampled seeds**.

## Live

**`SCRATCH/w3_rem3_exchange.py`** → `EXPERIMENTS/W3_rem3_exchange/forced_exchange_rem3.json` (forced rem≥3 fixed-card min-V; not S0+1).

## Resume

1. Read rem3 summary; if V=0 → dual-verify + certificate bundle.  
2. If best_V>0: try rem≥3 with nonlocal free / exact residual on new elites (not rem2 cores).  
3. Avoid replaying orbit same-U and rem2 residual.

Push; no force-push; ignore `.venv_solver`.
