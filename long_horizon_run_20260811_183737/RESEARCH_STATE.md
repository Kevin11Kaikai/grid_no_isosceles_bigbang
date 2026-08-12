# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (joint HS + grow-destroy)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**; dual hashes unchanged.

## Latest harvest / compute
| Result | Notes |
|---|---|
| HS2-delete max ×8 | **MAX_PROVED 164** (LH-F051) |
| Joint HS2-pair ×8 | **MAX_PROVED 164** (LH-F052) |
| Grow-134 destroy/refill | best **138** parity_even TIMEOUT; frames proved ≤134 (LH-F053) |
| S0 frame_d2 refill | MAX_PROVED 164 (LH-F048) |

## Closed this stretch
- Keep-S0-minus-(1 or 2) easy HS2 refill to 165
- Shallow grow frame/random destroy expecting ≥165

## Next 3
1. Long escalate parity / large free-pool maximize from non-S0 cores (TIMEOUT≠INFEAS).  
2. Cert-freq / structured Rem on S0 with large free pool (not HS2 of single q).  
3. Dual-verify before any ≥165 promote; avoid Hamming/rem2/S0+1 soft grind.

## Discipline
TIMEOUT ≠ INFEAS; scoped ≠ global; standing order push.
