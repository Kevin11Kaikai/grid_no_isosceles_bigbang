# Session 8 — averaged stopping time for the no-isosceles grid problem

**Verdict: `CONDITIONAL_BRIDGE_ONLY`.**

No new bound on `C(n)`, which remains `Omega(n / sqrt(log n))`. What exists is a conditional
obstruction theorem, one unconditional new lemma about the grid, and a bridge whose `l = 3`
half is closed and whose `l = 2` half is not.

## Objective

`C(n)` = largest subset of `[n]^2` with no nondegenerate isosceles triangle. Known:
`Omega(n/sqrt(log n)) <= C(n) <= n^2 exp(-c log n / log log n)`, the upper bound improved by
Croot–Mao–Pohoata–Sheffer–Yip (arXiv:2606.17487, 2026); the lower bound unchanged and
conjectured linear, reachable "via the random independent set process" (Jánosik et al.,
arXiv:2601.14465). The session target was an averaged stopping-time theorem replacing a
pointwise worst-case pair condition by a dynamically weighted exceptional budget.

## What is proved

**1. The pair conditions were never the obstruction.** At `r = 3`, three of the four instances
of Bennett–Bohman's pair-quantified stopping conditions are monotone non-increasing along the
process, hence deterministic given the static hypothesis. `Delta_2` and `Gamma` are initial
conditions, not tracked quantities. *(PROVED; refutes the framing carried in earlier branches
of this repository.)*

**2. Lemma 1 — the arithmetic.** The one-step increment of `d_2(v)` is `codeg(v,y)` at a
uniform `y`, with mean `2D/N = Theta(log n)`, tail `O(log n/tau)`, and maximum
`Delta_2 = n(1+o(1))`: Pareto index 1, truncated at `n`. Hence `D = Theta(n^2 log n)` and
`D^{1/2}/Delta_2 = Theta(sqrt(log n))`. The `log` in the degree *is* the harmonic sum over
scales of primitive lattice directions. *(PROVED.)*

**3. Theorem 2 — a conditional obstruction theorem.** Conditional on a survival hypothesis
(H-surv), for any useful tolerance and any horizon `m = Omega(n/sqrt(log n))` the probability
that a fixed vertex violates the pointwise condition on `d_2` is at least
`exp(-O(sqrt(log n) log log n)) = N^{-o(1)}`. So the expected number of violators is
`N^{1-o(1)}`: **pointwise dynamic concentration of `d_2` is not merely unprovable for `H_n`,
it is false**, for every concentration inequality, since the bad event's probability is
bounded from below. The deficit is `sqrt(log n)/log log n`.

*This is a **conditional obstruction theorem**, not a new grid theorem.* It says nothing about
`C(n)`; it says one method cannot be applied. Guo–Warnke (arXiv:2104.07854) has now been read
at theorem level and contains neither a relaxation of BB's hypotheses nor a barrier statement,
so the one named novelty risk is eliminated — novelty remains `PLAUSIBLE`, not `VERIFIED`.

**4. The correlation question is answered — positively clustered, maximally.** For
`v = (0,0)`, `y = (2,0)`, every `u = (2k,0)` has `codeg(v,u) >= n-1` and `codeg(u,y) >= n-1`,
so a **single** chosen vertex delivers a `Theta(n)` jump to `Theta(n)` vertices simultaneously,
all of them top-weighted in `v`'s neighbourhood. **Negative association is false for `H_n`**,
and every independence-based argument is dead. *(PROVED, explicit counterexample.)*

**5. Lemma D — but the clustering is capped one logarithm below the trivial bound.**
```
      A(v,y) := sum_u codeg(v,u)·codeg(u,y)  <=  54 n^3          uniformly in v, y,
```
versus the trivial `Delta_2 · 2D = O(n^3 log n)`. Three lines: the count
`#{u : s(v,u) = s} <= 16n` is **uniform in `s`**, so `sum_u s(v,u)^{-2} < 27n` converges, and
Cauchy–Schwarz pairs the two divergent harmonic sums `sum_u 1/s(v,u)` and `sum_u 1/s(u,y)`
into one convergent sum. *(PROVED, unconditional, elementary.)*

**6. Lemma C — and that logarithm is exactly what was needed.** Feeding Lemma D into Freedman
gives failure probability `exp(-Omega(sigma^2 (log n)^{3/2}))` for the neighbourhood-average
condition at `l = 3`, affordable under the union bound over `N` vertices once
`sigma >> (log n)^{-1/4}`. Against Theorem 2: the pointwise budget was `sigma sqrt(log n)`
against a requirement `log n/log log n` (deficit); the averaged budget is
`sigma (log n)^{3/2}` against a requirement `~log n` (surplus). **The averaged statistic beats
the pointwise one by exactly `log n`, and Lemma D is the source.** *(PROVED given Lemma D and
the crude cap, the latter conditional on (H-surv).)*

## What remains — exactly one obligation

`HANDOFF.md`, obligation **(Q2)**: the `l = 2` case needs
`|sum_{u in P(v,y)} e(u)| <= c |P(v,y)| s_2 / (log n)^{3/4}`, where `P(v,y)` is the set of
`Theta(n)` vertices that become 2-neighbours of `v` when `y` is chosen — precisely the lattice
points of **one line**, the perpendicular bisector of `v` and `y`. Lemma D does not apply:
its weights `codeg(v,·)` are what made Cauchy–Schwarz converge, and `P(v,y)` is unweighted.
The margin is generous (typical excesses suffice even fully aligned; only a coherent push to
the crude cap breaks it), so the obligation is sharp rather than hopeless.

