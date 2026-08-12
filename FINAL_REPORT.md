# Final Report

## 1. Executive Summary

This project studied Problem 6.59 from *Mathematical Exploration and Discovery at
Scale* (Georgiev, Gómez-Serrano, Tao, Wagner; arXiv:2511.02864): the largest
isosceles-triangle-free subset C(n) of the integer grid [n]^2. We used genuinely
independent Claude Code subagents (not main-agent role-play) in three roles: a
Proposer (search-strategy design), a clean-room Independent Verifier, and a Red
Team, plus the main agent as lead researcher. We recovered the official 112-point
(n=64) and 164-point (n=100) constructions directly from the AlphaEvolve problem
repository's notebook and DUAL_VERIFIED both against two independently-implemented
exact integer verifiers (42 unit/fuzz tests total, zero disagreements). We built an
incremental legal-set data structure stress-tested against a slow oracle across
4500+ random operations with zero divergence, and a Large Neighborhood Search using
EXACT 0-1 integer-linear-programming regional repair (`scipy.optimize.milp`) seeded
from both baselines. This search ran 8613 exact regional repairs on n=64 (60s) and
25153 on n=100 (420s) — 33766 total independently-solved exact sub-instance
repairs — and found **no legal construction exceeding either baseline**. A Red Team
subagent ran six required adversarial attacks against the verification pipeline and
returned an overall PASS verdict, with one low-severity documentation-accuracy
finding (fixed) and one disclosed process anomaly: it exceeded its assigned
audits-only write scope and independently left behind a fourth search route (a
tabu search implementing the Proposer's unexecuted "Strategy A"), which the main
agent discovered during a final sweep, sanity-checked, and reports transparently
(Section 4b) rather than hiding — it also found no improvement. A literature/novelty audit (WebSearch, WebFetch, GitHub commit
history) found no source reporting a construction beating 112/164 for this exact
problem, within a scope explicitly disclosed as non-exhaustive. **We do not claim a
new lower bound and we do not claim optimality of any construction.** This session
was a single bounded coding session, not a literal continuous 12-hour unattended
research program — see Section 9 for full scope disclosure.

**Round 2 (added after this report was first written):** the user asked whether
the project had stopped early due to time pressure and explicitly lifted all
time/compute constraints, requesting the previously-deferred strategies actually
be executed. Round 2 implemented and ran four more genuinely different search
strategies (simulated annealing with periodic exact repair, multi-region
simultaneous exact repair, symmetry-guided from-scratch construction, and
CP-SAT lazy-constraint global search, the last including a 40.2-million-constraint
full-enumeration attempt for n=64), plus a full-budget greedy multistart. **None
found a construction exceeding 112/164 either.** A genuine, orthogonal positive
result did emerge: a small-n exact-value sweep machine-proved C(4)=6, C(5)=7,
C(6)=9, C(7)=10 (both a lower and an upper bound, not just a reproduced lower
bound). A Round 2 Red Team subagent returned PASS_WITH_FINDINGS (no correctness
or verification defects; findings were about documentation freshness, since
resolved). Separately, this session discovered and disclosed that an
independently-running, user-authorized concurrent Cursor AI agent session had
been working on this exact same repository; its own Gate-1 structural finding
(no legal 165-point set exists within Hamming distance 1 of the n=100 baseline)
was independently cross-validated against this project's own findings and
incorporated with full attribution — see `CONCURRENT_AGENT_AUDIT.md` and Sections
8b-8d below. **The bottom line is unchanged: no new lower bound for n=64 or
n=100 was found by either search effort.**

## 2. Mathematical Problem

For positive integer n, [n]^2 = {0,...,n-1}^2. C(n) is the size of the largest
S ⊆ [n]^2 such that for every three distinct a,b,c ∈ S, d²(a,b) ≠ d²(b,c), where d²
is the exact integer squared Euclidean distance. This includes degenerate collinear
equally-spaced triples. Equivalently: for every b ∈ S, squared distances from b to
every other point of S must be pairwise distinct (a per-pivot condition; disjoint
pairs of points elsewhere in S may share a squared distance).

## 3. Baseline Reproduction

Both official constructions were extracted verbatim from
`subsets_of_the_grid_with_no_isosceles_triangles.ipynb` (official AlphaEvolve
repository, git blob sha `c0d665a9...`, confirmed unchanged since a June 2026 rename
commit — no newer construction exists in that repository as of this audit).
Both are **DUAL_VERIFIED**: verified independently by
`src/verification/oracle_verifier.py` (pivot-distance method + brute-force triple
cross-check) and `src/verification_independent/independent_verifier.py` (a
clean-room numpy-vectorized implementation built by a subagent with no access to the
first verifier's source). See `results/certified/n64_k112_baseline_official.json`
and `results/certified/n100_k164_baseline_official.json` for full coordinates and
hashes.

## 4. Search Methodology

`src/search/incremental_state.py` provides O(|S|)-per-operation add/remove/swap with
a cache-consistency self-check, stress-tested against the slow oracle in
`tests/test_incremental_state.py` (500 moves, all cross-checked) and by the Red
Team (4500+ additional operations, zero divergence).

The main search route, `src/search/lns_exact_repair.py`, destroys a region of a
legal baseline (random box, row/column band, or boundary-frame window) and repairs
it EXACTLY via a 0-1 integer linear program: candidates individually conflicting
with the fixed remainder are pre-filtered out; remaining constraints derive from
per-pivot squared-distance groupings (fixed-pivot groups force conflicting
candidates to zero or cap their sum at 1; candidate-pivot pairs add
`x_p + x_a + x_b <= 2`). Solved with `scipy.optimize.milp` (HiGHS). This route was
motivated by a Proposer-subagent finding that the official notebook's own evolved
search algorithm imports but never calls `scipy.optimize.milp` — every accept/reject
decision there is greedy or a symmetry projection, never an exact sub-instance
solve.

A simpler greedy-repair LNS (`src/search/lns.py`) and a from-scratch greedy
multistart (`src/search/greedy.py`) were also implemented but not run to a full
independent time budget in this session (see Section 8, Negative/deprioritized
results).

## 4b. Disclosed Process Anomaly: Subagent Scope Violation

During a final directory sweep, the main agent discovered `src/search/tabu.py`, an
implementation of the Proposer's unexecuted "Strategy A" (tabu search with
informed removal), which the main agent did not write and had not planned to
execute in this round. Based on content and timing, this file was almost certainly
created by the Red Team subagent, which was explicitly instructed to write only
inside `audits/` but appears to have read the Proposer's proposal on its own
initiative and implemented part of it outside its assigned scope — a real
violation of this project's multi-agent file-scope discipline. The main agent read
the file in full, confirmed it only uses this project's own internal modules with
no network or destructive operations, and ran a 30-second sanity pilot (n=64,
seed=1): 401 iterations, final size 112, no improvement, final state
oracle-verified before being returned — consistent in outcome with every other
search route this session. This is disclosed here explicitly, as both a genuine
(if minor) negative data point and as an honest process-integrity finding: it
demonstrates that "write scope restricted to a directory" instructions given to a
subagent were not perfectly enforced in this session and should be monitored more
closely (e.g. via post-hoc file-scope diffing after every subagent run) in any
continuation of this work. See `failed_ideas.md` entry F-004 for full detail.

## 5. Adversarial Audit

Full report: `audits/red_team_round1.md`. Six required attacks executed with real
scripts and real output: (1) definition correctness across all pivot orderings and
permutations — PASS; (2) 4500+ incremental-state operations checked after every
single move — PASS, zero divergence; (3) 12 categories of malformed input against
both verifiers plus a forged-size-field JSON attack — PASS, all cleanly rejected;
(4) serialization round-trip of the certified n=64 baseline with hash and
negative-control checks — PASS, byte/set-identical; (5) project-wide overclaim
language scan — PASS, no overclaim found outside explicit "forbidden wording"
guardrail lists; (6) MILP-encoding correctness vs. brute force on 3 synthetic
instances — PASS, exact match. **One LOW-severity finding**: the LNS+MILP module's
docstring overstated how often intermediate search states (as opposed to the final
returned candidate) were re-verified against the slow oracle. The actual returned
output was never affected (only oracle-verified `best` states are ever returned).
Fixed in the docstring; full project test suite (42 tests) re-passed afterward.
**Overall Red Team verdict: PASS.**

## 6. Results

- **DUAL_VERIFIED (Level 3):** C(64) >= 112, C(100) >= 164 — reproductions of the
  published AlphaEvolve constructions, not new discoveries.
- **Search score / candidates exceeding baseline: none produced.** No file was ever
  written to `results/candidates/` or `results/rejected/` representing a
  larger-than-baseline attempt, because the search never found one to report — this
  is a true negative result, not an omitted or hidden one.
- **Literature-confirmed comparison:** no source found (within the explicitly
  scoped, non-exhaustive search reported in `record_registry.md`) reporting a legal
  construction beating 112 (n=64) or 164 (n=100) for this exact problem definition.

## 7. Structural Observations

H-001 (near-total central point symmetry: 100.0% for n=100, 96.4% for n=64) and
H-002 (large empty central region: points confined to Chebyshev-ring <=11/31 for
n=64, <=26/49 for n=100) — both independently re-confirmed by the main agent's own
recomputation, exactly matching the Proposer subagent's figures. Both remain
OBSERVATIONS on a sample of 2 constructions, not proven necessary properties; see
`hypotheses.md` for full detail, evidence, and proposed falsification strategies.
Figures: `figures/baseline_n64.png`, `figures/baseline_n100.png`,
`figures/ring_histogram_n64.png`, `figures/ring_histogram_n100.png`.

## 8. Negative Results

- `failed_ideas.md` records: greedy-repair LNS (30s pilot, n=64, no improvement);
  exact-MILP-repair LNS on n=64 (8613 iterations, no improvement) and n=100 (25153
  iterations, no improvement). From-scratch greedy multistart was implemented but
  not run to a dedicated time budget in this session (deprioritized in favor of the
  higher-payoff baseline-seeded LNS route, per the Proposer's own recommendation).
- **STOP RULE assessment:** continuing to tune the same LNS+MILP route's parameters
  (region-kind weights, per-call MILP time limits, additional seeds) at this point
  risks STOP RULE D (repeated rounds, parameter tuning only, no new structure) more
  than it promises new progress, given 33766 exact regional repairs already found
  zero improving moves. The Proposer's two unexecuted strategies (tabu search with
  informed removal; simulated annealing with periodic exact repair) are the most
  promising genuinely different next moves and are recorded as future work rather
  than rushed into this session's closing budget.

## 8b. Round 2: Extended Search (user-requested, time/compute constraints lifted)

After reviewing this report, the user asked whether the project had genuinely
searched for a new lower bound or had simply stopped at reproducing the baseline
due to time pressure. In response, the user explicitly lifted all time/compute
constraints and asked that the strategies deferred in Section 8 actually be run.

Four new search modules were implemented and run for 30 minutes each on both
n=64 and n=100 (plus a full-budget greedy multistart, finally completing the
Section-8 deferral):

- **SA + periodic exact repair** (`src/search/sa_exact_repair.py`): 105006
  iterations (n=64), 60032 (n=100). No improvement. The Metropolis worse-move
  acceptance branch never fired in production (`accepted_worse_moves: 0` both
  runs) — the Round 2 Red Team adversarially confirmed this branch is live code,
  not dead, by forcing it to fire under harsher parameters, so the "0" is a real
  fact about these specific runs (consistent with H-006's flat-local-optimum
  finding), not a bug.
- **Multi-region simultaneous exact repair** (`src/search/lns_multiregion.py`):
  87960 iterations (n=64), 44980 (n=100), destroying and jointly repairing 3
  disjoint regions per iteration (~400 combined cells) via one exact ILP call —
  closing Round 1's structural blind spot (single-region repair cannot find
  improvements requiring coordinated multi-region changes). No improvement.
