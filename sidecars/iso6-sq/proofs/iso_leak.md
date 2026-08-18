# Q_SQ vs isosceles: peeling leak

This file lives in `d:\others\iso6-sq\proofs\`. It is **not** an iso6 proof.
Do not copy into `iso6/docs/`, `iso6/proofs/`, or `iso6/routes/`.

**Status.** Gaussian peeling is square-corner-free and **not** isosceles-free.
`Q_SQ` is a strictly leaky relaxation of `C`. Not PROMISING. No iso6 merge.

Code: `iso_census.py`, `run_iso_census.py`. Output: `out/iso_census.json`.

---

## Why this measurement

`C(n) ≤ Q_SQ(n)`. A power on `Q_SQ` would still win the campaign. But if
peeling (the known `Q_SQ` lower bound) is full of non-right isosceles, then
`C` is much smaller than `Q_SQ` on the same family, and elementary nights
spent only on square-corners are bounding the **wrong** (larger) function.

RF1 apex `b`: two distinct points at equal squared distance. Split:

- **J1 / rot90:** legs `u, R_±(u)` (right angle at `b`).
- **collinear 3-AP:** legs `u, −u` (midpoint `b`).
- **other:** equal length, not perpendicular, not collinear.

Sq-free ⇒ no J1. Iso-free ⇒ none of the three.

---

## Machine check

| family | n | m | triples | J1 | 3-AP | other | iso-free |
|---|---|---|---|---|---|---|---|
| peel_m6 | 348 | 90 | 217 | **0** | 24 | 193 | no |
| peel_m8 | 2796 | 560 | 3317 | **0** | 180 | 3137 | no |
| peel_m9 | 6892 | 1680 | 21595 | **0** | 1440 | 20155 | no |
| peel_m10 | 22366 | 4200 | 74489 | **0** | 3900 | 70589 | no |
| greedy_16 | 16 | 26 | 69 | 0 | 3 | 66 | no |
| greedy_24 | 24 | 44 | 175 | 0 | 19 | 156 | no |
| greedy_32 | 32 | 66 | 406 | 0 | 36 | 370 | no |
| fullrow_64 | 64 | 64 | 992 | 0 | 992 | 0 | no |

Peeling `m=3…10` was already checked sq-free. The J1 column is 0, as required.
The other two columns are large. At `m=9`, non-right non-collinear triples are
`20155/21595 ≈ 93%` of all isosceles; collinear 3-APs are the rest.

Greedy sq-free sets are the same shape: J1-free, isosceles-rich. A full row
is the collinear special case (every 3-AP on the row is an isosceles with
midpoint apex). That matches night 1: one row is sq-free, not iso-free.

---

## What the leftover looks like

No single `(u,v)` or cosine dominates. At `m=9` the most common other pairs
each appear 90 times (composition-class multiplicity), with many distinct
`r²` (`2097160`, `262145`, `16777280`, …) and many dots. One small pair that
does show up is `r²=65` with `{(-8,-1),(-4,7)}` (two representations
`1²+8²=4²+7²`). That same `65` appears as a Q4-surviving non-J1 on a dense
four-fold at `n=16` (`iso6-joint/out/j2_fourfold.json`). It is **one**
equal-length pair among many, not a one-parameter stencil on all of `Z²`.

There is no honest Szemerédi–Trotter system here: the slopes are not a small
named line set.

---

## Implication

Károlyi–Solymosi construct **IRT-free** sets of size `Ω(n^{1.3})`. They are
not a lower bound for `C(n)`. On this family `C` sees tens of thousands of
forbidden triples that `Q_SQ` ignores.

A later `Q_SQ=O(n^{2-ε})` proof would still imply the same bound for `C`,
but it is a harder target than `C` itself, and nights 1–3 did not produce
it. Further elementary counting that only uses `R_±` is bounding a function
that peeling already shows is superlinear for a reason `C` does not share.

**Not a safety proof for `C`.** Not PROMISING.
