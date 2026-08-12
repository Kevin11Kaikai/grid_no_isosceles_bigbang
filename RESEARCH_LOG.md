# Research Log

Chronological, timestamped where practical. All times are wall-clock within a single
session on 2026-08-11.

## Setup

- Created isolated project directory `D:\Others\grid_no_isosceles_bigbang` with its
  own git repo, separate from unrelated personal files in `D:\Others`.
- Verified environment: Python 3.12.7, numpy 1.26.4, scipy available, git 2.47.1.
- Confirmed network access (curl to github.com returned 200).

## Baseline recovery

- Located the official problem repository directory via GitHub API: only one file
  present, `subsets_of_the_grid_with_no_isosceles_triangles.ipynb` (no separate
  coordinate/data files).
- Downloaded the notebook directly from raw.githubusercontent.com.
- Read the notebook in full. Found the final reported constructions in cell-1:
  `sol_64` (112 points) and `sol_100` (164 points), verified by the notebook's own
  `verify_construction()` (an O(|S|^3) `itertools.permutations` triple check, matches
  our own bruteforce cross-check's algorithmic shape).
- Also found, in cell-4, the notebook's actual evolved SEARCH ALGORITHM (not the
  final answer) — an `IsoscelesFreeSet` incremental structure plus a two-phase
  symmetric-build + asymmetric-refinement ILS. This cell's own hardcoded
  fallback/seed constructions (108 points for n=64, 160 for n=100,
  `construction_n_64_64` / `construction_n_100_100` variables) are NOT the paper's
  final reported numbers — they are intermediate seeds referenced inside the search
  code itself. Deliberately did NOT extract these into `official_raw.py` to avoid
  confusing them with the actual 112/164 baseline (see the docstring warning in that
  file).
- Confirmed via GitHub commit history that the notebook's blob content is unchanged
  since a June 2026 "rename" commit (previous filename was `no_isosceles_triangles.ipynb`;
  content blob sha identical) — i.e. our downloaded copy is current and no newer
  construction has been pushed to the official repo.

## Verification

- Implemented `src/verification/oracle_verifier.py`: deliberately slow, obviously
  correct pivot-distance method plus an independent-logic brute-force triple method,
  both using pure Python arbitrary-precision integers, with a `full_cross_check`
  helper.
- Wrote 15 unit tests (`tests/test_oracle_verifier.py`). One test initially FAILED —
  not a verifier bug but a bug in my own test fixture (`(0,0),(1,0),(0,2),(3,1)` is
  actually illegal: pivot (1,0) has squared distance 5 to both (0,2) and (3,1)).
  Fixed the fixture, documented the catch in the test file itself, re-ran: 15/15 pass,
  including a 300-trial randomized fuzz cross-check between the two algorithms.
- Verified both official baselines with this oracle: both legal (SINGLE_VERIFIED at
  this point).
- Dispatched an independent Proposer subagent and an independent Verifier subagent in
  parallel (see Subagent Log below).
- Independent verifier subagent delivered a clean-room second implementation
  (numpy-vectorized distance matrix + per-row sort, cross-confirmed with pure-Python
  arithmetic on any candidate witness), 21/21 own tests passing, and independently
  confirmed both baselines legal from its own JSON re-derivation.
- Ran `src/verification/certify.py` on both baseline candidates: promoted to
  DUAL_VERIFIED. Hashes recorded in `artifact_hashes.json`.

## Search infrastructure

- Implemented `src/search/incremental_state.py`: O(|S|)-per-op add/remove/swap with
  a `cross_check_with_oracle()` method that both re-runs the slow oracle AND
  recomputes the internal per-pivot distance-set cache from scratch to catch
  staleness bugs specifically (not just wrong final legality verdicts).
- Stress-tested (`tests/test_incremental_state.py`): 500 random add/remove/swap moves
  with a full oracle cross-check after EVERY move (not just periodically, since n is
  small enough to afford it in testing), plus a multi-swap ejection-chain test and a
  checkpoint-restore roundtrip test. 3/3 pass, zero divergence found.

## Proposer subagent (Round 1)

- Dispatched with the mathematical definition, pointers to the official notebook and
  baseline data, and an explicit instruction to write only inside `scratch/proposer/`.
