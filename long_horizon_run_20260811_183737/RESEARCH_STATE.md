# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (Wave3 after xlarge Type0/1 TIMEOUT)  
**Phase:** Wave3 loop continues; incumbents unchanged.

## Incumbent

- n=64 **112** / n=100 **164** — **no legal +1**

## Wave3 ranking (still in force)

- **R1 PRIMARY:** enlarged Type0/1/… orbit-defect TIMEOUT track  
- **R2:** cert Hamming/microproblems — heavily `INFEASIBLE_SCOPED` (LH-F015–F022)  
- **BLOCKED:** Agent C S0+1 soft grind  
- **HOLD:** FunSearch  

## Orbit campaign results (TIMEOUT ≠ INFEASIBLE)

| Job | Universe | Wall | Cuts | Status |
|---|---|---:|---:|---|
| s401 Type0 | free261/def220/h14 | 2700s | 34563 | TIMEOUT size=0 |
| s641 n64 Type0 | free187/def160/h12 | 1200s | 24024 | TIMEOUT size=0 |
| s511 Type0 partial | free321/def280/part24/h16 | 1200s | 71759 | TIMEOUT size=0 |
| s501 Type0 xlarge | **free361/def320/h18** | 3600s | **86273** | TIMEOUT size=0 |
| s521 Type1 xlarge | free321/def320/h18 | 2400s | 68574 | TIMEOUT size=0 |
| s601 Type1 xlarge | free321/def320/h18 | 2400s | 76897 | TIMEOUT size=0 |
| Type2 xlarge | (SCRATCH live) | — | — | running |
| Type3/4 xlarge | queued | 1800s ea | — | next |

Cut growth on Type0 xlarge (34k→86k) shows search still exploring; no FEASIBLE yet.

## R2 cert micro obstruction map

Single-HS2 (8/8) and joint-HS pairs (10/10) `INFEASIBLE_SCOPED` under large Add — strong scoped obstruction to “clear easy certificate covers then refill”. Not a global UB.

## Next 3

1. Finish Type2 live; run Type3/4 enlarged defects.  
2. If all TIMEOUT: try longer Type0 (≥2h) **or** new core/defect policy (not same U).  
3. Keep R2 from reopening killed U_ids; no C S0+1; FunSearch held.
