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

## H-005 (Round 2)

**Statement:** No currently-empty cell in either baseline grid is directly addable
with zero conflicts (0/3984 for n=64, 0/9836 for n=100), and the average conflict
count against the full baseline rises roughly monotonically from the boundary
(~14 conflicts near ring 0) to the interior (~27 for n=64, ~42 for n=100 at the
deepest ring).

**Motivation:** Sharpens H-002: is the empty center merely unpopulated, or
measurably harder-blocked? A monotonic conflict gradient is evidence (not proof)
that the emptiness is a real structural difficulty, not a search artifact.

**Evidence:** Computed by the Round 2 Proposer subagent directly from the two
DUAL_VERIFIED certified JSON files, using `IncrementalIsoscelesFreeSet` for the
correctness-sensitive conflict counts. Not yet independently re-run by the main
agent (lower priority than H-006/H-006b, which were re-verified — see below).

**Tested n:** 64, 100.

**Status:** OBSERVATION, single-subagent computation, not yet independently
re-confirmed by the main agent or Red Team.

## H-006 (Round 2)

**Statement:** Both baselines sit at an exactly-flat single-point-removal local
optimum: for n=64, only 2 of 112 points (`(56,61)` and `(56,2)`) free even one
replacement empty cell when removed individually (each frees exactly 1 cell — not
enough for a net gain); the other 110/112 free zero. For n=100, **0 of 164** points
free any empty cell when removed individually.

**Motivation:** Explains, more precisely than "33766 MILP repairs found nothing,"
*why* Round 1's swap-based local routes (tabu, greedy-repair LNS) were very
unlikely to succeed from these exact starting points: there is essentially no
single-point-removal gradient to follow at all.

**Evidence:** Computed by the Round 2 Proposer subagent.
**INDEPENDENTLY RE-CONFIRMED by the main agent** with a fresh one-off script
against both certified JSON files: exact match, 2/112 (n=64), 0/164 (n=100).

**Tested n:** 64, 100.

**Status:** OBSERVATION, independently reproduced by two separate scripts
(Proposer's and the main agent's), still a sample of 2 constructions.

## H-006b (Round 2, orbit-space extension of H-006)

**Statement:** The same flatness holds under symmetric orbit-pair removal (removing
a point and its central-symmetric partner together). Of the 54 (n=64) / 82 (n=100)
currently-occupied symmetric orbit pairs, removing each pair and checking whether
*any* orbit (not just the one just removed) becomes addable: every single removal
opens exactly the trivially-self-reconstructable orbit and no alternative — 54/54
and 82/82 removals open only the pair just vacated, zero open a genuinely
different replacement orbit.

**Motivation:** Directly informs Strategy 3 (symmetry-guided search): rules out
single-orbit removal as a productive starting granularity, motivating 2-3
simultaneous orbit removals as the actual starting point for that search instead.

**Evidence:** Computed by the Round 2 Proposer subagent, which also caught and
disclosed its own script bug during this computation (a list-unpacking error that
produced a nonsensical uniform "opens 2" result before being caught and fixed by
re-deriving via `IncrementalIsoscelesFreeSet`).
**INDEPENDENTLY RE-CONFIRMED by the main agent**, which hit the *same class* of
script bug on its first attempt (failing to filter to orbit pairs where BOTH
points are actually occupied, silently including 2 spurious "orbits" for n=64
where only one of the pair was really present) — caught by a `remove_point`
correctness assertion, fixed, and re-run to the same result the Proposer reported:
54/54 (n=64) and 82/82 (n=100), zero alternative replacement orbits.

**Tested n:** 64, 100.

**Status:** OBSERVATION, independently reproduced via two separately-authored
scripts, EACH of which independently hit and self-caught a closely related
bug-class (mishandling which points in a "pair" are actually present/being
compared) before reporting a final number — noted here as a genuine
process-integrity data point: this exact bug pattern is apparently an easy trap
in this codebase's point-pair logic and future work in this area should watch
for it specifically.

## H-007 (Round 2)

**Statement:** Row/column occupancy counts cluster into a small number of
discrete values rather than a smooth distribution. n=64 row-occupancy histogram:
`{2 points: 10 rows, 3: 2, 4: 8, 6: 4, 7: 2, 8: 2}` (28 rows used). n=100:
`{2: 12, 4: 12, 6: 6, 8: 2, 10: 4}` (36 rows used).

**Motivation:** A quantized (not smooth) row/column occupancy signature is
consistent with the official notebook's generator-and-orbit construction method,
and could serve as a cheap invariant to check whether any future candidate was
built by a similar mechanism.

**Evidence:** Computed by the Round 2 Proposer subagent. Not yet independently
re-run by the main agent.

**Tested n:** 64, 100.

**Status:** OBSERVATION, single-subagent computation, not yet independently
re-confirmed.

## H-008 (Round 2)

**Statement:** The 4 points breaking SOL_64's central symmetry — `(1,2)`,
`(1,61)`, `(59,26)`, `(59,37)` — sit at ring depths `[4, 1, 4, 1]` (not the outer
edge), and none of their central-symmetric reflections `(62,61)`, `(62,2)`,
`(4,37)`, `(4,26)` are occupied by any other point in SOL_64. This is consistent
with these 4 points being standalone additions layered on a perfectly symmetric
108-point core, rather than points that displaced another point's rightful
symmetric slot.

**Motivation:** Confirms, point-by-point, the "symmetric core + asymmetric patch"
interpretation of SOL_64 that `proposal_round1.md` guessed from the aggregate
96.4% statistic but did not directly verify.

**Evidence:** Computed by the Round 2 Proposer subagent directly from
`results/certified/n64_k112_baseline_official.json`. Not yet independently
re-run by the main agent.

**Tested n:** 64 only (n=100 is 100% symmetric, so this observation does not
apply there).

**Status:** OBSERVATION, single-subagent computation, not yet independently
re-confirmed.
