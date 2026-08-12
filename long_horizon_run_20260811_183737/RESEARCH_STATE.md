# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 01:20 local (Wave3 deep orbit campaign)  
**Phase:** Wave3 Explore→CheapKill→Compute; incumbents unchanged.

## Incumbent

- n=64 **112** / n=100 **164** — **no legal +1**

## Wave3 ranking (in force)

- **R1 PRIMARY:** enlarged orbit-defect TIMEOUT track (types 0–4 xlarge all TIMEOUT size=0 so far)  
- **R2:** cert Hamming/HS micros — `INFEASIBLE_SCOPED` (LH-F015–F022)  
- **BLOCKED:** Agent C S0+1 soft grind (`scratch/wave3/agent_c_s0plus1_block.md`)  
- **HOLD:** FunSearch  

## Orbit results (TIMEOUT ≠ INFEASIBLE)

| Job | Universe | Wall | Cuts | Status |
|---|---|---:|---:|---|
| s401 Type0 | free261/def220/h14 | 2700s | 34563 | TIMEOUT size=0 |
| s641 n64 | free187/def160/h12 | 1200s | 24024 | TIMEOUT size=0 |
| s511 partial | free321/def280/h16 | 1200s | 71759 | TIMEOUT size=0 |
| s501 Type0 xlarge | free361/def320/h18 | 3600s | 86273 | TIMEOUT size=0 |
| s521/s601 Type1 | free321/def320/h18 | 2400s | ~69–77k | TIMEOUT size=0 |
| s702 Type2 | free321/def320/h18 | 1800s | 75512 | TIMEOUT size=0 |
| s531/s703 Type3 | ~free287–327/h16–18 | 1800s | ~58–97k | TIMEOUT size=0 |
| s541/s704 Type4 | ~free287–327/h16–18 | 1800s | ~59–100k | TIMEOUT size=0 |
| s801 Type0 **cert_lb2** | free361/…_rkcert_lb2 | 2700s | mid 21k@5min | **RUNNING** |
| s811 Type0 **mega 2h** | free≈360+/def360/h20 | 7200s | — | **RUNNING** |

## R2 obstruction map

Cert-involved, certfreq, cross-knn r2/r3, forced HS2 (8/8), joint-HS (10/10) → scoped INFEAS. Near-full Add TIMEOUT deprioritized.

## Next 3

1. Collect s801 cert_lb2 + s811 mega; dual-verify any FEASIBLE.  
2. If both TIMEOUT: new defect ranking (agent_c pool / core policy), not same U replay.  
3. Keep C S0+1 blocked; FunSearch held; do not reopen LH-F015–F022.
