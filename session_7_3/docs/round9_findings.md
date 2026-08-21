# Session 7.3 — Round 9 findings

**Headline: the note ends on a question about Bennett–Bohman's proof. Round 9 tests the
part of it that can be tested, and the answer supports the conjecture: with `Delta_2`,
degree and edge count all held fixed, raising `Gamma` from `O(1)` to `0.33 D` changes the
random greedy output by at most 2.4% — and slightly upward. `Gamma` constrains the
analysis, not the process.**

---

## 9.1 A confounded first attempt — recorded because it misled me

The obvious design: build synthetic 3-uniform `~D`-regular hypergraphs, dial `Gamma` up,
watch `|I|` fall. It appeared to work in reverse — `|I|/BB` *rose* from 0.594 to 0.843 as
the bad-pair fraction went from 0 to 1 (`experiments/r9_synth.c`).

That is an artefact. To give a group of `k` vertices a shared `Gamma`, my construction gave
each hub pair `{a,b}` codegree `k`. So raising the bad fraction also raised `Delta_2` to
`k`, concentrating many edges on few distinct pairs and making the hypergraph *less*
constraining. The measurement was of `Delta_2`, not `Gamma`.

## 9.2 `Gamma` isolated, with a matched control — `VERIFIED_COMPUTATIONAL_RESULT`

The fix is a control that differs in `Gamma` and in nothing else
(`experiments/r9_ctrl.c`):

- **Treatment.** Pair the vertices by a random perfect matching. For each matched pair
  `(v,v')` and each of `H` hub pairs `{a,b}`, add **both** `{v,a,b}` and `{v',a,b}`.
  Then `Gamma(v,v') = H`.
- **Control.** Identical — same edge count, same codegree 2 on every hub pair, same mean
  degree, same padding — except the two edges of each hub pair go to two **independent
  random** vertices, so `Gamma` stays `O(1)`.

`N = 50000`, `D = 200`, 3 seeds:

| `Gamma/D` | 0.00 | 0.07 | 0.23 | 0.33 |
|---|---|---|---|---|
| **treat / control** | 1.0000 | 0.9951 | 1.0094 | **1.0236** |

Concentrating `Gamma` onto a matching of pairs, all the way to a third of the maximum
possible value `D`, costs **nothing**. The largest deviation is `+2.4%`, in the wrong
direction to be a degradation.

## 9.3 The bad-pair fraction does not matter either

Second axis: hold the degree budget `P*H = 60` fixed and trade `Gamma` against the fraction
of bad pairs `P/N` (`experiments/r9_frac.c`):

| `(P, H)` | (1,60) | (2,30) | (4,15) | (10,6) | (20,3) | (60,1) |
|---|---|---|---|---|---|---|
| `Gamma/D` | 0.30 | 0.15 | 0.07 | 0.03 | 0.01 | 0.01 |
| bad fraction | 1/N | 2/N | 4/N | 10/N | 20/N | 60/N |
| treat `|I|` | 7222 | 7152 | 7096 | 7109 | 7079 | 7095 |
| treat/control | 1.0135 | 1.0003 | 1.0004 | 1.0030 | 0.9947 | 1.0000 |

Flat. Neither the size of `Gamma` nor how many pairs carry it moves the greedy output.

## 9.4 Two structural facts that came out of building the experiment

**(a) The rarity of bad pairs is forced, not lucky.** For fixed `v`,

```
    Sum_{v'} Gamma(v,v')  <=  Sum_{ {a,b} in P(v) } (d(a,b) - 1)  <=  D * (Delta_2 - 1)
```

so `#{v' : Gamma(v,v') >= T} <= D*Delta_2/T`. For `H_n`, with `D = 1.81 n^2 ln n`,
`Delta_2 ~ 1.7n`, `Gamma_max ~ 0.52 n^2`, that is `~5.9 n ln n` bad partners out of `n^2`,
i.e. a fraction `Theta(log n / n)`. **Round 8's measured `Theta(1/n)` bad fraction is a
consequence of `Delta_2` being small, not a coincidence of the lattice.** Any hypergraph
with small `Delta_2` automatically has few `Gamma`-bad pairs.

**(b) The regime in question is not testable at any feasible size.** `Gamma ~ D/log D`
exceeds `D^{1-eps}` only once `D^{eps} > log D`. For `eps = 0.1` that needs `D` of order
`10^20`. So no finite experiment can probe the actual gap between `D/log D` and
`D^{1-eps}`; §9.2's extreme `Gamma = Theta(D)` is the strongest available proxy, and it is
a *harder* test than the real one.

## 9.5 What this does and does not show

It shows the **conclusion** of Bennett–Bohman is robust to exactly the hypothesis that
`H_n` violates. Combined with Round 7 (the hypotheses fail by one logarithm, never
polynomially) and Round 8 (the `Gamma` failure is confined to a `Theta(N^{-1/2})` fraction
of pairs), the question the note poses now has direct evidence behind it.

It does **not** show the proof is repairable. BB need `Gamma` small to get *concentration*
of the quantities they track through the process; this experiment measures only the final
`|I|`, which is an average, not a concentration statement. A hypergraph can have a robust
mean and badly behaved fluctuations. And synthetic hypergraphs are not `H_n`: they mimic
the parameters, not the lattice-reflection structure that produces `H_n`'s bad pairs.

> **Honest form: the obstruction is in the proof method, and the conclusion survives the
> violation in every synthetic setting tested. That is evidence the strengthening is true.
> It is not a proof, and it does not tell anyone how to write one.**

## 9.6 Status after Round 9

| item | evidence | tier |
|---|---|---|
| `Gamma` isolated has no effect on greedy up to `Gamma = 0.33 D` | matched-control experiment, 3 seeds | **B** |
| the bad-pair fraction has no effect at fixed degree budget | same | **B** |
| bad fraction `<= D*Delta_2/(Gamma*N)`, so rarity is forced | derived; matches round 8 | **B** |
| `Gamma ~ D/log D` vs `D^{1-eps}` untestable below `D ~ 10^20` | derived | C |
| first synthetic design confounded `Gamma` with `Delta_2` | **correction** | — |
| `C(n) = Omega(n)` | **NOT PROVED** | — |

**Judge PASS 0 / TYPE2 0.** Ninth honest zero on the bound.

`NOVELTY_PRELIMINARY`. Nothing here is a new bound on `C(n)`.
