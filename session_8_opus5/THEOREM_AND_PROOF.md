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

---

## Part V. The correlation obligation

Part IV left one obligation (Q): the exceptional vertices and the vertices summed over in
`Sigma_l(v)` are generated by the same short-primitive-direction lines, and the sign of that
dependence was undetermined. This part settles it.

### 5.0 Reduction of (Q) to a single deterministic lattice sum

Write `e(u,i) := d_2(u,i) - s_2(t_i)` and define the **master statistic**

```
   W_l(v,i) := Sigma_l(v,i) - (l-1) d_l(v,i) s_2(t_i)  =  sum_u  m_v(u) · e(u,i),
```
where `m_v(u) := #{ e in d_l(v) : u in e }`. For `l = 3`, `m_v(u) = codeg_{H(i)}(v,u)`; for
`l = 2`, `m_v(u) = 1[u ~_2 v]`. Condition (A2) is exactly `|W_l(v,i)| <= (l-1) d_l(v) tol`.

`W_l` is, up to a drift term, a martingale in `i`. When `y` is chosen,
`Delta e(u) = codeg(u,y) - E[codeg(u,y)] + (lower order)`, so for `l = 3` the one-step
increment is

```
   Delta W_3(v,i) = A_i(v,y) - E_y[A_i(v,·)],   A_i(v,y) := sum_u codeg_{H(i)}(v,u)·codeg_{H(i)}(u,y).
```

**Everything about (Q) for `l = 3` is therefore controlled by the deterministic quantity
`A(v,y)`** — a two-step, codegree-weighted path count in the grid. `A` is exactly the joint
statistic the obligation asked for.

### 5.1 The clustering is real, and it is of the maximal possible kind

**Counterexample to negative association.** Take `v = (0,0)` and `y = (2,0)`. For every
`u = (2k,0)` on the `x`-axis: the perpendicular bisector of `v,u` is the vertical line
`x = k`, containing `n` lattice points, so `codeg(v,u) >= n-1`; the perpendicular bisector of
`u,y` is the vertical line `x = k+1`, so `codeg(u,y) >= n-1`. There are at least `(n-1)/2`
such `u`. Hence

```
   A(v,y) >= ((n-1)/2)·(n-1)^2 = Theta(n^3),     while   E_y[A(v,·)] = Theta(n^2 log^2 n).
```

So **one** chosen vertex simultaneously delivers a `Theta(n)` jump to `Theta(n)` vertices `u`,
*all of which are among the most heavily weighted in `v`'s neighbourhood.* The exceptional
vertices and `v`'s neighbours are **positively clustered**; they are **not** negatively
associated; and the clustering is maximal in kind, since a single step moves `Theta(n)`
coordinates of the sum coherently. Any argument assuming independence or negative association
of `{e(u)}` is false for `H_n`.

*(Measured: `max_y |A - E_y A| / n^3` = 2.264, 2.154, 2.189 at `n = 32, 48, 64` — flat, so
`Theta(n^3)` is the right order with constant about 2.2. `experiments/s8_joint.c`.)*

### 5.2 But the clustering is bounded — one logarithm below the trivial bound

The trivial bound is `A(v,y) <= Delta_2 · sum_u codeg(v,u) = Delta_2 · 2D = O(n^3 log n)`.
That is **not** good enough (§5.3). The following says the truth is a full logarithm smaller,
uniformly in `y`.

> **Lemma D.** There is an absolute constant `C` such that for all `n` and all `v != y` in
> `[n]^2`,
> ```
>        A(v,y) = sum_{u in [n]^2} codeg(v,u)·codeg(u,y)  <=  C n^3.
> ```

**Proof.** Write `s(a,b)` for the sup-norm of the primitive direction of `b - a`. By
Lemma 1(a) and its proof, `codeg(a,b) <= 2 r_2(|ab|^2) + L(a,b)` and
`L(a,b) <= 1 + sqrt(2)·n/s(a,b)`, so `codeg(a,b) <= R + sqrt(2) n/s(a,b)` with
`R := 1 + 2 max_{d <= 2n^2} r_2(d) = n^{o(1)}`.

