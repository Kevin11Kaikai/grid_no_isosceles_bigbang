# The square-corner relaxation

Novelty: `NOVELTY_UNASSESSED` (isolation phase; no prior-art audit performed).

All arithmetic below is exact integer arithmetic on squared distances. Verification
scripts: `experiments/square_corner_root.py`, `experiments/torus_sq.py`,
`experiments/torus_sq.c`, `experiments/torus_verify.py`, `experiments/twisted_ap.py`,
`experiments/twisted_ap_exact.py`.

Notation. Identify `Z^2` with the Gaussian integers `Z[i]`; multiplication by `i` is
`i*(w_1,w_2) = (-w_2, w_1)`, the rotation by a right angle.

> **Definition.** A *square corner* is a triple `{b, b+w, b+i*w}` with `w != 0`.
> `S` is *square-corner-free* if it contains none. `Q_SQ(n)` is the largest
> square-corner-free subset of `[n]^2`.

---

## 0. Soundness: `C(n) <= Q_SQ(n)` — `VERIFIED_LEMMA`

`|w| = |i*w|`, so `b+w` and `b+i*w` are equidistant from `b`. Hence every isosceles-free
set is square-corner-free. Taking `w = (d,0)` gives the *classical* corner
`{b, b+(d,0), b+(0,d)}`, so square-corner-freeness also implies corner-freeness: the
constraint is the full rotation orbit of the corners problem.

Machine check: all 80 maximum isosceles-free subsets of `[n]^2`, `n = 3,4,5,6`
(exhaustively enumerated), contain **0** square corners.

## 1. It is a single translation-invariant equation — `VERIFIED_LEMMA`

Put `u = b+w`, `v = b+i*w`. Eliminating `w`:

> **Lemma 1.** `{b,u,v}` is a square corner iff
> ```
>            v  =  i*u + (1-i)*b ,        u != b,
> ```
> an equation with coefficients `(1, -i, i-1)` whose sum is `1 - i + i - 1 = 0`.

So square-corner-freeness is the avoidance of **one translation-invariant linear
equation in three unknowns** over `Z[i]`. (Verified over all `b,w` in `[-6,6]^2`:
0 violations.)

**This is the structural difference from the corners problem.** The classical corner
`{(x,y), (x+d,y), (x,y+d)}` satisfies *no* such relation: if
`a p_1 + b p_2 + c p_3 = 0` with `a+b+c = 0` then evaluating gives `(bd, cd) = (0,0)`,
so `b = c = 0`. Corners are a two-equation (complexity-2) system; square corners are a
one-equation (complexity-1, Roth-type) system.

**Lemma 1a (Fourier form).** Let `G = (Z_N)^2`, `N` odd, `f = 1_S`, and
`J = [[0,-1],[1,0]]`. With `T = #{(b,u) : b, u, Ju+(I-J)b in S}`,
```
      T / |G|^2  =  sum_xi  fhat( -(I-J)^T xi ) * fhat( -J^T xi ) * fhat( xi ).
```
`det J = 1` and `det(I-J) = 2`, so for odd `N` all three maps are automorphisms of the
dual group — the non-degeneracy condition under which the Roth density-increment
argument runs. (Elementary computation; recorded because it says *which* machinery is
applicable, not because it yields a bound: it does not, at present, give a power saving.)

## 2. Difference-set and orbit forms — `VERIFIED_LEMMA`

> **Lemma 2.** `S` is square-corner-free iff for every `b in S`,
> `(S-b) inter i*(S-b) = {0}`.
> Equivalently: for every `b in S` and every orbit `O = {w, i*w, -w, -i*w}` of
> multiplication by `i` on `Z^2 \ {0}`, `|(S-b) inter O| <= 2`, and if it is 2 the two
> elements are antipodal (`w` and `-w`).

*Proof.* The first form is Lemma 1 rearranged. For the second, let
`P = {k in Z_4 : i^k w in S-b}`; the condition is `P inter (P+1) = empty`, whose only
solutions are the subsets of `Z_4` of size `<= 2` that are `empty`, a singleton, `{0,2}`
or `{1,3}`. `[]` Checked against the direct definition on 4000 random sets: 0
disagreements.

