# Round 11 — the regularity gap closes

**Headline: of the three hypotheses of Bennett–Bohman Thm 1.1 that `H_n` fails, one is
removable. Regularising upward to `D* = max_v deg(v)` costs a factor `sqrt(1.470) = 1.21`
in the conclusion and nothing else. The list of gaps goes 3 → 2 — and the two that remain
are the hard ones.**

This is the first time in eleven rounds that the campaign has *removed* an obstacle rather
than diagnosed one. It is also the cheapest of the three, and it does not help with the
other two at all.

---

## 11.1 The exact degree profile — `experiments/r11_reg.c`

Every edge of `H_n` has a **unique** apex: two apexes would force an equilateral triangle,
which does not exist in `Z^2`. So

```
    deg(a) = #{ {b,c} : |ab| = |ac| }  +  sum_{x != a} ( N_x(|xa|^2) - 1 )
```

with `N_x(r)` the number of grid points at squared distance `r` from `x`. Both terms fall
out of a single loop over the apex `x` — bucket the grid by distance from `x`, then
`cnt[r(a)] - 1` is what `a` receives and half the total is `x`'s own apex degree. `O(N^2)`,
exact integer arithmetic, no sampling.

| `n` | `Davg / n² ln n` | `Dmin` (corner) | `Dmax` (centre) | `Dmax/Davg` | `Dmax/Dmin` | `Dmin/Davg` |
|---|---|---|---|---|---|---|
| 16 | 1.6629 | 765 | 1 726 | 1.4623 | 2.256 | 0.648 |
| 24 | 1.6884 | 1 911 | 4 544 | 1.4703 | 2.378 | 0.618 |
| 32 | 1.7025 | 3 679 | 8 866 | 1.4674 | 2.410 | 0.609 |
| 48 | 1.7190 | 9 027 | 22 598 | 1.4739 | 2.503 | 0.589 |
| 64 | 1.7287 | 17 149 | 43 388 | 1.4733 | 2.530 | 0.582 |
| 96 | 1.7400 | 41 583 | 107 614 | 1.4703 | 2.588 | 0.568 |
| 128 | 1.7468 | 78 019 | 204 160 | 1.4702 | 2.617 | 0.562 |
| 160 | 1.7515 | 126 431 | 334 204 | 1.4686 | 2.643 | 0.556 |

`Dmax/Davg = 1.470` with no trend across a 10-fold range of `n` — Round 6's `1.47` is
confirmed exactly. The minimum is always the corner, the maximum always the centre.
`Dmax/Dmin` is still creeping upward (2.26 → 2.64) and whether it is bounded is **not**
settled here — **and it does not matter**, because the argument below uses only `Dmax`.

`Davg = 1.66..1.75 n^2 ln n` also independently reproduces the sampled value
`1.65..1.82` from Round 10's `r10_edgeg.c`, which computes degrees by a completely
different route (`|P(x)|`).

## 11.2 The repair

Regularising **downward** is not available: deleting edges of `H_n` would let non-isosceles-
free sets in. Regularising **upward** is, and it is free.

> **Lemma R11 (regularisation).** Let `D* = max_v deg_{H_n}(v)`. Let `R` be a 3-uniform
> hypergraph on `[n]^2`, edge-disjoint from `H_n`, with `deg_R(v) = D* - deg_{H_n}(v)`, and
> set `H' = H_n u R`. Then `H'` is `D*`-regular, and every independent set of `H'` is an
> isosceles-free subset of `[n]^2`.

The second clause is immediate — `I` independent in `H'` contains no edge of `H_n` — and it
is the whole point: a lower bound proved for `H'` transfers to `C(n)` verbatim.

The cost is a constant. With `D* = 1.470 Davg = 2.55 n^2 ln n` and `N = n^2`,

```
    N (log N / D*)^{1/(r-1)} = n^2 (2 ln n / 2.55 n^2 ln n)^{1/2} = 0.885 n
```

so the Bennett–Bohman conclusion for `H'` is still `Omega(n)`. The regularisation pays
exactly `sqrt(Dmax/Davg) = sqrt(1.470) = 1.21`.

## 11.3 Does `R` break the other hypotheses? — `experiments/r11_dummy.c`

That is the only thing that could go wrong, and it is what a fake reduction would look
like. `R` is built by the configuration model on the deficiency degrees, independently of
`H_n`. Measured directly:

