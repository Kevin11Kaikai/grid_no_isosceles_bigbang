# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-14 (recovery after e09ce853 connection_failed; harvested I–L)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**

## Harvest (F077–F080) — previous in-flight, now closed
- I n64 LNS: 0 improve, stuck 112
- J avoid-S0 merge: best 134
- K n64 rem-k frozen-core: cap≤112
- L n64 full-grid free: TIMEOUT, 40M cuts, size≤112

## Closed basins (do not reopen as primary)
- S0-preserving refill snaps to 164/112
- Forbid-Rem / midset ≤139
- Non-S0 soft-165 V=84
- Intact midset 137 CAPACITY_FAIL; n64 S0 free=0
- Killed Hamming U_ids, rem2 residual, S0+1 soft grind
- Avoid-S0 / lattice / ring / rowband / LNS-from-S0 (F068–F080)

## In flight
- Newfam M–Q: forced-asymm half, empty-row Hamming, pattern grow (knight/quadratic/perm), n64 geometric Hamming, corner↔interior Hamming

## Next
1. Cheap-kill M–Q; escalate only TIMEOUT / near-cap survivors.
2. Dual-verify ≥165/113 before promote.
3. If connection/quota dies: slim handoff + push.

## Discipline
TIMEOUT ≠ INFEAS; scoped ≠ global; standing order push.