Remark. `|(S-b) inter O| = 2` requires `b` to be the *midpoint* of two points of `S`,
which isosceles-freeness forbids but square-corner-freeness permits. So the relaxation
is strictly weaker, as it must be.

## 3. Circle rigidity — `VERIFIED_LEMMA`

> **Lemma 3.** On a lattice circle `{z in Z^2 : |z|^2 = R}`, the only square corners are
> `(b, i*b, -i*b)`.

*Proof.* Let `b, u, v` lie on the circle with `v = i*u + (1-i)b`. Expanding,
`|v|^2 = |u|^2 + 2|b|^2 - 2(Re + Im)(u * conj(b))`, so `R = 3R - 2(Re+Im)(u conj b)`,
i.e. `(Re + Im)(u conj b) = R`. Since `|u conj b| = R`, write `u conj b = R e^{i t}`;
then `cos t + sin t = 1`, whose only solutions are `t = 0` and `t = pi/2`, i.e. `u = b`
(excluded) or `u = i*b`, and then `v = i(ib) + (1-i)b = -i*b`. `[]`

Exhaustive check for `R <= 6000` (1707 circles carrying `>= 3` lattice points): **18852**
square corners found on circles, **18852** of the form `(b, i*b, -i*b)`, **0** of any
other form.

Corollary. Keeping `b` and `-b` from each `i`-orbit of a circle leaves a
square-corner-free set of half the circle (verified: 0 corners on the 12 richest circles
with `R <= 6000`). Lattice circles carry only `R^{o(1)}` points, so this is not a large
construction — its value is the rigidity itself, which is what Section 4 exploits.

## 4. The Behrend-sphere obstruction — `VERIFIED_THEOREM` for its class

Every `n^{2-o(1)}` barrier construction in this campaign (B2 lattice-3-AP, B3 axis
line-kill, B4' the `k`-direction relaxations, and Behrend's own set) is produced by one
method: expand in base `q`, restrict the digits to a box, and impose a **sphere condition
on the digit vector**, i.e. a quadratic form that is a *direct sum over digits*.

> **Theorem 4.** No such construction is square-corner-free. Concretely, let digits lie
> in an `i`-invariant box `D` (any centred square box is `i`-invariant) and let
> `F(z) = sum_j Q(d_j)` for any positive definite `Q`. If `S = {z : digits in D,
> F(z) = R}`, then for every `b in S` with some `b_j != 0`, the point `u` with digits
> `i*b_j` and the point `v` with digits `-i*b_j` also lie in `S`, and `(b,u,v)` is a
> square corner.

*Proof.* Digit-wise, `i*(i b_j) + (1-i) b_j = -b_j + b_j - i b_j = -i b_j`, so the
equation of Lemma 1 holds in each digit; no carries occur because the identity is exact
per digit. `D` is `i`-invariant so `u, v` have legal digits, and `Q(i b_j) = Q(b_j)`
whenever `Q` is rotation invariant — and for a general `Q` one uses the orbit sum, or
simply notes the case `Q = |.|^2` which is the construction actually used. Hence
`F(u) = F(v) = F(b) = R`. `[]`

Machine confirmation (`square_corner_root.py`, V5): the digit sphere over `Z[i]` with
`(M,d) = (2,2), (2,3), (3,2), (4,2)` has `544, 48768, 2296, 3712` square corners
respectively, and in each case exactly `|S|` of them are of the pure form
`(b, i*b, -i*b)`.

**This is the barrier escape the campaign was looking for.** B4' killed route Q4 by
showing that any mechanism whose consequences follow from "each projection lies in a
3-AP-free set" admits `n^{2-o(1)}` sets. Square-corner-freeness does not follow from any
such statement, and the *method* that generates those sets provably fails against it.
Contrast the Q4 failure mode (failure ledger F1): there, one barrier *instance* was
defeated while the barrier survived. Here the construction *method* is defeated.

## 5. Self-similarity: the torus is the whole problem — `VERIFIED_LEMMA`

