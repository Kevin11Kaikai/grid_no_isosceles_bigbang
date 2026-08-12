# Agent B Wave-2 Report — Orbit / Core / Defect Search

- **git_commit**: `797afdeb5e2cb4da0f4850e138a28735bf809518`
- **workers**: ~25% cores → default `5`
- **total_wall_time_s**: 17884.3
- **targets**: n100→165, n64→113

## Hard constraints observed

- Exclusive writes: `src/search/orbit_defect_search.py`, tests, `scratch/agent_b/`.
- No verifier/baseline/certified/claim_registry edits; no global UB from scoped UNSAT.
- TIMEOUT ≠ INFEASIBLE; every INFEASIBLE carries scope+model_hash.
- Types 0,3–6: defect/partial only. Types 1–2: pure AND defect compared.

## Axis smoke

- n64 smoke wall: 50.5s; rows=9
- n100 smoke wall: 105.0s; rows=9

### n64 smoke statuses

- t0 defect d[1, 8]: **TIMEOUT** size=0 (29.6s) hash=`996104bef53c`
- t1 pure d[0, 0]: **INFEASIBLE** size=0 (0.2s) hash=`534d8fdd5338`
- t1 defect d[1, 5]: **INFEASIBLE** size=0 (0.6s) hash=`e7978c082e9f`
- t2 pure d[0, 0]: **INFEASIBLE** size=0 (0.2s) hash=`e941ad609331`
- t2 defect d[1, 5]: **INFEASIBLE** size=0 (0.7s) hash=`409b1a9c0f2e`
- t3 defect d[1, 8]: **INFEASIBLE** size=0 (6.2s) hash=`e56a0698893e`
- t4 defect d[1, 8]: **INFEASIBLE** size=0 (10.1s) hash=`8efaf3318439`
- t5 defect d[1, 8]: **INFEASIBLE** size=0 (0.9s) hash=`7f6276cc5632`
- t6 defect d[1, 8]: **INFEASIBLE** size=0 (1.2s) hash=`027a2276fb4c`

### n100 smoke statuses

- t0 defect d[1, 8]: **TIMEOUT** size=0 (24.6s)
- t1 pure d[0, 0]: **INFEASIBLE** size=0 (0.6s)
- t1 defect d[1, 5]: **INFEASIBLE** size=0 (2.4s)
- t2 pure d[0, 0]: **INFEASIBLE** size=0 (0.5s)
- t2 defect d[1, 5]: **INFEASIBLE** size=0 (2.2s)
- t3 defect d[1, 8]: **INFEASIBLE** size=0 (23.5s)
- t4 defect d[1, 8]: **INFEASIBLE** size=0 (24.0s)
- t5 defect d[1, 8]: **INFEASIBLE** size=0 (12.8s)
- t6 defect d[1, 8]: **INFEASIBLE** size=0 (13.6s)

## n100 long pilots

- any_legal_plus1: False
- best: `{"candidate": null, "defect_budget": [1, 8], "infeasible_record": null, "mode": "defect", "model_hash": "55de47db07e8ed5c14f583631cf2c1d5fb6fcf5e206e49601dc9ca2638334a1f", "n": 100, "scope": {"defect_budget": [1, 8], "mode": "defect", "model_hash": "55de47db07e8ed5c14f583631cf2c1d5fb6fcf5e206e49601dc9ca2638334a1f", "n": 100, "seed": 21, "symmetry_type": 0, "time_limit_s": 3000.0, "universe_id": "orb_t0_defect_core41_free141_def120_part0_h8"}, "size": 0, "status": "TIMEOUT", "symmetry_type": 0, "`

- long_n100_t0_defect_d1-8_s21: **TIMEOUT** size=0 wall=2999.9s cand=None
- long_n100_t0_partial_d1-8_s22: **TIMEOUT** size=0 wall=2099.9s cand=None
- long_n100_t1_pure_d0-0_s31: **INFEASIBLE** size=0 wall=0.8s cand=None
- long_n100_t1_defect_d1-8_s32: **TIMEOUT** size=0 wall=2100.2s cand=None
- long_n100_t2_pure_d0-0_s33: **INFEASIBLE** size=0 wall=0.9s cand=None
- long_n100_t2_defect_d1-8_s34: **TIMEOUT** size=0 wall=1800.2s cand=None
- long_n100_t3_defect_d1-8_s51: **TIMEOUT** size=0 wall=1500.2s cand=None
- long_n100_t4_defect_d1-8_s52: **TIMEOUT** size=0 wall=1200.2s cand=None
- long_n100_t5_defect_d1-8_s54: **TIMEOUT** size=0 wall=1080.2s cand=None

## n64 long pilots

- any_legal_plus1: False
- best: `{"candidate": null, "defect_budget": [1, 8], "infeasible_record": null, "mode": "defect", "model_hash": "fe48a306f50c6bbd7cc31c92d2124591dfaab6b1455057bed42378375cca82ac", "n": 64, "scope": {"defect_budget": [1, 8], "mode": "defect", "model_hash": "fe48a306f50c6bbd7cc31c92d2124591dfaab6b1455057bed42378375cca82ac", "n": 64, "seed": 41, "symmetry_type": 0, "time_limit_s": 2400.0, "universe_id": "orb_t0_defect_core27_free107_def80_part0_h8"}, "size": 0, "status": "TIMEOUT", "symmetry_type": 0, "tag`

- long_n64_t0_defect_d1-8_s41: **TIMEOUT** size=0 wall=2400.1s cand=None
- long_n64_t1_pure_d0-0_s42: **INFEASIBLE** size=0 wall=0.3s cand=None
- long_n64_t1_defect_d1-8_s43: **TIMEOUT** size=0 wall=1500.1s cand=None
- long_n64_t3_defect_d1-8_s53: **TIMEOUT** size=0 wall=1200.2s cand=None

## Files

- `scratch/agent_b/manifest.jsonl`
- `scratch/agent_b/axis_smoke_summary.json`
- `scratch/agent_b/n100_orbit_defect_summary.json`
- `scratch/agent_b/n64_orbit_defect_summary.json`
- `scratch/agent_b/checkpoints/`
- `scratch/agent_b/candidates/` (only if legal +1 found; dual-verified in scratch, not certified)

## Note on claims

No new lower bound is announced here. Scoped INFEASIBLE/TIMEOUT only.
