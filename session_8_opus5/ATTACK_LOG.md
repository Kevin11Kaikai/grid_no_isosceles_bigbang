# Attack log — Session 8

Chronological. Each entry: what was tried, what happened, what it cost.

---

## A1. First candidate: "edge-weighted averages replace pointwise maxima"

**Claim attempted.** BB's hypotheses `Delta_2(H) < D^{1/2-eps}` and `Gamma(H) < D^{1-eps}`
are stated as pointwise maxima over pairs but consumed as edge-weighted averages; under the
weighted form `H_n` satisfies them.

**Result: REJECTED on inspection of the source, before any work.** At `r = 3`,
`d_{{v,y} up 3}(i)` and `c_{3,3->2}(v,v',i)` count size-**3** edges of `H(i)`, and size-3
edges of `H(i)` are exactly the edges of `H_n` with no chosen vertex. Both are therefore
**monotone non-increasing**, so the corresponding stopping conditions hold *deterministically*
once the static hypothesis holds at `i = 0` (§1.1 of THEOREM_AND_PROOF). `Delta_2` and
`Gamma` are initial conditions for monotone quantities, not dynamically controlled objects.
There is nothing to average.

**Consequence.** The candidate is not false, it is vacuous. Averaging `Delta_2`/`Gamma` cannot
help because the difficulty was never there. This also invalidates the framing carried in
earlier branches of this repository; it is recorded as a correction, not imported as fact.

---

## A2. Relocating the difficulty

Re-audited every occurrence of `d_2` and of the pair statistics in ind.tex (table in §1.2).
Findings:

- The unique dynamically nontrivial pair condition at `r = 3` is `c_{2,2->1}`.
- The conditions that carry the difficulty are the **per-vertex** conditions (V) on `d_2^±`,
  not the per-pair ones.
- `d_2` itself is never consumed pointwise at `o(1)` accuracy: it appears as a global
  average (`Z_V` drift), as a local average over `Theta(d_l(v))` vertices (`Z_l^-` drift),
  and as a crude step-size cap.
- The one place where a pair statistic is genuinely worst-case is the **step size**
  `Delta Z_l^+(v) <= codeg(v, y_i)` at ind.tex line 1172 — and `y_i` is **uniform**, which is
  what makes an averaged replacement conceivable.

This relocated the target from "pairs" to "`d_2(v)`", which is where the rest of the session
went.

---

## A3. The arithmetic of the increment (Lemma 1)

Computed the law of `codeg(v,y)` for uniform `y` analytically and checked it exactly
(`experiments/s8_tail.c`, `n = 64..512`):

```
   mean = 2D/N = Theta(log n),    P[X > tau] = O(log n / tau),    max = n(1+o(1)).
```

The tail is Pareto of index 1 truncated at `n`. The `log n` in `D` **is** the harmonic sum
over the scales of primitive directions; `D ≍ n^2 log n` and `Delta_2 ≍ n` are the same fact,
and `D^{1/2}/Delta_2 = Theta(sqrt(log n))` is forced. This is the arithmetic core of
everything that follows.

---

## A4. Second candidate: jump truncation with a weighted exceptional budget

**Claim attempted (Candidate A of the contract, first form).** Truncate the increment at
`tau`, apply Freedman to the truncated part, and pay for the exceptional part with the
predictable weighted hazard `Lambda_v^w(tau)`.

**Result: the expectation closes, the probability does not.** With `tau` chosen so the
Freedman exponent clears `log N`, the weighted hazard is
`Lambda_v^w = O(i_max · log(n/tau) / n) = O(log log n)` against a budget of order
`sigma sqrt(log n)` jump-units — comfortably small **in expectation**. But turning that into
high probability requires the number of exceptional steps to concentrate, and the exponent
available is `g log(g/mu)` with `g = O(sigma sqrt(log n))` and `log(g/mu) = Theta(log log n)`,
i.e. `O(sqrt(log n) log log n)` — short of `log N = 2 log n`.

