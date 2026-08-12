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

### LH-F015 — W3 cert-involved e16 / certfreq-top48 Hamming r=2
- Evidence: `EXPERIMENTS/W3_cert_hamming/summary.json` — both `INFEASIBLE_SCOPED` in <5s (hashes `b59dcc1e…`, `8ac6c1d5…`).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD those U_ids**; nonlocal / broader Add and orbit enlarge remain live.

### LH-F016 — Agent C S0+1 soft seed grinding (Wave3 block)
- Evidence: Gate2 + elite Hamming-remove=0 analysis; `scratch/wave3/agent_c_s0plus1_block.md`.
- Level: process / basin diagnostic.
- Status: **BLOCKED** for primary budget; reopen only with remove≥2 or nonlocal free vars / new formulation.

### LH-F017 — W3 cert-involved e56 Add LBle6 r=2
- Evidence: `EXPERIMENTS/W3_cert_nonlocal/U_cert_involved_e56_Add_LBle6_r2_cheap.json` — `INFEASIBLE_SCOPED` (~24s, hash `529a5b31…`).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD that U_id**.

### LH-F018 — W3 cross-knn r=2 partitions (bridge / corners / left-right)
- Evidence: `EXPERIMENTS/W3_cross_community/summary.json` — all three `INFEASIBLE_SCOPED` (hashes `6afb5cb0…`, `c420f5f7…`, `a0cf4e5d…`).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD those r=2 U_ids**.

### LH-F019 — W3 cross-knn same Rem/Add at r=3
- Evidence: `EXPERIMENTS/W3_cross_community/r3_followup_summary.json` — all three `INFEASIBLE_SCOPED` in <70s.
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD those r=3 U_ids**; do not re-spend; need new Rem/Add structure or orbit path.

### LH-F020 — Forced exact HS2 delete for 8 easiest qs + large Add (r=2)
- Evidence: `EXPERIMENTS/W3_forced_hitset/summary.json` — 8/8 `INFEASIBLE_SCOPED` (~46s each). Rem=exact size-2 hitting set; Add=LB≤8∪halo; no legal 165.
- Level: `SCOPED_INFEASIBLE` (strong micro-obstruction for “clear one easy q then +2 adds”).
- Status: **DEAD that microproblem family for those 8 qs / Add defs**; pair-HS / multi-q / orbit remain.

### LH-F021 — Near-unrestricted multicomm Add Hamming (deprioritized)
- Evidence: `U_fullrem_Add_multicomm4_r2` and `U_v3cert_rem_Add_multicomm3_r2` TIMEOUT with |Add|≈9800.
- Level: `TIMEOUT_INCONCLUSIVE` (low information).
- Status: **Deprioritized**; do not spend primary long budget on ≈full-grid Add.

### LH-F022 — Joint exact-HS pairs (r=|Rem|) among easiest qs
- Evidence: `EXPERIMENTS/W3_joint_hs/summary.json` — 10/10 pairs `INFEASIBLE_SCOPED` at r=4 (disjoint HS unions; |Add|≈2206–2210; ~29–30s each; hashes e.g. `682e9889…`, `e2e0f7e2…`).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD that pair-HS forced-delete family** for sampled easiest-6 pairs; no Rem=3 overlaps; orbit / other formulations remain.

### LH-F023 — Type0 partial xlarge s511 (20min)
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/partial_t0_s511.json` — `TIMEOUT` size=0; universe `orb_t0_partial_core41_free321_def280_part24_h16`; 1562 rounds / 71759 cuts / ~1200s.
- Level: `TIMEOUT_INCONCLUSIVE` (not killed).
- Status: **Open but deprioritize short partial vs Type0/1 defect longs**; escalate only with new partial-orbit selection.

### LH-F024 — Type0 xlarge defect s501 (60min)
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/long_t0_defect_s501_xlarge.json` — `TIMEOUT` size=0; `orb_t0_defect_core41_free361_def320_part0_h18`; 2568 rounds / 86273 cuts / ~3600s; hash `2a1b8eb9…`.
- Level: `TIMEOUT_INCONCLUSIVE`.
- Status: **Still open**; enlarging alone not enough for +1 in 1h; next = other types / new defect construction / longer only if information-positive.

