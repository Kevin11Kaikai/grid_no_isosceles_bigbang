# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 ~01:31 local  
**Remote:** `origin/master`  
**Phase:** LH-4 enlarged orbit longs — Type0 20min still TIMEOUT (open)

## Incumbent

- n=64 **112** / n=100 **164** — no promotion

## Live lead (highest priority)

Enlarged orbit universes (`max_extra=220`, `max_defect=220`, `halo=14`):

| Job | Status | Evidence |
|---|---|---|
| Type0 defect 180s | TIMEOUT | `LH4_orbit_enlarged/summary.json` |
| Type0 defect **1200s** | **TIMEOUT** (1921 rounds, 32186 cuts) | `long_t0_defect_s301.json` |
| Type1 defect 180s | TIMEOUT | summary |
| Type1 pure enlarged | INFEASIBLE_SCOPED | summary |
| Type1 defect 1200s | running / next | `long_t1_defect_s302.json` |

**Interpretation:** Unlike Wave2-scale orbit universes that often go INFEAS quickly, these enlarged defect models remain open under 20 minutes. Primary budget stays here.

## Killed / deprioritized

See `FAILED.md` LH-F001–F014 (S0 Hamming low-LB/frame; V3=baseline+1; far-from-S0 ≤136; etc.).

## Next 3 actions

1. Finish Type1 1200s enlarged defect.
2. If still TIMEOUT: multi-seed Type0 30–60min OR raise defect/halo further.
3. Do not spend primary budget on baseline+1 soft search or frame r=2 shells.

## Standing order

Push after checkpoints; continue; no Hard Stop for polish.
