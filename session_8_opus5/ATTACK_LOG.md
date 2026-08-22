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

---

# Q2 pass

## A13. Reformulating Q2 so that no cancellation is needed — the move that unlocked it

The obligation as first written asked for a **signed** bound on `sum_{u ∈ P(v,y)} e(u,i)`.
That formulation is unattackable, for a reason worth recording: `P(v,y)` is a *random*,
`F_i`-measurable subset of the deterministic line `L(v,y)` (only the points that still survive
and whose 3-edge has not yet shrunk join `v`), and cancellation in a sum over `L` says nothing
about cancellation in a sum over a random subset of `L`.

The fix is to notice that §5.4 never needed cancellation: with typical excesses the bound holds
**even with all signs aligned**, with a surplus of `sigma (log n)^{3/4}`. So the target becomes
`sum_{u ∈ L} |e(u,i)|`, and by Cauchy–Schwarz that follows from a bound on the **per-line
second moment** `Phi_L = sum_{u ∈ L} e(u,i)^2`, which is subset-monotone and hence immune to
the random-subset problem.

Route 2 of the old handoff (a per-line second moment) is therefore the right route, and route 1
(exchange sums, bound `sum_{u∈L} codeg(u,z)`) supplies its key input rather than being an
alternative to it.

## A14. First attempt: Lemma E and the `Phi_L` supermartingale — SUCCEEDED

**Lemma E** (proved, §6.1): for a line `L` and `z ∈ [n]^2`,
```
   z ∉ L :  sum_{u∈L} codeg(u,z) = O(n^{3/2})        z ∈ L :  sum_{u∈L} codeg(u,z) = O(n^2/s_L^2).
```
Proof: on a line the count `a_s = #{u ∈ L : s(u,z) = s}` obeys `a_s <= 8s` (the `8s` lines
through `z` of scale `s` each meet `L` once, provided `z ∉ L`) *and* `sum_s a_s <= n`.
Maximising `sum_s a_s/s` under both gives `8S + n/S <= 6 sqrt(n)` at `S = sqrt(n)/2`. Off the
line the total is a factor `sqrt(n)` below the trivial `|L| Delta_2 = n^2`.

Case (b) is not improvable and is exactly the feared event: **if the chosen `y_j` lies on the
bisector line, every one of the `Theta(n)` collinear points of `L` receives `Theta(n)` new
2-edges in a single step.** The proof handles it not by bounding the step but by *counting*
such steps.

**Theorem F** (proved, §6.2): `Phi_L(i) <= kappa sigma^2 n^3 log^2 n` for every line and every
`i <= T`, whenever `sigma = o(1)` and `sigma log log n -> ∞`. Ingredients:

- Doob decomposition; the compensator is `O(n^3 sqrt(log n)/q)`, a factor
  `sigma^2 (log n)^{3/2}` below the budget.
- **Stopped filtration** (6.4): before `T_Phi`, `sum_{u∈L}|e| <= sqrt(|L| d_Phi)`. This is what
  keeps the line-step jump at `sigma n^3 log n` instead of the crude `max|e| · n^2 = n^3 log n`;
  without it the jump budget would be `Theta(1)` and the whole argument would fail.
- Ordinary steps: Freedman with `C_ord = O(sigma n^{11/4} log n)` and
  `V_qv = O(sigma^2 n^6 (log n)^{5/2}/q)`; margins `n^{1/4}` and `(log n)^{1/2}` respectively.
- Line steps: jump budget `g_L = Theta(sigma log n)` (6.7) against hazard
  `mu_L = Theta((log n)^{-1/2})` (6.8); exponent `Theta(sigma log n log log n)`, clearing the
  `O(n^4)`-line union bound by `log log n`.

Crucially Theorem F uses **neither (H-surv) nor the crude cap** — only the vertex-count
condition (P), Lemma 1(c), and Lemmas D/E.

**Counterexample search** (`experiments/s8_line.c`, all lines of primitive direction of
sup-norm `<= 6`, `n = 48,96,192,384`): `max sum/n^{3/2}` = 3.11, 2.72, 2.32, 1.97, decreasing;
`max sum·s_L^2/n^2` = 1.66, 1.27, 1.03, 0.89, bounded. **No counterexample.** Computation was
used only for this search, as instructed.

## A15. Second attempt: substituting Theorem F into (H-surv) — FAILED, and the failure is exact

