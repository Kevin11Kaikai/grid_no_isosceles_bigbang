# Cover note — independent reproduction of `C(12) = 20`

**This is not a new result, and it is not a submission.** It was assembled as one, on a
prior-art verdict that turned out to be wrong. The correction is recorded here rather than
deleted, because the mistake is the more useful half.

---

## What was claimed, and why it was wrong

The package originally announced `C(12) = 20` as closing an open bracket `20 ≤ C(12) ≤ 23`.

The value was already known. Charton–Ellenberg–Wagner–Williamson, *PatternBoost*
([arXiv:2411.00566](https://arxiv.org/abs/2411.00566), Oct 2024), §"No isosceles triangles":

> "For `n` up to `≈ 32`, SAT solvers can find the best constructions **and prove their
> optimality**."

Their figure "Plotting the computed values" carries every value they computed. Read off the
plot: `f(4..18) = 6, 7, 9, 10, 13, 16, 18, 18, 20, 22, 23, 25, 28, 30, 32`, then
`f(21) = 36`, `f(23) = 40`, `f(25) = 44`, `f(27) = 48`, `f(32) = 56`. **`f(12) = 20`**, and
the plotted sequence agrees with this campaign's at every point the campaign computed.

The audit that cleared this result searched for the printed number. PatternBoost typesets
only `f(4..10)`, `f(16)`, `f(27)`, `f(32)` as captions; `f(11)…f(15)` exist in that paper
only as dots. So every text search came back empty, and the sentence granting optimality for
all `n ≤ 32` was not read as the claim it plainly is. Full account:
`../ledgers/failure_ledger.md` **F7**.

The refutation was also available with no network access at all. The sealed baseline handed
the campaign `C(16) = 28`, `C(27) = 48`, `C(32) = 56` as exact values. Only a source that had
computed exact values at `n = 16, 27, 32` could supply those, and no such source skips
`n = 12`.

## What the package still is

An exhaustive re-derivation of `C(12) = 20` by a method sharing nothing with SAT:

1. **No symmetry argument anywhere in the upper bound.** The decisive run disables symmetry
   reduction entirely and starts from `best = 20`, abandoning a branch only when it provably
   cannot reach 21 points. It terminated normally without ever raising `best`.
2. **Deterministic and reproduced to the digit** — 45 922 791 007 nodes, `best` pinned so
   pruning cannot depend on thread scheduling, identical across runs on separate occasions.
3. **Two independent implementations**, different cell order, different validity oracle,
   different bound, neither using symmetry: 45 922 791 007 and 32 795 784 946 nodes, both
   terminating from `best = 20` with no 21-point set.
4. **Calibrated** against `C(1..11) = 1,2,4,6,7,9,10,13,16,18,18` with no disagreement, and
   against `r_3(n)` on `1 × n` grids for `n = 1..24` — the sharp test that degenerate
   (collinear) triples are handled, since a `1 × n` grid contains nothing else.

Independent method agreement with a SAT result is worth having; it is not a contribution.
Known limitation, unchanged: both solvers are branch-and-bound programs by the same author,
so a shared *conceptual* error is not excluded by their agreement — only a shared coding
error is. The `r_3` calibration is the guard against the one conceptual error that matters,
and it passes.

## Where a real contribution would still fit

The sequence itself is absent from the OEIS. A search on
`1, 2, 4, 6, 7, 9, 10, 13, 16, 18, 18` returns nothing (the nearby A271914 is a different
problem — it requires nonzero area, i.e. it permits collinear triples). PatternBoost's values
live in a scatter plot; the AlphaEvolve repository records only large-`n` constructions. So
the machine-readable sequence does not exist anywhere, and creating it — attributed to
PatternBoost for `n ≤ 32`, with this package as independent verification for `n ≤ 12` — is
a genuine if modest gap to fill. That, and not a novelty claim, is the defensible submission.