- Delivered `scratch/proposer/proposal_round1.md`: a read of the official notebook's
  actual search algorithm, structural observations on the two baselines (central
  symmetry, empty-center region, sparse row/column usage — all explicitly flagged as
  OBSERVATIONS on a sample size of 2, not proven), and three concrete strategies.
- Key finding surfaced by the Proposer: the official notebook imports
  `scipy.optimize.milp` / `LinearConstraint` / `Bounds` but never actually calls them
  in the shown evolved program — every accept/reject decision there is greedy or a
  symmetry projection, never an exact sub-instance solve. This motivated the primary
  search route actually implemented.

## Search execution

- Implemented `src/search/lns.py` (greedy-repair LNS) and
  `src/search/lns_exact_repair.py` (exact 0-1 ILP repair via `scipy.optimize.milp`,
  formulation documented in the module docstring: fixed-pivot distance-groups force
  candidates to 0 or cap their sum at 1; candidate-pivot pairs add
  `x_p + x_a + x_b <= 2` constraints).
- n=64, greedy-repair LNS, 30s, seed=1: no improvement (stayed at 112).
- n=64, exact-MILP-repair LNS, 60s, seed=1: 8613 exact regional repairs, no
  improvement (stayed at 112).
- n=100, exact-MILP-repair LNS, 420s, seed=7: 25153 exact regional repairs, final
  size 164 throughout — no improvement over the baseline (`logs/lns_exact_n100_seed7.json`).
- Combined across both grids: 33766 independently-solved exact 0-1 ILP regional
  repairs, zero improving moves found.
- Added `tests/test_lns_exact_repair.py`: validated the MILP repair encoding against
  brute-force enumeration on 3 synthetic instances (all match exactly), including
  one case that caught ANOTHER test-fixture bug (a hand-picked "legal" fixed set
  that was actually illegal — same pattern as the earlier oracle-verifier test
  fixture bug; fixed the fixture, not the code).

## Red Team subagent (Round 1)

- Dispatched in parallel with the n=100 background search, given six required
  concrete attacks (definition edge cases including all-3-pivot-rotation checks,
  incremental-state divergence hunting, malformed-input injection, serialization
  round-trip, project-wide overclaim-language scan, and a from-scratch synthetic
  MILP-encoding correctness check) plus explicit scope restriction to `audits/` only.
- Delivered `audits/red_team_round1.md`: ran all 6 attacks for real with actual
  scripts and actual output. Result: PASS overall, one LOW-severity finding
  (Finding #1 — `src/search/lns_exact_repair.py`'s docstring overstated how often
  intermediate search states are re-verified against the slow oracle: only the
  initial state and each new-best improvement are checked, not every accepted
  `current` update; the function's actual RETURNED output was always safe
  regardless, since only oracle-verified `best` states are ever returned).
  4500+ incremental-state operations checked after every single move (not just
  checkpoints) found zero divergence. MILP encoding independently re-validated
  against brute force on 3 more synthetic cases (separate from the main agent's own
  3). Baseline arrays spot-checked by hand: correct counts, no duplicates, no
  off-grid points, sample pairwise distances recomputed by hand and matched.
- Main agent fixed Finding #1 by correcting the docstring to accurately describe
  the oracle-call frequency (see `src/search/lns_exact_repair.py`); re-ran the full
  42-test project suite afterward, all still pass.

## Literature / novelty audit

- WebSearch + WebFetch + GitHub commit-history check (see `record_registry.md` for
  full detail and caveats). No source found reporting a legal construction beating
  112 (n=64) or 164 (n=100) for the exact Problem 6.59 definition. Two candidate
  "false positive" papers (isosceles-RIGHT-triangle-only Salem-Spencer construction;
  a different-forbidden-configuration grid paper; an MCTS paper on unrelated
  extremal problems) were checked and explicitly ruled out as addressing different
  problems, not superseding results.

## Round 2 opened (user requested unrestricted time/compute)

User explicitly lifted the time/compute constraint and asked for the deferred
strategies (Strategy A/B, full greedy multistart, a genuinely new search round,
lazy-constraint/hypergraph search) to actually be executed rather than left as
future work. Round 2 begins here.

