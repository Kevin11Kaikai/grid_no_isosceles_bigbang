# Phase-0 Neighborhood Policy (Gate 1 / Main)

**Status:** binding for Wave 2 search pilots.  
**Git commit audited:** `148808f422cba7e8ca232ebb4710b84782086342`  
**Coordinate convention:** `0_to_n_minus_1` (Gate 0; A/B/C used the same certified baselines).  
**Baselines:** n64 size 112 hash `47d42165…e9c292`; n100 size 164 hash `8a84216d…bdc1`.  
**Consistency patch:** see `scratch/audit/gate1_consistency_check.md` (n=100 global deletion LB≥2 ⇒ primary Hamming pilot is **r=2**, not r=1).

**Hard claim rule.** Every solver outcome must be labeled  
`scope = (n, r, U_id, halo, symmetry_mode, time_limit, seed)`.  
Restricted UNSAT/OPT is **not** a global upper bound. No agent may claim a new lower bound without dual certify + hash + repro.

---

## Phase 1 — Hamming-shell (Search Agent A owns)

### 1.1 Universes

| Grid | U_id | Rem | Add | Vars | Allowed r | Role |
|---|---|---:|---:|---:|---|---|
| n=100 | **`U_small_r2`** (first **breakthrough** pilot) | 32 | 44 | 76 | **2** | Primary Wave-2 start |
| n=100 | `U_small` | 16 | 32 | 48 | 1 | **Negative-control / encoding sanity only** (expect INFEASIBLE) |
| n=100 | U_medium | 32 | 64 | 96 | 2,3 | After `U_small_r2` scoped result |
| n=100 | U_large | 48 | 128 | 176 | 2,3 | RH-6 / center ablation |
| n=64 | **U_small** (first pilot) | 12 | 24 | 36 | **1** | Primary for n=64 |
| n=64 | U_medium | 24 | 48 | 72 | 1,2 | |
| n=64 | U_large | 40 | 96 | 136 | 1,2,3 | |

**`U_small` / U_medium / U_large lists (n=64 and n=100 score pools):**  
`scratch/audit/agent_c/universe_halo_diagnostics.json`.  
Do **not** hard-code ring≤11 / ring≤26 as legality constraints.

**`U_small_r2` (n=100) — reproducible definition**

- Rem (32): Agent C `baselines.n100.universes.U_medium.removable_baseline_points` (top-32 `removal_score`).
- Add (44): union of (i) all 16 unselected cells with Agent A `exact_min_hitting_set=2` (listed in `gate1_consistency_check.json`) and (ii) Agent C `U_small.addable_unselected_points`.
- Shell meaning: `|S0\S|=2`, `|S\S0|=3` (target size 165).
- Universe hash SHA-256: `a100c8b65096256676e7959491c95b5868d3a71c7b43bdf0f27609e382d50e88`.
- **Not** a connected-component slice of the giant blocker-projection CC.

**Why not n=100 r=1 as breakthrough?**  
Agent A checked all 9836 unselected cells: sound VC lower bound ≥2 everywhere; 16 cells exact=2. Global r=1 Hamming shell around S0 is structurally empty of +1 improvements (see consistency check). Scoped wording only — not a global `C(100)≤164`.

### 1.2 First pilots (Wave 2)

1. **Primary breakthrough:** n=100 **`U_small_r2`, r=2** (76 vars).  
2. **Parallel secondary:** n=64 `U_small`, **r=1** (36 vars) — valid because global min deletion LB/exact = 1.  
3. **Optional negative-control (n=100):** `U_small`, r=1, 48 vars, few minutes, single seed; expected INFEASIBLE aligned with blocker proof; **not** a breakthrough attempt.

### 1.3 How Agent A communities enter joint models

