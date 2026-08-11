# Wave 2 Search Agent A Report

**Agent:** Search Agent A (Hamming-shell + conflict multi-region)  
**Git commit:** `148808f422cba7e8ca232ebb4710b84782086342`  
**Solver:** OR-Tools CP-SAT 9.15 via `.venv_solver\Scripts\python.exe`  
**Workers:** 5 (~25% of 20 logical CPUs; A+B+C ≤75%, ≥2 free)  
**CRITICAL_CONTRADICTION:** none  
**V=0 |S|≥165/113 candidate:** none  

---

## 1. Deliverables

| Path | Role |
|---|---|
| `src/search/hamming_shell_conflict.py` | Hamming-shell CP-SAT + lazy witness cuts |
| `src/search/conflict_multiregion.py` | Pure spatial / conflict / hybrid pilots |
| `tests/test_hamming_shell_conflict.py` | 9 unit tests (all PASS under `.venv_solver`) |
| `scratch/agent_a/manifest.jsonl` | Run log |
| `scratch/agent_a/negative_control_n100_r1.json` | n100 r=1 negative control |
| `scratch/agent_a/hamming_n100_r2_summary.json` | n100 r=2 (+ halo/r3 follow-ups) |
| `scratch/agent_a/hamming_n64_r1_summary.json` | n64 r=1 |
| `scratch/agent_a/multiregion_pilot_summary.json` | 6 comparative pilots |
| `scratch/agent_a/hamming/**` | Per-run JSON + halo universe defs |
| `scratch/agent_a/checkpoints/**` | Atomic checkpoints |
| `scratch/agent_a/multiregion/**` | Per-mode pilot JSON |

Universe hash recipe (Gate-1 Main):  
`sha256(json.dumps({"rem": sorted(tuples), "add": sorted(tuples)}, separators=(",", ":")))`.

Verified before long pilots:

- `U_small` (n100): `0e371058…4caac2`
- `U_small_r2` (n100): `a100c8b6…0e88` (32 rem + 44 add = 76 vars)

---

## 2. Negative control (n100, r=1, `U_small`)

- **Status:** `INFEASIBLE_SCOPED`
- **Hash:** `0e371058…` (match)
- **Rounds / cuts / best illegal V:** 17 / 49 / 5
- **Wall:** <1 s (budget was 300 s)
- **Interpretation:** Encoding sanity OK; aligns with Gate-1 global r=1 exclusion.  
  **Not** FEASIBLE+legal (would have been CRITICAL). **Not** TIMEOUT-as-INFEAS.

Full enumeration confirm: `C(16,1)×C(32,2)=7936` shells, **0 legal**, best V=5.

---

## 3. Primary: n100 r=2 on frozen `U_small_r2`

Four deterministic configs (seeds 1–3 asymmetric; seed 4 symmetric destroy):

| Config | Status | Rounds | Cuts | Best illegal V |
|---|---|---:|---:|---:|
| seed1 asym | INFEASIBLE_SCOPED | 15 | 81–91 | 7–11 |
| seed2 asym | INFEASIBLE_SCOPED | 15 | 91 | 11 |
| seed3 asym | INFEASIBLE_SCOPED | 15 | 81 | 10 |
| seed4 sym | INFEASIBLE_SCOPED | 5 | 25 | 13 |

All concluded in ≪ budget (seconds). Seed-dependent random objectives diversify incumbents; infeasibility is stable.

**Claim wording:** INFEASIBLE under `scope=(n=100,r=2,U_small_r2,halo=none,symmetry,seed,…)` only — **not** a global upper bound on C(100).

---

## 4. Halo escalate (new U_ids / hashes)

| U_id | Vars | Status | Notes |
|---|---:|---|---|
| `U_medium` r=2 | 96 | INFEASIBLE_SCOPED | Agent C medium |
| `U_large` r=2 | 176 | INFEASIBLE_SCOPED | Agent C large |
| `U_fullrem_Asmall_r2` | 208 | INFEASIBLE_SCOPED | Rem=all S0; Add=`U_small_r2` add |
| `U_fullrem_Alarge_r2` | 292 | INFEASIBLE_SCOPED | Rem=all S0; Add=`U_large` add |
| `U_score_spatial_halo_r2` | 1144 | INFEASIBLE_SCOPED | 360 rounds, 9268 cuts, ~54 s |
| `U_fullrem_Alarge_r3` | 292 | INFEASIBLE_SCOPED | r=3 follow-up |
| `U_fullrem_Ahalo2_r3` | 564 | INFEASIBLE_SCOPED | Rem=all; Add≤400 Chebyshev-2 halo |

Even with **unrestricted Rem (=S0)** and Add pools up to 400 cells, no legal |S|=165 appeared at r=2 or r=3 inside those Add restrictions.

---

## 5. n64 r=1 on C `U_small` (36 vars)

| Seed | Status | Rounds | Cuts | Best V |
|---:|---|---:|---:|---:|
| 1 | INFEASIBLE_SCOPED | 13 | 46 | 6 |
| 2 | INFEASIBLE_SCOPED | 13 | 45 | 4 |

**Full enumeration:** `C(12,1)×C(24,2)=3312` shells, **0 legal**, best V=2 — agrees with CP-SAT (model soundness check).

---

## 6. Multi-region comparative pilots

Modes: `pure_spatial` vs `conflict_driven` (spatial-knn6 far bridges; **not** giant projection CC) vs `hybrid`.  
Budgets: n64 ~12 min; n100 ~10 min each.

| n | Mode | Best size | Improved? | Iters |
|---:|---|---:|---|---:|
| 64 | pure_spatial | 112 | no | 69805 |
| 64 | conflict_driven | 112 | no | 2 |
| 64 | hybrid | 112 | no | 3 |
| 100 | pure_spatial | 164 | no | 38738 |
| 100 | conflict_driven | 164 | no | 14466 |
| 100 | hybrid | 164 | no | 25263 |

Conflict/hybrid on n64 are iteration-poor because knn-community bboxes make each MILP expensive; still no +1.

---

## 7. Method notes / soundness

- Every lazy cut comes from an oracle witness triple on a reconstructed shell incumbent.
- Cut evaluation check: all witnesses of a sample incumbent violate their encoded cuts.
- Zero-witness incumbents are dual-checked (`oracle_verifier` + `independent_verifier` + `conflict_metric` V=0) before `FEASIBLE_LEGAL`.
- Unit tests cover cardinality, reconstruction, universe hash stability, tiny legal/illegal sets, V/verifier consistency, worker cap.

---

## 8. Wall time (approx)

- Implementation + tests + Hamming/halo/r3 probes: ~0.5–0.7 h  
- Multi-region six pilots: ~1.2 h  
- **Total Agent A wall ≈ 1.7–2.0 h** (under 4–6 h budget; Hamming scopes closed early, time spent on escalate + multi-region)

---

## 9. Return brief for Main

- **Negative control:** INFEASIBLE_SCOPED (expected); no CRITICAL.  
- **n100 r=2 `U_small_r2`:** 4/4 INFEASIBLE_SCOPED; halo/full-rem escalations also scoped INFEAS (r=2 and r=3 on large Add).  
- **n64 r=1:** 2/2 INFEASIBLE_SCOPED; confirmed by full enum.  
- **V=0 candidate:** none.  
- **Multi-region:** no size improvement on 112/164.  
- **Files:** see §1.  
- **Do not** promote any of these to a global UB.