The counting step of Lemma 1(c) gives, for every `v`,
```
   #{ u in [n]^2 : s(v,u) = s }  <=  8s · (2n/s)  =  16 n                     (*)
```
— at most `8s` primitive directions of sup-norm `s`, and at most `2n/s` multiples of each
staying inside `[n]^2`. Note that (*) is **uniform in `s`**. It has two consequences, one
divergent and one **convergent**:
```
   sum_u 1/s(v,u)    <=  sum_{s<=n} 16n/s    =  O(n log n),
   sum_u 1/s(v,u)^2  <=  sum_{s>=1} 16n/s^2  =  16n·pi^2/6  <  27 n.          (**)
```
Expand `A(v,y) <= sum_u (R + sqrt(2)n/s(v,u))·(R + sqrt(2)n/s(u,y))` into four sums. The
three containing a factor `R` total `O(R^2 n^2) + O(R·n·n log n) = n^{2+o(1)}`. The remaining
sum is handled by **Cauchy–Schwarz against (**)**:
```
   2n^2 · sum_u 1/( s(v,u)·s(u,y) )
        <=  2n^2 ( sum_u s(v,u)^{-2} )^{1/2} ( sum_u s(u,y)^{-2} )^{1/2}
        <=  2n^2 · 27n  =  54 n^3.
```
Hence `A(v,y) <= 54 n^3 + n^{2+o(1)}`. ∎

**The mechanism, stated plainly.** The naive bound multiplies two harmonic sums
`sum_u 1/s`, each of which *diverges* logarithmically: it loses `log n` twice and recovers it
only once. Cauchy–Schwarz instead pairs the two divergent sums into a single sum
`sum_u 1/s^2`, which **converges** because (*) is uniform in `s`. The saving is exactly one
logarithm, and §5.3 shows one logarithm is exactly what is needed.

*(Measured: `E_y A/(n^2 log^2 n)` = 11.61, 12.17, 12.46 and `max_y A/n^3` = 6.62, 5.95, 5.56 at
`n = 32,48,64` — consistent with `A = Theta(n^2 log^2 n) + O(n^3)`, the constant `C = 54`
being loose by a factor of roughly 25.)*

### 5.3 Lemma C: the `l = 3` neighbourhood average is controllable

> **Lemma C.** Assume the crude cap (Prop 3(3a)) and Lemma D, and let `tol = sigma·s_2` with
> `sigma >= C'(log n)^{-1/4}`. Then for every `v` and every `i <= m`,
> ```
>    |W_3(v,i)| <= 2 d_3(v,i)·tol   with probability  1 - exp(-Omega( sigma^2 (log n)^{3/2} )),
> ```
> and that failure probability is at most `N^{-1-c}`, so the union bound over the `N` vertices
> is affordable.

**Proof.** Apply Freedman (ind.tex line 797) to the martingale part of `W_3(v,·)`.

*Deviation budget.* `d := 2 d_3(v)·tol`. With `d_3(v) = Theta(D q^2) = Theta(n^2 log n)` and
`s_2 = Theta(n sqrt(log n))` at `t = Theta(1)`,  `d = Theta( sigma·n^3 (log n)^{3/2} )`.

*Step size.* By Lemma D, `|Delta W_3| <= A(v,y) + E_y[A] <= C n^3 (1+o(1))`, so `J = O(n^3)`
and `d/(2J) = Omega( sigma (log n)^{3/2} )`.

*Predictable quadratic variation.*
`Var[Delta W_3 | F_i] <= E_y[A(v,y)^2] <= (max_y A)·E_y[A] = O(n^3)·O(n^2 log^2 n)`, using
Lemma D for the maximum and
`E_y[A] = sum_u codeg(v,u)·2 d_3(u)/|V| = O(D^2/N) = O(n^2 log^2 n)` for the mean. Over
`m = Theta(n/sqrt(log n))` steps, `V_qv = O(n^6 (log n)^{3/2})`, so
`d^2/(2 V_qv) = Omega( sigma^2 (log n)^{3/2} )`.

Freedman gives `exp(-min( d^2/(4 V_qv), d/(4J) )) = exp(-Omega( sigma^2 (log n)^{3/2} ))`,
which is at most `N^{-1-c} = exp(-(1+c)·2 log n)` as soon as
`sigma^2 (log n)^{3/2} >> log n`, i.e. `sigma >> (log n)^{-1/4}`. ∎

**What this says against Theorem 2.** For the *pointwise* condition the budget in jump-units
was `sigma sqrt(log n)` against a requirement of `log n / log log n` — a deficit of
`sqrt(log n)/log log n`. For the *averaged* condition the budget in jump-units is
`sigma (log n)^{3/2}` against a requirement of order `log n` — a **surplus** of
`sigma sqrt(log n)`. The averaged statistic gains exactly a factor `log n` over the pointwise
one, and Lemma D is where that factor comes from.

