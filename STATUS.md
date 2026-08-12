# Current Status

Current phase: **Round 2 complete.** The user explicitly lifted all time/compute
constraints after Round 1 and asked that the previously-deferred strategies
actually be executed; they were, plus one more (CP-SAT lazy-constraint global
search) and a bonus small-n exact-value sweep. Round 2's own Red Team subagent
returned PASS_WITH_FINDINGS (no correctness/verification defects; findings were
about documentation freshness, now resolved by this update). A separate,
independently-running concurrent Cursor agent session was also discovered
operating on this same repository during Round 2 — see `CONCURRENT_AGENT_AUDIT.md`
for the full incident report and audit.

Primary n: 100 (secondary: 64)

Verified baseline: n=64 (112 pts, DUAL_VERIFIED), n=100 (164 pts, DUAL_VERIFIED) —
unchanged across both rounds.

Current best candidate for the main targets: still the baseline itself — 112
(n=64) / 164 (n=100). **No candidate exceeding either baseline was produced by
this session's own search, nor by the independently-audited concurrent agent
session, across two full rounds and 8 distinct search strategies.**

Current best certified size: 112 (n=64, DUAL_VERIFIED), 164 (n=100, DUAL_VERIFIED)

**New this round — genuine exact results at small n:** C(4)=6, C(5)=7, C(6)=9,
C(7)=10, all machine-proven (greedy lower bound + CP-SAT infeasibility upper-bound
proof), independently reproduced with a different seed by the Round 2 Red Team.
See `claim_registry.md` Claim 6.

**New this round — cross-validated structural exclusion:** no legal 165-point set
exists within Hamming distance 1 of the certified n=100 baseline (a narrow
neighborhood exclusion, NOT a claim that C(100)<=164), independently derived by
two different methods/sessions. See `claim_registry.md` Claim 8.

Search methods tried across both rounds, all finding no improvement over 112/164:
LNS+exact-MILP single-region repair (Round 1, 33766 repairs), greedy-repair LNS
(Round 1), tabu search (Round 1, provenance-flagged), SA+periodic exact repair
(Round 2), multi-region exact repair (Round 2), symmetry-guided from-scratch
construction (Round 2), full-budget greedy multistart (Round 2), CP-SAT
lazy-constraint global search incl. a 40.2-million-constraint full-enumeration
attempt for n=64 (Round 2, inconclusive within time budget). Full detail:
`failed_ideas.md` (F-001 through F-011), `ROUND_LOG.md`.

Best structural observations:
- H-001 (near-total central point symmetry: 100.0% n=100, 96.4% n=64)
- H-002 (large empty central region)
- H-006/H-006b (both baselines sit at an EXACTLY FLAT single-point-removal AND
  single-symmetric-orbit-removal local optimum — independently confirmed by
  THREE separate implementations: the Round 2 Proposer subagent, the main agent,
  and the concurrent agent session's Gate-1 vertex-cover analysis)
- H-005, H-007, H-008 (conflict gradient, row/column occupancy quantization,
  symmetry-breaking point structure)

All in `hypotheses.md`.

Most important rejected candidate: none — no candidate produced by this project
(in either round) ever failed verification; every search route simply never
produced an improving legal candidate to test.

Most important verifier bug found: none in either verifier, across both rounds.
Round 1 found one LOW-severity documentation-accuracy defect (fixed). Round 2's
Red Team ran substantially more adversarial fuzz testing (37 fresh-script runs,
8993 individual oracle cross-checks targeting a specific bug class) and found
zero correctness or verification-pipeline defects in any of the 6 new Round 2
modules.

Largest unresolved gap: whether a construction not locally reachable from either
baseline (i.e. requiring a fundamentally different structure, not a
region-limited or Hamming-neighborhood-limited move from SOL_64/SOL_100) exists.
Two full rounds of local/regional/global search from these exact starting points,
across 8+ distinct strategies and two independent research efforts, found
nothing — but this remains, honestly, unresolved as a matter of mathematical
fact (see Limitations in FINAL_REPORT.md).

Subagent rounds completed: 2 full rounds (Round 1: Proposer, Independent
Verifier, Red Team; Round 2: Proposer, Red Team — five independent subagent
dispatches total, all real, not main-agent role-play), plus an independently
audited concurrent research effort from a separate agent session (not dispatched
by this project, discovered and disclosed mid-round).

Novelty status: no larger construction found in the literature scope searched
(Round 1, see `record_registry.md`, explicitly caveated as non-exhaustive); no
novel candidate exceeding 112/164 produced by our own search or the audited
concurrent session. Final verdict: **REPRODUCED_BASELINE / METHODOLOGICAL_PROGRESS**
(see FINAL_REPORT.md Section 10 for the authoritative statement, updated for
Round 2).
