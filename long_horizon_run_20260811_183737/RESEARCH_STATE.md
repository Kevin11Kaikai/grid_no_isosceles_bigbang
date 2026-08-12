# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (non-S0 fixed-card)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**; no promotion

## Picture
1. **S0-preserving** rem/refill (HS2, joint HS2, certfreq, frame_d2, random Rem without blacklist) → recover incumbent / MAX_PROVED 164
2. **Forbid-Rem** (blacklist deleted) → leave basin; best legal ~139 TIMEOUT; certfreq60 forbid MAX_PROVED 134
3. **Non-S0 fixed-card** from forbid midset: greedy pad V=84 stuck 30m (F063); naive pad V=364 (F062)

## In flight
- Exact-repair MILP loop on padded165 (`W3_nons0_fixedcard`)

## Next
1. Harvest exact-repair; if V stuck high, try longer / different destroy_k or abandon this midset.  
2. New constructions not S0-subset cores.  
3. Dual-verify before any ≥165.

## Discipline
TIMEOUT ≠ INFEAS; scoped ≠ global; standing order push.
