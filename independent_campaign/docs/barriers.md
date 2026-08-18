# Barrier Taxonomy — what a power-saving mechanism must avoid

Purpose: several natural mechanisms provably or demonstrably saturate above `n^{2-ε}`.
Diagnosing them precisely is a real deliverable: it tells later waves which arguments are
dead on arrival, and *why*. Two of the four barriers below are rigorous impossibility
theorems for a mechanism class; the other two are saturation diagnoses and are labelled as
such. Nothing here says the target is impossible — only that these particular inputs are
insufficient.

---

## B1 — Shell-counting barrier (Landau–Ramanujan). `VERIFIED_THEOREM` (for the class)

**Statement.** Let `D(X) = #{r ≤ X : r is a sum of two squares}`. By Landau–Ramanujan
`D(X) ~ K X / sqrt(log X)`. Any argument whose only input is the per-apex injectivity
`a ↦ |a-b|^2` — used through the colour-counting identity of RF3 — cannot prove better than

    m ≤ 1 + D(2n^2) = O(n^2 / sqrt(log n)).

*Why this is the exact ceiling.* By RF3, `Σ_r E_r = m(m-1)` with `E_r ≤ m` for each squared
distance `r`, giving `m - 1 ≤ #{realised squared distances} ≤ D(2n^2)`. And the relaxation
is genuinely achievable: choose one lattice point of `G_n` from each realised norm class
around a fixed corner apex `b_0`. The resulting set `T` has `|T| = D(2n^2) ≍ n^2/sqrt(log n)`
and satisfies "all distances from `b_0` are distinct". So per-apex distinctness at any
bounded number of apexes permits `n^2/sqrt(log n)`.

**Consequence.** `1/sqrt(log n)` is a hard cap for every purely distance-multiplicity
argument. Routes that reduce to "count available distances" are capped here. This includes:
the annulus/sub-box distance count, the local density bound `|S ∩ B(b,L)| ≤ 1 + D(L^2)`,
and the Cayley-graph/shell argument (whose gain is `ρ(r) ≤ n^{o(1)}`, since the maximal
number of representations as a sum of two squares is `exp(Θ(log n / log log n))`).

---

## B2 — Lattice-AP barrier (Behrend). `VERIFIED_THEOREM` (for the class)

**Statement.** No argument using only RF4 ("`S` contains no 3-term AP in `Z^2`", equivalently
"`S ∩ L` is 3-AP-free for every line `L`") can prove `C(n) = O(n^{2-ε})`.

*Proof.* Let `B ⊆ {0,...,n-1}` be 3-AP-free with `|B| = n·exp(-c·sqrt(log n))` (Behrend).
Then `B × B` is 3-AP-free in `Z^2`: a 3-AP `p, p+v, p+2v` with `v = (v_1,v_2)` yields a
3-AP in `B` in the first coordinate if `v_1 ≠ 0`, and in the second if `v_1 = 0, v_2 ≠ 0`.
So RF4 admits sets of size `n^2 exp(-2c sqrt(log n)) = n^{2-o(1)}`. ∎

Verified computationally for the base-3-digit-avoiding sets at `N = 9, 27, 81`
(`experiments/barrier_checks.py`).

---

## B3 — Axis line-kill barrier. `VERIFIED_THEOREM` (for the class)

This one matters most, because L2b (rows/columns killing transversal columns/rows) *is* a
genuine cross-line mechanism and passes the campaign's critical test — yet it is still not
enough on its own.

**Statement.** No argument using only the axis-direction line-kill constraints of L2b
— "two points of `S` in a common row with `x`-coordinates of equal parity force the column
at their midpoint to be **entirely** empty of `S`", plus the row/column transpose — can
prove `C(n) = O(n^{2-ε})`.

*Proof.* Take `B` 3-AP-free as in B2 and `S = B × B`. Occupied columns are exactly `B`.
For any row `y ∈ B`, `X_y = B`, so the killed columns are the same-parity midpoints `M(B)`,
and `M(B) ∩ B = ∅` precisely because `B` is 3-AP-free. Symmetrically for columns. Hence
`B × B` satisfies **every** axis line-kill constraint, while `|B × B| = n^{2-o(1)}`. ∎

**Computational confirmation** (`experiments/barrier_checks.py`): for `B` = base-3 digit-2-
avoiding sets in `[0,N)`,

