# Hypothesis / Route Registry

**Run:** `long_horizon_run_20260811_183737`  
**Policy:** Prefer information gain; no seed-grinding; scoped UNSAT ≠ global UB.

## Routes

| ID | Route | Owner bias | Status | Budget share (initial) | Notes |
|---|---|---|---|---:|---|
| A | Hamming-shell / blocker hypergraph exchange | Agent A lineage | LIVE — evolve beyond Wave2 score-U | ~40% | Wave2 killed `U_small_r2` + several halos SCOPED; next = certificate-driven Rem/Add |
| B | Orbit / structure + defect | Agent B lineage | LIVE — Wave2 COMPLETE (no +1); Type0 TIMEOUT open | ~20% | Wave2 freeze: report PASS; pure T1/T2 scoped INFEAS; Type0 longs TIMEOUT≠INFEAS; LH enlarge still live |
| C | Fixed-cardinality min-conflict | Agent C lineage | LIVE — plateau | ~15% | Best V=3 (n100@165), V=2 (n64@113); no V=0 |
| D | Hybrid / multi-region / residual-conflict exact repair | Main+A | LIVE | ~10% | Wave2 multi-region no +1; residual V-elite repair open |
| K | Critic / cheap-kill / red-team discipline | Critic | ALWAYS ON | ~10% | Kill repeats; enforce scopes |
| V | Verification infra / certificates | Main | ALWAYS ON | ~10% | Dual verify any ≥165/113 |
| X | Abstraction (conjecture vs theorem) | Main | PERIODIC | ~5% | |

## Active hypotheses (this run)

| HID | Claim | Evidence level | Next test |
|---|---|---|---|
| LH-A1 | Joint blocker VC Rem for easiest-q pairs admits r=2 shells | **REJECTED** (joint_VC=4 always) | see LH-F001 |
| LH-A2 | Global r=1 shell around official n100 S0 empty of +1 | `GLOBAL_SHELL_EXCLUSION` | do not re-spend |
| LH-A3 | Low-LB cells have complementary (low joint VC) pairs | **REJECTED on 85-q sample** | LH-F002; try fullrem LB≤4 Add next |
| LH-A4 | `U_fullrem_LBle4_r2` admits legal 165 | **REJECTED** (LH-F004) | — |
| LH-C1 | V=3 elites locally refillable to V=0 at \|S\|=165 | **REJECTED for tested halos** | LH-F003 |
| LH-B1 | Type-0/1 defect orbits can reach 165 | OPEN / TIMEOUT-heavy (Wave2 B closed no +1) | W3 R1: s401 45min TIMEOUT; s501 xlarge 60min + s511 partial in flight |
| LH-D1 | Residual communities beat Hamming U | **weakened** — refill infeasible; nonlocal free still open | |
| W3-A1 | Cert-involved / certfreq Rem+low-LB Add r=2 admits 165 | **REJECTED** e16/e56/top48 (LH-F015/017) | try cross-knn / residual nonlocal only |
| W3-A2 | Cross spatial-knn Rem/Add r=2/3 admits 165 | **REJECTED** (LH-F018/019) | need new Rem/Add or orbit |
| W3-A3 | Force exact HS2 for easy q + large Add ⇒ legal 165 | **REJECTED** 8/8 (LH-F020) | — |
| W3-A4 | Joint HS pair forced-delete r=|Rem| ⇒ legal 165 | **REJECTED** 10/10 (LH-F022) | orbit primary |
| W3-C0 | Soft S0+1 fixed-card seed grind | **BLOCKED** (LH-F016) | require remove≥2 / new formulation |

## Frozen Wave2 facts (import)

- n100 `U_small` r=1: `INFEASIBLE_SCOPED`, hash `0e371058…4caac2` (negative control).
- n100 `U_small_r2` r=2: 4/4 `INFEASIBLE_SCOPED`, hash `a100c8b6…0e88`.
- Escalated rem/add/halo shells (medium/large/fullrem/spatial-halo/r3 variants): all `INFEASIBLE_SCOPED` under Agent A budgets — still **scoped**.
- n64 `U_small` r=1: `INFEASIBLE_SCOPED` + brute 3312 shells agree.
- Agent C: no V=0; plateaus match Gate1 empirical min direct-insertion ΔV.
- Red Team Wave2: A/B/C PASS; Gate2 PASS/CLOSED (`scratch/wave2/gate2_decision.md`); legal +1 none.
- Agent B Wave2: Type0 longs TIMEOUT size=0; many axes scoped INFEAS; `any_legal_plus1=false`; no candidates.