**Conditional arithmetic if (Q2) closed** (§5.5, recorded, *not claimed*): the horizon would
then be capped by the `l = 3` pointwise condition plus tolerance compounding at
`t = O(sqrt(log log log n))`, giving `|I| = Theta(n sqrt(log log log n)/sqrt(log n))` — a
strict improvement by `sqrt(log log log n)`. This rests on (Q2), on (H-surv), on the
independence audit of Prop 3(3b), and on the compounding constant. **It is not a bound on
`C(n)`.**

## Strongest objection tested

That the averaged programme would inherit the same heavy tail as the pointwise one. It does
not, and the reason is quantitative rather than structural: the clustering is maximal in kind
but its total weight is `O(n^3)`, one logarithm below trivial. Had the trivial bound been the
truth, `d/(2J) = O(sigma sqrt(log n))` and the averaged programme would have died with the
pointwise one. It came down to one logarithm, supplied by the convergence of `sum_u 1/s^2`.

A second objection, caught in self-review: a fitting error of my own briefly made
`sd_y(A) = Theta(n^3)` rather than the true `Theta(n^2 log^2 n)` — the two differ by a factor
4 at `n <= 64` — which would have made the averaged programme look dead. Caught by computing
`sd/mean`, which is scale-free and came out flat at 0.22.

## Paper potential

**Not yet.** Theorem 2 is conditional on (H-surv) and its novelty is plausible but not
verified. Lemma D is elementary and no novelty is claimed for it. If (H-surv) is discharged,
Theorem 2 plus Lemmas D and C would be a short honest note — *"the random greedy independent
set process on the isosceles hypergraph cannot be analysed pointwise, but can be analysed on
average, and here is the exact logarithm that separates the two"* — of interest to people
working on the differential-equation method, not a result about `C(n)`. If (Q2) is also
settled, the picture changes and `C(n) = Omega(n)` becomes reachable.

## Files

`THEOREM_CONTRACT.md` · `THEOREM_AND_PROOF.md` (Parts I–V) · `ATTACK_LOG.md` (A1–A12) ·
`LITERATURE_NOTES.md` · `CLAIM_REGISTRY.md` · `CHECKPOINT.md` · `HANDOFF.md` · `experiments/`
(`s8_tail.c`, `s8_proc.c`, `s8_joint.c`)

---

## 中文说明（给工程背景的读者）

**问题。** `n×n` 格点里最多挑多少点不出等腰三角形，记 `C(n)`。已知至少 `n/√(log n)`，猜是
`n`——差一个 `√(log n)`。标准攻法是随机贪心。

**上一轮的结论。** 分析工具要求「**每一个**点的可用邻居数 `d_2(v)` 都紧贴理论曲线」，这一轮
之前已证明这个要求对格点问题**本身就是错的**（偶尔来一个"大单"占掉某人 `n` 小时，而均值只有
`log n`；`n²` 个人里总有人连吃几单）。所以只能改用「平均量」。

**这一轮回答了唯一剩下的问题：那些"接到大单的人"和"某人的同组同事"，是不是同一批？**

**答案：是，而且是最严重的那种。** 举个最小的例子：`v=(0,0)`、`y=(2,0)`，那么 `x` 轴上所有
`u=(2k,0)` 同时满足「`u` 和 `v` 关系密切」且「选中 `y` 会给 `u` 一个 `n` 量级的大单」。也就是
说，**选一个点，就同时给 `Θ(n)` 个人发大单，而这 `Θ(n)` 个人恰好都是 `v` 的核心同事。** 所以
任何假设"互相独立"或"负相关"的论证都是错的。

**但——这一轮也证明了这种聚集是有上限的，而且上限正好够用。** 关键量是
`A(v,y) = Σ_u codeg(v,u)·codeg(u,y)`。粗暴估计给 `n³·log n`，真值是 `54n³`——**正好小一个
对数**。证明只有三行：关键在于「距离尺度为 `s` 的点有多少个」这个计数**与 `s` 无关**，于是
`Σ 1/s²` 收敛（而 `Σ 1/s` 发散），Cauchy–Schwarz 把两个发散的和配成一个收敛的和。

**这一个对数，正好就是平均量比逐点量多出来的余量。** 逐点量差 `√(log n)/log log n`，平均量
反过来富余 `σ√(log n)`。差别整整一个 `log n`，来源就是上面那条引理。

**剩下的唯一一件事：** `l=2` 那一半。选中 `y` 时新加入 `v` 的 `Θ(n)` 个邻居，恰好是**一条直线
上的点**（`v` 和 `y` 的垂直平分线）。要证的是这条线上的点不会系统性地都是"接了大单的人"。
余量很宽（只要他们的偏差是典型大小，哪怕全部同号也够用），所以这是一道明确的题，不是死路。

**结论直说：`C(n)` 的下界这一轮仍然没有改进，还是 `n/√(log n)`；还不能发论文。** 得到的是一条
无条件的新引理（Lemma D）、一个条件性的障碍定理，以及一道被削到只剩一行几何的最后关卡。