| N  | \|B\| | \|B×B\| | isosceles-free | axis line-kill violations | diagonal line-kill violations |
|----|-------|---------|----------------|---------------------------|-------------------------------|
| 9  | 4     | 16      | no             | **0**                     | 10                            |
| 27 | 8     | 64      | no             | **0**                     | 76                            |
| 81 | 16    | 256     | no             | **0**                     | 520                           |

**The productive corollary.** `B × B` violates the *diagonal* line-kill constraint badly
(520 violations at N=81). So the diagonal / general-direction content of L2 is **strictly
stronger** than the rows-plus-columns content, and any successful mechanism built on L2 must
use non-axis directions essentially. This is the most useful positive signal at root level:
it identifies exactly where the unused information lives.

---

## B4 — Multi-direction line-kill saturation. `EMPIRICAL_PATTERN` / heuristic diagnosis

*Not* an impossibility theorem — a saturation estimate for the natural way of summing L2
over many directions.

For primitive `e` with both coordinates odd, let `s = |e_1| + |e_2|`. The `e`-lines number
`≍ ns` and carry `≍ n/s` grid points each; likewise the `e^⊥`-levels. If `|S| = δn^2`, some
`e`-line carries `≥ δn/s` points, whose midpoint set has size `≥ 2δn/s - 3`, and each killed
`e^⊥`-level removes `≍ n/s` grid points. So

    (points killed by direction e)  ≳  2 δ n^2 / s^2.

Summing over the `≍ s` primitive both-odd directions with `|e_1|+|e_2| = s`, and over
`s ≤ B`:

    Σ_e (killed)  ≍  Σ_{s ≤ B} s · (2 δ n^2 / s^2)  ≍  2 δ n^2 · log B.

Even assuming the killed sets were **perfectly disjoint** (they are not), `≤ n^2` forces only
`δ ≲ 1 / log n`. **The harmonic sum is the obstruction:** killing power per direction decays
like `s^{-2}` while directions accumulate only like `s`, so the total is logarithmic in the
number of directions used, no matter how many are used.

**What this tells wave 2.** A mechanism that adds up per-direction exclusions independently
cannot reach a fixed power. To beat `log`, one needs either (i) a superadditive interaction
between directions — a reason the exclusions must be near-disjoint *and* individually larger
than the trivial midpoint bound — or (ii) an argument that is not a sum over directions at
all.

---

## B5 — The iteration-arithmetic constraint. `VERIFIED_THEOREM` (elementary)

Any density-increment / self-improving scheme must produce a **constant multiplicative gain
per constant scale ratio**, not per polynomial scale ratio.

- Gain `(1+c)` per passage `n → n/K` for constant `K`: `log_K n` steps, so
  `δ ≤ (1+c)^{-log_K n} = n^{-log(1+c)/log K}` — **a fixed polynomial saving.** ✓
- Gain `(1+c)` per passage `n → n^{1/2}`: only `log log n` steps, so
  `δ ≤ (1+c)^{-log log n} = (log n)^{-c'}` — **polylog only.** ✗
- Gain `(1+c)` per passage `n → n^{1-γ}` for fixed `γ`: `≍ log log n` steps again. ✗

**Consequence.** The cross-scale route is essentially forced into the shape
`C(Kn) ≤ (K^2 - δ)C(n)` with `K = O(1)` and `δ > 0` fixed, equivalently: *an isosceles-free
set can never be within a `(1-c)` factor of extremal in all `K^2` sub-boxes simultaneously.*
Weaker scale-ratio versions are worth nothing asymptotically, so any recurrence result must
be checked against this arithmetic before it is called progress.

---

## Summary table

| Barrier | Mechanism class capped | Cap | Status |
|---|---|---|---|
| B1 | distance-multiplicity / shell counting | `n^2/sqrt(log n)` | rigorous for the class |
| B2 | lattice 3-AP-freeness (all lines) | `n^{2-o(1)}` | rigorous for the class |
| B3 | axis line-kill (rows+columns), full strength | `n^{2-o(1)}` | rigorous for the class |
| B4 | summed multi-direction line-kill | `n^2/log n` | heuristic saturation |
| B5 | scale iteration with sub-constant scale ratio | polylog only | rigorous arithmetic |

**Where the unused information demonstrably lives:** non-axis directions in L2 (by the B3
corollary), and any genuinely superadditive interaction between constraints (by B4).
