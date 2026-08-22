# Session 8 — averaged stopping time for the no-isosceles grid problem

**Verdict: `CONDITIONAL_BRIDGE_ONLY`.**

`C(n)` is **unchanged**: the proved lower bound is still `Omega(n/sqrt(log n))`. A claim-safety
audit (Part VII) downgraded the session's main dynamic theorem from PROVED to CONDITIONAL. What
is unconditional is three static lemmas about the geometry of `H_n`, a conditional obstruction
theorem, and a precise map of what is left.

## Objective

`C(n)` = largest subset of `[n]^2` with no nondegenerate isosceles triangle. Known:
`Omega(n/sqrt(log n)) <= C(n) <= n^2 exp(-c log n/log log n)` — upper bound improved by
Croot–Mao–Pohoata–Sheffer–Yip (arXiv:2606.17487, 2026); lower bound unchanged, conjectured
linear, reachable "via the random independent set process" (Jánosik et al., arXiv:2601.14465).
Target: an averaged stopping-time theorem replacing a pointwise worst-case pair condition by a
dynamically weighted exceptional budget.

## Unconditional results

**1. The pair conditions were never the obstruction.** At `r = 3`, three of the four instances
of Bennett–Bohman's pair-quantified conditions are monotone, hence deterministic. `Delta_2` and
`Gamma` are initial conditions, not tracked quantities.

**2. Lemma 1.** The one-step increment of `d_2(v)` is `codeg(v,y)` at uniform `y`: mean
`Theta(log n)`, tail `O(log n/tau)`, max `n(1+o(1))` — Pareto index 1 truncated at `n`. Hence
`D = Theta(n^2 log n)` and `D^{1/2}/Delta_2 = Theta(sqrt(log n))`. The `log` in the degree *is*
the harmonic sum over scales of primitive lattice directions.

**3. Positive clustering is real and maximal.** For `v = (0,0)`, `y = (2,0)` every `u = (2k,0)`
has `codeg(v,u), codeg(u,y) >= n-1`: one chosen vertex gives `Theta(n)` vertices a `Theta(n)`
jump simultaneously. **Negative association is false for `H_n`**, so every independence-based
argument is dead.

**4. Lemma D.** `A(v,y) = sum_u codeg(v,u) codeg(u,y) <= 54 n^3` uniformly, one full logarithm
below the trivial `Delta_2 · 2D = O(n^3 log n)`. Mechanism: `#{u : s(v,u) = s} <= 16n` is uniform
in `s`, so `sum_u s(v,u)^{-2} < 27n` converges, and Cauchy–Schwarz pairs two divergent harmonic
sums into one convergent one.

**5. Lemma E (line-restricted).** For a line `L` and `z ∈ [n]^2`:
```
   z ∉ L :  sum_{u∈L} codeg(u,z) = O(n^{3/2})       z ∈ L :  sum_{u∈L} codeg(u,z) = O(n^2/s_L^2).
```
Off the line, a factor `sqrt(n)` below trivial, because on a line the count
`a_s = #{u ∈ L : s(u,z) = s}` obeys **both** `a_s <= 8s` and `sum_s a_s <= n`. Case (b) is not
improvable — it *is* the coherent event, one chosen vertex on the bisector giving `Theta(n)`
collinear vertices `Theta(n)` new 2-edges in one step. No counterexample found in an exact
search over all short-direction lines, `n = 48..384`.

**6. Corollary 6.1 — averaging over a line does not help.** The line-average of `d_2` obeys the
*same* barrier as the pointwise value, deficit `sqrt(log n)/log log n`, identical mechanism. A
line is the extremal set, because the exceptional jumps are coherent along lines. What saved the
`l = 3` case was that the weights `codeg(v,·)` spread mass over the whole grid.

**7. The crude cap** `max_v d_2(v) <= K s_2` with `K = Theta(sqrt(log n)/log log n)` is
unconditional given the vertex-count condition.

## Conditional results

**Theorem 2 — a conditional obstruction theorem, permanently.** Given (H-surv), pointwise
dynamic concentration of `d_2` at `o(1)` relative accuracy is **false** for `H_n`, for every
concentration inequality, with deficit `sqrt(log n)/log log n`. Corollary 6.1 shows the line
technology cannot discharge (H-surv), so the label cannot be removed. (H-surv) is **not** needed
by the positive programme.

**Theorem F′ and Lemma C — conditional.** Theorem F′ bounds the per-line second moment
`Phi_L(i) = sum_{u∈L} e(u,i)^2` and would give condition (A2) for `l = 2`; Lemma C does the same
for `l = 3`. Both are conditional on (K1b), and Theorem F′ additionally on (K2), (K3), (K4).

## What the audit found

Five points were checked; two repaired, three failed.

