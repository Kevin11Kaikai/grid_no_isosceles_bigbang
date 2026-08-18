# Campaign split — `ε = 1/4` and the Extra budget

Lane: sidecar only. Do not copy into `iso6/` until a full `ε` is closed.

**Status.** Sidecar upper bound on Q4 is **closed as moot**. iso6 has
falsified Q4 (`n^{2-o(1)}` via four 3-AP-free projections). Lemmas below
remain correct and do not yield a power saving. Do not copy into `iso6/`.

Fix `ε = 1/4` throughout (any smaller positive `ε` has the same shape).
Write `r = r(a*)`, fold `S*` as in [`lemma3_caseA.md`](lemma3_caseA.md),
`μ = max_ant(S*)`, `ρ = max_row(S*)`, `t_max = max_d t_d`,
`Extra = Σ_d (t_d-1)`, `|S*| = 2r + 2·Extra`.

## Theorem B′ (small overlap → campaign bound)

The counting of [`lemma3_caseB.md`](lemma3_caseB.md) does not use `R ≤ √n`
until the last line. For every `ε ∈ (0,1]`,

```
|S|  ≤  (2n-1)(1 + R).
```

If `R ≤ n^{1-ε}` this is `|S| = O(n^{2-ε})`.

The single `r_3` diagonal (`R=1`) lives here. The `n=7` frame (`R=8>√7`)
does **not**; it is Case A′ (`R > n^{1-ε}`).

## Theorem (harmonic bound on `S*`)

Let `T = r + Extra = |S*|/2`. Constraint 4 on an anti-diagonal with `μ`
points of `S*` kills at least `μ-1` main diagonals (consecutive `d`-midpoints,
parity: same-parity subclasses lose at most `2` rather than `1`, which only
changes constants). Occupied diagonals include `D*` of size `r`, so

```
μ  ≤  2n - r + O(1).
```

Occupied anti-values of `S*` number `|U_ant(S*)| ≥ 2T/μ = 2(r+Extra)/μ`
(fold-symmetry: partners occupy mirrored anti-diagonals). `K` and `U_ant`
are disjoint and `a* ∈ K`, hence the extra-kill set satisfies

```
|K_extra|  ≤  2n-2 - |U_ant|  ≤  2n - 2(r+Extra)/μ.
```

Consecutive extra midpoints give `Σ |M_extra(d)| ≥ 2·Extra`. Each extra
midpoint `b` has `r*(b) ≤ r(b) ≤ r(a*) = r` because `a*` maximises `r` on
`K`. Therefore `2·Extra ≤ r |K_extra|`, so

```
Extra  ≤  r(((n-1)μ - r))/(μ + r)
```

(using `r ≤ nμ`, otherwise `|U_ant| > 2n`). Substitute `|S*| = 2r+2·Extra`:

```
|S*|  ≤  2n r μ / (r + μ)  ≤  2n min(r, μ).
```

This is a complete proof. It uses constraints 3 and 4 and the maximality of
`a*`.

## Three-way bound

Independently,

```
|S*|  ≤  n ρ,                  (at most ρ per row)
|S*|  ≤  2 t_max · r  ≤  4n t_max,
|S*|  ≤  2n μ.                 (harmonic, previous theorem)
```

Hence `|S*| ≤ n min(ρ, 4 t_max, 2μ)`.

**Corollary.** If `min(ρ, t_max, μ) ≤ n^{1-ε}`, then `|S*| = O(n^{2-ε})`.

Forced-pair Case A sets (`out/lemma3/extra_budget.json`) all have `μ ≤ 4`
and `t_max ≤ 2` up to `n=243`, with `r > n^{3/4}`, so they fall under the
corollary (`|S*| ≤ 2n μ = O(n)`).

## Packing when two maxima are large

Equal-parity consecutive midpoints on a row of `S*` kill at least `ρ-2`
columns (two parity classes). Occupied columns `C` of `S*` miss those kills,
and `|C| ≥ μ` (an anti-diagonal with `μ` points uses `μ` distinct columns),
so

```
ρ + μ  ≤  n + O(1).
```

A heavy diagonal uses `2 t_max` distinct columns, hence likewise

```
ρ + 2 t_max  ≤  n + O(1).
```

These do **not** forbid `ρ, t_max, μ` all `> n^{3/4}` for large `n`
(`3 n^{3/4} < n` once `n > 81`). They do forbid it at `n=81`.

## Remaining GAP on `S*` — closed except a core

The three-way corollary left the triple `ρ, t_max, μ` all `> n^{1-ε}`. That
triple is **not dangerous by itself**. Write `θ = n^{1-ε}` and

```
D_h  =  { d : t_d > θ },     Δ_h  =  { δ : k_δ > θ }.
```

