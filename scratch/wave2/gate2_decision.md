# Gate 2 Decision (Wave 2 Search Pilots)

**Date:** 2026-08-12  
**Role:** Main synthesis (Gate 2)  
**Depends on:** Gate 1 `WAVE2_READY` (`scratch/audit/gate1_decision.md`)  
**Inputs:** Search Agents A/B/C wave2 reports + Red Team Wave2 audit (B closed)  
**Synthesis commit base:** `ffe7123b5d5f60a879ea599f75aee87d218c8159` (pre-Gate2 HEAD)

---

## 1. Final verdict

**Gate 2: PASS / CLOSED**

**Breakthrough / legal +1:** **NONE** (n100→165, n64→113)

**Wave-3 readiness:** `WAVE3_READY` (route ranking + focused long runs)

**New lower-bound claims:** **NONE** (forbidden and unused)

This closes Wave 2 pilots under plan G2 criteria: each search route completed ≥1 pilot with scoped status; Red Team has no CRITICAL flaws; A/B/C all COMPLETE with PASS.

---

## 2. Checklist (plan §10 G2)

| Criterion | Result |
|---|---|
| Gate 1 passed / Wave2 authorized | **PASS** |
| Agent A Hamming + multi-region pilots complete | **PASS** (`scratch/agent_a/`) |
| Agent B orbit/core/defect pilots complete | **PASS** (`scratch/agent_b/`; report present) |
| Agent C fixed-card min-V pilots complete | **PASS** (`scratch/agent_c/`) |
| Red Team spot-checks A/B/C | **PASS** (A/C prior; B closed this Gate2) |
| Each route ≥1 scoped status outcome | **PASS** |
| TIMEOUT ≠ INFEASIBLE discipline | **PASS** |
| Scoped UNSAT ≠ global `C(n)≤…` | **PASS** |
| Any dual-verified legal \|S\|≥165/113 | **No** |
| Infra crash blocking G3 | **None** |

---

## 3. Cross-agent synthesis (certificate wording)

### Agent A — Hamming shells + multi-region

| Result | Evidence level | Claim allowed? |
|---|---|---|
| n100 r=1 `U_small` negative control `INFEASIBLE_SCOPED` | Encoding sanity + aligns Gate1 global r=1 exclusion | **Not** a new UB; expected control |
| n100 r=2 `U_small_r2` 4/4 `INFEASIBLE_SCOPED` (+ halo/fullrem/r3 escalations scoped INFEAS) | `SCOPED_INFEASIBLE` under listed U_ids | **Not** global `C(100)≤164` |
| n64 r=1 `U_small` `INFEASIBLE_SCOPED` (+ full enum 0 legal) | `SCOPED_INFEASIBLE` | **Not** global `C(64)≤112` |
| Multi-region pure/conflict/hybrid: no size improve (112/164) | `HEURISTIC` / budget negative | No impossibility |

**Legal +1:** none.

### Agent B — Orbit / core / defect

| Result | Evidence level | Claim allowed? |
|---|---|---|
| Smoke: many axes `INFEASIBLE` with scoped notes; Type0 defect `TIMEOUT` | Scoped model UNSAT **or** time-bound open | TIMEOUT **≠** INFEASIBLE |
| Long n100 Type0 defect/partial best → `TIMEOUT` size=0 (~3000s / ~2100s) | `TIMEOUT_INCONCLUSIVE` | **Not** global infeasible |
| Long n64 Type0 defect → `TIMEOUT` size=0 (~2400s) | `TIMEOUT_INCONCLUSIVE` | **Not** global infeasible |
| Pure Type1/Type2 (and several defect smokes) → scoped `INFEASIBLE` | `SCOPED_INFEASIBLE` (universe/mode/hash) | **Not** global UB |
| `any_legal_plus1: false`; candidates dir empty | No certified construction | No LB |

