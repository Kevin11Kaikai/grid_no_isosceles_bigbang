# Round 12 — the `Δ₂` half does not separate, and truncation does not repair it

**Headline: the route recommended at the end of Round 11 fails. `Δ₂` is not "the easy half"
of Obligation R10 — its primary role is structurally identical to `Γ`'s, and its one extra
role, the Azuma step size, is not repairable by truncation. Measured: the only viable
truncation level is `Δ₂max` itself, i.e. the original hypothesis. Below it the criterion
fails by `Θ(n)`.**

Two of my own claims are corrected here. Round 12 produces no new obstacle — it closes the
last route the campaign had.

---

## 12.1 Correction: `Δ₂` is not "only a step size"

The Round 11 checkpoint recorded, as the highest-expected-value next action:

> at `ind.tex` line 1172, `Δ₂` enters as the maximum STEP SIZE in the Freedman/Azuma bound
> for `d_l^+(v)`, not as a drift term.

That was a guess written without auditing the other uses, and it is wrong as stated.
Auditing every occurrence of `Δ_a(H)` and `D_{a↑b}`:

| line | use |
|---|---|
| **782** | **base case of `dlemma`'s reverse induction on `b`** — at `b = r`, `d_{A↑r}(0) = Δ_a(H)` |
| 811 | step-size bound `C` inside `dlemma`'s own Freedman application |
| 846 | per-pair bound feeding `clemma` |
| **1018/1029** | **the drift of `d_l^-(v)`: `O(d_l·[C_{2,2→1} + Σ_k D_{k↑k+1}])`** |
| **1172** | **step-size bound in the asymmetric Azuma for `Z_l^+(v)`** |

Line 782 is the dominant one, and it is **exactly** `Γ`'s situation: `Δ₂` is the `i = 0`
value of a tracked variable, the induction is diagonal in `A` (`d_{A↑b}` is driven by
`d_{A↑b+1}` for the *same* `A`), and the consumer at line 1018 is again a **sum over the
edges at `v`**, not a maximum. So Round 10's edge-weighting observation applies to `Δ₂`
verbatim — which is what Round 10 already measured (`Δ₂_edge ≍ D^{0.24}`, holding at
`ε ≈ 0.26`).

What line 1172 adds is a role `Γ` does not have. That, and only that, was worth attacking.

## 12.2 Why truncation looked plausible

At line 1172 the step of `Z_l^+(v)` is `d_{{v,y_i}↑l+1}`, where `y_i` is the vertex chosen
at step `i` — drawn **uniformly from `V(i)`**. The step is therefore not a maximum over
pairs; it is the codegree at a *random* partner. Rare large values look truncatable: cap
the step at `τ`, apply Freedman to the truncated martingale, and bound separately the
probability that any step exceeds `τ`.

The criterion is forced by the stopping time, which halts on the first vertex to fail:

```
    sum_v P(v ever sees a step > tau)  ~  i_max * E_v[ B_v(tau) ]  <<  1,
        B_v(tau) = #{ y : codeg(v,y) > tau },
        i_max = zeta N D^{-1/2} (log N)^{1/2}  ~  1.07 zeta n   for H_n.
```

So the average number of partners above `τ` must be `≪ 1/n`, while `τ` must stay below
`D^{1/2-ε}` for the proof to close. Both sides are measurable.

## 12.3 The measurement — `experiments/r12_tail.c`

For each sampled `v`, `P(v)` is built exactly and `codeg(v,y)` read off for every `y`.
30–40 apexes per `n`, seed 777.

`τ` in units of `D^{1/2}`, showing `i_max · E_v[B_v(τ)]`:

| `τ/√D` | 0.80 | 0.65 | 0.55 | 0.50 | 0.40 | 0.30 | 0.20 |
|---|---|---|---|---|---|---|---|
| `n = 32` | 0 | 7.9 | 106 | 175 | 1 575 | 3 528 | 8 669 |
| `n = 64` | 0 | 0 | 0 | 0 | 2 412 | 8 100 | 1.6e4 |
| `n = 128` | 0 | 0 | 0 | 0 | 838 | 2.8e4 | 4.2e4 |

**The transition sits exactly at `Δ₂max`.** `Δ₂max/√D` = 0.622, 0.487, 0.422 for
`n = 32, 64, 128`, and in every case the last column that passes is the one just above
`Δ₂max` and the first that fails is the one just below. There is no intermediate regime.

Sharper, at the very top of the distribution:

| `n` | 32 | 64 | 96 | 128 | 160 |
|---|---|---|---|---|---|
| partners **at** the per-vertex max | 1.43 | 2.43 | 2.10 | 2.10 | 1.50 |
| partners within 90% of the max | 4.2 | 11.7 | 28.4 | 48.3 | 70.2 |
| `i_max · (partners at max)` | 49.6 | 167 | 226 | 300 | 256 |
| the same, in units of `n` | 1.55 | 2.62 | 2.35 | 2.34 | 1.60 |

Each vertex has 1.4–2.4 partners *at* its maximum codegree — its mirror images, the same
`Θ(1)`-sized structured family Rounds 1 and 8 identified for `Γ`. Truncating one below the
max therefore already costs `i_max · Θ(1) = Θ(n)`, against a requirement of `≪ 1`.

**Truncation fails by exactly a factor `n`, and the only level at which it succeeds is the
original hypothesis.**

The mechanism is not subtle and is not specific to the lattice: the process must run
`i_max = Θ(n)` steps to produce `Θ(n)` points, all `N` vertices must survive every step,
and each vertex has `Θ(1)` worst partners. The product is `Θ(n)` and nothing in the
argument can absorb it.

## 12.4 Without truncation, how much is missing

Freedman gives exponent `d²/(2(v + Cd)) ≥ d/(2C)` in the `C`-dominated regime. Taking the
best case `d = D^{1/2}` and `C = Δ₂max`, against the `log N` a union bound over the `N`
vertices requires:

| `n` | 32 | 64 | 96 | 128 | 160 | 192 |
|---|---|---|---|---|---|---|
| `d/(2C)` | 0.804 | 1.026 | 1.114 | 1.184 | 1.269 | 1.331 |
| `log N` | 6.93 | 8.32 | 9.13 | 9.70 | 10.15 | 10.52 |
| **short by** | **8.63** | **8.10** | **8.19** | **8.20** | **8.00** | **7.90** |

The shortfall is flat at ≈ 8 across a six-fold range of `n`, and closes only like
`√(log D)` — imperceptibly. With `C = D^{1/2-ε}` as hypothesised, `d/(2C) = D^ε/2` would be
polynomially large instead. The symmetric Azuma is worse still: with `c_i = Δ₂max` for
every step, `Σc_i² = i_max Δ₂max² ≍ n³` against `d² ≍ n² log n`, giving exponent
`≍ log n / n → 0` — a vacuous bound.

So the deficit at line 1172 is the same one-logarithm family that Rounds 3–7 found
everywhere else, here localised to a single exponent in a single inequality.

## 12.5 Consequence: Obligation R10 does not split

Both halves need the same thing. `Γ` and `Δ₂` each fail pointwise, each hold on average
(Round 10), and each of their pointwise roles — base case, drift error term, step size —
is enforced by a stopping time that halts on a single bad `(vertex, partner)` event
occurring at any of `Θ(n)` steps. There is no easy half to peel off. The single obligation
is:

> an argument that tolerates a `Θ(1/n)` fraction of bad `(vertex, partner)` events across
> `Θ(n)` steps, which the pointwise stopping time forbids by construction.

That is not a repair to Bennett–Bohman. It is a different proof of their theorem.

## 12.6 Status

| item | evidence | tier |
|---|---|---|
| `Δ₂`'s dominant role is `dlemma`'s base case, structurally identical to `Γ`'s | `VERIFIED` (source reading, `lit/ind.tex` 782/811/846/1018/1172) | B |
| the line-1172 step is the codegree at a *uniformly random* partner | `VERIFIED` (source reading) | B |
| truncation is viable only at `τ ≥ Δ₂max`; below it the criterion fails by `Θ(n)` | `VERIFIED_COMPUTATIONAL_RESULT` (`n` = 32..160) | C |
| each vertex has `Θ(1)` partners at its maximum codegree | `VERIFIED_COMPUTATIONAL_RESULT` | C |
| the Freedman exponent is short by a flat factor ≈ 8, closing like `√(log D)` | `VERIFIED_COMPUTATIONAL_RESULT` (`n` = 32..192) | C |
| Obligation R10 splits into an easier half | **REFUTED** | — |
| `C(n) = Omega(n)` | **NOT PROVED** | — |

Judge PASS 0 · TYPE2 0. **Twelfth consecutive honest zero on the bound.**

## 12.7 Recommendation: stop

The Round 11 checkpoint committed to this in advance:

> If it does not close, the campaign has nothing left that changes any line of the ledger,
> and should stop.

It did not close. Every route the campaign identified is now either closed, killed, or
reduced to Obligation R10, which Round 12 shows is a single indivisible obligation
amounting to reproving Bennett–Bohman's theorem under weaker hypotheses. That is a genuine
research problem in probabilistic combinatorics, not a probe, a sweep, or a synthetic
hypergraph away.

No further round of this campaign will change a line of the ledger. **Closing out.**
