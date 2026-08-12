# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (Wave3 started post-Gate2)  
**Remote:** `origin/master`  
**Phase:** Gate2 **PASS/CLOSED**; Wave3 ranking funded; Explore→CheapKill loop active.

## Incumbent

- n=64 **112** / n=100 **164** — no promotion; **no legal +1**

## Wave3 ranking (funded)

Canonical: `scratch/wave3/ranking_memo.md` (LH copy `WAVE3_RANKING.md`)

| Rank | Route | Status |
|---|---|---|
| R1 PRIMARY | Enlarged Type0 orbit-defect TIMEOUT | s401 45min in flight (`def220/h14`); next = xlarge 320/h18/`U_large` |
| R2 SECONDARY | Cert-driven Hamming Rem/Add outside Wave2 U_* | several new U_ids cheap-killed SCOPED INFEAS; cross-knn pilots running |
| BLOCKED | Agent C S0+1 soft grind | `scratch/wave3/agent_c_s0plus1_block.md` |
| HOLD | FunSearch | no new structure yet |

## Wave3 cheap-kill ledger (n100 r=2 unless noted)

| U_id | Status | Notes |
|---|---|---|
| `U_cert_involved_e16_Add_e56_r2` | INFEASIBLE_SCOPED | <1s; LH-F015 |
| `U_certfreq_top48_Add_LBle5_r2` | INFEASIBLE_SCOPED | ~4.5s; LH-F015 |
| `U_cert_involved_e56_Add_LBle6_r2` | INFEASIBLE_SCOPED | ~24s |
| `U_fullrem_Add_multicomm4_r2` | TIMEOUT_INCONCLUSIVE | ~9800 Add ≈ unrestricted; **deprioritized** |
| Cross-knn community shells | running | `EXPERIMENTS/W3_cross_community/` |

## Live lead (R1)

| Run | Status | Notes |
|---|---|---|
| Type0 20min s301 | TIMEOUT | 1921 rounds / 32186 cuts |
| Type1 20min s302 | TIMEOUT | 114 rounds / 19919 cuts |
| Type0 **45min** s401 | in flight | mid-checkpoints under `scratch/agent_b/checkpoints/` |
| Type0 xlarge s501 | queued | `SCRATCH/w3_orbit_enlarge_next.py` after s401 |

## Discipline

TIMEOUT ≠ INFEASIBLE; scoped INFEAS ≠ global UB; no seed grinding; dual-verify before promote.

## Next 3 actions

1. Collect s401 45min result; if TIMEOUT, launch xlarge Type0 (320/18/U_large, ≥60min).
2. Finish cross-community cheap-kills; escalate only structured TIMEOUT survivors.
3. Keep C S0+1 blocked; hold FunSearch.
