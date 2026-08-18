# Q_SQ falsification ledger (sidecar only)

This file lives in `d:\others\iso6-sq\`. It is **not** an iso6 ledger.
Do not copy into `iso6/docs/`, `iso6/ledgers/`, or `iso6/routes/`.

**判定（给人工看）**

- 伪造电池漏掉了 Gaussian peeling（Károlyi–Solymosi）：`β=2+2i`、`P={0,1,i}` 的
  合成类在 `m=3…10` **全部 sq-free**（`peel.py` + `sq.py`）。定理给出
  `Q_SQ(n) ≫ n^{1.056}/log n`（论文还有 `Ω(n^{1.3})`）。有限 n 上 `|S|/n<1`，
  和 Behrend 一样小 n 看不见超线性。**greedy ~2.2n 不能当上界证据。**
- **一夜上界：没有幂次。** `O(n^{3/2})` 的 G≤mn 计数有不可修补的洞（会推出假的
  `O(n)`，与 peeling 矛盾）。不标 PROMISING。
- **二夜上界：仍没有幂次。** 未重跑 G≤mn。A：轻行 `m≤n^{3/2}` 真但重行禁区 `|F|≤rn` 太小，补集仍 Θ(n²)。B：`Σ|A_w|=m(m-1)` 与 `|A_w|+|A_{R(w)}|≤m` 真，CS 只给出 `m=O(n²)`；假定 `n_w=O(n)` 会假推出 `O(n)`，已拒绝。C：没有诚实点-线系统，跳过 ST。不标 PROMISING。
- **Peeling 相对 C 漏了。** `m=6…10` 全部 J1=0（sq-free），但等腰三元组很多
  （`m=9`：21595 个，其中 3-AP 1440、非直角非共线 20155）。`Q_SQ` 比 `C` 大，
  初等 square-corner 计数在打一个更大的函数。详见 `proofs/iso_leak.md`。
- **三夜上界：仍没有幂次。** 全体行/列禁区并集在 peeling 上仍留下 `>99.9%` 格子。
  两行共享列不是新几何（等于列内竖直对）。不标 PROMISING。
- 已证：Z[i] 形式 ⇔ J1；整行 sq-free；两整行必有 square-corner；重行禁区落在 r 列。
- **定理：两行支撑的 sq-free 集最多 \(2n-2\)。** \(F_2(n)=2n-2\)。相邻两行 \(F_2(n,1)=n+(n\bmod 2)\)。不是 \(Q_{\mathrm{SQ}}=O(n)\)，也不是 \(C(n)=O(n^{2-\varepsilon})\)。`proofs/two_row.md`。
- **三行：下界 \(F_3(n)\ge 2n-2+(n\bmod 2)\)（\(n\ge 4\)）已证；等号在 \(n\le 9\) 穷举成立，上界没有一般证明。不够发。停。** `proofs/three_row.md`。
- 四重交仍 Q4-可行。没有 `C(n)=O(n^{2-ε})`。

细节：`proofs/qsq_battery.md`（电池），`proofs/upper_bound.md`（一夜），
`proofs/upper_bound2.md`（二夜），`proofs/iso_leak.md`（等腰普查），
`proofs/upper_bound3.md`（三夜），`proofs/two_row.md`（两行定理），
`proofs/three_row.md`（三行：下界已证，上界停）。
原始输出：`out/peel.json`, `out/lemmas.json`, `out/power_counts.json`,
`out/attempt2_A.json`, `out/attempt2_B.json`, `out/attempt2_C.json`,
`out/iso_census.json`, `out/attempt3_D.json`, `out/two_row.json`,
`out/F_k.json`.

---

## Isolation

- Frozen `sq.py` (no iso6 / Q / iso6-joint import). Tiny `iso.py` only to check
  iso-free ⇒ sq-free. Census lives in `iso_census.py`.
- Did not edit `iso6/` or `iso6-q4f/`. This sidecar does not import `iso6-joint`.
- Did not recompute Claude’s greedy table or exact `Q_SQ(n)` for n≤7.

## Kill / fail lines

`|S|≥n^{1.1}` is not informative for `n<1024`. Used:

| Line | Meaning |
|---|---|
| **Q_SQ dies** | verified sq-free family with `|S|/n` clearly growing, or algebraic `n^{1+c}` / `n^{2-o(1)}` |
| **Ammunition fails** | that family repairs to `O(n)` / ratio not growing / hit-repair empties the set |
| **Soft warning only** | independent greedy stays `~2n` |

**Verdict: ammunition fails. Not a safety proof.**

## Negative controls

| family | n | \|S\| | sq-free | corners |
|---|---|---|---|---|
| BxB | 27 | 64 | no | 448 |
| BxB | 81 | 256 | no | 3840 |
| BxB | 243 | 1024 | no | ≥20000 (count capped) |
| fourfold (uncorrelated) | 16–64 | 2–9 | often yes | sparse trap |
| fourfold_freq | 16,32,48 | 10–24 | **no** | 1 |
| fourfold J1 embed `u=(3,2)` | 16 | 3 | **no** | 1 (3-AP-free projections) |

`B×B` is loaded with square corners (matches Q). Uncorrelated four-fold is too sparse
to see them (same finite-n trap as Behrend at n=2187). Dense four-fold and the 3-point
embed **do** violate sq-freeness. Checker is not a tautology.

## Battery (sq-free survivors only matter)

| family | n stretch | sq-free \|S\|/n | log-log slope | line |
|---|---|---|---|---|
| graph_linear | 32–128 | 1.00 | 1.00 | ammo fails (linear floor) |
| graph_cubic | 32–128 | 1.00 | 1.00 | ammo fails |
| graph_quadratic+repair | 32–128 | ~0.80 | ~1.0 | ammo fails |
| hyperbola+repair | 32–128 | 0.69–0.77 | ~1.1 | ammo fails |
| quad_res+repair | 32–128 | 0.77–0.84 | ~1.0 | ammo fails |
| sidon×sidon+repair | 32–128 | 0.88–1.31 | mixed, density ~1 | ammo fails |
| squares×squares+repair | 32–64 | 0.73–0.75 | ~1 | ammo fails |
| greedy_2rc_sq | 16–48 | 1.50–1.67 | ~1.0–1.2 | ammo fails |
| greedy_sq_free | 16–48 | 1.81–2.19 | ~1.0–1.3 | **soft warning only** |
| r3×r3 + hit-repair | 32–128 | **0** | — | every point in a corner |
| classical_corner_free + hit-repair | 27,81 | **0** | — | same; raw size 8n–16n but all dirty |
| full_rows_3ap + hit-repair | 27,81 | **0** | — | same |

The most plausible path to `n^{1+c}` (classical-corner-free / Behrend rows) is
**saturated** with rotated square corners: one-shot deletion of all participants
empties the set. That is a strong ammunition-fail for this construction class, not
a proof that no other class exists.

## Attempt 2 (heavy rows / energy / ST)

Did not retry `G≤mn`. Machine check in `out/attempt2_*.json`.

| method | true piece | hole |
|---|---|---|
| A light | all `r_y≤√n` ⇒ `m≤n^{3/2}` | incomplete: peeling is all-light at `m≤9`, heavy case still needed |
| A heavy | `F` in `r` columns, `|F|≤r n` | leftover `n²-|F|` is large (full row `n=64`: 1056 cells left) |
| B | `Σ|A_w|=m(m-1)`; pairing `|A_w|+|A_{R(w)}|≤m`; CS | only `m=O(n²)`; `n_w=O(n)` would fake `O(n)` |
| C | — | skipped: IRT is a rotation, not a named incidence system |

**Verdict: no power. Not PROMISING.** Isolation unchanged.

## Attempt 3 (row/col union) and iso leak

| check | result |
|---|---|
| peeling J1 | 0 (still sq-free) |
| peeling isosceles | large (`m=9`: 21595 triples, 20155 non-right) |
| all-row ∪ all-col `F` on peeling | leftover `>99.9%` of bbox |
| two-row shared columns | same cells as vertical pairs; leftover still Θ(n²) |

**Verdict: Q_SQ leaks vs C. No power. Not PROMISING.** See `proofs/iso_leak.md`,
`proofs/upper_bound3.md`.

## Not merged

Human decision whether Claude / route Q sees this. No iso6 merge.
