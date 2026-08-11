# Wave 2 Red Team Audit

**Role:** Independent Wave-2 Red Team (read-only vs searcher/verifiers/baselines/certified/Gate0–1)  
**Date:** 2026-08-11 (updated after Agent C completion)  
**Git HEAD audited against:** `148808f422cba7e8ca232ebb4710b84782086342`  
**Clean-room scripts:** `scratch/red_team_wave2/run_audit_checks.py`, `run_agent_c_full_audit.py`

---

## Executive verdict

| Agent | Completeness | Red-team verdict | Critical flaws? |
|---|---|---|---|
| **A** | COMPLETE | **PASS** | **No** |
| **B** | Smoke + long/partial checkpoints; **`agent_b_wave2_report.md` still absent**; partial t0 s22 still running | **PASS (partial / provisional)** | **No** (so far) |
| **C** | COMPLETE (`agent_c_wave2_report.md` + summaries + elites + reproduce) | **PASS** | **No** |

**Gate 2:** A and C are clean. Gate2 **can close after B finishes clean** (same TIMEOUT≠INFEASIBLE / scoped / no false V=0 / no protected mutations discipline). **Cannot close now** — B report PENDING.

**CRITICAL findings:** none.

---

## Checklist (required checks)

| # | Check | Result | Notes |
|---:|---|---|---|
| 1 | A r=1 negative-control vs Gate1 GLOBAL blocker LB; hash `0e371058…`; not TIMEOUT→INFEAS | **PASS** | Role=`negative_control`; `INFEASIBLE_SCOPED`; hash match; distinguished from GLOBAL LB proof |
| 2 | A r=2: \|R\|=2,\|A\|=3,\|S\|=165; hash `a100c8b6…`; scoped≠global UB | **PASS** | 4/4 primary `INFEASIBLE_SCOPED` |
| 3 | Spot-check lazy cuts | **PASS** | 15/15 witness cuts valid |
| 4 | B orbit mapping vs Gate1 | **PASS (provisional)** | Offsets + mandatory/compare sets match; smoke consistent |
| 5 | C incremental V vs exact `conflict_metric`; no card shrink | **PASS** | Summaries + all 62 elites + reproduce; filename V matches recomputed V |
| 6 | TIMEOUT ≠ INFEASIBLE | **PASS** (A/C); B so far | C: heuristic (no CP-SAT INFEAS tokens). B long t0 correctly `TIMEOUT` |
| 7 | Scoped UNSAT ≠ `C(n)≤…` | **PASS** | A/B scoped notes; C: “no new lower bound / not certified” |
| 8 | Candidates clean-room | **PASS** | A none; C best/elites V>0 illegal as claimed; B no candidates |
| 9 | No protected-path mutations | **PASS** | verifiers/baselines/certified untouched |
| 10 | No V=0 at \|S\|≥165/113 | **PASS** | A none; C min elite V = 3 (n100) / 2 (n64) |

### Agent C–specific checks (post-completion)

| # | Check | Result |
|---:|---|---|
| C1 | Fixed \|S\|=165/113 always | **PASS** — summaries, seed_results, checkpoints, 62 elites |
| C2 | Incremental ↔ exact; elite recompute | **PASS** — `incremental_exact_agree_all`; 0 name/V mismatches |
| C3 | V=0 claims none | **PASS** — confirmed |
| C4 | TIMEOUT≠INFEAS; no global UB | **PASS** |
| C5 | External-halo repair (not S′-only) | **PASS** — `expanded_repair_pool` / `S_cup_halo_cup_deleted_cup_lowblocker`; external∉baseline n100=1706, n64=1028; all seeds `repair_accept>0` |
| C6 | No certified/verifier/baseline writes | **PASS** |

---

## Agent A (full) — unchanged PASS

Negative control `U_small` r=1 → `INFEASIBLE_SCOPED`, hash `0e371058…4caac2`.  
Primary `U_small_r2` r=2 → 4/4 scoped INFEAS, hash `a100c8b6…0e88`, \|R\|=2,\|A\|=3,\|S\|=165.  
Lazy cuts valid; no V=0; no global UB wording.  
**No REPAIR_REQUIRED.**

---

## Agent B — still PENDING

