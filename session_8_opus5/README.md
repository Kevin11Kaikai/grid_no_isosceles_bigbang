# Session 8 — averaged stopping time for the no-isosceles grid problem

**Verdict: `NEW_INTERMEDIATE_GRID_THEOREM`.**

`C(n)` is **unchanged**: the proved lower bound is still `Omega(n/sqrt(log n))`. What the
session produced is a rigorous theorem about `H_n` that removes the identified obstruction
`(Q2)`, a matching negative result about what averaging can and cannot do, and exactly one
remaining obligation.

## Objective

`C(n)` = largest subset of `[n]^2` with no nondegenerate isosceles triangle. Known:
`Omega(n/sqrt(log n)) <= C(n) <= n^2 exp(-c log n/log log n)` — upper bound improved by
Croot–Mao–Pohoata–Sheffer–Yip (arXiv:2606.17487, 2026); lower bound unchanged, conjectured
linear, reachable "via the random independent set process" (Jánosik et al., arXiv:2601.14465).
Target: an averaged stopping-time theorem replacing a pointwise worst-case pair condition by a
dynamically weighted exceptional budget.

## The results, in dependency order

**1. The pair conditions were never the obstruction.** At `r = 3`, three of the four instances
of Bennett–Bohman's pair-quantified conditions are monotone, hence deterministic. `Delta_2` and
`Gamma` are initial conditions, not tracked quantities. *(PROVED.)*

**2. Lemma 1.** The increment of `d_2(v)` is `codeg(v,y)` at uniform `y`: mean `Theta(log n)`,
tail `O(log n/tau)`, max `n(1+o(1))` — Pareto index 1 truncated at `n`. Hence
`D = Theta(n^2 log n)` and `D^{1/2}/Delta_2 = Theta(sqrt(log n))`. *(PROVED.)*

**3. Theorem 2 — a conditional obstruction theorem.** Given (H-surv), pointwise dynamic
concentration of `d_2` at `o(1)` relative accuracy is **false** for `H_n`, for every
concentration inequality, with deficit `sqrt(log n)/log log n`. It is now settled that this
label is **permanent**: (H-surv) is its genuine hypothesis, and Corollary 6.1 shows the line
technology cannot discharge it. *(CONDITIONAL, permanently.)*

**4. The clustering is real and maximal.** For `v = (0,0)`, `y = (2,0)` every `u = (2k,0)` has
`codeg(v,u), codeg(u,y) >= n-1`: one chosen vertex gives `Theta(n)` vertices a `Theta(n)` jump
simultaneously. **Negative association is false for `H_n`.** *(PROVED.)*

**5. Lemma D — but bounded, one logarithm below trivial.**
`A(v,y) = sum_u codeg(v,u) codeg(u,y) <= 54 n^3` uniformly, versus the trivial `O(n^3 log n)`.
Mechanism: `#{u : s(v,u) = s} <= 16n` is uniform in `s`, so `sum_u s(v,u)^{-2} < 27n` converges
and Cauchy–Schwarz pairs two divergent harmonic sums into one convergent one. *(PROVED.)*

**6. Lemma C — the `l = 3` averaged condition closes.** Freedman with Lemma D gives failure
probability `exp(-Omega(sigma^2 (log n)^{3/2}))`. The averaged statistic beats the pointwise one
by exactly `log n`. *(PROVED.)*

**7. Lemma E — the line-restricted version.** For a line `L` and `z ∈ [n]^2`:
```
   z ∉ L :  sum_{u∈L} codeg(u,z) = O(n^{3/2})       z ∈ L :  sum_{u∈L} codeg(u,z) = O(n^2/s_L^2).
```
Off the line this is a factor `sqrt(n)` below the trivial `|L| Delta_2`, because on a line the
count `a_s = #{u ∈ L : s(u,z) = s}` obeys **both** `a_s <= 8s` and `sum_s a_s <= n`, capping
the harmonic sum at `sqrt(n)`. Case (b) is not improvable — it *is* the feared event, a single
chosen vertex on the bisector giving every one of `Theta(n)` collinear vertices `Theta(n)` new
2-edges in one step. *(PROVED; no counterexample found in an exact search.)*

**8. Theorem F — obligation (Q2) is discharged.** For `sigma = o(1)` with
`sigma log log n -> ∞`, the per-line second moment satisfies
`Phi_L(i) = sum_{u∈L} e(u,i)^2 <= kappa sigma^2 n^3 (log n)^2` for every line and every
`i <= T`, whence condition (A2) for `l = 2` holds. Two ideas made it work:
- **No cancellation is needed.** `P(v,y)` is a *random* subset of the bisector line, so signed
  cancellation over the line implies nothing about it. Bounding `sum |e(u)|` via the per-line
  second moment is subset-monotone and sidesteps this entirely.
- **The coherent line event is paid for by a jump count, not a step bound.** Budget
  `Theta(sigma log n)` against hazard `Theta((log n)^{-1/2})`; exponent
  `Theta(sigma log n log log n)`, clearing the `O(n^4)`-line union bound by `log log n`. The
  stopped filtration is essential: without it the jump budget would be `Theta(1)`.

Theorem F uses **neither (H-surv) nor the crude cap** — only the vertex-count condition (P),
Lemma 1(c), and Lemmas D/E. *(PROVED on the stopped filtration.)*

**9. Corollary 6.1 — averaging over a line does not help.** The line-average of `d_2` obeys the
*same* barrier as the pointwise value, with the identical deficit `sqrt(log n)/log log n`. A
line is the extremal set for this, because the exceptional jumps are coherent along lines. What
saved the `l = 3` case was that the weights `codeg(v,·)` spread mass over the whole grid.
*(PROVED.)*

