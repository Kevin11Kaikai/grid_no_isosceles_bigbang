# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-11 ~19:23 local  
**Synced:** `origin/master` through `f317bf6` (+ pending frame/n64 artifacts)  
**Phase:** LH-2 wide shells — low-LB killed through r=4; frame R2/r4 INFEAS; large frames TIMEOUT

## Incumbent

- n=64: **112** / n=100: **164** DUAL_VERIFIED — unchanged
- No candidate promotion

## Strongest new negatives

1. Any two exact-2 cells need joint_VC=4 (r=2 co-insert dead).
2. `U_fullrem_LBle4` r=2/r=3 and `U_fullrem_LBle5` r=4 → `INFEASIBLE_SCOPED`.
3. `U_fullrem_frameR2_r4` (1084 frame adds) → `INFEASIBLE_SCOPED`.
4. V=3/V=2 elite local refill → scoped INFEAS.
5. n64 cert Rem r=1 (`U_n64_exact1covers_LBle3_r1`) → `INFEASIBLE_SCOPED`.
6. Orbit n100 type2 pure/defect (new seeds) → scoped INFEAS.

## Open / live

| Item | Status |
|---|---|
| Frame R2/R4/R6 at r=2 (90s) | TIMEOUT_INCONCLUSIVE — **longer 600s runs next** |
| Frame R4/R6 at r=4 (90s) | TIMEOUT_INCONCLUSIVE |
| Conflict-eject fixed-card | best V=4 (worse than Wave2 V=3) — operator weak |
| Orbit n64 t0 defect | TIMEOUT history; not INFEAS |

## Next 3 actions

1. Finish `frame_long_timeout.py` (600s on R2/r2 and R6/r2).
2. If still TIMEOUT: try mid-band Add (not only frame) or leave S0-neighborhood (orbit enlarge / from-scratch).
3. Push checkpoint; reallocate away from low-LB Hamming.

## Standing order

Push after meaningful checkpoints; continue; no Hard Stop.
