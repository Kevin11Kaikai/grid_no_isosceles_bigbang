# Wave 2 Red Team Audit

**Role:** Independent Wave-2 Red Team (read-only vs searcher/verifiers/baselines/certified/Gate0–1)  
**Date:** 2026-08-12 (Gate2 close — Agent B COMPLETE)  
**Prior revision:** 2026-08-11 post-Agent-C (B PENDING)  
**Git HEAD at A/C audit:** `148808f422cba7e8ca232ebb4710b84782086342`  
**Agent B campaign commit (report):** `ffe7123b5d5f60a879ea599f75aee87d218c8159`  
**Clean-room scripts:** `scratch/red_team_wave2/run_audit_checks.py`, `run_agent_c_full_audit.py`

---

## Executive verdict

| Agent | Completeness | Red-team verdict | Critical flaws? |
|---|---|---|---|
| **A** | COMPLETE | **PASS** | **No** |
| **B** | COMPLETE (`agent_b_wave2_report.md` + smoke + n64/n100 long summaries) | **PASS** | **No** |
| **C** | COMPLETE | **PASS** | **No** |

**Gate 2:** A/B/C clean. Gate2 **CLOSED / PASS** by Main (`scratch/wave2/gate2_decision.md`). Legal +1: **none**.

**CRITICAL findings:** none.

---

## Checklist (required checks)

| # | Check | Result | Notes |
|---:|---|---|---|
| 1 | A r=1 negative-control vs Gate1 GLOBAL blocker LB; hash `0e371058…`; not TIMEOUT→INFEAS | **PASS** | Role=`negative_control`; `INFEASIBLE_SCOPED`; hash match |
| 2 | A r=2: \|R\|=2,\|A\|=3,\|S\|=165; hash `a100c8b6…`; scoped≠global UB | **PASS** | 4/4 primary `INFEASIBLE_SCOPED` |
| 3 | Spot-check lazy cuts | **PASS** | 15/15 witness cuts valid |
| 4 | B orbit mapping vs Gate1 | **PASS** | Offsets + mandatory/compare; smoke/long consistent |
| 5 | C incremental V vs exact `conflict_metric`; no card shrink | **PASS** | Summaries + elites + reproduce |
| 6 | TIMEOUT ≠ INFEASIBLE | **PASS** | A/C OK; B Type0 smoke/long correctly `TIMEOUT` (0 TIMEOUT rows carry infeasible_record) |
| 7 | Scoped UNSAT ≠ `C(n)≤…` | **PASS** | A scoped tokens; B infeasible_record notes; C no UB claim |
| 8 | Candidates clean-room | **PASS** | A none; B none (`any_legal_plus1=false`); C elites V>0 |
| 9 | No protected-path mutations | **PASS** | verifiers/baselines/certified untouched |
| 10 | No V=0 at \|S\|≥165/113 | **PASS** | A/B none; C min V = 3 / 2 |

### Agent C–specific checks (unchanged PASS)

| # | Check | Result |
|---:|---|---|
| C1–C6 | Fixed card; incr↔exact; no V=0; wording; external halo; no protected writes | **PASS** (see prior full audit) |

### Agent B–specific checks (closure)

| # | Check | Result |
|---:|---|---|
| B1 | Formal `agent_b_wave2_report.md` present | **PASS** |
| B2 | Smoke + long n64/n100 summaries present; campaign finished | **PASS** |
| B3 | `any_legal_plus1=false`; candidates empty | **PASS** |
| B4 | TIMEOUT ≠ INFEASIBLE on Type0 longs | **PASS** |
| B5 | Every `INFEASIBLE` row has scoped “not a global upper bound” note | **PASS** |
| B6 | Soft token `INFEASIBLE` vs `INFEASIBLE_SCOPED` | **ACCEPT** (RT-W2-02 soft closed) |

---

## Agent A (full) — PASS (unchanged)

