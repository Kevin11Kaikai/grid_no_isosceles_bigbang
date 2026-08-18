# Root Reformulations and the Multi-Direction Line-Kill Lemma

All statements proved from the definition. Evidence level indicated per item.
Novelty: NOVELTY_UNASSESSED (isolation phase).

Throughout: `S ⊆ G_n := {0,...,n-1}^2`, and *isosceles-free* means there are no three
distinct `a,b,c ∈ S` with `|a-b| = |b-c|` (degenerate collinear triples included).
Write `m = |S|`.

---

## RF1 — Bisector form  `VERIFIED_LEMMA`

**Lemma.** `S` is isosceles-free ⟺ for every pair of distinct `a,c ∈ S`, the perpendicular
bisector of `a` and `c` contains no point of `S`.

*Proof.* A point `b` satisfies `|a-b| = |c-b|` exactly when `b` lies on the perpendicular
bisector of `a,c`. Note `a,c` themselves are never on their own bisector, so the triple
`a,b,c` is automatically distinct. ∎

This is the form used everywhere below. Its content: **an excluded configuration is not a
point but an entire line.** That is the source of every cross-line statement in this file.

---

## RF2 — Reflection form  `VERIFIED_LEMMA`

**Lemma.** `S` is isosceles-free ⟺ for every line `L ⊆ R^2`,
`S ∩ σ_L(S) ⊆ L`, where `σ_L` is reflection in `L`.

*Proof.* `{a,c}` has perpendicular bisector `L` exactly when `c = σ_L(a)` and `a ∉ L`.
By RF1 this pair is allowed only if `S ∩ L = ∅`. Contrapositive gives the statement. ∎

Reading: **if `S` meets a line `L`, then `S` has no mirror-symmetric pair across `L`.**

---

## RF3 — Proper-edge-colouring form  `VERIFIED_LEMMA`

**Lemma.** Colour each edge of the complete graph on `S` by the squared distance of its
endpoints. `S` is isosceles-free ⟺ this is a *proper edge colouring* (no two edges of the
same colour share a vertex) ⟺ for every `r`, the distance-`r` graph induced on `S` has
maximum degree ≤ 1.

*Proof.* Two edges `ba`, `bc` share vertex `b` and have the same colour iff
`|a-b|^2 = |c-b|^2`. ∎

**Corollary (translation form).** For every `r ≥ 1`,
`Σ_{v : |v|^2 = r} |S ∩ (S - v)| ≤ m`,
the sum being over all lattice vectors `v` of squared norm `r`.

*Proof.* The left side counts ordered pairs `(b, b+v)` with both in `S` and `|v|^2 = r`,
i.e. `Σ_{b∈S} deg_r(b) ≤ m·1`. ∎

---

## RF4 — Lattice-AP form  `VERIFIED_LEMMA`

**Lemma.** `S` contains no 3-term arithmetic progression in `Z^2`: there are no
`p ∈ S`, `v ∈ Z^2 \ {0}` with `p, p+v, p+2v ∈ S`.

*Proof.* `p+v` is equidistant from `p` and `p+2v`. ∎

**Corollary.** For *every* line `L` in the plane (not only axis-parallel), `S ∩ L` is a
3-AP-free subset of the lattice points of `L`.

This is strictly stronger than the baseline hypothesis "every axis-parallel line is
3-AP-free", but on its own it still only yields `n^{2-o(1)}` (see `docs/barriers.md`, B2).

---

## RF5 — Paraboloid-lifting form  `VERIFIED_LEMMA`