This is exactly the gap the prompt names between "small expectation" and "high-probability
survival", and here it is quantified: **the deficit is a factor `sqrt(log n)/log log n`.**

**Consequence.** Not a failure of the truncation *device*; a failure of the *union bound over
vertices*. That distinction turned the second candidate into Theorem 2.

---

## A5. Attempted rescues of A4, and why each fails

| rescue | why it fails |
|---|---|
| Tune `zeta` (run length) down to make the hazard small | The conclusion `\|I\| = Omega(zeta n)` is linear in `zeta`; buying `exp(-sqrt(log n))` in probability costs a factor `exp(-sqrt(log n))` in the bound, far worse than `1/sqrt(log n)`. |
| Tune `delta` (accuracy) down to enlarge the budget | Admissibility forces `D^{-delta} = o(1)`; the budget is `<= sigma sqrt(log n)` with `sigma = o(1)` no matter what. Ceiling is structural (Lemma 1(d)), not a parameter choice. |
| Use a sharper inequality (Bennett/Freedman/compound-Poisson instead of Azuma) | Freedman does buy a factor `sqrt(log n)` over the asymmetric Azuma used at ind.tex line 1180 (the `d/(2C)` ceiling rather than `d^2/(3 m eta N)`). It is not enough: the barrier bounds the exponent **for any inequality**, since it lower-bounds the probability of the bad event directly. |
| Run longer (`t >> 1`) so relative fluctuations shrink | The tolerance schedule has its floor at `t = 0` and the jump size its ceiling at `t = 0`; the ratio is minimised early, so the constraint binds at `t = Theta(1)` regardless of horizon (Remark 2.0). |
| Regularise / sparsify the ground set | Random sparsification at density `p` scales `N -> pN`, `D -> p^2 D`, `Delta_2 -> p Delta_2`; the ratio `D^{1/2}/Delta_2` and the conclusion `N (log N/D)^{1/2}` are both **invariant**. Structured sparsification cannot help either: any `W` with `\|W\| = Omega(n^2/polylog)` has a horizontal line meeting it in `Omega(n/polylog)` points, and every horizontal line is a bisector. |
| Self-correcting error functions (Bohman–Keevash) | This removes the `q^{-C}` compounding of the tolerance, which is a real gain — but Theorem 2 is proved with **no** compounding assumed (`C = 0` is the most generous case), and it still holds. Self-correction does not touch the barrier. |

---

## A6. Counterexample-first check (X1) — the decisive one

**Question.** Is the pointwise condition (V) for `l = 2` actually *true* for `H_n`?

**Answer: no.** Theorem 2 lower-bounds the probability that a given vertex violates it by
`N^{-o(1)}`, so the expected number of violators is `N^{1-o(1)}`. This was then tested
directly by running the process (`experiments/s8_proc.c`): `max_v d_2^+ / mean_v d_2^+` is a
**large constant** (1.73–2.20 over `n = 64,128,256` and `alpha ∈ [0.25,1]`), not `1+o(1)`,
and the excess `(max-mean)/n` tracks the predicted `g* = 2 log n / log log n` (4.70 vs 5.84;
5.56 vs 6.14; 6.74/7.14/6.76 vs 6.47).

**Consequence.** The pointwise scheme is not merely hard for `H_n` — it is **false**. Any
correct analysis must drop the per-vertex condition on `d_2`. This is what makes the averaged
formulation necessary rather than merely convenient.

---

## A7. Check (X3) — does averaging actually remove the obstruction, or does the tail reappear?

Tested three candidate averaged statistics against the same heavy tail:

| statistic | budget in jump units | verdict |
|---|---|---|
| `sum_{v ∈ V(i)} d_2(v)` (global scalar) | `Theta(sigma n / log n)` | **survives** — no union bound needed, vast margin |
| `max_v d_2(v) <= s_2 log^{1/2} n` (crude cap) | `g = Theta(log n)`, exponent `Omega(log n log log n)` | **survives** — and it is all the `Z_V` step size needs |
| `Sigma_l(v)/((l-1) d_l(v))` (neighbourhood average) | average of `Theta(d_l(v)) >= Theta(n sqrt(log n))` terms; Chernoff gives `exp(-Omega(n))` | **survives** the union bound |
| `log d_2(v)` instead of `d_2(v)` | relative jump `1/sqrt(log n)`, budget `Theta(sqrt(log n))` — identical ratio | **fails**, same barrier (it is the same quantity) |

