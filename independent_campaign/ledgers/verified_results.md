# Verified Result Ledger

Evidence levels: VERIFIED_THEOREM | VERIFIED_LEMMA | VERIFIED_COMPUTATIONAL_RESULT |
EMPIRICAL_PATTERN | CONJECTURE | FALSIFIED | BLOCKED | KNOWN_BASELINE | NOVELTY_UNASSESSED

Novelty of everything below remains NOVELTY_UNASSESSED (isolation phase).

---

## Reformulations — `VERIFIED_LEMMA` (`proofs/root_reformulations.md`)

RF1 bisector · RF2 reflection · RF3 proper-edge-colouring · RF4 lattice-3-AP ·
RF5 paraboloid lifting.

## L1 — lattice points on a perpendicular bisector — `VERIFIED_LEMMA`

The bisector of `a,c` carries lattice points iff `g = gcd(d)` is even or `d/g` has both
coordinates odd. Exhaustively cross-checked against brute force: 0 discrepancies.

## L2 — multi-direction line-kill — `VERIFIED_LEMMA`

Pairs of `S` on a common `e`-line kill an entire transversal `e^⊥`-line. Genuine cross-line
information (passes the §8 critical test). Over all primitive directions it is *equivalent*
to the full problem, so the formulation is information-complete.

## Upper bounds actually proved at root — `VERIFIED_LEMMA` / `VERIFIED_COMPUTATIONAL_RESULT`

`C(n) ≤ (1/2 + o(1))n^2` (row/column form); `C(n) ≤ (3/4 + o(1))n^2` (diagonal form).
Both far weaker than the sealed baseline `n^2 exp(-c(log n)^{1/9})`. Recorded for mechanism,
not value.

## Barrier theorems — `VERIFIED_THEOREM` for their mechanism classes

- **B1** shell/distance-multiplicity counting caps at `n^2/√(log n)` (Landau–Ramanujan).
- **B2** lattice-3-AP-freeness caps at `n^{2-o(1)}` (Behrend `B×B`).
- **B3** axis line-kill (rows+columns, full strength) caps at `n^{2-o(1)}` (same `B×B`;
  0 violations verified at N=9,27,81).
- **B4′** *(supersedes the earlier heuristic B4)* **any line-kill relaxation using `O(1)`
  directions caps at `n^{2-o(1)}`**: `Q_k(n) ≳ n^2 exp(-Ck√(log n))`, so a power saving
  requires `k = Ω(√(log n))` directions. Proof in `proofs/q4_falsified.md`.
- **B5** iteration arithmetic: constant gain per *constant* scale ratio is required;
  gain per `n → n^{1/2}` yields polylog only.

## Z1 — The extremal interior is the wrong induction object — `VERIFIED_COMPUTATIONAL_RESULT`

Exhaustive enumeration of **all** maximum isosceles-free subsets of `[n]^2`, then of every
single-cell addition from the L-strip of `[n+1]^2` (`experiments/root_zero_extension.py`):

| n | C(n) | # optima | optima admitting ≥1 strip addition | C(n+1) |
|---|------|----------|-----------------------------------|--------|
| 3 | 4    | 12       | **0**                             | 6      |
| 4 | 6    | 4        | **0**                             | 7      |
| 5 | 7    | 48       | 6                                 | 9      |
| 6 | 9    | 16       | **0**                             | 10     |

For `n = 3, 4, 6`: **no** optimal `n×n` set extends into the strip at all, yet
`C(n+1) > C(n)`. So an optimal `(n+1)`-set never restricts to an optimal `n`-set at those
`n`; the optimum is reached only by *rearranging* the interior.

**Consequence (this is the point).** The naive boundary induction — "fix an extremal
interior, count addable strip cells" — does not merely lose constants. It measures a
quantity that can be **zero while the true increment is positive**, so it cannot bound
`C(n+1) - C(n)` from above *or* below. Any boundary argument must either quantify over all
*near*-extremal interiors (not just extremal ones), or abandon the interior/strip split.
Route E's original framing is refuted as stated; its brief already flagged this as the most
likely way the route produces a false theorem, and it did.

Independently re-derives `C(3)=4, C(4)=6, C(5)=7, C(6)=9`, all matching the sealed values.

Originated as a partial observation from the terminated route-E branch; re-derived from
scratch at root before being recorded.

## C(12) = 20 — `VERIFIED_COMPUTATIONAL_RESULT` (closes the supplied bracket)

Route C, `routes/C/report.md`. Two complete searches, the decisive one **with symmetry
reduction disabled** so the certificate does not depend on any symmetry argument:

| run | symmetry | start `best` | result | nodes |
|-----|----------|--------------|--------|-------|
| A-scratch | D4 root reduction | 0 | OPT 20 | 27 686 483 095 |
| A-nosym | **none** | 20 | no 21-point set exists | 45 922 791 007 |

Lower bound: three distinct 20-point witnesses, all passing an independent naive
triple-loop verifier. The supplied bracket was `20 ≤ C(12) ≤ 23`; the answer sits at the
bottom. The same solver independently re-derives `C(1..11) = 1,2,4,6,7,9,10,13,16,18,18`
(no disagreement) and reproduces `C(1,n) = r_3(n)` as the exact Salem–Spencer sequence for
`n ≤ 34` — an external calibration of its notion of "isosceles" and of its enumeration.
Also exhaustive: **all** maximum sets for `n = 8,9,10` (48, 4, 8 sets; unique up to `D4`
at `n = 9` and `n = 10`).

## Further barrier theorems (route H, `routes/H/report.md`) — `VERIFIED_THEOREM` for their classes

- **B6 — degree relaxation. THE STRONGEST BARRIER FOUND.** Replace "at most 1 point of `S`
  at each squared distance from each apex" by "at most `k`". Then for every fixed `k` there
  are sets of size `n^{2 - 2/(k+1) - o(1)}` (alteration on the moment sums
  `M_j(R) = Σ_{r≤R} r_2(r)^j`, using `r_2(r) ≤ d(r) = r^{o(1)}`). So `k=2` already admits
  `n^{4/3-o(1)}`.
  **Consequence: any argument that survives replacing 1 by 2 in the degree bound cannot
  prove better than `O(n^{4/3})`** — that includes essentially every counting, energy,
  `L^2`, Fourier or regularity argument that loses a constant factor when a radius class
  has two points instead of one. A proof of `n^{1+o(1)}` must be exactly tight at degree 1.
  Numerically confirmed: `M_j/(R log^{2^{j-1}-1} R)` converges for `j = 1,2,3,4`.
- **B7 — scale calibration.** Imposing the condition only for squared distances `r ≤ R`
  still admits `n^2/(2√(2R log R))` points, and the truncated problem is *exactly* the full
  problem on an `M × M` torus with `M ~ 2√R`. So an argument using only distances of length
  `≤ L` cannot prove better than `~n^2/L`: reaching `O(n^{1.5})` needs scale `n^{0.5}`,
  reaching `O(n^{1+ε})` needs essentially the full diameter. The difficulty is spread
  evenly over all dyadic scales — there is no hardest scale. Calibration check: at
  `R = 2n^2` the bound reproduces the known `Ω(n/√log n)`.
- **B8 — bounded apex sets.** Imposing distinctness only at `k` apexes admits
  `n^2/(k·n^{o(1)})` points for any `k = n^{o(1)}`. Exact for `k=1`
  (`Θ(n^2/√log n)`, Landau–Ramanujan) and `k=2` (bipartite matching). So "pick a few
  special points of `S` and count their distances" is provably insufficient; the condition
  must be used at essentially all points simultaneously.
- Route H independently re-derived B2/B3 (barriers for "each axis line 3-AP-free", "no 3-AP
  in `Z^2`", "corner-free" — all `n^{2-o(1)}`), and established that **no naive product/lift
  construction exists**: `C(16) = 28 < 36 = C(4)^2`, so `C(n^2) ≥ C(n)^2` is false.
- Route H's quadrant stress test found a *rigorous* ceiling (from the supplied exact values
  alone) of 50–57% simultaneous quadrant occupancy, with `C(2n)/C(n)` ratios of 2.0–2.6,
  never approaching 4. `EMPIRICAL_PATTERN` at small `n`; note the naive quadrant relaxation
  gives exactly `C(2n) ≤ 4C(n)` and nothing better, so any recurrence proof must use
  cross-quadrant triples.

## SQ — the square-corner relaxation — route SURVIVES the falsification gate

Full statements and proofs: `proofs/square_corner.md`. A *square corner* is
`{b, b+w, b+i·w}` with `i·(w1,w2) = (-w2,w1)`; `Q_SQ(n)` is the max square-corner-free
subset of `[n]^2`, and `C(n) ≤ Q_SQ(n)` because `|w| = |i·w|`.

- **Single invariant equation** — `VERIFIED_LEMMA`. Square-corner-freeness is avoidance of
  `v = i·u + (1-i)·b` over `Z[i]`, coefficients `(1,-i,i-1)` summing to 0: one
  translation-invariant three-variable equation. Corners provably admit no such relation,
  so this is a complexity-1 (Roth-type) condition where corners is complexity 2.
- **Circle rigidity** — `VERIFIED_LEMMA`. On any lattice circle the only square corners are
  `(b, i·b, -i·b)`. Exhaustive for `R ≤ 6000`: 18852 corners found, 18852 of that form,
  **0** others.
