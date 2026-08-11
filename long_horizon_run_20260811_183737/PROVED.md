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