### 5.4 The `l = 2` case does not close

The same programme for `l = 2` requires `|W_2(v,i)| <= d_2(v)·tol`, with
`W_2(v) = sum_{u ~_2 v} e(u)` and `d_2(v)·tol = Theta(sigma n^2 log n)`. Its increment has two
parts.

**(i) Existing neighbours move: `sum_{u ~_2 v} codeg(u,y)`. Controllable.** The set
`S = N_2(v,i)` has `|S| = d_2(v) = Theta(n sqrt(log n))`, and the worst case is that `S`
consists of the `|S|` vertices smallest in the `s(·,y)` order. By (*),
`#{u : s(u,y) <= K} <= 16nK`, so those vertices have `s(u,y) <= K` with `16nK = |S|`, i.e.
`K = Theta(sqrt(log n))`, whence
```
   sum_{u in S} codeg(u,y)  <=  n^{1+o(1)} + sqrt(2) n · sum_{s<=K} 16n/s  =  O( n^2 log log n ),
```
against a budget `Theta(sigma n^2 log n)`. Surplus `Theta(sigma log n / log log n)`. **Fine.**

**(ii) New neighbours arrive: `sum_{u in P(v,y)} e(u)`, with
`P(v,y) := {u : {v,u,y} in H(i)}` of size `codeg(v,y)`, up to `Delta_2 = n(1+o(1))`.
This does not close.**

- With the crude cap `|e(u)| <= s_2 (log n)^{1/2}` (Prop 3(3a)) the bound is
  `n · n log n = n^2 log n`, against budget `sigma n^2 log n` — short by a factor `1/sigma`.
- With *typical* excesses `|e(u)| = Theta(sd(e)) = Theta(n (log n)^{1/4})` the bound is
  `n^2 (log n)^{1/4}` **even with all signs aligned**, against budget `sigma n^2 log n` — a
  surplus of `sigma (log n)^{3/4}`. **Fine.**
- Cauchy–Schwarz against the global scalar
  `sum_{u in V} e(u)^2 = O(N·sd(e)^2) = O(n^4 sqrt(log n))` gives only
  `sqrt(|P|)·(sum_V e^2)^{1/2} = n^{5/2}(log n)^{1/4}` — short by `sqrt(n)`. Too lossy,
  precisely because it assumes the worst alignment.

So the `l = 2` case turns entirely on whether the `Theta(n)` vertices of `P(v,y)` — which are
precisely the lattice points of **one line**, the perpendicular bisector of `v` and `y` — are
systematically exceptional. They are collinear, and by §5.1 exceptional vertices are produced
along short-direction lines; a bisector is such a line. **The mechanism for positive
correlation is present, and Lemma D does not bound it**, because Lemma D controls a
`codeg(v,·)`-weighted sum whereas `P(v,y)` is an *unweighted* set of `Theta(n)` collinear
points. This is the single remaining obligation; see `HANDOFF.md`.

### 5.5 Line-by-line substitution into the bound (conditional arithmetic)

If §5.4 were closed, the horizon would be limited by the *next* binding constraint, the
pointwise `l = 3` condition together with its tolerance compounding:

```
 1.  max jump of d_3^-(v) per step   <=  codeg(v,y) + Gamma(v,y)  =  O(n^2)
 2.  budget for d_3                  =  sigma_{3,0}·s_3 = Theta( sigma_{3,0} n^2 log n )
 3.  jump budget                     g_3 = Theta( sigma_{3,0} log n )
 4.  hazard of a Theta(n^2) jump     mu_3 = Theta( 1/sqrt(log n) )
 5.  union bound g_3·log(g_3/mu_3) >= 2 log n     =>  sigma_{3,0} >= C/log log n
 6.  compounding sigma_3(t) = sigma_{3,0} e^{C t^2}/q^2 = o(1)
                                     =>  e^{(C+2)t^2} = o(log log n)
                                     =>  t = O( sqrt(log log log n) )
 7.  horizon  m = t·N/D^{1/2}        =  Theta( n sqrt(log log log n)/sqrt(log n) )
 8.  conclusion  |I| = Theta(m)      =  Theta( n sqrt(log log log n)/sqrt(log n) ).
```

That would be a strict improvement on `Omega(n/sqrt(log n))` by a factor
`sqrt(log log log n)`.

