# Claim Registry

## Claim 1

**Statement:** C(64) >= 112.

**Type:** KNOWN_RESULT (reproduced, not discovered by us).

**Evidence:**
- Candidate file: `results/certified/n64_k112_baseline_official.json`
- Verifier A: `src/verification/oracle_verifier.py`, PASS (`verifier_A_pass: true`)
- Verifier B: `src/verification_independent/independent_verifier.py`, PASS (`verifier_B_pass: true`)
- Literature source: arXiv:2511.02864 Problem 6.59; official AlphaEvolve repo notebook
  (`data/external/subsets_of_the_grid_with_no_isosceles_triangles.ipynb`, `sol_64`)
- Red Team status: see `audits/red_team_round1.md`

**Allowed wording:** "We reproduce and independently dual-verify the published
construction establishing C(64) >= 112."

**Forbidden wording:** "We prove C(64) = 112", "we discovered the 112-point
construction", "world record", "optimal".

## Claim 2

**Statement:** C(100) >= 164.

**Type:** KNOWN_RESULT (reproduced, not discovered by us).

**Evidence:**
- Candidate file: `results/certified/n100_k164_baseline_official.json`
- Verifier A: PASS
- Verifier B: PASS
- Literature source: same as Claim 1, `sol_100`
- Red Team status: see `audits/red_team_round1.md`

**Allowed wording:** "We reproduce and independently dual-verify the published
construction establishing C(100) >= 164."

**Forbidden wording:** "C(100) = 164", "optimal", "world record".

## Claim 3

**Statement:** Our incremental search state (`src/search/incremental_state.py`) is
consistent with the slow oracle verifier under randomized add/remove/swap sequences.

**Type:** COMPUTATIONAL.

**Evidence:**
- `tests/test_incremental_state.py`: 500-move randomized sequence, multi-swap chain,
  and checkpoint-restore roundtrip, all cross-checked against
  `src/verification/oracle_verifier.py` after every move. 3/3 tests pass.
- Independent Red Team attack (Attack 2 in the brief) — see `audits/red_team_round1.md`.

**Allowed wording:** "no divergence was found in N tested random move sequences" (N =
actual count tested, currently 500 in the automated test plus whatever additional
sequences the Red Team ran).

**Forbidden wording:** "the incremental state is proven correct in general" (only a
finite number of sequences were tested; this is empirical evidence, not a proof).

## Claim 4 (search outcome — RESOLVED)

**Statement:** An LNS-with-exact-MILP-repair search starting from the official
n=64/n=100 baselines did NOT find any legal construction exceeding 112/164 points
within the compute budget used in this session.

**Type:** COMPUTATIONAL / NEGATIVE_RESULT.

**Evidence:**
- n=64: 60s pilot, seed=1, 8613 exact regional-repair iterations (each an
  independently-solved 0-1 ILP), best size stayed at 112 throughout.
- n=100: 420s (7 min) run, seed=7, 25153 exact regional-repair iterations, best
  size stayed at 164 throughout. See `logs/lns_exact_n100_seed7.json`.
- MILP encoding itself validated correct against brute force on synthetic instances
  by both the main agent (`tests/test_lns_exact_repair.py`, 3/3 pass) and the Red
  Team subagent independently (3 more synthetic cases, `audits/red_team_round1.md`
  Attack 6) — so this negative result is not attributable to a broken repair step.
- Red Team round 1 verdict: PASS (one LOW-severity documentation-accuracy finding,
  fixed; no correctness defect in the returned/certified output of any search route).

**Allowed wording:** "No improvement over the baseline was found within the search
budget used in this session (33766 total exact-MILP regional repairs combined across
both grids); this does not establish that 113/165 or larger constructions do not
exist — only that this project's specific search routes, seeds, and time budgets did
not find one."

**Forbidden wording:** any claim of a new lower bound (no DUAL_VERIFIED certificate
exceeding 112 (n=64) or 164 (n=100) was produced in this session).

## Claim 5 (Round 2 search outcome, user-requested extended search)

**Statement:** Four additional, qualitatively different search strategies (SA with
periodic exact repair; multi-region simultaneous exact ILP repair; symmetry-guided
from-scratch construction; CP-SAT lazy-constraint global search), each run for 30
minutes on both n=64 and n=100 (plus a full-budget greedy multistart), also did NOT
find any legal construction exceeding 112/164.

**Type:** COMPUTATIONAL / NEGATIVE_RESULT.

**Evidence:**
- SA+exact-repair: 105006 iterations (n=64), 60032 iterations (n=100), no
  improvement. See `failed_ideas.md` F-005 for an important caveat: the SA
  acceptance criterion's worse-move branch was never actually triggered at these
  parameters (`accepted_worse_moves: 0` both runs), so this run does not yet fully
  test the mechanism it was designed to test.
