# Round 10 — how `Gamma` actually enters Bennett–Bohman, and what that changes

**Headline: the two Bennett–Bohman hypotheses that `H_n` violates are violated only as
*pointwise maxima*. The proof consumes them as *edge-weighted averages*, and under that
weighting `H_n` satisfies both with a polynomial margin (`eps ~ 0.26`), not a logarithmic
one. The open obligation is therefore not "strengthen BB by one logarithm" but
"replace two pointwise stopping-time conditions by edge-averaged ones".**

Still not a theorem about `C(n)`. Round 10 is a relocation of the obstacle, plus the
measurement that decides whether the relocation is worth anything.

---

## 10.1 The question Rounds 3–9 kept deferring

Round 9 closed with a stated limitation: BB need `Gamma` small *for concentration*, and
the synthetic experiments measured only the mean of `|I|`. The checkpoint named the entry
point: read `lit/ind.tex` and find out whether `Gamma` enters via a union bound over pairs
(a vanishing bad fraction is then tolerable) or via a per-pair requirement (it is not).

Answer: **neither, exactly.** The structure is three-layered.

### Layer 1 — `Gamma` is an initial condition, not a hypothesis used directly

`ind.tex` line 690 defines, for a pair `v,v'`,

```
c_{a,a'->k}(v,v',i) = #{ (e,e') : v in e\e', v' in e'\e, |e|=a, |e'|=a', |e cap e'|=k,
                                  e,e' in H(i) }
```

At `i = 0` every edge still has size `r`, so `c_{r,r->r-1}(v,v',0)` is **exactly** the
`(r-1)`-codegree of `v,v'` — i.e. `Gamma(H)` is the maximum initial value of this one
variable. Line 849: *"We again proceed by induction, with the base case following
immediately from the condition on `Gamma(H)`."* That is the **only** role of the
hypothesis `Gamma < D^{1-eps}`.

### Layer 2 — the induction is diagonal in the pair

`c_{k+1,k+1->k}(v,v')` is driven by `c_{k+2,k+2->k+1}(v,v')`, `c_{k+2,k+1->k}(v,v')` and
`c_{k+1,k+2->k}(v,v')` — the *same* pair throughout (line 849). Each pair's chain is
self-contained. For `r = 3` the chain has two links:

```
Gamma(v,v') = c_{3,3->2}(v,v',0)   ->   c_{3,3->2}(v,v',i)   ->   c_{2,2->1}(v,v',i)
```

and BB's own parameters (line 768) fix the drop: `C_{3,3->2} = D^{1-eps+...}`,
`C_{2,2->1} = D^{1/2-eps+...}`, a factor `D^{-1/(r-1)}` per link — the process runs
`i_max = zeta N D^{-1/(r-1)} log^{1/(r-1)} N` steps, each converting with probability
`~1/N`. So heuristically `c_{2,2->1}(v,v') ~ Gamma(v,v') * D^{-1/2} * polylog`.

### Layer 3 — the consumer is a SUM over the edges at a vertex

`C_{2,2->1}` is used in exactly one place in the main proof: the drift of `d_l^-(v)`,
`ind.tex` lines 1015–1029. The text there is explicit — *"the number of `y` that are
counted more than once in the first sum is at most `binom(l-1,2) C_{2,2->1}`"* — so the
true error term is

```
    sum_{e in d_l(v)}  sum_{ {x,x'} subset e\{v} }  c_{2,2->1}(x,x')
```

against a main term `~ d_l(v) * (l-1) * d_2 ~ d_l(v) * D^{1/(r-1)}`. For `r=3` each edge
contributes exactly one pair. **So what the proof needs is not `max Gamma`; it is `Gamma`
averaged over pairs weighted by how many edges contain the pair.**

Define

```
    Gamma_edge  :=  sum_{x<y} codeg(x,y) * Gamma(x,y)  /  sum_{x<y} codeg(x,y),
    codeg(x,y)  =  #edges containing both x and y  ( = Delta_2 at that pair),
    sum_{x<y} codeg(x,y) = 3 * |E(H)| = N D / ... (r=3)
```

and likewise `Delta_2^edge := sum codeg^2 / sum codeg`.

**The pointwise hypothesis is not what is consumed. It is what makes the stopping time
`T` (line 720) well defined.** That distinction is the whole content of Round 10, and
§10.4 states the price.

## 10.2 The measurement — `experiments/r10_edgeg.c`

Risk identified *before* running: `Gamma`-bad pairs are mirror pairs (Round 1, Round 8),
which have long perpendicular bisectors, hence **large** codegree. So the edge measure
might be biased *toward* exactly the bad pairs, in which case averaging buys nothing.

For a sampled vertex `x`, one pass over `P(x) = { {u,w} : {x,u,w} in H_n }` yields
`Gamma(x,y) = |P(x) cap P(y)|` and `codeg(x,y)` for **every** `y` simultaneously.
20 sampled `x` for `n <= 128`, 8 for `n >= 160`, seed 7.

