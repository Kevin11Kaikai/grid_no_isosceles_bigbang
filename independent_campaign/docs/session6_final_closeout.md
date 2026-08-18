# Problem 6.59 — No-Isosceles-Triangle Grid Sets — Final Closeout

> ## ⚠ SUPERSEDED IN PART — read `prior_art_audit.md` first
>
> This document was written **before** the prior-art audit was unsealed (2026-08-17) and
> before the post-closeout work in `proofs/ideal_uniformity.md`. Its body is preserved
> unedited as the record of the blind discovery phase. Three of its conclusions no longer
> stand:
>
> 1. **"Every result remains `NOVELTY_UNASSESSED`"** — no longer true. The audit ran.
>    Its verdicts: the square-corner / `Z[i]` formulation is **known** (Observation 2.1 of
>    arXiv:2607.22828); the tensor lemma is **known** — it is the mechanism of that paper's
>    `Ω(n^{1.318})` construction; the campaign's `Ω(n^{1.1562})` is **superseded**;
>    Theorem 4 is **known in substance** (their Remark 2.5). `C(12) = 20` was **not found**
>    in the literature and is the only surviving candidate contribution.
> 2. **"One surviving relaxation … not capped at `n^{2-o(1)}`"** — the *barrier* claim held
>    up, but the route did not. `Q_SQ` is the published quantity `F(n)`, whose best known
>    upper bound is Bloom's `O(n²/(log n)^{1-ε})` — **weaker than the baseline
>    `n·r_3(n)`** for the original problem. The relaxation is therefore lossy, and route SQ
>    is **DEPRIORITIZED**, not live.
> 3. **The resume plan in §9** is obsolete. Items 1–3 target `Q_SQ`, now deprioritized;
>    item 3 in particular is void, since `m(p)` was proved to be the *same problem* as
>    `g(q)`, not a cheaper sub-problem (`proofs/ideal_uniformity.md`, Theorem B).
>
> Also added after this document was written: Theorems A and B and Lemma C
> (`proofs/ideal_uniformity.md`), failure-ledger entries **F4** (small-scale tower ratios
> retired as an uninformative instrument), **F5** (the finite-margin `(1+i)`-tower
> recurrence falsified by exact computation), and **F6** (blind mode self-collision), and
> the root-level re-verification of `C(12) = 20` now packaged in `submission/`.
>
> The bottom line below is unchanged and remains correct: **the target was not reached.**

`C(n) = max |S|`, `S ⊆ {0,…,n-1}^2`, no three distinct `a,b,c ∈ S` with `d(a,b) = d(b,c)`
(squared Euclidean; degenerate/collinear triples included).

**Target: `C(n) = O(n^{2-ε})` for fixed `ε > 0`.**

> ## Bottom line
>
> **The target was not reached. No fixed polynomial saving was proved.** The strongest
> upper bound established in-campaign is `C(n) ≤ (1/2 + o(1))n^2`, which is *weaker* than
> the sealed baseline `n^2 exp(-c(log n)^{1/9})`; it is recorded for its mechanism, not its
> value. Nothing here improves the known bound.
>
> What the campaign did produce: an exhaustively certified new exact value, a barrier
> taxonomy of eight class-impossibility results that rules out most of the natural attack
> surface, two routes killed by explicit counterexample, and **one surviving relaxation
> that is provably not capped at `n^{2-o(1)}` by the construction method that caps
> everything else** — carrying a single, fully explicit remaining obligation.
>
> Every result remains `NOVELTY_UNASSESSED`. The prior-art audit (§23) was never unsealed,
> so nothing below is claimed as new.

---

## 1. Certified exact values

`C(12) = 20`, closing the supplied bracket `20 ≤ C(12) ≤ 23` at its lower end.
Exhaustive, and the decisive run had **symmetry reduction disabled**, so the certificate
depends on no symmetry argument: 45 922 791 007 nodes, no 21-point set exists. Three
distinct 20-point witnesses pass an independent naive verifier. `routes/C/report.md`.

Solver calibration, all independent of the sealed data: `C(1..11)` re-derived with no
disagreement; `C(1,n) = r_3(n)` reproduced as the exact Salem–Spencer sequence to `n = 34`;
all maximum sets enumerated for `n = 8,9,10` (unique up to `D4` at `n = 9, 10`).