- Multi-region exact repair (k=3 regions/iteration, ~400 combined cells): 87960
  iterations (n=64), 44980 iterations (n=100), no improvement. See F-006.
- Symmetry-guided and greedy-multistart from-scratch constructions: both far below
  baseline (79-121 points vs. 112-164), as expected for from-scratch construction
  in 30 minutes vs. the officially evolved baselines — not informative about
  whether 113/165 is reachable, only that from-scratch reconstruction in this
  budget cannot match the baseline's own construction process. See F-007, F-008.
- CP-SAT lazy-constraint global search: first attempt revealed a real efficiency
  bug (unseeded lazy loop spends its entire budget on one intractable round for
  n=100); fixed via baseline-pivot cut-seeding. See F-009 and Claim 6 below for the
  higher-value CP-SAT results this fix enabled.
- Independently, the Round 2 Proposer subagent computed H-006/H-006b (see
  `hypotheses.md`): both baselines sit at an exactly-flat single-point-removal AND
  single-orbit-pair-removal local optimum (2/112 and 0/164 points; 0/54 and 0/82
  orbit pairs open any genuinely different replacement when removed). Independently
  re-confirmed by the main agent via a separate script. This is not itself a search
  result, but it is strong structural evidence for WHY simple local-move searches
  (Round 1's tabu/greedy-LNS, and Round 2's SA/multi-region at modest region sizes)
  are unlikely to find anything from these exact starting points.

**Allowed wording:** "An extended, multi-strategy search (including simulated
annealing, multi-region exact repair, symmetry-guided construction, and CP-SAT
global search) also did not find a construction exceeding 112/164 within the
compute budget used; both baselines were independently confirmed to sit at an
exactly-flat local optimum under single-point and single-symmetric-orbit removal."

**Forbidden wording:** "no larger construction exists" / "112 and 164 are optimal"
/ any claim this constitutes an upper-bound proof (Claim 5's negative results are
heuristic search failures, not machine-checked bounds — see Claim 6 for the one
route in this project that CAN produce genuine upper bounds).

## Claim 6 (Round 2 bonus: small-n exact values via CP-SAT)

**Statement:** For n in {4, 5, 6, 7}, C(n) is exactly {6, 7, 9, 10} respectively —
machine-proven, not merely a reproduced lower bound.

**Type:** NEW_EXACT_RESULT (small-scale, orthogonal to the main n=64/n=100
question).

**Evidence:**
- `src/search/cpsat_small_n_sweep.py`, `logs/cpsat_small_n_sweep.json`.
- Lower bound: greedy multistart construction (legality checked by the same
  pure-Python oracle used everywhere else in this project).
- Upper bound: CP-SAT proves INFEASIBLE for target = lower_bound + 1 under a
  lazily-built (partial) constraint set. This is a mathematically valid complete
  proof despite using a partial constraint set, because removing constraints can
  only enlarge a feasible region — an infeasible relaxed model is a fortiori
  infeasible for the true, more-constrained problem. See the docstring of
  `src/search/cpsat_lazy.py` (`cpsat_prove_upper_bound`) for the full argument.
- n=8 through n=40 (several values tested) remained INCONCLUSIVE within the same
  per-n time budget — neither proven optimal nor beaten; lower bounds recorded in
  `logs/cpsat_small_n_sweep.json` but not claimed as exact.

**Allowed wording:** "C(4)=6, C(5)=7, C(6)=9, C(7)=10 (machine-proven exact via a
greedy lower-bound construction plus a CP-SAT infeasibility proof of the next
target, both re-verifiable from `logs/cpsat_small_n_sweep.json`)."

**Forbidden wording:** claiming any exact value for n=8 or above from this
sweep (all such results are explicitly INCONCLUSIVE, not exact); claiming this
sweep says anything about n=64 or n=100 (no exact-value technique used here scaled
to those grid sizes within this session's budget — see Claim 7 for the dedicated,
still-inconclusive-at-time-of-writing n=64 full-enumeration attempt).

## Claim 7 (Round 2 bonus, in progress: full-constraint-enumeration attempt for n=64)

**Statement:** A separate, non-lazy attempt (`src/search/cpsat_full_upper_bound.py`)
enumerates the COMPLETE forbidden-triple constraint set for n=64 (all 4096 grid
points as apex, not just the 112 baseline points) and issues one CP-SAT
feasibility solve for target=113. As of this document's last update this run's
outcome (see STATUS.md / ROUND_LOG.md for the current status) determines whether
this claim resolves to a genuine complete upper-bound proof, a new candidate, or
remains inconclusive.

**Type:** COMPUTATIONAL, IN PROGRESS / SEE STATUS.md FOR RESOLUTION.

**Forbidden wording (until resolved):** any statement of the outcome one way or
the other. This entry exists to pre-register the experiment and its exact
interpretation rules before the result is known, per this project's discipline of
not adjusting claimed methodology after seeing results.
