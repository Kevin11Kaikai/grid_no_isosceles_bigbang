# Failure / Counterexample Ledger

Per dead claim: exact statement | counterexample | failed step | hidden assumption |
kills lemma or mechanism | what the failure reveals | next route to spawn.

---

## F1 — Q4 (four-direction line-kill relaxation) — `FALSIFIED`

**Exact statement killed.** "`Q4(n) = O(n^{2-ε})` for some fixed `ε>0`", and with it the
plan to prove `C(n) = O(n^{2-ε})` via `C(n) ≤ Q4(n)`.

**Counterexample.** For 3-AP-free `A,B,W,Z`, the set
`S = {(x,y) : x ∈ A, y ∈ B, x+y ∈ W, x-y ∈ Z}` satisfies all four Q4 constraints
(Sufficiency Lemma, proved; 143 instances machine-checked, 0 violations). Averaging over
shifts of Behrend sets yields `Q4(n) ≥ r_3(n)^4/(64n^2) = n^{2-o(1)}`. Full proof in
`proofs/q4_falsified.md`.

**Failed step.** None — Q4 was never proved small. The error was *promotion*: Q4 was labelled
PROMISING on the strength of defeating one barrier construction (`B × B`).

**Hidden assumption exposed.** "Mechanism M defeats the known barrier construction" was
implicitly treated as "M has no barrier construction". False. `B × B` fails Q4's diagonal
constraint at every diagonal pair — that part was correct and remains true — but a
*different*, four-fold-intersection construction satisfies all four constraints at
`n^{2-o(1)}`. Escaping one construction is not escaping the barrier.

**Also exposed: greedy search misled.** Greedy random-restart on Q4 gave ~1.8n with slopes
≈1.0 across n=8..96, which looked like strong evidence Q4 was near-linear. It was worthless:
the true value is `n^{2-o(1)}`, and greedy could never find an algebraically structured set.
This was flagged as a caveat when the data was recorded, and the caveat was correct.
**Lesson: heuristic search lower bounds must never raise a route's status.**

**Scope of the kill.** Kills the *whole mechanism*, not just a lemma — and by the
generalisation below, kills every bounded-direction version of it, not only `k = 4`.

**What the failure reveals (the valuable part).** The same averaging works for any `k`
directions, giving `Q_k(n) ≳ n^2 exp(-Ck√(log n))`. Therefore:

- **No relaxation using `O(1)` directions of the line-kill mechanism can give a power
  saving.** A working mechanism needs `k = Ω(√(log n))` directions coupled simultaneously.
- More sharply: the barrier construction uses *only* the statement "each projection
  `φ_i(S)` lies in a 3-AP-free set". **Any mechanism whose consequences follow from that
  statement is dead for every `k`.** A live mechanism must impose a genuinely *joint*
  constraint across directions — one violated by `S = ∩_i φ_i^{-1}(W_i)` even when every
  `W_i` is 3-AP-free.

This supersedes the heuristic barrier B4 with a rigorous theorem (B4′) and converts it into
a concrete design requirement for every surviving route.

**Next routes to spawn.** (i) A branch hunting for a joint-across-directions constraint that
the four-fold intersection construction violates — the explicit target is now known, which
makes this far more tractable than an open-ended search. (ii) Re-audit every other route
against B4′: any route reducible to per-projection 3-AP-freeness is dead on arrival and
should be marked BLOCKED without further spend.

**Outcome of (i): SUCCEEDED.** Route Q found the square-corner constraint and built the
explicit certificate at `n = 200` — a member of this very barrier family whose only isosceles
triple is one square corner. See `proofs/square_corner.md`. This is the only place in the
campaign where a falsification produced a live successor route.

---

## F2 — Route E's boundary induction — refuted as framed (Z1)

**Exact statement killed.** "Bound `C(n+1) - C(n)` by fixing an extremal `n×n` interior and
counting addable strip cells."

**Counterexample.** Exhaustive enumeration of all maximum sets: for `n = 3,4,6`, **zero** of
them admit any single-cell addition from the `(n+1)`-strip, yet `C(n+1) > C(n)` in each case
(`experiments/root_zero_extension.py`).

**What the failure reveals.** The quantity the induction measures can be zero while the true
increment is positive, so it bounds the increment neither above nor below. Any boundary
argument must quantify over all *near*-extremal interiors, or abandon the interior/strip
split entirely. The route's own brief had flagged this as its most likely way to produce a
false theorem, and it did.

---

## F3 — Recurring methodological failure: hand-derived incremental filters

**Not a route, a bug class — the dominant one in this campaign, and it recurred three times
after being "learned".**

| where | omission | symptom |
|---|---|---|
| Q4 averaging identity | one of four shift ranges truncated (`z` needed `-(3n-2)`) | predicted 10000, got 9200 |
| torus solver (C) | listed 4 of the 6 ways a pair extends to a forbidden triple | invalid `g(q)` witnesses, `g(6)=8` instead of 6 |
| exact twisted-AP solver | same 6-case omission | `m(5) = 3`, using `{0,1,3}` — 3-AP-free over `Z` but **not** mod 5 |

