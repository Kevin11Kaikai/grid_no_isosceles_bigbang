# Current Status

Current phase: Round 1 complete. Session compute budget substantially spent;
converging to final report rather than opening Round 2 on the same search route
(see rationale below — avoids STOP RULE D territory).

Primary n: 100 (secondary: 64)

Verified baseline: n=64 (112 pts, DUAL_VERIFIED), n=100 (164 pts, DUAL_VERIFIED)

Current best candidate: the baseline itself — 112 (n=64) / 164 (n=100). No candidate
exceeding either baseline was produced.

Current best certified size: 112 (n=64, DUAL_VERIFIED), 164 (n=100, DUAL_VERIFIED)

Best search method: LNS with exact 0-1 ILP regional repair
(`src/search/lns_exact_repair.py`, `scipy.optimize.milp`/HiGHS). 8613 exact regional
repairs on n=64 (60s) and 25153 on n=100 (420s) — 33766 total independently-solved
exact sub-instance repairs — found zero improving moves on either grid.

Best structural observation: H-001 (near-total central point symmetry: 100.0% for
n=100, 96.4% for n=64) and H-002 (large empty central region) — both independently
re-confirmed by the main agent's own recomputation, matching the Proposer subagent's
figures exactly.

Most important rejected candidate: none — no candidate produced by this project ever
failed verification; the search simply never produced an improving legal candidate
to test.

Most important verifier bug found: none in either verifier. One LOW-severity
documentation-accuracy defect was found by Red Team (Finding #1: the LNS+MILP
module docstring overstated how often intermediate search states were
oracle-re-verified; the final *returned* candidate was always safe regardless).
Fixed in the docstring; see `audits/red_team_round1.md`.

Largest unresolved gap: whether a longer search budget, additional seeds, or the
two not-yet-executed Proposer strategies (Tabu with informed removal; SA on a
relaxed penalty landscape with periodic exact repair) would find an improvement that
this session's single LNS+MILP route and budget did not. Not resolved in this
session.

Best next action (for a future session with more compute): run Proposer Strategy A
(tabu search with blocking-score-informed removal) and Strategy B (SA + exact
repair) as genuinely different search trajectories, since Strategy C (this session's
route) has now been tried thoroughly enough (33766 exact regional repairs, zero
improvement) that further tuning of the same route risks STOP RULE D (repeated
rounds, parameter tuning only, no new structure).

Subagent rounds completed: 1 full round (Proposer, Independent Verifier, Red Team —
three independent subagents actually dispatched and returned, not main-agent
role-play).

Novelty status: no larger construction found in the literature scope searched (see
`record_registry.md`, explicitly caveated as non-exhaustive); no novel candidate
produced by our own search. Final verdict: REPRODUCED_BASELINE /
METHODOLOGICAL_PROGRESS (see FINAL_REPORT.md Section 10 for the authoritative
statement).