**It is not claimed.** Line 8 rests on §5.4 (open), on (H-surv) (unproved), on the
independence audit of Prop 3(3b), and on line 6's compounding constant. It is recorded here
only so that the value of closing §5.4 is explicit and so that no later reader has to
re-derive it. Nothing in Part V changes the proved lower bound for `C(n)`, which remains
`Omega(n/sqrt(log n))`.

---

## Part VI. Obligation (Q2): the dynamic line lemma

Part V left obligation (Q2): control `sum_{u in P(v,y)} e(u,i)`, where `P(v,y)` is the set of
vertices that become 2-neighbours of `v` when `y` is chosen — up to `n^{o(1)}` exceptions, the
lattice points of a **single line**, the perpendicular bisector of `v` and `y`. This part
proves it.

### 6.0 Filtration, stopping time, indices, and the object to be controlled

- `F_i` = sigma-algebra generated by `y_0, ..., y_{i-1}`. `y_i` is uniform on `V(i)` given `F_i`.
- `T` = the Bennett–Bohman stopping time (ind.tex line 720) with condition (V) for `l = 2`
  deleted and (A0)/(A1)/(A2) inserted. **Everything below is asserted for `i <= T` only.** The
  only property of `T` used is the vertex-count condition (P), in the one-sided form
  ```
        |V(i)| >= N q(t_i) / 2       for all i <= T.                              (6.1)
  ```
- `m := ` horizon, `t := D^{1/2} m / N = Theta(1)`, `q := q(t) = Theta(1)`,
  `s_2 = Theta(n sqrt(log n))`, `Delta_2 = n(1+o(1))`, `D = Theta(n^2 log n)`.
- `X_j(u) := ` number of size-2 edges at `u` created at step `j`. Every such edge `{u,x}` comes
  from a size-3 edge `{u,x,y_j}` of `H(j)`, so **deterministically**
  ```
        X_j(u)  <=  codeg_{H(j)}(u, y_j)  <=  codeg_{H_n}(u, y_j),                 (6.2)
  ```
  the second inequality because size-3 edges of `H(j)` are a subset of those of `H_n`.
- `xi_j(u) := X_j(u) - E[ X_j(u) | F_j ]`, a martingale difference array;
  `e(u,i) := d_2^+(u,i) - s_2^+(t_i) = sum_{j<i} xi_j(u) + O(n^{1+o(1)})`, the error term being
  the Riemann-sum discrepancy between `sum_j E[X_j]` and `s_2^+`, which BB absorb into `f_2`.
  We write `e(u,i) = sum_{j<i} xi_j(u)` below; the discrepancy is negligible at every scale
  appearing here.

For a line `L` of the plane write `L` also for `L ∩ [n]^2`, and `s_L` for the sup-norm of its
primitive direction, so that `|L| <= 1 + sqrt(2) n / s_L <= n`.

**The object.** For each line `L` define
```
     Phi_L(i)  :=  sum_{u in L}  e(u,i)^2 ,
```
with `e(u,·)` frozen at the step where `u` leaves `V`. Obligation (Q2) follows from a bound on
`Phi_L`, because Cauchy–Schwarz gives, for **every** subset `S ⊆ L` — in particular for the
random, `F_i`-measurable set `P(v,y) ∩ L`, which is what the application needs —
```
     sum_{u in S} |e(u,i)|  <=  sqrt( |L| · Phi_L(i) ).                            (6.3)
```
Using `|e(u,i)|` rather than `e(u,i)` is deliberate: it makes the bound immune to *which*
points of the bisector survive to step `i`, which is the difficulty that blocked the naive
route. **No cancellation is needed** — §5.4 already showed that typical excesses, even fully
aligned in sign, leave a surplus of `sigma (log n)^{3/4}`.

### 6.1 The static input: a line-restricted Lemma D

> **Lemma E.** Let `L` be a line and `z ∈ [n]^2`. Then
> ```
>    (a)  z ∉ L :   sum_{u in L} codeg(u,z)  <=  10 n^{3/2} + n^{1+o(1)} ,
>    (b)  z ∈ L :   sum_{u in L} codeg(u,z)  <=  4 n^2 / s_L^2 + n^{1+o(1)} .
> ```

**Proof.** As in Lemma D, `codeg(u,z) <= R + sqrt(2) n / s(u,z)` with `R = n^{o(1)}`, and
`|L| <= n`, so it suffices to bound `sum_{u in L} 1/s(u,z)`.

