# Lemma 1 — a Q4-feasible product has size at most `2n-1`

**Statement.** Let `A, B ⊆ {0,...,n-1}` be nonempty, and let `S = A × B`.
If `S` is Q4-feasible, then every main diagonal `x-y = d` contains at most one point of `S`, hence `|S| ≤ 2n-1`.
The same bound follows from anti-diagonals.

This is a proof, not a computation. Integer arithmetic only.

## Occupied anti-diagonals of a product

For `S = A × B` one has `U_col = A`, `U_row = B`, and

```
U_ant = {x+y : x ∈ A, y ∈ B} = A + B.
```

Every sum is realised: the point `(x, y)` is in `S`.

## Two points on a diagonal kill a sum in `A+B`

Fix a main diagonal `d`. Points of `S` on this diagonal are

```
(x, x-d)   with  x ∈ A  and  x-d ∈ B,
```

i.e. `x ∈ A ∩ (B+d)`. Suppose there are two distinct such abscissae `x ≠ x'`.
Their anti-diagonal values are `2x-d` and `2x'-d`. Constraint 3 of Q4 demands that the
midpoint anti-diagonal

```
( (2x-d) + (2x'-d) ) / 2  =  x + x' - d
```

be empty of `S`. But `x' ∈ A` and `x-d ∈ B`, so

```
x + x' - d  =  x' + (x-d)  ∈  A + B  =  U_ant.
```

The point `(x', x-d)` itself realises this sum, and it lies in the grid.
(It need not lie on the same diagonal; it only has to occupy the anti-diagonal.)
This contradicts constraint 3.

Hence `|S ∩ diagonal_d| ≤ 1` for every `d`. There are `2n-1` main diagonals, so `|S| ≤ 2n-1`.

## Anti-diagonal twin

Two points `(x, a-x)`, `(x', a-x')` on a common anti-diagonal kill the main diagonal
`x+x'-a`. That value equals `x - (a-x')` with `x ∈ A` and `a-x' ∈ B`, hence lies in
the set of occupied diagonals of the product (differences `A-B`). Same contradiction.
So `|S| ≤ 2n-1` also follows from constraint 4 alone.

## Remarks

- No parity hypothesis is used: L2b for `e=(1,1)` has none.
- Axis constraints 1–2 are not used. A product of 3-AP-free sets (the B3 construction)
  satisfies 1–2 and still dies here as soon as some `A ∩ (B+d)` has two elements.
- Sidecar thinning of `B×B` collapsing to `< n` points is the computational shadow of
  this lemma: a product cannot keep two points on a diagonal.

## What this does not prove

A *partial* filling of `A × B` need not occupy `A+B`. Lemma 1 is silent on those.
That is lemma 3.