- Full blocker-projection CC is a **giant** (1 component on both grids). That is a **global coupling fact**, **not** a small neighborhood. Do **not** describe the giant CC as a local community, and do **not** use it as a multi-region destroy partition.
- `U_small` (48 vars) comes from Agent C **score/ΔV top-M**, not from cutting the giant CC.
- Use **spatial 6-NN communities** on baseline points as the Phase-1/4 community layer:
  - n=64: communities `{0,1}` (sizes 56+56), one far conflict bridge `0↔1`.
  - n=100: communities `{0..9}` (sizes 13×4, 17×4, 22×2), 41 spatially-far knn bridges.
- For each pilot add-cell `q` among C’s add pool ∪ A’s easiest-ranked qs, include **all** baseline points in every spatial-knn community touched by `q`’s blocker edges (A fields `spatial_knn_communities_touched`) inside the Rem/free set when building joint shells.
- Prefer joint models over independent per-box repairs whenever a candidate `q` touches ≥2 knn communities (common: 3980 such qs on n64; 9836 on n100).

### 1.4 Halo enlarge order

Escalate only after a scoped pilot on the current U:

1. Grow Rem down C’s `removal_score` list / promote rem pools (U_medium → U_large).  
2. Raise add ΔV cutoff / union remaining Agent A low-deletion-LB cells.  
3. Union spatial Chebyshev halo around current Rem∪Add.  
4. Union blocker-incidence-graph halo (graph distance ≤ h) from A certificates (ego-neighborhoods — **not** the giant CC as a single region).  
5. For n=100: stay on **r=2** until `U_small_r2` / medium scoped results exist; then r=3 if needed.  
6. For n=64: r=1 first on `U_small`; increase r only after scoped pilots on U_small/U_medium.  
7. n=100 r=1 on `U_small` only as negative-control.

Formula (C): `U := U_score ∪ spatial_halo ∪ blocker_halo`.

### 1.5 Destroy ablations (symmetric vs asymmetric)

Run both destroy modes on the same U whenever budget allows:

| Mode | Definition | When required |
|---|---|---|
| **Symmetric destroy** | Remove closed under central 180° `(x,y)↦(n-1-x,n-1-y)` and/or under a chosen notebook axis-offset partner set | Diversity; matches near-symmetric cores (n100 Type0 / 180° is complete) |
| **Asymmetric destroy** | Deliberately unpaired removes | **Mandatory ablation** for odd targets under types that are cardinality-unreachable with pure orbits (B: types 0,3–6); also a diversity ablation for types 1–2 |

n64 note: C’s U_small Rem already leads with the four 180°-unpaired baseline points `[59,26],[59,37],[1,2],[1,61]`; Add leads with their missing partners / low-ΔV cells including `[62,2],[62,61],[4,26],[4,37]`. Preserve this as the default n64 r=1 seed universe.

### 1.6 Scoped claim wording

Allowed: “INFEASIBLE/OPTIMAL/TIMEOUT under `scope=…`.”  
Forbidden: “C(100)≤164”, “no 165 exists”, or any global UB from a restricted shell.

---

## Phase 2 — Orbit / Defect (Search Agent B owns)

### 2.1 Seven axis types (notebook offsets)

| Type | Offset | True G-action on full grid? | Phase-2 rule |
|---:|---|---|---|
| 0 | `(n-1,n-1)` | Yes | **Defects mandatory** for 113/165 |
| 1 | `(n-2,n-2)` | No (OOG boundary) | **Compare** pure-orbit vs orbit+defect |
| 2 | `(n,n)` | No (OOG boundary) | **Compare** pure-orbit vs orbit+defect |
| 3 | `(n,n-1)` | No | **Defects mandatory** |
| 4 | `(n-2,n-1)` | No | **Defects mandatory** |
| 5 | `(n-1,n)` | No | **Defects mandatory** |
| 6 | `(n-1,n-2)` | No | **Defects mandatory** |

Source: `scratch/audit/agent_b/orbit_parity_reachability.json`.  
`mapping_semantics_blocked`: **none**.

### 2.2 Mandatory vs compare

- **Mandatory defects (cardinality_unreachable by FULL-orbit subset-sum / parity):** types **0, 3, 4, 5, 6** on both n=64→113 and n=100→165.  
- **Compare pure vs defect (cardinality_reachable_but_legality_open):** types **1, 2** (each has one FULL size-1 fixed orbit). Cardinality ≠ legality — both models must be searched.

