# Session 7.3 — Round 3 findings (final round under the §78b budget)

**Headline: the linear lower bound was not proved. Round 3 closed the most natural escape
route from the `log n` obstruction, rigorously and decisively — and found that B6, recorded
in `iso6` as an *upper*-bound barrier, cuts both ways.**

---

## 3.1 Redirection: (B), not (A), is the binding constraint

Round 2 emphasised the slope condition (A). Measurement (`experiments/r3_slopes.py`) shows
that was misplaced. At the point where random greedy dies:

| `n` | `|forbA|`/`n` | `|forbB|`/`n` |
|---|---|---|
| 48 | 0.63 | 0.83 |
| 64 | 0.56 | 0.95 |
| 96 | 0.64 | 0.97 |
| 128 | 0.75 | 0.95 |

**(B) — the old-apex, sum-of-two-squares condition — forbids 83–97% of values; (A) forbids
about 60%.** The binding constraint is the arithmetic one, not the slope one.

Also measured: the *effective* number of slope-pairs (those whose slope is actually an
integer, hence actually forbids something) is only **8–15%** of the naive `i²/2`, and that
ratio decreases with `n` (0.152, 0.117, 0.095, 0.082 at `n = 48,64,96,128`). So Round 2's
"union bound is vacuous by a factor `n`" was pessimistic — but not by enough to matter: the
effective count still scales like `n^{1.37}`, against `n` available values.

## 3.2 The natural escape route, and why it fails — `VERIFIED_THEOREM`

Every route so far loses a `log n` traceable to `M_2(R) = Σ_{r≤R} r_2(r)² ≍ R log R` — the
mean multiplicity of a squared distance. The natural fix: **work inside a ground set where
that multiplicity is bounded.**

Let `S_k ⊆ [n]²` satisfy condition `D(k)` — at most `k` points at each squared distance
from each apex. Inside `S_k` the isosceles hypergraph has apex-degree
`Σ_d C(m_a(d),2) ≤ ((k-1)/2)|S_k|`, so `D = O(k|S_k|)` — **the log factor is gone.**
Then run the nibble inside `S_k`.

This is exactly the right shape of idea, and it fails. B6 (`iso6/routes/H/report.md`, sharp
form) gives

```
    |S_k| = Theta( n^{2-2/(k+1)} / (log n)^{alpha_k} ),      alpha_k = (2^k - 1)/(k+1)
```

and the penalty `alpha_k` is **doubly exponential in `k`**. Granting the nibble outright
(it does not in fact apply — Round 1), the best obtainable is

```
    |I_k|  =  O( sqrt( |S_k| log|S_k| / k ) )
           =  O( n^{1 - 1/(k+1)} * (log n)^{(1-alpha_k)/2} / sqrt(k) )
```

**Claim (rigorous).** For every `k >= 1` and every `n >= 3` this is `< n`; and for every
fixed `k` it is asymptotically *worse than the known bound* `n/sqrt(log n)`.

*Proof.* For `k >= 2`, `alpha_k >= 1`, so the log exponent `(1-alpha_k)/2 <= 0`, while
`n^{1-1/(k+1)} < n`; the product is `< n`. For `k = 1`, the bound is
`n^{1/2}(log n)^{1/4} < n`. Against `n/sqrt(log n)` the ratio is
`n^{-1/(k+1)} (log n)^{(2-alpha_k)/2} / sqrt(k) -> 0` for every fixed `k`, since the
polynomial factor `n^{-1/(k+1)}` dominates any power of `log n`. ∎

Numerically, at `n = 10^6` (target `10^6`, known bound `2.69 x 10^5`):

| `k` | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 |
|---|---|---|---|---|---|---|---|---|
| bound | 1.9e3 | **7.1e3** | 6.8e3 | 2.3e3 | 1.9e2 | 1.6 | 2e-11 | 3e-48 |

The route peaks at `k = 2` at about **7 100** — a factor 38 below the *known* bound and 140
below the target — then collapses. **The escape hatch is closed.**

### Independent re-verification of the moment exponents

The kill rests entirely on `alpha_k`, which rests on `M_j(R) ~ c_j R (log R)^{2^{j-1}-1}`.
Recomputed from scratch (`experiments/r3_moments.py`, lattice sieve, no `iso6` code reused),
`R` up to `4 x 10^6`:

| | `M_1/R` | `M_2/(R log R)` | `M_3/(R log^3 R)` | `M_4/(R log^7 R)` |
|---|---|---|---|---|
| `R=2.5e5` | 3.14139 | 4.649 | 0.758 | 0.00106 |
| `R=1e6` | 3.14155 | 4.584 | 0.687 | 0.00074 |
| `R=4e6` | **3.14159** | 4.530 | 0.632 | 0.00054 |

`M_1/R -> pi` exactly, and the exponents `0,1,3,7 = 2^{j-1}-1` are confirmed. (`M_2..M_4`
normalisations still drift downward — these are slowly-converging asymptotics with
lower-order terms — but the exponents are what the argument uses.) Matches `iso6`'s
independently-obtained values.

## 3.3 B6 cuts both ways — the round's one conceptual gain

`iso6` recorded B6 as an **upper-bound** barrier: *any argument robust at degree 2 cannot
prove better than `O(n^{4/3})`*. Round 3 shows the same theorem, read in the other
direction, also blocks the **lower-bound** route:

> **Relaxing the degree condition buys a larger ground set but destroys more logarithmic
> factors than it saves. The relaxation that removes the `log n` from the degree
> reintroduces it, doubly exponentially, in the size of the ground set.**

So B6 is not merely a constraint on proof techniques for the upper bound; it is a genuine
two-sided obstruction. That is the sharpest single statement this session produced.

## 3.4 Status after Round 3 — budget exhausted

| item | evidence | tier |
|---|---|---|
| (B) binds, not (A); effective slope count `~n^{1.37}` | `VERIFIED_COMPUTATIONAL_RESULT` | C |
| degree-`k` route `< n` for all `k`, and worse than `n/sqrt(log n)` | `VERIFIED_THEOREM` | **B** |
| moment exponents `2^{j-1}-1` re-verified from scratch | `VERIFIED_COMPUTATIONAL_RESULT` | C |
| B6 is a two-sided obstruction | `VERIFIED_THEOREM` | **B** |
| `C(n) = Omega(n)` | **NOT PROVED** | — |
| C002 existence for all `n` | **NOT PROVED, not falsified** | — |

**Rounds used: 3 of 3. Under rule §78b the campaign stops here with an honest zero on the
bound.** No candidate reached Judge PASS + Grade TYPE2.

## 3.5 What a future attempt would have to do

Every route examined across three rounds loses the same factor, and Round 3 shows the
obvious way of not losing it costs more than it saves. Concretely, a successful proof of
`C(n) = Omega(n)` must:

1. not pass to a bounded-degree ground set (3.2);
2. not use a first-moment or Local Lemma count (Round 1 §3, Round 2 §2.4);
3. not use the strengthening "all distances distinct" (Round 2 §2.1, capped at
   `O(n/(log n)^{1/4})`);
4. beat the mean multiplicity `M_2(R) ≍ R log R` directly, or run a bespoke greedy analysis
   valid at `Delta_2 ≍ D^{1/2}/sqrt(log n)` — i.e. **on** the Bennett–Bohman boundary
   rather than polynomially inside it.

Item 4 is the whole problem. Nothing in this campaign bears on it.

`NOVELTY_PRELIMINARY` throughout. Nothing here is a theorem about `C(n)`.
