# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-14 (sealed tournament wave1+2 closed; no beat)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**
- Best dual-verified non-incumbent: **147** (`best_asymm_west.json`, hash `0c03a317…`)

## Finite obstructions vs official S0
- n100 frozen-core r=2 cannot +1 (PROVED.md §6)
- n64 exhaustive k=1 and k=2: frozen-core r=1/r=2 cannot +1 (PROVED.md §8–9)

## This recovery wave (F077–F101)
- Hamming empty-row / interior / n64 geom r≤4: scoped INFEAS (N/Q/P)
- Larger-r Hamming: mixed INFEAS/TIMEOUT, no 165 (R)
- Pattern grow ≤135 CAPACITY_FAIL (O)
- 147 singleton-maximal; LNS 0-improve; shallow destroy snaps to 147 (M3/M4/F097)
- n64 asymm-keepbl: dual-OK **88**, cap=186 (S) — live

## Live
- **S2** n64 forced-asymm keepbl maximize (unsealed; from 88, cap 186) if still in flight
- Sealed-S0 tournament closed for this budget: n64 **90**, n100 **137** (LH-F102); next sealed branch = longer T-K keep55-style, not S0 Hamming

## Discipline
TIMEOUT ≠ INFEAS; scoped ≠ global; standing order push.
