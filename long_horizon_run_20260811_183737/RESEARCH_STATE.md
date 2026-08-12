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
| R1 PRIMARY | Enlarged Type0 orbit-defect | s401 45min **TIMEOUT** size=0; n64 enlarge TIMEOUT; **xlarge 320/h18/U_large s501 60min + partial s511 in flight** |
| R2 SECONDARY | Cert Hamming / microproblems | many new U_ids SCOPED INFEAS (see FAILED LH-F015–F020) |
| BLOCKED | Agent C S0+1 soft grind | active block |
| HOLD | FunSearch | no new structure |

## Key Wave3 negatives (scoped, not global UB)

- Cert-involved / certfreq / cross-knn r=2&3 → `INFEASIBLE_SCOPED`
- Forced exact HS2 for 8 easiest qs + large Add → 8/8 `INFEASIBLE_SCOPED` (LH-F020)
- Near-full multicomm Add → TIMEOUT deprioritized
- Type0 enlarged 20–45min still TIMEOUT≠INFEAS

## Live compute

| Job | Universe | Budget | Status |
|---|---|---:|---|
| s501 xlarge defect | max_extra=320, halo=18, U_large, dmax=16 | 3600s | running |
| s511 partial | max_extra=280, halo=16, U_large | 1200s | running |

## Discipline

TIMEOUT ≠ INFEASIBLE; scoped INFEAS ≠ global UB; dual-verify before promote.

## Next 3

1. Collect s501/s511; if TIMEOUT keep enlarging / change core policy; if FEASIBLE dual-verify.
2. Prefer multi-q joint certificate micros over more single-HS2.
3. Keep C S0+1 blocked; FunSearch held.
