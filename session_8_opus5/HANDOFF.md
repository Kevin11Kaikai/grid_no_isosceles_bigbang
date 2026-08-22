# Handoff — every remaining obligation

The claim-safety audit of Part VII downgraded Theorem F from PROVED to CONDITIONAL and the
session verdict to `CONDITIONAL_BRIDGE_ONLY`. There is no longer a single obligation. All of
them are listed below, in the order they should be attacked.

**Unconditional and safe to build on:** Lemma 1 (`Delta_2 = n(1+o(1))`, the fat top, the Pareto
tail `B_v(tau) = O(n^2 log n/tau)`, `D = Theta(n^2 log n)`), **Lemma D**
(`sum_u codeg(v,u) codeg(u,y) <= 54 n^3`), **Lemma E** (line-restricted: `O(n^{3/2})` off the
line, `O(n^2/s_L^2)` on it), the positive-clustering counterexample, Corollary 6.1, and the
crude cap Prop 3(3a).

**Conditional:** Theorem 2 (on (H-surv), permanently), Lemma C (on K1b), Theorem F′ (on K1b,
K2, K3, K4).

---

## (K1a) The dynamic pair codegree — BB's own condition

> Show `c_{2,2->1}(v,v',i) <= C_{2,2->1} = 8 D^{1/2-eps+2lambda}` for all pairs and all
> `i <= T`, with a polylogarithmic rather than polynomial `eps`.

`c_{2,2->1}(v,v',i)` is the codegree of the pair `v,v'` in the evolving 2-graph `G(i)` — the
unique genuinely dynamic pair condition at `r = 3` (§1.1). Typical value `s_2^2/N = Theta(log n)`
against a requirement `Theta(s_2/polylog)`, so `n/polylog` of room; but the jump is `Theta(n)`
when the chosen vertex lies on a line common to `v` and `v'`, putting the budget at
`Theta(sqrt(log n))` against `log n/log log n` — **the Theorem 2 shape**. It may fail.

## (K1b) The line-averaged pair codegree — needed by Theorem F′ and Lemma C

> Show `sum_{u ∈ L} c_{2,2->1}(u, y, i) = O(n^{3/2})` for every line `L`, every `y ∈ V(i)`, and
> every `i <= T`.

This is **not** implied by (K1a): at the level (K1a) allows, the line sum is
`Theta(n^2 sqrt(log n)/polylog)`, which exceeds both branches of Lemma E and would dominate the
whole jump analysis of Theorem F′ (§7.2(a)). What is asked is an average of `O(sqrt n)` along a
line against a typical value of `Theta(log n)` — far weaker than (K1a) and probably true, but
unproved. It arises because `Delta d_2^-(u,j) <= 1 + c_{2,2->1}(u,y_j,j)`.

**Attack it first**: it is the weakest of the four and it is what makes Theorem F′ and Lemma C
conditional. The natural route is the Lemma E template — bound `c_{2,2->1}(u,y)` by a
codegree-type count and use the uniform-in-`s` counting `#{u : s(u,y) = s} <= 16n` restricted to
a line, where it improves to `<= 8s`.

## (K2) The `d_2^-` feedback: does the tolerance compound or self-correct?

> The drift of `d_2^-` gives `R^-_i(u) = Theta(1) · (time-average of e(u,·))`, an `O(1)`
> feedback (§7.2(b)). Under Bennett–Bohman's one-sided bounding this produces a Grönwall
> amplification `q(t)^{-C}` of `Phi_L`. The true linearised system
> ```
>    d(delta_3)/dt = -4t delta_3 - 2 D^{1/2} q delta_2 ,   d(delta_2)/dt = (2/(D^{1/2}q)) delta_3 - 4t delta_2
> ```
> has eigenvalues `-4t ± 2i` and is **stable**, so errors should decay like `q^{+4}`. Determine
> which governs `Phi_L`, and compute the constant `C`.

This is the self-correction question in its sharpest form for this problem. It fixes the
horizon jointly with (7.10) and therefore fixes the numerical bound.

## (K3) `H_n` is not `D`-regular