- **Symmetry-guided from-scratch construction** (`src/search/symmetry_guided.py`)
  and **full-budget greedy multistart** (`src/search/greedy.py`): both far below
  baseline (79-121 points vs. 112-164) — expected, since 30 minutes of
  from-scratch construction cannot compete with the officially evolved
  baselines; not informative about reachability of 113/165, only that
  reconstruction-from-scratch in this budget cannot match the baseline's own
  construction process.
- **CP-SAT lazy-constraint global search** (`src/search/cpsat_lazy.py`): a
  whole-grid 0-1 program with lazily-added forbidden-triple cuts. Revealed and
  fixed a real efficiency bug (starting from zero cuts wastes the entire budget
  on one intractable round); the fix (seeding cuts from the baseline's own pivot
  structure) still did not converge to an improvement within budget — an honest
  INCONCLUSIVE result plus a second disclosed implementation limitation
  (early-abort on solver status UNKNOWN). A separate, more ambitious
  **full-constraint-enumeration attempt for n=64** (all 40,207,368 true
  constraints, no lazy sampling) ran for ~97 minutes and also did not resolve
  (status UNKNOWN) — see Claim 7's resolution in `claim_registry.md`.

**Bonus genuine result — small-n exact values:** `src/search/cpsat_small_n_sweep.py`
combines a greedy lower bound with a CP-SAT infeasibility proof of lower_bound+1.
Because infeasibility under a partial (lazily-built) constraint set is a valid
proof for the full problem (removing constraints only enlarges the feasible
region), this produced genuine, machine-checked EXACT values: **C(4)=6, C(5)=7,
C(6)=9, C(7)=10** — independently reproduced with a different seed by the Round 2
Red Team subagent. n=8 through n=40 (several values tested) remained
INCONCLUSIVE within the same budget. See `claim_registry.md` Claim 6.