### LH-F025 — Type1 xlarge defect s601/s521 (40min)
- Evidence: `xlarge_t1_defect_s601.json` + `long_t1_defect_s521_xlarge.json` — both `TIMEOUT` size=0; universe `orb_t1_defect_core0_free321_def320_part0_h18`; ~407–429 rounds / ~68–77k cuts.
- Level: `TIMEOUT_INCONCLUSIVE`.
- Status: **Open**; Type1 remains cut-heavy / round-sparse vs Type0.

### LH-F026 — Forced rem≥2 fixed-card exchange (long)
- Evidence: `EXPERIMENTS/LH3_forced_exchange/forced_exchange_n100_long.json` — 6×180s seeds, best_V=29, any_v0=false (short batch earlier best_V=28). Leaves S0+1 basin but plateau far above V=0.
- Level: `WEAK_NEGATIVE` / search plateau (not scoped UNSAT).
- Status: **Deprioritize naive swap LS**; need stronger neighborhood or exact residual repair.

### LH-F027 — Type2 xlarge defect s702 (30min)
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/xlarge_t2_defect_s702.json` — `TIMEOUT` size=0; `orb_t2_defect_core0_free321_def320_part0_h18`; 438 rounds / 75512 cuts / ~1800s.
- Level: `TIMEOUT_INCONCLUSIVE`.
- Status: **Open**; continue Type3/4 enlarge then reconsider defect-pool construction.

### LH-F028 — Type3 xlarge defect s703 (30min)
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/xlarge_t3_defect_s703.json` — `TIMEOUT` size=0; `orb_t3_defect_core7_free327_def320_part0_h18`; 815 rounds / 97485 cuts / ~1800s; hash `85d59560…`.
- Level: `TIMEOUT_INCONCLUSIVE`.
- Status: **Open**; Type4 + cert_lb2 Type0 next.

### LH-F029 — Type4 xlarge defect s704 (30min)
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/xlarge_t4_defect_s704.json` — `TIMEOUT` size=0; `orb_t4_defect_core7_free327_def320_part0_h18`; 806 rounds / 100067 cuts / ~1800s; hash `39dd3b23…`.
- Level: `TIMEOUT_INCONCLUSIVE`.
- Status: **Open**; Types 0–4 xlarge all TIMEOUT≠INFEAS; cert_lb2 Type0 is next distinct U.

### LH-F030 — Type0 cert_lb2 defect s801 (45min)
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/certlb2_t0_defect_s801.json` — `TIMEOUT` size=0; `orb_t0_defect_core41_free361_def320_part0_h18_rkcert_lb2`; 4114 rounds / 50113 cuts / ~2700s; hash `979c41f0…`.
- Level: `TIMEOUT_INCONCLUSIVE`.
- Status: **Open but distinct U did not yield +1 in 45min**; escalate with ≥2h Type0 agent_c or other types+cert_lb2.

### LH-F031 — Type5 xlarge defect s805 (15min probe)
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/xlarge_t5_defect_s805.json` — `TIMEOUT` size=0; `orb_t5_defect_core6_free326_def320_part0_h18`; 626r/93339 cuts / ~900s.
- Level: `TIMEOUT_INCONCLUSIVE` (short probe).
- Status: **Not killed**; do not treat as INFEAS.

### LH-F032 — Type6 xlarge defect s806 (15min probe)
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/xlarge_t6_defect_s806.json` — `TIMEOUT` size=0; `orb_t6_defect_core6_free326_def320_part0_h18`; 605r/91889 cuts / ~900s.
- Level: `TIMEOUT_INCONCLUSIVE` (short probe).
- Status: **Not killed**; Types 0–6 xlarge all TIMEOUT≠INFEAS under tested budgets.


