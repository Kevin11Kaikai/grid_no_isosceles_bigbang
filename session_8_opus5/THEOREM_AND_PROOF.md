# Theorem and proof — Session 8

Notation and process as in `THEOREM_CONTRACT.md`. Throughout, `r = 3`, `N = n^2`,
`L := ln n`, and `c, C, C_1, ...` are absolute positive constants. All references
"ind.tex line k" are to the arXiv LaTeX source of **arXiv:1308.3732**
(Bennett–Bohman, *A note on the random greedy independent set algorithm*), retrievable
with `arxiv.org/e-print/1308.3732`.

---

## Part I. Where pointwise pair control actually enters, for `r = 3`

This is a complete audit of the primary source, not a paraphrase of it.

### 1.1 The four stopping-time conditions at `r = 3`

**(S) `d_{A up b} <= D_{a up b}` for `2 <= a < b <= r`.** At `r = 3` the only instance is
`(a,b) = (2,3)`, and `b = r`, which is the base case of Lemma `dlemma` (ind.tex line 782):
it "follows immediately from the condition on `Delta_a(H)`". Moreover
`d_{{v,y} up 3}(i)` counts size-3 edges of `H(i)`, and edges of `H(i)` of size 3 are
exactly the edges of `H_n` none of whose vertices has been chosen. Hence

> **(1.1)** `d_{{v,y} up 3}(i)` is non-increasing in `i`, so (S) holds **deterministically
> for all `i`** as soon as `Delta_2(H_n) <= D_{2 up 3}`. There is no induction, no
> martingale, and no union bound at `r = 3`.

**(C) `c_{a,a'->k}(v,v') <= C_{a,a'->k}`.** Lemma `clemma` (ind.tex line 845) reduces every
case with `a' > k+1` to `dlemma`. The remaining cases are `a = a' = k+1`, i.e. `(3,3->2)`
and `(2,2->1)`.
- `c_{3,3->2}(v,v',i)` counts pairs of **size-3** edges; by the same monotonicity as (1.1)
  it is non-increasing, so it too is deterministic given `Gamma(H_n) <= C_{3,3->2}`.
- `c_{2,2->1}(v,v',i)` **can increase** and is the unique genuinely dynamic pair condition
  at `r = 3`. It is handled by the Freedman application at ind.tex lines 853–880.

> **(1.2)** At `r = 3`, of the two pair-quantified stopping conditions, three of the four
> relevant instances are deterministic consequences of static hypotheses on `H_n`, and only
> `c_{2,2->1}` requires a dynamic argument.

*(This corrects the framing carried in earlier sessions of this repository, which treated
`Delta_2` and `Gamma` as quantities requiring dynamic control. They do not; they are
initial conditions for monotone quantities. What requires dynamic control is `d_2(v)`.)*

**(V) `d_l^± (v) ∈ s_l^± ± D^{(l-1)/2-δ} f_l` for all `v ∈ V(i)`, `l = 2,3`.** This is the
condition that carries the whole difficulty, and §1.2 isolates which half.

### 1.2 Which uses of `d_2` are pointwise and which are averages

Every appearance of `d_2` in the proof of BB's Theorem 1.1:

| site | ind.tex | form | quantifier |
|---|---|---|---|
| drift of `Z_V` | 960 | `(1/\|V(i)\|) * sum_{v ∈ V(i)} (d_2(v)+1)` | **global average** |
| step of `Z_V` | 1163 | `ΔV = -1 - d_2(y_i)` for the **chosen** `y_i` | pointwise, but only a step size |
| drift of `Z_l^-` | 1018 | `Sigma_l(v) = sum_{e ∈ d_l(v)} sum_{u ∈ e\{v}} d_2(u)` | **local average over `Theta(d_l(v))` vertices** |
| drift error | 1018 | `O( d_l * [ C_{2,2->1} + sum_k D_{k up k+1} ] )` | pair maxima |
| step of `Z_l^+` | 1172 | `ΔZ_l^+(v) < D_{2 up l+1}`, i.e. `<= codeg(v, y_i)` | pointwise, step size |
| step of `Z_l^-` | 1180 | `ΔZ_l^-(v) < O( sum_k C_{l,k+1->k} )` | pointwise, step size |

