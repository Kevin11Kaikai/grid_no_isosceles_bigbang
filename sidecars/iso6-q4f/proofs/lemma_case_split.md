# Lemma 2 — support-size case split

**Statement.** Let `S` be Q4-feasible in `{0,...,n-1}^2`, and write
`U_col, U_row, U_dia, U_ant` for the occupied columns, rows, main diagonals `x-y`,
and anti-diagonals `x+y`. For every `ε > 0`:

1. If any one of the four supports has size `≤ n^{1-ε}`, then `|S| ≤ n^{2-ε}`.
2. If `|S| > n^{2-ε}`, then all four supports are `> n^{1-ε}`, and the rectangle
   density `δ := |S| / (|U_col| |U_row|)` satisfies `δ > n^{-ε}`.

## Point 1

Each occupied column contains at most `n` points of `S`, so `|S| ≤ n |U_col|`.
The same holds for rows. Each main diagonal contains at most `n` grid points of
`G_n`, so `|S| ≤ n |U_dia|`; likewise `|S| ≤ n |U_ant|`.

Therefore `|S| ≤ n · min(|U_col|, |U_row|, |U_dia|, |U_ant|)`.
If the minimum is `≤ n^{1-ε}`, then `|S| ≤ n^{2-ε}`.

## Point 2

Contrapositive of point 1 gives the support lower bounds.
For density: `|U_col| ≤ n` and `|U_row| ≤ n`, so

```
δ = |S| / (|U_col| |U_row|)  ≥  |S| / n^2  >  n^{-ε}.
```

(If one wants a lower bound in terms of the supports themselves: the dangerous
regime `|U_col|, |U_row| > n^{1-ε}` only makes the denominator smaller than `n^2`
when the supports are not full, which *increases* `δ`. The weakest lower bound
on `δ` in the dangerous regime is still `δ > n^{-ε}`.)

## Corollary (sparse rectangle)

If `δ ≤ n^{-ε}`, then `|S| = δ |U_col| |U_row| ≤ n^{-ε} n^2 = n^{2-ε}`.

Together with lemma 1, the only remaining obstacle to `Q4(n) = O(n^{2-ε})` is a
Q4-feasible set with `δ > n^{-ε}` that is *not* a full product.

## What this does not prove

It does not bound the dense partial-filling branch. Axis-only analysis of a
large rectangle is B3 (`B×B` has `δ = 1` on a `n^{1-o(1)} × n^{1-o(1)}`
rectangle and satisfies constraints 1–2). Diagonals are required; that is lemma 3.
