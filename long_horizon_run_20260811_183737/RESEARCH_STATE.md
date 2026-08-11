# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-11 local ~18:37 (bootstrap complete; research loop starting)  
**Git HEAD:** `2600e8fb9417f94ea26173788c8819a04a9c4501`  
**Phase:** Bootstrap DONE → Wave LH-1 cheap-kill + blocker-pair pilot

## Incumbent

- n=64: **112** DUAL_VERIFIED (`47d42165…e9c292`)
- n=100: **164** DUAL_VERIFIED (`8a84216d…bdc1`)
- No promotion this run yet.

## Gate / Wave heritage

- Gate0 PASS, Gate1 PASS (`WAVE2_READY`), Wave2 A/C complete (Red Team PASS), B incomplete (TIMEOUT / report missing).
- n100 r=2 primary; r=1 negative-control only; n64 r=1 sandbox.

## Live allocation

| Slice | Focus |
|---|---|
| 40% A | Blocker-pair joint VC → multi-add exact microproblems (new U construction) |
| 20% B | Orbit cheap-kill / avoid Wave2 TIMEOUT grind |
| 15% C | Residual structure of V=3 elites |
| 10% D/hybrid | Wire residual exact repair if C shows small witness support |
| 10% critic | Cheap-kill checks |
| 5% abstraction | Update OPEN/PROVED after pilots |

## Immediate next actions

1. **RUNNING/NEXT:** Exact blocker-pair compatibility pilot for easiest-16 qs (n100).
2. Analyze one V=3 elite residual witnesses.
3. If joint Rem size≤2 feasible for any pair+third, escalate to CP-SAT shell; else escalate Rem or try triple-q / r=3 certificate Rem.

## Hard stop conditions

Only: env kill, user stop, space exhausted with certificates, or full mathematical solution.
Do **not** stop because a Wave finished or report looks ready.