Negative control `U_small` r=1 → `INFEASIBLE_SCOPED`, hash `0e371058…4caac2`.  
Primary `U_small_r2` r=2 → 4/4 scoped INFEAS, hash `a100c8b6…0e88`.  
Lazy cuts valid; no V=0; no global UB wording.  
**No REPAIR_REQUIRED.**

---

## Agent B — COMPLETE / PASS

### Deliverables verified

| Path | Role |
|---|---|
| `scratch/agent_b/agent_b_wave2_report.md` | Formal wave2 report |
| `axis_smoke_summary.json` | n64+n100 axis smoke (18 rows) |
| `n100_orbit_defect_summary.json` | Long pilots; `any_legal_plus1=false` |
| `n64_orbit_defect_summary.json` | Long pilots; `any_legal_plus1=false` |
| `manifest.jsonl` | Run ledger |
| `checkpoints/` | Atomic mid/final checkpoints |
| `src/search/orbit_defect_search.py` + tests | Exclusive module |

### Status discipline (clean-room counts)

- Smoke: **TIMEOUT=2**, **INFEASIBLE=16** (Type0 defect TIMEOUT; other axes mostly scoped INFEAS).
- Long n100: **TIMEOUT=8**, **INFEASIBLE=2**; best = Type0 defect TIMEOUT ~3000s, size=0, cand=None.
- Long n64: **TIMEOUT=3**, **INFEASIBLE=1**; best = Type0 defect TIMEOUT ~2400s, size=0, cand=None.
- **0** TIMEOUT rows with `infeasible_record`.
- **0** INFEASIBLE rows missing scoped non-global note.
- **0** legal +1 candidates.

### Wording

Report: “No new lower bound… Scoped INFEASIBLE/TIMEOUT only.”  
TIMEOUT explicitly distinguished from INFEASIBLE; scoped notes present.

### Ownership

Writes confined to `scratch/agent_b/` + exclusive module/tests. No certified/verifier/baseline mutations observed for Wave2 B.

**Agent B REPAIR_REQUIRED:** RT-W2-01 **CLOSED**; RT-W2-02 **CLOSED (soft accept)**.

---

## Agent C (full) — PASS (unchanged)

Best V=3 @165 (n100), V=2 @113 (n64); no V=0; external-halo repair; no LB/UB claims.  
**No REPAIR_REQUIRED.**

---

## File ownership / git sanity

- Protected paths untouched.  
- Observation (info): `src/search/greedy.py` dirty outside Wave-2 exclusives — Main RT-W2-04.

---

## REPAIR_REQUIRED

| ID | Severity | Owner | Item |
|---|---|---|---|
| ~~RT-W2-01~~ | ~~Block Gate2~~ | ~~B~~ | **CLOSED** — report + campaign freeze |
| ~~RT-W2-02~~ | ~~Soft~~ | ~~B~~ | **CLOSED** — accept `INFEASIBLE`+scoped note |
| ~~RT-W2-03~~ | ~~Soft~~ | ~~C~~ | **CLOSED** |
| RT-W2-04 | Info | Main | Review `greedy.py` dirty tree (non-blocking) |

---

## Gate2 readiness call

- **A: PASS. B: PASS. C: PASS.**  
- **Gate2: CLOSE / PASS** (no legal +1; Wave3 ranking authorized).  
- Evidence: `scratch/wave2/gate2_decision.md`, `scratch/wave2/gate2_manifest.json`.

---

## Artifacts written by Red Team

- `audits/wave2_red_team.md` (this file; B-complete revision)  
- `scratch/red_team_wave2/summary.json` (updated)  
- `scratch/red_team_wave2/agent_b_checks.json` (updated)  
- Prior: `run_audit_checks.py`, `run_agent_c_full_audit.py`, `agent_a_checks.json`, `agent_c_*.json`, `ownership_checks.json`, `agent_b_status_probe.json`