## 2. Reformulations (`proofs/root_reformulations.md`)

Bisector · reflection · proper-edge-colouring · lattice-3-AP · paraboloid-lifting forms;
the lattice-point criterion L1 for perpendicular bisectors; and L2, the multi-direction
line-kill, which ranging over *all* primitive directions is **equivalent to the full
problem**. So the line-kill formulation loses no information — its failure was
methodological (independent summation over directions), not informational.

## 3. Barrier taxonomy — what is now ruled out

Each is a *class* impossibility: a construction proving that no argument confined to that
class can beat the stated cap.

| | mechanism class capped | cap | status |
|---|---|---|---|
| B1 | shell / distance-multiplicity counting | `n^2/√log n` | rigorous (Landau–Ramanujan) |
| B2 | lattice 3-AP-freeness | `n^{2-o(1)}` | rigorous (Behrend `B×B`) |
| B3 | axis line-kill, full strength | `n^{2-o(1)}` | rigorous (same `B×B`) |
| B4′ | line-kill with `O(1)` directions | `n^{2-o(1)}` | rigorous (`proofs/q4_falsified.md`) |
| B5 | scale-iteration arithmetic | polylog only | rigorous |
| **B6** | **degree `≤ k` instead of `≤ 1`** | **`n^{2-2/(k+1)-o(1)}`** | rigorous |
| B7 | distances of length `≤ L` only | `~n^2/L` | rigorous |
| B8 | distinctness at `n^{o(1)}` apexes only | `n^{2-o(1)}` | rigorous |

**B6 is the sharpest instruction the campaign produced.** Relaxing "degree exactly `≤ 1`"
to `≤ 2` raises the maximum from `n^{1+o(1)}` to `n^{4/3-o(1)}` — a polynomial jump. So any
argument that survives replacing 1 by 2 in the degree bound cannot prove better than
`O(n^{4/3})`. That includes essentially every counting, energy, `L^2`, Fourier and
regularity argument, all of which lose only a constant factor when a radius class holds two
points instead of one. A proof of `n^{1+o(1)}` must break the instant it admits a single
radius class of size 2.

B7 adds that the difficulty is spread evenly over all dyadic scales — each doubling of the
length scale buys exactly a factor 2, so there is no hardest scale to attack — and that the
radius-`R`-truncated problem is *exactly* the full problem on a torus of side `~2√R`.

## 4. The falsification record

Routes were killed only by explicit counterexample, never by opinion (§10).

- **Q4 (four-direction line-kill) — `FALSIFIED`.** A four-fold intersection of shifted
  Behrend sets satisfies all four constraints at `n^{2-o(1)}`. Killed *inside* the
  falsification-first gate, before the proof effort it was meant to justify was funded.
  Generalises to B4′. `proofs/q4_falsified.md`, failure ledger F1.
- **Route E (boundary increment) — refuted as framed (Z1).** For `n = 3,4,6`, **zero**
  optimal `n×n` sets admit any addition from the `(n+1)`-strip, yet `C(n+1) > C(n)`. So the
  naive interior/strip induction measures a quantity that can be zero while the true
  increment is positive; it bounds `C(n+1)-C(n)` neither above nor below.
- **No product/lift construction.** `C(16) = 28 < 36 = C(4)^2`, so `C(n^2) ≥ C(n)^2` is
  false — the standard route to a polynomial *lower*-bound improvement is closed.
- **SQ (square corners) — SURVIVED.** See §5.

## 5. The one live route: the square-corner relaxation

Full mathematics and verification: `proofs/square_corner.md`.

A *square corner* is `{b, b+w, b+i·w}` with `i·(w₁,w₂) = (-w₂,w₁)`. Since `|w| = |i·w|`,
every isosceles-free set is square-corner-free, so `C(n) ≤ Q_SQ(n)`.

**Why it is different from everything else tried.**

1. *It is one translation-invariant equation.* Square-corner-freeness is exactly the
   avoidance of `v = i·u + (1-i)·b` over `Z[i]`, coefficients summing to zero. The classical
   corners configuration provably satisfies no such relation. So this is a complexity-1
   (Roth-type) condition where corners is complexity 2 — the geometry is fully discharged
   into a single clean equation.
