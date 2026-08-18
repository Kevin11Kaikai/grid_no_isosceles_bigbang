# Ideal uniformity for the square-corner problem, and the two-way box/torus equivalence

Session 6, root, post-closeout continuation. Every claim below is either proved here or
labelled with its evidence level. Nothing here is progress toward `C(n) = O(n^{2-ε})`.

Notation. `Z[i]` the Gaussian integers. For an ideal `I ⊆ Z[i]`, `N(I) = |Z[i]/I|`. A
**square corner** in a `Z[i]`-module `M` is a triple `(b, u, v)` with `u ≠ b` and

```
    v = i·u + (1-i)·b            coefficients (1-i) + i - 1 = 0
```

`G(I)` = the largest square-corner-free subset of `Z[i]/I`. `Q_SQ(n)` = the largest
square-corner-free subset of the box `[0,n)² ⊆ Z²`.

Prior campaign notation, now seen to be special cases:
`g(q) = G((q))` (the torus `(Z_q)²`), and `m(p) = G((π))` where `p = π·π̄`, `p ≡ 1 mod 4`.

---

## 1. Theorem A (box ≤ torus). For every `q ≥ 2n`, `Q_SQ(n) ≤ g(q)`.

*Proof.* Let `S ⊆ [0,n)²` be square-corner-free in `Z²`. Suppose it has a square corner
on the torus `(Z_q)²`: `b, u ∈ S` with `u ≠ b`, and `v ∈ S` with `v ≡ b + i·w (mod q)`
where `w ≡ u - b`.

Work with honest integers. `w = u - b` has both coordinates in `(-n, n)`, so its
reduction mod `q` is the honest difference (as `q ≥ 2n > n`). Then `i·w = (-w₂, w₁)` also
has both coordinates in `(-n, n)`, so the honest point `P = b + i·w` has both coordinates
in `(-n, 2n)`. Since `v ∈ [0,n)²`, each coordinate of `P - v` lies in the **open** interval
`(-2n, 2n)`, and is `≡ 0 (mod q)`. As `q ≥ 2n`, the only multiple of `q` in `(-2n, 2n)` is
`0`. Hence `P = v` exactly, so `(b, u, v)` is a genuine square corner of `S` inside the
box — contradiction.

So `S` is square-corner-free on the torus, giving `|S| ≤ g(q)`. ∎

**Why this matters.** Before Theorem A the campaign had only the tensor lemma, which runs
the other way (`Q_SQ(n) = Ω(n^{log g(q)/log q})`, lower bounds). Theorem A closes the loop:
**upper bounds on the torus transfer back to the box.** Combining, with
`λ = limsup_I log G(I)/log N(I)`:

```
    Q_SQ(n) = n^{2λ + o(1)}
```

so the target `Q_SQ(n) = O(n^{2-ε})` is *equivalent* to `λ < 1`. The geometry is now
entirely gone: one number decides the route.

**Verification.** `experiments/ideal_tower.py`, block A1: for `n = 3..8` and
`q ∈ {2n, 2n+1, 3n, 4n+1}`, 4000 random subsets each, box-freeness compared with
torus-freeness by two separately written definition-only checkers. **0 disagreements in
96 000 tests**, including at the sharp threshold `q = 2n`.

---

## 2. Theorem B (ideal uniformity). `m(p)` and `g(q)` are the same function.

Define `ψ : Z² → F_p` by `ψ(a,b) = a + k·b (mod p)`, where `k² ≡ -1 (mod p)`.

*Proof.* `ψ(i·(a,b)) = ψ(-b, a) = -b + k·a = k·(a + k·b) = k·ψ(a,b)`, using `k² = -1`.
So `ψ` is a surjective `Z[i]`-module map, `i` acting as multiplication by `k`, with kernel
`Λ_p = {(a,b) : a + k b ≡ 0}`, a lattice of determinant `p`. Therefore
`F_p ≅ Z²/Λ_p ≅ Z[i]/(π)` as `Z[i]`-modules, and under this identification the twisted
3-AP `y, y+d, y+kd` **is** the square corner `b, b+w, b+i·w`. ∎

**Corollary B1.** `Λ_p` is an ideal of `Z[i]`, hence closed under multiplication by `i`,
hence a *square* lattice: its reduced basis satisfies `|u| = |v| = √p` exactly. Measured
for `p = 101, 401, 1601, 6421, 25601, 102401`: `|u| = |v| = √p` to 2 decimals in every
case. So `Z[i]/(π)` is a `√p × √p` square torus, and `m(p)` is the square-corner problem
at "side `√p`", matching `g(q)` at `q = √p`.

