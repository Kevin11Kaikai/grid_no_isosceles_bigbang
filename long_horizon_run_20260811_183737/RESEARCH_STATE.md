# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 ~01:11 local  
**Remote:** `origin/master`  
**Phase:** LH-4 — enlarged Type0 orbit TIMEOUT (live lead); Hamming S0-neighborhood largely exhausted at small r

## Incumbent

- n=64 **112** / n=100 **164** — no promotion

## Live lead

**Enlarged orbit Type0 defect** (`max_extra=220`, `max_defect=220`, `halo=14`):  
universe `orb_t0_defect_core41_free261_def220_part0_h14` → **TIMEOUT** @180s (≠ INFEAS).  
See `EXPERIMENTS/LH4_orbit_enlarged/summary.json`.

## Major negatives this run

- V3 elites = S0+1; soft |S|=165 stayed in that basin.
- easiest-16 pairs joint_VC=4; low-LB/frame Hamming shells INFEAS for small r.
- Far-from-S0 greedy/pattern ≤136; LNS from S0-core returns to 164 without beating.

## Next 3 actions

1. Longer enlarged Type0/1 defect orbits (15–60 min) with same large universe.
2. Hybrid annulus∪S0-core exact LNS.
3. Keep pushing checkpoints to `origin/master`.

## Standing order

Continue research; push after meaningful events; no Hard Stop for polish.
