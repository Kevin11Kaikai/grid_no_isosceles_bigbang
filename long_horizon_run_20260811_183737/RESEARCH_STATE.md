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
| Type2 xlarge s702 | free321/def320/h18 | 1800s | 75512 | TIMEOUT size=0 (LH-F027) |
| Type3 xlarge s703 | free327/def320/h18 | 1800s | 97485 | TIMEOUT size=0 (LH-F028) |
| Type4 xlarge s704 | — | 1800s | — | **running** |
| Type0 cert_lb2 s801 | new defect_rank | 2700s | — | queued after Type4 |

Cut growth on Type0 xlarge (34k→86k) shows search still exploring; no FEASIBLE yet. Forced rem≥2 LS best_V=29 (LH-F026). `defect_rank=cert_lb2` changes U fingerprint (8-point pool delta).

## R2 cert micro obstruction map

Single-HS2 (8/8) and joint-HS pairs (10/10) `INFEASIBLE_SCOPED` under large Add — strong scoped obstruction to “clear easy certificate covers then refill”. Not a global UB.

## Next 3

1. Finish Type4; launch Type0 cert_lb2 (new U).  
2. If still TIMEOUT: ≥2h Type0 or other symmetry with cert_lb2 — not same U replay.  
3. Keep R2 from reopening killed U_ids; no C S0+1; FunSearch held.
