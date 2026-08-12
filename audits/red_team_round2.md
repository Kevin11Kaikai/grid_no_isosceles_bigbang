# Red Team / Skeptic Audit — Round 2

Auditor: independent Red Team subagent, scope restricted to `audits/` only (no
files created or modified outside `audits/` at any point — verified at the end
via `git status --porcelain`, see the VERDICT section). Scope: the four Round 2
search modules (`sa_exact_repair.py`, `lns_multiregion.py`, `symmetry_guided.py`,
`cpsat_lazy.py`) plus the two bonus CP-SAT scripts (`cpsat_small_n_sweep.py`,
`cpsat_full_upper_bound.py`), the small-n exact-value claim, the headline
negative-result numbers in `failed_ideas.md`, the concurrent-agent audit and
Claim 8, and a project-wide documentation-integrity sweep.

All commands below were actually executed against the live repository at
`D:\Others\grid_no_isosceles_bigbang` on 2026-08-12, using the system Python
3.12.7 / numpy 1.26.4 / scipy 1.13.1 environment for the non-ortools modules and
`.venv_solver\Scripts\python.exe` (ortools) for the CP-SAT modules. Helper
scripts used to run these attacks are preserved at `audits/_rt2_scripts/` for
reproducibility (all written inside `audits/`, per this round's scope
restriction). Raw output is quoted verbatim (trimmed only where noted).

**Note on timing:** this repository was under **active, concurrent edits by the
main agent** (finishing Round 2 documentation) and by a **separate,
independently-running concurrent Cursor agent session** (its own "Wave 3" work,
disclosed in `CONCURRENT_AGENT_AUDIT.md`) for the entire duration of this audit.
Some findings below are explicitly timestamped/snapshotted for this reason —
see Finding R2-4.

---

## Attack 1 — Code review: is every `best`/return path oracle-re-verified?

Read `src/search/sa_exact_repair.py`, `src/search/lns_multiregion.py`,
`src/search/symmetry_guided.py`, `src/search/cpsat_lazy.py`,
`src/search/cpsat_small_n_sweep.py`, `src/search/cpsat_full_upper_bound.py` in
full, tracing every code path that assigns to a `best`/`best_legal` variable or
that constitutes the function's return value.

Findings, by file:

- **`sa_exact_repair.py`**: `best` is only ever reassigned inside
  `if len(current) > best_size:` (line ~151), which calls
  `is_legal_pivot_method` unconditionally *before* the assignment, and raises
  `AssertionError` (hard fail, not silent) on disagreement. The final return
  (`return sorted(best), meta`) is preceded by one more independent
  `is_legal_pivot_method(list(best), n)` check (line ~177). Every path to
  `best`/return is oracle-verified. The only state that is *not* verified on
  every step is the non-best `current` (checked only every
  `oracle_check_every=200` iterations) — but `current` never leaks into `best`
  or the return value without passing the unconditional new-best check first,
  so this is not a gap in the final output (same pattern the module's own
  docstring explicitly discloses up front, learning from Round 1 Finding #1).
- **`lns_multiregion.py`**: identical structure/verdict — `best` update and
  final return are both oracle-gated (lines ~104, ~123).
- **`symmetry_guided.py`**: `symmetric_build_once` itself never calls the slow
  oracle (only `IncrementalIsoscelesFreeSet.can_add`, already extensively
  stress-tested — see Attack 2 below). `symmetric_multistart` gates every
  `best` promotion (`if len(pts) > best_size:`, line ~148) and the final return
  (line ~156) on `is_legal_pivot_method`. No gap.
- **`cpsat_lazy.py`**: `cpsat_lazy_maximize`'s `best_legal` is only reassigned
  inside the `if not new_cuts:` branch (line ~211-220), itself gated by
  `is_legal_pivot_method` immediately above (with an `AssertionError` guard
  that would fire if the "zero violations" self-check and the oracle ever
  disagreed — never observed). `cpsat_prove_upper_bound`'s only points-bearing
  return path (`FEASIBLE_FOUND`) is oracle-gated the same way (line ~316).
  `INFEASIBLE_PROVEN`/`INCONCLUSIVE` never return points, so no legality claim
  is at risk there.
- **`cpsat_full_upper_bound.py`**: the `FEASIBLE`/`OPTIMAL` branch explicitly
  checks the oracle and, on disagreement, downgrades the verdict string to
  `"ENCODING BUG: ... DO NOT TRUST"` rather than silently reporting a candidate
  — the strongest of the six files' guard patterns.
- **`cpsat_small_n_sweep.py`**: both the lower-bound (`assert ok` after
  `greedy_multistart`) and the `FEASIBLE_FOUND` upper-bound branch
  (`assert ok2`) are oracle-gated before being trusted.

**Result: PASS.** No gap found in any of the six files' final-output
verification discipline. This is a genuine improvement over Round 1 (whose
Finding #1 was exactly this class of gap in `lns_exact_repair.py`'s
docstring) — every Round 2 module's docstring *pre-discloses* the
"not every intermediate state, only best/return" pattern instead of
overclaiming full coverage, and the actual code backs up the disclosure.

One informational (non-defect) note: `src/search/greedy.py`'s
`greedy_multistart` (a Round 1 file, reused as the lower-bound step inside
`cpsat_small_n_sweep.sweep()`) does not itself oracle-verify its `best` —
it relies on `IncrementalIsoscelesFreeSet` alone internally, and the caller
(`sweep()`, and the module's own `__main__` block) does the oracle check
afterward. Both actual call sites do check, so this is not a live gap, just
worth flagging if `greedy_multistart` is ever called from new code without
a follow-up oracle check.

---

## Attack 2 — Fuzz test the four search functions on synthetic small grids

Script: `audits/_rt2_scripts/fuzz_modules_sys.py`. Ran `sa_exact_repair_run`,
`lns_multiregion_run`, and `symmetric_multistart` on n in {8, 10, 12, 16} (3
seeds each for the first two, plus n in {1, 2, 3} as degenerate edge cases),
short 1-3s budgets, from `greedy_once`-constructed random legal starting
points. **Every** returned point set was independently checked against THREE
separate legality implementations from a fresh script this session wrote (not
just re-invoking the search module's own internal check): `is_legal_pivot_method`
(the project's primary oracle), `is_legal_bruteforce_triples` (an
algorithmically-distinct O(|S|^3) triple enumeration, for |S|<=80), and
`verify_independent` (the fully clean-room-implemented, numpy-vectorized
independent verifier in `src/verification_independent/`).

```
sa_exact_repair(seed=1) n=  8 size=  13 pivot=True bruteforce=True independent=True -> PASS
lns_multiregion(seed=1) n=  8 size=  12 pivot=True bruteforce=True independent=True -> PASS
... [37 runs total, n in {1,2,3,8,10,12,16}] ...
sa_exact_repair(tiny n=3) n=  3 size=   4 pivot=True bruteforce=True independent=True -> PASS
lns_multiregion(tiny n=3) n=  3 size=   4 pivot=True bruteforce=True independent=True -> PASS
symmetry_guided(tiny n=3) n=  3 size=   4 pivot=True bruteforce=True independent=True -> PASS

=== SUMMARY: 37 runs, 0 FAILED ===
ALL PASS
```

**Result: PASS.** Zero disagreements across all three independent legality
checks, 37 runs, 7 grid sizes including 3 degenerate edge cases (n=1,2,3).

One informational (non-defect) observation surfaced by the n=1 edge case:
`symmetry_guided.symmetric_build_once` returns **size 0** for n=1, because its
coupled-pair logic explicitly skips any point equal to its own reflection (the
grid center under odd n) rather than placing it as an unpaired single — even
though placing that lone center point alone is trivially legal. This is not a
correctness bug (0 points is still a legal, if suboptimal, output) and the
module's own docstring already scopes itself to even n (64, 100) where this
never arises; flagged only for completeness since this session's fuzzing
happened to probe it.

---

## Attack 3 — Targeted reflect-pair-logic fuzzing (per H-006b bug-class warning)

`hypotheses.md` H-006b explicitly documents that this codebase's point-**pair**
logic (which member of a pair is actually present/occupied) has already
independently bitten two separate authors (the Proposer subagent and the main
agent, in two separately-written H-006b analysis scripts). Since
`symmetry_guided.py`'s `reflect()`-based coupled-pair placement is exactly this
class of logic, this attack targeted it specifically.

Script: `audits/_rt2_scripts/fuzz_symmetry_pairs.py`. Imports the REAL
`reflect()` function from `symmetry_guided.py` (not a reimplementation) and
drives `IncrementalIsoscelesFreeSet` through a long random sequence of six
operation types mirroring and stress-extending the module's actual logic:
coupled-pair add (with rollback-on-partial-failure, exactly as in
`symmetric_build_once`), pair remove, single add, single remove,
"remove-one-of-a-pair" (deliberately breaks symmetry, mirroring the exact
scenario H-006b's bug involved), and "re-add the reflection when the partner
may or may not be present." **`cross_check_with_oracle()` was called after
EVERY single operation** (not periodically), and every resulting state was
additionally checked against `verify_independent` (the clean-room verifier).

```
n=  6 seed=1: 300 ops, 0 divergence, reflect() involution OK, final size=3
n=  6 seed=2: 300 ops, 0 divergence, reflect() involution OK, final size=4
... [30 (n, seed) combinations, n in {6,7,8,9,10,12} incl. odd n, 300 ops each] ...
n= 12 seed=5: 300 ops, 0 divergence, reflect() involution OK, final size=11

--- symmetric_build_once (real production function) direct replay ---
symmetric_build_once replay: all legal   [n in {8,10,12,16} x seed 1-10 x break_prob in {0, 0.05, 0.2} = 120 runs]

=== TOTAL cross_check_with_oracle() calls: 8993, divergences: 0 ===
ALL PASS
```

**Result: PASS.** 8993 individual oracle cross-checks (every single add/remove
operation, not just checkpoints) plus 120 direct replays of the actual
production `symmetric_build_once` function across a break-probability sweep —
zero divergences, zero incremental-cache staleness, and `reflect()` confirmed
to be a genuine involution on every grid size tested. The specific bug class
H-006b warned about (mishandling which member of a reflected pair is actually
present) was not found in `symmetry_guided.py`'s own add/remove logic under
adversarial fuzzing.

---

## Attack 4 — Spot check F-005: is `accepted_worse_moves: 0` a dead branch or a real fact?

`failed_ideas.md` F-005 reports `accepted_worse_moves: 0` for both the n=64 and
n=100 30-minute SA runs, with the interpretation that the delta<0 Metropolis
acceptance branch "never actually triggered in practice at these parameters."
This attack tests whether that branch is even reachable, or whether it is dead
code silently making the "0" meaningless.

Script: `audits/_rt2_scripts/spotcheck_sa_worse_moves.py`. Deliberately
adversarial parameters designed to force delta<0 outcomes: `milp_time_limit_s
= 0.01` (starves HiGHS so it more often returns weak/suboptimal incumbents),
`T0 = 8.0` (lenient acceptance), whole-grid `region_size_cap = n*n`, on n in
{10, 12, 14}, 5 seeds each, 4s budgets.

```
n=10 seed=1: iterations=  751 accepted_worse_moves=  83 final_size= 16 initial_size= 10 final_legal=True
n=10 seed=2: iterations=  813 accepted_worse_moves=  74 final_size= 16 initial_size= 12 final_legal=True
... [15 runs total] ...
n=14 seed=5: iterations= 1679 accepted_worse_moves=  64 final_size= 21 initial_size= 16 final_legal=True

RESULT: accepted_worse_moves > 0 achieved under adversarial params -- the delta<0
branch is LIVE code ...
```

**Result: PASS.** `accepted_worse_moves` fired 15-85 times per run across all
15 (n, seed) combinations tested (never once stayed at 0), and every final
`best` still passed the oracle check. This confirms the delta<0 Metropolis
branch is genuinely reachable code, not dead — so F-005's reported `0` at
*production* parameters (n=64/100, generous `milp_time_limit_s=3.0`, `T0=3.0`,
large-but-not-whole-grid region caps) is a real empirical fact about those
specific runs (consistent with H-006's "exactly-flat local optimum" finding:
well-provisioned MILP repairs on a near-optimal baseline rarely have room to
legally shrink), not evidence the branch itself was unreachable or broken.

---

## Attack 5 — Spot check F-006: multi-region iteration/MILP-call counts

Compared the prose numbers in `failed_ideas.md` F-006 against the actual saved
log artifacts directly:

```
$ [Read] logs/multiregion_n64_seed1.json
"iterations": 87960, "milp_calls": 87960, "wall_time_s": 1800.007331609726,
"improvements": [], "final_size": 112, "initial_size": 112

$ [Read] logs/multiregion_n100_seed1.json
"iterations": 44980, "milp_calls": 44980, "wall_time_s": 1800.016693353653,
"improvements": [], "final_size": 164, "initial_size": 164
```

Both exactly match F-006's claimed "87960 iterations" (n=64) / "44980
iterations" (n=100) and the ~1800s (30-minute) wall-clock budget. Also
cross-checked F-005's sibling claim the same way:

```
$ [Read] logs/sa_exact_n64_seed1.json  -> iterations: 105006, accepted_worse_moves: 0, wall_time_s: 1800.02
$ [Read] logs/sa_exact_n100_seed1.json -> iterations: 60032,  accepted_worse_moves: 0, wall_time_s: 1800.03
```

Exact match to F-005's prose. Both `multiregion_n{64,100}_seed1.json`'s
`points` field is byte-identical to `sa_exact_n{64,100}_seed1.json`'s and to
the certified official baselines, consistent with "no improvement found"
(when `improvements: []`, `best` never changes from the seeded initial state).

**Result: PASS.** No discrepancy found between the prose claims in
`failed_ideas.md` and the underlying saved log artifacts for either F-005 or
F-006.

---

## Attack 6 — Spot check F-009: `seed_cuts_from_points` cut count/timing claim

`failed_ideas.md` F-009 claims: *"773812 cuts for n=64 in 0.6s, 2000000
(capped) for n=100 in 2.7s."* Reproduced this independently 3 times, under
`.venv_solver` (ortools), by calling `seed_cuts_from_points` directly on the
official baselines:

```
$ .venv_solver/Scripts/python.exe audits/_rt2_scripts/spotcheck_cutcounts.py   [x3]
n=64: seed_points=112 -> 773812 cuts in 0.500s (capped at 2000000)
n=100: seed_points=164 -> 2000000 cuts in 2.391s (capped at 2000000)
n=64: seed_points=112 -> 773812 cuts in 0.516s (capped at 2000000)
n=100: seed_points=164 -> 2000000 cuts in 2.420s (capped at 2000000)
n=64: seed_points=112 -> 773812 cuts in 0.500s (capped at 2000000)
n=100: seed_points=164 -> 2000000 cuts in 2.420s (capped at 2000000)
```

**Result: the cut COUNT is exactly, deterministically reproducible** (773812
for n=64 every single time — this is a deterministic function of the fixed
baseline point set and grid enumeration order, so exact reproduction is
expected, not a coincidence) and **timing is in the same ballpark** (0.50-0.52s
vs. claimed 0.6s; 2.39-2.42s vs. claimed 2.7s — small variance consistent with
machine load, not a discrepancy worth flagging).

**However, see Finding R2-1 below**: at the start of this audit, the actual
saved log artifact this number should trace back to
(`logs/cpsat_maximize_n64_seed1.json`) contained a *different* run (the OLD,
unseeded 4-round/994s attempt, with `total_cuts` starting from 0 — matching
F-009's own description of the "first, unseeded attempt," not the fix) rather
than a seeded run backing the specific "773812... 0.6s" figure. No log file
anywhere in the repository contained the string "773812" except the prose of
`failed_ideas.md` itself at the time this attack began.

---

## Attack 7 — Independently reproduce the small-n exact sweep with a different seed

Task requirement: re-run `cpsat_small_n_sweep` for n in {4, 5} with a different
seed than the original run (which used seed=1) and confirm the same exact
values. Ran (via direct function call to `sweep()`, output redirected into
`audits/` rather than overwriting `logs/cpsat_small_n_sweep.json`, per this
round's scope restriction — see `audits/_rt2_scripts/reproduce_small_n_sweep.py`
and `audits/_rt2_scripts/small_n_reproduction_seed2.json`):

```
$ .venv_solver/Scripts/python.exe audits/_rt2_scripts/reproduce_small_n_sweep.py
n=4: EXACT: C(4) = 6 (upper bound machine-proven via lazy CP-SAT, lower bound via greedy construction)  (t=30.2s)
n=5: EXACT: C(5) = 7 (upper bound machine-proven via lazy CP-SAT, lower bound via greedy construction)  (t=30.8s)

=== COMPARISON vs original seed=1 sweep (logs/cpsat_small_n_sweep.json) ===
n=4: original(seed=1) lb=6 status=INFEASIBLE_PROVEN | reproduction(seed=2) lb=6 status=INFEASIBLE_PROVEN | MATCH=True
n=5: original(seed=1) lb=7 status=INFEASIBLE_PROVEN | reproduction(seed=2) lb=7 status=INFEASIBLE_PROVEN | MATCH=True
```

**Result: PASS.** C(4)=6 and C(5)=7 both independently reproduced with seed=2
(different from the original seed=1 run), same `INFEASIBLE_PROVEN` status
(a genuine machine-checked infeasibility certificate, not merely "search found
nothing"). This is exactly the kind of independent re-derivation this
project's own stated verification discipline calls for before trusting a new
machine-proved claim, and it holds up.

---

## Attack 8 — Project-wide overclaim scan (Round 2's own new files)

```
$ grep -rniE "optimal|world record|\bproved\b|\bsolved\b|C\([0-9]+\)\s*=" \
    src/search/sa_exact_repair.py src/search/lns_multiregion.py src/search/symmetry_guided.py \
    src/search/cpsat_lazy.py src/search/cpsat_small_n_sweep.py src/search/cpsat_full_upper_bound.py \
    failed_ideas.md hypotheses.md claim_registry.md CONCURRENT_AGENT_AUDIT.md
    tests/test_sa_exact_repair.py tests/test_lns_multiregion.py tests/test_symmetry_guided.py tests/test_cpsat_lazy.py
```

Every hit checked in context (full output omitted here for length; see the
attack log). Categorized:

- `cp_model.OPTIMAL` / `cp_model.FEASIBLE` (`cpsat_lazy.py`,
  `cpsat_full_upper_bound.py`) — raw solver status constants, not prose claims.
- `lns_multiregion.py`'s "optimal"/"sub-optimality" — explicitly scoped to
  per-sub-instance MILP optimality with an immediate correctness disclaimer
  ("possible sub-optimality never risks correctness — only search
  completeness"). Same pattern Round 1 already blessed for the sibling file.
- `claim_registry.md`'s hits are inside "Forbidden wording" guardrail lists, or
  explicit negations ("neither proven optimal nor beaten").
- **The one genuinely interesting case**: `failed_ideas.md` / `claim_registry.md`
  Claim 6 uses **"C(4)=6, C(5)=7, C(6)=9, C(7)=10"** — a literal `C(n) = k`
  pattern, which is on this project's own forbidden-wording list for the main
  C(64)/C(100) claims. This is a **deliberate, explicitly-sanctioned
  exception**, not an overclaim: Claim 6's own "Type" field is
  `NEW_EXACT_RESULT` (not `KNOWN_RESULT`/`NEGATIVE_RESULT` like the
  C(64)/C(100) entries), and unlike C(64)/C(100) (which only have a
  *reproduced lower bound*, never an upper-bound proof), C(4)-C(7) genuinely
  have BOTH bounds machine-proven (greedy lower bound + CP-SAT infeasibility
  upper-bound proof, independently re-verified by this audit in Attack 7) — so
  the equality is mathematically justified here in a way it is not for the
  main grids. This is good practice (a context-sensitive, explicitly-reasoned
  exception to a blanket wording rule), not sloppy overclaiming.
- No new files contained "world record" anywhere.

**Result: PASS.** No overclaim found in any Round 2-authored file (search
modules, tests, or documentation prose).

---

## Attack 9 — `CONCURRENT_AGENT_AUDIT.md` and Claim 8: overclaim / attribution check

Read `CONCURRENT_AGENT_AUDIT.md` in full and `claim_registry.md` Claim 8 in
full (both reproduced faithfully in this session's own context, not
re-summarized from memory).

**Hedging check on Claim 8:** its `Type` field is explicitly
`STRUCTURAL_EXCLUSION` with an inline parenthetical *"explicitly NOT a claim
that C(100)<=164 or C(64)<=112"*; its Forbidden-wording list explicitly bans
"C(100) <= 164", "no larger construction exists anywhere", and "proven
optimal" — all three of the natural over-generalizations a careless reader
might draw from "no legal 165-point set exists within Hamming radius 1." The
Allowed wording is correctly scoped to "one neighborhood," not solution space
generally. **No overclaim found in Claim 8's own wording.**

**Attribution fairness check:** Rather than only re-reading
`CONCURRENT_AGENT_AUDIT.md`'s own paraphrase of the other agent's numbers, this
audit went one level further and read the underlying source document directly:

```
$ [Read] scratch/audit/agent_a/agent_a_report.md
n=64:  "Min deletion LB over unselected q: **1** (2 cells)."
n=100: "Min deletion LB over unselected q: **2** (16 cells)."
```

This confirms, from the primary source (not the secondary paraphrase), that:
(a) for n=64 the MINIMUM deletion count across all 3984 unselected cells is 1,
achieved by exactly 2 cells — exact match to `CONCURRENT_AGENT_AUDIT.md`'s "for
n=64, the minimum is 1, achieved by exactly 2 cells" and to this project's own
H-006 (2/112 points individually open exactly 1 cell); (b) for n=100 the
minimum is 2 (not 1) — i.e. **zero** cells have a deletion requirement of 1 —
exact match to Claim 8's "0/164 points open any cell alone (deletion LB >= 2
for all 9836 unselected cells)". Both agree with this project's own,
main-agent-reconfirmed H-006 numbers. **No fabrication, exaggeration, or
misattribution found** — the numbers CONCURRENT_AGENT_AUDIT.md reports are
exactly what the cited source file says, and both this project's own
independently-derived finding and the concurrent agent's are given equal,
explicit, named credit ("TWO separate concurrent research efforts... (a) this
project's own H-006... (b) a separate...Gate-1 'Agent A' audit").

**One residual caution (not a violation, LOW severity):** `CONCURRENT_AGENT_AUDIT.md`
discloses up front that the other agent's artifacts were "reviewed, not
re-executed line-by-line." This audit's own check above (reading the primary
report) goes one step further than that, but still stops short of reading or
re-running `scratch/audit/agent_a/scripts/blocker_audit.py`'s actual algorithm
— so Claim 8's "two independently-implemented methods converge" framing rests
on this project's own H-006 (which WAS independently re-derived and code-level
verified by the main agent) plus a same-numbers match against an
*unaudited-at-the-code-level* external script's report. This is disclosed
honestly in Claim 8's own provenance note and does not constitute an overclaim,
but the practical evidentiary weight is slightly softer than "two
independently-audited implementations" would be. Recommend (not required) a
future round actually read or re-execute `blocker_audit.py` for a full
code-level cross-check, going beyond report-reading.

**Result: PASS**, with the residual caution above noted for completeness.

---

## Attack 10 — Duplicate/broken section headers

```
$ grep -n "^## " failed_ideas.md hypotheses.md claim_registry.md ROUND_LOG.md
```

failed_ideas.md: F-001 .. F-010 all present, each exactly once (the F-004
collision from the entangled commit is cleanly resolved — the concurrent
agent's entry is now uniquely "F-010", both entries fully preserved, no
lingering duplicate anywhere in the file).
hypotheses.md: H-001, H-002, H-003, H-005..H-008, H-006b — all unique.
claim_registry.md: Claim 1..8 — all unique.
ROUND_LOG.md: `## ROUND 1`, `## ROUND 2` — both unique (see Finding R2-1 for
context on when the Round 2 section appeared).

**Result: PASS.** No duplicate `## ` headers found in any of the four files
checked. The disclosed F-004/F-010 collision is genuinely and cleanly
resolved, not just renamed-with-residue.

---

## Findings

### Finding R2-1 (LOW-MEDIUM, documentation completeness/timing — largely
self-resolving): F-009's cut-count claim was, for most of this audit, not
backed by a matching saved log artifact; the promised "final numbers"
cross-reference is generic, not itemized

`failed_ideas.md` F-009 states the "773812 cuts... 0.6s" / "2000000 (capped)...
2.7s" figures and says *"Status: See ROUND_LOG.md Round 2 section for the
final, properly-seeded outcome."* At the time this audit began:

1. `ROUND_LOG.md` had **no Round 2 section at all** (it ended at "Round 1
   closed... No Round 2 was opened in this session").
2. `logs/cpsat_maximize_n64_seed1.json` contained the OLD, unseeded run (4
   rounds, 994s, `total_cuts` starting at 0) — i.e. exactly the run F-009 itself
   describes as the inefficient "first attempt," not the fix. No file anywhere
   in the repo contained the string "773812" except `failed_ideas.md`'s own
   prose.
3. `STATUS.md` and `FINAL_REPORT.md` were (and, as of this report's writing,
   remain) entirely Round-1-only (`STATUS.md`: *"Current phase: Round 1
   complete... converging to final report rather than opening Round 2"*;
   `FINAL_REPORT.md`: zero "Round 2" mentions anywhere).

During this audit (concretely, while Attacks 4-8 above were running),
`ROUND_LOG.md` gained a full `## ROUND 2` section, and
`logs/cpsat_maximize_n64_seed1.json` / `cpsat_maximize_n100_seed1.json` were
regenerated with fresh timestamps — the new n=64 log now shows
`"seed_cuts_count": 773812`, exactly matching both F-009's claim and this
audit's own independent reproduction (Attack 6). This is a **genuine,
reproducible number** (Attack 6 reproduced it 3/3 times, deterministically) —
the concern here was never that the figure was fabricated, only that it was
briefly under-documented/under-saved relative to what F-009's own
cross-reference promised.

Two residual gaps as of this writing:
- The new seeded n=64 run just saved (128.7s, 2 rounds) is a short
  confirmatory pass, not a 30-minute run comparable in scale to F-005/F-006's
  headline numbers.
- `ROUND_LOG.md`'s new Round 2 section item 2 summarizes CP-SAT with a generic
  *"No improvement over 112/164 found by any route"*, without restating the
  specific seeded cut-count/timing figures F-009 promised would appear there —
  so the specific cross-reference F-009 makes is still not literally satisfied,
  only the general "no improvement" conclusion.
- `STATUS.md` and `FINAL_REPORT.md` remain stale (Round-1-only) as of this
  audit's final check, even though `ROUND_LOG.md`'s new Round 2 section item 7
  explicitly forward-references both files for "the final, Red-Team-informed
  verdict." A reader consulting `STATUS.md` alone right now would incorrectly
  conclude the project stopped after Round 1.

**Why this is LOW-MEDIUM, not HIGH:** no mathematical or verification-pipeline
defect is involved anywhere in this finding — every number involved is
genuine and independently reproducible (Attacks 4-7), and the gap is entirely
one of documentation freshness/cross-reference completeness during an
actively-being-written round, compounded by this repository having two
concurrently-active agent sessions writing to it throughout. Given the main
agent was visibly still updating `ROUND_LOG.md`/`RESEARCH_LOG.md`/the log files
DURING this audit's execution, this is likely to be substantially resolved by
the time this report is read — flagged here as a snapshot, in the same spirit
`CONCURRENT_AGENT_AUDIT.md` used for the other agent's "still live" Wave 3.
**Recommendation:** before closing Round 2, run one more properly-seeded,
full-budget (or explicitly time-capped-and-labeled-as-such) CP-SAT pass for
both n=64 and n=100, save it under a clearly-dated log filename, and update
`STATUS.md`/`FINAL_REPORT.md` to reflect Round 2 (not just `ROUND_LOG.md`/
`RESEARCH_LOG.md`), so a reader of any ONE top-level doc gets an
accurate picture.

### Finding R2-2 (INFORMATIONAL, no action needed): `symmetric_build_once`
returns size 0 for odd n=1

See Attack 2. Not a correctness bug (0 is legal), the module is explicitly
scoped to even n=64/100 where this never arises, and this was only surfaced
by this audit's own adversarial n=1 edge-case probe, not a real usage path in
this project.

### Finding R2-3 (INFORMATIONAL, no action needed): `greedy_multistart`'s
internal `best` is not itself oracle-gated

See Attack 1. Both actual call sites (`sweep()`, the module's own `__main__`)
do perform the oracle check on the result, so this is not a live gap. Flagged
only as a note for any future caller of `greedy_multistart` that skips its own
post-check.

---

## VERDICT

**No correctness or verification-pipeline defect was found anywhere in Round
2's new code.** All six reviewed files (`sa_exact_repair.py`,
`lns_multiregion.py`, `symmetry_guided.py`, `cpsat_lazy.py`,
`cpsat_small_n_sweep.py`, `cpsat_full_upper_bound.py`) oracle-verify every
path that can produce a trusted `best`/return value, and this held up under:
37 fresh-script fuzz runs across 7 grid sizes with triple-verifier
cross-checking (Attack 2); 8993 individual `cross_check_with_oracle()` calls
plus 120 production-function replays targeting the specific point-pair bug
class H-006b warned about (Attack 3); an adversarial attempt to prove the SA
worse-move branch was dead code, which instead confirmed it fires reliably
under the right conditions (Attack 4); exact reproduction of the F-005/F-006
iteration counts against saved logs (Attack 5); 3x-repeated exact reproduction
of F-009's specific cut-count claim (Attack 6); and independent
different-seed reproduction of the small-n exact sweep, C(4)=6 and C(5)=7
(Attack 7). The full project test suite (system Python: 62 tests; `.venv_solver`:
3 more CP-SAT-specific tests) passes, 65/65.

The overclaim scan (Attack 8) found zero violations in any Round 2-authored
file, including correctly identifying Claim 6's deliberate, mathematically-
justified "C(n)=k" exception as good practice rather than a defect. Claim 8
and `CONCURRENT_AGENT_AUDIT.md` (Attack 9) are honestly hedged and fairly
attributed — this audit independently verified the cited numbers against the
concurrent agent's primary source file (not just its paraphrase) and found an
exact match. No duplicate section headers were found anywhere (Attack 10) —
the disclosed F-004/F-010 collision is genuinely, cleanly resolved.

The one substantive finding (R2-1) is a documentation-completeness/timing
issue, not a mathematical or correctness one: `failed_ideas.md` F-009's
specific numeric claim, while genuine and 3x independently reproduced by this
audit, was under-backed by saved artifacts and cross-references at the start
of this audit (partially self-resolved by the main agent's own concurrent
work during the audit), and `STATUS.md`/`FINAL_REPORT.md` remain stale as of
this writing despite `ROUND_LOG.md` now forward-referencing them for the
final verdict.

**Overall judgment: PASS_WITH_FINDINGS.** No CONDITIONAL, no FAIL — every
piece of Round 2's actual search/verification code held up under genuinely
adversarial testing (including several attacks specifically designed to try
to break it: forcing the SA worse-move branch, targeting the exact bug class
H-006b flagged, probing degenerate n). The findings are entirely about
keeping the project's own top-level status documents (`STATUS.md`,
`FINAL_REPORT.md`) and cross-references in sync with the substantial Round 2
work that has, on the actual code/math evidence, been done correctly.
Recommend: (1) finish syncing `STATUS.md`/`FINAL_REPORT.md` to Round 2 before
declaring the round closed; (2) if a "final, properly-seeded" CP-SAT number is
going to be cited by name in `failed_ideas.md`, save the exact run it came
from under a stable log filename so the citation is literally traceable, not
just independently-reproducible-if-someone-re-runs-it (which this audit did,
successfully, but a reader shouldn't have to).

**Scope compliance:** this Red Team session created/modified files only
inside `audits/` (`audits/red_team_round2.md`, `audits/_rt2_scripts/*`),
verified via `git status --porcelain` at the end of the session — every
non-`audits/` modification visible in that output (`RESEARCH_LOG.md`,
`ROUND_LOG.md`, `claim_registry.md`, `failed_ideas.md`, `hypotheses.md`,
`logs/cpsat_maximize_*.json`, and the `long_horizon_run_.../W3_*` files) was
independently confirmed to be attributable to the main agent's own concurrent
documentation work or the separate concurrent Cursor agent session's ongoing
Wave 3 activity, not to this Red Team session.