**(a)** Put `a_s := #{ u ∈ L : s(u,z) = s }`. The `u` with `s(u,z) = s` lie on the union of the
lines through `z` whose primitive direction has sup-norm `s`; there are at most `8s` such
directions, hence at most `8s` such lines. Since `z ∉ L`, none of them equals `L`, so each
meets `L` in at most one point and
```
        a_s <= 8s ,        and       sum_s a_s <= |L| <= n .
```
Maximise `sum_s a_s/s` subject to those two constraints: mass is best placed at small `s`, and
`sum_{s<=S} 8s = 4S(S+1)`, so with `S := ceil(sqrt(n)/2)` the first `S` scales absorb at least
`n` of the mass. Hence
```
        sum_{u in L} 1/s(u,z)  <=  sum_{s<=S} 8s/s  +  n/S  =  8S + n/S  <=  6 sqrt(n) + O(1).
```
Therefore `sum_{u in L} codeg(u,z) <= |L| R + sqrt(2) n · 6 sqrt(n) <= 10 n^{3/2} + n^{1+o(1)}`.

**(b)** If `z ∈ L` then every `u ∈ L \ {z}` has `u - z` parallel to the direction of `L`, so
`s(u,z) = s_L` for all of them. Hence
`sum_{u in L} 1/s(u,z) <= |L|/s_L <= (1 + sqrt(2) n/s_L)/s_L`, and
`sum_{u in L} codeg(u,z) <= |L| R + sqrt(2) n (1 + sqrt(2)n/s_L)/s_L <= 4 n^2/s_L^2 + n^{1+o(1)}`. ∎

**Why (b) cannot be improved, and what it means.** Case (b) is exactly the event the obligation
warned about: if the chosen vertex `y_j` lies **on** the bisector line `L`, then every
`u ∈ L` has `u - y_j` in the direction of `L`, so every `u ∈ L` simultaneously receives
`codeg(u,y_j) = Theta(n/s_L)` new 2-edges. For an axis-parallel `L` this is `Theta(n)` new
2-edges at each of `Theta(n)` collinear vertices, in **one step**. Case (a) says that when
`y_j ∉ L` this cannot happen: the total is `O(n^{3/2})`, a factor `sqrt(n)` below the trivial
`|L| · Delta_2 = n^2`. The whole of §6.2 is organised around that dichotomy.

*(Counterexample search, `experiments/s8_line.c`, all lines of primitive direction of sup-norm
`<= 6`, `n = 48,96,192,384`: `max sum/n^{3/2}` = 3.11, 2.72, 2.32, 1.97 — decreasing, so (a)
holds with room; `max sum·s_L^2/n^2` = 1.66, 1.27, 1.03, 0.89 — bounded, so (b) is the right
shape. No counterexample found.)*

### 6.2 The dynamic lemma

> **Theorem F.** Let `sigma = sigma(n)` satisfy `sigma = o(1)` and `sigma · log log n -> ∞`
> (for instance `sigma = (log log n)^{-1/2}`), and set
> ```
>       d_Phi  :=  kappa · sigma^2 n^3 (log n)^2       (kappa a small absolute constant).
> ```
> Then with probability `1 - o(1)`,
> ```
>       Phi_L(i)  <=  d_Phi        for every line L and every i <= T,
> ```
> and consequently, by (6.3), for every `v`, every `y`, and every `i <= T`,
> ```
>       sum_{u ∈ P(v,y)} |e(u,i)|  <=  sqrt(kappa) · sigma n^2 log n  +  n^{1+o(1)}
>                                   <=  (1/2) · d_2(v) · tol ,
> ```
> which is exactly condition (A2) for `l = 2`. **Obligation (Q2) is discharged.**

**Proof.** Fix a line `L`. There are at most `binom(N,2) = O(n^4)` lines meeting `[n]^2` twice,
so it suffices to prove failure probability `<= n^{-5}` for each.

*Doob decomposition.* Since `E[xi_i(u) | F_i] = 0`,
```
   Delta Phi_L(i) = 2 sum_{u∈L} e(u,i) xi_i(u)  +  sum_{u∈L} xi_i(u)^2 ,
   E[ Delta Phi_L | F_i ] = sum_{u∈L} E[ xi_i(u)^2 | F_i ] .
```
By (6.2), the layer-cake bound of Lemma 1(c) (`sum_y codeg(u,y)^2 = O(N n log n)`) and (6.1),
```
   E[ xi_i(u)^2 | F_i ] <= E_y[ codeg(u,y)^2 ] = (1/|V(i)|) sum_y codeg(u,y)^2 = O( n log n / q ),
```
so the compensator satisfies, deterministically for `i <= T`,
```
   A_i := sum_{j<i} sum_{u∈L} E[xi_j(u)^2 | F_j]  <=  |L| · m · O(n log n/q)  =  O( n^3 sqrt(log n) / q ) =: B.
```
`B / d_Phi = O( 1/(kappa q sigma^2 (log n)^{3/2}) ) = o(1)` because `sigma >> (log n)^{-3/4}`.
So `Psi_i := Phi_L(i) - A_i` is a martingale, `Psi_0 = 0`, and it suffices to show
`P[ Psi_i >= d_Phi/2 for some i <= T ] <= n^{-5}`.