(H-surv) needs a fixed line to retain a constant fraction of its vertices, which requires the
**line-average of `d_2` to be `O(s_2)`**, i.e. `sum_{u∈L}|e(u,i)| = O(n^2 sqrt(log n))`.
Theorem F gives `Theta(sigma n^2 log n)` — too large by `Theta(sigma sqrt(log n))`, and
shrinking `sigma` to repair it contradicts `sigma log log n -> ∞`. **The gap is exactly
`sqrt(log n)`.**

Trying instead the *signed* line-sum (which needs only constant relative accuracy) runs
straight into Lemma E(b): one line step moves it by `Theta(n^2)`, so the jump budget is
`Theta(eps sqrt(log n))` against hazard `Theta((log n)^{-1/2})`, exponent
`Theta(sqrt(log n) log log n)` — short of `log N` by `sqrt(log n)/log log n`, **the identical
deficit and mechanism as Theorem 2**.

> **Corollary 6.1.** Averaging over a *line* does not help: the line-average of `d_2` obeys the
> same barrier as the pointwise value. A line is the extremal set for this, because the
> exceptional jumps are coherent along lines (Lemma E(b)); what saved the `l = 3` case in
> Part V was that the weights `codeg(v,·)` spread mass over the whole grid.

**But the substitution turned out to be unnecessary,** and this is the pass's second finding.
Re-auditing the uses of (H-surv):

- Theorem 2 (barrier) genuinely needs it — a *lower* bound on the failure probability needs a
  *lower* bound on the hazard. Theorem 2 is negative and feeds nothing.
- The crude cap Prop 3(3a) does **not**: an upper bound on the failure probability needs an
  *upper* bound on the hazard, supplied by Lemma 1(c) and (P). Redone, it gives
  `max_v d_2(v) <= K s_2` with `K = Theta(sqrt(log n)/log log n)` and exponent
  `Theta(log n log log n)`. **Registry entry P1 is corrected from CONDITIONAL to PROVED.**
- Prop 3(3b) is superseded by Lemma C, a Freedman estimate assuming no independence.
- Theorem F does not use it.

So (H-surv) is now only a hypothesis of the barrier, and Corollary 6.1 says the line technology
cannot discharge it. Theorem 2 stays conditional permanently; the positive programme loses
nothing.

Two serious attempts were used (A14 succeeded, A15 failed). The budget is spent; the session
stops and archives the blocker rather than opening a third direction.

## A16. What is deliberately not done

- No literature reopened; the novelty status of Part V and VI is inherited unchanged.
- No simulation campaign. `s8_line.c` computes a deterministic quantity exactly and was run
  only as a counterexample search against Lemma E.
- `c_{2,2->1}` for `H_n` was not verified; it is the single remaining obligation.
- The tolerance-compounding constant of §5.5 line 6 was not computed, so no horizon and no
  bound for `C(n)` is stated.

---

# Claim-safety audit of Theorem F

## A17. What the audit found

Five points were checked. Two repaired, three failed. Theorem F is downgraded to CONDITIONAL
and the verdict returns to `CONDITIONAL_BRIDGE_ONLY`.

**1. Drift decomposition — repaired.** §6.0's "Riemann-sum discrepancy" was a mislabel. The
exact conditional expectation is `E[X_j(u)|F_j] = 2 d_3(u,j)/|V(j)|`, and the drift error
`R^+_i(u) = A^+_i(u) - s_2^+(t_i)` is the accumulated failure of `d_3(u,·)` and `|V(·)|` to sit
on their trajectories, not a quadrature error. Bounded by the two retained conditions:
`|R^+| <= 3(σ_3 + ε_V) s_2^+ + O(log n)`, contributing `O(σ^2 n^3 log n)` to `Phi_L` against a
budget `kappa σ^2 n^3 (log n)^2` — a factor `log n` of room. Closes, but only because (V) for
`l = 3` and (P) are retained.

**2. `d_2^-` — fails, two ways.** §6.2 silently identified `e` with `e^+`. Condition (A2) is
about `d_2 = d_2^+ - d_2^-`.
- *Jump.* `Δ d_2^-(u,j) <= 1 + c_{2,2->1}(u,y_j,j)`, so the line sum Theorem F needs is
  `sum_{u∈L} c_{2,2->1}(u,y,i)`. At the level BB's own condition allows
  (`c_{2,2->1} <= C_{2,2->1} = Theta(s_2/polylog)`) this is `Theta(n^2 sqrt(log n)/polylog)`,
  which **exceeds both branches of Lemma E** and would dominate the entire jump analysis. The
  needed statement is the much weaker **(K1b)** `sum_{u∈L} c_{2,2->1}(u,y,i) = O(n^{3/2})`.
  Unproved. **So Theorem F is not independent of the (K1) family, contrary to §6.5.**
