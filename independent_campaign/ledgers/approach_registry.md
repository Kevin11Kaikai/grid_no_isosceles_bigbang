# Approach Registry — Problem 6.59 (No-Isosceles Grid Sets)

Statuses: EXPLORING | PROMISING | BLOCKED | DEPRIORITIZED | FALSIFIED | MERGED | VERIFIED | CHAMPION

Target: `C(n) = O(n^{2-eps})` for fixed eps > 0.
Baseline (KNOWN, do not claim): `C(n) <= n * r_3(n) = n^2 exp(-c (log n)^{1/9})`.

---

## R0 — Root orchestrator notes (not a route)

Reformulations established in-session (see `proofs/root_reformulations.md`):

- **(RF1) Bisector form.** S is isosceles-free iff for every pair a,c in S, S contains no
  point of the perpendicular bisector of a,c.
- **(RF2) Reflection form.** For every line L in the plane: if S meets L then S contains no
  pair {a, sigma_L(a)} with a not on L. Equivalently `S ∩ sigma_L(S) ⊆ L`.
- **(RF3) Matching form.** For every r, the "distance-r graph" restricted to S has max degree
  <= 1. Equivalently the complete graph on S, edge-coloured by squared distance, is a
  *proper edge colouring*.
- **(RF4) 2D-AP form.** S contains no 3-term AP in Z^2 (midpoint of any two congruent-mod-2
  points is excluded). Strictly stronger than "every axis line is 3-AP-free".

---

## Route table

| ID | Mechanism | Status | Owner |
|----|-----------|--------|-------|
| R0 | Root: bisector/reflection reformulations + multi-direction line-kill | BLOCKED (B4′) | root |
| **SQ** | **Square-corner relaxation `{b, b+w, b+i·w}`** | **DEPRIORITIZED** (prior-art audit) | root (from Q) |
| A | Blind, unconstrained framing | NEVER RAN (session limit) | agent |
| B | Blind, "find the right representation" framing | NEVER RAN (session limit) | agent |
| C | Computational extremal laboratory / exact solver | **COMPLETE** — `C(12)=20` certified | agent |
| D | Cross-scale recurrence C(kn) <= (k^2-delta)C(n) | UNSTARTED; constrained by B5 | specialist |
| E | Boundary increment C(n+1)-C(n) | REFUTED AS FRAMED (Z1) | specialist |
| F | Blind, quantitative/analytic counting framing | NEVER RAN (session limit) | agent |
| G | Algebraic / polynomial method / slice rank / rank-4 matrices | UNSTARTED | specialist |
| H | Extremal constructor + relaxation barriers | **COMPLETE** — B6/B7/B8 proved | adversary |
| Q | Q4, then joint-direction hunt | **COMPLETE** — Q4 falsified, SQ discovered | agent |

**PRIOR-ART AUDIT UNSEALED 2026-08-17 — see `docs/prior_art_audit.md`.** Route SQ is
downgraded from LIVE to DEPRIORITIZED. Not because it was barriered (the barrier analysis
held up), but because `Q_SQ(n)` is the published quantity `F(n)` (isosceles-right-triangle-
free sets), whose best known upper bound is Bloom's `O(n²/(log n)^{1-ε})` — **weaker than
the baseline `n·r_3(n)` for the original problem.** The relaxation is therefore lossy: it
can only help after someone proves a power saving for `F(n)`, itself an open problem. The
campaign's tensor lemma is the mechanism of the published `Ω(n^{1.318})` construction
(arXiv:2607.22828, Gaussian base `51+51i`, carry-free digits, 281-digit AlphaEvolve
alphabet), and the campaign's `Ω(n^{1.1562})` is superseded. Surviving citable candidates:
`C(12) = 20` and Theorem 4. Neither is progress on the target.

Wave-3 note: the mandatory SURVIVAL RULE (write `report.md` in the first few tool calls,
append continuously) worked. Three of three wave-3 branches were again terminated by the
API session limit, but this time C, H and Q all left complete, self-describing reports on
disk and their results were recoverable in full. Waves 1 and 2, which lacked the rule, left
nothing. **Record this: the rule is the reason this campaign has results at all.**

Branches A,B,C,F,G,H,D,E are mutually blind (each instructed not to read sibling routes).
Recurrence information (route D) and boundary information (route E) are isolated to those
branches only. Root's own findings (R0, barriers) have NOT been broadcast to any branch.

---

## WAVE 1 STATUS — all eight branches terminated by session limit

