# Concurrent Agent Audit

## What happened

During Round 2 of this project (triggered by the user explicitly lifting all
time/compute constraints and asking that deferred search strategies actually be
run), this session discovered that **a separate, independently-running AI agent
session — a Cursor IDE agent — had been operating on this exact same repository,
concurrently, without this session's knowledge.** The user subsequently confirmed
(when asked) that the associated GitHub remote (`github.com/Kevin11Kaikai/...`) is
their own account, i.e. this was legitimate, user-authorized concurrent work on
the same problem via a different tool, not an unauthorized third party.

Discovery chain: an unexpected file `src/search/orbit_defect_search.py` (1621
lines, referencing "Wave 2 Agent B" terminology never used by this session) led to
finding `.cursor/plans/higher_lower_bound_plan_0f037df3.plan.md`, a
`long_horizon_run_20260811_183737/` directory with its own `FINAL_REPORT.md` /
`PROVED.md` / `STATEMENT.md` / `INCUMBENT.json`, and `scratch/agent_c/`,
`scratch/audit/`, `scratch/red_team_wave2/` trees — an extensive, independently
structured multi-agent research campaign (its own Proposer/"Agent A/B/C"
roles, its own Gate 0/Gate 1/Gate 2 review process, its own Red Team).

## The entanglement incident

The other agent's first commit visible to this session, `2600e8f` ("Add Wave 0-2
search artifacts, audits, and conflict-driven modules"), was made from the same
working directory while this session's own Round 2 files were sitting uncommitted
in the working tree. That commit bundled together the other agent's own new files
**and this session's own in-progress files** (`sa_exact_repair.py`,
`symmetry_guided.py`, `lns_multiregion.py`, `cpsat_lazy.py`, and others) under a
single commit this session did not review or author. One concrete, disclosed
consequence: `failed_ideas.md` ended up with two different sections both titled
"F-004" (this session's, about the Round-1 `tabu.py` provenance anomaly; the other
agent's, about its own re-run of `tabu.py` with different seeds). Resolved by
renumbering the other agent's entry to F-010 with an explicit provenance note (see
`failed_ideas.md`). No content was deleted; both versions are preserved.

The repository also has a git remote (`origin`) and the other agent's own
process notes describe a standing order to commit+push checkpoints to
`origin/master`. This session made no push to that remote and made no attempt to
alter, redirect, or disable it — that is the user's infrastructure to manage.

The other agent's process was **still actively committing during this audit**
(commit count grew from 2 to 72+ within minutes of first discovery; its own
`PROCESS_LESSONS.md` describes an ongoing "Wave 3"). This audit therefore covers a
**snapshot**: its own Gate 0 / Gate 1 / Wave 2 material, which its own
`REGISTRY.md` explicitly marks "Frozen Wave2 facts" (i.e. treated as closed by
that process itself), not its still-in-flight Wave 3 experiments, which remained a
moving target throughout this session and are explicitly out of scope for this
audit.

## Audit of the other agent's mathematical claims (Gate 0 / Gate 1 / Wave 2)

This session independently reviewed (read, not re-executed line-by-line) the
following artifacts: `long_horizon_run_20260811_183737/{STATEMENT,PROVED,
REGISTRY,PROCESS_LESSONS,OPEN_QUESTIONS}.md`, `scratch/audit/agent_a/
agent_a_report.md`, `scratch/audit/agent_c/agent_c_report.md`,
`scratch/audit/gate1_decision.md`, `scratch/red_team_wave2/summary.json`.

**Overclaim scan:** grepped all of its markdown files for the same forbidden
terms this project's own Red Team scans for ("world record", "proved" (bare),
"optimal" (bare), "C(n) = k"). No violation found — the one hit ("OPTIMAL" as a
raw CP-SAT solver status label, e.g. "INFEASIBLE/OPTIMAL/TIMEOUT under scope=...")
is a benign, correctly-scoped usage, not a claim about C(n). Its `PROVED.md` file
name is more assertive than this project's own convention, but its actual content
is entirely hedged DUAL_VERIFIED-lower-bound reproductions and explicitly-scoped
structural facts — it does not claim a new lower bound or an unqualified upper
bound anywhere this session found.

