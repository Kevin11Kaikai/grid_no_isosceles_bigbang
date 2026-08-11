# Hypothesis / Route Registry

**Run:** `long_horizon_run_20260811_183737`  
**Policy:** Prefer information gain; no seed-grinding; scoped UNSAT ≠ global UB.

## Routes

| ID | Route | Owner bias | Status | Budget share (initial) | Notes |
|---|---|---|---|---:|---|
| A | Hamming-shell / blocker hypergraph exchange | Agent A lineage | LIVE — evolve beyond Wave2 score-U | ~40% | Wave2 killed `U_small_r2` + several halos SCOPED; next = certificate-driven Rem/Add |
| B | Orbit / structure + defect | Agent B lineage | LIVE — incomplete Wave2 | ~20% | Long TIMEOUT; Type1 pure INFEASIBLE; report absent |
| C | Fixed-cardinality min-conflict | Agent C lineage | LIVE — plateau | ~15% | Best V=3 (n100@165), V=2 (n64@113); no V=0 |
| D | Hybrid / multi-region / residual-conflict exact repair | Main+A | LIVE | ~10% | Wave2 multi-region no +1; residual V-elite repair open |
| K | Critic / cheap-kill / red-team discipline | Critic | ALWAYS ON | ~10% | Kill repeats; enforce scopes |
| V | Verification infra / certificates | Main | ALWAYS ON | ~10% | Dual verify any ≥165/113 |
| X | Abstraction (conjecture vs theorem) | Main | PERIODIC | ~5% | |

## Active hypotheses (this run)

| HID | Claim | Evidence level | Next test |
|---|---|---|---|
| LH-A1 | Score-based `U_small_r2` is too narrow; **joint blocker VC Rem** for easiest-q pairs may admit legal r=2 shells | OPEN | Blocker-pair → multi-add exact microproblems |
| LH-A2 | Global r=1 shell around official n100 S0 is empty of +1 (Gate1) | `GLOBAL_SHELL_EXCLUSION` | Negative-control already PASS; do not re-spend |
| LH-C1 | V=3 plateaus at \|S\|=165 are structurally near-legal (few witness triples); exact local repair can kill residual V | OPEN | Analyze V3 elites; exact repair on witness support |
| LH-B1 | Type-0/1 defect orbits can reach 165 under legality | OPEN / Wave2 TIMEOUT-heavy | Cheap smoke then diversify; avoid replaying same TIMEOUT seeds |
| LH-D1 | Residual-conflict communities of V>0 elites yield smaller exact models than Hamming universes | OPEN | After LH-C1 structure dump |

## Frozen Wave2 facts (import)

- n100 `U_small` r=1: `INFEASIBLE_SCOPED`, hash `0e371058…4caac2` (negative control).
- n100 `U_small_r2` r=2: 4/4 `INFEASIBLE_SCOPED`, hash `a100c8b6…0e88`.
- Escalated rem/add/halo shells (medium/large/fullrem/spatial-halo/r3 variants): all `INFEASIBLE_SCOPED` under Agent A budgets — still **scoped**.
- n64 `U_small` r=1: `INFEASIBLE_SCOPED` + brute 3312 shells agree.
- Agent C: no V=0; plateaus match Gate1 empirical min direct-insertion ΔV.
- Red Team Wave2: A/C PASS; B provisional/PENDING report.