> **(1.3)** `d_2(v)` is never consumed pointwise at `o(1)` relative accuracy. It is consumed
> as a global average (row 1), as a local average over `Theta(d_l(v))` vertices (row 3), and
> as a crude cap on a step size (rows 2, 5, 6). The **only** reason the pointwise condition
> (V) with `l = 2` appears in BB's stopping time is that it is the natural way to supply
> rows 1 and 3; it is stronger than either needs.

Rows 5 and 6 are where the pair statistic is genuinely worst-case. Row 5 for `l = 2` is the
critical one:

```
Delta Z_2^+(v)  <=  codeg(v, y_i),      y_i uniform on V(i).
```

The step size is the codegree at a **uniformly chosen** partner. That is the entire reason
an averaged or tail-based replacement is conceivable at all.

---

## Part II. The arithmetic of `H_n`

### Lemma 1 (structure of the increment law)

Let `v ∈ [n]^2` and write `codeg(v,y) = d_{{v,y} up 3}(0)`.

**(a)** `codeg(v,y) <= 2 r_2(|vy|^2) + L(v,y)`, where `r_2(d)` is the number of lattice
points at squared distance `d` from a point and `L(v,y)` is the number of points of `[n]^2`
on the perpendicular bisector of `v,y`. Consequently
`Delta_2(H_n) <= n + 2 max_{d <= 2n^2} r_2(d) = n + n^{o(1)}`.

**(b) (fat top).** Let `A_v := { (v_1, v_2 + 2k) ∈ [n]^2 : k ≠ 0 }`. Then
`|A_v| >= floor((n-1)/2)` and `codeg(v,y) >= n - 1` for every `y ∈ A_v`.
Hence `Delta_2(H_n) >= n-1`, so `Delta_2(H_n) = n(1 + o(1))`.
Moreover the sets `{ x : {v,x,y} ∈ H_n }`, for distinct `y ∈ A_v`, are **pairwise disjoint**.

**(c) (Pareto tail).** For every `v` and every `tau >= 4`,
`B_v(tau) := #{ y : codeg(v,y) > tau } <= C_0 n^2 (log n) / tau`.

**(d) (degree).** `D := D(H_n) = Theta(n^2 log n)`; in particular `D <= C_1 n^2 log n`, so
`D^{1/2} / Delta_2 = Theta( sqrt(log n) )`.

**Proof.**

**(a)** Let `x` complete `{v,y}` to an edge. The apex is `v`, `y`, or `x`. Apex `v` forces
`|vx|^2 = |vy|^2`, so at most `r_2(|vy|^2)` choices; apex `y` likewise. Apex `x` forces `x`
on the perpendicular bisector of `v,y`. A line meets `[n]^2` in at most `n` points (a
non-horizontal line meets each of the `n` rows at most once; a horizontal line meets it in
exactly `n`). Finally `r_2(d) = d^{o(1)}` is classical.

**(b)** For `y = (v_1, v_2+2k)` the perpendicular bisector of `v,y` is the horizontal line
`x_2 = v_2 + k`, which contains all `n` points `(j, v_2+k)`, `j ∈ [n]`. Each such `x` other
than the midpoint `(v_1, v_2+k)` is not collinear with `v,y` (it has a different first
coordinate), so `{v,y,x}` is a nondegenerate isosceles triple with apex `x`. That gives
`n-1` choices. The count of admissible `k ≠ 0` with `v_2 + 2k ∈ [0,n)` is at least
`floor((n-1)/2)`. Distinct `y ∈ A_v` give distinct values of `k`, hence distinct horizontal
lines, hence disjoint sets of `x`. ∎(b)

**(c)** If `codeg(v,y) > tau` then either `2 r_2(|vy|^2) > tau/2` or `L(v,y) > tau/2`.

