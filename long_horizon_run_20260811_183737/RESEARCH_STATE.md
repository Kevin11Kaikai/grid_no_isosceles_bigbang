# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (dispersed Hamming + rem3 residual harvest)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**

## Wave3 kills (recent)
- Spatial knn-block Hamming (LH-F042) and dispersed-stride Hamming (LH-F044): SCOPED INFEAS.
- rem3 residual s802: soft/partial INFEAS; soft-core maximize = **164** dual-legal (LH-F045).
- rem3 soft swap plateau V=42 (LH-F041); rem2 residual dead earlier.

## Live
- Pattern screen+LNS (`W3_pattern_lns`) — annulus legalize ~128; checker ~124.
- From-scratch grow_v3 — boundary ~135 so far.
- Exact LNS from ring-bias start=111 (`W3_from_scratch/run_job.py`).

## Next 3
1. Finish pattern LNS / from-scratch LNS; dual-verify if ≥165.
2. LNS warm-start from best grow (~135) and best pattern (~128+).
3. Do not reopen killed Hamming U_ids / rem2 residual / S0+1 soft.

## Blocked
- C S0+1; FunSearch held; spatial/dispersed Hamming; rem2 residual; rem3 residual for s802.