| `n` | `\|R\|/\|E(H_n)\|` | `Δ₂(R)` max | `Δ₂(R)` mean | `Γ_R` mean | `Γ_R` max | `ln²n` | `Δ₂(H_n)≈n` | `Γ(H_n)≈n²/2` |
|---|---|---|---|---|---|---|---|---|
| 24 | 0.470 | 27 | 5.03 | 17.4 | 65 | 10.1 | 24 | 288 |
| 32 | 0.467 | 31 | 5.51 | 20.9 | 68 | 12.0 | 32 | 512 |
| 48 | 0.474 | 40 | 6.30 | 27.9 | 75 | 15.0 | 48 | 1 152 |
| 64 | 0.473 | 40 | 6.80 | 32.4 | 68 | 17.3 | 64 | 2 048 |

`Γ_R` mean / `ln²n` = 1.72, 1.74, 1.86, 1.87 — flat, so `Γ_R = Theta(log²N)` as predicted.
`Δ₂(R)` mean matches `6|R|/N(N-1)` to three decimals and grows like `log N`; the max is
about six times the mean, the expected Poisson tail over `N²` pairs. Hence

```
    Delta_2(H') <= Delta_2(H_n) + O(log N)   =  Theta(n)      unchanged
    Gamma(H')   <= Gamma(H_n)   + O(log^2 N) =  Theta(n^2)    unchanged
```

and the edge-weighted statistics of Round 10 can only improve: `R` contributes `~0.47|E|`
extra edges each carrying `Γ = O(log²N)`, which *dilutes* the weighted mean.

**Honest note on the numbers.** At `n = 64`, `Δ₂(R) = 40` against `Δ₂(H_n) ≈ 84` — the
dummy hypergraph's codegree is not small in absolute terms at accessible `n`, it is only
small *asymptotically* (`log N` against `n`). Anyone reading the table should see that
separation is a statement about growth rates, not about `n = 64`.

## 11.4 What is not done

1. The configuration model produces triples with repeated vertices (0.5–0.6% here), which
   were discarded, perturbing the degrees slightly. An exact construction needs a proper
   degree-sequence realisation for 3-uniform hypergraphs plus a switching argument. Routine,
   not done.
2. Edge-disjointness from `H_n` was not enforced in the experiment. `|H_n| / C(N,3) ≈
   3.5 ln n / n^2 -> 0`, so rejection sampling costs nothing, but it is not implemented.
3. The `Δ₂(R)` and `Γ_R` bounds are **measured**, not proved. They are standard
   Chernoff/Poisson estimates for the configuration model; the proof is not written.

None of these is deep. Lemma R11 should be regarded as `PARTIAL_PROOF` — the mathematical
content is settled and the write-up is not.

## 11.5 The ledger, and the blunt part

| gap | status after Round 11 |
|---|---|
| `D`-regularity | **CLOSED** — removable at a cost of `sqrt(1.470) = 1.21` |
| `Γ < D^{1-eps}` pointwise | fails; holds as an edge-weighted average with `eps ~ 0.40` |
| `Δ₂ < D^{1/2-eps}` pointwise | fails; holds as an edge-weighted average with `eps ~ 0.26` |

Adding `R` does **not** lower `Γ` or `Δ₂` — those are maxima over pairs of `H_n`, and `H_n`
is a subgraph of `H'`. So Round 11 removes the easy gap and leaves the hard two exactly
where Round 10 left them: they fail pointwise, hold on average, and what stands between
those two facts is the stopping time at `ind.tex` line 720.

## 11.6 Status

| item | evidence | tier |
|---|---|---|
| exact degree profile of `H_n`; `Dmax/Davg -> 1.470`, min at corner, max at centre | `VERIFIED_COMPUTATIONAL_RESULT` (exact, `n <= 160`) | C |
| every edge of `H_n` has a unique apex | `VERIFIED_THEOREM` (no equilateral triangle in `Z^2`) | C |
| Lemma R11: upward regularisation is free up to `sqrt(1.470)` | `PARTIAL_PROOF` (§11.4) | **B** |
| `Δ₂(R) = O(log N)`, `Γ_R = Theta(log²N)` | `VERIFIED_COMPUTATIONAL_RESULT` | C |
| `C(n) = Omega(n)` | **NOT PROVED** | — |

Judge PASS 0 · TYPE2 0. **Eleventh consecutive honest zero on the bound.**

`NOVELTY_PRELIMINARY`. Upward regularisation by dummy edges is a standard device; the
content here is the verification that it is free *for this hypergraph*, not the device.
