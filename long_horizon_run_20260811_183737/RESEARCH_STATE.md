# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (Wave3 mid-loop)  
**Remote:** `origin/master`  
**Phase:** Gate2 CLOSED; Wave3 Explore→CheapKill→Compute active.

## Incumbent

- n=64 **112** / n=100 **164** — no promotion; **no legal +1**

## Wave3 ranking

Canonical: `scratch/wave3/ranking_memo.md`

| Rank | Route | Status |
|---|---|---|
| R1 PRIMARY | Enlarged orbit-defect | s401 45min TIMEOUT; s511 partial 20min TIMEOUT; **s501 Type0 xlarge 60min running**; **s601 Type1 xlarge 40min launched** |
| R2 SECONDARY | Cert Hamming / microproblems | LH-F015–F022 many SCOPED INFEAS; joint-HS pairs dead |
| BLOCKED | Agent C S0+1 soft grind | active block |
| HOLD | FunSearch | no new structure |

## Key Wave3 negatives (scoped, not global UB)

- Cert-involved / certfreq / cross-knn r=2&3 → `INFEASIBLE_SCOPED`
- Forced exact HS2 for 8 easiest qs + large Add → 8/8 `INFEASIBLE_SCOPED` (LH-F020)
- Joint HS pairs among easiest-6 → 10/10 `INFEASIBLE_SCOPED` at r=4 (LH-F022)
- Near-full multicomm Add → TIMEOUT deprioritized
- Type0 enlarged 20–45min still TIMEOUT≠INFEAS

## Live compute

| Job | Universe | Budget | Status |
|---|---|---:|---|
| s501 Type0 xlarge defect | free361/def320/h18 | 3600s | running (~20min: 1606 rounds / 68400 cuts, size=0) |
| s601 Type1 xlarge defect | 320/h18/dmax20 | 2400s | **launched** |
| s511 Type0 partial | free321/def280/part24/h16 | 1200s | **TIMEOUT** size=0 (1562r / 71759 cuts) |

## Discipline

TIMEOUT ≠ INFEASIBLE; scoped INFEAS ≠ global UB; dual-verify before promote.

## Next 3

1. Collect s501/s601; FEASIBLE → dual-verify; TIMEOUT → change core policy / longer / other types.
2. No more joint-HS pair micros (LH-F022); Hamming only for novel Rem/Add.
3. Keep C S0+1 blocked; FunSearch held.