- *Drift.* `E[Δd_2^-(u)] - Δs_2^- = (s_2/(Nq)) e(u,j) + O(σ) Δ s_2^-`. The coefficient
  `s_2/(Nq) = Theta(sqrt(log n)/n)` over `m = Theta(n/sqrt(log n))` steps has total weight
  `Theta(1)` — a genuine `O(1)` feedback, giving a discrete Grönwall amplification `q^{-C}` of
  the martingale part under BB's one-sided bounding. The *true* linearised system has
  eigenvalues `-4t ± 2i` and is stable, so the amplification may be an artefact of one-sidedness;
  which governs `Phi_L` is unresolved. **(K2).**

**3. Re-centring and the PQV — repaired.** Freedman was applied to truncated increments
`ΔΨ 1[ordinary]`, which are not martingale differences; re-centring was omitted. Its cost is
`mu_L × (max line jump) = Theta(σ n^3 (log n)^{1/2})`, negligible against `d_Phi` when
`σ >> (log n)^{-3/2}`. The PQV chain was re-derived line by line and is correct as published:
`Var <= 8 d_Phi E[sum_L xi^2] + 2 E[(sum_L xi^2)^2] = O(σ^2 n^5 (log n)^3/q)`, giving
`d_Phi^2/(4V_qv) = Theta(q σ^2 (log n)^{3/2})`.

**4. `t`- and `q`-dependence — partial.** §6.2 was written at `t = Theta(1)`, silently. Since
`m = Theta(t n/sqrt(log n))`, `t = Theta(1)` reproduces the known bound up to a constant and
proves nothing new; any improvement needs `t -> ∞`. Redone with `q = e^{-t^2}` throughout:
budget `d_Phi(t) = Theta(σ^2 n^3 (log n)^2 t^4 q^3)`, line-jump budget
`g_L = Theta(σ log n · t^2 q^{1/2})`, hazard `mu_L = Theta(t/sqrt(log n))` — **`q`-free**,
because line and ambient set thin by the same factor. The jump-count condition
`σ t^2 q^{1/2} log(σ t q^{1/2} (log n)^{3/2}) >= 5` is maximised near `t^2 = 2` and then decays,
giving with `σ = (log log n)^{-1/2}` the ceiling
```
       t  <=  c sqrt( log log log n ),        m  =  Theta( n sqrt(log log log n) / sqrt(log n) ).
```
So Theorem F′ does support a growing horizon, but only that far. **The asymmetry
`g_L ∝ q^{1/2}` versus `mu_L ∝ q^0` is the exact obstruction.**

**5. Non-regularity and Candidate A — fails.** `H_n` is **not `D`-regular**, and BB's
Theorem 1.1 assumes it is. Exact degrees `2D(v) = sum_y codeg(v,y)`:

| `n` | centre | corner | edge midpoint | max/min |
|---|---|---|---|---|
| 64  | 71 719  | 32 252  | 36 319  | 2.22 |
| 128 | 341 507 | 147 848 | 170 587 | 2.31 |

A constant bounded away from 1, not decreasing. Either regularise by dummy edges — which then
requires re-proving Lemmas 1, D, E for the augmented hypergraph, since they are statements about
grid geometry — or prove a version of BB with vertex-dependent `D(v)`. Neither is done, and the
earlier campaign's dummy-edge regularisation is not imported. **(K3).**

And Candidate A itself is unproved: the variation equations (ind.tex 981, 995, 998) contain
`f_2`, the error function of a variable no longer tracked pointwise, so a replacement
error-function system must be exhibited and the supermartingale property of `Z_V` and `Z_3^±`
re-established under the averaged conditions. Calling this "bookkeeping" in §6.5 was wrong.
**(K4).**

## A18. What survives, and what the audit cost

**Survives, unchanged:** Lemma 1, **Lemma D**, **Lemma E**. All three are deterministic
statements about the geometry of `H_n`, proved from the counting `#{u : s(v,u)=s} <= 16n`,
`r_2(d) = d^{o(1)}`, the collinear-point count and Cauchy–Schwarz. Nothing in the audit touches
them. They remain the two genuinely new pieces of mathematics in the session (D and E), together
with the arithmetic of Lemma 1.

