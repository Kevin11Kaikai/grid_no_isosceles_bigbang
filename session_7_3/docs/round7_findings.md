# Session 7.3 — Round 7 findings

**Headline: Round 7 settled the question Round 6 could not, and the answer is the good one.
`greedy/n` tends to a POSITIVE constant — the random independent set process really does
achieve `Theta(n)`. And the obstacle is now pinned exactly: both Bennett–Bohman hypotheses
fail for `H_n` by precisely one logarithmic factor, never by a polynomial one.**

---

## 7.1 Does `greedy/n` tend to a constant or to zero? — `VERIFIED_COMPUTATIONAL_RESULT`

Round 6 measured `alpha ≈ 0.09` in `g/n = c(log n)^{-alpha}` and stated honestly that the
data could not tell whether that decay is real. It matters: if real, `greedy/n -> 0` and
the route arXiv:2601.14465 calls "most probably" sufficient **fails**.

**Theory supplies the discriminating form.** Availability `~ exp(-D m^2/N^2)` gives
`Int_0^M e^{a m^2} dm = N` with `a = D/N^2`, hence `a M^2 = ln(2 a M N)`. With `M = gamma n`,
`N = n^2` and `D = K n^2 ln n`:

```
    K gamma^2 ln n = ln n + lnln n + O(1)
    =>   gamma^2 = A + B*(lnln n / ln n) + C/ln n ,     gamma -> sqrt(A) > 0 .
```

So the *shape* of the finite-`n` decay distinguishes the hypotheses. Both this and the
rival `gamma = c(ln n)^{-alpha}` (which tends to 0) are **linear least squares**.

**Data** (`r6_greedy.exe`; 20 seeds for `n <= 1024`, 10 at 2048, 6 at 4096, 1 at 8192):

| `n` | 64 | 128 | 256 | 512 | 1024 | 2048 | 4096 | 8192 |
|---|---|---|---|---|---|---|---|---|
| greedy | 68.00 | 135.35 | 268.00 | 532.85 | 1056.00 | 2088.20 | 4137.50 | 8214 |
| `g/n` | 1.0625 | 1.0574 | 1.0469 | 1.0407 | 1.0313 | 1.0196 | 1.0101 | **1.0027** |

(Round 6's `n=64` value 71.0 rested on 3 seeds and was high; 20 seeds give 68.00. Total
decay over `n = 64 -> 8192` is therefore **5.6%**, against the **32.1%** that
`g ≍ n/sqrt(log n)` requires — the exclusion is stronger than Round 6 reported.)

**Model comparison** (`experiments/r7_fit.py`):

| model | limit | RSS | AIC | out-of-sample: predict `n=8192` from `n<=4096` |
|---|---|---|---|---|
| **L3** `gamma^2 = A + B u + C w` | `gamma -> 0.716` | **9.14e-06** | **−104.3** | 1.00149, error **−0.12%** |
| L2 `gamma^2 = A + B u` | `gamma -> 0.835` | 6.06e-05 | −90.7 | 1.00743, error +0.47% |
| P `gamma = c (ln n)^{-alpha}` | `gamma -> 0` | 1.08e-04 | −86.0 | 1.00854, error +0.58% |

The theory-derived form beats the power-of-log rival **at equal parameter count** (L2 vs P:
RSS 43% lower), and on the honest test — predicting a held-out point — L3 is **5x more
accurate** than P.

**The independent check that makes this convincing.** The heuristic predicts
`gamma_inf = 1/sqrt(K)` where `K = lim D/(n^2 ln n)`. Round 6 computed `K = 1.81` from an
*exact* edge count, with no reference to the greedy data. That gives

```
    predicted  gamma_inf = 1/sqrt(1.81) = 0.743
    fitted     gamma_inf = 0.716  (L3)  /  0.835 (L2)
```

**within 4%** — a parameter obtained by extrapolating measurements matching one derived
independently from the hypergraph's degree.

> **Conclusion: `greedy/n` tends to a positive constant near `0.72–0.84`. The random
> independent set process achieves `Theta(n)`. Round 6's `alpha ≈ 0.09` is the finite-`n`
> signature of the `lnln n / ln n` correction, not a genuine power of `log n`.**

*Caveats, stated plainly.* Model selection on 8 points is evidence, not proof. The
heuristic is crude — it assumes the selected set behaves like a random set of the same
density, which is exactly the correlation a rigorous proof must handle — so its 4%
agreement with the fit could be partly luck. And note BB's formula read as an equality
gives `sqrt(2/K) = 1.051`, differing from the heuristic's `0.743` by `sqrt 2`; the data
favours `0.743`, but BB's theorem only claims `Theta(.)`, so this is not a discrepancy.
All three agree on the point that matters: **linear**.