2. *The Behrend method provably fails against it.* Every `n^{2-o(1)}` barrier set in this
   campaign (B2, B3, B4′) comes from one method: digit expansion plus a sphere condition,
   i.e. a quadratic form that is a direct sum over digits. **No such construction can be
   square-corner-free**, because the per-digit triple `(b_j, i·b_j, -i·b_j)` satisfies the
   equation digitwise *and* preserves any direct-sum form (Theorem 4, machine-confirmed).
   This defeats the construction **method**, not one instance — precisely the mistake that
   made Q4 look promising (F1).
3. *Circle rigidity.* On any lattice circle the only square corners are `(b, i·b, -i·b)`:
   exhaustively, `R ≤ 6000`, 18852 corners found, 18852 of that form, **0** others.
4. *It is exactly self-similar.* With `g(q)` the maximum on the torus `(Z_q)^2`, the tensor
   lemma gives `Q_SQ(n) = Ω(n^{log g(q)/log q})` for every `q`, needing no carry analysis.
   So bounding `g` bounds everything.
5. *An explicit witness that it is the right constraint.* Route Q built a member of the B4′
   barrier family at `n = 200` — `A,B,W,Z` all 3-AP-free, all four line-kill constraints
   satisfied — whose **only** isosceles triple is a single square corner (apex `(66,66)`,
   `w = (2,3)`). The minimal possible counterexample is realised.

**How hard the falsification attempt was pushed, and its outcome.**

| instrument | result | exponent reached |
|---|---|---|
| Behrend digit-sphere | *proved* impossible (Theorem 4) | — |
| exact `g(q)`, `q ≤ 11`, symmetry cross-checked | `2,3,4,5,6,8,9,11,12,16` | **1.156** (rigorous) |
| product construction via `m(p) = p^{0.547±0.005}`, `p ≤ 8009` | flat, not drifting up | 1.094 |
| torus search, `q ≤ 64` | flat across `q = 13…64` | 1.095 |
| planar search, `n ≤ 320` (route Q) | `~2.8n` | ~1.12 |

Two independent instruments — the one-dimensional twisted-AP reduction and direct torus
search — agree to three digits. Nothing approaches the `2.0` that would kill the route.
`m(p)` exhaustive values agree with search **exactly** wherever both were computed, so the
search is optimal on its whole checkable range.

**Rigorously established:** `Q_SQ(n) = Ω(n^{1.1562})` (from exact `g(11) = 16` plus the
tensor lemma, witness independently verified) and `Q_SQ(n) = o(n^2)` (it implies
corner-freeness). Square-corner-free sets are provably superlinear, so the relaxation
cannot prove `C(n) = O(n^{1.15})` — irrelevant, since the target is `O(n^{2-ε})`.

**The single remaining obligation of the entire campaign:**
```
                      prove   Q_SQ(n) = O(n^{2-ε})
```
which immediately gives `C(n) = O(n^{2-ε})`. The target quantity is pinned between
`n^{1.1562}` and `o(n^2)`; the object is one invariant three-variable equation over `Z[i]`;
it is exactly self-similar; and no Behrend-type obstruction exists.

**Honest caveat, stated as plainly as possible.** Unbarriered is not provable. A power
saving for a Roth-type problem is not available from the density-increment machinery as it
stands — that machinery is exactly what yields `exp(-c(log n)^{1/9})` rather than `n^{-ε}`
in every known case. This route removes the construction-side obstruction that killed every
other mechanism and reduces the geometry to one equation. That is a real reduction in
difficulty. **It is not a proof and must not be reported as one.**

## 6. Methodology findings worth keeping

- **The SURVIVAL RULE is why this campaign has results.** Waves 1 and 2 (eight, then nine
  branches) were destroyed by the API session limit and left *nothing* — no branch ever
  wrote a report. Wave 3 carried a mandatory rule: create `report.md` within the first few
  tool calls and append continuously, assuming termination at any moment. All three wave-3
  branches were again killed by the session limit, and all three left complete, recoverable
  reports. Same failure, opposite outcome.