**Soft naming note (RT-W2-02):** status token is `INFEASIBLE` rather than `INFEASIBLE_SCOPED`, but every recorded infeasible_record carries an explicit “scoped / not a global upper bound” note. Accepted as **PASS with soft residual** (non-blocking).

### Agent C — Fixed-cardinality min-conflict

| Result | Evidence level | Claim allowed? |
|---|---|---|
| n100 \|S\|=165 best exact V=3 (8 seeds); no V=0 | `HEURISTIC` plateau | Not impossibility of V=0 |
| n64 \|S\|=113 best exact V=2 (4 seeds + reproduce); no V=0 | `HEURISTIC` plateau | Not impossibility of V=0 |
| Incremental ↔ exact agree; card held | Implementation soundness | — |

**Legal +1:** none. Soft V plateaus match Gate1 empirical min direct-insertion ΔV (descriptive only).

### Red Team

| Agent | Completeness | Verdict | Critical flaws |
|---|---|---|---|
| A | COMPLETE | **PASS** | No |
| B | COMPLETE (report + summaries + smoke/long) | **PASS** | No |
| C | COMPLETE | **PASS** | No |

---

## 4. What is *not* claimed

1. **No** new lower bound on `C(64)` or `C(100)`.
2. **No** global upper bound from any scoped CP-SAT UNSAT.
3. **No** identification of TIMEOUT with INFEASIBLE (esp. B Type0 longs).
4. **No** promotion of Agent C V=3/V=2 soft states to legality or optimality.
5. **No** FunSearch / Phase-5 authorization from this gate alone.

---

## 5. Obstruction map → Wave 3 actions (not seed grinding)

| Obstruction | Grade | Implication |
|---|---|---|
| Score/halo Hamming U_ids at r≤3 (A) | Scoped closed | Do **not** re-spend primary budget on same U_ids; only certificate-/residual-driven new Rem/Add |
| Multi-region modes as run (A) | Heuristic flat | Need nonlocal free-sets / residual communities, not more same knn boxes |
| Type0 defect Wave2 universes (B) | TIMEOUT open | Still live: enlarge defect/halo/time or change core policy — **not** “proven empty” |
| Pure Type1/2 orbits (B) | Scoped INFEAS | Pure-orbit compare killed for those models; defect path remains the live compare |
| Fixed-card soft at S0∪{q} V=3/2 (C) | Heuristic basin | Do **not** grind more seeds on same operators; require forced exchange / residual exact repair / different init basins |

---

## 6. Next three recommended actions (Wave 3)

1. **Rank & fund open TIMEOUT / certificate routes first:** enlarge Type0 (and related) orbit-defect models that timed out (B), and/or Hamming Rem/Add rebuilt from residual certificates — **not** re-running Wave2 score-`U_*` shells.
2. **Kill S0+1 soft grinding:** treat C’s V=3/V=2 elites as basin diagnostics; next soft/exact work must force Hamming remove≥2 or nonlocal free variables (LH already flagged elites as S0∪{q}).
3. **Wave-3 Main ranking memo:** pick top 1–2 routes by (open TIMEOUT information, scoped progress, diversity vs killed U_ids); concentrate long budgets there. Hold FunSearch until G2–G3 interfaces stay stable and soft metrics still plateau after those focused runs.

---

## 7. Paths written by this Gate2 Main close

- `scratch/wave2/gate2_decision.md` (this file)
- `scratch/wave2/gate2_manifest.json`
- Updated: `audits/wave2_red_team.md`
- Updated: `scratch/red_team_wave2/summary.json`, `agent_b_checks.json`
- Updated LH ledger files under `long_horizon_run_20260811_183737/` (append-only closure notes)

---

## 8. Ownership / protected paths

Verifier / baseline / `results/certified` / claim_registry: **unchanged by Gate2 synthesis**.  
Info residual: RT-W2-04 (`greedy.py` dirty outside exclusives) remains Main housekeeping, non-blocking for Gate2 close.
