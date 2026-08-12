# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (post Type0 2h)  
**Phase:** Wave3 continues; incumbents unchanged.

## Incumbent

- n=64 **112** / n=100 **164** — **no legal +1**

## Orbit campaign summary

Types **0–6** xlarge + Type0 **cert_lb2** + Type0 **2h** all **TIMEOUT** size=0 (LH-F024–F034).  
`fix_core=True` scoped INFEAS (LH-F033). Soft-core remains open but stagnant.

| Notable | Wall | Cuts | Notes |
|---|---:|---:|---|
| s501 Type0 1h | 3600s | 86273 | TIMEOUT |
| s901 Type0 2h | 7200s | 91864 | TIMEOUT (LH-F034) — cuts barely grew vs 1h |
| s801 cert_lb2 | 2700s | 50113 | more rounds, fewer cuts |

## Live

- Type1 **cert_lb2** s821 (40min) running

## Next 3

1. Collect s821; if TIMEOUT shift hard to residual/exact repair of rem≥2 illegal cores (not more Type0 wall).  
2. Keep Hamming killed U_ids closed; S0+1 blocked.  
3. FunSearch held.

## Discipline

TIMEOUT ≠ INFEASIBLE; scoped INFEAS ≠ global UB; dual-verify before promote.
