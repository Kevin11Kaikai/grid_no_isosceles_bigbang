# Lemma 3 — dense partial filling

Status: **partial (campaign split).** B′ and global heavy lines are proved.
One `(H,J)`-core remains. Campaign bound still open.

Old disjoint-kill argument remains false (§3.4). New writeup:

- [`lemma3_caseB.md`](lemma3_caseB.md) — complete (`√n` form)
- [`lemma3_caseA.md`](lemma3_caseA.md) — old A1 (`max_dia(S*)≤√n`) is false
- [`lemma3_campaign.md`](lemma3_campaign.md) — B′ / B″; old triple closed
- [`lemma3_sstar.md`](lemma3_sstar.md) — few heavy vertices on `S*`
- [`lemma3_heavy.md`](lemma3_heavy.md) — global heavy lines; one core GAP


## 3.0 Notation

`S` Q4-feasible. `m_d = |S ∩ diagonal_d|`. `P = Σ_d binom(m_d, 2)` = number of
unordered co-diagonal pairs. `M(A_d)` = pairwise midpoints of anti-values on `d`.
`K = ∪_d M(A_d)`. Constraint 3: `K ∩ U_ant = ∅`, so `|K| + |U_ant| ≤ 2n-1`.
`r(a) = #{d : a ∈ M(A_d)}` for `a ∈ K`. Then `Σ_{a ∈ K} r(a) = Σ_d |M(A_d)| ≥ Σ_d (m_d-1)_+ = |S| - |U_dia|`.

## 3.1 Proved: at most one point per diagonal implies linear size

If `m_d ≤ 1` for every main diagonal, then `|S| ≤ 2n-1`.
Likewise for anti-diagonals. So every set with `|S| > 2n-1` has some `m_d ≥ 2` and
some anti-diagonal with at least two points. (Exact: `Q4(7)=16 > 14`.)

## 3.2 Proved: no three vertices of an axis-aligned square

An axis-aligned square with step `Δ ≠ 0` has vertices
`(x,y), (x+Δ,y), (x,y+Δ), (x+Δ,y+Δ)`.
Any three of them contain either both main-diagonal vertices or both anti-diagonal
vertices. Those two vertices share a 45-degree line, and the third sits on the
midpoint transversal. Constraint 3 or 4 forbids it.

Equivalently: `S` contains no triple `(x,y), (x+Δ,y), (x,y+Δ)` (equal-leg corner),
nor the three other sign patterns. This uses constraints 3–4, not just 1–2.

A Cauchy–Schwarz count from `|c_x| + |r_y| ≤ n+1` at each occupied cell (when
boundary effects cooperate) only recovers `|S| ≤ n²/2`, i.e. L3, **not** a power
saving. Equal-leg corners alone are not enough.

## 3.3 Proved: Cauchy–Schwarz reduction to pair count

`Σ_d m_d² ≥ |S|² / |U_dia| ≥ |S|² / (2n)`.
Hence `P ≥ |S|²/(4n) - |S|/2`.
For `|S| ≥ 4n` one gets `|S|² ≤ 8 n P`, i.e.

```
|S|  ≤  sqrt(8 n P).
```

Consequences (all proved as implications, not as bounds on `P`):

- `P = O(n)` ⇒ `Q4(n) = O(n)`
- `P = O(n^{2-2ε})` ⇒ `Q4(n) = O(n^{1.5-ε})`
- a uniform `m_d ≤ n^{1-ε}` on every diagonal ⇒ `P ≤ n · n^{2-2ε}` ⇒ `|S| = O(n^{2-ε})`

The last implication **cannot** be used as a proof: a single 3-AP-free diagonal is
Q4-feasible of size `r_3(n) = n^{1-o(1)}` (constraints 1,2,4 vacuous; constraint 3
is 3-AP-freeness on that line). So `max_d m_d` is not `O(n^{1-ε})`.

