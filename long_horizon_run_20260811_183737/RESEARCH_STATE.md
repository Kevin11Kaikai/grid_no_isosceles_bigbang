# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 ~00:55 local  
**Remote:** `origin/master` (standing-order pushes active)  
**Phase:** LH-3/4 — far-from-S0 constructions underperform; exact LNS returns to ≤164 basin

## Incumbent

- n=64: **112** / n=100: **164** DUAL_VERIFIED — **no promotion**

## Session headline

1. Wave2 V=3 elites = **S0∪{q}** only.
2. Many S0 Hamming shells with restricted Add = `INFEASIBLE_SCOPED` (low-LB through r=4; frame r=2).
3. Midband Add r=2 @600s = TIMEOUT (open).
4. From-scratch/patterns ~132–135; half-rebuild+LNS climbs to **164**, does not beat.
5. LNS from annulus pattern: see `EXPERIMENTS/LH3_patterns/lns_from_annulus.json`.
6. Orbit n100 types 2–6 short Wave2-style universes: scoped INFEAS.

## Next 3 actions

1. Inspect annulus-LNS final size; if <164, hybrid pattern∪S0-core.
2. Enlarge orbit universes (not Wave2 halo caps) for type0/1 defects.
3. Consider literature constructions / notebook generator replay with exact repair.

## Standing order

Push after checkpoints; continue; no Hard Stop on report polish.