*Lines.* Write `y - v = g·(a,b)` with `gcd(a,b) = 1`, `g >= 1`. The perpendicular bisector
of `v,y` is a line of primitive direction `(-b,a)`, so consecutive lattice points on it are
at Euclidean distance `sqrt(a^2+b^2) >= s`, where `s := max(|a|,|b|)`. Its intersection with
`[n]^2` has diameter at most `sqrt(2) n`, so `L(v,y) <= 1 + sqrt(2) n / s`. Thus
`L(v,y) > tau/2` forces `s <= 4 sqrt(2) n / tau =: K` (for `tau >= 4`). For a fixed primitive
`(a,b)` with `max(|a|,|b|) = s`, the number of `y = v + g(a,b)` lying in `[n]^2` is at most
`2n/s`; and the number of primitive `(a,b)` with `max(|a|,|b|) = s` is at most `8s`. Hence
```
#{ y : L(v,y) > tau/2 }  <=  sum_{s=1}^{K} 8s · (2n/s)  =  16 n K  <=  91 n^2 / tau.
```

*Representation function.* By Markov and `sum_{y ∈ [n]^2} r_2(|vy|^2) <= sum_{d <= 2n^2} r_2(d)^2
= O(n^2 log n)` (the classical estimate `sum_{d<=X} r_2(d)^2 ≍ X log X`),
`#{ y : 2 r_2(|vy|^2) > tau/2 } <= (4/tau) · sum_y 2 r_2(|vy|^2) = O(n^2 log n / tau)`.

Adding the two gives (c). ∎(c)

**(d)** `sum_{y} codeg(v,y) = 2 D` (each edge `{v,y,x}` is counted once at `y` and once at
`x`). The upper bound follows by summing (a): the `r_2` part is `O(n^2 log n)` as above, and
```
sum_y L(v,y) <= n^2 + sqrt(2) n · sum_{s <= n} 8s · (2n/s) / s = n^2 + O(n^2 · sum_{s<=n} 1/s)
             = O(n^2 log n).
```
The lower bound `D = Omega(n^2 log n)` follows from the matching count of lattice points on
bisectors of primitive direction of each size `s <= n` (for each `s` a positive proportion of
the primitive directions and offsets give a bisector containing `>= c n / s` lattice points,
and there are `>= c s · n/s = c n` such `y` per scale `s`, contributing `>= c n^2 / s`;
summing `1/s` over `s <= n` gives the logarithm). Combining with (b),
`D^{1/2}/Delta_2 = Theta(sqrt(n^2 log n)/n) = Theta(sqrt(log n))`. ∎

**Measured (`experiments/s8_tail.c`, `n = 64..512`, exact computation).** `Delta_2/n` =
1.297, 1.211, 1.137, 1.127 — consistent with `n(1+o(1))`. `2D/N` = 17.5, 20.8, 24.1, 27.4,
i.e. `≈ 4.75 ln n - 2.3`. `max_tau B_v(tau)·tau/n^2` = 7.0, 8.4, 9.4, 10.2, within the
constant `C_0` of (c). *(Measurement, not evidence for the asymptotics.)*

### 1.4 What Lemma 1 says qualitatively

The one-step increment `X = codeg(v, y)` for uniform `y` has

```
mean  =  2D/N  =  Theta(log n),        P[X > tau] = O(log n / tau),        max  =  n(1+o(1)).
```

The mean is logarithmic **because** the tail is Pareto of index 1 truncated at `n`: the
`log n` in `D` is the harmonic sum `sum_{s<=n} 1/s` over the scales `s` of primitive
directions. `D ≍ n^2 log n` and `Delta_2 ≍ n` are therefore not two independent facts about
the grid — they are the same fact, and `D^{1/2}/Delta_2 = Theta(sqrt(log n))` is forced.

---

## Part III. The barrier

Fix a horizon `m` and write `t = t(m) = D^{1/2} m / N`, `q(t) = e^{-t^2}`,
`s_2^+(t) = 2 D^{1/2} ∫_0^t e^{-u^2} du`. Recall `s_2^+` is non-decreasing and
`s_2^+(t) <= sqrt(pi) D^{1/2}` for all `t`.