- **`scratch/agent_b/agent_b_wave2_report.md`:** absent  
- Resume log: long t0 s21 `DONE … status=TIMEOUT`; **`START long_n100_t0_partial_d1-8_s22`** still open; mid partial checkpoints continue  
- Prior provisional audit stands: orbit offsets match Gate1; TIMEOUT≠INFEASIBLE on smoke/long final; scoped notes OK; no candidates  

**REPAIR_REQUIRED before Gate2 close:** RT-W2-01 (final report + freeze outcomes); soft RT-W2-02 (`INFEASIBLE_SCOPED` naming).

---

## Agent C (full) — PASS

### Deliverables verified

| Path | Role |
|---|---|
| `agent_c_wave2_report.md` | Formal wave2 report |
| `n100_fixed165_summary.json` / `n64_fixed113_summary.json` | Campaign summaries |
| `manifest.jsonl` | 16 ledger lines (incl. smoke/pilot + reproduce 1201) |
| `elite_archive/**` | 62 elites |
| `checkpoints/candidates/**`, `seed_results/**` | Per-seed artifacts |
| `reproduce_best.json`, `campaign_meta.json` | Optional reproduce (~30 min, V=2 flat) |
| `src/search/fixed_cardinality_minconflict.py` | Read-only code review |

### Results (claimed = clean-room)

| Grid | Target \|S\| | Seeds | Best V | V=0? | Incr↔exact |
|---|---:|---:|---:|---|---|
| n=100 | 165 | 8 | **3** | No | Yes |
| n=64 | 113 | 4 | **2** | No | Yes |
| n=64 reproduce 1201 | 113 | 1 | **2** | No | Yes |

Clean-room (verifier A + B + `conflict_metric`): n100 seed101 V=3; n64 seed201 V=2; reproduce V=2; sample V10 elite V=10 — all card-correct, illegal, no V=0. All 62 elite filenames’ V tags match recomputed `conflict_count`.

### External-halo repair pool

Code implements `expanded_repair_pool` with policy meta `S_cup_halo_cup_deleted_cup_lowblocker` (Gate1 add/low-ΔV/easiest blockers/halo/partners + recently deleted). Docstring forbids S′-only deletion as sole operator. Moves (`1for1`, `2for2`, large, ejection) take `external` from `Gate1Pools.external_candidates()`. Halo sizes ~1828 (n100) / ~1090 (n64); thousands of external cells outside baseline. Campaign seeds all show `repair_accept > 0`.

### Wording / certification

Report: “**Not claimed:** no new lower bound; no certification; no record announcement.”  
Summaries: “not a lower-bound claim; not certified.”  
No `C(n)≤…` global UB; no TIMEOUT-as-INFEASIBLE (heuristic search).

### Ownership

Writes confined to `scratch/agent_c/` + exclusive module/tests. No `results/certified`, verifier, or baseline mutations.

**Agent C REPAIR_REQUIRED:** none (RT-W2-03 closed — formal report present).

---

## File ownership / git sanity

- Protected paths untouched.  
- Observation (info): `src/search/greedy.py` dirty outside Wave-2 exclusives — Main RT-W2-04.

---

## REPAIR_REQUIRED

| ID | Severity | Owner | Item |
|---|---|---|---|
| RT-W2-01 | **Block Gate2 close** | B | Finish campaign; write `agent_b_wave2_report.md`; keep TIMEOUT≠INFEASIBLE |
| RT-W2-02 | Soft | B | Prefer `INFEASIBLE_SCOPED` status token |
| ~~RT-W2-03~~ | ~~Soft~~ | ~~C~~ | **CLOSED** — formal report present |
| RT-W2-04 | Info | Main | Review `greedy.py` dirty tree |

---

## Gate2 readiness call

- **A: PASS. C: PASS.**  
- **B: PENDING** → Gate2 **HOLD**.  
- **After B completes clean:** Gate2 **can close** without further A/C rework (unless B introduces CRITICAL findings).

---

## Artifacts written by Red Team

- `audits/wave2_red_team.md` (this file; updated)  
- `scratch/red_team_wave2/summary.json` (updated)  
- `scratch/red_team_wave2/run_audit_checks.py`  
- `scratch/red_team_wave2/run_agent_c_full_audit.py`  
- `scratch/red_team_wave2/agent_a_checks.json`  
- `scratch/red_team_wave2/agent_b_checks.json` / `agent_b_status_probe.json`  
- `scratch/red_team_wave2/agent_c_checks.json` / `agent_c_full_checks.json`  
- `scratch/red_team_wave2/ownership_checks.json`
