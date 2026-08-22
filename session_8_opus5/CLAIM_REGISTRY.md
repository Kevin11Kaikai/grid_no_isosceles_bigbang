# Claim registry — Session 8

Status is exactly one of **PROVED / CONDITIONAL / EMPIRICAL / FALSIFIED / OPEN**.
"Proved" means a complete argument is written in `THEOREM_AND_PROOF.md`.

---

## Structure of the Bennett–Bohman argument at `r = 3`

| # | claim | status | where |
|---|---|---|---|
| S1 | `d_{{v,y} up 3}(i)` is non-increasing in `i`; hence stopping condition (S) holds deterministically at `r = 3` given `Delta_2(H) <= D_{2 up 3}` | **PROVED** | §1.1 (1.1) |
| S2 | `c_{3,3->2}(v,v',i)` is non-increasing; hence that instance of (C) is deterministic given `Gamma(H) <= C_{3,3->2}` | **PROVED** | §1.1 |
| S3 | at `r = 3` the `dlemma` reverse induction is empty and `clemma` reduces to the single dynamic case `c_{2,2->1}` | **PROVED** (reading of ind.tex 773–889) | §1.1 (1.2) |
| S4 | `d_2` is consumed only as a global average, a local average over `Theta(d_l(v))` vertices, and a crude step-size cap — never pointwise at `o(1)` relative accuracy | **PROVED** (complete audit, table §1.2) | §1.2 (1.3) |
| S5 | "`Delta_2`/`Gamma` are stated as pointwise maxima but consumed as edge-weighted averages, so averaging them helps" | **FALSIFIED** — they are initial conditions for monotone quantities; there is nothing dynamic to average | ATTACK_LOG A1 |

## Arithmetic of `H_n`

| # | claim | status | where |
|---|---|---|---|
| G1 | `Delta_2(H_n) = n(1+o(1))`; specifically `n-1 <= Delta_2 <= n + n^{o(1)}` | **PROVED** | Lemma 1(a),(b) |
| G2 | `\|A_v\| >= floor((n-1)/2)` and `codeg(v,y) >= n-1` on `A_v`, with pairwise disjoint completion sets | **PROVED** | Lemma 1(b) |
| G3 | `B_v(tau) = #{y : codeg(v,y) > tau} <= C_0 n^2 (log n)/tau` | **PROVED** | Lemma 1(c) |
| G4 | `D(H_n) = Theta(n^2 log n)`; hence `D^{1/2}/Delta_2 = Theta(sqrt(log n))` | **PROVED** (upper bound in full; lower bound by the matching bisector count) | Lemma 1(d) |
| G5 | the one-step increment of `d_2(v)` is Pareto(1)-tailed truncated at `n`, with mean `Theta(log n)`; the `log` in `D` is the harmonic sum over primitive-direction scales | **PROVED** (restatement of G3+G4) | §1.4 |
| G6 | measured constants: `Delta_2/n ∈ [1.13, 1.30]`, `2D/N ≈ 4.75 ln n - 2.3`, `max_tau B_v(tau) tau/n^2 <= 10.3` for `n = 64..512` | **EMPIRICAL** (exact computation, `s8_tail.c`) | §1.3 table |

## The barrier