**Corollary B2 (evidence downgrade — the important consequence).** The closeout records
four independent falsification instruments for route SQ and treats the agreement of the
`m(p)` ladder (exponent `0.547`) with the `g(q)` ladder (exponent `0.545`) as
corroboration from two directions. **By Theorem B it is not.** They are one problem in two
parameterisations, and the agreement is a consistency check on the code, not evidence
about the mathematics. Measured against group size:

```
    m(p):  p =  101  401 1601 6421      values 13  26  56 120   exponents .5558 .5436 .5456 .5461
    g(q):  q =   10   20   40   80      values 12  26  56 117   exponents .5396 .5438 .5456 .5434
```

Identical values (26 vs 26, 56 vs 56) at matched group size; mean exponent gap `0.0046`.

**The route's surviving independent instruments are therefore two, not four:**
Theorem 4 (a proof), and the structured-construction hunt of §4 below.

**Verification.** `experiments/same_problem.py`: T1 checks the intertwining over all `p²`
residue pairs for 8 primes (0 mismatches); T2 compares the two complete definitions on
2100 random sets across 7 primes with no shared code (0 disagreements).

---

## 3. Lemma C (half-orbit form) and the bound `m(p) ≤ (p+1)/2`

Let `H = ⟨k⟩ = {1, k, -1, -k}`, a subgroup of order 4 of `F_p*` (`4 | p-1`).

`A` is twisted-AP-free iff for every `x ∈ A`, the difference set `D_x = (A - x)\{0}`
satisfies `k·D_x ∩ D_x = ∅`.

*Proof.* `y, y+d, y+kd ∈ A` with `d ≠ 0` says exactly: for `x = y`, both `d` and `kd` lie
in `D_x`. ∎

`H` acts freely on `F_p*`, so `F_p*` splits into `(p-1)/4` orbits `uH = {u, ku, -u, -ku}`.
Inside one orbit the forbidden pairs `{v, kv}` form the 4-cycle
`u — ku — (-u) — (-ku) — u`, whose maximum independent sets have size 2 and are exactly
`{u,-u}` and `{ku,-ku}`. Hence `|D_x| ≤ 2·(p-1)/4` and

```
    m(p) ≤ (p+1)/2.
```

Rigorous, and very weak (`m(p)` is observed near `√p`). Its value is not the bound but the
**mechanism it names**: for every `x ∈ A`, the additively defined set `A - x` must lie in a
*multiplicatively* defined half-orbit selector of density `1/2`. That is an
additive/multiplicative incompatibility — a sum-product mechanism, not a
density-increment mechanism, and therefore not automatically subject to the "no power
savings for Roth-type problems" wall. Supporting computation: if `A = G` is a
multiplicative subgroup then freeness requires `g₁ - 1 = k(g₂ - 1)` to be unsolvable in
`G`, which is `|G|²` pairs against one equation, forcing `|G| ≲ √p`. So `√p` emerges from
an algebraic count independently of the Minkowski/lattice picture.

**Verification.** `experiments/twisted_ap_structured.py` block V0: free action, `(p-1)/4`
orbits, 4-cycle structure and `α = 2` confirmed orbit-by-orbit for `p = 101, 401, 1601, 6421`.

---

## 4. The structured-construction hunt (evidence, not proof)

Failure ledger F1 records that greedy search on Q4 read `~1.8n` with slope `1.0` while
the truth was `n^{2-o(1)}`, because **greedy cannot find an algebraically structured set**.
Every SQ survival instrument except Theorem 4 was a search. So the honest attack is to go
looking for algebraic constructions directly.

Seven families were tested; every candidate was re-checked by the complete definition.
The condition is invariant under `x ↦ ax + b` (`a ∈ F_p*`), so dilates and multiplicative
cosets are not separate families — this was verified rather than assumed.

| family | best exponent (p ≤ 1601) | behaviour |
|---|---|---|
| interval / AP | 0.5000 | `Θ(√p)`, Minkowski-sharp |
| 2-dimensional Bohr set | 0.4965 | worse than an interval |
| multiplicative subgroup / coset | 0.4363 | `|G| ≲ √p` as predicted by §3 |
| geometric progression | 0.5381 | best found; still `≈ √p` |
| quadratic / quartic residues | 0.4146 | worse |
| **Behrend digit sphere** | 0.3121 | **fails, as Theorem 4 requires** |
| half-orbit selector clique | 0.5000 | `Θ(√p)` |