Every instance produced *plausible* wrong numbers rather than crashes, and one of them
(`m(5)=3`) briefly appeared to refute a correct lemma, which would have killed the surviving
route on false evidence.

**Every instance was caught the same way:** re-testing against the complete definition with
an independently written checker that shares no code, no tables and no data structures with
the thing being tested.

**Rule.** A hand-derived incremental filter is never permitted to be the only test of a
claim. Cross-check against the full definition, and when a computation contradicts a proved
lemma, suspect the computation's *inputs* first — F2's mirror image is that a wrong input
looks exactly like a wrong lemma.

---

## F4 — Small-scale tower ratios are an uninformative instrument — `INSTRUMENT RETIRED`

**What was being measured.** `G(I·(1+i)) / G(I)` on the `(1+i)`-adic tower of `Z[i]`. A
bound `c < 2` would prove `C(n) = O(n^{2-ε})` (Theorem A + tower arithmetic,
`proofs/ideal_uniformity.md` §5). Measured ratios: exact `2.00, 1.00, 2.00, 1.50, 1.50`
for `j ≤ 6`, then greedy `1.31–1.78` hovering near `1.45` out to `j = 13`. Against a budget
of `2`, that reads like a comfortable factor-of-1.4 margin.

**Calibration that destroyed it.** `experiments/tower_control.py` runs the *same solver* on
3-term APs, a relation whose fate is known: Behrend gives 3-AP-free sets of size
`N^{1-o(1)}`, so its local exponent **must** tend to `1` and its ratio **must** creep to the
full budget. Measured:

| tower | index | ratios | `λ_local` | true limit |
|---|---|---|---|---|
| `Z/2^m`, 3-APs | 2 | 1.5000, 1.3333, 2.0000 | 0.585, 0.415, 1.000 | 1 |
| `Z/3^m`, 3-APs | 3 | 2, 2, 2 | 0.6309 throughout | 1 |

A relation that **must die** reads `1.5` at its first index-2 step and a flat `0.63` across
the whole index-3 tower. The creep in the 3-AP case is only `exp(-c√log N)`, which at
`N ≤ 8192` is a factor of order one and invisible.

**Verdict.** Small-scale tower ratios cannot distinguish a surviving relation from a dying
one. The `(1+i)` ratio data is recorded as **UNINFORMATIVE**, never as support for route SQ.

**Why this is F1 again, and worse.** F1's lesson was "heuristic search lower bounds must
never raise a route's status." This instrument was built *after* that lesson and still had
to be killed by calibration rather than by foresight. **New rule: any new numerical
instrument must be run on a relation with a known answer before its readings on the open
problem are recorded at all.**

---

## F5 — Finite-margin form of the `(1+i)`-tower recurrence — `FALSIFIED`

**Exact statement killed.** "`G(I·(1+i)) ≤ c·G(I)` with `c < 2` at every step of the tower",
the finite-margin recurrence that would have delivered `C(n) = O(n^{2-ε})` from a single
constant.

**Counterexample.** Exhaustive computation: `G((1+i)^j) = 1, 2, 2, 4, 6, 9` for `j = 1..6`.
The ratio is **exactly 2** at `j = 1→2` and at `j = 3→4`. The exponent implied by the exact
data is therefore `2·log₂2 = 2.0000` — no saving whatsoever. (Solver revalidated against
every known `g(q)`, `q ≤ 8`; all witnesses re-verified by a definition-only checker.)

**What survives.** Theorem A (`Q_SQ(n) ≤ g(q)` for `q ≥ 2n`) and the tower arithmetic are
proved and stand. They give `Q_SQ(n) = n^{2λ+o(1)}` with `λ = limsup log G(I)/log N(I)`, so
the target is *equivalent* to `λ < 1`.

**What the failure reveals.** Retreating from "every step" to "`limsup` of steps" turns the
statement into `λ < 1`, which is the target itself. So the tower is a **restatement**, not a
reduction. §8 audit verdict recorded: A NEW FORMULA IS NOT A NEW MECHANISM. Two hours of
apparent breakthrough produced clarity (the box↔torus loop closes; one number `λ` decides
the route) and zero progress on the bound. Both halves are recorded.

---

## F6 — Blind mode has begun colliding with itself — `PROCESS FINDING`

Theorem B of `proofs/ideal_uniformity.md` proves that the `m(p)` ladder and the `g(q)`
ladder are the same problem on two different ideals. But the campaign already held the
split/inert reduction that implies this. So an instrument recorded in the closeout as
*independent corroboration* was a restatement of one the campaign had already derived, and
root spent part of a session discovering that its own two witnesses were one witness.

Under §3 HARD ISOLATION every result is `NOVELTY_UNASSESSED`, so this kind of collision is
invisible until it is stumbled over. Self-collision is the signature of an exhausted blind
phase: the marginal value of further blind generation is now low, and the ordered prior-art
checklist in `docs/session6_final_closeout.md` §8 should be executed before more theorem
effort is funded. **This is a recommendation to the user, not a decision — unsealing changes
the campaign's rules and requires network access, so it is theirs to make.**