None of the eight agents completed; all died mid-run at the API session limit. No branch
produced a `report.md`. Surviving on disk: partial code for C, D, E, G, H
(`routes/*/`, ~150KB total); routes A, B, F produced nothing. Wave 1 must be **relaunched**,
not resumed from summaries — the campaign's blindness requirement makes cold restarts
acceptable, and the surviving code (verifiers, exact solvers, search harnesses) is reusable
scaffolding that will make the relaunch cheaper.

**One claim arrived in a terminated agent's partial output and is NOT yet verified:**

> `C(12) = 20`, exhaustively (which would close the supplied interval `20 ≤ C(12) ≤ 23`).

Status: `CONJECTURE` / unverified third-party claim. The agent died before writing its
method or its exhaustiveness certificate to disk, and root has not reproduced it. It must be
independently re-derived before being recorded anywhere as a result. Do **not** propagate it
into other branches' baselines until then — a wrong "exact" value would poison every
downstream falsification test.

---

## WAVE 2 — relaunched, nine branches

Q (Q4 falsification, then joint-direction hunt) · A, B, F (blind structural) ·
C (computational lab; priority zero = certify C(12) independently) · D (recurrence) ·
E (boundary) · G (algebraic/polynomial) · H (extremal constructor).

A, B, F, C, D, E, G, H are blind to Q4, to the barrier taxonomy, and to each other:
each is forbidden `docs/`, `proofs/`, `ledgers/`, and sibling `routes/`. Only branch Q holds
the Q4 dossier. This preserves §4/§17 anti-colonisation.

## Q4 — `FALSIFIED` (root, wave 2)

`Q4(n) ≥ r_3(n)^4/(64n^2) = n^{2-o(1)}` via a four-fold intersection of shifted Behrend sets.
Killed within the falsification-first gate, before the proof effort it was meant to justify
was funded. Generalises to barrier **B4′** (see verified-results ledger). Branch Q redirected
to hunt for a joint-across-directions constraint violated by the explicit adversary set.
Details: `proofs/q4_falsified.md`, failure ledger F1.

---

## R0 — Root: bisector / line-kill mechanism

- **Mechanism.** RF1: the forbidden object is not a point but the whole perpendicular
  bisector of every pair. L1 characterises when that bisector carries lattice points
  (`g` even, or `d/g` both-odd). L2 turns this into: pairs on a common `e`-line kill an
  entire transversal `e^⊥`-line, everywhere in the grid.
- **Cross-line information?** YES — genuinely. A configuration inside one row forbids points
  in every other row. Passes the §8 critical test.
- **Strongest surviving claim.** `C(n) ≤ (3/4 + o(1))n^2` from the diagonal form;
  `≤ (1/2 + o(1))n^2` from the row/column form. Both are constant-factor results and are
  **far weaker than the sealed baseline** — recorded for the mechanism, not the bound.
- **Relation to the existing `n·r_3(n)` mechanism.** Strictly stronger as *information*
  (see B3 corollary), but every single-direction analysis collapses back to `#lines · r_3`,
  i.e. exactly the baseline.
- **Hardest remaining obligation.** Extract the multi-direction content non-additively.
  Summing over directions is capped at `1/log n` by the harmonic sum (barrier B4).
- **Status.** `BLOCKED` as a route to a power saving, with obstruction B4 stated precisely.
  `VERIFIED_LEMMA` for L1, L2, RF1–RF5.

### Key structural fact discovered at root (feeds later synthesis)

L2 ranging over *all* primitive directions is **equivalent to the full problem** (every pair
lies on a common `e`-line for `e = (c-a)/gcd`, and L2's killed set is exactly the lattice
points of the bisector). So the line-kill formulation loses no information. The failure is
therefore **not informational but methodological**: independent summation over directions is
the wrong extraction method. See `docs/barriers.md` B4.

### Barriers established at root (see `docs/barriers.md`)

- **B1** shell/distance-multiplicity counting caps at `n^2/sqrt(log n)` — rigorous for class.
- **B2** lattice-3-AP-freeness caps at `n^{2-o(1)}` via Behrend `B×B` — rigorous for class.
- **B3** axis line-kill (rows+columns, full strength) caps at `n^{2-o(1)}` via the *same*
  `B×B`, which satisfies **every** axis line-kill constraint (0 violations, verified at
  N=9,27,81) — rigorous for class. **Corollary: the diagonal / non-axis directions carry
  strictly more information** (520 violations at N=81). This is the sharpest positive
  pointer root produced.
- **B4** summed multi-direction line-kill caps at `n^2/log n` — heuristic saturation.
- **B5** iteration arithmetic: a power saving requires constant gain per *constant* scale
  ratio; gain per `n → n^{1/2}` yields polylog only — rigorous, constrains route D.