| `n` | `D` | `Gamma_unif` | `Gamma_edge` | `Gamma_edge/D` | `Gamma_max/D` | bias e/u | `D2_edge` | `D2_edge/sqrt D` | `D2_max/sqrt D` |
|---|---|---|---|---|---|---|---|---|---|
| 32 | 5 952 | 98.2 | 150.1 | 0.02521 | 0.10603 | 1.53 | 17.53 | 0.2272 | 0.6312 |
| 48 | 14 720 | 133.1 | 236.8 | 0.01609 | 0.08655 | 1.78 | 21.13 | 0.1741 | 0.5407 |
| 64 | 28 822 | 169.8 | 345.5 | 0.01199 | 0.07340 | 2.04 | 24.90 | 0.1467 | 0.4933 |
| 96 | 69 435 | 223.5 | 571.4 | 0.00823 | 0.06408 | 2.56 | 30.36 | 0.1152 | 0.4416 |
| 128 | 135 894 | 291.6 | 873.0 | 0.00642 | 0.05591 | 2.99 | 35.84 | 0.0972 | 0.4168 |
| 160 | 235 959 | 375.1 | 1 272.6 | 0.00539 | 0.05145 | 3.39 | 41.29 | 0.0850 | 0.3917 |
| 192 | 349 150 | 428.8 | 1 673.0 | 0.00479 | 0.05020 | 3.90 | 45.63 | 0.0772 | 0.3776 |
| 256 | 639 957 | 513.9 | 2 533.2 | 0.00396 | 0.04652 | 4.93 | 53.64 | 0.0671 | 0.3661 |

`D = 1.65–1.82 n^2 ln n` across the whole range, reproducing Round 6's `1.75` from an
independently written program.

### The predicted risk is real — and loses anyway

The edge measure **is** biased toward the bad pairs, and the bias grows polynomially:
`Gamma_edge / Gamma_unif = 1.53 -> 4.93`, which is `~0.27 sqrt(n)` (ratio to `sqrt n` is
0.270, 0.257, 0.255, 0.261, 0.264, 0.268, 0.281, 0.308 — flat to 8% over an 8-fold range;
against `ln n` it drifts by 100%). So mirror pairs really are over-represented in the edge
measure by `Theta(sqrt n)`. The uniform mean nevertheless falls fast enough that the
product still wins.

### The dichotomy — this is the result

Fitting each ratio as a power of `D` over the 107-fold range of `D`:

```
    Gamma_edge / D          ~  D^-0.396        =>  Gamma_edge   ~ D^{1 - 0.40}
    Delta_2^edge / sqrt(D)  ~  D^-0.261        =>  Delta_2^edge ~ D^{1/2 - 0.26}
```

whereas for the maxima the exponent is **zero up to logarithms**: `Gamma_max = Theta(n^2)`
by the explicit mirror-pair construction (Round 1/8) against `D = Theta(n^2 log n)`, so
`Gamma_max/D = Theta(1/log n)` exactly, and `Delta_2 = Theta(n) = Theta(sqrt(D)/sqrt(log D))`.

| BB hypothesis | as a pointwise max | as an edge-weighted average |
|---|---|---|
| `Gamma < D^{1-eps}` | `Theta(D/log D)` — fails for **every** fixed `eps` | `~ D^{0.60}` — holds with `eps ~ 0.40` |
| `Delta_2 < D^{1/2-eps}` | `Theta(D^{1/2}/sqrt(log D))` — fails for **every** fixed `eps` | `~ D^{0.24}` — holds with `eps ~ 0.26` |

Both averaged conditions hold simultaneously at `eps = 0.26`, and `D > N^eps` is trivially
satisfied (`D ~ N log N`). **The failure is entirely an artefact of taking a maximum over
pairs.** Under the weighting the proof's own drift computation applies, `H_n` is not near
the boundary — it is polynomially inside it.

Note the mechanism is not "bad pairs are rare so they wash out". Round 8 measured a
`Theta(1/n)` bad fraction and Round 9 showed that rarity is *forced* by
`sum_{v'} Gamma(v,v') <= D(Delta_2 - 1)`. Round 10 adds that the rarity survives the
adversarial re-weighting the proof actually imposes — despite a `sqrt(n)` bias against it.

## 10.3 Independent verification

`Gamma` is now computed by two independently written programs using different algorithms
(`r8_gdist.c`, lattice-vectors-by-norm CSR, samples random *pairs*; `r10_edgeg.c`, builds
`P(x)` exactly and enumerates completions, covers *all* partners of a sampled `x`).
At `n = 64`:

```
    r8_gdist  4000 random pairs        uniform-pair mean Gamma = 179.4
    r10_edgeg 100 x * all 4095 partners uniform-pair mean Gamma = 178.6
```

