# Q_SQ overnight upper-bound attempt (sidecar only)

This file lives in `d:\others\iso6-sq\proofs\`. It is **not** an iso6 proof.
Do not copy into `iso6/docs/`, `iso6/proofs/`, or `iso6/routes/`.

**Status.** No power `Q_SQ=O(n^{2-ε})` was proved. Not PROMISING. The
`O(n^{3/2})` counting argument has an unfixable hole (recorded below).
True lemmas: Z[i] form, one row is free, two full rows are not.

**Honesty.** Four-fold remains Q4-feasible. A Q_SQ power would give
`C(n)=O(n^{2-ε})`. This night did not produce one. Failed counting is not
a safety proof for Q_SQ, and the peeling construction is not `n^{2-o(1)}`.

---

## Phase 0 — kill switch (Gaussian peeling)

Károlyi–Solymosi smallest example (`β=2+2i`, `P={0,1,i}`, peel `1,0,i`).
Implemented in `peel.py`. Theorem 2.6 gives

```
F(n) ≫ n^α / log n,    α = log 3 / log(2√2) ≈ 1.05664.
```

Machine check (`out/peel.json`): for `m=3…10`, `Φ` is injective and the
balanced composition class is **square-corner-free** (`sq.py`).

| m | \|S\| | bbox n | \|S\|/n | log\|S\|/log n | sq-free |
|---|---|---|---|---|---|
| 3 | 6 | 11 | 0.55 | 0.75 | yes |
| 6 | 90 | 348 | 0.26 | 0.77 | yes |
| 8 | 560 | 2796 | 0.20 | 0.80 | yes |
| 9 | 1680 | 6892 | 0.24 | 0.84 | yes |
| 10 | 4200 | 22366 | 0.19 | 0.83 | yes |

Finite-n `|S|/n` is still `<1` (same delay as Behrend). The exponent is
climbing toward 1.056. **Asymptotic superlinearity is the kill-switch:**
any claimed `Q_SQ=O(n)` is false. `O(n^{1.2})` is false against the paper’s
`Ω(n^{1.3})`. `O(n^{3/2})` is compatible with both.

This is the algebraic family the construction battery missed.

---

## Phase 1 — lemmas that hold

### Lemma (Z[i] form)

Clockwise square-corner at `b` iff `a + i c = (1+i)b` in `Z[i]`.
The other orientation is `c + i a = (1+i)b`. Degenerate iff `a=b=c`.
Equivalent to J1 (`w` and `R_±(w)`).

Checked: all ordered triples in `[8]^2`, 249984 comparisons, **0 mismatches**.

### Lemma (one row is free)

A single full row or full column of `[n]^2` is square-corner-free.
Hence `Q_SQ(n) ≥ n`. Compatible with Phase 0.

*Proof.* If `w` is horizontal, `R(w)` is vertical, so the third point leaves
the row. If `w` is not horizontal, `b` and `b+w` are not both on the row.
Same for a column. Checked at `n=8,16,32,48`.

### Lemma (two full rows are not free)

Any two distinct full rows `y` and `y+d` (`d≠0`) contain a square-corner.

*Proof.* Take `x=d` (assume `d>0`; otherwise swap). The three points
`(d,y)`, `(d,y+d)`, `(0,y)` lie on the two rows. Here `w=(0,d)` and
`R_+(w)=(-d,0)`. Checked: every pair of full rows at `n=4,8,16,24` is
dirty. Witness at `n=4`: `{(1,0),(1,1),(0,0)}`.

**Corollary.** Any three full rows are dirty (they contain two). Checked
directly at `n=12` (660 triples, 0 free) and `n=16` (1680 triples, 0 free).
This does **not** imply `Q_SQ=O(n)`: a sq-free set may occupy every row
partially (peeling does).

---

## Phase 2 — the `O(n^{3/2})` hole (unfixable in this counting)

Let `m=|S|`, `P=m(m-1)` ordered pairs `(b,a)` in `S`. Each pair has two
candidate thirds `b+R_±(a-b)`. Let `G` be the number of those that land
**in the grid**, `I` the number that land **in S**. Sq-free ⇒ `I=0`.

Always `G ≤ 2P`. Always `G ≤ 2 n^2 m` (choose the grid point first, then
apex in `S`).

**Attempted power.** Assume `G ≥ c P` with `c>0` and `G ≤ m n`. Then
`m=O(n)`, hence also `O(n^{3/2})`.

**Why this dies.**

1. `G ≤ m n` is **not** a grid identity. It fails on random dense sets
   (`out/power_counts.json`: n=16 m=40, `G ≤ mn` is false).
2. On small peeling samples `G ≤ mn` still holds, but it **cannot persist**:
   peeling has `m ≍ n^{1.056}/polylog`, `P ≍ m^2`, and `G/P` stays order-1
   (measured 0.82–1.05). Then `G/mn ≍ m/n → ∞`, so `G ≤ mn` fails for the
   same family at large `m`. Using it would prove `O(n)`, contradicting
   Phase 0.
3. Replacing `mn` by `m n^{1/2}` or `m^{3/2}` still loses: the only
   **valid** upper bounds are `G=O(m^2)` and `G=O(n^2 m)`, which with
   `G ≥ c m^2` yield only `m=O(n^2)`.

Same hole blocks the weaker Hölder interpolations from this pair of
quantities. Stop. Do not relabel as `o(n^2)`.

A power would need a **different** upper bound on an IRT-count that uses
`I=0` more than “the third point is missing” — e.g. incidence geometry
stronger than this double count, or Fourier (Pilatte). That is not this
counting argument, and it was not proved tonight.

---

## Rejected false bounds

| Claim | Status |
|---|---|
| `Q_SQ=O(n)` | False (peeling theorem + verified sq-free samples) |
| `Q_SQ=O(n)` via two-full-rows | False implication: two *full* rows are dirty, but partial rows are allowed |
| `Q_SQ=O(n^{3/2})` via `G≤mn` | Hole above |
| `Q_SQ=o(n^2)` via Szemerédi/Ajtai–Szemerédi | Not attempted (not a power; B-type) |

---

## What would still be a win later

An elementary (or any) complete proof of `Q_SQ=O(n^{2-ε})` for a fixed
`ε>0`. Compatible targets start at `O(n^{3/2})` or even `O(n^{1.4})`.
Pilatte’s `n^2/log^{1+c}n` is not the prize. This file does not contain
that proof.
