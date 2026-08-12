# FINAL_REPORT (incremental)

**Run:** `long_horizon_run_20260811_183737`  
**Status:** Research in progress — incumbents unchanged.

## Bottom line (live)

- Certified lower bounds unchanged: \(C(64)\ge 112\), \(C(100)\ge 164\).
- No dual-verified improvement found.
- Gate2 CLOSED / Wave3 ranking funded: R1 enlarged orbit TIMEOUT; R2 cert Hamming; C S0+1 blocked; FunSearch held.
- Wave3 R2: cert-involved/certfreq/cross-knn/forced-HS2/joint-HS micros → `INFEASIBLE_SCOPED` (not global UB).
- Wave3 R1: Type0 xlarge 60min (free361/def320/h18) still **TIMEOUT size=0** with 86k cuts (search progressing, not proven empty); Type1 xlarge likewise TIMEOUT.
- Soft |S|=165 elites remain S0∪{q} basin.

## Methods tested this run

Hamming certificate/Rem-Add shells; residual elite refill; forced-exchange min-V; cert-seeded r=4; from-scratch/half-rebuild; pattern legalize; orbit smokes; LNS-exact from non-S0 starts; Wave3 cert/cross-knn cheap-kills; enlarged orbit defects.

## What is NOT claimed

Scoped INFEASIBLE ≠ \(C(100)\le 164\). TIMEOUT ≠ INFEASIBLE. Heuristic plateaus ≠ optimality.
