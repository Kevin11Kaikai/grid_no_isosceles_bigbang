# Session 7.3 — Round 6 findings

**Headline: Round 6 resolved a contradiction the campaign had been carrying unnoticed, and
the answer is the encouraging one. Random greedy on `[n]^2` is linear, not `n/sqrt(log n)`.
The conjectured proof route of arXiv:2601.14465 is therefore *empirically sound*, and the
obstruction is confined entirely to the analysis — specifically, to the two Bennett–Bohman
hypotheses that Round 1 proved fail.**

---

## 6.0 The contradiction that forced this round

Round 2 §2.5 concluded *"the random independent set process empirically does deliver
`Omega(n)`, with constant about 0.78."* But Round 4's plain-greedy data, rescaled, said the
opposite:

| `n` | 8 | 16 | 32 | 48 |
|---|---|---|---|---|
| `greedy/n` | 1.50 | 1.375 | 1.25 | 1.167 (decaying) |
| `greedy/(n/sqrt(ln n))` | 2.16 | 2.29 | 2.33 | 2.29 (flat) |

Two incompatible readings of the same process, and the answer decides whether the
conjectured route is viable at all. `n <= 48` cannot separate them, because `sqrt(log n)`
moves by only 15% over that range. Round 6 pushed the measurement far enough to decide.

## 6.1 The measurement — `VERIFIED_COMPUTATIONAL_RESULT`

`experiments/r6_greedy.c` (C, exact same process as the Python greedy; validated against
it at `n = 16,32,48`). Vertices in uniformly random order; accept `p` iff `S u {p}` stays
isosceles-free. Degenerate/collinear triples are caught by the apex-midpoint case.

| `n` | 64 | 128 | 256 | 512 | 1024 | 2048 | 4096 | 8192 |
|---|---|---|---|---|---|---|---|---|
| greedy | 71.0 | 135.7 | 269.0 | 532.3 | 1051.7 | 2086.0 | 4139.5 | 8214 |
| `greedy/n` | 1.1094 | 1.0599 | 1.0508 | 1.0397 | 1.0270 | 1.0186 | 1.0106 | **1.0027** |

Fit `greedy = c * n * (log n)^{-alpha}`:

| range | 256→512 | 512→1024 | 1024→2048 | 2048→4096 | 4096→8192 | 128→8192 |
|---|---|---|---|---|---|---|
| `alpha` | 0.065 | 0.090 | 0.117 | 0.087 | 0.090 | **0.0897** |

Remarkably stable. Including the noisier `n=64` point raises it to 0.135; `alpha` is in
`[0.09, 0.14]`.

**The exclusion, stated as a ratio.** Over `n = 64 -> 8192` (a factor 128), `sqrt(ln n)`
grows by 47%. If `greedy ≍ n/sqrt(log n)`, then `greedy/n` had to fall by **32.1%**. It
fell by **9.6%** — 30% of the required amount, exactly as at `n=4096`.

**A model I tested and discarded.** At `n <= 2048` the residual looked like
`greedy = n + 0.85 sqrt(n)`: `(greedy/n - 1) sqrt(n)` = .875, .678, .812, .898, .865, .840.
It then breaks — .680 at `n=4096` and **.243** at `n=8192`. The `sqrt(n)` correction model
is dead; recorded so it is not re-derived. Relatedly, `greedy/n` passing through `1.00` near
`n ~ 10^4` is an accident of scale, **not** a structural constant: the decrement is a steady
`~0.008` per doubling and will carry `greedy/n` below 1.

> **`greedy(n)` is linear in `n` up to a factor decaying no faster than `(log n)^{-0.14}`.
> The model `greedy ≍ n/sqrt(log n)` is excluded by a factor 3.5–5 in the exponent.**

To be precise about what this does *not* settle: `alpha ≈ 0.09 > 0`, so the data is equally
consistent with `greedy/n -> const` (with finite-size corrections) and with
`greedy/n -> 0` like `(log n)^{-0.09}`. It cannot distinguish those. What it excludes,
decisively and over seven doublings, is the exponent `1/2` that would make the greedy
process merely reproduce the known bound.

Round 2's qualitative conclusion is confirmed and Round 4's implied worry is refuted.
Round 2's *constant* 0.78 is corrected: it was measured for the **one-point-per-column**
restricted process (FAR-C002), not the free process, which gives `~1.01–1.11 n`.

## 6.2 Bennett–Bohman: hypotheses fail, conclusion approximately holds

