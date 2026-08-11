# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-11 ~19:35 local  
**Phase:** LH-3 — frame Add pools killed at r=2; V3 elites exposed as baseline+1; forced-exchange live

## Incumbent

- n=64: **112** / n=100: **164** — unchanged, no promotion

## Critical discovery

All 9 Wave2 `n100_V3` elites have **hamming_remove=0, hamming_add=1** — they are exactly `S0 ∪ {q}` with V=3. Soft fixed-card search never left the single-insertion basin (matches Gate1 min ΔV=3).

## LH-2 shell kills (scoped)

| Universe | r | Status |
|---|---:|---|
| U_fullrem_LBle4 | 2,3 | INFEAS |
| U_fullrem_LBle5 | 4 | INFEAS |
| U_fullrem_frameR2 | 2 (long), 4 | INFEAS |
| U_fullrem_frameR6 | 2 (long) | INFEAS |
| U_exact2covers_LBle5 | 2 | INFEAS |
| midband10–26 | 2,4 @120s | TIMEOUT |
| n64 exact1covers | 1 | INFEAS |

## Live next

1. Interpret forced-exchange fixed-card (`LH3_forced_exchange`).
2. Longer midband / full-empty r=2 if information-positive.
3. Orbit types 3–6 short smokes; avoid baseline+1 soft search.

## Standing order

Push checkpoints to `origin/master`; continue; no Hard Stop.
