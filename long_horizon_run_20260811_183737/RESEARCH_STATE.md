# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (Wave3 continued under push standing order)  
**Phase:** Explore continues; incumbents unchanged.

## Incumbent

- n=64 **112** / n=100 **164** — **no legal +1**; no dual-verified promotion

## Closed / deprioritized this stretch

| Family | Result |
|---|---|
| Orbit Types 0–6 xlarge + cert_lb2 + Type0 2h | TIMEOUT size=0 (not INFEAS) |
| Joint HS pairs / HS2 micros | SCOPED INFEAS (LH-F020–F022) |
| rem≥2 residual soft+fullstrip | CAPACITY_FAIL / SCOPED INFEAS (LH-F036–F040) |
| rem≥3 swap LS | best_V=42 (LH-F041) |
| From-scratch grow | best legal **137** (LH-F042) |

## Live lead / next

1. New defect-pool constructions (not agent_c truncation replay).  
2. Structured destroy/refill from legal 137–164 sets (not S0+1).  
3. Keep killed Hamming U_ids and rem2 residual cores closed.

## Discipline

TIMEOUT ≠ INFEASIBLE; scoped INFEAS ≠ global UB; dual-verify before promote.  
Standing order: commit+push after checkpoints; no force-push.