| # | claim | status | where |
|---|---|---|---|
| B1 | (H-surv): a fixed `Theta(n)` set and a fixed grid line each retain a constant fraction while a constant fraction of the grid survives | **CONDITIONAL** — assumed, not proved. Measured ratio `\|A_v ∩ V(i)\|/(q\|A_v\|)` = 0.27, 0.25, 0.94/0.70/1.27 | §III hypothesis |
| B2 | Given (H-surv): for any admissible tolerance and any horizon `>= t_0 N/D^{1/2}`, `-log P[v violates (V), l=2] <= C sigma sqrt(log n) log log n = o(log N)` | **CONDITIONAL on B1**, otherwise **PROVED** | Theorem 2 |
| B3 | Given (H-surv): `E[# vertices violating (V) for l=2] >= N^{1-o(1)}`; the four conditions of ind.tex line 720 are jointly unsatisfiable for `H_n` at any horizon `Omega(n/sqrt(log n))` | **CONDITIONAL on B1**, otherwise **PROVED** | Corollary 2.1 |
| B4 | Pointwise dynamic concentration of `d_2` at `o(1)` relative accuracy, established by a union bound over vertices, is impossible for `H_n` — **for every concentration inequality**, because the probability of the bad event is bounded *below* | **CONDITIONAL on B1**, otherwise **PROVED** | Theorem 2 |
| B5 | the deficit is exactly `sqrt(log n)/log log n`, and its source `D^{1/2}/Delta_2 = Theta(sqrt(log n))` is the same `sqrt(log n)` that separates `n/sqrt(log n)` from `n` | **PROVED** given B2 | Remark 2.2 |
| B6 | `max_v d_2^+ / mean_v d_2^+` is a large constant (1.73–2.20) rather than `1+o(1)`, and `(max-mean)/n` tracks `2 log n / log log n` | **EMPIRICAL** (`s8_proc.c`, `n = 64,128,256`, 3 seeds, 4 values of `alpha`) | §III table |
| B7 | random or structured sparsification of the ground set cannot improve the ratio `D^{1/2}/Delta_2` | **PROVED** for random (exact invariance); **PROVED** for structured at density `Omega(1/polylog)` (pigeonhole on horizontal lines) | ATTACK_LOG A5 |

## The averaged replacement

| # | claim | status | where |
|---|---|---|---|
| P1 | crude cap `max_v d_2(v) <= s_2^+ log^{1/2} n` holds whp, with exponent `Omega(log n log log n)` | **CONDITIONAL on B1**, otherwise **PROVED** | Prop 3(3a) |
| P2 | condition (P) on `\|V(i)\|` is unaffected by the barrier; failure probability `exp(-Omega(n^{1-o(1)}))` | **PROVED** given P1 | Prop 3(3a) |
| P3 | the neighbourhood average `Sigma_l(v)/((l-1)d_l(v))` concentrates with failure probability `exp(-Omega(n))`, so the union bound over vertices is affordable for it | **CONDITIONAL** — the Chernoff step assumes a degree of independence among `{J_u}` that is argued but not audited | Prop 3(3b) |
| P4 | the global scalar `sum_v d_2(v)` concentrates with vast margin | **PROVED** (budget `Theta(sigma n/log n)` jump-units) | Prop 3(3c)(1) |
| P5 | the drift of `Z_l^-(v)` needs a quasirandomness statement: that `v`'s evolving 2-neighbourhood does not over-sample the vertices with large `d_2` | **OPEN** — this is the single remaining obligation | Prop 3(3c)(2), HANDOFF |

## Bottom line

| # | claim | status |
|---|---|---|
| **R1** | `C(n) = Omega(n)` | **OPEN** — not proved, not falsified |
| **R2** | `C(n) = Omega(n/sqrt(log n))` (Jánosik et al., alteration) | known, unimproved by this session |
| **R3** | any strict improvement of the lower bound on `C(n)` | **not obtained** |
| **R4** | random greedy on `H_n` can be analysed by pointwise dynamic concentration of `d_2` | **FALSIFIED** (conditional on B1) |

---

## Wording rules in force

- "asymp / Theta" is used only where both bounds are proved (G1, G3, G4, G5).
- "with high probability" is used only for statements with an explicit failure probability.
- "**new**" is not claimed anywhere. Theorem 2's novelty is `PLAUSIBLE, UNVERIFIED`
  (see LITERATURE_NOTES: Guo–Warnke was not read in full).
- "**impossible**" appears only in B4, and it names the exact strategy ruled out: *pointwise
  dynamic concentration of `d_2(v)` at `o(1)` relative accuracy, established by a union bound
  over the `N` vertices*. It does **not** rule out: averaged conditions, self-correcting
  error functions, non-greedy constructions, or any argument that does not union-bound over
  vertices.

---

# Closure pass — additional claims

## Classification of Theorem 2 (asked and answered)