| item | outcome |
|---|---|
| exact drift decomposition via `2 d_3(u,i)/\|V(i)\|` | **repaired.** The error is the accumulated failure of `d_3` and `\|V\|` to track, not a quadrature error; `\|R^+\| <= 3(σ_3+ε_V) s_2^+`, costing a factor `log n` less than the budget |
| `d_2^-`, hence the current degree `d_2` | **failed.** The published argument controlled `d_2^+` and silently called it `d_2`. The jump needs (K1b); the drift gives an `O(1)` feedback whose sign is unresolved (K2) |
| re-centring the truncated Freedman step, and the PQV | **repaired.** Re-centring was omitted; it costs `Theta(σ n^3 (log n)^{1/2})`, negligible. The PQV chain is correct as published |
| full `t`- and `q(t)`-dependence | **partial.** §6.2 was written at `t = Theta(1)` and silent about it — which reproduces the known bound up to a constant. Redone, Theorem F′ survives only to `t = O(sqrt(log log log n))`; the ceiling is the asymmetry `g_L ∝ q^{1/2}` vs `mu_L ∝ q^0` |
| non-regularity; complete Candidate A | **failed.** `H_n` is **not `D`-regular** — exact degrees `2D(v)` give centre/corner ratios 2.22 (`n=64`) and 2.31 (`n=128`), a constant not decreasing — and BB's theorem assumes regularity (K3). The remaining re-derivation was called "bookkeeping"; it is not (K4) |

Three of the five defects came from one habit: verifying that a single statistic can be
maintained, then describing the surrounding re-derivation as bookkeeping. **A condition is not
verified until every variable it is stated in terms of has been carried through, at the horizon
the conclusion needs, under the hypotheses the source theorem actually assumes.**

## What remains

`HANDOFF.md` lists all of it: **(K1a)** BB's own `c_{2,2->1}` condition; **(K1b)** the
line-averaged version `sum_{u∈L} c_{2,2->1}(u,y,i) = O(n^{3/2})`, which is what makes Theorem F′
and Lemma C conditional and is the weakest of the four — attack it first; **(K2)** whether the
`d_2^-` feedback compounds as `q^{-C}` or self-corrects as `q^{+4}`; **(K3)** the non-regularity
of `H_n`; **(K4)** a complete proof of the substituted Candidate A.

If all closed, `m = Theta(n sqrt(log log log n)/sqrt(log n))` — a strict improvement by
`sqrt(log log log n)`, **not claimed**. Reaching `C(n) = Omega(n)` needs `t = Theta(sqrt(log n))`,
which the horizon ceiling forbids outright, so a linear bound requires a different treatment of
the line-step hazard, not merely the closure of K1–K4.

## Paper potential

**No.** The only unconditional new content is Lemmas D and E and the arithmetic of Lemma 1, all
elementary — `r_2(d) = d^{o(1)}`, primitive-direction counts, collinear-point counts,
Cauchy–Schwarz — with only the assembly belonging to this session. Novelty was not re-checked in
this pass and remains `PLAUSIBLE, NOT EXHAUSTIVELY VERIFIED`. Theorem 2 is permanently
conditional.

## Files

`THEOREM_CONTRACT.md` · `THEOREM_AND_PROOF.md` (Parts I–VII) · `ATTACK_LOG.md` (A1–A19) ·
`LITERATURE_NOTES.md` · `CLAIM_REGISTRY.md` · `CHECKPOINT.md` · `HANDOFF.md` ·
`experiments/` (`s8_tail.c`, `s8_proc.c`, `s8_joint.c`, `s8_line.c`)

---

## 中文说明（给工程背景的读者）

**问题。** `n×n` 格点里最多挑多少点不出等腰三角形，记 `C(n)`。已知至少 `n/√(log n)`，猜是
`n`，差一个 `√(log n)`。

**这一轮做的是自查，不是新攻。** 上一轮我说「Q2 证完了」，这次按五条逐项复核，**两条修好，
三条没过，主定理降级为有条件**。

**修好的两条。** 一是漂移项：原来我写成"黎曼和的误差"，那是错的——它其实是 `d_3` 和 `|V|`
偏离各自轨道的累积，用保留下来的两个条件能卡住，代价比预算小一个 `log n`。二是截断后
Freedman 需要重新中心化，原文漏了，补上后代价可忽略。

**没过的三条。**

一、**我只控制了 `d_2^+`，却当成了 `d_2`。** 真正要控制的是当前度数 `d_2 = d_2^+ − d_2^-`。
补上 `d_2^-` 之后冒出两个新问题：它的跳变由 `c_{2,2→1}` 决定（于是主定理反而依赖我原本列为
"另一条待证义务"的 K1），它的漂移会把 `e` 反馈回自身、系数是 `Θ(1)`（可能放大也可能自我
修正，未定）。

二、**原来的证明其实是在 `t = Θ(1)` 下写的，而我没说。** 但 `t = Θ(1)` 只能重现已知的界（差
个常数），要改进必须 `t → ∞`。重算之后主定理只能撑到 `t = O(√(log log log n))`——瓶颈是
跳变预算带因子 `q^{1/2}` 而风险不带。

三、**`H_n` 根本不是正则图，而 Bennett–Bohman 的定理要求正则。** 精确算出来：中心点的度数是
角点的 **2.2–2.3 倍**，而且不随 `n` 减小。这一条以前完全没注意到，是四条里最大的。

**保住的：** 三条静态引理（Lemma 1、D、E）完好无损——它们只是格点几何的初等计数，自查完全
没碰到。还有那个障碍定理和"沿直线取平均也没用"的推论。

**结论直说：`C(n)` 下界仍是 `n/√(log n)`，没有改进；不能发论文。** 剩下五条义务全部列在
`HANDOFF.md`，建议先攻 K1b（最弱的一条，也是让主定理变成有条件的那一条）。

这轮学到的教训已写进 handoff：**只验证单个统计量能维持、然后把周边推导称作"记账"，是不行的**
——条件里出现的每一个变量都要走完，走到结论真正需要的时间尺度，并且在原定理真正假设的前提下。