So averaging does remove the obstruction, in the precise sense that all three surviving
statistics clear the union bound by large margins. This is recorded as the positive content
of the session (Proposition 3).

---

## A8. Where it stops

The remaining obligation is **not** a concentration problem. It is that the drift of `Z_l^-(v)`
consumes `Sigma_l(v)` relative to `s_2`, and the vertices `u` summed over — `v`'s neighbours
in the evolving 2-graph — are produced by the *same* short-primitive-direction lines that
produce the large values of `d_2(u)`. The correlation is real and its sign is not determined
by anything proved here. Stated precisely in `HANDOFF.md`.

Two substantive revisions of the candidate theorem were used (A1 -> A4 -> Proposition 3),
which is the budget the contract allows. The session stops here rather than opening a third.

---

# Closure pass (continuation)

## A9. Claim-safety audit of Theorem 2

Question asked: is Theorem 2 a new theorem, a corrected obstruction lemma, a conditional
theorem, or a heuristic supported by computation?

**Answer: a conditional obstruction theorem.** Precisely:

- Its proof is complete and self-contained **given (H-surv)**, which is *assumed*, not proved
  (registry B1). So it is not unconditional.
- It is not a heuristic: the probability of the bad event is bounded **from below** by an
  explicit Binomial-domination argument, and the two inputs (Lemma 1(b): `|A_v| >= (n-1)/2`
  with `codeg >= n-1` and disjoint completion sets; Lemma 1(d): `D = O(n^2 log n)`) are
  proved. The finite-`n` tables corroborate the mechanism; nothing rests on them.
- It is not a theorem *about `C(n)`*. It says nothing about the isosceles problem; it says
  that one method cannot be applied to it. "Obstruction lemma" is the honest label, and its
  scope must always be quoted with the strategy it rules out (registry B4).
- Novelty: the specific competitor named in the plan (Guo–Warnke) has now been read at
  theorem level and does **not** contain either a relaxation of BB's hypotheses or a barrier
  statement (see LITERATURE_NOTES). Novelty is therefore `PLAUSIBLE` with one named
  competitor eliminated — still not `VERIFIED`, since the search was not exhaustive.

**Wording that is permitted:** "conditional obstruction theorem for the random greedy process
on `H_n`". **Wording that is not:** "new grid theorem", "new theorem about `C(n)`".

## A10. Third candidate: reduce (Q) to a deterministic lattice sum — SUCCEEDED for `l = 3`

The obligation was stated as a vague correlation question. The first move was to make it
deterministic. Writing `W_l(v,i) = sum_u m_v(u) e(u,i)`, the martingale increment for `l = 3`
is exactly `A(v,y) - E_y[A]` with

```
   A(v,y) = sum_u codeg(v,u)·codeg(u,y),
```

a two-step codegree-weighted path count. **The whole correlation question for `l = 3` is a
deterministic statement about `A`.** This removed the vagueness and made the question finite.

**The clustering is real (§5.1).** `v = (0,0)`, `y = (2,0)`: every `u = (2k,0)` has
`codeg(v,u) >= n-1` and `codeg(u,y) >= n-1`, so `A(v,y) = Theta(n^3)` against a mean of
`Theta(n^2 log^2 n)`. One chosen vertex gives `Theta(n)` vertices a `Theta(n)` jump, and all
of them are top-weighted in `v`'s neighbourhood. **Answer to the posed question: positively
clustered, maximally so; not negatively associated.** Any independence or negative-association
argument is dead.