**Also survives:** Theorem 2 (the barrier) and Corollary 6.1 (line-averaging obeys the same
barrier). Theorem 2's statement should read `s_2^+ + C·tol` for an absolute constant `C`, since
by (7.2) the drift error is of the same order as `tol`; the structure and the deficit
`sqrt(log n)/log log n` are unaffected.

**Downgraded:** Theorem F PROVED -> **CONDITIONAL** on (K1b), (K2), (K3), (K4), and restated as
Theorem F′ with explicit `t,q` dependence and horizon ceiling `t = O(sqrt(log log log n))`.
Lemma C PROVED -> **CONDITIONAL** on (K1b): its increment
`ΔW_3 = A(v,y) - E_y[A]` was computed with `Δe(u) = codeg(u,y) - E` and omits the `-Δd_2^-(u)`
term of (7.3), which is the identical defect.

**Verdict:** `NEW_INTERMEDIATE_GRID_THEOREM` -> **`CONDITIONAL_BRIDGE_ONLY`**.

## A19. Lesson recorded

Three of the five defects came from the same habit: verifying that a *single* statistic can be
maintained, and then describing the surrounding re-derivation as bookkeeping. The `d_2^-` half,
the `t`-dependence and the regularity hypothesis were all in that residue. **A condition is not
verified until every variable it is stated in terms of has been carried through, at the horizon
the conclusion needs, under the hypotheses the source theorem actually assumes.**

The `sd/mean` lesson from the previous pass stands and is preserved in HANDOFF: check fits with
scale-free ratios.

(K1) is deliberately **not** attacked in this pass, as instructed.

---

# Obligation (K1b)

## A20. Exact combinatorial description, and the geometric lemma

`c_{2,2->1}(u,y,i)` counts pairs of size-2 edges `f ∋ u`, `f' ∋ y` with `|f ∩ f'| = 1`, i.e.
`f = {u,w}`, `f' = {y,w}`. **Lemma H** (proved) gives the exact characterisation of the evolving
2-graph: for `u,w ∈ V(i)`, `{u,w} ∈ H(i)` iff `∃ z ∈ I(i)` with `{u,w,z} ∈ H_n`. Hence
```
   c_{2,2->1}(u,y,i) = |N(u,i) ∩ N(y,i)|,      S_L(y,i) = e_{G(i)}(L ∩ V(i), N(y,i)).
```
So the object is the number of `G(i)`-edges between a line and the 2-neighbourhood of `y`.

**Lemma G** (proved) is the geometric input: for `w ≠ z`,
`codeg_L(w,z) <= 5` unless `L = B(w,z)` (i.e. unless `z = refl_L(w)`). Two of the three apex
cases put `u` on a **circle** — and a circle meets a line in at most two points, regardless of
arithmetic — while the third puts `u` on the perpendicular bisector, which meets `L` once unless
it *is* `L`. This is the one-level-up analogue of Lemma E's dichotomy, and it is cleaner: the
exceptional case is a single `z` per `w`, with no scale dependence.

## A21. First attempt: the deterministic bound — reaches `n^2 sqrt(log n)/log log n`

Lemma G gives `Λ_L(w,i) <= 5i + |L| 1[refl_L(w) ∈ I(i)]`, hence
```
   S_L(y,i) <= 5 i · d_2(y,i)  +  |L| · #{w ∈ N(y,i) : refl_L(w) ∈ I(i)}
            =  Theta(n^2 sqrt(log n)/log log n)  +  O(n^2/sqrt(log n)).
```
**Finding: the coherent-reflection term is *not* the problem here** — it is smaller than the
bulk term by `log n/log log n`, and (A23) it comfortably meets the requirement. This is the
first place in the session where the reflection mechanism is harmless.

The bulk term is lossy because `Λ_L(w,i) <= 5i` allows every `w` to attain the maximum, while
globally `sum_w Λ_L(w,i) = sum_{u∈L} d_2(u,i) = Theta(n^2 sqrt(log n))`, so the average `Λ_L` is
`Theta(sqrt(log n))` — a factor `n/log n` below the pointwise bound.

## A22. Second attempt: counterexample search — the threshold is ATTAINED, not violated

**Proposition K** (proved). For any set `A` of distinct odd integers in `[1,n)`,
```
      I_A := {(0,0)} ∪ {(a,2) : a ∈ A}
```
is an independent set of `H_n`. The independence check is two Diophantine equations:
`a'(a'-2a) = 4` and `a(a-2a') = 4`, neither solvable for odd `a,a' >= 3`; triples inside the row
are collinear hence degenerate hence not edges.