Agreement to 0.5%. `VERIFIED_COMPUTATIONAL_RESULT`.

## 10.4 The price — stated plainly

The averaged conditions are not a free substitution. `Gamma` and `Delta_2` do not enter
BB as inequalities that must merely be *true*; they enter through the **stopping time**
(line 720):

```
  T := min( i_max , first i at which any of (eq:points), (eq:vertexdegree),
            (eq:setdegree)  d_{A^b} <= D_{A^b}  for ALL A,
            (eq:codegree)   c_{a,a'->k}(v,v') <= C_{a,a'->k}  for ALL v,v'   fails )
```

If a single pair breaches its bound, `T` stops and the analysis ends — regardless of how
small the aggregate error is. So the obligation is:

> **Obligation R10.** Replace the pointwise conditions (eq:setdegree) and (eq:codegree) in
> the definition of `T` by vertex-aggregated ones, e.g.
> `sum_{e in d_l(v)} c_{2,2->1}(e\{v}) <= l * d_l(v) * D^{1/(r-1)-eps'}` for all `v`, and
> re-derive the supermartingale/Freedman estimates of lines 1015–1060 and 1147–1185 under
> the aggregated condition.

Is that genuinely easier than the original problem (§34)?

1. *What difficulty disappears:* the two hypotheses `H_n` violates. They are also the
   **only** hypotheses `H_n` violates apart from regularity (§10.5).
2. *What structure appears:* the edge-weighted statistics above, with `eps ~ 0.26` of room,
   plus Round 9's a priori identity `sum_{v'} Gamma(v,v') <= D(Delta_2-1)` as an initial
   condition for the aggregate.
3. *Hardest remaining obligation:* dynamic concentration for the aggregate
   `sum_{e in d_l(v)} c(e\{v})` — a sum of `~D` correlated variables — with failure
   probability `exp{-N^{Omega(1)}}`.
4. *Genuinely easier?* **Partly, and I will not claim more.** In its favour: the union
   bound shrinks from `N^2` pairs to `N` vertices, and the quantities have polynomial
   rather than logarithmic room. Against it: BB explicitly say of these variables (line
   695) *"We do not establish dynamic concentration for these variables, but we only need
   relatively crude upper bounds"* — so the proposed route asks for **more** than BB do of
   the `c` variables (concentration of a correlated sum) in exchange for asking **less** of
   the hypergraph. Whether that trade closes is not established here.

`BLOCKED` is the correct status for the route, not `PROGRESS` on `C(n)`.

## 10.5 The third gap, unchanged

`H_n` is **not** `D`-regular; Round 6 measured `Dmax/Davg ~ 1.47`. BB Thm 1.1 requires
`D`-regularity. Even granting Obligation R10 in full, the theorem does not apply verbatim.
Bounded-ratio almost-regularity is the most likely of the three gaps to be routine (add
dummy edges, or restrict to a sub-region), but it has **not** been checked in this
campaign and must not be waved through.

So the ledger of what separates `H_n` from a linear lower bound via BB Thm 1.1 is:

| gap | status after Round 10 |
|---|---|
| `Gamma < D^{1-eps}` pointwise | fails; **holds on average with `eps ~ 0.40`** |
| `Delta_2 < D^{1/2-eps}` pointwise | fails; **holds on average with `eps ~ 0.26`** |
| `D`-regularity | fails (`Dmax/Davg ~ 1.47`); unexamined |

## 10.6 Status

| item | evidence | tier |
|---|---|---|
| `Gamma` enters BB only as the `i=0` value of `c_{r,r->r-1}`, per pair, via the stopping time | `VERIFIED` (source reading, `lit/ind.tex` 690/720/768/849/1017) | B |
| the consumer is an edge-weighted sum, not a max | `VERIFIED` (`lit/ind.tex` 1015–1029) | B |
| `Gamma_edge ~ D^{0.60}`, `Delta_2^edge ~ D^{0.24}` for `H_n` | `VERIFIED_COMPUTATIONAL_RESULT` (`n` = 32..256) | C |
| edge measure is biased `~0.27 sqrt(n)` toward bad pairs, and averaging wins anyway | `VERIFIED_COMPUTATIONAL_RESULT` | C |
| `Gamma` cross-validated between two independent programs to 0.5% | `VERIFIED_COMPUTATIONAL_RESULT` | C |
| Obligation R10 closes | **NOT ESTABLISHED** | — |
| `C(n) = Omega(n)` | **NOT PROVED** | — |

Judge PASS 0 · TYPE2 0. **Tenth consecutive honest zero on the bound.**

`NOVELTY_PRELIMINARY`. The observation that BB's `Gamma`/`Delta_2` conditions are
consumed as averages is a reading of a published proof, not a new theorem; whether it has
been made before has not been searched.
