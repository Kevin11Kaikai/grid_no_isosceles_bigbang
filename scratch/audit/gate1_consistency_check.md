# Gate 1 Consistency Check

## Verdict on the “deletion lower bound 2” (n=100)

**Classification: `GLOBAL_RIGOROUS_LOWER_BOUND`**, with **`EXACT_MINIMUM = 2`** on the 16 easiest cells.

| Question | Answer |
|---|---|
| Coverage | **All** 9836 unselected cells (`100² − 164`) |
| Method | Sound VC lower bound `max(type1_forced_lb, matching_lb)` on Type1∪Type2 blocker edges (`blocker_audit.py`) |
| Min LB over all q | **2** (histogram has no 0 or 1) |
| Easiest 16 | LB=UB=exact=2 (`exact_bounds_coincide`) |
| Intractable (466) | Still LB≥2 (bounds-only; never heuristic-as-exact) |
| Heuristic? | **No** |

Hashes match Gate 0 (`8a84216d…bdc1`). Agent A raw artifacts **not** modified.

## Does this exclude Hamming r=1?

Yes, for the **global** r=1 shell around the official baseline:

- Model: `|R|=1`, `|A|=2`, target size 165.
- Every new `q∈A` must be compatible with `S0 \ R`.
- Every `q∉S0` needs ≥2 deletions from `S0` to clear blockers.
- One deletion cannot clear any `q`; a second add cannot erase baseline certificates.
- Therefore **no** improving set lies in the global r=1 Hamming shell.
- Scoped claim only: exclusion of that shell model — **not** “C(100)≤164”.

Same argument makes n=100 `U_small` r=1 a **negative-control** (expected INFEASIBLE), not a primary breakthrough pilot.

## Case applied

**Case A** (global rigorous LB / exact min = 2).

## Revised pilots

| Grid | Role | r | Universe | Vars |
|---|---|---:|---|---:|
| n=100 | **Primary breakthrough** | **2** | `U_small_r2` | 76 |
| n=100 | Negative-control / encoding sanity | 1 | `U_small` (48) | 48 |
| n=64 | **Primary** | **1** | `U_small` | 36 |

### `U_small_r2` (n=100)

- Rem (32): Agent C `U_medium.removable_baseline_points`
- Add (44): union of Agent A’s 16 exact-min-deletion-2 cells and Agent C `U_small` addables
- Hash: `a100c8b65096256676e7959491c95b5868d3a71c7b43bdf0f27609e382d50e88`
- Shell: `|S0\S|=2`, `|S\S0|=3`
- UNSAT wording: scoped to `(n=100,r=2,U_small_r2,…)` only

## 48-variable `U_small` definition

- **Not** a cut of the giant blocker-projection CC (that CC is size 164 / one component).
- From Agent C score/ΔV top-M: 16 rem + 32 add = 48 vars.
- Explicit lists in `universe_halo_diagnostics.json`; hash `0e371058…4caac2`.
- Includes A’s easiest quartet `[24,18]` and mirrors.

## n=64

Min deletion LB/exact = **1** on `[62,2]` and `[62,61]` over all 3984 unselected cells → r=1 remains a valid primary pilot.

## Final status

**`WAVE2_READY`** after Main policy/decision/manifest revisions below.

No formal Hamming-shell solver was run in this check.