## 3.4 Disjoint-kill bound, and why it fails

If the sets `M(A_d)` were pairwise disjoint, then
`|S| - |U_dia| ≤ |K| ≤ 2n - |U_ant|`, hence `|S| ≤ 4n - |U_ant|`.
Together with `|S| ≤ n |U_ant|` this yields `|S| ≤ 4n-4`.

This hypothesis is **false**. Exact maximisers pile many co-diagonal pairs onto
**one** killed anti-diagonal:

| n | |S| | max `r(a)` | `K` histogram |
|---|-----|-------------|---------------|
| 4 | 8 | 4 | `{3: 4}` |
| 7 | 16 | 8 | `{6: 8}` |
| 10 | 21 | 8 | `{9: 8}` |

`n=7` is a frame: 8 pairs, all reflections across the empty anti-diagonal `x+y=6`.
So `r(a)` can be `Θ(n)`. B4-style overlap is realised, and it is realised by an
`O(n)` set, not a quadratic one.

## 3.5 Product / dense-rectangle computations

Frozen checker, details in `out/upperbound/`.

- Full `A×B` (including Behrend `B×B`) is never Q4-feasible once some diagonal has
  two points. Q4-repair of the product has size `≤ 2n-1` at `n=9,16,27,32,81`
  (`product_sanity.json`). Agrees with lemma 1.
- Random `|R|×|T|` rectangles with `|R|,|T| ~ n/2` to `n/3`, greedy Q4-subset:
  kept size stays `~1.3–1.5 n`, rectangle density `δ` **falls** as the rectangle
  grows (`81, 27×27 → 117` points, `δ=0.20`). No `n^{1.3}` set.
- 3-AP-free × 3-AP-free repair: same linear residue (`n=81`, raw 256, kept 110).
- Greedy max-`δ` on the full grid: `δ ~ Θ(1/n)` (`n=64`, `δ=0.05`), i.e. the
  sparse branch of lemma 2, not the dense branch.

None of this is an upper bound. It is a failed attempt to kill lemma 3 by
counterexample, and a confirmation of lemma 1.

## 3.6 GAP (the remaining lemma)

To get a fixed `ε>0` one must bound `P` strictly below `n^3` in a way that
survives (i) one heavy 3-AP-free diagonal of size `n^{1-o(1)}` and (ii) the
`r(a)=Θ(n)` overlap of the frame examples.

A plausible route that was **not closed**: only `n^{o(1)}` diagonals can be heavy
at once, because `M(A_d)` must miss the union of all occupied anti-diagonals.
If that were true one would get `|S| = O(n^{3/2+o(1)})`, hence
`O(n^{2-1/2})`. The obstacle is anti-value reuse across diagonals (`λ = max_ant`
can be `≥2`, and the bound `|U_ant| ≥ (Σ m_d)/λ` with `λ ~ m` collapses to L3).

Using `|M(A_d)| ≥ m_d-1` plus AM-GM only yields `|S| ≤ O(n^2)`, no power.

## 3.7 Overlap dichotomy (current attack)

Let `R = max_a r(a)`.

**Case B (`R ≤ n^{1/2}`). Proved.**
`|S| ≤ (2n-1)(1+R) = O(n^{3/2})`. See `lemma3_caseB.md`.
The single 3-AP-free diagonal (`r=1`) lives here.

**Case A (`R > n^{1/2}`). Not closed.**
Fold is optional. Global heavy lines (`lemma3_heavy.md`) close Case A
unless `|H| > n^{7/8}` and `|J| > n^{3/4}`. The `n=7` frame has `H = J = ∅`.

Q4-dies line: not fired on forced or mixed searches (`out/lemma3/`).

## Verdict

Case B is a theorem. Campaign B′ and global heavy lines are theorems.
Lemma 3 as a whole is **not** a theorem. Do not claim `Q4(n)=O(n^{2-ε})`.

