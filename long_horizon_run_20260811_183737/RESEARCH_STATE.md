# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 ~00:28 local  
**Remote:** `origin/master` (push standing order active)  
**Phase:** LH-3 far-from-S0 construction; midband r=2 still TIMEOUT@600s

## Incumbent

- n=64: **112** / n=100: **164** — unchanged

## Latest results

| Line | Outcome |
|---|---|
| From-scratch grow | best legal **n100=135**, **n64=88** |
| Half-baseline rebuild | best **164/112** (recovered S0 at keep=0.75); keep=0.5 → ~130–136 |
| Midband Add r=2 @600s | `TIMEOUT_INCONCLUSIVE` (not INFEAS; 1148 rounds) |
| Frame R2/R6 r=2 long | `INFEASIBLE_SCOPED` |
| V3 elites | all = S0+1 |

## Running / next

1. LNS-exact from half-rebuild start (~136) — in progress
2. If no beat of 164: try SA/exact multi-region from partial; orbit types 5–6
3. Midband left as TIMEOUT (optional later longer / different r)

## Standing order

Commit+push after meaningful checkpoints; continue; no Hard Stop.