*Stopping.* Let `T_Phi` be the first `i` at which `Phi_L(i) > d_Phi`, and run the argument on
`[0, T ∧ T_Phi]`. Before `T_Phi` we may use, via Cauchy–Schwarz,
```
   sum_{u∈L} |e(u,i)|  <=  sqrt(|L| d_Phi)  <=  sqrt(kappa) sigma n^2 log n ,
   ( sum_{u∈L} e(u,i)^2 )^{1/2}  <=  sqrt(d_Phi) .                                  (6.4)
```
This is the only place the stopped filtration is used, and it is what makes the estimate
self-consistent rather than circular.

*Splitting the steps.* Call step `i` a **line step** if `y_i ∈ L`, and an **ordinary step**
otherwise. This is exactly the dichotomy of Lemma E.

*Ordinary steps.* Pairing Cauchy–Schwarz the other way from (6.4),
```
   | 2 sum_{u∈L} e(u,i) xi_i(u) |  <=  2 ( sum_{u∈L} e(u,i)^2 )^{1/2} ( sum_{u∈L} xi_i(u)^2 )^{1/2}
                                   <=  2 sqrt(d_Phi) ( Delta_2 · sum_{u∈L} codeg(u,y_i) )^{1/2}
                                   <=  2 sqrt(d_Phi) ( n · 10 n^{3/2} )^{1/2}
                                    =  O( sigma n^{11/4} log n )
```
using Lemma E(a) and `xi_i(u)^2 <= Delta_2 · codeg(u,y_i) + O(log^2 n)`. Adding
`sum_{u∈L} xi_i(u)^2 = O(n^{5/2})` gives an ordinary-step jump
`C_ord = O(sigma n^{11/4} log n)`, whence
```
   d_Phi / (4 C_ord)  =  Omega( sigma n^{1/4} log n )  >>  log n .                  (6.5)
```
For the predictable quadratic variation, the same pairing gives
```
   Var[ Delta Phi_L | F_i ]  <=  8 d_Phi · E_y[ sum_{u∈L} xi_i(u)^2 ]  +  2 E_y[ (sum_u xi^2)^2 ]
                             <=  8 d_Phi · |L| · O(n log n/q)  +  O(n^5 log n/q)
                              =  O( sigma^2 n^5 (log n)^3 / q ),
```
so over `m = Theta(n/sqrt(log n))` steps `V_qv = O(sigma^2 n^6 (log n)^{5/2}/q)` and
```
   d_Phi^2 / (4 V_qv)  =  Omega( q sigma^2 (log n)^{3/2} )  >>  log n
   whenever  sigma >> (log n)^{-1/4}.                                                (6.6)
```
By Freedman (ind.tex line 797) applied to the truncated martingale, the ordinary steps
contribute at most `exp(-Omega(min{(6.5),(6.6)})) <= n^{-5}`.

*Line steps.* Here Lemma E(b) gives only `sum_{u∈L} codeg(u,y_i) = O(n^2/s_L^2) <= O(n^2)`, so
`sum_{u∈L} xi_i(u)^2 <= Delta_2 · O(n^2) = O(n^3)` and, by (6.4),
```
   | Delta Phi_L(i) |  <=  2 sqrt(d_Phi) · O(n^{3/2})  +  O(n^3)  =  O( sigma n^3 log n ) .
```
The number of line steps that the budget can absorb is therefore
```
   g_L  :=  ( d_Phi / 2 ) / O(sigma n^3 log n)  =  Theta( sigma log n ).             (6.7)
```
Their predictable hazard is bounded deterministically using (6.1) and `|L| <= n`:
```
   mu_L  :=  sum_{i<m} P[ y_i ∈ L | F_i ]  =  sum_{i<m} |L ∩ V(i)| / |V(i)|
         <=  m · n / (Nq/2)  =  Theta( 1 / (q sqrt(log n)) ) .                       (6.8)
```
The number of line steps stochastically dominates nothing, but is *dominated* by `Bin(m, p)`
with `p = 2/(nq)`, so `P[ #line steps >= g_L ] <= (e mu_L / g_L)^{g_L}` and
```
   - log P  >=  g_L · log( g_L / (e mu_L) )  =  Theta( sigma log n ) · log( Theta(sigma q (log n)^{3/2}) )
            =  Theta( sigma · log n · log log n ) .
```
This exceeds `5 log n` precisely when `sigma log log n -> ∞`, which is the hypothesis. ∎