**But the clustering is bounded (Lemma D).** `A(v,y) <= 54 n^3` uniformly, versus the trivial
`Delta_2 · 2D = O(n^3 log n)`. The proof is three lines: the count
`#{u : s(v,u) = s} <= 16n` is **uniform in `s`**, so `sum_u 1/s(v,u)^2 <= 16n·pi^2/6 < 27n`
converges, and Cauchy–Schwarz pairs the two divergent harmonic sums `sum_u 1/s(v,u)`,
`sum_u 1/s(u,y)` into one convergent one.

**The saved logarithm is exactly the one needed.** Feeding `J = O(n^3)` and
`Var <= (max A)(mean A) = O(n^5 log^2 n)` into Freedman gives failure probability
`exp(-Omega(sigma^2 log^{3/2} n))`, which beats `N^{-1-c}` once `sigma >> (log n)^{-1/4}`.
Compare Theorem 2: pointwise budget `sigma sqrt(log n)` against requirement
`log n / log log n` (deficit `sqrt(log n)/log log n`); averaged budget
`sigma log^{3/2} n` against requirement `~log n` (surplus `sigma sqrt(log n)`). **The averaged
statistic beats the pointwise one by exactly a factor `log n`, and Lemma D is the source.**

Had the trivial bound `O(n^3 log n)` been the truth, `d/(2J) = O(sigma sqrt(log n))` and the
averaged programme would have died with the pointwise one. It came down to one logarithm.

## A11. Fourth candidate: the same for `l = 2` — FAILED, and the failure is located

`W_2(v) = sum_{u ~_2 v} e(u)` against budget `Theta(sigma n^2 log n)`. Two increment terms:

| term | bound | verdict |
|---|---|---|
| existing neighbours move, `sum_{u ~_2 v} codeg(u,y)` | worst case is the `d_2(v)` vertices smallest in `s(·,y)`; by the same uniform count `K = Theta(sqrt(log n))` and the sum is `O(n^2 log log n)` | **fine**, surplus `sigma log n/log log n` |
| new neighbours arrive, `sum_{u in P(v,y)} e(u)`, `\|P\| <= Delta_2 = n(1+o(1))` | crude cap gives `n^2 log n` — short by `1/sigma`; *typical* excesses give `n^2 (log n)^{1/4}` even fully aligned — fine | **open** |

Attempted rescues of the second term, both refuted:

- **Cauchy–Schwarz against the global scalar `sum_u e(u)^2 = O(n^4 sqrt(log n))`** gives
  `sqrt(|P|)(sum e^2)^{1/2} = n^{5/2}(log n)^{1/4}`, short by `sqrt(n)`. It assumes worst-case
  alignment, which is exactly what has to be excluded, so it cannot work.
- **Reuse of Lemma D.** Lemma D bounds a `codeg(v,·)`-weighted sum. `P(v,y)` is an
  **unweighted** set of `Theta(n)` collinear points (the lattice points of the perpendicular
  bisector of `v,y`). The weights are what made Cauchy–Schwarz converge; without them the
  argument gives nothing.

So the obligation has moved from "some unspecified correlation" to a single sharp question
about **one line**: are the lattice points of the perpendicular bisector of `v,y`
systematically exceptional? By §5.1 exceptional vertices are produced along
short-primitive-direction lines, and a bisector is such a line, so the mechanism for positive
correlation is present and undismissed.

Two substantive attempts were used in this pass (A10 succeeded for `l = 3`, A11 failed for
`l = 2`). That is the budget. The session stops, and the blocker is archived in `HANDOFF.md`
rather than replaced by another exponent fit.

## A12. What was deliberately not done

- No new simulation campaign. `s8_joint.c` computes a deterministic quantity `A(v,y)` exactly
  at `n = 32,48,64`; it was used to identify the dependence structure (and to catch a fitting
  error of my own: `sd_y(A)` is `Theta(n^2 log^2 n)`, not `Theta(n^3)` — the two are within a
  factor 4 at these `n`, and mistaking them would have made the averaged programme look dead).
- No attempt to discharge (H-surv), which remains the assumption under Theorem 2.
- No attempt on the tolerance-compounding constant of §5.5 line 6.
