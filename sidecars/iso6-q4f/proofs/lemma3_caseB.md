# Lemma 3 Case B — small overlap implies `O(n^{3/2})`

**Statement.** Let `S` be Q4-feasible in `G_n = {0,...,n-1}^2`. Write
`r(a)` for the number of main diagonals `d` such that `a` is a pairwise
midpoint of the occupied anti-values on `d` (so `a ∈ K`, hence `a ∉ U_ant`
by constraint 3). If

```
R  :=  max_a r(a)  ≤  n^{1/2},
```

then `|S| ≤ (2n-1)(1 + n^{1/2}) = O(n^{3/2})`.

This is a complete proof. It does not use constraints 1, 2, or 4, except
insofar as Q4-feasibility already gives constraint 3.

## Counting

Let `m_d = |S ∩ diagonal_d|` and `U_dia = {d : m_d ≥ 1}`. There are
`2n-1` main diagonals (`x-y` runs through `{1-n,...,n-1}`), so `|U_dia| ≤ 2n-1`.

Anti-values of points on a fixed diagonal all have the same parity (because
`x+y = 2x-d`). Distinct pairs therefore have integer midpoints. Sorting the
anti-values `α_1 < ⋯ < α_m` on a diagonal with `m ≥ 2`, the consecutive
midpoints `(α_i+α_{i+1})/2` are strictly increasing, hence

```
|M(A_d)|  ≥  m_d - 1    for m_d ≥ 2,
```

and `|M(A_d)| = 0` for `m_d ≤ 1`. Summing over diagonals:

```
Σ_d |M(A_d)|  ≥  Σ_{m_d ≥ 2} (m_d - 1)  =  |S| - |U_dia|.
```

By definition `r(a) = #{d : a ∈ M(A_d)}` and `K = ∪_d M(A_d)`, so

```
Σ_{a ∈ K} r(a)  =  Σ_d |M(A_d)|  ≥  |S| - |U_dia|.
```

Constraint 3 says `K ∩ U_ant = ∅`. Possible anti-diagonal indices are
`{0,...,2n-2}` (`2n-1` values), therefore `|K| ≤ 2n-1`. Combined with
`r(a) ≤ R` on `K`:

```
|S| - |U_dia|  ≤  Σ r(a)  ≤  R · |K|  ≤  R (2n-1).
```

Hence `|S| ≤ |U_dia| + R(2n-1) ≤ (2n-1)(1+R)`.
Under `R ≤ n^{1/2}` this is `|S| ≤ (2n-1)(1+n^{1/2}) = O(n^{3/2})`.

## Compatibility with the two mandatory examples

- **Single 3-AP-free diagonal** of size `r_3(n)`. Only one diagonal has
  `m_d ≥ 2` (in fact only one is occupied). Each midpoint `a ∈ M(A_d)` is
  hit by that single diagonal, so `r(a) = 1 ≤ n^{1/2}` for `n ≥ 1`.
  The example lives in Case B. The bound `O(n^{3/2})` is far above `r_3(n)`.
- **Frame / large `r(a)`.** The `n=7` maximiser has `r(6) = 8 > √7 ≈ 2.65`.
  It is **not** in Case B; it is Case A. Case B does not claim to cover it.

## Campaign form

The same counting, with the threshold `R ≤ n^{1-ε}` instead of `n^{1/2}`,
gives `|S| = O(n^{2-ε})`. That is Theorem B′ in
[`lemma3_campaign.md`](lemma3_campaign.md). The `√n` form above is the
special case `ε = 1/2`, which is stronger on this branch and harder on Case A.

## What this does not prove

If some `r(a) > n^{1/2}`, the same counting only gives `|S| ≤ (2n-1)(1+R)`
with `R` possibly as large as `2n-1`, i.e. `O(n^2)`. That is Case A.
