# Proof Obligation Ledger

Per route: Proved / Computational / Conjectural / Hardest remaining lemma / Why simpler.

No hidden proof debt. A route whose hardest remaining lemma is theorem-strength with no
difficulty reduction is marked BLOCKED, never "essentially complete".

---

## SQ — square-corner relaxation (the only live route)

**Proved.** `C(n) ≤ Q_SQ(n)`. The invariant-equation form `v = i·u + (1-i)·b` over `Z[i]`,
and that corners admit no analogous single relation. The difference-set / `i`-orbit form.
Circle rigidity. Theorem 4 (no digit-sphere construction is square-corner-free). The tensor
lemma `Q_SQ(n) = Ω(n^{log g(q)/log q})`. The product lemma `g(p) ≥ m_A(p)m_B(p)` for
`p ≡ 1 mod 4`. `Q_SQ(n) = Ω(n^{1.1562})`. `Q_SQ(n) = o(n^2)` (via corner-freeness).

*Added post-closeout* (`proofs/ideal_uniformity.md`): **Theorem A**, `Q_SQ(n) ≤ g(q)` for
every `q ≥ 2n` — the converse of the tensor lemma, so upper bounds on the torus now
transfer back to the box. **Theorem B**, ideal uniformity: `G(I)` depends only on the
`Z[i]`-module `Z[i]/I`, and `m(p) = G((π))`, `g(q) = G((q))` are one function. **Lemma C**,
the half-orbit form and `m(p) ≤ (p+1)/2`. Consequence of A: `Q_SQ(n) = n^{2λ+o(1)}` for
`λ = limsup_I log G(I)/log N(I)`, so **the target is equivalent to `λ < 1`** and all
geometry is discharged into one real number. `λ ≥ 0.5781` rigorous; no upper bound `< 1`.

**Evidence downgrade (Corollary B2).** The closeout credited route SQ with four independent
survival instruments and treated the `m(p)`/`g(q)` agreement as two-directional
corroboration. Theorem B proves it is one problem in two parameterisations (identical values
26 vs 26, 56 vs 56 at matched group size). **Independent instruments: two, not four** —
Theorem 4 (a proof) and the structured-construction hunt. The `m(p)` ladder is struck.

**Falsified post-closeout (F5).** The finite-margin `(1+i)`-tower recurrence
`G(I·(1+i)) ≤ c·G(I)`, `c < 2`, which would have proved the target from one constant: the
exact ratio **equals 2** at `j = 1→2` and `j = 3→4` (`G((1+i)^j) = 1,2,2,4,6,9`). The
asymptotic form is `λ < 1`, i.e. the target restated — §8 verdict: restatement, not
reduction. The supporting numerics were separately retired as uninformative (F4): the same
solver reads ratio `1.5` on 3-APs, a relation Behrend forces to die.

**Computational.** `g(q)` exact for `q ≤ 11`, symmetry-off cross-checked, witnesses
independently re-verified. `m(p)` exact for `p ≤ 41`, greedy to `p = 8009`. Torus lower
bounds to `q = 64`. Soundness on all 80 maximum isosceles-free sets, `n ≤ 6`.

**Conjectural.** `Q_SQ(n) = n^{1+o(1)}`, or merely `Q_SQ(n) = O(n^{2-ε})`. Unproved.
`m(p) = √p · polylog`. Unproved — only that search cannot beat `p^{0.547}`.

**Hardest remaining lemma.** An upper bound `Q_SQ(n) = O(n^{2-ε})`. This is
theorem-strength: it is a power saving for a Roth-type problem, and the density-increment
machinery does not deliver power savings. **No difficulty reduction is claimed for it, so
the route is not "essentially complete" — it is one honest step from the start, and that
step is the whole problem.**

**Why it is nevertheless a genuine reduction.** All geometry is discharged into a single
translation-invariant three-variable equation; the object is exactly self-similar, so
bounding the finite quantity `g(q)` suffices; and the construction method that caps every
other mechanism at `n^{2-o(1)}` is *proved* not to apply. That is a reduction in difficulty,
not a restatement. It is not progress toward a bound.

**What would kill it.** Any square-corner-free family of size `n^{2-o(1)}`. Four
independent attempts failed, one of them by proof (Theorem 4). If found, the route dies
exactly as Q4 did and B6/B7/B8 leave essentially nothing standing.

## R0 / line-kill — `BLOCKED`

Hardest remaining lemma: extract multi-direction content non-additively. Obstruction B4′ is
rigorous and applies to every bounded direction set. No difficulty reduction available.

## Q4 — `FALSIFIED`. E — refuted as framed (Z1). A, B, F, D, G — never ran.