**Core novel claim: `GLOBAL_RIGOROUS_LOWER_BOUND` on deletions (Gate 1, Agent A).**
Statement: for the certified n=100 baseline S0 (164 points), every one of the
9836 currently-unselected grid cells requires deleting **at least 2** existing
points from S0 (a minimum vertex cover of a "blocker conflict graph") before it
could legally be added; for n=64, the minimum is 1, achieved by exactly 2 cells.
Consequence claimed: `GLOBAL_SHELL_EXCLUSION` — no legal 165-point set exists
within Hamming radius r=1 of the n=100 baseline (1 deletion + 2 additions), since
even a single addition already requires 2 deletions under the proven-sound bound.
Their own `STATEMENT.md` is explicit that this is a **structural exclusion, not a
proof that C(100) <= 164** (a genuinely correct distinction: it rules out one
specific neighborhood, not all of solution space).

**Verdict: CREDIBLE, and independently cross-validated by this session's own,
separately-derived H-006** (see `hypotheses.md`): this session's Round 2 work
found, via direct brute-force simulation (not a graph/vertex-cover argument),
that removing any single point from the n=100 baseline opens exactly **0** empty
cells (0/164), and for n=64, exactly **2** of 112 points open exactly 1 cell each
when removed alone — the same "1" vs "2" split, with matching cell counts, that
the other agent's independently-coded vertex-cover analysis reports. Two
differently-implemented methods (this session's exhaustive single-removal
simulation via `IncrementalIsoscelesFreeSet`; the other agent's blocker-graph
minimum-vertex-cover computation) converging on identical numbers for both grids
is real, meaningful corroboration — promoted into `claim_registry.md` as Claim 8
with this cross-validation explicitly cited.

**Wave 2 search results (Agent A/B/C campaigns, red-teamed internally as PASS):**
extensive additional negative search evidence — Hamming-shell exchange search at
several radii (`INFEASIBLE_SCOPED` under explicit, disclosed universes, correctly
NOT labeled a global bound), orbit/defect search (`any_legal_plus1: false`),
fixed-cardinality min-conflict search (best achieved V=3 at n=100/165 and V=2 at
n=64/113 — i.e. even directly searching AT the target size while minimizing
violations, it could not reach zero). All consistent in direction and conclusion
with this session's own Round 1 and Round 2 negative results: **no construction
exceeding 112/164 was found by either process.**

## What was and was not incorporated

- **Incorporated:** the Gate-1 deletion-lower-bound / shell-exclusion finding
  (Claim 8, cross-validated), as corroborating structural evidence alongside this
  session's own H-006/H-006b.
- **Not incorporated as this project's own claims:** the other agent's still-live
  Wave 3 experiments (a moving target during this audit), its own internal
  hypothesis IDs (LH-*, W3-*) and universe-naming scheme (kept in its own files,
  not renamed into this project's `hypotheses.md`), and its own certification
  artifacts under `CERTIFICATES/`/`VERIFICATION/` (not re-verified by this
  session's own dual-verifier pipeline; if that other run ever produces a
  candidate exceeding 112/164, it would need to go through this project's own
  `src/verification/certify.py` promotion path independently, exactly like any
  other candidate, before this project would report it).
- **Not touched:** the git remote, the other agent's own working files, or any of
  its in-progress Wave 3 experiment output.

## Bottom line

Two independently-authored, concurrently-run research efforts on the identical
problem, using different methods, reached the same overall conclusion within
this session's timeframe: **no legal construction exceeding C(64)>=112 or
C(100)>=164 was found**, and a genuine (if narrow) structural exclusion result
(no improvement reachable via a single-point-swap neighborhood of the n=100
baseline) was independently derived by both. This convergence is itself
meaningful evidence, reported honestly here rather than silently folded into a
single narrative that obscures that two separate processes were involved.
