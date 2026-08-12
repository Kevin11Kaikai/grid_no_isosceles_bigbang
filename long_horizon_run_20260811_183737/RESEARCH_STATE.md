# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (rem2 residual)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**

## Lead
rem>=2 illegal V=25 -> strip witnesses -> legal cores:
- full involved strip core=121: exact extend to 165 **INFEASIBLE_SCOPED** (LH-F036)
- soft strip cores 130-160: 6min TIMEOUT (LH-F037); **long escalate k=5/10 running**

## Orbit
Types 0-6 xlarge + cert_lb2 + Type0 2h all TIMEOUT size=0. Deprioritize same-U wall.

## Next
1. Collect soft long core-extend (need=5 from core 160).
2. If FEASIBLE dual-verify; if INFEAS kill that core family; if TIMEOUT try other rem2 seeds.
3. Keep S0+1 / killed Hamming closed.
