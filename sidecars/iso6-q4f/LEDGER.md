# Q4 falsification ledger (sidecar only)

This file lives in `d:\others\iso6-q4f\`. It is **not** an iso6 ledger.
Do not copy into `iso6/docs/`, `iso6/ledgers/`, or `iso6/routes/`.

**判定（给人工看）**

- **Q4 作为战役路线已死。** iso6 `docs/Q4_route.md` 现为 `FALSIFIED`：四重平移 Behrend 交
  `{(x,y): x∈A, y∈B, x+y∈W, x-y∈Z}`（四个集合都 3-AP-free）给出
  `Q4(n) ≥ r_3(n)^4/(64 n^2) = n^{2-o(1)}`。证明在 iso6 `proofs/q4_falsified.md`。
  本 sidecar 的构造电池**没有**找到这个族（只试了 `B×B` 稀疏化、两因子乘积、曲线、
  差集不交的 `(d,α)`）。弹药失效 ≠ Q4 安全。
- 本车道的上界尝试因此**失去目标**：任何只从四方向封杀推出的 `O(n^{2-ε})` 都假。
  已证的引理 1–2、B′、重线切分仍然对，但盖不住上述四重交，而那正是未填的
  `|H|>n^{7/8}` 核心。
- 小 n 精确值贴着 `~2n` 不与 `n^{2-o(1)}` 矛盾（Behrend 密度在小 n 看不见）。
- **不要把 sidecar 上界并进 iso6。** iso6 已经用伪造结了 Q4；这里没有可合并的幂次上界。

---

## Kill / fail lines used here

Plan line `|S| >= n^{1.1}` is **not informative** for `n < 1024`, because `n^{1.1} < 2n` on that range (a linear `2n` set would already “beat” it). Practical lines at the sizes we can run:

| Line | Meaning |
|---|---|
| **Q4 dies** | a family, on a stretch of `n`, has `|S|/n` clearly growing, or `|S| >= 2.5 n` with `verify = True` |
| **Ammunition fails** | that family repairs to `O(n)` / ratio not growing |
| **Gap** | exact `Q4(n)` sits clearly above greedy `~1.8n` |

All `verify()` checks used the frozen checker in `q4.py`.

---

## A. Small-n exact `Q4(n)`

Source: `exact.py` → `out/exact_table.json` and `out/exact_n{n}.json` (witnesses).

| n | size | size/n | status | seconds |
|---|------|--------|--------|---------|
| 1 | 1 | 1.000 | EXACT | 0.00 |
| 2 | 2 | 1.000 | EXACT | 0.00 |
| 3 | 4 | 1.333 | EXACT | 0.00 |
| 4 | 8 | 2.000 | EXACT | 0.00 |
| 5 | 8 | 1.600 | EXACT | 0.02 |
| 6 | 12 | 2.000 | EXACT | 0.14 |
| 7 | 16 | 2.286 | EXACT | 1.38 |
| 8 | 16 | 2.000 | EXACT | 50.05 |
| 9 | 18 | 2.000 | lower bound (180s timeout) | 180 |
| 10 | 21 | 2.100 | lower bound (180s timeout) | 180 |

Notes:

- iso6 greedy table had `n=8 → 16`. **Exact: `Q4(8)=16`.** No gap at n=8.
- `Q4(7)=16 > 2·7`. The `2n` cap in Q4_route is only for **full column support**, not a global cap. Ratio 2.286 is still constant-scale, not `n^{1+c}`.
- n=9,10 unfinished. Lower bounds stay near `2n`.
- **Gap line: not fired.** Exact values track `~2n`, not a jump above greedy.

---

## B. Construction battery

Source: `construct.py` → `out/construct_table.json` (includes point sets) and `out/construct_bxb_extra.json`.
Every row below has `verify=True`.

Sizes `|S|` (ratio `|S|/n` in parentheses):

| family | n=9 | 16 | 27 | 32 | 48 | 64 | 81 |
|---|---|---|---|---|---|---|---|
| Bxb_thin_base3 | 8 (0.89) | 22 (1.38) | 22 (0.82) | 48 (1.50) | 69 (1.44) | 70 (1.09) | 65 (0.80) |
| AxB_base3_x_sidon | 6 (0.67) | 16 (1.00) | 28 (1.04) | 38 (1.19) | 61 (1.27) | 68 (1.06) | 70 (0.86) |
| AxB_greedy3AP | 8 (0.89) | 23 (1.44) | 38 (1.41) | 49 (1.53) | 71 (1.48) | 99 (1.55) | 114 (1.41) |
| thick_fn_2_per_row | 7 (0.78) | 13 (0.81) | 17 (0.63) | 17 (0.53) | 22 (0.46) | 26 (0.41) | 35 (0.43) |
| curve_union | 14 (1.56) | 23 (1.44) | 43 (1.59) | 49 (1.53) | 72 (1.50) | 97 (1.52) | 132 (1.63) |
| sample_Bxb_n^1.2 | 7 (0.78) | 16 (1.00) | 22 (0.82) | 35 (1.09) | 54 (1.13) | 55 (0.86) | 56 (0.69) |
| sample_grid_n^1.2 | 9 (1.00) | 17 (1.06) | 27 (1.00) | 31 (0.97) | 48 (1.00) | 66 (1.03) | 86 (1.06) |
| single_row_3AP_free | 5 (0.56) | 7 (0.44) | 10 (0.37) | 10 (0.31) | 14 (0.29) | 16 (0.25) | 20 (0.25) |

Extra `B×B` thinning (base-3 digit-2-avoiding product, then Q4 repair):

| n | raw `\|B×B\|` | kept | kept/n | raw/n |
|---|---|---|---|---|
| 81 | 256 | 65 | 0.80 | 3.16 |
| 243 | 1024 | 189 | 0.78 | 4.21 |

### Family verdicts

1. **Sparse `B×B` (the B3 construction, repaired).** Raw size is `n^{2-o(1)}`. After forcing Q4 feasibility, residue is `< n` at the Behrend scales n=81 and n=243. **Ammunition fails.** Diagonal violations are not a few bad points; thinning destroys the quadratic mass. This is the most important negative of the battery.

2. **Non-product `A×B` (base3 × Sidon, greedy-3AP × greedy-3AP).** Ratios stay in `~1.0–1.55`, no growth in n. **Ammunition fails.**

3. **Thickened function graphs (2 per 3-AP-free row).** Ratios *fall* with n (`0.78 → 0.43`). **Ammunition fails.**

4. **Curve unions** (lines, parabolas, hyperbolas, exponential, up to 11 slopes). Strongest algebraic family here: ratios `~1.45–1.63`, flat in n, still below iso6 greedy `~1.8n` and below `2n`. **Ammunition fails** (no `n^{1+c}`).

5. **Random sample + repair** from `B×B` or from the full grid, target `n^{1.2}` points. After repair, `~n` or less. **Ammunition fails.**

6. **Single-row 3-AP-free.** Recovers the known lemma `Q4(n) ≥ r_3(n)`; ratio → 0 relative to n. Sanity check only.

**Q4-dies line: not fired.** No family produced `|S| >= 2.5 n`. No family’s `|S|/n` grows with n on `9…81`.

---

## What this does *not* say

- It does not prove `Q4(n) = O(n)` or `O(n^{2-ε})`.
- It does not prove there is no algebraic barrier. It proves that **these** barrier-shaped families (especially `B×B`) do not survive the two diagonal constraints as large sets.
- Greedy / exact `~2n` is still a weak-method picture at large n. A new construction not in this list could still kill Q4.

## Next (still sidecar, still not iso6)

Falsification battery is recorded above. An upper-bound attempt was run anyway
(human request, 12h sidecar slot). Outcome is the next section. Do not touch iso6 files.

---

## Upper bound attempt

**Verdict: partial success. `Q4(n)=O(n^{2-ε})` is not proved.**
Nothing here is copied into iso6.

### Proved (checkable)

- **Lemma 1.** A Q4-feasible full product `A×B` has at most one point per main
  diagonal, hence `|S|≤2n-1`. Proof: `proofs/lemma_product.md`.
  Computation: `out/upperbound/product_sanity.json` — full products fail Q4;
  repaired size `≤2n-1` at `n=9,16,27,32,81`.
- **Lemma 2.** If any of `|U_col|,|U_row|,|U_dia|,|U_ant| ≤ n^{1-ε}`, then
  `|S|≤n^{2-ε}`. If `|S|>n^{2-ε}` then rectangle density `δ>n^{-ε}`.
  Proof: `proofs/lemma_case_split.md`.
- **Lemma 3.2.** Q4 forbids three vertices of any axis-aligned square (equal-leg
  corners). Alone this only recovers `O(n^2)`, not a power saving.
- **Lemma 3.3.** `|S| ≤ sqrt(8 n P)` for `|S|≥4n`, where `P` is the number of
  co-diagonal pairs. Thus `P=O(n)` would give `Q4(n)=O(n)`, but `P=O(n)` is unproved.

### Falsified as a proof idea (do not reuse)

Disjoint midpoint-kills ⇒ `|S|≤4n`. Exact maximisers violate disjointness as hard
as possible: `n=7` has `max r(a)=8` (eight diagonals share one killed anti-diagonal
`x+y=6`). Data: `out/upperbound/max_r_exact.json`. This is B4 overlap, realised
by an `O(n)` frame, not by a quadratic set.

### Computation on the dense branch (not a bound)

- Exact `n≤8`: `δ` from 1.0 down to 0.33; `max_dia` is 2–3; `K∩U_ant=0`.
- Dense random rectangles up to `81×(27×27)`: kept `~1.4n`, `δ` falling.
- 3-AP rectangle repair: `n=81` raw 256 → 110 (`1.36n`).
- Greedy max-`δ`: `δ~Θ(1/n)` (sparse branch).
- **No `n^{1+c}` set in the dense regime.** Q4-dies line still not fired.

### GAP (hardest remaining lemma)

Bound `P` (or show few diagonals can be heavy at once) tightly enough to beat
`n^{2-o(1)}`, while allowing (i) one 3-AP-free diagonal of size `r_3(n)` and
(ii) `r(a)=Θ(n)` frame overlap. `|M|≥m-1` plus AM-GM does not do it.

### What we are not claiming

- Not `Q4(n)=O(n^{2-ε})`.
- Not `Q4(n)=O(n)`.
- Not “Q4 is safe”.
- Not a result to merge into iso6 unless a human asks.

---

## Lemma 3 overlap dichotomy

**Verdict: Q4 dies. Sidecar upper bound is moot. Do not merge into iso6.**

### Case B / B′ (theorem)

If `max_a r(a) ≤ n^{1-ε}`, then `|S| ≤ (2n-1)(1+n^{1-ε}) = O(n^{2-ε})`.
The `√n` form is `ε=1/2`. Proof: `proofs/lemma3_caseB.md` and
`proofs/lemma3_campaign.md`. The single `r_3` diagonal (`r=1`) is in this case.

### Case A (partial)

Global heavy lines (`proofs/lemma3_heavy.md`), no fold required: if
`min(|H|,|J|) ≤ n^{1-ε}` or both `|H|,|J| ≤ n^{7/8}`, then
`|S| = O(n^{2-ε})`. This absorbs `S'` peeling. Remaining GAP:
`|H| > n^{7/8}` and `|J| > n^{3/4}`. Current tools do not close it
(packing, KST, `r_3`, `R|K|` interpolation, changing `ε`). If that
configuration exists, `|S| > n^{13/8}` and Q4 dies. Search through
`n=243` has `|H|=|J|=0`. Writeup: `proofs/lemma3_heavy.md`.