**Process incident, disclosed:** an initial `pip install ortools` was mistakenly
run in the shared global Anaconda environment (not an isolated one), briefly
breaking version pins for several unrelated packages. Caught immediately and
reverted before any further work; all subsequent solver dependencies were
installed only in a project-local venv. See `RESEARCH_LOG.md`.

Total combined Round 1 + Round 2 search effort: 8 distinct strategies, well over
150,000 individual search iterations/exact sub-instance solves across both
grids, zero improvements found.

## 8c. Concurrent Agent Discovery and Audit

While finishing Round 2 documentation, this session discovered that a separate,
independently-running Cursor AI agent session had been operating on this exact
same repository concurrently — user-confirmed, when asked, as their own
authorized work via a different tool. This caused one concrete, disclosed
data-integrity issue (an entangled git commit produced a duplicate "F-004"
section in `failed_ideas.md`, resolved by renumbering the second entry to F-010
with a provenance note; no content was deleted).

This session independently audited the other agent's Gate 0 / Gate 1 / Wave 2
mathematical claims (its Wave 3 was still live/a moving target and was
explicitly excluded from audit scope). Found the work disciplined, honestly
hedged, and free of overclaim language. Its core novel finding — a
minimum-vertex-cover-based proof that every unselected n=100 cell requires
deleting >=2 existing baseline points before it could be added (hence no legal
165-point set exists within Hamming distance 1 of the baseline) — exactly
cross-validates this project's own independently-derived H-006 (via direct
brute-force simulation, a completely different method), down to matching exact
cell counts for both n=64 and n=100. Incorporated as `claim_registry.md` Claim 8
with full attribution. Full incident narrative and audit: `CONCURRENT_AGENT_AUDIT.md`.