Lift `p ↦ p̂ = (p_1, p_2, p_1^2 + p_2^2) ∈ Z^3`, and set `Ŝ = {p̂ : p ∈ S}`.
For `b ∈ R^2` let `ξ_b(x,y,z) = z - 2b_1 x - 2b_2 y` (the linear functional whose kernel
direction is the normal of the paraboloid's tangent plane at `b̂`).

**Lemma.** For `a, b ∈ R^2`, `ξ_b(â) = |a-b|^2 - |b|^2`. Consequently `S` is isosceles-free
⟺ for every `b ∈ S`, the functional `ξ_b` is injective on `Ŝ`.

*Proof.* `ξ_b(â) = |a|^2 - 2⟨a,b⟩ = |a-b|^2 - |b|^2`. Injectivity of `ξ_b` on `Ŝ` is
exactly distinctness of `|a-b|` over `a ∈ S`. ∎

Reading: `m` points on a paraboloid such that each of the `m` tangent-plane normal
directions *induced by the points themselves* separates all of them into distinct levels.
Recorded as a representation; no bound extracted from it yet (see registry route R0-rep).

---

## L1 — Lattice points on a perpendicular bisector  `VERIFIED_LEMMA`

**Lemma.** Let `a ≠ c ∈ Z^2`, `d = c - a`, `g = gcd(d_1,d_2)`, `e = d/g` (primitive).
The perpendicular bisector of `a,c` contains a lattice point **iff `g` is even, or both
coordinates of `e` are odd.** When it does, its lattice points form the coset
`{x_0 + t·e^⊥ : t ∈ Z}` with `e^⊥ = (-e_2, e_1)`; consecutive lattice points are at
distance `|e|`.

*Proof.* The bisector is `{x : 2⟨x,d⟩ = |c|^2 - |a|^2}`. Since
`|c|^2 - |a|^2 = ⟨c-a, c+a⟩ = g⟨e, a+c⟩`, this is `2⟨x,e⟩ = ⟨e, a+c⟩ =: T`.
As `e` is primitive, `x ↦ ⟨x,e⟩` is onto `Z`, so lattice solutions exist iff `T` is even.
Now `T = ⟨e, 2a + d⟩ = 2⟨e,a⟩ + g|e|^2`, so `T` is even iff `g|e|^2` is even, i.e. iff `g`
is even or `|e|^2 = e_1^2 + e_2^2` is even. For primitive `e`, `|e|^2` is even iff both
coordinates are odd. The solution set of `⟨x,e⟩ = T/2` is a coset of `ker = Z·e^⊥`. ∎

*Verification.* `experiments/root_checks.py` compares the criterion against brute-force
search for an equidistant lattice point in `[-40,40]^2`, over all ordered pairs
`a,c ∈ [-6,6]^2` (28 560 pairs): **0 discrepancies**. `VERIFIED_COMPUTATIONAL_RESULT`.

*Hand sanity checks (all consistent):* `a=(0,0), c=(1,0)`: `g=1` odd, `e=(1,0)` not both odd →
bisector `x=1/2`, no lattice points. `c=(2,0)`: `g=2` even → `x=1`, lattice points.
`c=(1,1)`: `e=(1,1)` both odd → `x+y=1`, lattice points. `c=(1,2)`: `g=1`, `e=(1,2)` →
`2x+4y=5`, no lattice points. `c=(2,4)`: `g=2` even → `x+2y=5`, lattice points.

---

## L2 — Multi-direction line-kill lemma  `VERIFIED_LEMMA`

For a primitive `e ∈ Z^2` put `φ_e(x) = ⟨x, e⟩` and `ψ_e(x) = ⟨x, e^⊥⟩`.
The level sets of `ψ_e` are the lines of direction `e` ("`e`-lines"); the level sets of
`φ_e` are the lines of direction `e^⊥`.

**Lemma.** Let `a ≠ c ∈ S` lie on a common `e`-line, and write `c - a = g·e`.
If `g|e|^2` is even then

    φ_e(S) omits (φ_e(a) + φ_e(c)) / 2.

That is: **the entire `e^⊥`-line at the midpoint `φ`-level contains no point of `S`,
anywhere in the grid.**

*Proof.* `φ_e(c) = φ_e(a) + g|e|^2`, so the stated level is `φ_e(a) + g|e|^2/2`, an integer
under the parity hypothesis. By L1 the bisector of `a,c` is exactly the line
`⟨x,e⟩ = T/2 = φ_e(a) + g|e|^2/2`, and by RF1 it misses `S`. ∎

**Corollary L2a (both-odd directions).** If `e` is primitive with both coordinates odd then
`|e|^2` is even, the parity hypothesis is automatic, and *every* pair of `S` on a common
`e`-line kills an `e^⊥`-level. Writing `Φ_e = φ_e(S)` and `Q_L = φ_e(S ∩ L)` for each
`e`-line `L`:

    M(Q_L) ∩ Φ_e = ∅,    where M(Q) = { (q+q')/2 : q ≠ q' ∈ Q }.

Since `Q_L ⊆ Φ_e`, in particular each `Q_L` is 3-AP-free — but the statement is strictly
stronger: the midpoints must avoid the `φ_e`-image of **all** of `S`, not just of `S ∩ L`.

**Corollary L2b (axis and diagonal instances).**
- `e = (1,0)`: two points of `S` in a common **row** with `x`-coordinates of equal parity
  force the **column** at their midpoint to be entirely empty of `S`.
- `e = (0,1)`: same with rows/columns exchanged.
- `e = (1,1)`: two points of `S` on a common **diagonal** force the **anti-diagonal**
  `x+y = (A(a)+A(c))/2` to be entirely empty of `S` — with *no parity condition*.
- `e = (1,-1)`: two points on a common anti-diagonal kill a diagonal.

**Critical-test answer.** L2 uses information strictly beyond "each axis-parallel line is
3-AP-free": the excluded object is a *transversal* line, so a configuration inside one row
constrains every other row. This is genuine cross-line information. Whether it is enough is
a separate question — see `docs/barriers.md`, barrier B3, where the mechanism is shown to
saturate at a `1/log n` factor.

---

## L3 — What L2 actually yields, quantitatively  `VERIFIED_LEMMA` (bound), see B3 for the cap

**Proposition (row/column form).** Let `U ⊆ {0,...,n-1}` be the set of occupied columns and
`K = ∪_y M(X_y)` the set of killed columns, where `X_y` is the set of `x`-coordinates in
row `y`. Then `K ∩ U = ∅`, hence `|U| + |K| ≤ n`. Moreover `|M(X_y)| ≥ |X_y| - 3` for every
`y`, so `|X_y| ≤ |K| + 3`, and therefore

    m ≤ n · min(|U|, |K| + 3) ≤ n(n+3)/2.

*Proof.* Disjointness is L2b. For the midpoint bound, split `X_y` by parity into `X_y^0`,
`X_y^1`; midpoints of same-parity pairs are integers, and for a set `A` of integers
`|{a+a' : a ≠ a' ∈ A}| ≥ 2|A| - 3`, so `|M(X_y)| ≥ 2·max(|X_y^0|,|X_y^1|) - 3 ≥ |X_y| - 3`.
Finally `m ≤ n|U|` (each occupied column holds ≤ n points) and `m ≤ n·max_y |X_y|`. ∎

**Proposition (diagonal form, no parity loss).** With `w` = number of occupied
anti-diagonals, every diagonal `d` satisfies `|S ∩ d| ≤ n + 1 - w/2`, and `m` is at most the
total size of the `w` fattest anti-diagonals. Optimising the two constraints numerically
(`experiments/root_checks.py`) gives `m ≤ (3/4 + o(1)) n^2`: the bound is
`0.7598 n^2` at `n=50`, `0.7550` at `n=100`, `0.7525` at `n=200`, `0.7512` at `n=400`,
`0.7506` at `n=800` — clearly converging to `3/4`.
`VERIFIED_COMPUTATIONAL_RESULT` for the optimisation; the two input inequalities are
`VERIFIED_LEMMA`.

**Status.** These are honest constant-factor improvements on `n^2`, obtained from a genuinely
cross-line mechanism, but they are **far weaker than the sealed baseline**
`n^2 exp(-c(log n)^{1/9})` and are recorded only because L2 is the mechanism, not the bound.
The mechanism's asymptotic ceiling is analysed in `docs/barriers.md`.
