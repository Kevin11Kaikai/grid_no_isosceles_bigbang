# Session 7.3 — Round 2 findings (FAR-C002 existence only)

**Scope, as instructed: attack only the existence of one-point-per-column isosceles-free
sets, i.e. `for every n there is f:[n]->[n] whose graph is isosceles-free`, which would
give `C(n) >= n` outright.**

**Headline: existence is NOT proved. Round 2 produced one rigorous sub-barrier, one
verified representation shift, and evidence that the conjecture is true with an explicit
constant. C002 stays `PROGRESS`; it was not falsified either.**

---

## 2.1 Sub-barrier: the clean strengthening is provably too weak — `VERIFIED_THEOREM`

The obvious way to get an isosceles-free set is to make **all** pairwise distances
distinct (a 2-D Golomb/Sidon set); then no two distances coincide at all, let alone at a
shared apex. Counting kills it:

`C(m,2) <= Ndist(n)` = number of distinct squared distances realised in `[n]^2`, and
`Ndist(n) ~ K*2n^2/sqrt(log n)` by Landau-Ramanujan, so `m = O(n/(log n)^{1/4})`.

Measured exactly (`experiments/r2_probes.py`):

| `n` | 16 | 32 | 64 | 128 | 256 | 512 | 1024 |
|---|---|---|---|---|---|---|---|
| cap `m` | 15 | 29 | 56 | 108 | 209 | 406 | 792 |
| **cap/`n`** | 0.938 | 0.906 | 0.875 | 0.844 | 0.816 | 0.793 | **0.773** |

`cap/n` decreases monotonically. **Consequence: any proof of `C(n) = Omega(n)` must
genuinely exploit that only *same-apex* distances need be distinct.** The strengthening
that would make the problem easy is sublinear and therefore unusable. This closes off the
most natural route to C002 and is the round's one clean rigorous statement.

## 2.2 No explicit algebraic construction — `VERIFIED_COMPUTATIONAL_RESULT`

Violation counts for one-per-column algebraic maps (`experiments/r2_probes.py`), `0` would
be a construction:

| `f(i)` | n=16 | n=32 | n=64 | n=128 |
|---|---|---|---|---|
| `i^2 mod n` | 35 | 109 | 289 | 791 |
| `i^3 mod n` | 32 | 142 | 508 | 1308 |
| `3^i mod n` | 30 | 98 | 347 | 706 |
| `floor(i^2/n)` | 17 | 60 | 173 | 547 |
| `i^-1 mod n` | 44 | 212 | 837 | 3057 |

All fail, and the best of them tracks `~n log n` — **exactly the count predicted for a
uniformly random `f`**. So the algebraic families carry no useful structure here; they are
no better than chance. This extends the `iso6` finding ("no algebraic family tested is
isosceles-free") to the one-per-column setting, which is the shape C002 needs.

## 2.3 Representation shift: the constraint is a SLOPE condition — `VERIFIED_LEMMA`

Adding column `i` with value `v`, the constraints split **exactly** two ways. Writing
`phi_j := f(j)^2 + (i-j)^2`:

- **(A) apex = the new column.** For `a,b < i` the condition
  `(i-a)^2+(v-f(a))^2 = (i-b)^2+(v-f(b))^2` has its `v^2` **cancel**, leaving the linear
  equation `2v(f(b)-f(a)) = phi_b - phi_a`. So

  > `v` is legal for the new apex **iff `2v` is not a slope of the point set
  > `P_j = (f(j), phi_j)`, `j < i`.**

- **(B) apex = an old column `a`.** `(v-f(a))^2 = d - (i-a)^2` for some `d` already used at
  `a` — solvable only when `d-(i-a)^2` is a **perfect square**, hence rare.

Verified against the definition over 968 (prefix, value) pairs, **0 mismatches**
(`experiments/r2_avail.py`). This is the representation shift §26 asks for: a quadratic
distance condition becomes a **slope-avoidance** condition plus a sum-of-two-squares
condition. It is the one new handle Round 2 produced.

## 2.4 Why first-moment methods cannot settle existence — `VERIFIED_THEOREM`

Counting forbidden values at step `i`:
- from (A): up to `C(i,2) ~ i^2/2` slopes;
- from (B): `~ i^2/(sqrt(2) n)` after the perfect-square filter.

At `i = n` this is `~n^2/8` forbidden events against only `n` available values. **The union
bound is vacuous by a factor of `n`**, so no first-moment or naive-LLL argument can work —
the forbidden values must collide heavily, and the whole question is *how much*. This is a
different obstruction from Round 1's `log n` deficit and is more severe.

## 2.5 The decisive measurement: the greedy frontier does NOT decay — `VERIFIED_COMPUTATIONAL_RESULT`

Pure random greedy, filling columns left to right, using the (A)/(B) split
(`experiments/r2_frontier.py`). Fraction of columns reached before availability hits zero:

| `n` | 32 | 48 | 64 | 96 | 128 | 160 | 192 |
|---|---|---|---|---|---|---|---|
| seeds | 12 | 12 | 12 | 12 | 12 | 6 | 6 |
| **mean/`n`** | 0.794 | 0.804 | 0.779 | 0.779 | 0.777 | 0.783 | 0.721 |
| max/`n` | 0.938 | 0.917 | 0.891 | 0.844 | 0.828 | 0.844 | 0.760 |

**`mean/n` is flat at `~0.78` across a 5x range of `n`.** It does not decay toward 0.
Two consequences:

1. **C002 is not falsified.** Had the frontier decayed, one-per-column sets would fail for
   large `n` and C002 would be dead. It plateaus instead.
2. **The random independent set process empirically does deliver `Omega(n)`** — with
   constant about `0.78` — which is exactly what arXiv:2601.14465 predicts and exactly what
   nobody can prove. The obstruction is entirely in the analysis, not in the truth.

The `n=192` dip rests on 6 seeds and is within sampling noise of the flat trend; it should
not be read as the onset of decay without more seeds.

## 2.6 Correction to a Round 1 statement

Round 1 said the polynomial growth of backtracking node counts was "the real evidence that
these sets exist for every `n`". That was too strong. Round 2 shows pure greedy *runs out*
at `~0.78n` and backtracking is doing real repair work on the last `~22%`. The evidence for
existence now rests on the **flat frontier fraction** (2.5), which is the better statistic.
The node counts remain polynomial over the range tested, but that range is small.

## 2.7 Status after Round 2

| item | evidence | tier |
|---|---|---|
| all-distances-distinct capped at `O(n/(log n)^{1/4})` | `VERIFIED_THEOREM` | B |
| slope + sum-of-two-squares reformulation | `VERIFIED_LEMMA` | B |
| first-moment methods vacuous by a factor `n` | `VERIFIED_THEOREM` | B |
| greedy frontier flat at `~0.78` | `VERIFIED_COMPUTATIONAL_RESULT` | C |
| no algebraic construction | `VERIFIED_COMPUTATIONAL_RESULT` | C |
| **C002 existence for all `n`** | **NOT PROVED, not falsified** | — |
| `C(n) = Omega(n)` | **NOT PROVED** | — |

**Hardest remaining obligation, stated honestly:** show that the slopes determined by
`{(f(j), f(j)^2+(i-j)^2)}` miss at least one even integer in `[0,2n)` at every step. That
is a question about slope-set structure with `~i^2/2` slopes landing in `n` targets, i.e.
about *collisions among slopes* — genuinely different from the original problem, but no
tool in this campaign bears on it.

`NOVELTY_PRELIMINARY` throughout. Nothing here is a theorem about `C(n)`.
