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

**Round 1 closed.** No Round 2 was opened in this session — see FINAL_REPORT.md for
the full rationale and final verdict.
