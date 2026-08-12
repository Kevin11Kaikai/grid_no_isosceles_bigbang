# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (post harvest + destroy/LNS/HS2-max)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**

## Harvest + follow-ups
| Result | Notes |
|---|---|
| pattern/grow LNS | best 133–135; no +1 (LH-F046) |
| rem3 residual | s802 max=164 incumbent; s801 TIMEOUT (LH-F045/046) |
| large destroy region MILP | always 164 (LH-F047) |
| global refill frame_d2 | **MAX_PROVED 164** (LH-F048) |
| exact-LNS from S0 | 0 improve / 30min (LH-F050) |
| HS2-delete maximize ×8 | **8/8 MAX_PROVED 164** (LH-F051) |

## Next 3
1. Joint/multi-HS deletes or non-S0 cores (grow-135 cores) with maximize — not single-HS2.  
2. Avoid killed Hamming / rem2 residual / S0+1 / stock S0-LNS.  
3. Dual-verify any ≥165.

## Discipline
TIMEOUT ≠ INFEAS; scoped ≠ global; standing order push.