**Where each ingredient went.** Lemma E(a) supplies the `sqrt(n)` that makes the ordinary
steps invisible — (6.5) has margin `n^{1/4}`. Lemma E(b) is not improvable, and the coherent
`Theta(n)`-jump-to-`Theta(n)`-collinear-vertices event is paid for by a **jump count**, not by
a step-size bound: `(6.7)` against `(6.8)` is a budget of `sigma log n` against a hazard of
`(log n)^{-1/2}`, and it clears by `log log n`. The stopped bound (6.4) is what keeps the
line-step jump at `sigma n^3 log n` rather than at the crude `max|e| · n^2 = n^3 log n`; without
it `g_L` would be `Theta(1)` and the argument would fail.

### 6.3 Can the line lemma be summed over directions and scales without losing the logarithm?

Yes, and trivially so: **it does not need to be summed.** The application (§5.4(ii)) requires
the bound for one line at a time — the bisector of the particular pair `(v,y)` — and Theorem F
is proved for every line simultaneously by a union bound over the `O(n^4)` lines, which costs
`5 log n` in the exponent and is already paid for in (6.5)–(6.8). No summation over primitive
directions or scales occurs, so no logarithm can be lost there.

The sum over directions and scales happens *inside* Lemma E, in
`sum_{s<=S} 8s/s + n/S <= 6 sqrt(n)`, and that is where the saving comes from: the constraint
`a_s <= 8s` together with `sum_s a_s <= n` is what caps the harmonic sum at `sqrt(n)` instead
of `log n · n`. Note the contrast with Lemma D, where the saving came from
`sum_u 1/s(v,u)^2 < 27n` converging. Both are consequences of the same uniform count
`#{u : s(v,u) = s} <= 16n`; on a line the count improves to `<= 8s`, which is stronger for
small `s` and is what the line lemma exploits.

**Audit of the Freedman exponent.** The exponent actually used is
```
   min{  d_Phi^2/(4 V_qv),  d_Phi/(4 C_ord)  }  =  min{ Omega(q sigma^2 (log n)^{3/2}),  Omega(sigma n^{1/4} log n) }
```
for the truncated part, plus `Theta(sigma log n log log n)` for the jump count. The binding
constraint is the **jump count**, not the quadratic variation: the variance term (6.6) has
margin `(log n)^{1/2}` and the ordinary step term (6.5) has margin `n^{1/4}`, while the jump
count clears only by `log log n`. The correct reading of `d^2/(2(v + Cd)) <= d/(2C)` is used
once, as a ceiling on what the step-size term can ever give; it is never used as a lower bound.

### 6.4 Substituting into (H-surv): it does **not** close, and it does not need to

The prompt's decision test asks that the dynamic lemma be substituted into (H-surv). Doing so
gives a definite negative, and a definite simplification.

**(a) Theorem F is too weak for (H-surv), by exactly `sqrt(log n)`.** (H-surv) needs a fixed
line to retain a constant fraction of its vertices while `q = Theta(1)`. A vertex `u` is
removed at step `j` with conditional probability `(1 + d_2(u,j))/|V(j)|`, so a line `L` retains
a constant fraction iff
```
   sum_{j<m} ( sum_{u∈L} d_2(u,j) ) / ( |L| |V(j)| )  =  O(1)
   <=>  the line-average of d_2 is O(s_2)
   <=>  sum_{u∈L} |e(u,j)|  =  O( |L| s_2 )  =  O( n^2 sqrt(log n) ).
```
Theorem F delivers `sqrt(kappa) sigma n^2 log n`, which is `Theta(sigma sqrt(log n))` times too
large. Shrinking `sigma` to `Theta((log n)^{-1/2})` to fix this contradicts the hypothesis
`sigma log log n -> ∞`. **The gap is exactly `sqrt(log n)`.**