| # | claim | status |
|---|---|---|
| T2a | Theorem 2 is a **conditional obstruction theorem**: complete proof given (H-surv); probability of the bad event bounded **from below**, so not a heuristic; says nothing about `C(n)` itself | **settled** (ATTACK_LOG A9) |
| T2b | Theorem 2 is **not** a new grid theorem and must not be described as one | **settled** |
| T2c | novelty: Guo–Warnke (arXiv:2104.07854) read at theorem level, contains neither a relaxation of BB's hypotheses nor a barrier statement | **VERIFIED for that source**; overall novelty still `PLAUSIBLE, NOT EXHAUSTIVELY VERIFIED` |

## The correlation obligation

| # | claim | status | where |
|---|---|---|---|
| C1 | `W_l(v,i) = sum_u m_v(u) e(u,i)`, and for `l = 3` its martingale increment is exactly `A(v,y) - E_y[A]` with `A(v,y) = sum_u codeg(v,u) codeg(u,y)`; the correlation obligation for `l = 3` is thereby reduced to a **deterministic** lattice sum | **PROVED** | §5.0 |
| C2 | exceptional vertices and `v`'s neighbours are **positively clustered**, maximally: `v=(0,0)`, `y=(2,0)` gives `A(v,y) = Theta(n^3)` vs mean `Theta(n^2 log^2 n)`, one step moving `Theta(n)` coordinates coherently. **Negative association is FALSE for `H_n`** | **PROVED** (explicit counterexample) | §5.1 |
| C3 | **Lemma D:** `A(v,y) <= 54 n^3 + n^{2+o(1)}` uniformly in `v,y` — one full logarithm below the trivial `Delta_2·2D = O(n^3 log n)`. Mechanism: `#{u : s(v,u)=s} <= 16n` is uniform in `s`, so `sum_u s(v,u)^{-2} < 27n` converges, and Cauchy–Schwarz pairs two divergent harmonic sums into one convergent one | **PROVED** (elementary, self-contained) | §5.2 |
| C4 | **Lemma C:** given the crude cap and Lemma D, `\|W_3(v,i)\| <= 2 d_3(v) tol` with failure probability `exp(-Omega(sigma^2 log^{3/2} n))`, affordable under the union bound over `N` vertices whenever `sigma >> (log n)^{-1/4}`. The `l = 3` half of obligation (Q) is closed | **PROVED** given C3 and Prop 3(3a) | §5.3 |
| C5 | the averaged statistic has jump budget `sigma log^{3/2} n` where the pointwise one had `sigma sqrt(log n)` — a gain of exactly `log n`, sourced entirely in Lemma D | **PROVED** given C3, C4, Thm 2 | §5.3 |
| C6 | the `l = 2` half: the *existing-neighbour* term is `O(n^2 log log n)` against budget `Theta(sigma n^2 log n)` | **PROVED** | §5.4(i) |
| C7 | the `l = 2` half: the *new-neighbour* term `sum_{u in P(v,y)} e(u)`, `\|P\| = codeg(v,y) <= n(1+o(1))`, is **not controlled**. Crude cap short by `1/sigma`; Cauchy–Schwarz against `sum_u e(u)^2` short by `sqrt(n)`; Lemma D inapplicable (`P(v,y)` is unweighted) | **OPEN — the single remaining obligation** | §5.4(ii), HANDOFF |
| C8 | measured: `max_y\|A - E_y A\|/n^3` = 2.264, 2.154, 2.189 and `E_y A/(n^2 log^2 n)` = 11.61, 12.17, 12.46 at `n = 32,48,64` | **EMPIRICAL** (exact, `s8_joint.c`) | §5.1–5.2 |
| C9 | if C7 were closed, the horizon would be capped by the `l = 3` pointwise condition plus tolerance compounding at `t = O(sqrt(log log log n))`, giving `\|I\| = Theta(n sqrt(log log log n)/sqrt(log n))` | **CONDITIONAL** — recorded, explicitly **not claimed**; rests on C7, (H-surv), Prop 3(3b) and the compounding constant | §5.5 |

## Bottom line, updated