- **The dominant bug class was hand-derived incremental filters.** Three separate times a
  hand-enumerated "which cells does adding this point forbid" table omitted cases: the Q4
  averaging box (one shift range truncated), the C torus solver and the exact twisted-AP
  solver (each listing 4 of the 6 ways a pair extends to a forbidden triple). Every one
  produced *plausible* wrong numbers — an inflated `m(5) = 3`, invalid `g(q)` witnesses —
  and every one was caught the same way: by re-testing against the complete definition with
  an independently written checker. **Never let a hand-derived filter be the only test.**
- **The Q4 promotion error, and its mirror image.** Q4 was promoted on the strength of
  defeating one barrier *construction*, which was silently treated as having no barrier at
  all. The lesson recorded then — heuristic search lower bounds must never raise a route's
  status — was applied here, but note the asymmetry that makes SQ's evidence admissible:
  the route dies iff a *large* construction exists, so search failing to find one is
  evidence of survival, whereas for Q4 the analogous search was estimating an *upper* bound
  and was worthless. Direction of the inequality decides whether search counts.
- **Extremal sets are rigid and non-algebraic.** The `n = 9` and `n = 10` optima are unique
  up to symmetry, leave whole rows empty, and pair identical rows at fixed offsets. No
  algebraic family tested (modular parabola, cube, inverse, primitive-root graph, Sidon,
  lattice circles, 2-D Behrend spheres) is isosceles-free, and none beats plain greedy. The
  problem resists algebraic construction in a way 3-AP problems do not — weak evidence that
  the truth is near `n^{1+o(1)}`.

## 7. Isolation and novelty status

§3 hard isolation was maintained throughout: no web search, no literature database, no
external problem-specific retrieval, no prior-session material. Only the problem statement,
the sealed baseline packet, standard in-model mathematics, in-session reasoning, and code
written from scratch in-session.

Consequently **everything above is `NOVELTY_UNASSESSED`.** The prior-art audit was never
unsealed. When it is, check first, in this order: (i) whether the square-corner /
`Z[i]`-invariant-equation formulation is known and whether `Q_SQ` has been studied under
another name (rotated corners, Gaussian-integer Roth); (ii) whether the degree-`k`
relaxation bound `n^{2-2/(k+1)-o(1)}` is known; (iii) whether `C(12) = 20` is already
recorded.

## 8. Artifacts

```
proofs/      root_reformulations.md   q4_falsified.md   square_corner.md
docs/        barriers.md   Q4_route.md (FALSIFIED)   session6_final_closeout.md
ledgers/     approach_registry.md  verified_results.md  failure_ledger.md
             proof_obligation_ledger.md
experiments/ root_checks.py  barrier_checks.py  four_direction_linekill.py
             q4_soundness.py  q4_falsify_root.py  q4_barrier_proof.py
             root_zero_extension.py  square_corner_root.py  torus_sq.py
             torus_sq.c  torus_verify.py  torus_greedy.py
             twisted_ap.py  twisted_ap_exact.py
routes/      C/report.md  H/report.md  Q/report.md  (+ their source trees)
```

## 9. If the campaign resumes

1. Attack `Q_SQ(n) = O(n^{2-ε})` directly — it is the whole remaining obligation, and by
   the tensor lemma it suffices to bound `g(q)` on the torus. Note B6 applies here too: any
   argument robust to degree 2 is capped at `n^{4/3}`, so check candidate arguments against
   B6 *before* developing them.
2. Settle `g(q)` exactly for `q = 12…17`. The exact values are the only rigorous handle on
   the exponent, and the gap between exact (`1.156` at `q=11`) and heuristic (`1.095`) says
   the search is *under*-estimating — exact values may push the rigorous lower bound up and
   are the cheapest way to test whether the exponent is really flat.
3. Determine the truth about `m(p)`: is it `√p · polylog` or `p^{1/2+c}`? An upper bound on
   `m(p)` would be the first genuine upper-bound progress in the campaign, and it is a
   clean one-dimensional question about a single invariant equation over `F_p`.
4. Routes A, B, F, D, G were never run. Given B6/B7/B8, D and G should be re-scoped before
   any spend: any argument they produce that is robust at degree 2 is dead on arrival.