**Hypothesis (H-surv).** There is `c_0 > 0` such that for all `v ∈ [n]^2` and all `i <= m`:
(i) `|A_v ∩ V(i)| >= c_0 |A_v|` whenever `q(t_i) >= 1/2`; and
(ii) for `y ∈ A_v ∩ V(i)` with `q(t_i) >= 1/2`, at least `c_0 (n-1)` of the `n-1` points `x`
of Lemma 1(b) still lie in `V(i)` with `{v,x,y} ∈ H(i)`.

*(H-surv) says only that a fixed set of `Theta(n)` vertices, and a fixed line of `n`
vertices, retain a constant fraction while a constant fraction of the whole grid survives.
It is weaker than the vertex-count condition (P) that BB's own stopping time enforces, but
it is not formally implied by it; it is registered as the one unproved input. Measured
value of `|A_v ∩ V(i)| / (q |A_v|)` at the centre vertex: 0.27, 0.25, 0.94/0.70/1.27
(`experiments/s8_proc.c`, `n = 64,128,256`).*

### Theorem 2 (log-deficit barrier for pointwise control of `d_2`)

Assume (H-surv). Let `t_0 > 0` be any constant and suppose the horizon satisfies
`t_0 <= t <= 1`. Let `tol` be any **admissible** tolerance, i.e. `tol <= sigma · s_2^+(t)`
with `sigma = sigma(n) = o(1)`. Then for every `v ∈ [n]^2`,

```
   -log P[ d_2^+(v,m) > s_2^+(t) + tol ]   <=   C_2 · sigma · sqrt(log n) · log log n
                                            =   o( log N ).                       (*)
```

Consequently

```
   E[ # { v ∈ V(m) : d_2^+(v,m) > s_2^+ + tol } ]   >=   N^{1 - o(1)},
```

and **no union bound over the `N` vertices can establish condition (V) for `l = 2`**, for
any choice of concentration inequality whatsoever. The achievable exponent falls short of
`log N` by a factor `Omega( sqrt(log n) / (sigma · log log n) )`.

**Proof.**

*Reduction to the largest admissible tolerance.* The event `{d_2^+ > s_2^+ + tol}` is
decreasing in `tol`, so it suffices to prove (*) for the largest tolerance in question; and
for smaller ones the bound only improves. We may therefore assume
`sigma >= (log n)^{-1/4}` (if the given `sigma` is smaller, apply the theorem with
`sigma = (log n)^{-1/4}`; a violation at the larger tolerance is a violation at the smaller).

*The number of exceptional steps needed.* The violation must be an **excess over the
trajectory**, not the trajectory itself: `E[d_2^+(v,m)] = s_2^+(t)(1+o(1))` by construction,
and that mean is produced by the bulk of the increments, whose common value is
`E[codeg(v,y)] = 2D/N = Theta(log n)` (Lemma 1(d)). What must be manufactured is only the
excess `tol`. So set

```
   g  :=  ceil( 2 tol / (c_0 (n-1)) ).                                               (2.1)
```

The tolerance floor in BB's schedule is `tol(0) = D^{1/2-δ}` (ind.tex line 908: `f_l(0)=1`),
and the relative accuracy at the horizon is `D^{-δ} f_2(t) / (2Q(t))` with `Q(t)=∫_0^t q`.
Admissibility forces this to be `o(1)`, hence `D^{-δ} = o(1)`; and since `f_2 >= 1` and
`2Q <= sqrt(pi)`, we get `D^{-δ} <= sqrt(pi) sigma`. The binding time is `t = Theta(1)`,
where `tol` is at its floor and the jump size at its ceiling. Hence by Lemma 1(d)

```
   g  <=  2 D^{1/2-δ} / (c_0(n-1)) + 1  <=  C_3 · sigma · sqrt(log n).               (2.1')
```

