# Agent C Wave 2 Report — Fixed-Cardinality Min-Conflict

**Role:** Search Agent C (Phase 3)  
**Module:** `src/search/fixed_cardinality_minconflict.py`  
**Scope:** Fix `|S|=target`, minimize exact `V(S)` from `conflict_metric.conflict_count`.  
**Not claimed:** no new lower bound; no certification; no record announcement.

## Setup

| Item | Value |
|---|---|
| Targets | n=100 → \|S\|=165; n=64 → \|S\|=113 |
| Workers | 5 subprocesses (~25% of 20 logical cores) |
| Moves | 1-for-1, 2-for-2, large-k swap, ejection neighborhood, PT swaps, reheating |
| Exact repair pool | S′ ∪ Gate1 halo ∪ recently deleted ∪ low-ΔV ∪ A easiest blockers (never S′-only) |
| Inits | baseline+low-blocker, Gate1 low-ΔV, orbit-informed, random fixed-card |
| Incremental V | O(\|S\|) updates; periodic exact recompute; mismatch → STOP + counterexample |
| Campaign wall | **5707 s (~1.59 h)** including optional reproduce |

## Results

### n=100, \|S\|=165 (8 seeds × 25 min)

| Seed | Init | Initial V | Best V | Time-to-best (s) | Iters |
|---:|---|---:|---:|---:|---:|
| 101 | baseline_plus_low_blocker | 4 | **3** | 1.88 | 299964 |
| 102 | gate1_low_delta_v | 8 | **3** | 2.25 | 298200 |
| 103 | orbit_informed | 3 | **3** | 0.00 | 295200 |
| 104 | random_fixed_card | 25 | **3** | 6.60 | 298842 |
| 105 | baseline_plus_low_blocker | 4 | **3** | 6.63 | 298209 |
| 106 | gate1_low_delta_v | 9 | 5 | 4.67 | 352800 |
| 107 | orbit_informed | 9 | 6 | 10.00 | 339622 |
| 108 | random_fixed_card | 35 | **3** | 14.67 | 351600 |

- **Best exact V = 3** (seeds 101–105, 108).  
- **No V=0** legal candidate.  
- Incremental ↔ exact agreement: **true** on all finished seeds; **0** counterexamples.  
- Cardinality held at 165 throughout (validated on saved points).

### n=64, \|S\|=113 (4 seeds × 15 min)

| Seed | Init | Initial V | Best V | Time-to-best (s) | Iters |
|---:|---|---:|---:|---:|---:|
| 201 | baseline_plus_low_blocker | 4 | **2** | 6.08 | 381007 |
| 202 | gate1_low_delta_v | 7 | **2** | 2.01 | 371400 |
| 203 | orbit_informed | 2 | **2** | 0.00 | 414432 |
| 204 | random_fixed_card | 30 | **2** | 1.29 | 385200 |

- **Best exact V = 2**.  
- **No V=0**.  
- Incremental ↔ exact: **true**; cardinality fixed at 113.

### Optional reproduce

- n=64 seed 1201, init `baseline_plus_low_blocker`, 30 min: **V=2** (flat; 676286 iters).  
- Did not break the V=2 plateau.

## Observations (descriptive, not lower-bound claims)

- Gate-1 empirical min direct-insertion ΔV was **3 on n100** and **2 on n64**. Soft search plateaued at those same values for the best seeds.  
- This is consistent with “baseline + one easiest cell” soft states being easy to reach and hard to rearrange below that V under the operators tried.  
- Seeds 106–107 on n100 stalled higher (V=5/6), showing init/basin sensitivity.

## Artifacts

| Path | Role |
|---|---|
| `scratch/agent_c/manifest.jsonl` | Per-run ledger |
| `scratch/agent_c/n100_fixed165_summary.json` | n100 campaign summary |
| `scratch/agent_c/n64_fixed113_summary.json` | n64 campaign summary |
| `scratch/agent_c/elite_archive/**` | Improving elites |
| `scratch/agent_c/checkpoints/candidates/**` | Periodic / final seed checkpoints |
| `scratch/agent_c/seed_results/**` | Per-seed JSON results |
| `scratch/agent_c/reproduce_best.json` | Optional reproduce |
| `scratch/agent_c/campaign_meta.json` | Wall / paths |
| `tests/test_fixed_cardinality_minconflict.py` | Unit tests (5 passed) |

## Parent return summary

- **n100:** initial V typically 3–35 depending on init; **best V=3**; time-to-best ≈ **2–15 s** on successful seeds; no V=0.  
- **n64:** initial V typically 2–30; **best V=2**; time-to-best ≈ **0–6 s**; no V=0.  
- **Incremental/exact agreement:** yes (all campaign seeds).  
- **Wall time:** ~1.59 h (within 4–6 h budget).  
- **Files:** listed above under `scratch/agent_c/` + module/tests.