**Disclosed incident:** Attempted `pip install ortools` to enable CP-SAT lazy-
constraint search. This installed into the shared/global Anaconda base
environment (not a project-local venv) and silently upgraded `numpy` 1.26.4 ->
2.5.2 and `protobuf` 6.33.0 -> 6.33.6 system-wide, which pip itself flagged as
breaking version pins for `gensim`, `numba`, `presidio-analyzer`, `scipy`,
`streamlit`, and `ultralytics` — packages unrelated to this project. This was a
shared-system side effect that should have been done in an isolated environment
from the start; caught immediately (before any further work), reverted via
`pip uninstall ortools immutabledict` + `pip install --force-reinstall
numpy==1.26.4 protobuf==6.33.0`, verified `numpy`/`scipy.optimize.milp` import
correctly again and the full 42-test project suite still passes. Going forward,
any additional solver dependency (e.g. OR-Tools for CP-SAT) will be installed
only inside a project-local virtual environment, never into the global/base
interpreter.

## Round 2 execution

- Isolated venv (`.venv_solver/`) created; OR-Tools CP-SAT installed there only.
- Implemented and tested `sa_exact_repair.py`, `lns_multiregion.py`,
  `symmetry_guided.py`, `cpsat_lazy.py`, `cpsat_small_n_sweep.py`,
  `cpsat_full_upper_bound.py`. Two more hand-verified-legal test fixture bugs
  caught and fixed (same class as Round 1's).
- Dispatched Round 2 Proposer subagent (`scratch/proposer/proposal_round2.md`):
  gap analysis of Round 1, design recommendations for all 4 strategies, new
  structural hypotheses H-005 to H-008. Independently re-confirmed H-006/H-006b.
- Ran all 4 new strategies for 30 min each on n=64 and n=100, plus a full-budget
  greedy multistart. No improvement over 112/164 found by any route (see
  `failed_ideas.md` F-005 to F-009, `ROUND_LOG.md` Round 2).
- Small-n exact sweep produced genuine new results: C(4)=6, C(5)=7, C(6)=9,
  C(7)=10 (machine-proven). A separate full-constraint-enumeration attempt for
  n=64 at target 113 was inconclusive after ~97 minutes.

## Discovery: a concurrent agent session on the same repository

While finishing Round 2 documentation, discovered (via an unexpected file,
`src/search/orbit_defect_search.py`) that a separate, independently-running
Cursor AI agent session had been operating on this exact same repository
concurrently. Investigated the full scope (a `.cursor/plans/` file, an extensive
`long_horizon_run_20260811_183737/` campaign, `scratch/agent_c/`,
`scratch/audit/`, `scratch/red_team_wave2/` trees, 72+ commits and growing,
a `git remote origin` pointing to a GitHub repo). Paused all further writes and
asked the user for guidance before proceeding (see conversation) rather than
silently absorbing, ignoring, or trying to reconcile the situation unilaterally.
User confirmed: this is their own authorized concurrent work via a different
tool, and asked for the other session's Wave 2 results to be given a proper
unified audit rather than either ignored or blindly trusted.

Audited the other session's Gate 0/Gate 1/Wave 2 mathematical claims (its Wave 3
was still live/a moving target during this audit and was explicitly excluded from
scope). Found its work disciplined, honestly hedged, and free of overclaim
language. Its core novel finding (a Hamming-shell structural exclusion for n=100,
derived via minimum-vertex-cover blocker-graph analysis) exactly cross-validates
this project's own independently-derived H-006 (derived via direct brute-force
simulation) -- two different algorithms agreeing on identical numbers for both
grids. Incorporated as `claim_registry.md` Claim 8, with full attribution and
methodology disclosure in the new `CONCURRENT_AGENT_AUDIT.md`.

Fixed one concrete data-integrity casualty of the entangled commit: a duplicate
"F-004" section in `failed_ideas.md`, resolved by renumbering the other session's
entry to F-010 with a provenance note (content preserved, not deleted).

Dispatched a Round 2 Red Team subagent to independently audit all new Round 2
code AND the concurrent-agent audit's own fairness/overclaim discipline. See
`audits/red_team_round2.md`.

*(Log continues below.)*
