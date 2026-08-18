# J2 census (non-right leftovers; no named stencil)

This file lives in `d:\others\iso6-joint\proofs\`. It is **not** an iso6 proof.
Do not copy into `iso6/docs/`, `iso6/proofs/`, or `iso6/routes/`.

**Honesty.** Four-fold remains Q4-feasible, `Q4(n)=n^{2-o(1)}`. Nothing
here proves `Q4` or `C` has a power. A constraint that fires is not an
upper bound. **J2 is not named.** Not PROMISING.

Code: `j2.py`, `run_j2.py`. Output: `out/j2_*.json`.

---

## What was asked

J1 kills only `{b, b+u, b+R_±(u)}`. The rest of RF1 is equal-length legs
that are not a 90° rotation. The hope: a **short one-parameter** stencil
(like J1) that (i) is implied by RF1, (ii) is not a fifth line-kill,
(iii) fires on dense four-fold **and** on Q4-greedy, (iv) survives B4′.

The only rotations of `Z²` that send every vector to a lattice vector are
multiples of 90°. So the only universal one-parameter rotation stencils
are J1 (`±90°`) and collinear 3-AP (`180°`, legs `u,−u`). Anything else
is “two different representations of the same `r²`” — a two-parameter
family, i.e. RF1 minus Q4, the original leftover class already discarded
in `joint_candidates.md`.

This file records the census that confirms that diagnosis, and does
**not** invent a fake J2.

---

## Dense four-fold

Frequency-greedy `A,B,W,Z`. Every set Q4-verified. All triples are
Q4-form survivors (`killed=0`), as before.

| n | \|S\| | triples | J1 | 3-AP | other (Q4-surv) |
|---|---|---|---|---|---|
| 16 | 12 | 1 | 0 | 0 | 1 |
| 24 | 15 | 2 | 2 | 0 | 0 |
| 32 | 19 | 0 | 0 | 0 | 0 |
| 40 | 21 | 4 | 1 | 0 | 3 |
| 48 | 27 | 4 | 2 | 0 | 2 |
| 64 | 30 | 3 | 1 | 0 | 2 |

Non-J1 equal-length pairs **do** appear (`n=16,40,48,64`). Collinear 3-AP
does **not** on these dense samples. Examples:

- `n=16`: `r²=65`, outgoing `{(-1,8),(4,7)}` (`1²+8²=4²+7²`).
- `n=40`: `r²∈{1125,250,145}`, three distinct pairs, each once.
- `n=64`: `r²∈{2725,65}`.

No repeating `(u,v)` family. The `65` pair is the same two-squares
identity that also shows up in Gaussian peeling (`iso6-sq/proofs/iso_leak.md`);
it is still one `r²`, not a stencil for all `w∈Z²`.

---

## Independent Q4-greedy

| n | sets | J1 | 3-AP | other |
|---|---|---|---|---|
| 16 | 4 | 4/4 | 4/4 | 4/4 |
| 24 | 3 | 3/3 | 3/3 | 3/3 |
| 32 | 3 | 3/3 | 3/3 | 3/3 |

Every regenerated Q4-greedy set fires J1 **and** collinear 3-AP **and**
non-right non-collinear leftovers (`oth_surv` sums 48, 87, 197). The
leftover class is not a single named angle.

---

## Three-point four-fold embeds

Eight distinct leftover other-pairs from the dense four-fold census,
embedded as `{0,u,v}` shifted into `[n]²`:

- **8/8** have 3-AP-free `A,B,W,Z` (Q4-feasible as a three-point four-fold).
- **7/8** are **not** P1–P3 on the extra forms
  `2x±y, x±2y, 3x+y, x+3y`. The one extra-killed example is
  `u=(-8,-6)`, `v=(0,10)` (`r²=100`), a horizontal-ish pair.

B4′: a bounded extra-projection list does not kill the leftover class.
Rewriting “add these `r²` as extra line-kills” is the same dead move as
for J1.

---

## Verdict

| Claim | Status |
|---|---|
| J1 named, fires, not a finite extra-projection restatement | already recorded |
| Non-J1 Q4-survivors exist on four-fold | **true** |
| Those leftovers are one short stencil J2 | **false** (generic two-squares) |
| Collinear 3-AP as “J2” | fires on Q4-greedy; not on these four-folds; and “no 3-AP on every line” is not a finite joint lemma (B4′ if finitely many slopes) |
| PROMISING power route | **no** |

Do not merge into iso6. Human decision whether route Q sees the census.
