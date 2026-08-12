# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (midset LNS; grow-union running)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**

## Strong scoped (S0 basins)
- HS2 / joint HS2 / certfreq Rem / frame_d2 → **MAX_PROVED 164** (=incumbent)

## Non-S0 constructions
- Grow/pattern LNS ≤135; grow-destroy / parity ≤138; midset LNS stuck 137 (F056)
- Parity 30m TIMEOUT≠proved max

## In flight
- Grow-union universe maximize (multi-grow defect pool + S0 cells)

## Next
1. Harvest grow-union; if plateau ≪165, try new universes (not S0-subset cores).  
2. Avoid killed Hamming/rem2/S0+1/HS2-keep-S0.  
3. Dual-verify before promote.

## Discipline
TIMEOUT ≠ INFEAS; scoped ≠ global; standing order push.