- **Behrend-sphere obstruction (Theorem 4)** — `VERIFIED_THEOREM` for its class. The
  digit-sphere method — the single method producing *every* `n^{2-o(1)}` barrier set in this
  campaign (B2, B3, B4′) — provably never yields a square-corner-free set, because the
  per-digit triple `(b_j, i·b_j, -i·b_j)` satisfies the equation digitwise and preserves any
  direct-sum quadratic form. **This is the campaign's first genuine barrier escape**, and it
  defeats the construction *method*, not merely one instance (contrast failure F1).
- **Tensor lemma** — `VERIFIED_LEMMA`. With `g(q)` = the max on the torus `(Z_q)^2`,
  `Q_SQ(n) = Ω(n^{log g(q)/log q})` for every `q`, with no carry conditions needed. The
  problem is exactly self-similar under scaling, so it suffices to bound `g`.
- **`g(q)` exact for `q ≤ 11`** — `VERIFIED_COMPUTATIONAL_RESULT`:
  `2,3,4,5,6,8,9,11,12,16`. Every value cross-checked with symmetry reduction disabled;
  every witness re-verified by an independently written checker. Hence
  **`Q_SQ(n) = Ω(n^{1.1562})`** — square-corner-free sets are provably superlinear, so the
  relaxation cannot prove `C(n) = O(n^{1.15})`. Harmless: the target is `O(n^{2-ε})`.
- **Product lemma** — `VERIFIED_LEMMA`. For `p ≡ 1 mod 4`, `g(p) ≥ m_A(p)·m_B(p)` where `m`
  counts subsets of `F_p` avoiding the twisted 3-AP `{y, y+d, y+kd}`, `k^2 = -1`.
- **Falsification test result** — `EMPIRICAL_PATTERN`. `m(p) = p^{0.547 ± 0.005}`, flat
  across `p` from 37 to 8009 and not drifting up; exhaustive values agree with the search
  *exactly* wherever both were computed (`p ≤ 41`). So the product construction reaches only
  `~p^{1.10}`, not `p^{2-o(1)}`. Since a *lower* bound on `m` is what would kill the route,
  search is legitimate evidence here — the asymmetry runs the opposite way to Q4.

**Status: the only surviving route.** Remaining obligation, and it is the whole of it:
prove `Q_SQ(n) = O(n^{2-ε})`. What is known about the target is now sharp:
`n^{1.1562} ≤ Q_SQ(n) ≤ o(n^2)`.

## Q4 — `FALSIFIED`

`Q4(n) ≥ r_3(n)^4/(64 n^2) = n^{2-o(1)}`. See `proofs/q4_falsified.md` and failure ledger F1.

---

## Standing negative result

**No fixed polynomial saving has been proved.** The strongest upper bound established in
this campaign is `(1/2+o(1))n^2`, weaker than the sealed baseline. Every mechanism examined
is capped at `n^{2-o(1)}` or worse by one of B1–B8, **with exactly one exception: SQ, the
square-corner relaxation.** For SQ the cap is not merely unproved — the method that produces
every one of those barrier constructions is *proved* not to produce square-corner-free sets
(Theorem 4). SQ is therefore the campaign's one live route, and it carries a single, fully
explicit remaining obligation: `Q_SQ(n) = O(n^{2-ε})`.

This does not make SQ a proof, and it is not evidence that a power saving is provable. It
means the construction-side obstruction that killed every earlier mechanism is absent here.

## The design requirement every surviving route must now meet

The B4′ barrier construction uses only "each projection `φ_i(S)` lies in a 3-AP-free set".
**Any mechanism whose consequences follow from that statement is dead.** A live mechanism
must impose a constraint *jointly* across directions — one violated by
`S = ∩_i φ_i^{-1}(W_i)` even when every `W_i` is 3-AP-free.

**SQ meets it, and the witness is explicit.** Route Q built a member of the B4′ barrier
family at `n = 200` — `A,B,W,Z` all 3-AP-free, all four line-kill constraints satisfied —
whose *only* isosceles triple is a single square corner: apex `(66,66)`, legs to `(63,68)`
and `(68,69)`, `w = (2,3)`, squared leg length 13 (`routes/Q/certificate.py`,
`certificate_n200.npz`). The minimal possible counterexample is realised: the square corner
is the first thing the barrier family misses. Route Q also proved *why* no bounded direction
set can recover it — each direction `e` kills the square corners of at most 3 lines' worth
of `w`, so `k` directions leave a `1 - O(k/R)` fraction of rotation classes unconstrained
(measured decay exactly `1/R`), meaning `k = Θ(n)` directions would be needed.
