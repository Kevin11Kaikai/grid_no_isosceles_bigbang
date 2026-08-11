# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-11 ~19:00 local  
**Git HEAD (pre-this-commit):** `7d1f4f2` (origin/master synced)  
**Phase:** LH-1 negatives recorded → LH-2 new Hamming universe + route reallocation

## Incumbent

- n=64: **112** DUAL_VERIFIED (`47d42165…e9c292`)
- n=100: **164** DUAL_VERIFIED (`8a84216d…bdc1`)
- No promotion this run.

## LH-1 results (meaningful)

| Experiment | Result | Level |
|---|---|---|
| easiest-16 pairs joint VC | **120/120 joint_VC=4** → no r=2 co-insertion of any two exact-2 cells | necessary-condition cheap-kill |
| mixed easy2×lb3/lb4 (top20) | joint_VC ∈ {4,5,6}; **0 ≤3** | cheap-kill |
| complementary pairs (85 qs, 3570 pairs) | **0 joint_VC≤3**; many ≥6 | strong negative on low-LB complementarity |
| V=3 residual structure | 9 elites: always **3 witnesses**, **6–7 involved**; cores legal after strip | observation |
| V=3 residual refill (involved∪halo) | 9/9 `INFEASIBLE_SCOPED` | scoped |
| V=3 expanded residual (R_free 2–3) | 4 elites ×2 radii: all `INFEASIBLE_SCOPED` | scoped |
| n64 V=2 residual refill | 6/6 `INFEASIBLE_SCOPED` | scoped (sandbox) |
| single-q cover + 2 adds (limited pool) | 0 legal 165 | heuristic/scoped |

## Interpretation

1. Score-U and easiest-cell co-insertion are dead for r=2: any two exact-2 cells need **≥4 deletions**.
2. Soft V=3/V=2 elites are **refill-traps**: legal cores cannot regain target cardinality inside large local halos (CP-SAT).
3. Need Add cells with **structurally shared** blockers (not low individual LB), or higher r, or non-baseline-centered starts (orbit / from-scratch fixed-card).

## Live allocation (rebalanced)

| Slice | Focus |
|---|---|
| 35% A | `U_fullrem_LBle4_r2` + then LB≤5 / r=3 if needed |
| 20% B | Orbit/defect cheap diversify (avoid Wave2 TIMEOUT grind) |
| 15% C | New fixed-card operators OR abandon refill-from-elite |
| 15% D | Nonlocal Rem (blocker-cover Rem for single q + large Add) |
| 10% critic/verify | Keep scopes honest |
| 5% abstraction | Update FAILED/PROVED |

## Immediate next actions

1. **NOW:** Run `U_fullrem_LBle4_r2` CP-SAT (Add from `blocker_detail_n100.json.gz`).
2. Single-q exact-2 Rem + large Add (all LB≤5) r=2 micro-shells.
3. Orbit Type1/2 smoke with short budget (B).

## Standing order

Push meaningful checkpoints to `origin/master` (no force). Continue until Hard Stop.
