# FINAL_REPORT (incremental)

**Run:** `long_horizon_run_20260811_183737`  
**Status:** Research in progress — incumbents unchanged.

## Bottom line (live)

- Certified lower bounds unchanged: \(C(64)\ge 112\), \(C(100)\ge 164\).
- No dual-verified improvement found.
- Gate2 CLOSED / Wave3 ranking funded (`scratch/wave3/ranking_memo.md`): R1 enlarged Type0 orbit TIMEOUT; R2 cert Hamming outside killed U_ids; C S0+1 soft grind blocked; FunSearch held.
- Major structural finding: Wave2 Agent-C V=3 elites are exactly **baseline + one cell**; soft |S|=165 search never left that basin.
- Wave3 cert cheap-kills (involved e16/e56, certfreq-top48, cross-knn bridge_top) → `INFEASIBLE_SCOPED` quickly; near-full multicomm Add TIMEOUT deprioritized.
- Hamming shells around official S0 with low-LB / frame Add pools are heavily `INFEASIBLE_SCOPED` for small r; midband remains TIMEOUT@600s.
- Far-from-S0 greedy/pattern constructions reach ~130–135; exact LNS from partial (~136) climbs back to **164** without exceeding it.
- Orbit n100 types 2–6 (short new seeds, Wave2-style universes) report scoped INFEASIBLE; enlarged Type0 remains TIMEOUT-open (s401 45min in flight).

## Methods tested this run

Hamming certificate/Rem-Add shells; residual elite refill; forced-exchange min-V; cert-seeded r=4; from-scratch/half-rebuild; pattern legalize; orbit smokes; LNS-exact from non-S0 starts; Wave3 cert/cross-knn cheap-kills; enlarged orbit defects.

## What is NOT claimed

Scoped INFEASIBLE ≠ \(C(100)\le 164\). TIMEOUT ≠ INFEASIBLE. Heuristic plateaus ≠ optimality.
