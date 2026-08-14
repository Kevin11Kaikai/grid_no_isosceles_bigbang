# Proved / Strongly Established Statements

Only finite verified statements and dual-certified constructions. No overclaim.

## Dual-certified lower bounds

1. \(C(64) \ge 112\) — `DUAL_VERIFIED` official baseline (hash `47d42165…e9c292`).
2. \(C(100) \ge 164\) — `DUAL_VERIFIED` official baseline (hash `8a84216d…bdc1`).

## Gate 0

- \(V(S)=0 \iff\) legal under both verifier logics on fuzz suite (`scratch/audit/gate0_conflict_equivalence.json`).
- Baselines re-verified DUAL_VERIFIED (`scratch/audit/phase0_baseline_reverify.json`).

## Gate 1 structural (sound, scoped wording)

1. **n=100 vs official S0:** for every unselected cell \(q\), sound blocker VC lower bound on deletions ≥ 2 (`GLOBAL_RIGOROUS_LOWER_BOUND` on deletion count). Easiest 16 have exact min deletions = 2.
2. **Consequence:** no legal \(|S|=165\) exists in the **global Hamming r=1 shell** around the official n=100 baseline (`GLOBAL_SHELL_EXCLUSION`). **Not** a proof that \(C(100)\le 164\).
3. **n=64 vs official S0:** global min deletion LB = 1; easiest 2 cells exact = 1. r=1 shells remain mathematically open a priori (Wave2 score-U_small closed as scoped UNSAT only).

## Wave 2 scoped exact results (not global UB)

See `FAILED.md` IMP-F003–F005 and Agent A summaries. All `INFEASIBLE_SCOPED` under declared universes.

## Long-horizon finite facts vs official n=100 S0 (2026-08-14)

4. **Unselected surplus after a min 2-cover of an easiest q is exactly that q.** The F081 "free=3 / cap=165" count includes the two deleted S0 points. True unselected addable set = `{q}` (all 24 covers).
5. **All easiest-16 pairs have joint VC = 4** (E002). No 2-deletion opens two easiest qs at once.
6. Combined with Gate1 histogram (exactly 16 unselected cells have deletion LB=2; rest ≥3): **every 2-deletion from this S0 opens at most one unselected cell.** Frozen-core r=2 cannot produce |S|=165. Not a global C(100) upper bound.
7. Sampled k-deletes (random / top-degree / outer, k=2..16) open 0 unselected cells; first positive n_unsel at k=24 (3–4) still surplus-negative vs k+1.

8. **n=64 vs official S0, exhaustive k=1:** all 112 one-deletions checked. Exactly two open any unselected cell: `(56,2)→{(62,2)}` and `(56,61)→{(62,61)}`. None opens ≥2 unselected cells. Therefore frozen-core r=1 cannot produce |S|=113 around this S0. Not a global C(64) upper bound.