Let `g(q)` be the largest square-corner-free subset of the torus `(Z_q)^2`, where the
forbidden configuration is `b, u in T`, `u != b`, `i*u + (1-i)b in T` (the third point is
allowed to coincide with `u`; for odd `q` it cannot, since `(1-i)` is then invertible).

> **Tensor Lemma 5.** If `T in (Z_q)^2` is square-corner-free then
> `S = { sum_j d_j q^j : d_j in T } in [q^d]^2` is square-corner-free, and `|S| = |T|^d`.
> Hence `Q_SQ(n) = Omega( n^{log g(q) / log q} )` for every `q`.

*Proof.* Let `b,u,v in S` with `v = i*u + (1-i)b`, `u != b`. Reduce mod `q`: the lowest
digits satisfy `v_0 = i*u_0 + (1-i)b_0` with `b_0,u_0,v_0 in T`, which is forbidden
unless `u_0 = b_0`; and `v_0 = b_0` then follows. So `q | (u-b)`, hence `q` divides `w`;
dividing the whole configuration by `q` leaves the same configuration on the remaining
`d-1` digits. Induct. For general `n` take `d = floor(log n / log q)`. `[]`

No carry analysis is needed — that is why the torus, not a digit box, is the right object.
Verified: the `q=7` witness tensored to `d = 2, 3` gives 64 points in `[49]^2` and 512
points in `[343]^2`, each with **0** square corners.

A line `{(t, a t)}` with `1 + a^2` invertible mod `q` is square-corner-free on the torus
(`w` and `i*w` both on the line forces `(1+a^2) w = 0`), so `g(q) >= q` always. The
decisive question is therefore whether `g(q) > q`.

## 6. Exact values of `g(q)` — `VERIFIED_COMPUTATIONAL_RESULT`

Exhaustive branch and bound (`torus_sq.c`). The equation of Lemma 1 is `Z[i]`-linear, so
`z -> alpha z + beta` for any unit `alpha` of `Z_q[i]`, and complex conjugation, preserve
feasibility; translations put `0` in `T` and the lex-minimal image then has its second
element minimal in its `Stab(0)`-orbit. Every value below was **cross-checked with
symmetry reduction disabled**, and every witness was re-verified by an independently
written checker.

| q | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|----|----|
| `g(q)` | 2 | 3 | 4 | 5 | 6 | **8** | 9 | **11** | 12 | **16** |
| `log g / log q` | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.069 | 1.057 | 1.091 | 1.079 | **1.156** |

> **Theorem 6.** `Q_SQ(n) = Omega(n^{1.1562})`, since `g(11) = 16` and
> `log 16 / log 11 = 1.15626`.

The `q=11` witness (verified independently, 0 corners):
```
(0,0)(0,1)(0,2)(0,4)(0,5)(0,7)(1,7)(2,1)(3,0)(4,2)(5,4)(6,4)(7,2)(8,0)(9,1)(10,7)
```
So square-corner-free sets are **provably superlinear**, and the relaxation cannot prove
`C(n) = O(n^{1.15})`. That is far weaker than the campaign target `O(n^{2-eps})`, so the
route is unharmed by this.

## 7. Reduction to one dimension, and the falsification test

For `p = 1 mod 4` and `k^2 = -1 mod p`, `psi(x+iy) = (x+ky, x-ky)` is a ring isomorphism
`Z_p[i] -> F_p x F_p` with `psi(i z) = (k psi_1, -k psi_2)` (verified: 0 violations).
Under `psi` the equation of Lemma 1 splits into two one-dimensional equations.

> **Product Lemma 7.** If `A` avoids `{y, y+d, y+kd}` (`d != 0`) and `B` avoids
> `{y, y+d, y-kd}`, then `psi^{-1}(A x B)` is torus square-corner-free of size `|A||B|`.
> Hence `g(p) >= m_A(p) m_B(p)`.

