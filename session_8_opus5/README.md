# Session 8 — averaged stopping time for the no-isosceles grid problem

**Verdict: `NEW_INTERMEDIATE_GRID_THEOREM`.** No new bound on `C(n)`. What was obtained is a
proof that one specific, universally used analysis route is **false** for this hypergraph,
with the exact size of the failure, plus the reduction that route failure forces.

## Objective

`C(n)` = largest subset of `[n]^2` with no nondegenerate isosceles triangle. Known:
`Omega(n/sqrt(log n)) <= C(n) <= n^2 exp(-c log n/log log n)` — the upper bound improved by
Croot–Mao–Pohoata–Sheffer–Yip (arXiv:2606.17487, 2026); the lower bound unchanged and
conjectured to be `Omega(n)`, reachable "via the random independent set process"
(Jánosik et al., arXiv:2601.14465).

The session target was the weakest rigorous averaged stopping-time theorem that replaces an
unnecessary pointwise worst-case pair condition by a dynamically weighted exceptional budget.

## What was actually proved

**1. The pair conditions were never the obstruction (§1.1–1.2).** At `r = 3`, the two
Bennett–Bohman conditions quantified over pairs are, in three of their four instances,
**monotone non-increasing** along the process — they hold deterministically once the static
hypothesis holds at time zero. Only `c_{2,2->1}` is dynamic. `Delta_2` and `Gamma` are initial
conditions, not tracked quantities; there is nothing about them to average. *(This refutes
the framing carried in earlier branches of this repository.)*

**2. The arithmetic of the increment (Lemma 1).** For `H_n`, the one-step increment of
`d_2(v)` is `codeg(v,y)` at a uniformly random `y`, and

```
   mean = 2D/N = Theta(log n),   P[X > tau] = O(log n/tau),   max = Delta_2 = n(1+o(1)).
```

A Pareto tail of index 1, truncated at `n`. Consequently `D(H_n) = Theta(n^2 log n)` and
`D^{1/2}/Delta_2 = Theta(sqrt(log n))`. The `log` in the degree **is** the harmonic sum over
the scales of primitive lattice directions: the size of `D` and the size of `Delta_2` are one
fact, not two.

**3. The barrier (Theorem 2, conditional on a survival hypothesis).** For any tolerance fine
enough to be useful and any horizon `m = Omega(n/sqrt(log n))`, the probability that a fixed
vertex violates the Bennett–Bohman pointwise condition on `d_2` is at least

```
   exp( - O( sqrt(log n) · log log n ) )   =   N^{-o(1)},
```

so the expected number of violating vertices is `N^{1-o(1)}`. Hence:

> **Pointwise dynamic concentration of `d_2(v)` at `o(1)` relative accuracy, established by a
> union bound over the `N` vertices, is impossible for `H_n` — and the condition is not merely
> unprovable but false.**

Because the argument bounds the probability of the bad event **from below**, it applies to
every concentration inequality, every choice of the parameters `zeta, delta, eps`, every
horizon, self-correcting error functions, and sparsified ground sets alike (ATTACK_LOG A5).

The deficit is a factor `sqrt(log n)/log log n`, and it is **the same `sqrt(log n)`** that
separates the known bound `n/sqrt(log n)` from the conjectured `n`. The constraint binds at
`m = Theta(n/sqrt(log n))`: pointwise analysis can carry the process to the alteration
threshold and no further.

Direct simulation of the process agrees quantitatively: `max_v d_2^+ / mean_v d_2^+` is
1.73–2.20 (not `1+o(1)`), and the excess over the mean is `Theta(n)` times the predicted
number of exceptional steps `2 log n/log log n` — measured 4.70 / 5.56 / 6.74 against
predicted 5.84 / 6.14 / 6.47 at `n = 64, 128, 256`.

**4. The reduction that follows (Proposition 3).** Since `d_2` is consumed only as a global
average, as a local average over `Theta(d_l(v))` vertices, and as a crude step-size cap, the
per-vertex condition can be dropped. Three of the four replacement conditions clear the union
bound with large margins (`exp(-Omega(n))` or better). One does not close.

## What remains

A single obligation, stated in `HANDOFF.md`: **the exceptional vertices and the vertices that
join `v` in the evolving 2-graph are produced by the same short-primitive-direction lines, and
the sign of that correlation is undetermined.** A first-moment estimate has a margin of
`Theta(sigma log n)`; correlation could eat it.