| # | claim | status |
|---|---|---|
| **R1** | `C(n) = Omega(n)` | **OPEN** |
| **R2** | `C(n) = Omega(n/sqrt(log n))` | known; **unimproved by this session** |
| **R3** | any strict improvement of the lower bound | **not obtained** |
| **R4** | pointwise dynamic concentration of `d_2` works for `H_n` | **FALSIFIED** (conditional on B1) |
| **R5** | `{e(u)}` are negatively associated or independent enough for a first-moment argument | **FALSIFIED** (C2, unconditional) |
| **R6** | the averaged programme's `l = 3` obligation | **CLOSED** (C4) |
| **R7** | the averaged programme's `l = 2` obligation | **OPEN** (C7) — the one remaining |

## Wording rules, updated

- Lemma D and C2 are **unconditional and proved**; they may be stated flatly.
- Lemma C is proved *given* Lemma D and the crude cap, which is itself conditional on
  (H-surv). Quote it as "conditional on (H-surv)".
- **"new" is still not claimed anywhere.** Lemma D is elementary; its ingredients
  (`r_2(d) = d^{o(1)}`, collinear-point counts, Cauchy–Schwarz) are all standard, and only the
  assembly is this session's.
- `Theta(n sqrt(log log log n)/sqrt(log n))` must always appear with the word **conditional**
  and with C7 named. It is not a bound on `C(n)`.

---

# Q2 pass — additional claims

| # | claim | status | where |
|---|---|---|---|
| E1 | **Lemma E(a):** for a line `L` and `z ∉ L`, `sum_{u∈L} codeg(u,z) <= 10 n^{3/2} + n^{1+o(1)}` — a factor `sqrt(n)` below the trivial `\|L\| Delta_2`. Mechanism: on a line `a_s := #{u∈L : s(u,z)=s} <= 8s` *and* `sum_s a_s <= n`, so `sum_s a_s/s <= 8S + n/S <= 6 sqrt(n)` | **PROVED** (elementary, unconditional) | §6.1 |
| E2 | **Lemma E(b):** for `z ∈ L`, `sum_{u∈L} codeg(u,z) <= 4 n^2/s_L^2 + n^{1+o(1)}`, and this is **not improvable**: one chosen vertex on the bisector line gives every one of `Theta(n)` collinear vertices `Theta(n)` new 2-edges in one step | **PROVED** | §6.1 |
| E3 | counterexample search against E1/E2: `max sum/n^{3/2}` = 3.11, 2.72, 2.32, 1.97 (decreasing) and `max sum·s_L^2/n^2` = 1.66, 1.27, 1.03, 0.89 (bounded) at `n = 48,96,192,384`, all lines of primitive direction of sup-norm `<= 6`. **No counterexample found** | **EMPIRICAL** (exact, `s8_line.c`) | §6.1 |
| F1 | reformulation: (Q2) needs no cancellation. Bounding `sum_{u∈L}\|e(u,i)\|` suffices (§5.4), and via Cauchy–Schwarz that follows from the per-line second moment `Phi_L = sum_{u∈L} e(u,i)^2`, which is subset-monotone and hence immune to the random-subset problem that blocks the signed formulation | **PROVED** | §6.0 |
| F2 | **Theorem F:** for `sigma = o(1)` with `sigma log log n -> ∞`, `Phi_L(i) <= kappa sigma^2 n^3 log^2 n` for **every** line `L` and every `i <= T`, whp. Hence condition (A2) for `l = 2` holds. **Obligation (Q2) is discharged** | **PROVED**, using only condition (P), Lemma 1(c) and Lemmas D/E — **not** (H-surv), **not** the crude cap | §6.2 |
| F3 | the binding constraint in Theorem F is the **jump count** for line steps (budget `Theta(sigma log n)` vs hazard `Theta((log n)^{-1/2})`, exponent `Theta(sigma log n log log n)`), not the quadratic variation (margin `(log n)^{1/2}`) nor the ordinary step size (margin `n^{1/4}`) | **PROVED** | §6.3 |
| F4 | the line lemma needs **no** summation over primitive directions or scales — the application uses one line at a time and the `O(n^4)` lines are handled by a union bound costing `5 log n`, already paid. No logarithm is lost | **PROVED** | §6.3 |
| F5 | the stopped bound (6.4) is essential: without it the line-step jump would be `max\|e\| · n^2 = n^3 log n`, giving jump budget `Theta(1)` and failure | **PROVED** (audit) | §6.2 |
| H1 | Theorem F is **too weak for (H-surv) by exactly `sqrt(log n)`**: (H-surv) needs line-average `d_2 = O(s_2)`, i.e. `sum_{u∈L}\|e\| = O(n^2 sqrt(log n))`; Theorem F gives `Theta(sigma n^2 log n)` | **PROVED** | §6.4(a) |
| H2 | the direct (signed) route to (H-surv) meets the **identical Theorem 2 barrier**: budget `Theta(eps sqrt(log n))` vs requirement `log n/log log n`, deficit `sqrt(log n)/log log n` | **PROVED** | §6.4(b) |
| H3 | **Corollary 6.1:** averaging over a *line* does not help — the line-average of `d_2` obeys the same barrier as the pointwise value. A line is the extremal set, because exceptional jumps are coherent along lines (E2); the `l = 3` case survived only because `codeg(v,·)` weights spread mass over the whole grid | **PROVED** | §6.4 |
| H4 | **(H-surv) is not needed by the positive programme.** It is required only by the barrier Theorem 2 (a *lower* bound on the hazard). Theorem F, Lemma C and Prop 3(3a) all need only an *upper* bound on the hazard | **PROVED** (re-audit) | §6.4(c) |
| H5 | **CORRECTION to P1.** The crude cap `max_v d_2(v) <= K s_2` is **unconditional** given (P) and Lemma 1(c), with `K = Theta(sqrt(log n)/log log n)` and exponent `Theta(log n log log n)`. P1 was previously marked CONDITIONAL on B1; that was wrong — an upper bound on a failure probability needs an upper bound on the hazard, not a lower one | **PROVED** (supersedes P1) | §6.4(c) |
| H6 | Theorem 2 must remain labelled **conditional permanently**: (H-surv) is its genuine hypothesis and Corollary 6.1 shows the line technology cannot discharge it | **settled** | §6.4 |
| K1 | `c_{2,2->1}(v,v') <= C_{2,2->1}` for `H_n` — the last unverified stopping-time condition | **OPEN — the single remaining obligation** | §6.5, HANDOFF |
| K2 | every `sigma`-constraint in the programme (`sigma >> (log n)^{-1/4}` for Lemma C; `sigma log log n -> ∞` for Theorem F; `sigma_{3,0} >= C/log log n` for `l = 3`) is met by `sigma = (log log n)^{-1/2}` | **PROVED** (arithmetic) | §6.5 |

