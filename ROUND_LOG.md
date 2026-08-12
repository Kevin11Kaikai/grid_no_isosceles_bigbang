# Round Log

## ROUND 1

**1. Proposer output:** `scratch/proposer/proposal_round1.md`. Three strategies
proposed (Tabu/informed-removal, SA-with-relaxed-energy+exact-repair,
LNS-seeded-from-baseline+exact-MILP-repair). Recommended Strategy C (LNS+MILP) as
best time/payoff given a minutes-to-tens-of-minutes budget, since it starts from the
already-strong 112/164 baselines rather than from scratch.

**2. Main Agent selection:** Implemented Strategy C
(`src/search/lns_exact_repair.py`) plus a simpler greedy-repair LNS baseline
(`src/search/lns.py`) for comparison. Ran:
- n=64, greedy-repair LNS, 30s pilot, seed=1: no improvement (112 -> 112).
- n=64, exact-MILP-repair LNS, 60s pilot, seed=1, 8613 MILP solves: no improvement
  (112 -> 112).
- n=100, exact-MILP-repair LNS, 420s (7 min) run, seed=7: **in progress / see
  STATUS.md for resolved outcome** (this round log entry was written while the run
  was still executing in the background; final numbers appended below once
  available).

**3. Candidates/logs saved:** `logs/lns_exact_n100_seed7.json` — RESULT: 25153
exact-MILP regional repairs, final_size=164 (no improvement over baseline). No file
was written to `results/candidates/` for this run since no improving candidate was
ever produced (consistent with the project's rule that a candidate file is only
created when there is something to certify).

**4. Red Team:** Round 1 Red Team subagent dispatched in parallel, auditing:
oracle verifier, independent verifier, incremental state, LNS+MILP exact repair
(including a from-scratch MILP-encoding-correctness check on tiny synthetic
instances), certify.py promotion pipeline, and all existing unit tests, plus a
project-wide scan for overclaim language ("optimal", "world record", "proved",
"C(n) ="). Full findings: `audits/red_team_round1.md`. **VERDICT: PASS**, one
LOW-severity documentation-accuracy finding (Finding #1: `lns_exact_repair.py`
docstring overstated per-iteration oracle re-verification frequency; final returned
candidates were unaffected). Fixed in the docstring by the main agent.

**5. Main Agent decision:** PROMOTE (both baselines, DUAL_VERIFIED, unchanged) /
REPAIR (Finding #1 docstring, fixed, all 42 project unit tests still pass after the
fix) / STOP further rounds on the same search route (see below) for this session.

**6. Direction for next round (deferred to a future session, not executed here):**
Round 1's LNS+MILP route was run to a point (33766 total exact regional repairs
across both grids, zero improvements, MILP encoding independently validated correct
by both the main agent's own tests and the Red Team's separate synthetic cases) where
continuing to tune the SAME route's parameters (region-kind weights, MILP time
limits, more seeds) would risk STOP RULE D (repeated rounds, parameter tuning only,
no new structure) rather than STOP RULE E (compute growing, no improvement) territory
it has already reached. The Proposer's two unexecuted strategies (Strategy A: tabu
search with blocking-score-informed removal; Strategy B: simulated annealing on a
relaxed penalty landscape with periodic exact repair) remain the most promising
genuinely-different next moves and are recorded as future work in FINAL_REPORT.md
rather than rushed into this session's remaining budget at the expense of honest,
complete reporting.

**Round 1 closed** within its original session-bounded scope. The user then asked
(after reviewing the Round 1 report) whether the project had stopped early due to
time pressure rather than genuinely searching for improvement, and explicitly
lifted all time/compute constraints, asking that the previously-deferred
strategies actually be executed. Round 2 follows.

## ROUND 2

**1. Proposer output:** `scratch/proposer/proposal_round2.md`. Real independent
subagent, restricted to `scratch/proposer/`, dispatched to review Round 1's
negative result and design the four newly-requested strategies. Key finding: a
critical gap analysis showing Round 1's single-region repair structurally cannot
find improvements requiring simultaneous multi-region changes, plus new structural
hypotheses H-005 through H-008 (notably H-006/H-006b: both baselines sit at an
exactly-flat single-point AND single-symmetric-orbit removal local optimum).
H-006/H-006b were independently re-confirmed by the main agent with a separate
script (which, in the process, hit and self-caught the same class of point-pair
bug the Proposer itself had already flagged and fixed).

**2. Main agent implementation and execution:** Four new search modules
implemented, tested (with 2 more hand-verified-legal test fixture bugs caught and
fixed, same pattern as Round 1), and run for 30 minutes each on both n=64 and
n=100: SA+exact repair (`src/search/sa_exact_repair.py`), multi-region exact
repair (`src/search/lns_multiregion.py`), symmetry-guided from-scratch
construction (`src/search/symmetry_guided.py`), CP-SAT lazy-constraint global
search (`src/search/cpsat_lazy.py`, via an isolated project-local venv with
OR-Tools). A full-budget greedy multistart was also finally run (previously
deprioritized in Round 1). **No improvement over 112/164 found by any route.**
Full detail and honest caveats (e.g. the SA run's worse-move acceptance branch
never actually triggered in practice) in `failed_ideas.md` F-005 through F-009.

**3. Bonus result:** a small-n exact-value sweep (`src/search/cpsat_small_n_sweep.py`)
combining a greedy lower bound with a CP-SAT lazy infeasibility proof produced
genuine, machine-checked EXACT values: **C(4)=6, C(5)=7, C(6)=9, C(7)=10**. See
`claim_registry.md` Claim 6. A separate, more ambitious full-constraint-enumeration
attempt for n=64 at target=113 (`src/search/cpsat_full_upper_bound.py`, 40.2M
constraints, ~97 minutes total) was INCONCLUSIVE (solver hit its time limit
without resolving) — see Claim 7's resolution.

**4. Process incident: an environment mistake, caught and fixed.** An initial
`pip install ortools` was run in the shared/global Anaconda environment rather
than an isolated one, silently upgrading numpy/protobuf system-wide and breaking
version pins for several unrelated packages (gensim, numba, streamlit, etc.).
Caught immediately, reverted (`pip uninstall` + `pip install --force-reinstall`
back to original pinned versions), verified via the full 42-test project suite
still passing. All subsequent solver dependencies were installed only in a
project-local venv (`.venv_solver/`). See `RESEARCH_LOG.md` for full detail.

**5. Process incident: a second, larger scope discovery — a concurrent agent.**
While finishing Round 2 documentation, the main agent discovered that a separate,
independently-running Cursor AI agent session had been operating on this exact
same repository concurrently (user-confirmed as their own authorized work on a
different tool, not a third party). This caused a real, disclosed data-integrity
issue (a duplicate "F-004" section, resolved by renumbering) via an entangled git
commit. Full narrative, and an independent audit of that other session's own
mathematical claims (one of which -- a Hamming-shell structural exclusion for
n=100 -- was cross-validated against this project's own H-006 and incorporated as
`claim_registry.md` Claim 8), is in `CONCURRENT_AGENT_AUDIT.md`.

**6. Red Team:** Round 2 Red Team subagent dispatched, restricted to `audits/`,
auditing all new Round 2 code, the small-n sweep's reproducibility, the
concurrent-agent audit's own claims/attribution for fairness and overclaim, and
checking for any further duplicate-section damage from the entangled commit. Full
findings: `audits/red_team_round2.md`.

**7. Main agent decision:** See STATUS.md / FINAL_REPORT.md for the final,
Red-Team-informed verdict.
