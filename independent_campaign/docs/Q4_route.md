# Route Q4 — the four-direction line-kill relaxation

> ## STATUS: `FALSIFIED` — see `proofs/q4_falsified.md`
>
> `Q4(n) ≥ r_3(n)^4/(64 n^2) = n^{2-o(1)}`, by a four-fold intersection of shifted Behrend
> sets. No power saving can come from Q4. **Everything below was written before the
> falsification and is retained only as the record of how the route was promoted and why
> that promotion was wrong.** The "escapes barrier B3" argument in it is correct but
> insufficient: defeating one barrier construction is not defeating the barrier.

Root-derived route. Status when written: `PROMISING`. Novelty: NOVELTY_UNASSESSED.

## The relaxation

`S ⊆ {0,...,n-1}^2`. Write `U_col, U_row, U_dia, U_ant` for the occupied columns, rows,
diagonals (`x-y`), anti-diagonals (`x+y`). Let `M(A)` = same-parity midpoints of distinct
pairs of `A`. Constraints:

1. every row `y`:          `M(X_y) ∩ U_col = ∅`   (`X_y` = x-coords in row `y`)
2. every column `x`:       `M(Y_x) ∩ U_row = ∅`
3. every diagonal `d`:     `M(A_d) ∩ U_ant = ∅`   (`A_d` = the `x+y` values on diagonal `d`;
                                                   same parity automatically, no parity loss)
4. every anti-diagonal `a`:`M(D_a) ∩ U_dia = ∅`

Define `Q4(n)` = max `|S|` subject to 1–4.

## Why it matters

- **Sound.** Each constraint is an instance of L2b (`proofs/root_reformulations.md`), hence
  implied by isosceles-freeness. So `C(n) ≤ Q4(n)`, and *any* upper bound on `Q4` transfers
  directly. `VERIFIED_COMPUTATIONAL_RESULT`: 125 independently generated and exactly verified
  isosceles-free sets (n = 8,12,16,24,32) all satisfy Q4 — **0 violations**
  (`experiments/q4_soundness.py`).
- **Purely combinatorial.** All geometry has been discharged; Q4 is a statement about four
  interlocking midpoint/occupancy systems on intervals. Far more tractable than the original.
- **It escapes barrier B3.** The Behrend product `B × B` satisfies constraints 1–2 exactly
  (0 violations at N=9,27,81) and has size `n^{2-o(1)}` — that is barrier B3. But `B × B`
  violates constraint 3 *maximally*: for any diagonal `d`, the points are `x ∈ B ∩ (B+d)`
  with anti-diagonal values `2x-d`, and a pair `x,x'` kills anti-diagonal `x+x'-d = x'+y`
  where `y = x-d ∈ B` — which is always in `B+B`, the occupied set. So **every** diagonal
  pair of `B × B` violates constraint 3. `VERIFIED_LEMMA` + confirmed computationally
  (520 violations at N=81). The B3 barrier construction is therefore *specifically* defeated
  by the diagonal directions, exactly as the B3 corollary predicted.

## Evidence on the size of Q4(n)

Random-restart greedy maximal Q4-feasible sets (`experiments/four_direction_linekill.py`,
40 restarts, independently re-verified in `O(|S|^2)`):

| n | 8 | 12 | 16 | 24 | 32 | 48 | 64 | 96 |
|---|---|----|----|----|----|----|----|----|
| best | 16 | 21 | 28 | 41 | 60 | 88 | 116 | 184 |
| best/n | 2.00 | 1.75 | 1.75 | 1.71 | 1.88 | 1.83 | 1.81 | 1.92 |

Successive log-log slopes: 0.67, 1.00, 0.94, 1.32, 0.95, 0.96, 1.14 — i.e. **linear growth**,
`≈ 1.8n`, over the whole range. `EMPIRICAL_PATTERN` only.

Two structural facts consistent with linearity, both `VERIFIED_LEMMA`:
- **Graphs of functions cap at 2n.** If every column is occupied then `U_col` is everything,
  so constraint 1 forces `M(X_y) = ∅` for every row, i.e. no two same-parity elements per
  row, i.e. `|X_y| ≤ 2`. Hence `|S| ≤ 2n`.
- **A single row achieves `r_3(n) = n^{1-o(1)}`**, with constraints 2–4 vacuous.

## The honest caveat

Greedy random-order search is a **weak lower bound** and is exactly the method that would
fail to find an algebraically structured extremal set — it would never have found `B × B`
either. So the linear data is suggestive, NOT evidence that `Q4(n)` is small. The two open
questions, in priority order:

1. **(Falsification first.)** Does there exist an algebraic construction of Q4-feasible sets
   of size `n^{2-o(1)}`, or even `n^{1+c}`? If yes, Q4 is barriered like B2/B3 and dies. This
   must be attacked before any proof effort.
2. **(The prize.)** Prove `Q4(n) = O(n^{2-ε})`. This would immediately give
   `C(n) = O(n^{2-ε})` — the campaign's primary target.

## Proof-obligation ledger for Q4

- **Proved:** soundness (`C(n) ≤ Q4(n)`); `B × B` fails constraint 3 maximally; the `2n` cap
  for full-column-support sets; `Q4(n) ≥ r_3(n)`.
- **Computational:** the greedy growth table; 125-set soundness check; `B×B` violation counts.
- **Conjectural:** `Q4(n) = n^{1+o(1)}`, or even `Q4(n) = O(n^{2-ε})`. Unproved.
- **Hardest remaining lemma:** an upper bound on `Q4` better than `n^{2-o(1)}`. Constraints
  1–2 alone provably cannot give it (barrier B3). So any proof must use constraint 3 or 4
  *jointly* with 1 or 2 — the joint use is the entire difficulty and is not yet reduced.
- **Why it may be genuinely easier than the original target:** the geometry is gone, the
  object is four midpoint systems on intervals, and the known barrier construction for the
  axis-only version is explicitly defeated. That is a real reduction in difficulty, not a
  restatement. But it is **not** yet a proof, and Q4 could still be barriered by an algebraic
  construction not yet found — see open question 1.