## Bottom line, updated

| # | claim | status |
|---|---|---|
| **R1** | `C(n) = Omega(n)` | **OPEN** |
| **R2** | `C(n) = Omega(n/sqrt(log n))` | known; **still unimproved** |
| **R3** | any strict improvement of the lower bound | **not obtained** |
| **R7** | the averaged programme's `l = 2` obligation | **CLOSED** (F2) — supersedes the previous OPEN |
| **R8** | (H-surv) is dischargeable by line-averaging | **FALSIFIED** (H2, H3) |
| **R9** | (H-surv) is needed for a bound on `C(n)` | **FALSIFIED** (H4) — it gates only the barrier |
| **R10** | `c_{2,2->1}` for `H_n` | **OPEN** — the one remaining |

## Wording rules, updated

- Lemma E and Theorem F are **proved** and may be stated flatly, with their hypotheses:
  Theorem F holds *for `i <= T`*, i.e. on the stopped filtration, and needs condition (P).
- **"new" is still not claimed.** No literature was reopened in this pass, so the novelty
  status of Part V is inherited: `PLAUSIBLE, NOT EXHAUSTIVELY VERIFIED`. Lemma E is elementary.
- Theorem 2 is a **conditional obstruction theorem** and now permanently so (H6).
- The conditional arithmetic of §5.5 (`n sqrt(log log log n)/sqrt(log n)`) is **still not
  claimed**; it now depends on K1 and on the compounding constant rather than on (Q2).
