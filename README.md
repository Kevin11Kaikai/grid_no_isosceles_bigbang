# Grid-No-Isosceles BigBang

Auditable, multi-agent computational research project on **Problem 6.59** from
*Mathematical Exploration and Discovery at Scale* (Georgiev, Gómez-Serrano, Tao,
Wagner; arXiv:2511.02864):

> For positive integer n, let [n]^2 = {0,...,n-1}^2. C(n) is the size of the largest
> S ⊆ [n]^2 such that no three distinct points a,b,c ∈ S have |a-b| = |b-c| (exact
> squared-integer distances; degenerate collinear equidistant triples are forbidden
> too). Equivalently: for every b ∈ S, squared distances from b to every other point
> of S must be pairwise distinct.

## What this project actually did (honest scope statement)

This was run as a single extended coding-agent session, not a literal continuous
12-hour unattended research program. Real work performed:

1. Two **independently-implemented, dual-verified** exact integer verifiers
   (`src/verification/oracle_verifier.py`, `src/verification_independent/independent_verifier.py`),
   built by two separate subagents that did not read each other's code, cross-checked
   by 36 total unit tests plus 500-trial fuzz testing.
2. **Reproduction of the official baselines**: the paper's C(64)≥112 and C(100)≥164
   constructions were pulled from the official AlphaEvolve GitHub repository's
   notebook, converted to a canonical JSON schema, and DUAL_VERIFIED (see
   `results/certified/`).
3. A real **search engine** with an incremental legal-set data structure
   (`src/search/incremental_state.py`) that is stress-tested against the slow oracle
   (2000+ random add/remove/swap operations with zero divergence), plus a genuine
   **Large Neighborhood Search with exact 0-1 ILP repair** (`src/search/lns_exact_repair.py`,
   using `scipy.optimize.milp`) run against both baselines.
4. A real **Proposer subagent** and a real **Red Team subagent**, run as independent
   Claude Code subagents (not the main agent role-playing), see `scratch/proposer/`
   and `audits/`.
5. A **literature/novelty audit** (`record_registry.md`) via WebSearch/WebFetch/GitHub
   API, explicitly scoped and caveated.

See `FINAL_REPORT.md` for the actual numeric outcome and `STATUS.md` for current state.

## Layout

See `REPRODUCIBILITY.md` for exact commands. Directory structure follows the
project brief: `src/` (verification, search, structures), `tests/`, `data/baselines/`,
`results/{candidates,certified,rejected}/`, `audits/`, `scratch/proposer/`, `paper/`.
