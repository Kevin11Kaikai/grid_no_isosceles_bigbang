# `S*` after the campaign split — heavy vertices

Lane: sidecar only. Do not copy into `iso6/` until a full `ε` is closed.

**Status.** The old triple (`ρ, t_max, μ` all `> n^{1-ε}`) is closed. `S*` is
`O(n^{2-ε})` unless both colour classes of the `(d,δ)` graph have more than
`n^{1-ε}` heavy vertices. `S'` can itself be Case A, so peeling is not “one
fold then B′”. `Q4(n)=O(n^{2-ε})` is **not proved**.

Fix `ε = 1/4` and write `θ = n^{1-ε}`. Fold `S*` at a maximiser `a*` as in
[`lemma3_caseA.md`](lemma3_caseA.md). Each pair of `S*` on diagonal `d` is
`{a*±δ}` for a positive `δ`. This defines a bipartite incidence graph

```
T  ⊆  D* × Δ,     |E(T)| = |S*|/2,
t_d = deg(d),     k_δ = deg(δ),
t_max = max t_d,  μ = max k_δ.
```

A diagonal of the grid has at most `n` points, so `2 t_d ≤ n` and `t_d ≤ n/2`.
There are at most `2n-1` diagonals. Positive `δ = |α-a*|` run through at
most `2n-2` values. Each `k_δ ≤ |D*| ≤ 2n-1`.

```
D_h  =  { d ∈ D* : t_d > θ },
Δ_h  =  { δ ∈ Δ  : k_δ > θ }.
```

## Theorem (few heavy diagonals or few popular deltas)

If `min(|D_h|, |Δ_h|) ≤ θ`, then `|S*| ≤ 8 n^{2-ε}`.

**Proof.** Split the edges of `T` by the `D*`-side:

```
|E|  =  Σ_{d ∈ D_h} t_d  +  Σ_{d ∉ D_h} t_d
     ≤  |D_h| · (n/2)  +  (2n-1) · θ.
```

If `|D_h| ≤ θ` this is at most `θ n/2 + 2n θ = (5/2) n^{2-ε}`, hence
`|S*| = 2|E| ≤ 5 n^{2-ε}`.

Split instead by the `Δ`-side:

```
|E|  =  Σ_{δ ∈ Δ_h} k_δ  +  Σ_{δ ∉ Δ_h} k_δ
     ≤  |Δ_h| · (2n-1)  +  (2n) · θ.
```

If `|Δ_h| ≤ θ` this is at most `θ(2n-1) + 2n θ ≤ 4 n^{2-ε}`, hence
`|S*| ≤ 8 n^{2-ε}`.

## Corollary (old triple is empty of danger)

The three-way corollary of [`lemma3_campaign.md`](lemma3_campaign.md) left only

```
ρ > θ,   t_max > θ,   μ > θ.
```

That forces `|D_h| ≥ 1` and `|Δ_h| ≥ 1`, not `|D_h| > θ` or `|Δ_h| > θ`.
A single heavy diagonal (`|D_h| = 1 ≤ θ` for `n ≥ 1`) is covered by the
theorem, as is a single popular `δ`. In particular a plus-shaped `T`
(one heavy row, one heavy column, plus a matching for a long grid-row) has
`|S*| = O(n^{2-ε})`. The `n=7` frame has `t_d = 1` for every `d`, so
`D_h = Δ_h = ∅`.

Forced-pair sets through `n=243` have `t_max ≤ 2` and `μ ≤ 4`, hence
`D_h = Δ_h = ∅` (`a1_dh.py`).

## Remaining GAP on `S*`

Both

```
|D_h| > θ    and    |Δ_h| > θ
```

at once: more than `n^{1-ε}` diagonals each carry more than `n^{1-ε}` nested
pairs, and more than `n^{1-ε}` deltas are each used on more than `n^{1-ε}`
diagonals. Harmonic counting `|S*| ≤ 2n μ` is then allowed to be quadratic.
Complete `(d,δ)` bicliques with disjoint differences cannot live here
(`|S*| ≤ n`, so `k t ≤ n/2`, which forbids `k, t > n^{3/4}`). Difference-overlap
bicliques of this size were not found (`a1_biclique.py`, `kt ≈ n/3`). That is
not a proof the core is empty.

Kővári–Sós–Turán still does not apply: `K_{2,3}` is feasible (`a1_k23b.py`)
and `K_{3,3}` is feasible (`a1_k33.py`, `n=32`, `Δ={1,5,13}`, three diagonals,
18 points of `S*`).

## Theorem B″ (small kill-set)

The Case B counting is `|S| ≤ |U_dia| + R |K| ≤ (2n-1)(1+|K|)`. If
`|K| ≤ n^{1-ε}` then `|S| = O(n^{2-ε})`. Since `K ∩ U_ant = ∅` and
`|K| + |U_ant| ≤ 2n-1`, this is the dual of lemma 2 on `|U_ant|`: the
dangerous window is `n^{1-ε} < |U_ant| < 2n - n^{1-ε}`.

The same split, applied to the whole set rather than `S*`, is
[`lemma3_heavy.md`](lemma3_heavy.md). That version absorbs peeling.

## `S'` is not automatically B′

Subsets are Q4-feasible, so B′ would close `S'` if `R' ≤ θ`. That implication
is **false as a theorem about all Case A remainders**. Script `sprime_thin.py`
places just `θ+2` pairs at `a*`, then a second matching at another centre, then
fills. At `n=128`, `R' = 39 > 38.1`. At `n=243`, `R' = 63 > 61.5`, with
`|S'| = 235` and `|S*| = 288`. Two Case A matching-layers coexist. Forced-pair
examples had `R' ≤ 2` only because they maximised the first matching.

Peeling therefore cannot be “one fold, then B′”. Disjoint A3 layers (all
`t_d = 1`) use disjoint `D*` per centre and at most `2n/θ = 2 n^{ε}` such
centres, totalling `|S*|`-sum `O(n)` from those layers; that is compatible
with the campaign bound and with the two-matching examples. Stacking many
Type-II layers each of size `Θ(n^{2-ε})` is **not** controlled and would
cancel the saving.

## What this does not prove

- Not `|S*| = O(n^{2-ε})` in the double-heavy core.
- Not `|S'| = O(n^{2-ε})`.
- Not `Q4(n) = O(n^{2-ε})`.
