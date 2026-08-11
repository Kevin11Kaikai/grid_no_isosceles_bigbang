# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-11 ~19:02 local  
**Phase:** LH-2 — r≤3 low-LB shells killed; r=4 pair-cover CP-SAT running; orbit type2 scoped INFEAS

## Incumbent

- n=64: **112** / n=100: **164** (unchanged, DUAL_VERIFIED)
- No promotion.

## Fresh LH-2 results

| Experiment | Result |
|---|---|
| `U_fullrem_LBle4_r2` | `INFEASIBLE_SCOPED` (128 add / 292 vars) |
| `U_fullrem_LBle4_r3` | `INFEASIBLE_SCOPED` |
| `U_exact2covers_LBle5_r2` | `INFEASIBLE_SCOPED` (40 rem / 316 add) |
| r=4 easiest-pair micro | **108/120** pairs become legal after some size-4 Rem; **0** finished 165 under capped 3-add enum |
| Orbit n100 type2 pure/defect | `INFEASIBLE` scoped (seeds 51/52) |
| Orbit n64 type0 defect 60s | `TIMEOUT` (≠ INFEAS) |

## Live next

1. CP-SAT `U_paircover4_LBle5_r4` + `U_fullrem_LBle5_r4`
2. If those INFEAS: raise Add to LB≤8 or leave baseline neighborhood (orbit enlarge / from-scratch)
3. Push checkpoint after CP-SAT lands

## Standing order

Sync to `origin/master` after meaningful checkpoints; continue loop; no Hard Stop.
