# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (spatial Hamming kill + rem3 residual)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**

## Wave3 status
- Orbit Types0–6 xlarge/cert_lb2/2h: TIMEOUT size=0 (deprioritize same-U).
- rem>=2 residual: **dead** sampled seeds (LH-F038–F040).
- rem3 soft swap: plateau best_V=42 (LH-F041).
- Spatial-block Hamming r=2: **8/8 SCOPED INFEAS** (LH-F042).
- rem3 s802 soft/partial exact extend: **SCOPED INFEAS** (LH-F043); s801 in flight.
- Pattern screen: checker/modular legalize up to ~119 so far; LNS grow live.
- From-scratch grow: boundary ~134; exact LNS from ring-bias start=111 live.

## Next 3
1. Finish rem3 s801 residual; if INFEAS → deprioritize rem3 residual for these elites.
2. Pattern LNS / from-scratch exact LNS — dual-verify if ≥165.
3. Dispersed Rem Hamming or maximize-from-pattern (not knn-block Rem).

## Blocked
- C S0+1 soft; FunSearch held; killed Hamming U_ids; rem2 residual cores; spatial knn-block Hamming.

## Pause (2026-08-12 resource_exhausted)
- Wave3 agents **e1307832**, **f14150c1** terminated: esource_exhausted.
- Research **paused** pending quota; incumbents still **112/164**; **no legal +1** claimed.
- Detail: LOGS/resource_exhausted.md.
