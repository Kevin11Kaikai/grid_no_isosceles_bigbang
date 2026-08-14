# Round 3 — Adversarial Discovery Tournament

**Opened:** 2026-08-14. **Orchestrator:** main agent (Claude Opus 5, Claude Code).
**Objective:** strictly beat 112 (n=64) or 164 (n=100). Primary target **n=100**.

This campaign runs on a **modified** version of the user-supplied "Sol Ultra"
tournament protocol. Every section is adopted as written except Section 2
(hard isolation), which is amended below. The amendment is recorded here so the
deviation is auditable.

## Amendment to Section 2 — "seal the history, not the mathematics"

**Adopted as written:** discovery agents get no web access, no literature, no
prior-art lookup, no sight of the official baseline coordinates (`SOL_64`,
`SOL_100`), no sight of this project's route history (`failed_ideas.md`,
`long_horizon_run_*`, `TOURNAMENT_SEALED/`, `hypotheses.md`, `PROVED.md`).

**Rejected:** the clause sealing structural facts about the object, and the
clause requiring verifiers to be rebuilt from scratch.

**Evidence for the amendment.** Our own sealed (S0-blind) tournament — which is
exactly the configuration Section 2 mandates — reached n=64 **90** and n=100
**137**. An unaffiliated group (arXiv:2606.26399) running a symmetry-aware MCTS
at 7 CPU-days/trial independently reached **≈1.4n** (89.6 / 140) on the same
problem. Two independent measurements put blind generic search at ~1.4n. The
incumbents sit at 1.75n / 1.64n. The 27-point gap at n=100 is therefore
**structural, not compute-bound**, and full isolation is the one configuration
already measured to top out 27 points short.

**Consequence.** Agents ARE told the structural prior (approximate 4-fold
symmetry + boundary concentration is known to carry this problem past 1.4n) and
ARE required to state explicitly how their mechanism handles symmetry and
boundary density. Blind is the *history*, not the *object*.

**Verifiers.** Reused, not rebuilt. `src/verification/oracle_verifier.py` and
`src/verification_independent/independent_verifier.py` are two logically
independent implementations (exact integer arithmetic, different code paths:
per-pivot hash scan vs numpy distance matrix + argsort). They have absorbed 8993
oracle cross-checks and 37 adversarial fuzz runs with zero defects. Section 10's
two-independent-verifier requirement is already satisfied; replacing a
zero-defect component to purchase the appearance of independence is a bad trade.

## Allocation rationale (orchestrator-only; not shown to agents)

`failed_ideas.md` F-001..F-010 plus the concurrent session's routes are
**entirely search metaheuristics**: greedy multistart, LNS (greedy / exact-MILP /
multi-region repair), tabu, simulated annealing, CP-SAT lazy-constraint global
search, symmetry-guided multistart, Hamming shells, pattern-grow, orbit-defect.

Nothing **constructive** has ever been attempted in this repository: no
number-theoretic construction, no recursive/product lifting, no design-theoretic
approach in distance-spectrum space. The known Ω(n/√log n) lower bound comes from
a Behrend-type explicit construction, i.e. from precisely the family nobody here
has touched. Wave 1 is weighted accordingly.

## Wave 1 routes

| Route | Mechanism family | Status |
|---|---|---|
| R1-ALG | Explicit number-theoretic construction (modular/Behrend/Sidon/perfect-difference) | EXPLORING |
| R2-SYM | Imposed 4-fold symmetry + boundary concentration, orbit-level exact solve | EXPLORING |
| R3-REC | Recursive / product lifting from exactly-solved small n | EXPLORING |
| R4-SPEC | Design in distance-spectrum space (Golomb/B2 rulers per pivot), then realize coordinates | EXPLORING |

Statuses per Section 4: `EXPLORING` `PROMISING` `BLOCKED` `FALSIFIED` `MERGED`
`VERIFIED` `CHAMPION`. Per Section 5, `FALSIFIED` requires a counterexample, an
impossibility theorem, a contradiction, or exhaustive elimination of a precisely
defined finite class — never poor performance.

## Standing constraints inherited from the project

- Never write "no larger construction exists"; only "we found no larger
  construction in the sources/searches examined".
- TIMEOUT ≠ INFEAS. Scoped ≠ global.
- Do not stage or modify the concurrent Cursor session's files
  (`long_horizon_run_*`). Round 3 writes only under `ROUND3_TOURNAMENT/`.
- `ortools` only in `.venv_solver`, never the global Anaconda env.
- Do not modify `tests/test_orbit_defect_search.py`.

## Prediction on record (Section 20 discipline)

Before Wave 1 launches, the orchestrator predicts that a **fully isolated**
campaign per unamended Section 2 would land at n=100 **137 ± 3**. Recorded now so
it can be settled against outcome rather than argued afterwards.
