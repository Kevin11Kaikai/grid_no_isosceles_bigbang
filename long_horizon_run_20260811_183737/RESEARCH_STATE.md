# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (forbid-Rem)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**

## Key new fact (F060)
Keeping a large S0 core while **forbidding** deleted points blocks S0 recovery:
- Rem40 forbid → capacity 127
- Rem60 forbid → **proved max 128**
- Rem80 forbid → best 134 TIMEOUT (non-S0 hash)

Without blacklist, Rem80/100 **snap back** to incumbent (F059).

## Next 3
1. Long escalate forbid Rem80/100 (TIMEOUT≠INFEAS).  
2. Structured Rem blacklist (HS2-involved / certfreq) + maximize.  
3. Fixed-card from non-S0 134 midset (not S0+1).

## Discipline
TIMEOUT ≠ INFEAS; scoped ≠ global; standing order push.
