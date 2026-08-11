# Failed / Dead Ends (imported + this run)

**Discipline:** Record negatives with evidence level. Scoped INFEASIBLE ≠ global optimality. Do not repeat without genuine new reason.

## Imported (pre-run)

### IMP-F001 — Single-region exact LNS from baselines
- Evidence: n64 ~8613 iters (session-documented; log incomplete); n100 25153 iters (`logs/lns_exact_n100_seed7.json`); no improve.
- Level: `HEURISTIC` / compute-budget negative.
- Status: **DEAD for primary budget** (RH-1). Sandbox only if testing new destroy kernels.

### IMP-F002 — Tabu / greedy LNS / center-probe
- Evidence: tabu logs; greedy multiseed; center-probe max_center_pts=0.
- Level: `HEURISTIC`.
- Status: **DEAD** as primary; H-006 flatness explains.

### IMP-F003 — n100 Hamming r=1 (any / U_small)
- Evidence: Gate1 GLOBAL deletion LB≥2 all 9836 cells; Agent A negative control `INFEASIBLE_SCOPED` + brute 7936 shells.
- Level: `GLOBAL_SHELL_EXCLUSION` + `SCOPED_INFEASIBLE`.
- Status: **DEAD as breakthrough**. Negative-control only if encoding changes.

### IMP-F004 — n100 `U_small_r2` and Wave2 score/halo Add pools (r=2/3)
- Evidence: `scratch/agent_a/hamming_n100_r2_summary.json` — primary + medium/large/fullrem/spatial-halo/r3 all `INFEASIBLE_SCOPED`.
- Level: `SCOPED_INFEASIBLE` (universes listed therein).
- Status: **DEAD those U_ids**. New Rem/Add definitions allowed if certificate-driven / residual-driven.

### IMP-F005 — n64 score `U_small` r=1
- Evidence: CP-SAT + brute 3312 shells, 0 legal.
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD that U_id**; other Rem/Add still open (global min deletion=1).

### IMP-F006 — Fixed-card min-V plateau (Wave2 C)
- Evidence: best V=3 @165 (n100), V=2 @113 (n64); no V=0 under operators/budget.
- Level: `HEURISTIC`.
- Status: **Operators stagnated**; residual exact repair / new neighborhoods still open (not full route kill).

### IMP-F007 — Multi-region pure/conflict/hybrid pilots (Wave2 A)
- Evidence: no size improve on n64/100 under listed budgets.
- Level: `HEURISTIC`.
- Status: **Those modes/budgets dead**; residual-elite repair is distinct.

## This run

_(append as experiments conclude)_
