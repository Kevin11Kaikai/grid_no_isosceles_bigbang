# Session 7.3 — Round 8 findings

**Headline: Round 7 asked for a log-strengthening of Bennett–Bohman. Round 8 shows that is
much stronger than what `H_n` actually needs. `Gamma` exceeds BB's threshold on only a
`Theta(1/n)` fraction of vertex pairs; on the other `1 - Theta(1/n)` it is `Theta(log^2 n)`,
below the threshold by four to five orders of magnitude and widening. The required
strengthening is therefore not "allow a larger `Gamma` everywhere" but "tolerate a
vanishing fraction of bad pairs" — a far more standard and plausible ask.**

---

## 8.1 The distribution of `Gamma(v,v')` — `VERIFIED_COMPUTATIONAL_RESULT`

BB's hypothesis constrains `max_{v,v'} Gamma(v,v')`. Rounds 1 and 7 only ever measured that
maximum. Round 8 measures the whole distribution, using
`Gamma(v,v') = |P(v) n P(v')|` with `P(v) = {{a,b} : {v,a,b} isosceles}`, computed in
`O(n^2 log n)` per vertex via a table of lattice vectors indexed by norm
(`experiments/r8_gdist.c`, 2000 random pairs per `n`).

| `n` | 32 | 64 | 128 | 256 |
|---|---|---|---|---|
| median `Gamma` | 62 | 92 | 122 | 158 |
| **median / `ln^2 n`** | 5.162 | 5.319 | 5.182 | **5.138** |
| mean (all pairs) | 103.4 | 183.8 | 339.0 | 518.3 |
| p99 (all pairs) | 600 | 1880 | 6848 | 12822 |
| max over sample | 704 | 2425 | 9032 | 32754 |
| fraction structured | .107 | .058 | .030 | .013 |
| `4/n` | .125 | .0625 | .0312 | .0156 |

`median/ln^2 n` is **dead flat at ~5.15**, exactly the naive prediction: `P(v)` and `P(v')`
are sets of `D ~ 1.78 n^2 ln n` pairs among `~n^4/2`, so if unrelated they meet in
`2D^2/N^2 ~ 6.1 ln^2 n`. **The typical pair behaves as if the hypergraph were random.**

Against BB's threshold (`eps = 0.1`, so `D^{0.9}`):

| `n` | 32 | 128 | 256 | 1024 |
|---|---|---|---|---|
| median `Gamma` / `D^{0.9}` | 2.4e-02 | 2.8e-03 | 9.4e-04 | **9.9e-05** |

The typical pair satisfies BB's condition with four to five orders of magnitude to spare,
and the margin **widens**. Only the extremal `Theta(1/n)` fraction violates it.

## 8.2 Which pairs are bad, and why — with a prediction I got wrong

For both `v` and `v'` to be apexes of `{a,b}`, the points `a,b` must be mirror images across
the perpendicular bisector of `{v,v'}`. For both to be lattice points that reflection must
preserve `Z^2`. Reflection with primitive normal `(p,q)` has matrix
`I - 2(p,q)^T(p,q)/(p^2+q^2)`, which is integral only for `p^2+q^2 in {1,2}` — i.e. row,
column, diagonal, anti-diagonal. **Four families, hence the `4/n` above, which the data
confirms.**

**But my stronger prediction — that every other direction collapses to the generic level —
is FALSE, and the measurement refuted it** (`experiments/r8_dir.c`):

| direction `(p,q)` | (1,0) | (0,1) | (1,1) | (1,-1) | (2,1) | (3,1) | (3,2) | (4,1) |
|---|---|---|---|---|---|---|---|---|
| `p^2+q^2` | 1 | 1 | 2 | 2 | 5 | 10 | 13 | 17 |
| reflection integral | YES | YES | YES | YES | no | no | no | no |
| `Gamma/n^2` (`n=128`) | .537 | .537 | .518 | .510 | .082 | .102 | .050 | .024 |

The four reflection directions are extremal by a factor `>= 5` over the next-shortest, so
the reflection mechanism does explain the *maximum*. But `(2,1)` gives `Gamma/n^2 = 0.082`
at both `n=64` and `n=128` — still `Theta(n^2)`, not polylogarithmic. **The bad set is
"pairs whose difference has a short primitive direction", not just the four families.**

This is still consistent with 8.1, because a random difference vector in `[n]^2` has
primitive direction of norm `~n^2`. The fraction of pairs with primitive direction of norm
`<= R` is `~ c sqrt(R)/n`, so for any fixed `R` the bad set is `Theta(1/n) = Theta(N^{-1/2})`.

## 8.3 A third hypothesis gap, minor but worth recording

`|P(v)|` at the centre gives `D/(n^2 ln n) ~ 2.57`, while Round 6's exact edge count gives
the *average* `1.75`. The ratio 1.47 is exactly Round 1's measured `Dmax/Davg = 1.36-1.50`.
So **`H_n` is not `D`-regular**, which BB Thm 1.1 explicitly requires. Constant-factor
irregularity is normally harmless for such arguments, but it is a third gap and should be
stated rather than glossed. (This discrepancy is also what flagged the distinction between
centre-degree and average-degree, which had been used loosely in earlier rounds.)

## 8.4 The target, restated and weakened

Round 7 posed: *strengthen BB to permit `Gamma = O(D/log D)`.* Round 8 says that is more
than `H_n` needs:

> **What `H_n` actually requires is a version of Bennett–Bohman tolerating a `Theta(N^{-1/2})`
> fraction of vertex pairs on which `Gamma` is `Theta(D/log D)`, with `Gamma = O(log^2 n)`
> on all the rest — together with `Delta_2 = O(D^{1/2}/sqrt(log D))` and constant-factor
> irregularity.**

"Almost all pairs are good" relaxations are routine in this literature in a way that
"the max is bigger than allowed" is not. This is the sharpest and most plausible form the
target has taken, and it is the form the note should state.

## 8.5 Status after Round 8

| item | evidence | tier |
|---|---|---|
| median `Gamma = Theta(log^2 n)`, flat at `5.15 ln^2 n` | `VERIFIED_COMPUTATIONAL_RESULT` | **B** |
| typical pair beats `D^{0.9}` by 4-5 orders, widening | same | **B** |
| bad pairs = short-primitive-direction pairs, `Theta(1/n)` fraction | same | **B** |
| the 4 extremal families = the lattice-reflection directions | derived + measured | **B** |
| "only those 4 are `Theta(n^2)`" | **REFUTED by measurement** | — |
| `H_n` is not `D`-regular (`Dmax/Davg ~ 1.47`) | `VERIFIED_COMPUTATIONAL_RESULT` | C |
| `C(n) = Omega(n)` | **NOT PROVED** | — |

Structured `Gamma` values (480/1987/8064 row; 580/2195/8540 diagonal, `n=32/64/128`) were
reproduced **exactly** by two independent algorithms — Round 7's brute-force `O(n^4)`
enumeration and Round 8's set-intersection method. Round 7's numbers are confirmed.

**Judge PASS 0 / TYPE2 0.** Eighth honest zero on the bound.

`NOVELTY_PRELIMINARY`. Nothing here is a new bound on `C(n)`.