Best structured exponent found: **0.5381**, below the greedy baseline `0.547`. `1.000`
would kill the route. **No algebraic family beats `√p`.**

Evidence level: `SUPPORTED_BY_SEARCH_OVER_A_CHOSEN_FAMILY_LIST`. It is not exhaustive over
constructions and must never be upgraded. Its force is that it is the *right* kind of
search — the kind F1 says was missing.

---

## 5. The `(1+i)`-adic tower, and why the finite-margin recurrence is dead

`(1+i)` is prime in `Z[i]` with `N((1+i)) = 2` and `(1+i)^{2m} = (2^m)` up to a unit. So
`Z[i]/(1+i)^j` is a tower of `Z[i]`-modules of size `2^j` with **index 2 at every step** —
precisely the "constant gain per constant scale ratio" that barrier B5 says a power saving
requires, and precisely what `Z_p` does not have (which is why Roth over `Z_p` must use
Bohr sets and loses a logarithm).

**Reduction (proved).** If `G(I·(1+i)) ≤ c·G(I)` with `c < 2` for all `I` in the tower
beyond some point, then `G((1+i)^j) = O(c^j) = O(N^{log₂ c})`, and by Theorem A
`Q_SQ(n) = O(n^{2 log₂ c})` with `2 log₂ c < 2`, hence `C(n) = O(n^{2-ε})`.

**New exact values** (`experiments/ideal_tower.py` A3; solver revalidated against all
known `g(q)`, `q ≤ 8`, in A2; witnesses re-verified by a definition-only checker):

```
    j       1    2    3    4    5    6
    N       2    4    8   16   32   64
    G(I)    1    2    2    4    6    9
    ratio        2.00 1.00 2.00 1.50 1.50
```

`j = 3` and `j = 5` (`N = 8, 32`) are ideals not of the form `(q)`; these values are new.

**FALSIFIED, by exact exhaustive computation: the finite-margin form of the recurrence.**
The exact ratio **equals 2** at `j = 1→2` and at `j = 3→4`. So "`c < 2` at every step" is
false, and the exponent implied by the exact data is exactly `2 log₂ 2 = 2.0000` — no
saving at all. Retreating to the asymptotic form `limsup_j ratio < 2` makes the statement
equivalent to `λ < 1`, which by Theorem A is the target itself.

**§8 audit verdict: the tower is a restatement of the target, not a reduction of it.**
A NEW FORMULA IS NOT A NEW MECHANISM. Recorded as such; no difficulty reduction claimed.

**Self-refutation check that saved this from being reported as progress.** The greedy
ladder beyond `j = 6` reads ratios `1.31–1.78` hovering near `1.45`, which looks like
comfortable margin. `experiments/tower_control.py` runs the *same solver* on a relation
whose fate is known — 3-term APs, which Behrend forces to `N^{1-o(1)}`, so its local
exponent must tend to `1`:

```
    control  Z/2^m, 3-APs:  ratios 1.5000, 1.3333, 2.0000   λ_local 0.585, 0.415, 1.000
    control  Z/3^m, 3-APs:  λ_local pinned at 0.6309 = log2/log3   (true limit: 1)
```

A relation that **must die** reads `1.5` at the first index-2 step and `0.63` throughout
the index-3 tower. Therefore small-scale tower ratios cannot distinguish a surviving
relation from a dying one, and the `(1+i)` ratio data is **UNINFORMATIVE**, not support.
Logged as failure-ledger F4.

---

## 6. Status after this section

- Theorem A, Theorem B, Corollaries B1/B2, Lemma C: `PROVED`, machine-verified.
- `Q_SQ(n) = n^{2λ+o(1)}` with `λ = limsup log G(I)/log N(I)`: `PROVED`. Target ⇔ `λ < 1`.
- `λ ≥ 0.5781` rigorous (from `g(11) = 16`). No upper bound on `λ` below `1` is known.
- Route SQ's independent survival evidence: **two instruments, not four** (Theorem 4 and
  the structured hunt). The `m(p)` ladder is struck.
- The `(1+i)` tower: reduction proved, finite-margin recurrence **falsified**, asymptotic
  form is the target restated. Contributes clarity, not progress.
- Everything remains `NOVELTY_UNASSESSED`; the prior-art audit is still sealed.

**No part of this document may be reported as progress toward the upper bound.**
