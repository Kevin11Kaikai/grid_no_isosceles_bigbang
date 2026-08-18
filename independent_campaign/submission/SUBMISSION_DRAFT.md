# Submission drafts

Three drafts, in descending order of how defensible they are. Read §0 first — it changes
what can honestly be sent, and it retires the draft that was here before.

---

## 0. What the prior-art check established

`C(12) = 20` **is already known.** Charton–Ellenberg–Wagner–Williamson, *PatternBoost*
([arXiv:2411.00566](https://arxiv.org/abs/2411.00566), Oct 2024), §"No isosceles triangles":

> "For `n` up to `≈ 32`, SAT solvers can find the best constructions **and prove their
> optimality**."

Their figure *"Plotting the computed values"* plots every value they computed. `f(12) = 20`.

So **nothing may be submitted anywhere as a new value.** What is genuinely missing is
different and smaller: the sequence exists in the literature only as *dots on a scatter plot*.
Nobody has written it down.

**Verified absent from the OEIS.** A search on `1, 2, 4, 6, 7, 9, 10, 13, 16, 18, 18`
returns no match, and so does the 9-term prefix. The nearest neighbour, **A271914**, is a
*different problem* — it counts isosceles triangles of **nonzero area**, i.e. it permits
collinear triples, so its diagonal is `T(n,n) = 2n − 2` and diverges from `C(n)` from `n = 5`
onward (`T(5,5) = 8` vs `C(5) = 7`). **A271906** is the *right-isosceles* variant. Neither is
this sequence.

That gap — a known sequence with no machine-readable record — is the whole of what is left to
contribute, and Draft A fills it.

---

## Draft A — OEIS new-sequence submission ★ recommended

Submit at <https://oeis.org/wiki/Contributing_a_new_sequence> (requires a free account; new
submissions are reviewed by editors, usually within days to weeks).

> **%N** `a(n)` is the maximum size of a subset of the `n × n` grid `{1..n}²` containing no
> three distinct points `a, b, c` with `|a−b| = |b−c|`; that is, containing no isosceles
> triangle, **including degenerate (collinear) ones**.
>
> **%S** `1, 2, 4, 6, 7, 9, 10, 13, 16, 18, 18, 20, 22`
>
> **%O** `1,1`
>
> **%C** Collinear triples count as (flat) isosceles triangles. Consequently the trace of an
> optimal set on any line is a 3-term-AP-free set, and `a(n)` for a `1 × n` grid is
> `A003002`-adjacent (the Salem–Spencer maximum `r_3(n)`); this is the sharpest available test
> that degenerate triples are handled correctly.
>
> **%C** Not monotone in the strict sense: `a(10) = a(11) = 18`.
>
> **%C** Distinct from A271914, which requires the isosceles triangle to have nonzero area
> (i.e. permits collinear triples) and whose main diagonal is `2n − 2`; the two sequences agree
> for `n ≤ 4` and differ from `n = 5` on. Distinct also from A271906, the right-isosceles
> variant.
>
> **%C** Charton, Ellenberg, Wagner and Williamson report that SAT solvers determine `a(n)`
> and prove optimality for all `n` up to about 32, and plot the resulting values; the printed
> values there are `a(4..10) = 6, 7, 9, 10, 13, 16, 18`, `a(16) = 28`, `a(27) = 48`,
> `a(32) = 56`. The intermediate values appear in their paper only as points of a figure. The
> terms `a(11)`, `a(12)`, `a(13)` of the DATA line above were not transcribed from that figure
> but recomputed independently; the remaining plotted values are deliberately omitted, pending
> a b-file from those authors.
>
> **%C** Asymptotically `n/sqrt(log n) << a(n) << exp(-c*(log n)^(1/9)) * n^2`; even
> `a(n) = O(n^1.99)` is open. Proving the upper bound uses the horizontal-line 3-AP structure
> together with bounds on 3-AP-free sets.
>
> **%H** F. Charton, J. S. Ellenberg, A. Z. Wagner, G. Williamson, *PatternBoost:
> Constructions in Mathematics with a Little Help from AI*,
> [arXiv:2411.00566](https://arxiv.org/abs/2411.00566), 2024. (Values for `n <= 32`, by SAT,
> with proved optimality.)
>
> **%H** B. Georgiev, J. Gómez-Serrano, T. Tao, A. Z. Wagner, *Mathematical exploration and
> discovery at scale*, [arXiv:2511.02864](https://arxiv.org/abs/2511.02864), 2025, §6.39.
> (Problem 59 of the AlphaEvolve Repository of Problems; constructions of size 112 in `[64]²`
> and 164 in `[100]²`.)
>
> **%e** For `n = 12`, one optimal set of 20 points is
> `(0,0) (0,1) (0,7) (0,8) (1,2) (1,3) (1,6) (3,0) (3,11) (4,0) (4,11) (5,1) (5,10) (8,10)`
> `(9,10) (10,6) (10,11) (11,7) (11,8) (11,11)` (coordinates `0..11`).
>
> **%Y** Cf. A271914 (nonzero-area isosceles), A271906 (right isosceles), A003002
> (3-AP-free subsets of `{1..n}`).

**Note to the editor, to send with it:**

> The values `a(1..13)` were independently recomputed for this submission by exhaustive
> branch-and-bound, in two implementations sharing no cell order, no validity oracle and no
> bound, neither using any symmetry argument — 45 922 791 007 and 32 795 784 946 search nodes
> at `n = 12`, both terminating from `best = 20` without finding a 21-point set, and both
> calibrated against `r_3(n)` on `1 × n` grids for `n = 1..24`. They agree with the values of
> arXiv:2411.00566 at every point. Sources, logs and a definition-only verifier are attached.
>
> I have deliberately stopped the DATA line at `n = 13`, the largest value I verified myself
> (`a(13) = 22`: an explicit witness checked from the definition, plus an exhaustive
> symmetry-free run from `best = 22`, 596 185 011 999 nodes, finding no 23-point set).
> `a(13)` is one of the values arXiv:2411.00566 plots but does not print, so this is also an
> independent confirmation of that figure.
> The authors of arXiv:2411.00566 hold exact values through `n ≈ 32`; the correct next step is
> for those to be contributed as a b-file by them, and I would rather leave that to them than
> transcribe numbers off their figure.

**Before sending:** email Adam Zsolt Wagner and Jordan Ellenberg, ask for their exact table
through `n = 32`, and offer them the OEIS authorship. That is both the courteous move and the
one that produces the better sequence entry. If they decline or don't reply, submit the
13-term version above as it stands.

---

## Draft B — issue on the AlphaEvolve Repository of Problems

This problem is **Problem 59** there
(<https://google-deepmind.github.io/alphaevolve_repository_of_problems/problems/59.html>),
= §6.39 of arXiv:2511.02864. Issues are open; a Google CLA is required for *pull requests*
but not for issues.

> **Title:** Problem 59 (no isosceles triangles): the exact small values have no
> machine-readable record
>
> The problem page and §6.39 give the asymptotics and the large-`n` constructions (112 in
> `[64]²`, 164 in `[100]²`) but no small values. The exact values are known — arXiv:2411.00566
> determines them by SAT with proved optimality for all `n ≲ 32` — yet the intermediate ones
> exist only as points in that paper's Figure "Plotting the computed values", and the sequence
> is not in the OEIS.
>
> Two small things that might be worth having on the problem page:
>
> 1. **The values, printed.** `C(1..13) = 1, 2, 4, 6, 7, 9, 10, 13, 16, 18, 18, 20, 22`, and from
>    arXiv:2411.00566: `C(16) = 28`, `C(27) = 48`, `C(32) = 56`. Note `C(10) = C(11) = 18`.
> 2. **An independent check of the small end.** I re-derived `C(1..13)` by exhaustive
>    branch-and-bound in two implementations sharing no cell order, no validity oracle and no
>    bound, neither using any symmetry argument (45 922 791 007 and 32 795 784 946 nodes at
>    `n = 12`, both from `best = 20`, neither finding a 21-point set), calibrated against
>    `r_3(n)` on `1 × n` grids. Full agreement with the SAT values. Sources and logs attached
>    if useful — an independent-method confirmation of a SAT result seemed worth offering,
>    since the two share no failure mode.
>
> No new result is claimed. I initially mistook `C(12) = 20` for an open value precisely
> because it is only ever plotted, which is what prompted this issue.

**Honest assessment of Draft B:** low value. The maintainers already have these numbers.
Send it only if you want the values on the page for the next person.

---

## Draft C — comment on erdosproblems.com #657

`#657` (<https://www.erdosproblems.com/657>) is the *continuous* relative: isosceles-free
`n`-point sets in `R²` and how many distinct distances they force. Its bound
`f(n) ≥ 2^{c(log n)^{1/9}}` is the same Kelley–Meka/Bloom–Sisask input that gives the
`e^{-c(log n)^{1/9}} n²` upper bound for the grid problem. The page carries a
"Related OEIS sequences: **Possible**" field and invites comments.

> The grid analogue of this problem — `C(n)`, the largest subset of `[n]²` with no
> (possibly flat) isosceles triangle — shares this problem's upper-bound mechanism, via
> 3-AP-freeness on lines. Its exact small values are known by SAT for `n ≲ 32`
> (arXiv:2411.00566) but are not in the OEIS; `C(1..13) = 1, 2, 4, 6, 7, 9, 10, 13, 16, 18,
> 18, 20, 22`. It is Problem 59 of the AlphaEvolve Repository of Problems (§6.39 of
> arXiv:2511.02864), where AlphaEvolve found 112 points in `[64]²`. Offered only as a
> cross-reference for the "Related OEIS sequences" field.

**Honest assessment of Draft C:** send only *after* the OEIS sequence exists, so the comment
has an A-number to point at. Until then it is a comment with nothing to link.

---

## What is not being submitted, and why

- **No claim on `C(12) = 20`.** Known. See §0 and `../ledgers/failure_ledger.md` F7.
- **No claim on the asymptotics.** The campaign reached nothing there, and its `Z[i]`
  formulation, tensor lemma and Behrend-digit obstruction are all in arXiv:2607.22828.
- **Barrier B6** (`the degree-k relaxation admits n^{2−2/(k+1)−o(1)}`, so any argument robust
  at degree 2 is capped at `n^{4/3}`) is the one item the audit could not locate in the
  literature. Its proof is a routine alteration argument against `Σ_{r≤R} r_2(r)^j`, so it is
  most likely folklore, and it is a statement about relaxations rather than about `C(n)`. If
  anything here is ever worth a note, it is this — but it needs a real literature search
  against the repeated-distance and Sidon-set literature first, not another audit that only
  reads text.
