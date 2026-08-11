# Audit Agent A — Insertion Blockers & Conflict Communities

**Scope:** Wave 1 / Gate 1 structural audit only.
**No search** for constructions of size 113 (n=64) or 165 (n=100).
**No modifications** to verifiers, baselines, `conflict_metric.py`, or `results/certified`.

- Git commit: `148808f422cba7e8ca232ebb4710b84782086342`
- Schema: `agent_a_blockers_v1`
- Deterministic seed: `0`
- Exact hitting-set only when bounds coincide, bitset DP (≤18 verts), or branch-and-bound (≤40). Heuristics alone are never labeled exact.

## Blocker definition

- **Type1** (q as pivot): each pair `p1,p2 ∈ S0` with `|p1−q|²=|p2−q|²` → edge `{p1,p2}`.
- **Type2** (existing pivot `b`): each `b,p ∈ S0` with `|q−b|²=|p−b|²` → edge `{b,p}`.
- Min deletions = min vertex cover of the union of these blocker edges.

## Hashes used

- n=64: `47d42165b7804493a847e064494ef067e97bc8ac12121cd04ac19f23fee9c292` (matches `phase0_baseline_reverify.json`).
- n=100: `8a84216d28f5afbbbd6b06301b159eab1b57c85bb814d78dd708da2be65cbdc1` (matches `phase0_baseline_reverify.json`).

## Files written

- `blocker_stats_n64.json`
- `blocker_communities_n64.json`
- `blocker_detail_n64.json.gz` (top-200 full edges + compact all-q)
- `blocker_stats_n100.json`
- `blocker_communities_n100.json`
- `blocker_detail_n100.json.gz` (top-200 full edges + compact all-q)
- `agent_a_report.md` (this file)
- `scripts/blocker_audit.py`

## Top findings

### n=64

- Runtime ≈ 2.6s; exact fraction ≈ 0.984.
- Full blocker-projection CC: **1** (giant coupling of all S0 if 1). Spatial 6-NN communities: **2**; multi-spatial-community qs: **3980**; spatially-far conflict bridges (knn): **1**.
- Min deletion LB over unselected q: **1** (2 cells).
- Easiest-100 zone mix: `{'boundary_frame': 48, 'mid_band': 46, 'center_box': 6}`.
- Easiest-ranked q (structural only — **not** claimed insertable):

  1. q=[62, 2] zone=boundary_frame edges=2 LB=1 UB=1 exact=1 spatial_knn_comms=1
  2. q=[62, 61] zone=boundary_frame edges=2 LB=1 UB=1 exact=1 spatial_knn_comms=1
  3. q=[1, 25] zone=boundary_frame edges=2 LB=2 UB=2 exact=2 spatial_knn_comms=2
  4. q=[1, 38] zone=boundary_frame edges=2 LB=2 UB=2 exact=2 spatial_knn_comms=2
  5. q=[4, 26] zone=mid_band edges=2 LB=2 UB=2 exact=2 spatial_knn_comms=1

### n=100

- Runtime ≈ 6.8s; exact fraction ≈ 0.953.
- Full blocker-projection CC: **1** (giant coupling of all S0 if 1). Spatial 6-NN communities: **10**; multi-spatial-community qs: **9836**; spatially-far conflict bridges (knn): **41**.
- Min deletion LB over unselected q: **2** (16 cells).
- Easiest-100 zone mix: `{'mid_band': 62, 'boundary_frame': 38}`.
- Easiest-ranked q (structural only — **not** claimed insertable):

  1. q=[24, 18] zone=mid_band edges=3 LB=2 UB=2 exact=2 spatial_knn_comms=4
  2. q=[24, 81] zone=mid_band edges=3 LB=2 UB=2 exact=2 spatial_knn_comms=4
  3. q=[75, 18] zone=mid_band edges=3 LB=2 UB=2 exact=2 spatial_knn_comms=4
  4. q=[75, 81] zone=mid_band edges=3 LB=2 UB=2 exact=2 spatial_knn_comms=4
  5. q=[3, 17] zone=boundary_frame edges=4 LB=2 UB=2 exact=2 spatial_knn_comms=3

## Interpretation constraints

- Low blocker counts / low deletion LBs mark structurally least-obstructed cells for later shell universes.
- Far-coupled communities support non-local conflict (RH-3); prefer multi-region variables over pure spatial boxes.
- This report does **not** assert existence of any legal |S|=|S0|+1 set.

## Run commands

```bash
python scratch/audit/agent_a/scripts/blocker_audit.py --n all
```