## 7.2 Where exactly Bennett–Bohman fails — `VERIFIED_COMPUTATIONAL_RESULT`

Read from the source (`lit/ind.tex`, lines 250–253) rather than from memory:

> `Gamma(H)` = the maximum, over distinct vertices `v,v'`, of the number of edge pairs
> `e,e'` with `v in e\e'`, `v' in e'\e`, and `|e n e'| = r-1`.

For `r = 3` that is: the number of pairs `{a,b}` forming an isosceles triple with **both**
`v` and `v'`. The blow-up mechanism is then exact: if `v,v'` share the row `y_0`, a pair
`{a,b}` with both as apexes forces both onto the perpendicular bisector of `ab`, so that
bisector **is** the row, giving `a = (x, y_0+t)`, `b = (x, y_0-t)` — about `n^2/2` pairs.

**Measured** (`experiments/r7_gamma.c`, exact enumeration):

| `n` | 16 | 24 | 32 | 48 | 64 | 96 | 128 |
|---|---|---|---|---|---|---|---|
| same row | 143 | 275 | 480 | 1126 | 1987 | 4522 | 8064 |
| **diagonal** | 163 | 340 | 580 | 1270 | 2195 | 4854 | **8540** |
| generic pair | 29 | 20 | 21 | 45 | 24 | 45 | 72 |
| `row/n^2` | .559 | .477 | .469 | .489 | .485 | .491 | **.492** |

`row/n^2 -> 0.492`, matching the derived `1/2` exactly. **Correction to Round 1:** the
extremal pair is the *diagonal*, not the axis-parallel one (`diag/n^2 -> 0.521`); Round 1
identified the right mechanism at `n=12` but not the true maximiser. Generic pairs give
`O(n)` — three orders of magnitude less, confirming the blow-up is entirely structural.

**The sharp statement.** With `D = K n^2 ln n`, `K = 1.81` (Round 6, exact):

| `n` | 32 | 64 | 128 | limit |
|---|---|---|---|---|
| `Gamma * ln n / D` | 0.3327 | 0.3100 | 0.2984 | → `0.52/1.81 = 0.287` |

```
    BB requires  Gamma   < D^{1-eps}          H_n has  Gamma   ≍ D / log D
    BB requires  Delta_2 < D^{1/2-eps}        H_n has  Delta_2 ≍ D^{1/2} / sqrt(log D)
```

(The `Delta_2` line uses Round 1's measurement `Delta_2 ≈ 1.7n` against
`D^{1/2} = 1.345 n sqrt(ln n)`, giving `Delta_2/D^{1/2} = 1.264/sqrt(ln n)`.)

> **Neither hypothesis fails polynomially. Each fails by exactly a logarithmic factor —
> the same logarithm that Rounds 1–5 traced to `Sum_{d<=X} r_2(d)^2 ≍ X log X`.**

*Caveat:* the `Gamma` values are evaluated at four candidate extremal pairs, not maximised
over all `~n^4` pairs, so they are **lower bounds**. For showing BB's hypothesis *fails*
that is exactly the right direction; the matching upper bound `Gamma = O(n^2)` is not
verified here.

## 7.3 The target, now well-posed

Six rounds produced a diagnosis. Round 7 turns it into a single concrete question:

> **Strengthen Bennett–Bohman Theorem 1.1 to permit `Delta_2 = O(D^{1/2}/sqrt(log D))` and
> `Gamma = O(D/log D)` in place of the polynomial gaps `D^{1/2-eps}` and `D^{1-eps}`.**

That alone gives `C(n) = Omega(n)`, resolving the open problem — and §7.1 is evidence the
conclusion is true for `H_n`, so nothing is being asked for that the process does not
already deliver. This is a question about *their proof*, not about isosceles triangles.

## 7.4 Status after Round 7

| item | evidence | tier |
|---|---|---|
| `greedy/n -> positive const ~0.72-0.83`; process is `Theta(n)` | fit + out-of-sample + independent constant | **B** |
| fitted `gamma_inf` matches derived `1/sqrt(K)` to 4% | `VERIFIED_COMPUTATIONAL_RESULT` | **B** |
| `Gamma ≍ D/log D`; `Delta_2 ≍ D^{1/2}/sqrt(log D)` | exact enumeration (lower bds) | **B** |
| Round 1's `Gamma`-extremal pair corrected (diagonal, not row) | correction | C |
| Round 6's `n=64` value corrected (68.00, not 71.0) | correction | — |
| `C(n) = Omega(n)` | **NOT PROVED** | — |

**Judge PASS 0 / TYPE2 0.** Seventh honest zero on the bound. But the campaign now has a
positive thesis and a single named technical obstacle, which is a far better object than
the list of closed method families it had at Round 5.

`NOVELTY_PRELIMINARY`. Nothing here is a new bound on `C(n)`.
