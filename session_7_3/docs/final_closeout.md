# Final closeout — Session 7.3, twelve rounds

## Executive verdict

**No new bound on `C(n)`. Twelve rounds, twelve honest zeros. Judge PASS 0, Grade TYPE2 0.**

The campaign produced a diagnosis, not a theorem: it identified *why* the natural route to
`C(n) = Ω(n)` stalls, removed one of the three obstacles, and then showed that the remaining
obligation does not decompose. It is closing because the last route it had is now closed,
not because a budget expired.

## FAR cascade statistics

12 rounds · candidate families probed: probabilistic, recursive/dilation, arithmetic
quotient, bounded-degree, decomposition, hypergraph-independence · COMPLETE claims 0 ·
Judge PASS 0 · TYPE2 0 · TYPE3 0 · deep attacks 1 (Obligation R10, refuted as separable).

## What is proved

| result | round |
|---|---|
| all-distances-distinct is capped at `O(n/(log n)^{1/4})` | 2 |
| parity separation; the doubling recurrence `C(2n) ≥ 2·C_H(n)` (and its self-kill, `ρ → 1/√3`) | 4 |
| the degree-`k` ground-set route is `< n` for every `k`, and worse than `n/√(log n)` | 3 |
| B6 is a **two-sided** obstruction — it blocks the lower bound as well as the upper | 3 |
| the mod-`p` reduction `C(p) ≥ A(p)`, and `A(p) = Θ(√p)` capping the route at `2.7√p` | 5 |
| every edge of `H_n` has a unique apex | 11 |
| irregularity is removable: upward regularisation costs `√1.470 = 1.21` (write-up incomplete) | 11 |

## What is measured

The `√(V/μ)` threshold and its exact match to the known bound (2, 5) · `greedy/n →` a
positive constant ≈ 0.72–0.84, out-of-sample validated, power-of-log models excluded (6, 7)
· `Γ ≍ D/log D`, `Δ₂ ≍ D^{1/2}/√(log D)`, `D = 1.75 n² ln n` (6, 7, 11) · the `Γ`-bad set is
a `Θ(1/n)` fraction, forced by `Σ_{v'} Γ(v,v') ≤ D(Δ₂−1)` (8, 9) · `Γ` isolated has no
effect on the process, matched control (9) · `Γ_edge ≍ D^{0.60}`, `Δ₂_edge ≍ D^{0.24}` (10)
· the codegree tail and the failure of truncation (12).

## The barrier map

Every route the campaign examined loses the same logarithm, traceable to
`Σ_{d≤X} r₂(d)² ≍ X log X`. Round 10 relocated it: the two Bennett–Bohman hypotheses that
`H_n` fails are stated as **pointwise maxima over pairs** and consumed by the proof as
**edge-weighted averages**, under which `H_n` satisfies both with `ε ≈ 0.26`. What blocks
the substitution is the stopping time (`lit/ind.tex` line 720), which halts on the first
pair to breach its bound.

Round 12 closed the last route by showing the obligation does not split. `Δ₂`'s dominant
role is identical to `Γ`'s; its one extra role, the Azuma step size at line 1172, is not
repairable by truncation — the only viable truncation level is `Δ₂max` itself, because each
vertex has `Θ(1)` partners exactly at its maximum codegree and the process runs `Θ(n)`
steps in which all `N` vertices must survive. Without truncation the Freedman exponent is
short of `log N` by a flat factor ≈ 8 across `n = 32…192`.

## The single remaining obligation

> An argument that tolerates a `Θ(1/n)` fraction of bad `(vertex, partner)` events across
> `Θ(n)` steps — which a pointwise stopping time forbids by construction.

This is a research problem in probabilistic combinatorics: a proof of Bennett–Bohman's
theorem under averaged rather than pointwise hypotheses. It is not reachable by any probe,
sweep, or synthetic hypergraph, and nothing in this campaign bears on it.

## Novelty

`NOVELTY_PRELIMINARY` throughout. Nothing here is a theorem about `C(n)`. The Round 10
observation is a reading of a published proof (arXiv:1308.3732); whether it has been made
before was not searched. The regularisation device of Round 11 is standard — only its
verification for this hypergraph is the campaign's.

## Deliverable

`Human_Review/note.html` — *"The √log n gap is in the analysis, not in the truth"*.
Published at https://claude.ai/code/artifact/9320efc0-07a2-42d0-a2db-14cfeb3b1d0c and
mirrored in the repository at `session_7_3/`.

Tier B. It is a working note, not a paper, and no amount of further rounds would have made
it one.

## Resume instructions

Do not reopen this campaign to run more probes. The DO-NOT-REDO list in `CAMPAIGN_STATE.md`
records twenty-odd routes, measurements and mistakes that must not be repeated, including
several corrections of the campaign's own earlier claims. If the remaining obligation is
ever attacked, the entry point is `lit/ind.tex` lines 720 (stopping time), 782 and 849
(the two base cases), 1015–1029 (the drift consumer) and 1172 (the step size).
