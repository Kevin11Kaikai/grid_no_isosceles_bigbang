# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (harvest parallel jobs; continue Explore)  
**Phase:** Wave3 harvest complete; new destroy-refill compute launching.

## Incumbent

- n=64 **112** / n=100 **164** — **no legal +1**; no dual-verified promotion

## Harvest (jobs finished; no processes left)

| Job | Result | Notes |
|---|---|---|
| W3_pattern_lns v2 | best **133** (annulus 103→133) | dual OK; beats_164=false |
| W3_grow_lns | best **134** (boundary 120→134) | dual OK; beats_164=false |
| W3_from_scratch grow_v3 | best **135** | dual OK; plateau |
| W3_from_scratch summary | best **132** (keep_frac LNS) | dual OK |
| W3_rem3_residual | s802 soft/partial **INFEAS**; maximize → **164** (=incumbent hash); s801 soft **TIMEOUT** 30min | LH-F045/F046 |

## Closed / deprioritized

- Orbit xlarge TIMEOUT; rem2 residual dead; rem3 residual elites weak; spatial/dispersed Hamming dead; S0+1 blocked; plain grow/pattern-LNS plateau ≪164

## Next 3

1. **PRIMARY:** Exact-LNS destroy/refill from official S0 (164) + from grow-135, larger destroy / longer MILP — aim |S|≥165.  
2. Avoid killed Hamming U_ids / rem2 residual / S0+1 soft grind.  
3. Dual-verify any ≥165 before promote.

## Discipline

TIMEOUT ≠ INFEASIBLE; scoped INFEAS ≠ global UB; dual-verify before promote.  
Standing order: commit+push; no force-push; ignore `.venv_solver`.