Forced-pair search (`lemma3_search.py`, `out/lemma3/forced_table.json`):

| n | |S| | |S|/n | max r | |S*| | |S'| | case |
|---|-----|-------|-------|------|------|------|
| 16 | 32 | 2.00 | 16 | 32 | 0 | A |
| 81 | 173 | 2.14 | 78 | 164 | 9 | A |
| 128 | 288 | 2.25 | 109 | 252 | 36 | A |
| 243 | 551 | 2.27 | 235 | 508 | 43 | A |

Old GAP “`max_dia(S*) = O(√n)`” is **false**. Scripts: `a1_construct.py`,
`a1_longrow.py`, `extra_budget.py`.

Mixed greedy at `n=128` is Case B (`max_r=7 ≤ √128`). Exact `n=7` frame is Case A, as required.

### `(d,α)` products (ammunition fails)

`da_product.py` → `out/da_product/summary.json`. Disjoint-difference products
are Q4-feasible and stay at `|S|/n ≤ 0.75`, not growing. FourDir bicliques
same. Kill line `|S|≥2.5n` not fired.

### Sidecar closed

iso6 falsified Q4 (`n^{2-o(1)}`). This lane's construction battery did not
find that family. The upper-bound lemmas do not survive as a campaign
proof. Stop. Do not merge into iso6.


