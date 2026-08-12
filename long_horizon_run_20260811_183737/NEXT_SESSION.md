# NEXT_SESSION (≤1 page)

**Run:** `long_horizon_run_20260811_183737/`
**Read:** `RESEARCH_STATE.md`, `FAILED.md`, `scratch/wave3/ranking_memo.md`

## Status

Gate2 CLOSED → Wave3 executed. Incumbents **still 112 / 164**. **No legal +1.** FunSearch held. C S0+1 blocked.

## Wave3 ranking outcomes

| Route | Result |
|---|---|
| R1 enlarged soft_core orbit (types 0–4, mega, cert_lb2) | All **TIMEOUT size=0** (not INFEAS). Largest: free401/h20 @2h, 121k cuts. |
| R1 fix_core | **SCOPED INFEAS** (LH-F033) — do not use |
| R2 cert Hamming / HS2 / joint-HS / cross-knn | **SCOPED INFEAS** (LH-F015–F022, F035) |
| C S0+1 soft grind | **BLOCKED** |

## Live

- Type5 then Type6 xlarge 30min each (`EXPERIMENTS/W3_orbit_enlarge/t56_job.py`).

## Resume priorities

1. Collect `long_t5_defect_s851_xlarge.json` / `long_t6_defect_s861_xlarge.json`.
2. If still TIMEOUT: **stop replaying soft Type0 enlargements**; invent new model (different cardinality exchange, nonlocal residual with remove≥2 outside killed U_ids, or structure not tried).
3. Dual-verify any |S|≥165 before promote / claim_registry touch.

Push checkpoints; no force-push; ignore `.venv_solver`.
