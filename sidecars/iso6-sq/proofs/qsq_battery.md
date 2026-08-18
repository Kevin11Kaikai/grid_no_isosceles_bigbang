# Q_SQ construction battery (sidecar only)

This file lives in `d:\others\iso6-sq\proofs\`. It is **not** an iso6 proof.
Do not copy into `iso6/docs/`, `iso6/proofs/`, or `iso6/routes/`.

**Honesty.** Nothing here proves `Q_SQ(n)=O(n^{2-ε})` or `C(n)=O(n^{2-ε})`.
The four-fold 3-AP-free intersection remains Q4-feasible. A failed battery is
not a safety proof (q4f missed the four-fold family; this lane may have missed
another). No PROMISING. No upper-bound attempt.

**Object.** A square-corner is `{b, b+w, b+R(w)}` with `R=±90°`, `w≠0`
(Cursor J1 / Claude square-corner). `Q_SQ(n)` = max size of a square-corner-free
subset of `[n]^2`. Checker: `sq.py`, exact integer arithmetic.

**Sanity.** An n=16 isosceles-free greedy set (`|S|=17`) is sq-free. Iso-free ⇒
sq-free is one-way.

---

## Negative controls

`B×B` with `B` = base-3 digit-2-avoiding:

| n | \|B\|² | corners |
|---|---|---|
| 27 | 64 | 448 |
| 81 | 256 | 3840 |
| 243 | 1024 | ≥20000 (enumeration capped) |

Uncorrelated four-fold (`A,B,W,Z` independent greedy 3-AP-free) is often sq-free
at `|S|≤9` — too sparse, same trap as finite Behrend. Frequency-greedy `W,Z` on
`A×B` produces corners at n=16,32,48 (`|S|=10,16,24`, 1 corner each). Explicit
four-fold embed of `u=(3,2)`, `R(u)=(-2,3)` is 3 points, 3-AP-free projections,
1 square-corner.

---

## Families

Repair = delete max-degree vertices (small sets) or delete **every** point that
sits in any square-corner (hit-repair; remaining is sq-free, possibly empty).

### Function graphs — linear floor

`y=ax+b` (mod n) and `y=x^3+x` (mod n) are sq-free at n=32,64,128 with `|S|=n`.
Quadratic `y=x^2` is not; repair leaves `~0.80n`. Embedded parabola `{(t,t^2)}`
is sq-free and size `~√n`.

### At most 2 per row/column

Without the sq constraint the cap saturates at `2n` and has many corners.
Enforcing `can_add` yields sq-free sets at `1.50n`–`1.67n` (n=16..48).

Independent greedy sq-free (comparator only): `1.81n, 2.00n, 2.16n, 2.19n`.
Log-log slopes 1.24, 1.26, 1.04. **Soft warning only** — same shape as Claude’s
`~2.5n` and as Q4’s `~1.8n`. Never a status change.

### Sidon / convex products

`A×A` for greedy Sidon, squares, cubes: corners present; repair returns density
`≲1` (Sidon n=128: 132/128=1.03). Cubes stay `o(n)`.

`r_3×r_3` (greedy 3-AP-free product, i.e. a `B×B` variant) has hundreds to
thousands of corners. Hit-repair **empties** the set at n=32,64,128.

### Classical-corner-free then repair — the intended kill path

`S={(x,y): y-x ∈ B}` with `B` 3-AP-free kills axis-aligned corners (a 3-AP in
`B`). Raw sizes: `8n` at n=27 (`|S|=216`), `16n` at n=81 (`|S|=1296`).

Those sets are saturated with **rotated** square corners (5610 at n=27; n=81
count skipped as large). Hit-repair remaining: **0**. Same for full rows
indexed by a 3-AP-free set (`n·r_3(n)` scale).

This class cannot be repaired into a superlinear sq-free set by deleting
participants. It is not a Q_SQ barrier.

### Modular

Hyperbola `xy≡1 (mod p)` and quadratic-residue graphs are size `~n`, not
sq-free; repair leaves `~0.7n`–`0.8n`.

---

## Verdict

**Ammunition failed, not safe.** No verified sq-free family on this battery has
`|S|/n` clearly growing, and the large algebraic candidates are corner-saturated.

This does **not** prove `Q_SQ(n)=O(n^{1+o(1)})`. It does mean this sidecar has
no construction that kills `Q_SQ` as a power-saving route. Whether to fund an
upper bound is a later human decision; this phase does not start one.