*Hazard of an exceptional step.* Call step `i` a **hit** if `y_i ∈ A_v ∩ V(i)`. Conditional
on `F_i` the choice is uniform on `V(i)`, so `P[hit at i | F_i] = |A_v ∩ V(i)| / |V(i)|`.
For `t <= 1` we have `q(t_i) >= e^{-1}`, so (after absorbing `e^{-1}` into `c_0`) hypothesis
(H-surv)(i) applies at every step `i <= m`; with the trivial `|V(i)| <= N` this gives
`P[hit at i | F_i] >= p := c_0 (n-1)/(2n^2) >= c_0/(3n)`. Hence the number `J` of hits
stochastically dominates `Bin(m,p)`, with

```
   mu := m p  >=  c_0 m/(3n)  =  c_0 t N/(3 n D^{1/2})  >=  c_0 t / (3 C_1^{1/2} sqrt(log n)).  (2.2)
```

*Hits produce the excess.* By Lemma 1(b) the sets `{x : {v,x,y} ∈ H_n}` for distinct
`y ∈ A_v` are pairwise disjoint, and by (H-surv)(ii) at least `c_0(n-1)` members of each
survive as created size-2 edges. So `J >= g` contributes at least `g c_0 (n-1) >= 2 tol` to
`d_2^+(v,m)` over and above what the non-hit steps contribute.

*The bulk does not cancel it.* Let `S` be the contribution of the non-hit steps. By
Lemma 1(c) and the layer-cake formula,
```
   sum_y codeg(v,y)^2 = 2∫_0^{n(1+o(1))} u B_v(u) du
                     <= 2∫_0^{log n} u N du + 2∫_{log n}^{n(1+o(1))} u · C_0 N (log n)/u du
                      = O(N n log n),
```
so `E[X^2] = O(n log n)` for one increment `X`, and
`Var(S) <= m E[X^2] = O((n/sqrt(log n)) · n log n) = O(n^2 sqrt(log n))`, i.e.
`sd(S) = O(n (log n)^{1/4})`. Conditioning on the positions of the hit steps removes at most
`g` steps from the bulk, changing its mean by `O(g log n) = o(tol)`. Since
`tol = sigma s_2^+ = Theta(sigma n sqrt(log n))`,
```
   sd(S) / tol  =  O( (log n)^{1/4} / (sigma sqrt(log n)) )  =  O( 1 / (sigma (log n)^{1/4}) ),
```
which is at most `1/2` precisely because `sigma >= (log n)^{-1/4}` — the reduction made at
the start. Chebyshev then gives `P[ S >= E[S] - tol/2 | hit positions ] >= 1/2`. Therefore

```
   P[ d_2^+(v,m) > s_2^+ + tol ]  >=  (1/2) · P[ Bin(m,p) >= g ]
                                  >=  (1/2) · binom(m,g) p^g (1-p)^m
                                  >=  (1/(2e)) · (mu/g)^g e^{-mu - g^2/m}.
```

Taking logarithms, with `g = O(sqrt(log n))` and `m = Theta(n/sqrt(log n))` so `g^2/m = o(1)`,

```
   -log P  <=  g · log(g/mu)  +  mu  +  O(1).                                        (2.3)
```

