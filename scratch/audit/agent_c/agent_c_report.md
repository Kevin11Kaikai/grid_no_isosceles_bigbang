# Audit Agent C Report — Wave 1 / Gate 1

- **git HEAD:** `148808f422cba7e8ca232ebb4710b84782086342`
- **n64 hash:** `47d42165b7804493a847e064494ef067e97bc8ac12121cd04ac19f23fee9c292` (match=True)
- **n100 hash:** `8a84216d28f5afbbbd6b06301b159eab1b57c85bb814d78dd708da2be65cbdc1` (match=True)
- **Scope:** density / Hamming-scale / universe-halo diagnostics only.
- **Confirmations:** no formal +1 solver; no search for sizes 165 or 113; no writes outside `scratch/audit/agent_c/`; row/col/ring stats are descriptive only.

## C1 — Density findings

### n=64 (size 112, V=0)

- Row occupancy: mean=1.750, empty_rows=33/64 (descriptive).
- Col occupancy: mean=1.750, empty_cols=36/64 (descriptive).
- Ring: max_occupied_ring=11 / max_ring=31; empty-center cells beyond that = 1600 (39.062% of grid).
- Region densities: boundary=0.0429, mid=0.0094, center=0.0000.
- Local crowding (Chebyshev r=5 among selected): mean=3.39, max=7.
- Distance-usage pressure: usage_ratio mean=1.0000 (legal⇒1); unselected cells blocked per pivot: mean=333.3, max=450.
- Direct insertion: zero-ΔV cells=0; ΔV≤1: 0; ΔV≤2: 6; ΔV≤3: 8; ΔV≤5: 26; ΔV≤10: 490.
- Central 180° symmetry: 108/112 = 0.9643; fully_symmetric=False.

### n=100 (size 164, V=0)

- Row occupancy: mean=1.640, empty_rows=62/100 (descriptive).
- Col occupancy: mean=1.640, empty_cols=64/100 (descriptive).
- Ring: max_occupied_ring=26 / max_ring=49; empty-center cells beyond that = 2116 (21.160% of grid).
- Region densities: boundary=0.0276, mid=0.0025, center=0.0000.
- Local crowding (Chebyshev r=5 among selected): mean=5.07, max=8.
- Distance-usage pressure: usage_ratio mean=1.0000 (legal⇒1); unselected cells blocked per pivot: mean=510.4, max=840.
- Direct insertion: zero-ΔV cells=0; ΔV≤1: 0; ΔV≤2: 0; ΔV≤3: 16; ΔV≤5: 112; ΔV≤10: 1672.
- Central 180° symmetry: 164/164 = 1.0000; fully_symmetric=True.

## C2 — Hamming neighborhood scale

For shell |S₀\S|=r, |S\S₀|=r+1. Raw full-grid scales are astronomical; low-ΔV add-pools and finite Rem/Add universes are required before exact search.

### n=64

- **r=1** (remove 1, add 2): log10(raw)≈8.95; raw≈8.886232e+08.
  - After add-pool ΔV≤2: add_pool=6, log10(comb)≈3.23.
  - Scenario rem=12 add=24: vars=36, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈3.52.
  - Scenario rem=16 add=32: vars=48, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈3.90.
  - Scenario rem=24 add=48: vars=72, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈4.43.
  - Scenario rem=32 add=64: vars=96, CP-SAT=comfortable, MILP=moderate, log10(shell)≈4.81.
- **r=2** (remove 2, add 3): log10(raw)≈13.82; raw≈6.546221e+13.
  - After add-pool ΔV≤2: add_pool=6, log10(comb)≈5.09.
  - Scenario rem=12 add=24: vars=36, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈5.13.
  - Scenario rem=16 add=32: vars=48, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈5.77.
  - Scenario rem=24 add=48: vars=72, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈6.68.
  - Scenario rem=32 add=64: vars=96, CP-SAT=comfortable, MILP=moderate, log10(shell)≈7.32.
- **r=3** (remove 3, add 4): log10(raw)≈18.38; raw≈2.388880e+18.
  - After add-pool ΔV≤2: add_pool=6, log10(comb)≈6.53.
  - Scenario rem=12 add=24: vars=36, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈6.37.
  - Scenario rem=16 add=32: vars=48, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈7.30.
  - Scenario rem=24 add=48: vars=72, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈8.60.
  - Scenario rem=32 add=64: vars=96, CP-SAT=comfortable, MILP=moderate, log10(shell)≈9.50.

### n=100

- **r=1** (remove 1, add 2): log10(raw)≈9.90; raw≈7.932439e+09.
  - After add-pool ΔV≤2: add_pool=0, log10(comb)≈-inf.
  - Scenario rem=12 add=24: vars=36, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈3.52.
  - Scenario rem=16 add=32: vars=48, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈3.90.
  - Scenario rem=24 add=48: vars=72, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈4.43.
  - Scenario rem=32 add=64: vars=96, CP-SAT=comfortable, MILP=moderate, log10(shell)≈4.81.
