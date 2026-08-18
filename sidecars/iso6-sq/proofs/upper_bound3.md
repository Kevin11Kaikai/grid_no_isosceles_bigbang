# Q_SQ power attempt 3 (multi-row union; not G≤mn)

This file lives in `d:\others\iso6-sq\proofs\`. It is **not** an iso6 proof.
Do not copy into `iso6/docs/`, `iso6/proofs/`, or `iso6/routes/`.

**Status.** No power `Q_SQ=O(n^{2-ε})`. Not PROMISING. Did not retry
`G≤mn`, Method A’s one-row `F`, Method B’s `n_w=O(n)`, or unnamed ST.

Code: `attempt3.py`, `run_attempt3.py`. Output: `out/attempt3_D.json`.

---

## Method D — union over all rows and columns

Night 2 Method A used **one** heavy row. Here: every occupied row’s
horizontal pairs, every occupied column’s vertical pairs, union.

Horizontal pair on row `y`: apex `(x,y)`, partner `(x+d,y)` forbids
`(x, y±d)`. Vertical pair on column `x` forbids `(x±d, y)`.

Two-row shared columns at distance `d` produce the **same** cells as the
vertical pairs in those columns (`|F_tworow|=|F_cols|` on every peeling
sample). They are not a third geometric source.

Sq-free ⇒ `S ∩ F = ∅`. Checked: `S_hits_F_*=0` on peeling, greedy, full
row, and two-row synthetics.

### Machine check

| family | n | m | \|F_union\| | n²−\|F\| | leftover/n² |
|---|---|---|---|---|---|
| peel_m6 | 348 | 90 | 214 | 120890 | 0.998 |
| peel_m8 | 2796 | 560 | 2914 | 7814702 | 1.000 |
| peel_m9 | 6892 | 1680 | 13410 | 47486254 | 1.000 |
| greedy_16 | 16 | 28 | 83 | 173 | 0.676 |
| greedy_32 | 32 | 71 | 303 | 721 | 0.704 |
| fullrow_64 | 64 | 64 | 3040 | 1056 | 0.258 |
| tworow r=20 share=0 | 64 | 40 | 1160 | 2936 | 0.717 |
| tworow r=20 share=10 | 64 | 40 | 860 | 3236 | 0.790 |

Peeling occupies 389 rows at `m=9` and still leaves `>99.97%` of the bbox
legal for this obstruction. Two medium rows, even with 10 shared columns,
leave most of the grid. `implies_O(n)=false`; `leftover_le_n^{3/2}=false`.

### Hole

`F` is supported on the occupied rows’ columns (and symmetrically). Union
over many light rows does not make `F` a positive-density subset of
`[n]^2` on the only superlinear sq-free family we have. Stop. Do not
pretend the leftover is `O(n^{2-ε})`.

Compatible with night 1: one full row is sq-free, leftover a triangle of
size `Θ(n²)`.

---

## Method C′ — ST still skipped

Peeling’s non-right isosceles (see `iso_leak.md`) use many slopes, not a
named point-line system whose incidences dominate IRTs. No ST.

---

## Isolation

Only `d:\others\iso6-sq\` for this attempt. Reused `sq.py`, `peel.py`,
`attempt2.heavy_row_forbidden`. No iso6 / Q import. Kill-switch held.
