# Hypotheses

Structural observations from the Proposer subagent (`scratch/proposer/proposal_round1.md`),
formatted per the project's hypothesis-tracking convention. These are OBSERVATIONS on a
sample of exactly 2 constructions (n=64, n=100) — not proven patterns.

## H-001

**Statement:** The official n=100 baseline construction (SOL_100) is invariant under
the central point-symmetry map (x,y) -> (99-x, 99-y); the n=64 baseline (SOL_64) is
96.4% invariant (108/112 points) under the analogous (x,y) -> (63-x, 63-y) map.

**Motivation:** Understanding whether near-optimal constructions are forced to be
(close to) centrally symmetric would help focus search on a symmetric-generator
representation, cutting the effective search space roughly in half.

**Evidence:** Direct computation over `data/baselines/official_raw.py` by the
Proposer subagent, INDEPENDENTLY RE-CONFIRMED by the main agent with a fresh
one-off script: n=64 108/112 = 0.9643, n=100 164/164 = 1.0000 centrally symmetric
under the stated maps. Exact match to the Proposer's figures.

**Tested n:** 64, 100 (both are the only two available official baselines; sample
size 2).

**Tested seeds:** N/A (deterministic property of fixed baseline data, not
search-seed-dependent).

**Counterexample strategy:** Search explicitly for high-quality asymmetric
constructions (e.g. via the greedy/LNS routes seeded from random, non-symmetric
starting points) and compare their achievable size against the symmetric baselines.

**Red Team result:** Not yet independently re-verified by Red Team as of this
writing — flagged for Red Team round 1 (see `audits/red_team_round1.md`).

**Status:** OBSERVATION (confirmed reproducible computation; still an observation
about a sample of 2, not a proven necessary property of near-optimal constructions).

## H-002

**Statement:** Both baseline constructions leave a large, entirely empty central
square region: SOL_64 has zero points at Chebyshev-distance-to-edge ("ring") > 11 out
of a max possible ring of 31 (~39% of grid area empty); SOL_100 has zero points at
ring > 26 out of max 49 (~21% of grid area empty). Points concentrate heavily near
the boundary.

**Motivation:** If the empty center is a genuine structural necessity (not just an
artifact of the search algorithms used to produce the baselines), search routes could
safely restrict their candidate pool to the boundary region, dramatically shrinking
the effective search space. If it is NOT necessary, deliberately probing the center
could reveal missed points.

**Evidence:** Direct computation by the Proposer subagent over the two baselines.

**Tested n:** 64, 100.

**Tested seeds:** N/A.

**Counterexample strategy:** Run LNS with region selection deliberately biased toward
the central empty region ("center-probe" variant proposed in
`scratch/proposer/proposal_round1.md` section 3, Strategy C) and see whether any
interior points can be legally added without shrinking the achievable frame density
elsewhere.

**Red Team result:** Not yet independently re-verified.

**Status:** OBSERVATION. This project's actual LNS runs used a region-kind mix
including generic random boxes (which can and do land in the center), so some
center-probing did occur implicitly; see STATUS.md / FINAL_REPORT.md for whether any
center points were found addable during this session's search budget.

## H-003

**Statement:** The official notebook's own evolved search algorithm imports
`scipy.optimize.milp`, `LinearConstraint`, `Bounds` but never calls them in the shown
n=64 evolved program (cell 4 of the notebook) — every accept/reject decision in that
algorithm is a single greedy incremental check or a symmetry-group projection, never
an exact sub-instance solve.

**Motivation:** This is a plausible "gap" the official search left on the table:
exact repair of a small destroyed region (LNS) could find regional optima the
official greedy-refill heuristic missed by insertion-order luck.

**Evidence:** Direct reading of `data/external/subsets_of_the_grid_with_no_isosceles_triangles.ipynb`
cell 4 by the Proposer subagent; independently spot-checked by the main agent while
reading the same notebook to extract baseline coordinates.

**Tested n:** N/A (code-reading observation, not a numerical experiment).

**Counterexample strategy:** N/A — this is a factual claim about a specific file's
contents, not a falsifiable mathematical conjecture. It motivated
`src/search/lns_exact_repair.py`, this project's main new search route.

**Red Team result:** See `audits/red_team_round1.md` Attack 6 (MILP encoding
correctness check).

**Status:** OBSERVATION (confirmed factual — verified by direct code reading, not
merely inferred).