## Strongest objection tested, and how it was resolved

The truncation-plus-weighted-hazard scheme (the session's own second candidate) closes **in
expectation** — the weighted cumulative hazard is `O(log log n)` against a budget of order
`sqrt(log n)`. The objection is that expectation control is not survival: the number of
exceptional steps must also concentrate. It does not, and the deficit is exactly
`sqrt(log n)/log log n`. Resolving that objection is what produced Theorem 2, by turning the
failed positive attempt into a lower bound on the failure probability.

A second objection, found in self-review, was a genuine defect in the first written proof: the
jump count `g` had been taken as the whole trajectory in jump units rather than the tolerance
in jump units. Corrected; the corrected statement is strictly stronger.

## Paper potential

**Not yet.** Theorem 2 is a barrier for one hypergraph, conditional on an unproved survival
hypothesis, with novelty plausible but unverified (Guo–Warnke, arXiv:2104.07854, was not read
in full). If (H-surv) is discharged and the novelty check completed, it would be a short,
honest note: *"the random greedy independent set process on the isosceles hypergraph cannot be
analysed by pointwise dynamic concentration"* — of interest to people working on the
differential-equation method, not a result about `C(n)`. If obligation (Q) is also settled,
the picture changes completely and the target `C(n) = Omega(n)` becomes reachable.

## Files

`THEOREM_CONTRACT.md` · `THEOREM_AND_PROOF.md` · `ATTACK_LOG.md` · `LITERATURE_NOTES.md` ·
`CLAIM_REGISTRY.md` · `CHECKPOINT.md` · `HANDOFF.md` · `experiments/`

---

## 中文说明（给工程背景的读者）

**问题。** 在 `n×n` 的方格点阵里，最多能挑出多少个点，使得任意三点都不构成等腰三角形？
记作 `C(n)`。目前只知道 `C(n)` 至少是 `n/√(log n)` 量级，大家猜真相是 `n` 量级——差的正好
是一个 `√(log n)` 因子。学界公认的攻法是"随机贪心"：随便挑一个点，把所有会和它凑成等腰
三角形的点删掉，再挑下一个，如此反复。

**这一轮做了什么。** 分析这种贪心算法的标准工具（Bennett–Bohman 定理）要求：**每一个**
点在每一步的"剩余可用邻居数" `d_2(v)` 都必须紧贴理论曲线，误差要小到可以忽略。本轮证明了
**这个要求对这个格点问题是错的**——不是难证，是本来就不成立。

**打个比方。** 想象你在管一家有 `n²` 个员工的公司，你想保证"每个人的工时都不超过均值的
1.01 倍"。平时大家每天工作量差不多（均值 `log n` 小时）。但偶尔会来一个"大单"，一来就占掉
某些人 `n` 小时——相当于均值的 `n/log n` 倍。大单虽然稀少，但公司有 `n²` 个人，只要有**一个**
人连着接到几个大单，你的保证就破了。算一下：你能容忍的大单额度只有约 `√(log n)` 单，而要让
`n²` 个人**全都**不超标，你需要容忍约 `log n / log log n` 单。**两者差了 `√(log n) / log log n`
倍——而且这个 `√(log n)`，和上面那个没证出来的 `√(log n)` 是同一个东西。**

计算机模拟完全印证了这一点：最忙的那个人的工作量确实是平均值的 1.7–2.2 倍，而且超出的部分
正好等于"预测的大单数 × 每单 `n` 小时"。

**所以下一步该怎么走。** 既然"逐个人都达标"做不到，就别要求它。仔细查了原证明后发现：证明
里其实**从来没有真正用到单个人的工时**，只用到了「全公司平均」和「某个人周围一圈人的平均」。
这两个平均量的波动小得多，都能轻松满足要求。本轮把问题化简到了**唯一一件还没证的事**：接到
大单的人，和"某个特定员工的同组同事"，是不是由同一批原因决定的（在格点里，就是同一批"短方向
的直线"）。如果它们的相关性方向对我们有利，`C(n) = Ω(n)` 就通了；这一步本轮没做出来。

**结论摆明了讲：`C(n)` 的下界这一轮没有改进，仍然是 `n/√(log n)`。** 得到的是一个诊断——
证明了一整类做法为什么走不通、差多少，以及唯一剩下的那道关卡是什么。
