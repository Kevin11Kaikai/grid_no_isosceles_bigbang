# Gate 1 Decision

## 1. Final verdict

**Gate 1: PASS** (after consistency patch)

**Wave-2 readiness: `WAVE2_READY`**

Wave 2 `/multitask` search pilots are **allowed**, using the revised universes in `scratch/audit/phase0_neighborhood_policy.md` and `scratch/audit/gate1_consistency_check.md`.  
This decision does **not** start Wave 2.

### Consistency patch summary

Human review found a contradiction: Agent A’s n=100 min deletion bound **2** vs Main’s former n=100 **r=1** primary pilot.  
Classification: **`GLOBAL_RIGOROUS_LOWER_BOUND`** over all 9836 unselected cells (sound VC LB; easiest 16 also **exact=2**).  
Therefore n=100 primary Hamming breakthrough is **r=2** (`U_small_r2`); n=100 r=1 retained only as **negative-control**.

## 2. Checklist (plan §10 G1)

| Criterion | Result |
|---|---|
| Gate 0 PASS already recorded | **PASS** |
| Audit Agent A/B/C complete | **PASS** |
| Required JSON artifacts present and parseable | **PASS** |
| Baseline hashes match Gate 0 / A / B / C | **PASS** |
| Same git commit | **PASS** (`148808f422cba7e8ca232ebb4710b84782086342`) |
| Consistency check of n=100 deletion-bound vs r=1 | **PASS** (`gate1_consistency_check.*`) |
| Neighborhood policy aligned with blocker proof | **PASS** (revised) |
| No breakthrough search / no 165–113 solvers in Gate 1 | **PASS** |
| Unresolved math contradictions that block Wave 2 | **None** (former r=1 contradiction resolved) |

## 3. Cross-check notes (unchanged substance)

- Hashes/commit/coords: agree Gate 0 / A / B / C.
- A vs C easiest lists: n64 strong agree; n100 partial agree (metric difference) — non-blocking.
- B Type0 vs C 180°: 108/112 and 164/164 — agree.
- Orbit defects: mandatory types 0,3–6; compare 1,2; none mapping-blocked.
- Giant blocker-projection CC: **global coupling fact**, not a small community; `U_small` is Agent C score/ΔV top-M.

## 4. Recommended Hamming pilots (post-patch)

| Priority | Grid | r | Universe | Vars | Role |
|---|---|---:|---|---:|---|
| 1 | n=100 | **2** | `U_small_r2` | 76 | **Primary breakthrough** |
| 2 | n=64 | **1** | `U_small` | 36 | Primary for n=64 |
| 3 | n=100 | 1 | `U_small` | 48 | Negative-control only |

## 5. Wave 2 authorization

| Question | Answer |
|---|---|
| Status | **`WAVE2_READY`** |
| May Wave 2 search `/multitask` start? | **Yes** (after human launch) |
| Did this write enter Wave 2? | **No** |
| Protected paths still frozen? | **Yes** |

## 6. Paths written / revised (Main only)

**New**

- `scratch/audit/gate1_consistency_check.json`
- `scratch/audit/gate1_consistency_check.md`

**Revised**

- `scratch/audit/phase0_neighborhood_policy.md`
- `scratch/audit/gate1_manifest.json`
- `scratch/audit/gate1_decision.md` (this file)

Agent A/B/C original artifacts were **not** modified.
