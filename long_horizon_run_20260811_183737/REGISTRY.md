# Hypothesis / Route Registry

**Run:** `long_horizon_run_20260811_183737`  
**Policy:** Prefer information gain; no seed-grinding; scoped UNSAT 鈮?global UB.

## Routes

| ID | Route | Owner bias | Status | Budget share (initial) | Notes |
|---|---|---|---|---:|---|
| A | Hamming-shell / blocker hypergraph exchange | Agent A lineage | LIVE 鈥?evolve beyond Wave2 score-U | ~40% | Wave2 killed `U_small_r2` + several halos SCOPED; next = certificate-driven Rem/Add |
| B | Orbit / structure + defect | Agent B lineage | LIVE 鈥?Wave2 COMPLETE (no +1); Type0 TIMEOUT open | ~20% | Wave2 freeze: report PASS; pure T1/T2 scoped INFEAS; Type0 longs TIMEOUT鈮營NFEAS; LH enlarge still live |
| C | Fixed-cardinality min-conflict | Agent C lineage | LIVE 鈥?plateau | ~15% | Best V=3 (n100@165), V=2 (n64@113); no V=0 |
| D | Hybrid / multi-region / residual-conflict exact repair | Main+A | LIVE | ~10% | Wave2 multi-region no +1; residual V-elite repair open |
| K | Critic / cheap-kill / red-team discipline | Critic | ALWAYS ON | ~10% | Kill repeats; enforce scopes |
| V | Verification infra / certificates | Main | ALWAYS ON | ~10% | Dual verify any 鈮?65/113 |
| X | Abstraction (conjecture vs theorem) | Main | PERIODIC | ~5% | |

## Active hypotheses (this run)

| HID | Claim | Evidence level | Next test |
|---|---|---|---|
| LH-A1 | Joint blocker VC Rem for easiest-q pairs admits r=2 shells | **REJECTED** (joint_VC=4 always) | see LH-F001 |
| LH-A2 | Global r=1 shell around official n100 S0 empty of +1 | `GLOBAL_SHELL_EXCLUSION` | do not re-spend |
| LH-A3 | Low-LB cells have complementary (low joint VC) pairs | **REJECTED on 85-q sample** | LH-F002; try fullrem LB鈮? Add next |
| LH-A4 | `U_fullrem_LBle4_r2` admits legal 165 | **REJECTED** (LH-F004) | 鈥?|
| LH-C1 | V=3 elites locally refillable to V=0 at \|S\|=165 | **REJECTED for tested halos** | LH-F003 |
| LH-B1 | Type-0/1 defect orbits can reach 165 | OPEN / TIMEOUT-heavy | Types0鈥? xlarge + cert_lb2 + 2h TIMEOUT; deprioritize same-U wall |
| LH-D1 | Residual communities beat Hamming U | **weakened** 鈥?refill infeasible; nonlocal free still open | |
| W3-A1 | Cert-involved / certfreq Rem+low-LB Add r=2 admits 165 | **REJECTED** e16/e56/top48 (LH-F015/017) | 鈥?|
| W3-A2 | Cross spatial-knn Rem/Add r=2/3 admits 165 | **REJECTED** (LH-F018/019) | 鈥?|
| W3-A3 | Force exact HS2 for easy q + large Add 鈬?legal 165 | **REJECTED** 8/8 (LH-F020) | 鈥?|
| W3-A4 | Joint HS pair forced-delete r=|Rem| 鈬?legal 165 | **REJECTED** 10/10 (LH-F022) | 鈥?|
| W3-C1 | Forced rem鈮? fixed-card LS reaches V=0 | **weakened** best_V鈮?5鈥?9 (LH-F026) | 鈥?|
| W3-C0 | Soft S0+1 fixed-card seed grind | **BLOCKED** (LH-F016) | 鈥?|
| W3-G1 | Pattern/grow exact-LNS reaches 鈮?65 | **weakened** best 133鈥?35 (LH-F046) | LNS from S0 / large-destroy |
| W3-R3 | rem3 residual elites repair to 165 | **REJECTED** s802; s801 soft TIMEOUT (LH-F045/046) | 鈥?|
| W3-A5 | Delete easy HS2 / joint HS2 from S0 then global max 鈬?165 | **REJECTED** MAX_PROVED 164 (LH-F051/052) | 鈥?|
| W3-G2 | Structured destroy+global max from grow/midset ⇒ 165 | **weakened** ≤139 (F053/066) | new cores |

## Frozen Wave2 facts (import)

- n100 `U_small` r=1: `INFEASIBLE_SCOPED`, hash `0e371058鈥?caac2` (negative control).
- n100 `U_small_r2` r=2: 4/4 `INFEASIBLE_SCOPED`, hash `a100c8b6鈥?e88`.
- Escalated rem/add/halo shells (medium/large/fullrem/spatial-halo/r3 variants): all `INFEASIBLE_SCOPED` under Agent A budgets 鈥?still **scoped**.
- n64 `U_small` r=1: `INFEASIBLE_SCOPED` + brute 3312 shells agree.
- Agent C: no V=0; plateaus match Gate1 empirical min direct-insertion 螖V.
- Red Team Wave2: A/B/C PASS; Gate2 PASS/CLOSED (`scratch/wave2/gate2_decision.md`); legal +1 none.
- Agent B Wave2: Type0 longs TIMEOUT size=0; many axes scoped INFEAS; `any_legal_plus1=false`; no candidates.
| W3-F1 | Blacklist Rem from S0 then global max ⇒ 165 | **weakened** best 139; certfreq60 MAX=134 (F060/061) | new families |

