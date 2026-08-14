# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-14 (F106 n64 matching closed; no +1)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**
- Best dual-verified non-incumbent n100: **147** (`best_asymm_west.json`)
- Best dual-verified non-incumbent n64 this wave: **91** (`best_n64_asymm.json`)

## Finite obstructions vs official S0
- n100 frozen-core r=2 cannot +1 (PROVED.md §6)
- n64 exhaustive k=1 and k=2: frozen-core r=1/r=2 cannot +1 (PROVED.md §8–9)

## Closed this recovery (do not reopen as primary)
- Hamming N/Q/P r≤4 INFEAS; R mixed TIMEOUT
- Pattern grow O ≤135 CAPACITY_FAIL
- 147 singleton-maximal; LNS 0-improve; shallow destroy snaps (M3/M4/F097)
- n64-91: extra LNS 0-improve (F104); destroy snaps / under-cap (F105)
- n64 keepbl matching/drop: cap up to 750, legal sizes **≤90** (F106) — did not beat 91

## Next (if continuing)
- Change symmetry type (official notebook 7-axis), not another 180° matching
- Dual-verify ≥113/165 before promote

## Discipline
TIMEOUT ≠ INFEAS; scoped ≠ global; standing order push.