By (2.1') and (2.2), and using `sigma <= 1`,

```
   g / mu  <=  C_3 sigma sqrt(log n) · 3 C_1^{1/2} sqrt(log n) / (c_0 t)  <=  C_4 log n / t,   (2.4)
```

and `mu = O(t/sqrt(log n)) = O(1)`. Substituting (2.1') and (2.4) into (2.3), with
`t ∈ [t_0, 1]`,

```
   -log P  <=  C_3 sigma sqrt(log n) · log(C_4 log n / t_0)  +  O(1)
            =  C_2 · sigma · sqrt(log n) · log log n,
```

which is (*). Since `log N = 2 log n` and `sigma = o(1)`, the right-hand side is `o(log N)`,
so `P >= N^{-o(1)}`. Summing over the `N` vertices (and using (H-surv) to keep a constant
fraction in `V(m)`) gives `E[#violating] >= N^{1-o(1)}`.

For the union-bound consequence: if (V) with `l = 2` were established by a union bound we
would need `P[v violates] <= N^{-1-c}`, i.e. `-log P >= (1+c) log N`, contradicting (*). ∎

**Remark 2.0 (why `t <= 1` is not a restriction).** The tolerance schedule has its *floor*
at `t = 0` (`tol(0) = D^{1/2-δ}`, growing thereafter by `f_2`) while the jump size
`Theta(q(t) n)` has its *ceiling* at `t = 0`. The ratio `g(t) = tol(t)/(c_0 q(t) n)` is
therefore minimised early, so the constraint binds at `t = Theta(1)` regardless of the
intended horizon. A violation before time `t_0` stops the process there, so Theorem 2 rules
out **every** horizon `m >= t_0 N / D^{1/2} = Theta(n/sqrt(log n))`, not only short ones.

### Corollary 2.1 (the condition is false, not merely unproved)

Under (H-surv), for any horizon with `t >= t_0` and any admissible tolerance, the expected
number of vertices violating (V) for `l = 2` is `N^{1-o(1)}`. In particular BB's stopping
time satisfies `P[T >= m] = o(1)` whenever the other three conditions hold with probability
`1-o(1)`; the four conditions of ind.tex line 720 are **jointly unsatisfiable for `H_n`** at
any horizon `m = Omega(n / sqrt(log n))`.

### Remark 2.2 (why the deficit is exactly one logarithm)

The two sides of (*) are

```
   budget in jump units      g   ≍  sigma · D^{1/2}/Delta_2  =  sigma · sqrt(log n)
   union-bound requirement   g · log(g/mu)  >=  log N        =  2 log n
```

and `log(g/mu) = Theta(log log n)` by (2.4). The deficit is `sqrt(log n)/log log n`, and its
source is precisely the identity `D^{1/2}/Delta_2 = Theta(sqrt(log n))` of Lemma 1(d) — the
same `sqrt(log n)` that separates the known bound `n/sqrt(log n)` from the conjectured `n`.
**The missing factor in the lower bound and the missing factor in the union bound are the
same quantity.**

### Empirical confirmation of the mechanism

`experiments/s8_proc.c` runs the actual process and measures `d_2^+(v,m)` for all `v`.
Theorem 2 predicts `max_v d_2^+ - mean_v d_2^+ ≈ g* · n` where `g*` solves
`g log g = log N`, i.e. `g* ≈ 2 log n / log log n`.

| `n` | `alpha = m/n` | max/mean | `(max-mean)/n` | `g* = 2 ln n / ln ln n` |
|---|---|---|---|---|
| 64  | 0.50 | 1.83 | 4.70 | 5.84 |
| 128 | 0.50 | 1.82 | 5.56 | 6.14 |
| 256 | 0.50 | 1.90 | 6.74 / 7.14 / 6.76 (3 seeds) | 6.47 |
| 256 | 0.25 | 2.20 | 4.70 | — |
| 256 | 0.75 | 1.78 | 8.53 | — |
| 256 | 1.00 | 1.73 | 10.34 | — |

The excess is `Theta(n)` times the predicted number of exceptional steps, and `max/mean`
is a **large constant** (≈1.8–2.2) rather than `1+o(1)`. *(Sanity check on the mechanism;
the theorem is proved above, not inferred from this table.)*

---

## Part IV. What survives, and the averaged replacement

Theorem 2 kills the pointwise route. §1.2 says which route is left: since `d_2` is consumed
only through averages, drop the per-vertex tracking of `d_2` entirely.

### Proposition 3 (the three surviving obligations)

At `r = 3`, replacing (V) for `l = 2` by (A0)+(A1)+(A2) of the contract leaves exactly the
following to be checked. Each is analysed below; two are settled, one is not.

**(3a) The crude cap (A0) is available, with room.** `d_2(v) >= K s_2^+` requires
`>= K s_2^+/Delta_2 = Theta(K sqrt(log n))` exceptional steps at `v`. Taking
`K = log^{1/2} n`, this is `g = Theta(log n)` steps, and by (2.3)–(2.4)
`-log P >= g log(g/mu) - O(1) = Omega(log n · log log n) >> log N`. So

```
   max_{v ∈ V(i)}  d_2(v)  <=  s_2^+(t) · log^{1/2} n     for all i <= m,  whp.
```

This is all that the step size of `Z_V` needs: with `|ΔZ_V| = O(s_2 log^{1/2} n)`, and using
the deterministic identity `sum_{i<m} d_2(y_i) = N - |V(m)| - m <= N`, the symmetric Azuma
bound (ind.tex line 1147) applied to `Z_V` gives failure probability
`exp( - Omega( N D^{-2δ} / (s_2 log^{1/2} n) ) ) = exp( - Omega( n^{1-o(1)} ) )`,
which is `exp(-N^{Omega(1)})` with enormous room. **The vertex-count condition (P) is not
affected by the barrier.** `[PROVED]`

**(3b) The neighbourhood average (A2) concentrates, with room.** Write
`e(u) := (d_2(u) - s_2)_+`. By Lemma 1(b) and the disjointness there, `e(u) <= J_u · n(1+o(1))`
where `J_u` is the number of exceptional steps at `u`, and `E[J_u] = mu = O(1/sqrt(log n))`
by (2.2). Hence for each `v` and `l ∈ {2,3}`,

```
   E[ Sigma_l(v) ] - (l-1) d_l(v) s_2   <=  (l-1) d_l(v) · n · mu  =  O( d_l(v) · n / sqrt(log n) ),
```
to be compared with the permitted `(l-1) d_l(v) · tol = Theta( d_l(v) · sigma n sqrt(log n) )`.
The ratio is `O( 1/(sigma log n) )`, so (A2) holds in expectation whenever
`sigma >> 1/log n` — an enormous margin. For concentration, `Sigma_l(v)/((l-1)d_l(v))` is an
average of `Theta(d_l(v))` terms, with `d_2(v) = Theta(n sqrt(log n))` and
`d_3(v) = Theta(n^2 log n)`; a Chernoff bound on `sum_u J_u` over that many nearly
independent contributions gives failure probability `exp(-Omega(mu d_l(v))) = exp(-Omega(n))`,
far below `N^{-1}`. **The union bound over vertices is affordable here** — this is the exact
point at which averaging buys what pointwise control cannot. `[PROVED modulo the
independence audit noted in HANDOFF.md]`

**(3c) The global average (A1) and the drift of `Z_l^-`.** This is the obligation that does
**not** close in this session. Two distinct things are needed:

1. *(A1) as a martingale.* `sum_{v ∈ V(i)} d_2(v)` is a single scalar; its one-step change is
   `O(D)` and its scale is `|V| s_2 = Theta(n^3 sqrt(log n))`, so its budget in step units is
   `Theta(sigma n / log n)` — vast. Concentration is not the difficulty.
2. *(the real gap)* The drift of `Z_l^-(v)` is `Sigma_l(v)/|V|`, and (A2) controls
   `Sigma_l(v)` **relative to `s_2`** only if the `u` summed over are typical for `v`. What
   must be shown is a **quasirandomness statement about `H_n`**: that the neighbourhood of
   `v` in the evolving 2-graph does not systematically over-sample the vertices `u` whose
   `d_2(u)` is large. Those `u` are exactly the ones lying on short-primitive-direction lines
   through recently chosen vertices — and `v`'s own `d_2`-neighbours are produced by the same
   lines. **The correlation is real and its sign is not determined by anything proved here.**

> **This is the single remaining proof obligation.** It is stated precisely in `HANDOFF.md`.

### What Proposition 3 does and does not give

It does **not** give `C(n) = Omega(n)`. It reduces the problem from "prove a false pointwise
statement" to "prove one quasirandomness statement about the co-evolution of `v`'s 2-neighbourhood
and the exceptional set", and it certifies that the other components (the vertex count, the
crude cap, the neighbourhood averages, the three monotone pair conditions of (1.1)–(1.2)) are
all available with large margins. No new bound on `C(n)` follows until (3c) is settled.
