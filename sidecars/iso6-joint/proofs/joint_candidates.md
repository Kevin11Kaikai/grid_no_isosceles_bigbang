# Joint candidates (sidecar only)

This file lives in `d:\others\iso6-joint\proofs\`. It is **not** an iso6 proof.
Do not copy into `iso6/docs/`, `iso6/proofs/`, or `iso6/routes/`.

**Honesty.** The four-fold 3-AP-free intersection remains Q4-feasible and
`Q4(n)=n^{2-o(1)}`. Nothing here proves `Q4(n)=O(n^{2-ε})` or `C(n)=O(n^{2-ε})`.
A joint lemma that *fires* on that adversary is a constraint, not an upper bound.

**Status of J1:** named, checkable, implied by RF1, fires on dense four-fold and
on independently regenerated Q4-greedy, and is **not** a restatement of a fixed
finite list of extra 3-AP-free projections (B4′). **Not PROMISING** as a
power-saving route — the Q4 lesson.

---

## Recap

RF1: `S` isosceles-free iff it contains no three distinct `a,b,c` with
`|a-b|^2 = |b-c|^2` (exact integer squared distances).

Q4 line-kill in direction `e` kills only pattern **P1** on `ψ(x,y)=e·(x,y)`.
A 3-AP-free projection kills **P1+P2+P3**. With
`u = b-a`, `v = c-b`, `U=ψ(u)`, `V=ψ(v)`:

- P1: `U=V ≠ 0`
- P2: `U+2V=0`, `U≠0`
- P3: `2U+V=0`, `V≠0`

The four Q4 forms are `x`, `y`, `x+y`, `x-y`. Every isosceles triple in a
four-fold `S` must sit in the **survivor class**: `|u|^2=|v|^2` and not P1–P3
on those four forms. (Verified: `killed=0` on every dense four-fold below.)

---

## Lemma J1 (right-isosceles / rotate-90 stencil)

Let `R_±` be rotation by `±90°` on `Z^2`: `R_+(p,q)=(-q,p)`, `R_-(p,q)=(q,-p)`.

If `S` is isosceles-free, then `S` contains no three points of the form

```
{ b,  b+u,  b+R(u) }     u ≠ 0,   R ∈ {R_+, R_-}.
```

*Proof.* The two legs from apex `b` are `u` and `R(u)`, and `|u|^2=|R(u)|^2`.
This is an instance of RF1. ∎

This is a **two-leg** constraint on a single pair of displacements. It is not
a fifth line-kill (the three points are not collinear).

### Which rotate-90 stencils Q4 already kills

Q4 (equivalently: four 3-AP-free projections) kills some, not all, of J1.

| `u` | `R_+(u)` | Q4 forms | note |
|---|---|---|---|
| `(1,1)` | `(-1,1)` | P1 on `y` | 45° |
| `(2,1)` | `(-1,2)` | P2 on `x` | |
| `(1,2)` | `(-2,1)` | P3 on `x` | |
| `(3,1)` | `(-1,3)` | P3 on `x-y` | |
| `(1,3)` | `(-3,1)` | P2 on `x+y` | |
| `(3,2)` | `(-2,3)` | **none** | smallest survivor, `r^2=13` |
| `(4,1)` | `(-1,4)` | **none** | `r^2=17` |
| `(5,1)` | `(-1,5)` | **none** | |
| `(5,2)` | `(-2,5)` | **none** | |
| `(4,3)` | `(-3,4)` | **none** | |

The surviving family begins at equal legs of squared length 13, not at
`(2,1)` / `(1,2)`. Adding those two directions as extra line-kills is the
wrong reading of the leftover (and is B4′-dead as a power-saving route anyway).

---

## Census

Frozen checkers: `iso.py`, `q4.py`. Four-fold builder: `fourfold.py` (greedy
and frequency-greedy 3-AP-free `A,B,W,Z`; Sufficiency Lemma definition).
Independent Q4-greedy: `q4_greedy.py` (regenerated here; does not read
`routes/Q`). Classifier: `census.py`.

### Dense four-fold

Frequency-greedy `W,Z` on dense `A×B`. Every set Q4-verified.

| n | kind | \|S\| | iso-free | triples | Q4-killed | survivors | J1 |
|---|---|---|---|---|---|---|---|
| 16 | freq | 12 | no | 1 | 0 | 1 | 0 |
| 20 | freq_zfirst | 14 | no | 1 | 0 | 1 | 0 |
| 24 | freq_zfirst | 16 | no | 3 | 0 | 3 | 2 |
| 32 | freq | 21 | no | 10 | 0 | 10 | 6 |
| 40 | freq | 25 | no | 10 | 0 | 10 | 8 |
| 48 | freq | 24 | no | 6 | 0 | 6 | 3 |
| 64 | freq | 32 | no | 4 | 0 | 4 | 2 |

- **All** four-fold triples are construction survivors (`killed=0`).
- J1 fires for `n≥24`. Frequent leftover `(u,v)` are rotate-90:
  `(5,8)`/`(8,-5)`, `(6,17)`/`(17,-6)`, `(7,17)`/`(17,7)`, `(11,15)`/`(15,-11)`,
  `(13,30)`/`(30,-13)`.
- Independent uncorrelated `A,B,W,Z` is too sparse (`|S|~10`) and often
  isosceles-free — same finite-n phenomenon as Behrend at `n=2187`. The lemma
  is about the **pattern class**, witnessed on dense four-fold / Q4-greedy /
  explicit 3-point embeds.

Explicit four-fold witness (3 points): `u=(3,2)`, `R_+(u)=(-2,3)`, shifted
into `[n]^2`. All 40 small Q4-surviving rot90 embeds (`pmax=8`) are Q4-feasible,
have 3-AP-free `A,B,W,Z`, and fire J1 (`out/j1_fourfold_embeds.json`).

### Independent Q4-greedy

| n | sets | J1 fires | mean \|S\| | triples | survivors | rot90 survivors |
|---|---|---|---|---|---|---|
| 16 | 8 | 8/8 | 25.9 | 333 | 245 | 116 |
| 20 | 6 | 6/6 | 31.7 | 341 | 253 | 103 |
| 24 | 6 | 6/6 | 37.8 | 441 | 349 | 127 |
| 32 | 4 | 4/4 | 53.2 | 519 | 429 | 152 |
| 40 | 3 | 3/3 | 64.7 | 517 | 448 | 163 |

J1 fires on **every** regenerated Q4-greedy set. Rotate-90 is a large slice of
the leftover; other equal-leg survivors exist (e.g. 3-4-5 with a horizontal
leg `v=(5,0)`). Those are also RF1, but they are not needed to name J1.

---

## B4′ gate

For a fixed extra-form list

```
2x+y, x+2y, 2x-y, x-2y, 3x+y, x+3y
```

- Of 296 small rotate-90 Q4-survivors (`pmax=10`), **276** are not P1–P3 on any
  of those forms. Killing direction for a stencil `u=(p,q)` depends on `(p,q)`
  (`P1` along `e ⊥ (u-R(u))`). No bounded list of extra projections kills J1.
- Dense four-fold at `n=32` (`|S|=19`, J1 count 4): extra forms explain **0**
  of the 4 stencils. Thinning so that `φ_{(1,2)}` is 3-AP-free **still fires J1**
  (2 leftover). Thinning along `(2,1)` happened to delete this sample's four
  stencils; that is fiber-greedy loss, not a pattern kill — the family test
  says `(2,1)` does not P1–P3-kill 276/296 survivors.
- Q4-greedy `n=32` (`|S|=51`, J1 count 31): 25 stencils survive the extra-form
  list. After a fifth 3-AP-free projection, J1 still fires for `e∈{(2,1),(1,2),
  (2,-1),(3,1),(1,3)}`.
- Five-fold witness: three points with `u=(-10,-9)`, `R_+(u)=(9,-10)`, plus
  `φ_{(2,1)}` 3-AP-free, still Q4-feasible, still fires J1
  (`out/b4_gate.json`).

**Verdict.** J1 is joint enough to keep as a named constraint. It is **dead as
a power-saving route if rewritten as “add (2,1) and (1,2) as line-kills”**
(B4′: any bounded list of extra 3-AP-free projections is still `n^{2-o(1)}`).
Do not call it PROMISING.

---

## Discarded

- **Two-form midpoint.** Census leftovers are dominated by rotate-90 equal
  legs, not by a repeating “two non-Q4 `e`-lines meet at the bisector” stencil.
  No separate lemma.
- **Extra line-kills `(2,1)` and `(1,2)`.** `(2,1)` rotate-90 is already Q4-killed
  (P2/P3). Using them as a fifth/sixth projection is B4′-dead for a power
  saving. Diagnostic only.
- **Full leftover class `{|u|^2=|v|^2 not P1–P3 on Q4}`.** That is isosceles-freeness
  minus Q4, i.e. the original problem, not a short named family.
  Re-checked in `proofs/j2_census.md`: non-J1 survivors exist, 8/8 three-point
  embeds are four-fold feasible, 7/8 survive extra forms, still no one-parameter
  J2. Collinear 3-AP fires on Q4-greedy, not on the dense four-fold samples here.

---

## What this is not

- Not a proof that four-fold S is small.
- Not a merge into iso6, route Q, or `iso6-q4f`.
- Finite Behrend four-fold may be isosceles-free by sparsity; J1 is still
  implied by RF1 and is violated by every Q4-surviving rotate-90 triple,
  including those that are themselves four-folds of 3-AP-free 3-element sets.
