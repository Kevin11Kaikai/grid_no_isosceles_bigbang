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

### LH-F001 — easiest-16 pairwise co-insertion at r=2
- Evidence: `EXPERIMENTS/LH1_blocker_pair/blocker_pair_pilot_n100.json` — joint_VC=4 for all 120 pairs; 0 pair-legal cores; 0 feasible 165.
- Level: necessary-condition + enumeration under cover Rem.
- Status: **DEAD** for “two exact-2 cells with |R|=2”.

### LH-F002 — low-LB complementary pairs (broader sample)
- Evidence: `mixed_pair_vc_scan.json`, `complementary_blocker_pairs.json` (85 qs / 3570 pairs): 0 with joint_VC≤3.
- Level: finite verified on sampled qs (not all C(9836,2)).
- Status: **DEAD as primary hope** that easy cells pair cheaply; reopen only with proof of complementary high-LB pairs or full-pair certificate search.

### LH-F003 — V=3/V=2 elite residual refill
- Evidence: `LH1_v3_residual/*`, `LH1_n64_sandbox/n64_v2_residual_refill.json` — cores legal; refill to 165/113 in involved∪halo (and expanded R_free) `INFEASIBLE_SCOPED`.
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD those refill universes**; do not spend primary budget re-refilling same elites without nonlocal free-sets.

### LH-F004 — U_fullrem_LBle4 r=2 and r=3
- Evidence: `LH1_hamming_newU/shell_r2_seed1.json`, `shell_r3_LBle4_seed1.json` — both `INFEASIBLE_SCOPED` (292 vars, hash `8214a82a…`).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD** that Add filter at r≤3 with full Rem.

### LH-F005 — U_exact2covers_LBle5_r2
- Evidence: `LH2_single_q_large_add/shell_r2_seed1.json` — `INFEASIBLE_SCOPED` (356 vars).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD**.

### LH-F006 — r=4 easiest-pair / LBle5 CP-SAT
- Evidence: `r4_easiest_pair_micro.json` + `cpsat_r4_shells.json` — paircover and fullrem LBle5 at r=4 both `INFEASIBLE_SCOPED`.
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD** LB≤5 Add at r≤4 with those Rem definitions.

### LH-F007 — frame R2 fullrem r=4
- Evidence: `LH2_frame_shells/U_fullrem_frameR2_r4.json` — `INFEASIBLE_SCOPED` (1084 adds).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD** outer ring≤2 Add at r=4.

### LH-F008 — n64 exact1-cover Rem r=1
- Evidence: `LH2_n64_cert_r1/shell_r1_seed1.json` — `INFEASIBLE_SCOPED` (20 vars).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD** that tiny cert universe (score U_small already dead).

### LH-F009 — conflict-eject fixed-card (seeds 301–304)
- Evidence: best V=4 in 75s×4; no V=0.
- Level: `HEURISTIC`.
- Status: operator underperforms Wave2 C (V=3); deprioritize unless redesigned.

### LH-F010 — frame fullrem r=2 long (R=2 and R=6)
- Evidence: `U_fullrem_frameR2_r2_long.json`, `U_fullrem_frameR6_r2_long.json` — both `INFEASIBLE_SCOPED`.
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD** frame-only Add at r=2 with full Rem.

### LH-F011 — forced-exchange soft min-V (r_min=2)
- Evidence: best V=28 (seeds 401–404); no V=0.
- Level: `HEURISTIC`.
- Status: weak operators; keep constraint idea, change neighborhood.

### LH-F012 — cert-seeded paircover + residual refill (partial)
- Evidence: `LH3_cert_seeded/cert_seeded_minv_partial.json` — 35 trials, min V_seed=25, 0 legal.
- Level: `HEURISTIC` / partial.
- Status: no V=0 signal; do not grind same 45s residual refills.

### LH-F013 — annulus pattern + exact LNS
- Evidence: `LH3_patterns/lns_from_annulus.json` — 132→136 in 420s; no path to 164.
- Level: `HEURISTIC`.
- Status: weak basin; needs S0-core fusion or different generator.

### LH-F014 — midband fullrem r=2 @600s
- Evidence: `LH2_midband_shells/U_fullrem_midband10_26_r2_long.json` — TIMEOUT_INCONCLUSIVE.
- Level: TIMEOUT (not INFEAS).
- Status: open but expensive; deprioritize vs orbit enlarge / hybrid.

### IMP-F008 — Wave2 Agent B orbit/defect freeze (no +1)
- Evidence: `scratch/agent_b/agent_b_wave2_report.md`, `n100_orbit_defect_summary.json`, `n64_orbit_defect_summary.json`, `axis_smoke_summary.json`.
- Smoke: Type0 defect TIMEOUT; types 1–6 mostly scoped INFEASIBLE (with non-global notes).
- Long best: n100 Type0 defect/partial TIMEOUT size=0; n64 Type0 defect TIMEOUT size=0; `any_legal_plus1=false`.
- Level: mix `SCOPED_INFEASIBLE` + `TIMEOUT_INCONCLUSIVE` — **not** global empty.
- Status: **Wave2 B route frozen as no-+1 under those universes/budgets**; Type0 TIMEOUT remains **open** for enlarged/longer models (LH-4). Do not re-label TIMEOUT as INFEASIBLE.