[`lemma3_sstar.md`](lemma3_sstar.md): if `min(|D_h|, |Δ_h|) ≤ θ`, then
`|S*| ≤ 8 n^{2-ε}`. A single heavy diagonal or a single popular `δ` is
covered. The `n=7` frame (`t_d=1`) is covered. Search for the old triple
(`a1_triple.py`, min `=5` at `n=243`) is obsolete as a gap.

**Remaining GAP (not filled).** `|H| > n^{7/8}` and `|J| > n^{3/4}`.
Routes that do not close it are listed in [`lemma3_heavy.md`](lemma3_heavy.md)
§“Why the remaining GAP is not filled”. This is the hard kernel of lemma 3,
not a bookkeeping leftover. If the configuration exists, `|S| > n^{13/8}`
and Q4 dies. Search has not found it.

## Theorem B″ (small kill-set)

`|S| ≤ (2n-1)(1+|K|)`. If `|K| ≤ n^{1-ε}` then `|S| = O(n^{2-ε})`. Dual to
lemma 2 on `|U_ant|`.

## Global heavy lines (no fold)

[`lemma3_heavy.md`](lemma3_heavy.md). Write `H = {d : m_d > n^{1-ε}}` and
`J` dually on antis. If `min(|H|,|J|) ≤ n^{1-ε}`, then `|S| ≤ 3 n^{2-ε}`.
The core `S_core` (points on a heavy diagonal and a heavy anti) satisfies
`|S| ≤ |S_core| + 4 n^{2-ε}` and `|S_core| ≤ |H| |J|`, so both supports
`≤ n^{7/8}` also give `|S| = O(n^{2-ε})`.

This is the same split as the `S*` heavy-vertex theorem, applied to the
whole set. Search (`a1_heavy.py`, `a1_manyheavy.py`) has `|H|=|J|=0` through
`n=243` (max `m_d = 12` at `n=243`, threshold `61.5`). Not a proof the
remaining core is empty.

## `S'` peeling is absorbed

B′ after one fold is still **false** (`sprime_thin.py`). It is no longer the
gap. [`lemma3_heavy.md`](lemma3_heavy.md) bounds the whole set: if every
diagonal (or every anti) has `≤ n^{1-ε}` points, or if both heavy-support
sizes are `≤ n^{7/8}`, then `|S| = O(n^{2-ε})` with no fold. Two matching
layers have `m_d = 2` and fall under the first half.

## `(d,α)`-product falsification

Script `da_product.py`, output `out/da_product/`.

If `D` and `A = a* ± Δ` are 3-AP-free and `(D-D) ∩ (A-A) = {0}`, the
product is Q4-feasible: constraints 1–2 are vacuous (at most one point per
row/column), 3–4 follow because `U_ant ⊆ A` and `U_dia ⊆ D`. Size
`|D|·|A|`. Scaled families (`Δ ⊂ [m]`, `D ⊂ mℤ` 3-AP-free) are at most
`r_3(n/m) r_3(m) = n^{1-o(1)}` and in practice `≪ 2n`.

Best `|S|/n` on `n ≤ 243`:

| n | best `|S|/n` | family |
|---|---|---|
| 16 | 0.75 | disjoint geom2 `t=2` |
| 81 | 0.64 | FourDir biclique `t=2` |
| 128 | 0.75 | FourDir biclique `t=3` |
| 243 | 0.74 | FourDir biclique `t=3` |

Ratio is **not growing**. All families sit below `n`, far from the kill
line `|S| ≥ 2.5n`. This is ammunition-fails, not Q4-dies.

A complete `(d,δ)` biclique still has `k t ≈ n/3` (`a1_biclique.py`),
i.e. linear, consistent with the harmonic bound when `μ` or `t_max` is
small.

## Verdict

| Piece | Status |
|---|---|
| Theorem B′, `R ≤ n^{1-ε} ⇒ \|S\|=O(n^{2-ε})` | **proved** |
| Theorem B″, `\|K\| ≤ n^{1-ε} ⇒ \|S\|=O(n^{2-ε})` | **proved** |
| Harmonic bound on `S*` | **proved** |
| `min(ρ,t_max,μ) ≤ n^{1-ε} ⇒ \|S*\|=O(n^{2-ε})` | **proved** |
| `min(\|D_h\|, \|Δ_h\|) ≤ n^{1-ε} ⇒ \|S*\|=O(n^{2-ε})` | **proved** (closes old triple) |
| Global: `min(\|H\|,\|J\|) ≤ n^{1-ε} ⇒ \|S\|=O(n^{2-ε})` | **proved** |
| Global: `\|H\|,\|J\| ≤ n^{7/8} ⇒ \|S\|=O(n^{2-ε})` | **proved** |
| Remaining: `\|H\| > n^{7/8}` and `\|J\| > n^{3/4}` | **inhabited** (iso6 four-fold Behrend; Q4 dies) |
| `Q4(n)=O(n^{2-ε})` | **false** |

Do not merge into iso6.