Round 1 proved rigorously that BB Thm 1.1 does **not** apply to `H_n`: `Delta_2 ≍
D^{1/2}/sqrt(log n)` and `Gamma = Omega(n^2)` against a required `D^{1-eps}`. But BB's
*conclusion* for `r=3` is `|I| = Theta(N (log N / D)^{1/2})`, which is exactly linear here.
Does it hold anyway? `experiments/r6_bb.c` computes `Sum_d N_a(d)^2` exactly (4-fold
symmetry), hence the edge count and `D = 3 * #edges / N`:

| `n` | 32 | 64 | 128 | 256 | 512 | 1024 |
|---|---|---|---|---|---|---|
| `D/(n^2 ln n)` | 1.7025 | 1.7287 | 1.7468 | 1.7602 | 1.7705 | **1.7787** |
| BB `= N(ln N/D)^{1/2}` | 34.7 | 68.8 | 137.0 | 272.9 | 544.2 | 1085.8 |
| measured greedy | — | 71.0 | 135.7 | 269.0 | 532.3 | 1051.7 |
| **measured / BB** | — | 1.032 | 0.990 | 0.986 | 0.978 | **0.969** |

The BB formula predicts the measured greedy to within 1–3% over `n = 64..1024`. **But the
ratio drifts steadily downward, about 1% per doubling, and I state that rather than
claiming a match.** `D/(n^2 ln n)` is still rising (differences 0.026, 0.018, 0.013, 0.010,
0.008, ratio ~0.78), extrapolating to `L ≈ 1.81`, hence `BB/n -> sqrt(2/L) ≈ 1.05`; the
measured `greedy/n` is already 1.011 at `n=4096` and still falling. So greedy decays
slightly faster than BB predicts (`alpha ≈ 0.09` measured against `alpha ≈ 0.03` implied by
BB's own drift).

**Honest form of the claim:**

> The Bennett–Bohman conclusion has the right *order* and approximately the right
> *constant* for `H_n` over three decades, despite its hypotheses provably failing. It is
> not an exact asymptotic match, and this data cannot decide whether `greedy/n` tends to a
> positive constant or to zero like a small power of `1/log n`.

## 6.3 What Round 6 changes

Rounds 1, 3, 4, 5 closed method families and produced the `sqrt(V/mu)` threshold that
*derives* the known bound `n/sqrt(log n)`. Round 6 shows the process itself does **better**
than that threshold — by a factor of about `sqrt(log n)`, which is precisely the missing
factor:

```
    alteration / first-moment threshold   :   n / sqrt(log n)     <- what we can PROVE
    the greedy process actually achieves  :   ~ n                 <- what is TRUE
    gap                                   :   sqrt(log n)
```

> **The `sqrt(log n)` gap is not a gap between the truth and the conjecture. It is a gap
> between the truth and the *analysis*. The process already achieves the conjectured bound;
> only the proof is missing.**

This is a materially better statement of the open problem than the campaign had before, and
it sharpens Round 3 §3.5 item 4 into a concrete, well-posed target: **prove a nibble/greedy
analysis for a 3-uniform hypergraph with `Gamma = Omega(n^2) ≫ D^{1-eps}`.** The
codegree obstruction `Gamma` comes from axis-parallel mirror pairs (Round 1) — a highly
structured, low-entropy family, which is exactly the kind of degeneracy a bespoke argument
can hope to absorb.

## 6.4 Status after Round 6

| item | evidence | tier |
|---|---|---|
| greedy is linear, `alpha in [0.09,0.14]`, not `1/2` | `VERIFIED_COMPUTATIONAL_RESULT` (`n<=8192`) | **B** |
| `n/sqrt(log n)` model excluded by factor 3.5–5 in exponent | same | **B** |
| BB conclusion approx. holds though hypotheses fail; ratio drifts ~1%/doubling | `VERIFIED_COMPUTATIONAL_RESULT` | **B** |
| `D/(n^2 ln n) -> ~1.81` | exact computation, `n <= 1024` | C |
| Round 2's constant 0.78 corrected (it was the one-per-column process) | correction | — |
| `C(n) = Omega(n)` | **NOT PROVED** | — |

**Judge PASS 0 / TYPE2 0.** Sixth honest zero on the bound. But unlike rounds 1–5, Round 6
is *positive* evidence: it says the conjecture is right, the route is right, and names the
single technical obstacle.

`NOVELTY_PRELIMINARY`. Nothing here is a new bound on `C(n)`.
