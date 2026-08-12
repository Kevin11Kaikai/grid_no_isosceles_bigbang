# FINAL_REPORT (incremental)

**Run:** `long_horizon_run_20260811_183737`  
**Status:** Research in progress — incumbents unchanged.

## Bottom line (live)

- Certified lower bounds unchanged: \(C(64)\ge 112\), \(C(100)\ge 164\).
- **No dual-verified improvement** in Wave3.
- Soft_core orbit enlargements (types 0–4, mega free401/h20 @2h, cert_lb2, mega+cert_lb2) all **TIMEOUT size=0** — TIMEOUT ≠ INFEASIBLE.
- `fix_core=True` on enlarged Type0 → **SCOPED INFEASIBLE** (LH-F033).
- Certificate Hamming / forced-HS2 / joint-HS / cross-knn → **SCOPED INFEASIBLE** (not global UB).
- Agent C S0+1 soft grinding **blocked**; FunSearch **held**.

## Methods tested this run (Wave3+)

Enlarged orbit/defect (soft+fix core); cert_lb2 defect ranking; mega caps; Type5/6 diversify; certificate Hamming Rem/Add; forced/joint HS micros; n64 HS2 sandbox.

## Methods tested this run

Hamming certificate/Rem-Add shells; residual elite refill; forced-exchange min-V; cert-seeded r=4; from-scratch/half-rebuild; pattern legalize; orbit smokes; LNS-exact from non-S0 starts; Wave3 cert/cross-knn cheap-kills; enlarged orbit defects.

## What is NOT claimed

Scoped INFEASIBLE ≠ \(C(100)\le 164\). TIMEOUT ≠ INFEASIBLE. Heuristic plateaus ≠ optimality.