### 2.3 Ranking for Wave-2 pilots

1. Type **0** + defects (aligns with H-001 / central symmetry; n100 fully closed; n64 core 108/112).  
2. Types **1** and **2** pure-orbit cardinality pilots (only odd-reachable FULL types), then same types with defects.  
3. Types **3–6** defect-mandatory pilots (shared even-size FULL multiset).  

Do **not** treat repo `symmetry_guided.py` (central 180° pairs only) as covering types 1–6.

### 2.4 Baseline completeness cues (descriptive, not constructions)

- n100 Type0: 0 partial orbits; FULL core 164/164 — agrees with C central 180° `fully_symmetric=True`.  
- n64 Type0: 2 partial FULL orbits; core 108/112 — agrees with C 108/112 unpaired count (listings differ: B orbit reps vs C unpaired present points; same structural fact).

---

## Phase 3 — Fixed-cardinality min-conflict (Search Agent C owns)

### 3.1 Targets (do **not** generate 165/113 pools in Gate 1)

Later Wave-2 init only:

- n=100: fix `|S|=165`, minimize `V(S)`.  
- n=64: fix `|S|=113`, minimize `V(S)`.

Suggested cold starts (policy only — **not executed now**):

- Start from S₀ and apply 1-for-1 / 2-for-2 moves into the candidate/halo pool below.  
- Alternate seeds that inject C’s lowest-ΔV unselected cells and A’s min-deletion-LB cells.  
- For symmetry-biased seeds: n100 may start from the full Type0/180° core; n64 should allow breaking the four unpaired points.

### 3.2 Candidate / halo pool (A + C)

```
Pool ⊆ S′ ∪ recently_deleted
     ∪ C_low_delta_V (ΔV ≤ 5 on n64; ΔV ≤ 5 on n100, noting empirical min ΔV=3)
     ∪ A_easiest_blocker_qs (top by min-deletion LB / edge count)
     ∪ spatial_halo(Rem∪Add)
     ∪ blocker_halo(A communities, graph distance ≤ h)
```

### 3.3 Repair-pool rule

Exact repair / feasibility-at-target **must** be allowed to pick points **outside** the current parent S′.  
S′-only deletion repair is forbidden as the sole operator.

---

## Phase 4 — Multi-region conflict repair (Search Agent A owns)

### 4.1 Recommended communities (from A)

| Grid | Partition | Communities | Far conflict bridges |
|---|---|---|---|
| n=64 | spatial_knn6 | `{0,1}` (56+56) | `0↔1` (weight 22660) — **always joint** |
| n=100 | spatial_knn6 | `{0..9}` | Prefer heaviest far bridges first: `6↔8`, `7↔8`, `4↔9`, `5↔9` (6245); then `8↔9` (4720); then corner↔side bridges involving `{1,2,3}↔{8,9}` (3911) |

Ring-band partitions (3–4 bands) are secondary ablations only; full projection CC is not usable as a multi-cut.

### 4.2 Comparison matrix (required Wave-2 pilots)

1. **Pure spatial** boxes (existing `lns_multiregion` style).  
2. **Conflict-only** destroys = knn community sets + bridge pairs above.  
3. **Hybrid** = spatial box ∪ communities touched by A’s easiest qs / C’s low-ΔV adds.

Record scoped status, best V at fixed target if used, and whether any legal +1 appears. Prefer conflict/hybrid if pure spatial remains flat.

---

## Evidence-grade labels (all phases)

| Label | Meaning |
|---|---|
| **exact** | Bounds coincide, bitset DP, branch-and-bound, or solver OPT/INFEAS inside a declared finite scope |
| **bound** | Sound LB/UB only (A hitting-set when exact null) |
| **heuristic** | Greedy / score ranks — never promoted to exact |
| **descriptive** | Occupancy, rings, crowding, structural distances — not legality constraints and not constructions |

A/B/C artifacts already follow this split; Wave-2 modules must keep the same vocabulary.
