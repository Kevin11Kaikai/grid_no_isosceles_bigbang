# Independent campaign record — branch `campaign-record-6.59`

An independently-run search campaign on Problem 6.59, conducted under hard isolation (no
literature access, no access to this repository) and then audited against the literature
after the fact. Everything it produced is in `independent_campaign/`.

**Nothing on `master` is modified by this branch.** All content is added under
`independent_campaign/`, plus this file.

---

## Headline, stated plainly

**The campaign did not move the problem, and it produced nothing new.** The target it
pursued — `C(n) = O(n^{2−ε})` for a fixed `ε > 0` — was not reached, and the prior-art audit
found that its principal mathematical results had all been obtained before. The known bounds
are where they were: `n/√(log n) ≲ C(n) ≲ e^{−c(log n)^{1/9}} n²`.

**Correction, 2026-08-18.** An earlier version of this file presented `C(12) = 20` as new.
It is not: PatternBoost ([arXiv:2411.00566](https://arxiv.org/abs/2411.00566)) proved
optimality by SAT for all `n ≲ 32` in 2024 and plots `f(12) = 20`. The audit had missed it by
searching printed numbers rather than reading the paper's figure. See
`independent_campaign/ledgers/failure_ledger.md` **F7**. What is below is corrected
accordingly; nothing in this branch is a novelty claim any more.

What remains: one independent reproduction that is stronger than what this repository's own
logs contain, and one registry entry that gains a correction.

---

## Delta 1 — `C(12) = 20`, exhaustively, with the upper bound proved

Not new to the literature (see the correction above); new relative to *this repository*.
`logs/cpsat_maximize_n12_seed1.json` on `master` records `best_legal_size: 19` with round 2
ending `FEASIBLE`, not `OPTIMAL` — a construction, one short of optimal, without a proof of
optimality.

This branch supplies both halves, by a method independent of both master's CP-SAT run and
PatternBoost's SAT computation:

- **`C(12) ≥ 20`** — four mutually distinct 20-point witnesses, each checked from the
  definition by a verifier that enumerates all 1140 triples and all three apex choices.
- **`C(12) ≤ 20`** — no 21-point set exists, established **twice**, by two exhaustive
  branch-and-bound implementations sharing no cell order, no validity oracle and no bound
  (45 922 791 007 and 32 795 784 946 nodes). **Neither uses any symmetry argument**: both
  decisive runs start from `best = 20` and abandon a branch only when it provably cannot
  reach 21 points.

The decisive run's node count is deterministic (`best` is pinned, so pruning does not
depend on thread scheduling) and reproduced to the digit across separate occasions.
Calibration: `C(1..11) = 1,2,4,6,7,9,10,13,16,18,18` re-derived with no disagreement, and
`C(1,n) = r_3(n)` reproduced against the Salem–Spencer sequence for `n = 1..24` with zero
mismatches — the sharp test that degenerate (collinear) triples are handled, since a
`1 × n` grid contains nothing else.

Self-contained package with sources, logs and build instructions:
`independent_campaign/submission/`.

## Delta 2 — a correction to `record_registry.md` entry 1 (Károlyi–Solymosi)

The registry rules out arXiv:2607.22828 with the reason that isosceles-right-triangle-free
sets are *"a DIFFERENT, strictly weaker problem … not comparable to"* `C(n)`.

**The conclusion is right — nothing there supersedes the `C(n)` record — but the stated
reason is not.** Writing `F(n)` for the isosceles-right-triangle-free maximum:

- The two problems *are* comparable, in one direction: isosceles-free implies
  IRT-free, so **`C(n) ≤ F(n)`**. Every upper bound on `F` is therefore an upper bound
  on `C`.
- Their `Ω(n^{1.318})` carries no information about `C`, but not because the problems are
  incomparable — because it is a **lower** bound on the **larger** quantity, and lower
  bounds do not propagate downward.
- The reason `F` is useless as a route to `C` is sharper and worth recording: the best
  known upper bound on `F` is Bloom's `O(n²/(log n)^{1−ε})`, and
  `e^{−c(log n)^{1/9}}` decays faster than every power of `log n`. So passing to `F`
  yields `C(n) = O(n²/(log n)^{1−ε})`, **weaker than the baseline `n·r_3(n)`**. The
  relaxation is *lossy*, not incomparable.

This campaign independently rediscovered `F(n)` as a relaxation, developed it for most of
its budget as its sole surviving route, and only the audit revealed it to be lossy. The
derivation is in `independent_campaign/docs/prior_art_audit.md` §1a.

---

## What the audit found was already known

Recorded so this branch is not mistaken for a claim of novelty. All of the following were
derived independently here and are **not new** — they appear in arXiv:2607.22828
(Károlyi–Solymosi):

| campaign result | status |
|---|---|
| the exact value `C(12) = 20` | plotted in arXiv:2411.00566, proved optimal there by SAT |
| the square-corner / `Z[i]` single-equation formulation of IRT-freeness | their Observation 2.1 |
| the carry-free tensor / self-similarity lemma | the mechanism of their `Ω(n^{1.318})` construction |
| Theorem 4, the Behrend digit-sphere obstruction | their Remark 2.5, in different clothing |
| `Q_SQ(n) = Ω(n^{1.1562})` | superseded by their `Ω(n^{1.318})` |

## What is worth keeping anyway

The negative record held up against the literature. In particular
`independent_campaign/ledgers/failure_ledger.md` documents six falsifications and process
failures with their causes — including one bug class that recurred three times after being
"learned", each time producing *plausible wrong numbers* rather than a crash, and once
briefly appearing to refute a correct lemma. Every instance was caught the same way:
re-testing against the complete definition with a checker sharing no code, tables or data
structures.

`independent_campaign/ARCHIVE.md` is the index. Read
`independent_campaign/ledgers/failure_ledger.md` **F7** first — it is the costliest failure
in the record and the cheapest to have avoided — then
`independent_campaign/docs/prior_art_audit.md`.