> Exact degrees `2D(v) = sum_y codeg(v,y)`:
>
> | `n` | centre | corner | edge midpoint | max/min |
> |---|---|---|---|---|
> | 64 | 71 719 | 32 252 | 36 319 | 2.22 |
> | 128 | 341 507 | 147 848 | 170 587 | 2.31 |
>
> The ratio is a constant bounded away from 1 and is not decreasing. BB's Theorem 1.1 assumes
> `D`-regularity, and every trajectory `s_l(t)` and the entire stopping time are written for a
> single `D`. Either (i) regularise upward by dummy edges **and re-prove Lemmas 1, D and E for
> the augmented hypergraph** — they are statements about grid geometry, so they do not transfer
> for free — or (ii) state and prove a version of BB with vertex-dependent degrees `D(v)`.

The earlier campaign's dummy-edge regularisation is **not** imported as established, per the
frozen-status instruction. This obligation was not visible before the audit and is the largest
of the four.

## (K4) A complete proof of the substituted Candidate A

> Re-derive ind.tex §sec:dynamic with (A0)/(A1)/(A2) in place of (V) at `l = 2`:
> - re-derive the variation equations (ind.tex 981, 995, 998), whose right-hand sides contain
>   `f_2`, the error function of a variable no longer tracked pointwise;
> - exhibit a replacement error-function system with `f(0) = 1`, `f` increasing, satisfying the
>   resulting differential inequalities;
> - re-establish the supermartingale property of `Z_V` and `Z_3^±` using only the averaged
>   conditions;
> - compute the compounding constant `C`, which with (7.10) fixes the horizon.

§6.5 called this "bookkeeping". That was wrong and the word is now banned for anything not
written down.

## (H-surv) — for the barrier only

Still assumed, still only a hypothesis of Theorem 2. Corollary 6.1 shows the line technology
cannot discharge it (the line-average of `d_2` obeys the same barrier as the pointwise value),
so Theorem 2 is permanently conditional. It is **not** needed by the positive programme.

---

## If all of (K1a), (K1b), (K2), (K3), (K4) closed

Theorem F′ holds to `t <= c sqrt(log log log n)` — the ceiling comes from the asymmetry
`g_L ∝ q^{1/2}` versus `mu_L ∝ q^0` in (7.8)–(7.10), not from the compounding — and then
```
   m = t N / D^{1/2} = Theta( n sqrt(log log log n) / sqrt(log n) ),
```
a strict improvement on `Omega(n/sqrt(log n))` by `sqrt(log log log n)`. **Not claimed.**
Reaching `C(n) = Omega(n)` needs `t = Theta(sqrt(log n))`, which (7.10) forbids outright; a
linear bound therefore requires a different treatment of the line-step hazard, not merely the
closure of K1–K4.

## What must not be redone

- Do **not** revisit "average `Delta_2` or `Gamma`" (registry S1/S2/S5).
- Do **not** try to rescue the *pointwise* `d_2` condition (registry B4, ATTACK_LOG A5), and do
  not try to rescue it by averaging over a **line** either — Corollary 6.1 shows the
  line-average obeys the same barrier.
- Do **not** assume independence or negative association of `{e(u)}`; both are false (§5.1).
- Do **not** use Cauchy–Schwarz against the *global* `sum_u e(u)^2`; short by `sqrt(n)` (§5.4).
  Against the *per-line* second moment it works — that is Theorem F′.
- Do **not** attempt a *signed* bound on `sum_{u ∈ P(v,y)} e(u)`: `P(v,y)` is a random subset of
  the bisector line, so cancellation over the line implies nothing about it (§6.0).
- Do **not** state a result in terms of `d_2^+` and call it a result about `d_2`. That was the
  central defect found by the audit (§7.2).
- Do **not** describe an unwritten re-derivation as "bookkeeping" (§7.5(b)).
- Do **not** infer asymptotics from finite-`n` tables. Earlier in this session a fitting error of
  exactly that kind — `sd_y(A) = Theta(n^3)` rather than the true `Theta(n^2 log^2 n)`, the two
  differing by a factor 4 at `n <= 64` — briefly made the averaged programme look dead. It was
  caught by computing **`sd/mean`**, which is scale-free and came out flat at 0.22. **Keep using
  scale-free ratios when checking a fit.**
