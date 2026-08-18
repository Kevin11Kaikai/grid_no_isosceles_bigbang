# Cover note — `C(12) = 20`, Erdős Problem 6.59

Suggested destination: the entry for Problem 6.59 on erdosproblems.com (small-value data),
not a paper. The result is a computation, not a theorem.

---

**Subject:** Problem 6.59 (no-isosceles subsets of `[n]²`) — `C(12) = 20`, exhaustive

The entry lists `20 ≤ C(12) ≤ 23`. An exhaustive search closes this at the lower end:

> **`C(12) = 20`.**

Attached is a certificate package: the definition used, four explicit 20-point witnesses,
two independent exhaustive solvers, an independent definition-only verifier, run logs, and
build/run instructions. Reproduction takes about two minutes on 20 threads for the first
solver and 23 minutes for the second.

Points a referee will want first:

1. **The upper bound does not use any symmetry argument.** The decisive run disables
   symmetry reduction entirely and starts from `best = 20`, so it abandons a branch only
   when that branch provably cannot reach 21 points. It terminated normally without ever
   raising `best`.
2. **Its node count is deterministic** (`best` is pinned, so pruning does not depend on
   thread scheduling) and reproduced to the digit — 45 922 791 007 — across runs made on
   different occasions.
3. **Calibration.** The same solver re-derives `C(1..11) = 1,2,4,6,7,9,10,13,16,18,18` with
   no disagreement, and on `1 × n` grids reproduces the Salem–Spencer sequence `r_3(n)`
   exactly for `n = 1..24`. The latter is the sharp test that degenerate (collinear)
   triples are being handled, since a `1 × n` grid has nothing but degenerate triples.
4. **Two independent implementations both establish the upper bound at `n = 12`**, with
   visibly different search trees — different cell order, different validity oracle,
   different bound, no symmetry in either. Method A explores 45 922 791 007 nodes,
   Method B 32 795 784 946; both terminate normally from `best = 20` without finding a
   21-point set.

Known limitation, stated plainly: both exhaustive solvers are branch-and-bound programs
written by the same author, so a shared *conceptual* error is not excluded by their
agreement — only a shared coding error is. The `r_3` calibration is the intended guard
against the one conceptual error that matters here, mishandling degenerate triples, and
it passes.

I make no claim of novelty for anything else in the package, and none for the asymptotics:
this is a single small value and it bears on no conjecture about the growth of `C(n)`.