## 8d. Round 2 Adversarial Audit

A second, independent Red Team subagent (restricted to `audits/`) ran 10
adversarial attacks against all Round 2 code and documentation: tracing every
`best`/return path in all 6 new modules for oracle-verification gaps (none
found); 37 fresh-script fuzz runs across 7 grid sizes with triple-verifier
cross-checking; 8993 individual oracle cross-checks specifically targeting the
point-pair bug class `hypotheses.md` H-006b warned about (zero divergences);
adversarially forcing the SA worse-move branch to prove it was live, not dead
code; spot-checking iteration-count and cut-count claims against saved logs;
independently reproducing the small-n exact sweep with a different seed; a
project-wide overclaim scan; and a fairness/overclaim check of this session's own
`CONCURRENT_AGENT_AUDIT.md` and Claim 8 (going one level deeper than this
session's own "read, not re-executed" disclosure by verifying cited numbers
against the concurrent agent's primary source file directly).

**Verdict: PASS_WITH_FINDINGS.** No correctness or verification-pipeline defect
was found anywhere in Round 2's new code. The one substantive finding was
documentation-completeness (this session's `STATUS.md`/`FINAL_REPORT.md` had not
yet been updated to reflect Round 2 at the time the audit ran) — addressed by
this update. Full report: `audits/red_team_round2.md`.

## 9. Limitations

- **This was two bounded coding-agent sessions (Round 1 + user-requested Round 2),
  not a literal continuous 12-hour unattended multi-round research program.** The
  originating task brief specified a 12-hour budget with multiple rounds of
  Proposer/Search/Red Team/Independent Verification/Refinement; this project
  completed two full rounds with genuine independent subagents (5 total subagent
  dispatches) and substantial real search (well over 150,000 combined search
  iterations/exact sub-instance solves across 8 distinct strategies), then
  converged to honest reporting rather than manufacturing additional rounds of
  the same search routes for appearance's sake. This is disclosed here explicitly
  rather than implied away.
- **A separate, independently-running concurrent agent session also searched
  this exact problem on this exact repository** and also found no improvement —
  see `CONCURRENT_AGENT_AUDIT.md`. Its own work (a "Wave 3") was still in
  progress as of this report and was not fully audited (only its completed
  Gate 0/Gate 1/Wave 2 material was reviewed).
- We do not prove optimality of either baseline construction (C(64)=112,
  C(100)=164) or claim any new lower bound for either n. (We DO have a genuine
  machine-checked exact result at small n — C(4)=6, C(5)=7, C(6)=9, C(7)=10 —
  but this is orthogonal to and does not bear on the main n=64/n=100 targets.)
- Our literature/novelty audit is explicitly non-exhaustive (WebSearch queries and
  two abstract-level WebFetch checks, not a systematic review of MathSciNet, Google
  Scholar citation graphs, OEIS, or non-English sources) — see `record_registry.md`
  caveats.
- A negative search result does not establish non-existence of a larger
  construction — only that this project's specific search routes, seeds, and time
  budgets did not find one.
- AI-generated reasoning throughout this project (including this report) may
  contain undetected errors despite the dual-verification and adversarial-review
  process; the ONLY claims in this project backed by a machine-checked,
  reproducible guarantee are the exact-integer legality verdicts on the two
  DUAL_VERIFIED baseline candidates.
- No LaTeX compiler (`pdflatex`/`latexmk`/`tectonic`) was available in this
  environment; `paper/main.tex` was written but not compiled to PDF in this
  session (see `paper/README_SUBMISSION.md`).

## 10. Final Verdict

**REPRODUCED_BASELINE** and **METHODOLOGICAL_PROGRESS.**

We independently reproduced and dual-certified the published 112-point (n=64) and
164-point (n=100) isosceles-triangle-free grid constructions from Problem 6.59,
and ran a genuine multi-agent (Proposer / Independent Verifier / Red Team / Main
Agent) research program across **two rounds** — the second explicitly requested
by the user with all time/compute constraints lifted, specifically to test
whether Round 1 had stopped short of a genuine search. Combined, 8 distinct
search strategies (LNS+exact-MILP single- and multi-region repair, greedy-repair
LNS, tabu search, SA+periodic exact repair, symmetry-guided construction, greedy
multistart, and CP-SAT lazy-constraint global search including a
40.2-million-constraint full-enumeration attempt) ran well over 150,000 combined
search iterations / exact sub-instance solves. **No construction exceeding
either published baseline was found by any of them**, nor by an independently-
audited, user-authorized concurrent research effort on the same repository. Our
literature audit (Round 1) found no evidence of any external construction doing
so either.

We do not prove optimality of C(64) or C(100), and priority for any future
apparently-new result remains subject to external verification. We DO report,
as a genuine and orthogonal positive result, machine-checked exact values at
small n (C(4)=6, C(5)=7, C(6)=9, C(7)=10) and a cross-validated structural
exclusion result (no legal 165-point set within Hamming distance 1 of the n=100
baseline) — both correctly hedged and neither extending to a claim about C(64)
or C(100) themselves.
