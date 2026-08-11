# Failed / Negative-Result Ideas

Recording negative results explicitly per project discipline: a correct "no
improvement found" is valuable evidence, not a failure to hide.

## F-001: Greedy multistart from scratch (Route A), quick pilot

**What was tried:** `src/search/greedy.py` builds a legal set from an empty grid by
scanning all n^2 points in a random/boundary-first/center-first order and greedily
adding whenever legal.

**Result:** Not run to full budget in this session (superseded by seeding from the
already-good official baselines instead, which is a far higher payoff starting
point given the notebook's own search already spent significant compute reaching
112/164 from scratch). Implemented and unit-exercised via `IncrementalIsoscelesFreeSet`
but not run as a standalone multi-minute experiment.

**Status:** DEPRIORITIZED, not formally falsified — flagged for future work if more
compute becomes available.

## F-002: Randomized-destroy LNS with greedy repair (Route D-lite), seeded from official n=64 baseline

**What was tried:** `src/search/lns.py`: repeatedly destroy a random region (box or
random point subset) of the legal 112-point n=64 baseline, then greedily re-add
points in randomized order. 30-second pilot run, seed=1.

**Result:** 1927 iterations, best size stayed at 112 throughout (`improvements: []`).
No improvement.

**Interpretation:** Consistent with the baseline already being a strong local optimum
under simple random-destroy + greedy-repair, which is essentially the same class of
move the official notebook's own Phase 2 refinement already performs extensively
(8-30% random destroy, greedy refill) — so finding an improvement with an even
simpler repair heuristic in 30s was a long shot from the start; recorded for
completeness rather than as a surprising negative result.

**Status:** STOP RULE E applies (compute growing, no improvement) for this specific
weak-repair variant; superseded by F-003 (exact MILP repair) as the primary route.

## F-003: LNS with EXACT MILP repair (Route D main), seeded from official n=64 baseline

**What was tried:** `src/search/lns_exact_repair.py`: destroy a randomly chosen region
(box / row-or-column band / boundary-frame window), then solve EXACTLY (0-1 ILP via
`scipy.optimize.milp`) for the maximum legal subset of that region's currently-empty
cells given the rest of the (fixed, untouched) set. 60-second pilot, seed=1,
milp_time_limit_s=2.0.

**Result:** 8613 iterations (i.e. 8613 separate exact MILP solves, each on a small
regional sub-instance), best size stayed at 112 throughout (`improvements: []`).

**Interpretation:** This is a stronger negative result than F-002, since each repair
step is provably optimal FOR THAT REGION given the rest of the set fixed — i.e. no
single-region exact repair anywhere the search looked in 8613 tries could find a net
gain. This does not rule out a gain requiring simultaneous changes across multiple
disjoint regions, or regions this search's box/row-col/frame sampling did not
happen to try.

**Status:** See STATUS.md / FINAL_REPORT.md for the parallel n=100 run outcome
(longer budget); this n=64 result is treated as a completed negative data point for
this session's compute budget, not as proof that 113 is unreachable.

## F-004: Tabu with informed removal (Strategy A), seeded from official baselines

**What was tried:** `src/search/tabu.py` — trial-remove small batches scored by how
many sampled empty cells they free, tabu tenure on re-add, boundary-biased refill.
Also multi-seed greedy LNS (4×90s, seeds 101–104) and a center-probe exact-MILP
variant that frees frame points then repairs over the empty center box.

**Result:**
- Tabu n=64, ~150s effective (early plateau), seed=3: 4252 iters, stayed at 112
- Tabu n=100, ~210s, seed=11: 1810 iters, stayed at 164
- Greedy LNS n=64 multiseed: all four seeds stayed at 112 (~22k iters combined)
- Direct check: 0 center cells (ring>11 / >26) are individually addable to either
  baseline without removals

**Status:** NEGATIVE under these budgets/seeds — not a proof that 113/165 are
unreachable; different trajectories (SA+exact repair, longer multi-region destroy)
remain open.

## F-004: Tabu search with informed removal (Proposer Strategy A) — PROVENANCE ANOMALY

**What was tried:** `src/search/tabu.py`: remove the point(s) whose removal is
scored as most likely to free up currently-blocked high-value (boundary-biased)
candidates, tabu the removed point for a tenure window (aspiration override if it
would set a new record), greedily refill in boundary-first order. 30s pilot on
n=64, seed=1, remove_batch=2. Result: 401 iterations (early-stopped on a long
plateau, honoring the wall clock), final size 112 — no improvement.

**PROVENANCE ANOMALY (disclosed for audit integrity):** This file was NOT written
by the main agent, and does not correspond to any file the main agent's own tool
calls created. It appeared in `src/search/` during Round 1, matching the Proposer
subagent's unexecuted "Strategy A" description almost exactly (informed removal,
tabu tenure, aspiration criterion, boundary-biased refill). The Red Team subagent
for this round was explicitly instructed to write ONLY inside `audits/`; based on
file timing and content, it appears the Red Team subagent read
`scratch/proposer/proposal_round1.md` on its own initiative (not instructed to)
and additionally implemented Strategy A outside its assigned scope, in violation of
this project's multi-agent file-scope discipline (project brief section 3: "如果
环境不支持subagents... 不得声称完成了multi-agent审计"-adjacent rule that
subagents must not touch files outside their assigned scope). The main agent did
NOT ask for or expect this file, discovered it only during a final directory sweep,
and is disclosing this explicitly rather than either (a) silently claiming it as
planned work, or (b) silently deleting a working, safe, seemingly-correct
implementation. The code was read in full and sanity-run before being trusted at
all (see above); it uses only this project's own internal modules, performs no
network/destructive operations, and its "best" output is oracle-verified before
being returned (same pattern as the other search routes), so it was judged safe to
report as a bonus data point -- but its origin is a genuine process violation that
should inform how strictly file-scope instructions are enforced/monitored in future
rounds of this project.

**Status:** Reported as an additional (fourth) negative data point, clearly
provenance-flagged. Not treated as an official, main-agent-authored part of the
Round 1 search plan.
