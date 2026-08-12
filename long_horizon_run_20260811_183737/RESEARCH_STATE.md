# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (post cert_lb2 s801)  
**Phase:** Wave3 loop continues; incumbents unchanged.

## Incumbent

- n=64 **112** / n=100 **164** — **no legal +1**

## Wave3 ranking

- **R1 PRIMARY:** orbit-defect TIMEOUT track (enlarge + new defect_rank)  
- **R2:** cert Hamming/micros — LH-F015–F022 SCOPED INFEAS  
- **BLOCKED:** Agent C S0+1 soft grind  
- **HOLD:** FunSearch  

## Orbit campaign (TIMEOUT ≠ INFEASIBLE)

| Job | Universe | Wall | Rounds | Cuts | Status |
|---|---|---:|---:|---:|---|
| s501 Type0 xlarge | free361/def320/h18 | 3600s | 2568 | 86273 | TIMEOUT |
| s601/s521 Type1 | free321/def320/h18 | 2400s | ~420 | ~70k | TIMEOUT |
| s702 Type2 | free321/def320/h18 | 1800s | 438 | 75512 | TIMEOUT |
| s703 Type3 | free327/def320/h18 | 1800s | 815 | 97485 | TIMEOUT |
| s704 Type4 | free327/def320/h18 | 1800s | 806 | 100067 | TIMEOUT |
| s801 Type0 **cert_lb2** | …h18_rkcert_lb2 | 2700s | **4114** | 50113 | TIMEOUT (LH-F030) |
| s901 Type0 **2h** | free361/def320/h18 | 7200s | — | — | **launching** |

cert_lb2: more rounds, fewer cuts than agent_c truncation — still size=0.

## Next 3

1. Run ≥2h Type0 agent_c s901.  
2. If TIMEOUT: Type1/5 cert_lb2 or new formulation (not more same-U 30min).  
3. Keep killed Hamming/S0+1 closed; FunSearch held.