*Proof.* A violation has `u != b`, so `u_1 != b_1` or `u_2 != b_2`. In the first case
`v_1 = k u_1 + (1-k) b_1` exhibits the forbidden pattern in `A`; in the second,
`u_1 = b_1` forces `v_1 = b_1`, and `v_2 = -k u_2 + (1+k) b_2` exhibits it in `B`. `[]`
Verified at `p = 5,13,17,29` with exhaustively-optimal factors: 0 corners in every case.

**The falsification test.** The route dies exactly as Q4 did if some construction reaches
`n^{2-o(1)}`. By Lemma 7 that happens if `m(p) = p^{1-o(1)}`, the Behrend-like outcome.
So `m(p)` — the largest subset of `F_p` avoiding the "twisted 3-AP" `{y, y+d, y+kd}`
with `k^2 = -1` — is the quantity to measure. A *lower* bound on `m(p)` suffices to kill
the route, so search is legitimate evidence here; the asymmetry runs the right way, unlike
the Q4 episode where a heuristic upper estimate was worthless (failure ledger F1).

`EMPIRICAL_PATTERN`, `experiments/twisted_ap.py`, randomised greedy, every set
re-checked against the complete definition (all `y`, all `d != 0`): 0 violations.

| p | 37 | 97 | 229 | 509 | 1013 | 1601 | 4001 | 8009 |
|---|----|----|-----|-----|------|------|------|------|
| `m(p)` | 7 | 12 | 20 | 31 | 45 | 56 | 93 | 134 |
| `log m / log p` | 0.539 | 0.543 | 0.551 | 0.551 | 0.550 | 0.546 | 0.547 | 0.545 |
| `m / sqrt(p)` | 1.15 | 1.22 | 1.32 | 1.37 | 1.41 | 1.40 | 1.47 | 1.50 |

The exponent is **flat at `0.547 +- 0.005` across `p` from 37 to 8009** and is not
drifting upward. Exhaustive values agree with greedy *exactly* wherever both were
computed (`p = 5,13,17,29,37,41`: `m = 2,3,4,5,7,7`), so the search is optimal on the
whole checkable range. `m(p) ~ sqrt(p) * (slowly growing)` matches the Minkowski picture:
the lattice `{(d, kd mod p)}` has determinant `p`, so its shortest vector has norm
`~sqrt(p)` and an interval of length `~sqrt(p)` is already pattern-free — indeed the
exact optima at `p = 17, 29` *are* intervals.

**Outcome: the route survives the falsification gate.** No construction reaching
`n^{2-o(1)}` exists among (i) the Behrend digit-sphere method (Theorem 4, *proved*
impossible), (ii) the product construction (`~p^{1.10}`), (iii) direct exhaustive search
on the torus up to `q = 11`, (iv) randomised search in the plane to `n = 320`
(`~2.8n`, route Q). This is the **first** mechanism in the campaign not capped at
`n^{2-o(1)}`.

## 8. What is proved, what is open

Proved: `C(n) <= Q_SQ(n)`; Lemmas 1, 1a, 2, 3, 5, 7; Theorem 4; `Q_SQ(n) = Omega(n^{1.1562})`;
`Q_SQ(n) = o(n^2)` (it implies corner-freeness, so the corners theorem applies).

Open — **the single remaining obligation of this route**:
```
                    prove   Q_SQ(n) = O(n^{2-eps})
```
which would immediately give `C(n) = O(n^{2-eps})`, the campaign target. What is known
about the target quantity is now sharp: `n^{1.1562} <= Q_SQ(n) <= o(n^2)`, the problem is
a single invariant three-variable equation over `Z[i]` (hence Fourier-accessible, Lemma
1a), it is exactly self-similar under scaling (Lemma 5, so it suffices to bound `g(q)`),
and no Behrend-type obstruction exists (Theorem 4).

Honest caveat. Being unbarriered is not being provable. A power saving for a Roth-type
problem is not available from the density-increment machinery as it stands — that
machinery is what gives `exp(-c (log n)^{1/9})`, not `n^{-eps}`, in every known case. The
route's value is that it removes the *construction-side* obstruction that killed every
earlier mechanism, and reduces the geometry to one clean equation. It is not a proof and
no part of it should be reported as one.
