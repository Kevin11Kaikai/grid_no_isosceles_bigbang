# Q_SQ power attempt 2 (not G≤mn)

This file lives in `d:\others\iso6-sq\proofs\`. It is **not** an iso6 proof.
Do not copy into `iso6/docs/`, `iso6/proofs/`, or `iso6/routes/`.

**Status.** No power `Q_SQ=O(n^{2-ε})` was proved. Not PROMISING. Night 1’s
`G≤mn` count is not reused. Methods A and B each have a named hole.
Method C was skipped: no honest point-line system.

**Honesty.** Four-fold remains Q4-feasible. A Q_SQ power would give
`C(n)=O(n^{2-ε})`. This attempt did not produce one. Kill-switch: nothing
implying `Q_SQ=O(n)` or `O(n^{1.2})` (peeling / Károlyi–Solymosi).

Code: `attempt2.py`, `run_attempt2.py`. Output: `out/attempt2_{A,B,C}.json`.

---

## Kill-switch (unchanged)

Gaussian peeling (`peel.py`, `β=2+2i`, `P={0,1,i}`) is sq-free for
`m=3…10`. Theorem: `F(n) ≫ n^{1.056}/log n`, and the paper has
`Ω(n^{1.3})`. Any lemma implying `O(n)` or `O(n^{1.2})` is false.
`O(n^{3/2})` is compatible.

---

## Method A — heavy vs light rows

Let `r_y = |S ∩ row y|`, `m = Σ r_y`. Threshold: a row is **heavy** if
`r_y > n^{1/2}`, else **light**.

### Light case (true, tautological)

If every `r_y ≤ n^{1/2}`, then `m ≤ n · n^{1/2} = n^{3/2}`. This case
needs no geometry. It is compatible with peeling: at `m=6,8,9` one has
`max_r = 5,10,16` against `√n ≈ 18.7, 52.9, 83.0`, so peeling sits
entirely in the light case at these sizes (`out/attempt2_A.json`). A
power `O(n^{3/2})` would still require the **heavy** case to cap `m`.

### Heavy case: forbidden cells of a horizontal pair

Take a heavy row `y_*` with x-set `X`, `|X|=r > n^{1/2}`. Each ordered
pair of distinct points on the row is a difference `w=(d,0)`. Then
`R_±(w)=(0,±d)`, so the third vertex of the square-corner is in the
**same column as the apex**:

```
apex (x, y_*), partner (x+d, y_*)  ⇒  forbidden cells (x, y_* ± d).
```

Write `F` for the set of such cells that land in `[n]^2`. Sq-freeness
forces `S ∩ F = ∅` (except the heavy row itself is not in `F`).

**True lemma (forbidden-set support).** `F` lives in the `r` columns
indexed by `X`. Hence `|F| ≤ r n`. Also `|F| ≤ 2 r (r-1)` before
grid clipping. Both `|F|≤r n` checks passed on every heavy example.

### Machine check

| family | n | m | max_r | heavy | \|F\| | n²−\|F\| | r n |
|---|---|---|---|---|---|---|---|
| peel_m6 | 348 | 90 | 5 | 0 | 0 | 121104 | — |
| peel_m8 | 2796 | 560 | 10 | 0 | 0 | 7817616 | — |
| peel_m9 | 6892 | 1680 | 16 | 0 | 0 | 47499664 | — |
| greedy_32 | 32 | 64 | 7 | 1 | 50 | 974 | 224 |
| fullrow_16 | 16 | 16 | 16 | 1 | 184 | 72 | 256 |
| fullrow_36 | 36 | 36 | 36 | 1 | 954 | 342 | 1296 |
| fullrow_64 | 64 | 64 | 64 | 1 | 3040 | 1056 | 4096 |
| synth_r12_n36 | 36 | 12 | 12 | 1 | 204 | 1092 | 432 |
| synth_r20_n36 | 36 | 20 | 20 | 1 | 572 | 724 | 720 |
| synth_r16_n64 | 64 | 16 | 16 | 1 | 368 | 3728 | 1024 |
| synth_r32_n64 | 64 | 32 | 32 | 1 | 1504 | 2592 | 2048 |

Peeling and small greedy are all-light. The heavy examples are the test
of the case that would have to finish an `O(n^{3/2})` proof.

### Hole (stop Method A)

`|F|` is too small to cap the rest of `S`. Even a **full row** (`r=n`)
leaves a positive-density complement: at `n=64`, `|F|=3040` and
`n²−|F|=1056` cells remain legal for this one-row obstruction (edge
columns lack a partner `x+d` in range, so `F` is a triangle, not the
whole grid). A synthetic heavy row of length `n/2` leaves `2592/4096`
of the grid. Greedy `n=32` has one heavy row of size 7 and `|F|=50`
against `n²=1024`.

The typical hole named in the plan is exactly this: `|F|=O(r²)` (or
the tighter `|F|≤r n`) lives in `r` columns and does not empty
`[n]^2`. Pretending `F` is the whole grid would be a fake repair.
**Method A stops here.** Light case `m≤n^{3/2}` is true but incomplete.

This does **not** claim `Q_SQ=O(n)`: one full row is sq-free (night 1),
and peeling occupies every row only thinly.

---

## Method B — energy of difference apexes

Let `A_w = S ∩ (S−w)` (apexes realizing difference `w≠0`).

### True lemmas

1. **Counting identity.** `Σ_w |A_w| = m(m−1)`. Checked on peeling
   `m=6,8,9`, greedy `n=16,24,32`, and full rows `n=16,36,64`
   (`identity=true` throughout `out/attempt2_B.json`).

2. **Pairing.** Sq-free ⇒ `(A_w + R(w)) ∩ S = ∅` for both
   `R_±`. Equivalently `A_w ∩ A_{R(w)} = ∅`, so
   `|A_w| + |A_{R(w)}| ≤ m`. Checked: `max_|Aw|+|A_Rw|` is `24,150,420`
   on peel `m=6,8,9` (against `m=90,560,1680`) and `15,35,63` on full
   rows (against `m=n`). `pairing_Aw_disjoint_from_S_minus_Rw=true`,
   `max_pair_le_m=true`. No failures.

3. **Cauchy–Schwarz.** `(Σ |A_w|)^2 ≤ n_w · Σ |A_w|^2`. Holds on every
   sample (`cs_ok=true`).

### What CS / pairing actually give

Pairing plus `n_w ≤ O(n²)` (at most `O(n²)` nonzero differences in
`[n]^2`) yields

```
m(m−1) = Σ |A_w| ≤ 2 m n_w = O(m n²)  ⇒  m = O(n²).
```

That is the trivial bound. Hölder on energy does not improve it without
an extra alignment: one would need some `w` with both `A_w` and
`A_{R(w)}` large **and** geometrically aligned so that the forbidden
translate eats a positive fraction of `S`. Pairing only says the two
apex sets are disjoint subsets of `S`. On peeling the mass is spread:
`n_w = 4498, 126284, 900906` at `m=6,8,9` (order `m²`, not `O(n)`).

### Kill-switch against `O(n)`

If one assumed `n_w = O(n)` then `m=O(n)`, which is **false**
(peeling). A full row does have `n_w = 2n−2 = O(n)`, but that is a
special geometry, not a grid identity. The code therefore records
`implies_O(n)=false` and refuses that bound.

**Hole.** The only uniform bound from this energy is `m=O(n²)`. No
`ε>0`. Alignment was not obtained. **Method B stops here.**

---

## Method C — Szemerédi–Trotter skipped

An IRT / square-corner is the Gaussian relation `a + i c = (1+i)b`
(equivalently `w` and `R(w)`), a **rotation**, not a linear incidence.

Candidate systems that were considered and rejected as dishonest:

- **Axis-parallel lines.** `k=2n` lines, `I=m` incidences. ST says
  `I ≪ m^{2/3} k^{2/3} + m + k`, which for `m ≤ n²` is tautological and
  does not see square-corners.
- **Circles centred at points of `S`.** The number of distinct radii /
  circles is not `O(m)` in a way that makes `I ≪ m^{2/3}k^{2/3}+m+k`
  cap `m` below `n²`; the IRT count is not equal to those incidences.
- **No explicit line set** was written whose incidences equal or
  dominate IRT completions.

Plan rule: do not invoke ST on an unspecified system. **Skip.**
`out/attempt2_C.json`: `st_applied=false`.

---

## What holds vs what does not

| Claim | Status |
|---|---|
| all-light ⇒ `m ≤ n^{3/2}` | true, tautological |
| heavy-row `F` lives in `r` columns, `|F|≤r n` | true |
| `|F|` caps `|S|` in the complement | **false** (hole A) |
| `Σ |A_w| = m(m−1)` | true |
| `(A_w+R(w)) ∩ S = ∅` ⇒ `|A_w|+|A_{R(w)}|≤m` | true |
| CS/Hölder ⇒ `m=O(n^{2-ε})` | **false** (hole B; only `O(n²)`) |
| `n_w=O(n)` ⇒ `Q_SQ=O(n)` | **false**; kill-switch |
| ST on an unnamed system | **not applied** |
| `G≤mn` (night 1) | **not reused** |
| `Q_SQ=O(n^{2-ε})` | **not proved** |

---

## Isolation

Only `d:\others\iso6-sq\`. Reused `sq.py`, `peel.py`. No iso6 / Q import.
No Pilatte / Gowers. No merge. Not PROMISING.
