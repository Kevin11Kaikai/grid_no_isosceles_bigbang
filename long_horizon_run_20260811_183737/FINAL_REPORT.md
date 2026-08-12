# FINAL_REPORT (incremental)

**Run:** `long_horizon_run_20260811_183737`  
**Status:** Research in progress — incumbents unchanged.

## Bottom line (live)

- Certified lower bounds unchanged: \(C(64)\ge 112\), \(C(100)\ge 164\).
- No dual-verified improvement found.
- Major structural finding: Wave2 Agent-C V=3 elites are exactly **baseline + one cell**; soft |S|=165 search never left that basin.
- Hamming shells around official S0 with low-LB / frame Add pools are heavily `INFEASIBLE_SCOPED` for small r; midband remains TIMEOUT@600s.
- Far-from-S0 greedy/pattern constructions reach ~130–135; exact LNS from partial (~136) climbs back to **164** without exceeding it.
- Orbit n100 types 2–6 (short new seeds, Wave2-style universes) report scoped INFEASIBLE.

## Methods tested this run

Hamming certificate/Rem-Add shells; residual elite refill; forced-exchange min-V; cert-seeded r=4; from-scratch/half-rebuild; pattern legalize; orbit smokes; LNS-exact from non-S0 starts.

## What is NOT claimed

Scoped INFEASIBLE ≠ \(C(100)\le 164\). TIMEOUT ≠ INFEASIBLE. Heuristic plateaus ≠ optimality.