With `y = (0,2)`, `L` the bottom row and `M` the row `x_2 = 1`: every `w = (x,1)` satisfies
`|w-y|^2 = x^2+1 = |w-(0,0)|^2` and `|w-(a,0)|^2 = (x-a)^2+1 = |w-(a,2)|^2`, so by Lemma H every
surviving `w ∈ M` is a **common** 2-neighbour of `y` and of every `(a,0)`, `a ∈ A`. Hence
`S_L(y,i) >= #{alive a} · (|M ∩ V(i)| - 2)`.

Measured exactly (`experiments/s8_k1b.c`, `V(i)` computed exactly from `I_A`, `A` a greedy Sidon
set of odds; independence verified exhaustively, 0 violating triples):

| `n` | 64 | 100 | 144 | 196 | 256 |
|---|---|---|---|---|---|
| `S_L/n^{3/2}` | 0.4805 | 0.4900 | 0.4815 | 0.4956 | **0.4941** |

**Flat at ≈ 0.49.** So the configuration attains `Theta(n^{3/2})` exactly. It does **not**
falsify (K1b) — an `O(n^{3/2})` upper bound with unspecified constant survives — but it shows:

1. `n^{3/2}` is the right exponent and cannot be improved uniformly over legitimate `I`;
2. **no deterministic proof of (K1b) can have room**: `|I_A| = Theta(sqrt n) << m`, so this is a
   possible state of the process;
3. why the family stops there. `S_L ≈ #{alive a}·|M ∩ V|`; `w = (x,1)` is blocked when
   `x = (a+a')/2` and `(a,0)` is blocked when `2a ∈ A+A` non-trivially. Keeping `M` alive forces
   `|A+A| = o(n)`; keeping the `(a,0)` alive forces `A` 3-AP-free. Going past `n^{3/2}` needs a
   **3-AP-free set of size `omega(sqrt n)` with sumset `o(n)`** — implausible by Freiman/Roth,
   not constructed here, and an additive-combinatorics question outside this session.

A first, buggy version of the harness (`sums` allocated as bytes and indexed as `int`) crashed;
after the fix a 3-AP-free-only greedy was also tried and gives a *smaller* `S_L`, because
without the Sidon/gap conditions the row `M` is almost entirely blocked. The Sidon variant is
the extremal one.

## A23. Correction: the `O(n^{3/2})` threshold in HANDOFF was over-strict

`O(n^{3/2})` was chosen in §7.2(a) merely to match Lemma E(a). Re-deriving what Theorem F′
actually needs from the ordinary-step Freedman term gives
```
        S_L(y,i)  <<  sigma^2 n^2  =  n^2 / log log n        at sigma = (log log n)^{-1/2}.
```
Against this:
- extremal configuration §8.3: `Theta(n^{3/2})` — below by `sqrt(n)/log log n`;
- reflection term of (8.4): `Theta(n^2/sqrt(log n))` — below by `sqrt(log n)/log log n`;
- **bulk term of (8.4): `Theta(n^2 sqrt(log n)/log log n)` — above by exactly `sqrt(log n)`.**

## A24. Outcome

**(K1b) is OPEN — neither proved nor falsified.** It reduces to

> **(K1b′)** `sum_{w ∈ N(y,i)} Λ_L(w,i) <= d_2(y,i) · n/log n` for every line `L`, every
> `y ∈ V(i)`, every `i <= T` — i.e. the average of `Λ_L` over `N(y,i)` is a `1/sqrt(log n)`
> fraction of its deterministic maximum `5i`.

Orientation: typical `Λ_L` is `Theta(sqrt(log n))`; (K1b′) asks for `Theta(n/log n)`; the
deterministic maximum is `Theta(n/sqrt(log n))`. **The margin is `n/log n` and the shortfall is
one square root of a logarithm.** But it is a statement that `N(y,i)` does not over-sample the
high-`Λ_L` vertices — a correlation statement involving a line, exactly the configuration
Corollary 6.1 flags as delicate.

New and proved in this pass: **Lemma H**, **Lemma G**, the deterministic bound (8.4),
**Proposition K**, and the corrected threshold (8.6). Theorem F′ and Lemma C remain
**CONDITIONAL**, now on (K1b′) rather than (K1b), plus (K2), (K3), (K4). Nothing here changes
`C(n)`, still `Omega(n/sqrt(log n))`.

(K2), (K3), (K4), Candidate A and the original (K1a) were not attacked, as instructed.
