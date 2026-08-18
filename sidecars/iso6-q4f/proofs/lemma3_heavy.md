# Global heavy lines — peeling is not a separate gap

Lane: sidecar only. Do not copy into `iso6/` until a full `ε` is closed.

**Status.** Any Q4-feasible set (no fold) is `O(n^{2-ε})` unless both
diagonal families have many heavy lines, and those heavy supports are
themselves large. Light Case A layers, including stacked A3 matchings, are
covered. `Q4(n)=O(n^{2-ε})` is **not proved**.

Fix `ε = 1/4` and `θ = n^{1-ε}`. For `S ⊆ G_n` write `m_d = |S ∩ diagonal_d|`
and `m^α = |S ∩ anti_α|`. A grid diagonal has at most `n` points, and there
are `2n-1` diagonals and `2n-1` anti-diagonals. Each pair `(d,α)` determines
at most one grid point. Set

```
H  =  { d : m_d > θ },     J  =  { α : m^α > θ }.
```

No Q4 hypothesis is used until the remaining GAP. The two mandatory examples
are covered: a single `r_3` diagonal has `|H| ≤ 1 ≤ θ` once it is heavy, and
`|J| = 0` (each of its points uses a distinct anti); the `n=7` frame has
`m_d ≤ 3 < 7^{3/4}` so `H = J = ∅`.

## Theorem (few heavy diagonals or few heavy antis)

If `min(|H|, |J|) ≤ θ`, then `|S| ≤ 3 n^{2-ε}`.

**Proof.** `|S| = Σ_d m_d ≤ |H| · n + (2n-1) · θ`. If `|H| ≤ θ` this is at
most `nθ + 2nθ = 3 n^{2-ε}`. The same count on anti-diagonals gives the
`|J| ≤ θ` half.

This includes every set in which every diagonal has `m_d ≤ θ` (then `H = ∅`),
in particular every A3 frame (`m_d = 2`) and every forced-pair example through
`n=243` (`t_max ≤ 2`). Folding and `S'` peeling are not needed on this branch.

## Theorem (core product)

Write `S_core` for the points of `S` that lie on some `d ∈ H` and on some
`α ∈ J`. Then

```
|S|  ≤  |S_core|  +  4 n^{2-ε}.
```

**Proof.** Points off `S_core` lie on a light diagonal or a light anti (or
both). Light diagonals contribute at most `(2n-1)θ`. Light antis contribute
at most `(2n-1)θ`. Those two pools may overlap; the sum still bounds the
complement of `S_core`.

Each point of `S_core` is a unique pair `(d,α) ∈ H × J`, so
`|S_core| ≤ |H| |J|`.

**Corollary.** If `|H| ≤ n^{1-ε/2}` and `|J| ≤ n^{1-ε/2}`, then
`|S_core| ≤ n^{2-ε}` and `|S| ≤ 5 n^{2-ε}`. For `ε = 1/4` the extra
threshold is `n^{7/8}`.

Together with the previous theorem: the only remaining configuration is

```
min(|H|, |J|)  >  n^{1-ε}     and     max(|H|, |J|)  >  n^{1-ε/2}.
```

A complete product `H × J` in `(d,α)`-coordinates is a product set in the
grid after an affine change, and lemma 1 forbids it from being Q4-feasible
at size larger than `2n-1`. The GAP is a *partial* filling of a large
`(d,α)` rectangle with 3-AP-free rows and 3-AP-free columns.

## What this does to the fold picture

[`lemma3_sstar.md`](lemma3_sstar.md) remains correct: it is the same split
applied to `S*` after a fold. The global split is strictly stronger, because
it never peels. A second Case A matching (`sprime_thin.py`) has `m_d = 2`
on the used diagonals, so `H = ∅` and the first theorem applies to the
whole set. Stacked Type-II layers with every `m_d ≤ θ` are likewise
covered. The only peeling that could still matter is a stack of layers
that *together* make many diagonals heavy; that is already the remaining
GAP above, not a layer-count problem.

## Axis copy

The same two theorems hold with rows and columns in place of diagonals and
antis (`R_h = {y : ρ(y) > θ}`, `C_h` dually). If `min(|R_h|, |C_h|) ≤ θ`,
or both are `≤ n^{7/8}`, then `|S| = O(n^{2-ε})` already. The remaining
GAP therefore also needs the axis pair to be thick; otherwise the first
theorems close the set.

## Why the remaining GAP is not filled

W.l.o.g. `|H| > n^{7/8}` and `|J| > n^{3/4}`. This configuration, if it
exists, has `|S| > |H| θ > n^{13/8}` and is a Q4-dies (superlinear). The
question is whether Q4 forbids it. The routes below do **not**.

1. **Disjoint midpoint sets.** `|H|(θ-1) > 2n` for large `n`, so the
   `M(A_d)` cannot be pairwise disjoint. They must share midpoints. That
   only recovers Case A (`R ≥ √n` by pigeon with `|K| ≤ 2n`), not
   `R = O(n^{3/4})`.
2. **`R |K|` interpolation.** `R |K| ≥ |H|(θ-1) > n^{13/8}`. Combined with
   `|S| ≤ 2n min(R,|K|)` this does *not* bound `min(R,|K|)`, because a
   lower bound on the product does not upper-bound the minimum. The worst
   case is `R` and `|K|` both `Θ(n)`, which is allowed and gives `|S| = O(n^2)`.
3. **`r_3` per line.** Each `A_d` is 3-AP-free, so `|S| ≤ |H| r_3(n) + 2n θ`.
   Behrend is `n^{1-o(1)}`, not `O(n^{1-ε})` for a fixed `ε`. This is B4.
4. **KST.** `K_{3,3}` is Q4-feasible. No forbidden complete bipartite graph
   of fixed size.
5. **Packing a complete `(d,α)` biclique.** Difference-disjoint products
   have `|S| ≤ n` and cannot enter the GAP. Difference-overlap plus
   `ρ + 2 t ≤ n` still allows `|H| ≈ n/2`, `|J| ≈ n/4`, product `n^2/8`.
   Packing does not kill a complete core.
6. **Column Cauchy–Schwarz.** Incidences `I > n^{13/8}` give average
   `|X_d ∩ X_{d'}| ≫ √n` for `d,d' ∈ H`. Two heavy diagonals sharing `√n`
   columns is Q4-feasible when the common `x`-set is 3-AP-free (it is,
   affinely). Structure, not a bound.
7. **Changing `ε`.** Smaller `ε` makes `θ` larger and the leftover thicker
   (`|H| > n^{1-ε/2}`). The bump moves; it does not vanish.

The GAP is inhabited. iso6 `proofs/q4_falsified.md` (read-only; not copied
here) gives a Q4-feasible four-fold intersection of 3-AP-free sets of size
`n^{2-o(1)}`. That set is exactly a thick partial filling of a `(d,α)`
rectangle. Sidecar search missed it. The upper-bound attempt on Q4 stops.

## What this does not prove

- Not `|S| = O(n^{2-ε})` when `|H| > n^{7/8}` and `|J| > n^{3/4}`.
- Not `Q4(n) = O(n^{2-ε})`.
- Not that the remaining core is empty.
