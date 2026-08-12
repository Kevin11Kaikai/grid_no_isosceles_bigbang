# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`  
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Wave3 post-Gate2. Incumbents **112/164**. **No legal +1.** FunSearch held. C S0+1 blocked.

## Done (high signal)

- Soft_core orbit types **0–6** xlarge / mega / cert_lb2: all **TIMEOUT size=0** (TIMEOUT≠INFEAS).
- `fix_core=True` Type0: **SCOPED INFEAS** (LH-F033).
- Cert Hamming / HS2 / joint-HS / cross-knn / n64 HS2: **SCOPED INFEAS** (LH-F015–F022, F035).
- rem2 residual: full involved-strip core extend **INFEASIBLE_SCOPED**; soft_core extend TIMEOUT.

## Live lead (new formulation)

**`SCRATCH/w3_rem2_core_maximize.py`** — strip top conflict pivots from V=25 rem2 soft state → legal core (~160) → maximize free adds with lazy cuts. Output: `EXPERIMENTS/W3_rem2_residual/core160_maximize.json` (+ `CANDIDATES/` if ≥165 dual-ok).

## Resume

1. Collect `core160_maximize.json`; if `best_legal_size≥165` and dual OK → certificate bundle + promote path.  
2. Else: vary strip-k / longer wall / different soft seeds with **remove≥2** (not S0+1).  
3. Do **not** replay soft Type0 orbit same-U short runs; FunSearch still held unless new structure justifies.

Push; no force-push; ignore `.venv_solver`.
