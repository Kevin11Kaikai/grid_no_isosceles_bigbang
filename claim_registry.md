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