- **r=2** (remove 2, add 3): log10(raw)≈15.33; raw≈2.119207e+15.
  - After add-pool ΔV≤2: add_pool=0, log10(comb)≈-inf.
  - Scenario rem=12 add=24: vars=36, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈5.13.
  - Scenario rem=16 add=32: vars=48, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈5.77.
  - Scenario rem=24 add=48: vars=72, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈6.68.
  - Scenario rem=32 add=64: vars=96, CP-SAT=comfortable, MILP=moderate, log10(shell)≈7.32.
- **r=3** (remove 3, add 4): log10(raw)≈20.45; raw≈2.813151e+20.
  - After add-pool ΔV≤2: add_pool=0, log10(comb)≈-inf.
  - Scenario rem=12 add=24: vars=36, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈6.37.
  - Scenario rem=16 add=32: vars=48, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈7.30.
  - Scenario rem=24 add=48: vars=72, CP-SAT=comfortable, MILP=comfortable, log10(shell)≈8.60.
  - Scenario rem=32 add=64: vars=96, CP-SAT=comfortable, MILP=moderate, log10(shell)≈9.50.

Guidance: start CP-SAT lazy on ≤~50–80 vars (U_small r=1); MILP only for very small Rem; avoid full-grid add pools at r≥2.

## C3 — Proposed universes

### n=64

- **U_small**: rem=12, add=24, vars=36; r∈[1]; CP-SAT=comfortable.
  - Rule: Remove: top removal_score (crowding+boundary+unpaired-symmetry+blocking). Add: lowest delta_V among ΔV≤5 (only 6 cells have ΔV≤2), mostly non-center, 2 center probes.
  - Add regions: {'boundary': 20, 'mid': 2, 'center': 2}
- **U_medium**: rem=24, add=48, vars=72; r∈[1, 2]; CP-SAT=comfortable.
  - Rule: Remove: top-24 removal_score. Add: delta_V<=5, ~15% center / mid mix, 6 forced center cells.
  - Add regions: {'boundary': 33, 'mid': 8, 'center': 7}
- **U_large**: rem=40, add=96, vars=136; r∈[1, 2, 3]; CP-SAT=comfortable.
  - Rule: Remove: top-40 removal_score. Add: delta_V<=10 with substantial center/mid inclusion for RH-6 ablation.
  - Add regions: {'boundary': 62, 'mid': 16, 'center': 18}
- **Recommended first r=1:** U_small (36 vars).

### n=100

- **U_small**: rem=16, add=32, vars=48; r∈[1]; CP-SAT=comfortable.
  - Rule: Remove: top removal_score (crowding+boundary+blocking; symmetry already full). Add: lowest delta_V among ΔV≤5 (empirical min ΔV=3; 16 cells at ≤3), mostly frame/mid, 2 center probes.
  - Add regions: {'mid': 4, 'boundary': 26, 'center': 2}
- **U_medium**: rem=32, add=64, vars=96; r∈[1, 2]; CP-SAT=comfortable.
  - Rule: Remove: top-32 removal_score. Add: delta_V<=5, ~15% center, 8 forced center cells.
  - Add regions: {'mid': 6, 'boundary': 48, 'center': 10}
- **U_large**: rem=48, add=128, vars=176; r∈[1, 2, 3]; CP-SAT=comfortable.
  - Rule: Remove: top-48 removal_score. Add: delta_V<=10 with heavy center/mid for empty-center necessity test.
  - Add regions: {'mid': 8, 'boundary': 88, 'center': 32}
- **Recommended first r=1:** U_small (48 vars).

## Halo combination

Combine spatial Chebyshev halo, score-band expansion, and (future) blocker-graph halo from Agent A: `U := U_score ∪ spatial_halo ∪ blocker_halo`. Escalate U_small→medium→large / grow h only after scoped pilots. **Never** treat scoped UNSAT as global.

## Files written

- `scratch/audit/agent_c/density_hamming_diagnostics_n64.json`
- `scratch/audit/agent_c/density_hamming_diagnostics_n100.json`
- `scratch/audit/agent_c/universe_halo_diagnostics.json`
- `scratch/audit/agent_c/agent_c_report.md`
- `scratch/audit/agent_c/scripts/run_density_hamming_audit.py`

## Parent return summary

- First r=1 universe sizes: n64 U_small → 36 vars (12 rem + 24 add); n100 U_small → 48 vars (16 rem + 32 add).
- Key density: both baselines are boundary-heavy with large empty centers; n100 is fully 180°-symmetric, n64 ≈96.4%; direct +1 insertions have zero-ΔV count n64=0, n100=0.
- Confirmed: no 165/113 search performed.