**(b) The direct route for (H-surv) meets the Theorem 2 barrier, unchanged.** One may try to
control the *signed* sum `sum_{u∈L} e(u,i)` instead, which is a martingale and needs only
constant relative accuracy: `|sum_{u∈L} e(u,i)| <= eps |L| s_2 = Theta(eps n^2 sqrt(log n))`
with `eps` a constant. But by Lemma E(b) a single line step moves it by `Theta(n^2)`, so the
budget in jump-units is `g = Theta(eps sqrt(log n))` against a hazard
`mu_L = Theta((log n)^{-1/2})`, giving an exponent
`g log(g/mu) = Theta(sqrt(log n) log log n)` — short of `log N` by
`sqrt(log n)/log log n`. **This is the identical deficit as Theorem 2**, with the identical
mechanism.

> **Corollary 6.1 (averaging over a line does not help).** The line-average of `d_2` obeys the
> same barrier as the pointwise value of `d_2`. A line is precisely the wrong set to average
> over, because the exceptional jumps are coherent along lines (Lemma E(b)). What made the
> `l = 3` case work in Part V was that the weights `codeg(v,·)` spread the mass over the whole
> grid; a line is the extremal set on which they do not.

**(c) But (H-surv) is not needed by the positive programme.** Re-auditing where it was used:

| use | needs (H-surv)? |
|---|---|
| Theorem 2 (the barrier) | **yes** — it supplies a *lower* bound on the hazard, which is what a lower bound on the failure probability requires. Theorem 2 is a negative result and feeds nothing. |
| Prop 3(3a), the crude cap `max_v d_2(v) <= K s_2` | **no.** An *upper* bound on the failure probability needs an *upper* bound on the hazard, i.e. Lemma 1(c) plus (6.1). Redoing the computation gives the cap with `K = Theta(sqrt(log n)/log log n)`, exponent `Theta(K sqrt(log n) log log n) = Theta(log n log log n)`. This is a **correction** to the registry, which had P1 marked conditional on (H-surv). |
| Prop 3(3b) neighbourhood average | superseded by Lemma C (§5.3), which is a Freedman estimate and assumes no independence. |
| Theorem F (§6.2) | **no** — the proof above uses only (6.1), Lemma 1(c), Lemmas D/E and the stopped bound (6.4). It does not use the crude cap either. |

So (H-surv) survives only as a hypothesis of the barrier Theorem 2, and Corollary 6.1 shows it
is itself out of reach of these methods. Since a barrier is not an input to a bound, this costs
the positive programme nothing — but it does mean **Theorem 2 must remain labelled conditional
permanently**, and Corollary 6.1 says the label cannot be removed by the line technology.

### 6.5 What the positive programme now has, and what it still lacks

| stopping-time condition at `r = 3` | status after Part VI |
|---|---|
| (S) `d_{A up 3} <= Delta_2` | deterministic, monotone (§1.1) |
| (C) `c_{3,3->2} <= Gamma` | deterministic, monotone (§1.1) |
| (C) `c_{2,3->1}`, `c_{3,2->1}`, `c_{3,3->1}` | reduce to (S) via ind.tex line 846 |
| (C) `c_{2,2->1} <= C_{2,2->1}` | **NOT VERIFIED for `H_n`** — see HANDOFF |
| (P) `\|V(i)\|` | Prop 3(3a)+(3c)(1): crude cap (now unconditional) + global scalar; margin `exp(-Omega(n^{1-o(1)}))` |
| (V) `l = 3`, pointwise | ample jump budget (§5.5 lines 1–5); needs `sigma_{3,0} >= C/log log n` |
| (V) `l = 2`, pointwise | **FALSE** (Theorem 2, conditional on (H-surv)) — deleted from the stopping time |
| (A0) crude cap | Prop 3(3a), corrected: unconditional, `K = Theta(sqrt(log n)/log log n)` |
| (A1) global scalar | Prop 3(3c)(1), vast margin |
| (A2) `l = 3` | **Lemma C** (§5.3), needs `sigma >> (log n)^{-1/4}` |
| (A2) `l = 2` | **Theorem F** (§6.2), needs `sigma log log n -> ∞` |

Every `sigma`-constraint above is met by `sigma = (log log n)^{-1/2}`. What is missing is one
unverified condition (`c_{2,2->1}`) and the bookkeeping of BB's §sec:dynamic under the
substituted conditions, including the tolerance-compounding constant of §5.5 line 6. **No bound
on `C(n)` is stated, and the proved bound remains `Omega(n/sqrt(log n))`.**
