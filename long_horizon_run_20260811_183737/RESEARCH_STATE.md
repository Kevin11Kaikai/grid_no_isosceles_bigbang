# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (random large Rem harvest)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**

## Hard scoped facts (S0-related)
| Setting | Result |
|---|---|
| HS2 / joint HS2 delete | MAX_PROVED 164 |
| certfreq Rem ≤64 | MAX_PROVED 164 |
| frame_d2 global refill | MAX_PROVED 164 |
| random Rem 80/100 maximize | TIMEOUT best=164 incumbent (F059) |

## Non-S0
- Grow/LNS/parity/midset/union: plateau ≤138; no +1

## Next 3
1. Longer escalate prove≥165 under Rem80/100 cores (TIMEOUT≠INFEAS) OR leave S0 basin via forced-forbidden incumbent cells.  
2. Fixed-card V-minimize at 165 from non-S0 warm starts (not S0+1 soft grind).  
3. Dual-verify before any promote.

## Discipline
TIMEOUT ≠ INFEAS; scoped ≠ global; standing order push.
