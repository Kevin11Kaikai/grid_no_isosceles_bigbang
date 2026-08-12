# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 ~01:52 local  
**Remote:** `origin/master` @ `df3d642` (+ in-flight 45min Type0)  
**Phase:** LH-4 enlarged orbit longs — both Type0/1 20min TIMEOUT; 45min Type0 running

## Incumbent

- n=64 **112** / n=100 **164** — no promotion this run

## Live lead

Enlarged defect orbits (`max_extra=220`, `max_defect=220`, `halo=14`):

| Run | Status | Notes |
|---|---|---|
| Type0 20min s301 | TIMEOUT | 1921 rounds / 32186 cuts |
| Type1 20min s302 | TIMEOUT | 114 rounds / 19919 cuts |
| Type0 **45min** s401 | **RUNNING** | `long_t0_defect_s401_45min.json` |

Wave2-scale orbit universes often INFEAS; these enlarged models stay open.

## Critical process finding

All Wave2 `n100_V3` elites = **S0 ∪ {q}** (Hamming remove=0). Soft |S|=165 never left that basin.

## Next 3 actions

1. Collect 45min Type0 result; push.
2. If TIMEOUT: second seed 45–60min and/or raise halo/defect further.
3. Avoid S0+1 soft search and killed Hamming U_ids in `FAILED.md`.

## Standing order

Push after meaningful events; continue; no Hard Stop for polish.
