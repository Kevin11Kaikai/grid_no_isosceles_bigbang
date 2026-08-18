# Erdős Problem 6.59 — campaign record

`C(n) = max |S|`, `S ⊆ {0,…,n−1}²`, with no three distinct `a,b,c ∈ S` satisfying
`d(a,b) = d(b,c)` (squared Euclidean distance; degenerate/collinear triples included).

**Target pursued: `C(n) = O(n^{2−ε})` for a fixed `ε > 0`.**

---

## Outcome, stated once and plainly

**The target was not reached. The campaign did not move the problem.** The known bounds
are where they were:

```
    n/√(log n)  ≲  C(n)  ≲  e^{−c (log n)^{1/9}} · n²
```

The prior-art audit found that the campaign's principal mathematical results had all been
obtained before, in some cases by the same route. **The count of novel contributions is
zero.** The last candidate, the exact value `C(12) = 20`, was itself found to be known —
PatternBoost ([arXiv:2411.00566](https://arxiv.org/abs/2411.00566)) proved optimality by SAT
for all `n ≲ 32` in 2024 and plots `f(12) = 20`; the audit had missed it by searching printed
numbers instead of reading the figure (**F7**). What remains at `n = 12` is an independent
reproduction by a different method, which is verification and not discovery.

This archive is kept because the *negative* record — what was ruled out, what was falsified
and how — held up against the literature, and because the process findings are reusable.
F7 is the one to read first: it is the failure that cost the most and was the cheapest to
have avoided.

---

## Reading order

1. **`docs/prior_art_audit.md`** — start here. Assessed novelty for every substantive
   result. Supersedes parts of the closeout.
2. **`docs/session6_final_closeout.md`** — the discovery-phase record, preserved unedited
   under a banner marking the three conclusions the audit overturned.
3. **`ledgers/failure_ledger.md`** — the most reusable document in the archive: six
   falsifications and process failures with their causes, including three that were caught
   only by cross-checking against the complete definition.
4. **`proofs/`** — the mathematics, with evidence levels attached.
5. **`submission/`** — the `C(12) = 20` certificate package, self-contained.

---

## What is established, by evidence level

**Proved and machine-verified.**

| result | where |
|---|---|
| `C(12) = 20`, exhaustive, no symmetry argument used, two independent solvers — **known already**, see F7; retained as independent reproduction | `submission/` |
| B4′ — every bounded-direction line-kill relaxation admits `n^{2−o(1)}` | `proofs/q4_falsified.md` |
| B6 — the degree-`k` relaxation admits `n^{2−2/(k+1)−o(1)}`; hence any argument robust at degree 2 is capped at `n^{4/3}` | `routes/H/report.md` |
| `C(n²) ≥ C(n)²` is **false** (`C(16) = 28 < 36`) | `routes/H/report.md` |
| Theorem A — `Q_SQ(n) ≤ g(q)` for every `q ≥ 2n`, so torus upper bounds transfer to the box | `proofs/ideal_uniformity.md` |
| Theorem B — `G(I)` depends only on the `Z[i]`-module `Z[i]/I`; `m(p)` and `g(q)` are one function | `proofs/ideal_uniformity.md` |
| `Q_SQ(n) = n^{2λ+o(1)}` for `λ = limsup log G(I)/log N(I)`; the target is equivalent to `λ < 1` | `proofs/ideal_uniformity.md` |

**Falsified in-campaign, by explicit counterexample or exhaustive computation.**

| claim | how it died |
|---|---|
| Q4 (four-direction relaxation) is `O(n^{2−ε})` | four-fold intersection of shifted Behrend sets reaches `n^{2−o(1)}` (F1) |
| Route E's boundary induction | zero of the maximum sets at `n = 3,4,6` admit any single-cell extension, yet `C(n+1) > C(n)` (F2) |
| The finite-margin `(1+i)`-tower recurrence `c < 2` | exact ratio **equals 2** at two steps; `G((1+i)^j) = 1,2,2,4,6,9` (F5) |

**Known, per the audit — independently derived here, but not new.** The square-corner /
`Z[i]` single-equation formulation; the carry-free tensor lemma; Theorem 4 (the Behrend
digit-sphere obstruction). All appear in arXiv:2607.22828 (Károlyi–Solymosi), whose
`Ω(n^{1.318})` construction supersedes the campaign's `Ω(n^{1.1562})`. And the exact value
`C(12) = 20`, which appears in arXiv:2411.00566 (Charton–Ellenberg–Wagner–Williamson).

**Deprioritized.** Route SQ. The barrier analysis was correct — `Q_SQ` really is not capped
at `n^{2−o(1)}` — but `Q_SQ` is the published quantity `F(n)`, whose best known upper bound
is Bloom's `O(n²/(log n)^{1−ε})`, *weaker* than the baseline `n·r_3(n)`. The relaxation
loses more than it gains.

---

## Process findings that transfer

These are the parts worth carrying to another problem.

- **The survival rule.** Agents must write `report.md` within their first few tool calls
  and append continuously. Waves 1 and 2 lacked it and left nothing when they hit the
  session limit; wave 3 had it and all three branches' results were recovered in full from
  identical terminations. This rule is why the campaign has any results at all.
- **Hand-derived incremental filters are the dominant bug class** (F3). Three separate
  solvers each enumerated 4 of the 6 ways a pair extends to a forbidden triple. Every
  instance produced *plausible wrong numbers* rather than a crash, and one briefly appeared
  to refute a correct lemma. All three were caught the same way: re-testing against the
  complete definition with a checker sharing no code, tables or data structures.
- **Calibrate a new instrument on a known answer before recording its readings** (F4). The
  `(1+i)`-tower ratios looked like a comfortable margin until the same solver was run on
  3-term APs — a relation Behrend forces to die — and read `1.5` at the first step. The
  instrument was blind; the readings were struck.
- **Escaping one barrier construction is not escaping the barrier** (F1). Q4 was promoted
  on the strength of defeating `B × B`, and a different construction reached `n^{2−o(1)}`.
- **Figures are data, and a supplied baseline is a citation with its source stripped** (F7).
  The audit cleared `C(12) = 20` as new because no paper *printed* it; the paper that had it
  plotted it, alongside a sentence claiming proved optimality for the whole range. Worse, the
  campaign was handed exact values at `n = 16, 27, 32` in its sealed packet and never asked
  what source could possibly supply those and not `n = 12`. **Read the figures, and interrogate
  where your given numbers came from.**
- **Blind isolation has a shelf life** (F6). §3 forbade literature access, which guaranteed
  every correct discovery would be `NOVELTY_UNASSESSED`; on a problem worked by Wu,
  Ellenberg–Jain, Solymosi, Bloom, Shkredov and AlphaEvolve-scale search, the prior is that
  correct discoveries are already known. The protocol made independent rediscovery of known
  mathematics the default outcome. The signal that it had run its course was
  self-collision — the campaign deriving, as "independent corroboration", a restatement of
  something it already held.

---

## Contents

```
ARCHIVE.md      this index
docs/           prior_art_audit.md · session6_final_closeout.md · barriers.md · Q4_route.md
proofs/         ideal_uniformity.md · square_corner.md · q4_falsified.md
                root_reformulations.md
ledgers/        failure_ledger.md · approach_registry.md · verified_results.md
                proof_obligation_ledger.md
experiments/    root-level verification and falsification code
routes/         per-branch source and reports; C, H and Q carry report.md
submission/     the C(12) = 20 certificate package
```

No compiled binaries are included; all sources build with the commands given in the
documents that use them.
