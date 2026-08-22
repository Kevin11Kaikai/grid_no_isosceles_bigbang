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
