# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-11 ~19:55 local  
**Remote:** synced frequently to `origin/master`  
**Phase:** LH-3 — S0-neighborhood largely exhausted at small r; pivot to far-from-S0

## Incumbent

- n=64: **112** / n=100: **164** DUAL_VERIFIED — no promotion

## Headline findings this run

1. **Wave2 V=3 elites = S0∪{q}** (remove 0 / add 1) — soft |S|=165 search never exchanged.
2. **Joint VC=4** for every easiest-16 pair → r=2 cannot co-insert two exact-2 cells.
3. **Frame Add** ring≤2 and ≤6 at r=2 with full Rem → `INFEASIBLE_SCOPED` (long runs).
4. **LB≤5 Add** dead through r=4 (fullrem / paircover).
5. Orbit n100 types **2,3,4** defect (short new seeds) → scoped INFEAS.
6. Cert-seeded r=4 exchanges: pair-legal seeds with V≈25–30; residual refill did not reach V=0 (partial, 35 trials).

## Allocation shift

| Was | Now |
|---|---|
| 40% Hamming around S0 | **15%** cleanup only |
| 15% soft fixed-card near S0 | **25%** forced far-init / from-scratch |
| 20% orbit | **30%** enlarge universes / other axis types |
| rest | critic / verify / abstraction |

## Immediate next

1. From-scratch / random-init legal set growth toward 165 (not seeded from S0+1).
2. Optional: midband long shell (TIMEOUT@120s) — one 600s attempt then drop if TIMEOUT/INFEAS.
3. Keep pushing checkpoints.

## Hard stop

Only env kill / user stop / space exhausted with certificates / full solution.
