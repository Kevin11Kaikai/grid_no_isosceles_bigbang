# Joint-constraint ledger (sidecar only)

This file lives in `d:\others\iso6-joint\`. It is **not** an iso6 ledger.
Do not copy into `iso6/docs/`, `iso6/ledgers/`, or `iso6/routes/`.

**判定（给人工看）**

- 任务是找一条 **RF1 推出的、四重 3-AP-free 交会违反的联合约束**，不是给 Q4 上界。
  Q4 已死：`Q4(n)=n^{2-o(1)}`。本车道 **没有**、也 **不得** 声称 `Q4` 或 `C(n)` 有幂次节约。
- 命名引理 **J1**（直角等腰 / 旋转 90° 模板）：无等腰 ⇒ 不含 `{b, b+u, b+R(u)}`，
  `R=±90°`。这是双腿约束，不是第五条直线封杀。
- J1 **会开火**：密四折 `n=24…64`、独立重生的 Q4-greedy（每个样本）、以及
  Q4-幸存旋转 90° 的三点四折嵌入（40/40）。
- **没有命名 J2。** 非直角 Q4-幸存等腰在密四折和每个 Q4-greedy 样本上都存在，
  但是「同一 r² 的两种表示」，不是 J1 那种一条参数的模板。Z² 上全局旋转只剩
  ±90°（J1）和 180°（共线 3-AP）。把剩余类整包命名 = RF1 减 Q4 = 原问题。
  三点嵌入 8/8 仍四折可行，7/8 不被额外线性型杀掉（B4′）。不标 PROMISING。
- B4′：**不是** “再加有限条 3-AP-free 投影” 的改写（296 个小模板里 276 个不被
  `(2,1),(1,2),…` 的 P1–P3 杀掉；存在五折见证仍违反 J1）。
  若改写成“加 `(2,1)` 和 `(1,2)` 做线杀”，则 **作为幂次路线已死**。
- **不标 PROMISING。** 人工决定要不要给 Claude / route Q 看。不要并进 iso6。

细节：`proofs/joint_candidates.md`（J1），`proofs/j2_census.md`（非直角普查）。
原始输出：`out/`.

---

## Isolation

- Frozen `iso.py`, `q4.py` (snapshot, no iso6 import).
- Four-fold = Sufficiency Lemma `S={(x,y): x∈A, y∈B, x+y∈W, x-y∈Z}` with
  3-AP-free `A,B,W,Z`.
- Q4-greedy regenerated here. Did not read `iso6/routes/Q/adv_*.json`.
- No edits to `iso6/` or `iso6-q4f/` upper-bound work.

---

## Census (dense four-fold)

All Q4-verified. Every isosceles triple is a Q4-form survivor (`killed=0`).

| n | \|S\| | triples | J1 |
|---|---|---|---|
| 16 | 12 | 1 | 0 |
| 20 | 14 | 1 | 0 |
| 24 | 16 | 3 | 2 |
| 32 | 21 | 10 | 6 |
| 40 | 25 | 10 | 8 |
| 48 | 24 | 6 | 3 |
| 64 | 32 | 4 | 2 |

Uncorrelated independent greedy `A,B,W,Z` stays around `|S|~10` and is often
isosceles-free (too sparse for forensics). Frequency-greedy `W,Z` is the dense
corpus. Smallest Q4-surviving J1 stencil: `u=(3,2)`, `r^2=13`.

## Independent Q4-greedy

J1 fires `8/8, 6/6, 6/6, 4/4, 3/3` at `n=16,20,24,32,40`. Rotate-90 is a large
share of leftover triples (e.g. 116/245 survivors at `n=16`).

## B4′

| Test | Result |
|---|---|
| Extra forms `2x±y, x±2y, 3x+y, x+3y` kill all small rot90 Q4-survivors? | No (276/296 leftover) |
| Dense four-fold + fifth 3-AP-free `φ_{(1,2)}` still fires J1? | Yes |
| Q4-greedy + those extra forms explain all J1? | No (25 leftover at n=32) |
| Five-fold 3-point witness (`φ_{(2,1)}` also 3-AP-free) fires J1? | Yes |
| Rewrite as extra line-kills `(2,1),(1,2)` | Dead for a power saving (B4′) |

## J2 census

Did not name a new stencil. Machine check in `out/j2_*.json`. See `proofs/j2_census.md`.

| corpus | J1 | 3-AP | other Q4-survivors |
|---|---|---|---|
| dense four-fold n=16…64 | some n | 0 | some n (generic two-squares) |
| Q4-greedy n=16,24,32 | every sample | every sample | every sample |

**Verdict: leftover class stays unnamed. Not PROMISING.**

## Not merged

Human decision whether Claude or route Q sees this. This sidecar does not
write into iso6.