**10. Two corrections.** (i) The crude cap Prop 3(3a) is **unconditional**, not conditional on
(H-surv): an upper bound on a failure probability needs an *upper* bound on the hazard, not a
lower one. `K = Theta(sqrt(log n)/log log n)`. (ii) (H-surv) is **not needed by the positive
programme** at all; it gates only the barrier.

## What remains — exactly one obligation

`HANDOFF.md`, **(K1)**: verify `c_{2,2->1}(v,v',i) <= C_{2,2->1}` for `H_n` — the codegree of a
pair in the evolving 2-graph, the unique genuinely dynamic pair condition at `r = 3`. Typical
value `Theta(log n)` against a requirement of `Theta(s_2/polylog)`, so there is `n/polylog` of
room; but the jump is `Theta(n)` when a chosen vertex lies on a line common to `v` and `v'`,
which puts the budget at `Theta(sqrt(log n))` against `log n/log log n` — **the Theorem 2
shape.** This may well fail; it is the last thing that could.

Also missing, but a computation rather than an open question: the tolerance-compounding
constant of §5.5 line 6, which fixes the horizon. If both were settled the conditional
arithmetic gives `Theta(n sqrt(log log log n)/sqrt(log n))` — **still not claimed.**

## Paper potential

**Not yet, and novelty is not verified.** No literature was reopened in this pass, so the
status of Part V is inherited: `PLAUSIBLE, NOT EXHAUSTIVELY VERIFIED`. Lemmas D and E are
elementary — every ingredient (`r_2(d) = d^{o(1)}`, primitive-direction counts, collinear-point
counts, Cauchy–Schwarz) is standard, and only the assembly is this session's. Theorem 2 is
permanently conditional. What would make a publishable note is (K1) plus the compounding
constant, which together would turn Lemmas C/E and Theorem F into a first improvement of the
lower bound; without them the material is a diagnosis, not a result about `C(n)`.

## Files

`THEOREM_CONTRACT.md` · `THEOREM_AND_PROOF.md` (Parts I–VI) · `ATTACK_LOG.md` (A1–A16) ·
`LITERATURE_NOTES.md` · `CLAIM_REGISTRY.md` · `CHECKPOINT.md` · `HANDOFF.md` ·
`experiments/` (`s8_tail.c`, `s8_proc.c`, `s8_joint.c`, `s8_line.c`)

---

## 中文说明（给工程背景的读者）

**问题。** `n×n` 格点里最多挑多少点不出等腰三角形，记 `C(n)`。已知至少 `n/√(log n)`，猜是
`n`，差一个 `√(log n)`。攻法是随机贪心。

**前两轮的结论。** 逐点控制（要求每个点的邻居数都紧贴曲线）对格点问题**本身就是错的**；改用
平均量后，`l=3` 那一半靠 Lemma D 通了。剩下 `l=2` 那一半：选中一个点 `y` 时，新加入 `v` 的
`Θ(n)` 个邻居**恰好是一条直线上的格点**——`v` 与 `y` 的垂直平分线。

**这一轮把这条直线攻下来了。**

关键有两点。**第一，不需要正负抵消。** 原来的提法要求"带符号的和很小"，但那条线上真正加入的
只是一个**随机子集**，整条线上抵消得再好也不能推出子集上抵消。而其实根本不需要抵消：即使
所有偏差同号，只要它们是**典型大小**就够，还余 `log^{3/4}n`。于是改成控制**每条直线上的
平方和** `Φ_L = Σ_{u∈L} e(u)²`——这个量对子集单调，随机子集的问题自动消失。

**第二，"一条直线同时被打" 这个事件不能靠限制单步大小来对付，要靠数次数。** 新引理（Lemma E）
说：如果被选中的点**不在**那条线上，整条线受到的冲击只有 `n^{3/2}`——比平凡上界 `n²` 小
`√n` 倍；如果**在**线上，就是最坏的 `n²`，无法改进。证明的窍门在于：在一条直线上，"距离尺度
为 `s` 的点数"既 `≤ 8s` 又总共 `≤ n`，两个约束一起把调和和卡在 `√n`。

然后把"在线上"的步数当作**预算**来数：预算 `Θ(σ log n)` 步，而每步落在线上的风险只有
`Θ(1/√(log n))`，指数是 `Θ(σ log n · log log n)`，压得住 `n⁴` 条直线的 union bound。
**Q2 证完了。** 而且这个证明**不需要** (H-surv)，也不需要粗略上界。

**顺带两个发现。** 一，把 (H-surv) 代进去**不成立**，而且差的正好还是 `√(log n)`——因为
「沿一条直线取平均」和「逐点」撞同一堵墙（直线正是最坏的平均集合，大冲击沿直线是同相的）。
二，但 (H-surv) **根本用不着**——它只是那个"负面障碍定理"的假设，对正面路线毫无作用。

**结论直说：`C(n)` 的下界这一轮仍然没有改进，还是 `n/√(log n)`；还不能发论文。** 剩下最后
一件事（`HANDOFF` 里的 K1）：演化中的二元图里，一对点的公共邻居数有没有上界。典型值是
`log n`，要求是 `√(log n)` 量级——余量有 `n/polylog`；但它的跳变结构又是 `√(log n)` 对
`log n/log log n` 的老形状。**这一条很可能过不去，它是最后一个可能挡路的东西。**
