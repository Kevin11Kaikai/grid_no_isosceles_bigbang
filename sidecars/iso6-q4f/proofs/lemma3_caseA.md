# Lemma 3 Case A — large overlap, reflection fold

**Setup.** `S` is Q4-feasible and `R = max_a r(a) > n^{1/2}`.
Fix `a*` attaining the maximum, so `r(a*) > n^{1/2}`. Write
`σ(x,y) = (a*-y, a*-x)`. This involution preserves `x-y`, sends anti-value
`α` to `2a*-α`, and has no fixed point in `S` (those would lie on the empty
anti-diagonal `x+y=a*`).

```
S*  =  { P ∈ S : σ(P) ∈ S }
S'  =  S \ S*
D*  =  { d : diagonal d contains a pair with midpoint anti-value a* }
```

`|D*| = r(a*)`. On diagonal `d ∈ D*` write `2 t_d` for the number of `S*`-points
(nested pairs `{a*±δ}`). Then `|S*| = 2 Σ t_d ≥ 2 r(a*) > 2 n^{1/2}`.

Subsets of Q4-feasible sets are Q4-feasible. In particular `S'` is Q4-feasible.

## What is actually proved

**Trivial counting.** `|S*| ≤ max_dia(S*) · (2n-1)`. The same with
`max_row(S*) · n` or `max_ant(S*) · (2n-1)`. So *if* any one of those three
maxima is `≤ n^{1/2}`, then `|S*| = O(n^{3/2})`. This implication was never
the gap; it is the definition of those maxima.

**A2.** If `S'` itself has `max r ≤ n^{1/2}`, Case B gives `|S'| = O(n^{3/2})`.

**A3 (frame).** If `t_d = 1` for every `d ∈ D*` (pure matching), then
`|S*| = 2 r(a*) ≤ 2(2n-1) = O(n)`. The `n=7` maximiser is of this type
(`r(6)=8`, `|S*|=16`, `|S'|=0`).

**Fold geometry.** Occupied rows `R` and columns `C` of `S*` satisfy
`C = {a*-y : y ∈ R}` and `ρ_row(y) = ρ_col(a*-y)`. A point of `S*` in row `y`
has its partner in column `a*-y`; that column contains *exactly* those partners.

## The old A1 hypothesis is false

The previous writeup treated “prove `max_dia(S*) = O(n^{1/2})`” (or row/ant)
as the remaining GAP. That statement is **false** as a theorem about all
Case A sets. Explicit Q4-feasible constructions (`a1_construct.py`,
`a1_longrow.py`):

| seed | n | `max r` | `|S*|` | `max_dia(S*)` | `max_row(S*)` | `max_ant(S*)` | `√n` |
|---|---|---|---|---|---|---|---|
| heavy diagonal | 32 | 24 | 62 | **6** | 4 | 4 | 5.66 |
| heavy diagonal | 48 | 33 | 84 | **8** | 3 | 4 | 6.93 |
| heavy diagonal | 81 | 59 | 148 | **10** | 4 | 5 | 9 |
| long row | 32 | 12 | 24 | 2 | **9** | 1 | 5.66 |
| long row | 81 | 31 | 62 | 2 | **16** | 2 | 9 |

Each of `max_dia` and `max_row` can separately exceed `√n` while staying in
Case A. A `t=2` biclique (`a1_biclique.py`, `n=81`) has `k=15` diagonals on
the same two `δ`, so `max_ant(S*) ≥ 15 > 9` as well. Extra-kill overlap
`max_extra_r` can also exceed `√n` (same biclique: all `k` diagonals share
`Mix({δ,ε})`).

So none of the following is a theorem:

- `max_dia(S*) ≤ √n`
- `max_row(S*) ≤ √n`
- `max_ant(S*) ≤ √n`
- extra midpoints disjoint, or `max_extra_r ≤ √n`
- `(d,δ)` graph `K_{3,2}`-free / `K_{2,3}`-free (`a1_k32.py` places `k=5`
  copies of the same two-delta fibre)

## What remains (the real A1)

**Claim (open).** `|S*| = O(n^{3/2})` for the fold at a maximiser `a*`.

All constructions above still have `|S*| = O(n)` (typically `~2n`). Forced-pair
greedy (`lemma3_search.py`) up to `n=243` is `|S*| ≤ 2.27 n`. Complete
`(d,δ)` bicliques have `k t ≈ n/3`. Combining a long row with a long diagonal
did not make `min(max_row, max_col, max_dia, max_ant)` exceed `√n`
(`a1_allmax.py`). That suggests a possible replacement

```
min( max_row(S*), max_col(S*), max_dia(S*), max_ant(S*) )  ≤  n^{1/2},
```

which would imply `|S*| = O(n^{3/2})` by trivial counting, but this is
**not proved**, and a counterexample was not found.

**A2 is also not automatic.** If `S'` has large `r`, fold again. Uncontrolled
peeling can use `Θ(n)` layers and destroy a power saving.

## Routes that failed

1. Disjoint extra anti-diagonal kills ⇒ `|S*| = O(n)`. Extra kills overlap.
2. Kővári–Sós–Turán on `(d,δ)` incidences, assuming a forbidden `K_{s,t}`.
   `K_{k,2}` (`a1_k32.py`), `K_{2,3}` (`a1_k23b.py`), and `K_{3,3}`
   (`a1_k33.py`) are all Q4-feasible.
3. Axis bound `ρ + 2r/ρ ≤ n` does not force `ρ ≤ √n` (it allows `ρ = O(1)`
   and `ρ = Θ(n)`).
4. Pair-count / Cauchy–Schwarz using `r*(b) ≤ r(a*)` overcounts because
   several pairs on one diagonal can share a midpoint; consecutive midpoints
   only recover `|S*| = O(n^2)`.

## Verdict on Case A

Not closed. Campaign retarget: [`lemma3_heavy.md`](lemma3_heavy.md).
The whole set (not just `S*`) is `O(n^{2-ε})` unless many diagonals and
many antis are heavy and at least one heavy support exceeds `n^{7/8}`.
`S'` peeling is absorbed. Do not claim `Q4(n)=O(n^{2-ε})`.