### LH-F033 ? Type0 fix_core=True vs soft_core (enlarged U)
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/fixcore_compare.json` ? fix_core `INFEASIBLE` in ~8s (scoped); soft_core `TIMEOUT` 600s size=0 on same free241/def200/h14.
- Level: `SCOPED_INFEASIBLE` (fix) + `TIMEOUT_INCONCLUSIVE` (soft).
- Status: **fix_core killed for this U**; soft_core remains the live TIMEOUT path (default). Not a global UB.

### LH-F034 ? Type0 xlarge defect 2h s901
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/long2h_t0_defect_s901.json` ? `TIMEOUT` size=0; `orb_t0_defect_core41_free361_def320_part0_h18`; 4108 rounds / 91864 cuts / ~7200s; hash `e8dddbff?`.
- Level: `TIMEOUT_INCONCLUSIVE`.
- Status: **Still open**; 2h on agent_c U did not produce FEASIBLE. Prefer new encodings / residual repair over further same-U wall-time.

### LH-F034 �� Type0 xlarge defect 2h s901
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/long2h_t0_defect_s901.json` �� `TIMEOUT` size=0; `orb_t0_defect_core41_free361_def320_part0_h18`; 4108 rounds / 91864 cuts / ~7200s; hash `e8dddbff��`.
- Level: `TIMEOUT_INCONCLUSIVE`.
- Status: **Still open**; 2h on agent_c U did not produce FEASIBLE. Prefer new encodings / residual repair over further same-U wall-time.

### LH-F035 �� n64 forced HS2 r=2 (4 easiest LB=2 qs)
- Evidence: `EXPERIMENTS/W3_n64_hitset/summary.json` �� 4/4 `INFEASIBLE_SCOPED` in ~1s.
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD that n64 micro family**; aligns with n100 LH-F020.

### LH-F035 �� Type1 cert_lb2 defect s821 (40min)
- Evidence: `EXPERIMENTS/W3_orbit_enlarge/certlb2_t1_defect_s821.json` �� `TIMEOUT` size=0; `orb_t1_defect_core0_free321_def320_part0_h18_rkcert_lb2`; 432 rounds / 75187 cuts / ~2400s.
- Level: `TIMEOUT_INCONCLUSIVE`.
- Status: **Open**; cert_lb2 on Type1 did not beat agent_c Type1 TIMEOUT profile.

### LH-F036 �� rem2 residual full-involved core extend to 165
- Evidence: `EXPERIMENTS/W3_rem2_residual/core_extend_s504.json` �� legal core size 121 from V=25 rem>=2 set; greedy max 164; exact extend `INFEASIBLE_SCOPED` (~541s, 296 rounds / 244k cuts).
- Level: `SCOPED_INFEASIBLE` (this core cannot reach 165).
- Status: **DEAD for that core**; try soft-strip / other rem2 seeds; max legal containing this core is <=164.

### LH-F037 �� rem2 soft-strip core extend (6min each)
- Evidence: `EXPERIMENTS/W3_rem2_residual/soft_core_extend_summary.json` �� 8 plans all `TIMEOUT` (cores 130�C160); full-involved strip was INFEAS (LH-F036).
- Level: `TIMEOUT_INCONCLUSIVE` (soft) + prior scoped INFEAS (full strip).
- Status: **Escalate largest cores (160/155)** with longer budget; not yet killed.

### LH-F038 �� rem2 soft long extend core160/155
- Evidence: `EXPERIMENTS/W3_rem2_residual/soft_core_extend_long.json` �� core160 need=5: 30min TIMEOUT (4451r/105k cuts); core155 need=10: 20min TIMEOUT.
- Level: `TIMEOUT_INCONCLUSIVE`.
- Status: **Open**; maximize-from-core160 launched to prove max size.

### LH-F039 �� rem2 soft cores capacity / brute
- Evidence: `EXPERIMENTS/W3_rem2_residual/soft_brute_capacity.json` + `addable_screen.json` �� soft cores ~150�C160 typically have addable��need; seed504 k=5 CAPACITY_FAIL (4<5 ? max��164); seed601 k=5/10/15 unique combos all `INFEASIBLE_SCOPED`.
- Level: `SCOPED_INFEASIBLE` / `CAPACITY_FAIL`.
- Status: **Soft near-full cores dead for these seeds**; prefer full-involved strip + addable-restricted exact extend.

### LH-F040 �� rem2 full-involved strip + addable-restricted extend
- Evidence: `EXPERIMENTS/W3_rem2_residual/fullstrip_addable_extend.json` �� 5/5 seeds `INFEASIBLE_SCOPED` in <0.2s each (cores 104�C121; free=addable only).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD rem2 residual-repair family** for sampled seeds (soft+full strip); need new illegal seeds or non-residual constructions.

### LH-F041 �� Forced rem>=3 fixed-card exchange
- Evidence: `EXPERIMENTS/W3_rem3_exchange/forced_exchange_rem3.json` �� 6��150s, best_V=42, any_v0=false (worse than rem2 best_V��25).
- Level: `WEAK_NEGATIVE` / plateau.
- Status: **Deprioritize naive rem3 swap LS**; residual/exact needed if revisiting.

### LH-F042 — Spatial-block Hamming Rem/Add r=2 (new U_ids)
- Evidence: `EXPERIMENTS/W3_spatial_hamming/summary.json` — 8/8 `INFEASIBLE_SCOPED` (knn Rem 24/32 × opp/outer Add; ~57s total).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD that spatial-block Hamming family**; not a global UB. Prefer dispersed Rem or non-Hamming constructions.

### LH-F043 — rem3 soft/partial exact residual s802
- Evidence: `EXPERIMENTS/W3_rem3_residual/soft_extend_s802.json` + `partial_extend_s802.json` — soft core98 need67 free173 `INFEASIBLE_SCOPED` (~0.8s); partial core143 need22 free22 `INFEASIBLE_SCOPED`.
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD for rem3 elite s802 cores**; seed 801 residual still in flight. Does not kill rem3 construction broadly.

### LH-F044 — Dispersed-stride Hamming Rem/Add r=2
- Evidence: `EXPERIMENTS/W3_dispersed_hamming/summary.json` — 3/3 `INFEASIBLE_SCOPED` (stride Rem 24–40 × outer Add).
- Level: `SCOPED_INFEASIBLE`.
- Status: **DEAD dispersed-stride Hamming family** (with spatial knn-block LH-F042). Prefer non-Hamming / pattern grow.

### LH-F045 — rem3 exact residual elites s802/s801
- Evidence: `EXPERIMENTS/W3_rem3_residual/summary.json` + `core_maximize_s802.json` — s802 soft/partial INFEAS; maximize soft-core → legal **164** (not +1); s801 soft `TIMEOUT` (~32s escalate-open), partial INFEAS.
- Level: `SCOPED_INFEASIBLE` / `TIMEOUT_INCONCLUSIVE` (s801 soft).
- Status: **Deprioritize rem3 residual for these elites**; optional long soft s801 only if pattern/from-scratch stall.

### LH-F042 �� From-scratch grow long batch (partial)
- Evidence: `EXPERIMENTS/W3_from_scratch/grow_long.json` �� best legal size **137** (boundary_first); far below 165; matches prior grow plateau ~135.
- Level: `WEAK_NEGATIVE`.
- Status: **Deprioritize plain grow**; need stronger destroy/refill or structure.

### LH-F046 — Parallel harvest: pattern-LNS / grow-LNS / grow_v3 / rem3 long
- Evidence:
  - `EXPERIMENTS/W3_pattern_lns/summary_v2.json` — best_final **133** (annulus); dual OK; `beats_164=false`.
  - `EXPERIMENTS/W3_grow_lns/summary.json` — best_final **134**; dual OK; `beats_164=false`.
  - `EXPERIMENTS/W3_from_scratch/grow_v3.json` — best_size **135**; dual OK.
  - `EXPERIMENTS/W3_rem3_residual/soft_extend_s801_long.json` — soft core87 need78 `TIMEOUT` ~1800s (73 rounds / 4860 cuts).
  - `core_maximize_s802.json` — maximize soft core → legal **164** with incumbent hash `8a84216d…` (not a new construction).
- Level: `WEAK_NEGATIVE` (grow/pattern plateau) + `TIMEOUT_INCONCLUSIVE` (s801 soft) + `SCOPED` (s802 max=164).
- Status: **Deprioritize plain pattern/grow LNS at 10–15min**; escalate destroy-refill from S0/legal-135. rem3 residual elites closed except optional mega-budget on s801 only if needed.

### LH-F047 — One-shot large destroy+region MILP on S0
- Evidence: `EXPERIMENTS/W3_large_destroy/summary.json` — 13 plans (frames d2–d5, boxes, row bands); all `final_size=164`; several recover incumbent hash `8a84216d…`; center boxes remove 0 (empty-center). `any_plus=false`.
- Level: `SCOPED` region-optimal under tested destroys (not global UB).
- Status: **Region-local repair from S0 does not beat 164** on these plans; try global-refill after destroy / long LNS.

### LH-F048 — Global refill after frame destroy of S0
- Evidence: `EXPERIMENTS/W3_global_refill/summary.json` — frame_d2: `MAX_PROVED` best=164 (=incumbent hash); frame_d3/d4: best=164 then escalate `TIMEOUT` (not proved). `any_plus=false`.
- Level: `SCOPED_MAX` (d2) + `TIMEOUT_INCONCLUSIVE` (d3/d4 escalate).
- Status: **d2 kill: no legal >164 containing the depth-2 frame complement core**; escalate d3/d4 with longer prove budget.

### LH-F049 — Exact-LNS from S0 (30min) + global-refill long d3/d4
- Evidence:
  - LNS from S0: terminal `937031` — `final_size=164`, 131044 MILP iters, **0 improvements**, incumbent hash.
  - `EXPERIMENTS/W3_global_refill/summary_long.json` — frame_d3/d4_long 20min each: best=164, escalate `TIMEOUT` (not MAX_PROVED), incumbent hash.
- Level: `WEAK_NEGATIVE` (S0 LNS plateau) + `TIMEOUT_INCONCLUSIVE` (d3/d4 prove >164).
- Status: **S0 region-LNS unlikely to leave 164 in 30min**; d2 still the only proved max=164 under frame complement.

### LH-F050 — Exact-LNS from legal S0 / grow (long)
- Evidence: `EXPERIMENTS/W3_lns_from_legal/summary.json` — S0: 30min / 131k MILP, 0 improvements, size=164; grow124: 25min → **132** (plateau early). `any_plus=false`.
- Level: `WEAK_NEGATIVE`.
- Status: **Deprioritize stock exact-LNS region repair from S0/grow** at these budgets.

### LH-F051 — HS2-delete then global maximize (8 easiest qs)
- Evidence: `EXPERIMENTS/W3_hs2_delete_max/summary.json` — 8/8 `MAX_PROVED` best=164 (=incumbent hash); each core=162, free=3, cap=165 but cannot select all 3.
- Level: `SCOPED_MAX` (strong micro-obstruction: keep S0\{hs2} ⇒ max legal 164).
- Status: **DEAD \"delete one easy HS2 then refill to 165 keeping the rest of S0\"**; aligns with LH-F020 Hamming INFEAS.

### LH-F052 — Joint HS2-pair delete + global maximize (8 pairs)
- Evidence: `EXPERIMENTS/W3_joint_hs2_delete_max/summary.json` — 8/8 `MAX_PROVED` best=164 (=incumbent hash `8a84216d…`); cores=160, free=6, cap=166.
- Level: `SCOPED_MAX`.
- Status: **DEAD \"keep S0 minus two disjoint easy HS2s and refill to 165\"**; extends LH-F051 / W3-A4.

### LH-F053 — Grow-134 structured destroy + global maximize
- Evidence: `EXPERIMENTS/W3_grow_destroy_max/summary.json` — grow best 134; destroy best **138** (parity_even TIMEOUT 300s); frame_d3/d4 `MAX_PROVED` 134; several `CAPACITY_FAIL` (<165). `any_plus=false`.
- Level: `HEURISTIC / SCOPED_MAX / TIMEOUT_INCONCLUSIVE` (parity TIMEOUT ≠ proved max).
- Status: **Deprioritize shallow grow-core frame/random destroys**; escalate long parity / large free-pool maximize only if information-positive.

### LH-F054 — Cert-freq Rem top16/32/48/64 + global maximize on S0
- Evidence: `EXPERIMENTS/W3_certfreq_destroy/summary.json` — 4/4 `MAX_PROVED` best=164 (=incumbent hash). Even core=100 (top64 Rem) free=203 recovers only S0.
- Level: `SCOPED_MAX`.
- Status: **DEAD \"delete top cert-involved points from S0 then refill past 164\"** under these Rem sizes.

### LH-F055 — Parity-even long maximize 30min from grow-134 core
- Evidence: `EXPERIMENTS/W3_parity_long/summary.json` — `TIMEOUT` best=138 (same plateau as 5min); 54 rounds / 285660 cuts / ~1800s; dual OK hash `5855ccab…`.
- Level: `TIMEOUT_INCONCLUSIVE` (not proved max; not +1).
- Status: **Deprioritize same parity cut-loop wall**; try LNS from midset / new cores.

### LH-F056 — Midset (parity 137) aggressive LNS + redestroy
- Evidence: `EXPERIMENTS/W3_midset_lns/summary.json` — LNS 3×10min / 0 improvements size=137; redestroy k30 CAPACITY_FAIL cap160; k50/70 TIMEOUT ≤137.
- Level: `WEAK_NEGATIVE / TIMEOUT_INCONCLUSIVE`.
- Status: **Deprioritize stock LNS from ~137 parity midsets** at these destroy fracs.

### LH-F057 — Grow-union universe maximize (cold LB≥130)
- Evidence: `EXPERIMENTS/W3_grow_union_universe/summary.json` — universe=1087 (8 grows+S0); `TIMEOUT` best=0 / 26 rounds / 241k cuts / 1200s.
- Level: `TIMEOUT_INCONCLUSIVE` + **method bug** (cold LB≥130 never recorded a legal seed).
- Status: **Invalid as capacity/UB claim**; rerun warm-started (`summary_warm.json`).

### LH-F058 — Grow-union warm maximize 25min
- Evidence: `EXPERIMENTS/W3_grow_union_universe/summary_warm.json` — warm start 131; `TIMEOUT` best=131 (no improve); 32 rounds / 241032 cuts / ~1500s.
- Level: `TIMEOUT_INCONCLUSIVE` / `WEAK_NEGATIVE` for this universe+cut-loop.
- Status: **Deprioritize plain cut-maximize over multi-grow∪S0 at ~25min**; need better search or different U.

### LH-F059 — Large random Rem from S0 + global maximize
- Evidence: `EXPERIMENTS/W3_random_large_rem/summary.json` — Rem80/100: `TIMEOUT` best=164 (=incumbent hash) in ~900s (recovered S0; not proved max). Rem120: early stall best=44 (core) after huge cut dump — `TIMEOUT_INCONCLUSIVE`/tool stress.
- Level: `TIMEOUT_INCONCLUSIVE` (not UB); weak signal that large Rem still returns to S0 basin quickly for k≤100.
- Status: Open for longer prove-≥165 under Rem80 cores; not a +1.

### LH-F060 — Forbid-Rem refill (blacklist deleted S0 points)
- Evidence: `EXPERIMENTS/W3_forbid_rem_refill/summary.json`
  - k=40: `CAPACITY_FAIL` cap=127
  - k=60: `MAX_PROVED` 128 (cap=169) — scoped max ≪165
  - k=80: `TIMEOUT` best=134 dual OK (left S0 basin; not +1)
- Level: `CAPACITY_FAIL / SCOPED_MAX / TIMEOUT_INCONCLUSIVE`.
- Status: **Leaving S0 by blacklisting Rem is necessary but insufficient at these seeds**; escalate k=80 long / structured Rem.

### LH-F061 — Long forbid-Rem (30min ×3)
- Evidence: `EXPERIMENTS/W3_forbid_rem_long/summary.json`
  - rand80: TIMEOUT best=134 (~30m)
  - rand100: TIMEOUT best=**139** (~30m)
  - certfreq60 forbid: `MAX_PROVED` 134 in ~4s (cap free=94)
- Level: `TIMEOUT_INCONCLUSIVE / SCOPED_MAX`.
- Status: certfreq60-forbid **dead** at max 134; rand100 forbid open but plateau ≪165.
