# Session 7.3 — FAR-cascade campaign on the lower bound

A self-contained research campaign, separate from the `long_horizon_run_*` construction
work in this repository. Twelve rounds, then closed. **It did not prove a new bound on `C(n)`.** What it produced
is a diagnosis of why the natural route stalls, one removed obstacle, and a proof that the
remaining obligation does not decompose.

## Problem identity

Problem **59** of the AlphaEvolve Repository of Problems = **§6.39** of arXiv:2511.02864.
The label "6.59" used elsewhere in this repository is a conflation and finds nothing in
search. The continuous cousin is erdosproblems.com **#657**.

## What changed relative to the rest of the repository

The construction campaign chased `C(64) ≥ 113` and `C(100) ≥ 165` — i.e. the *upper* end of
what can be built by search. Round 1 here redirected to the **lower bound**: arXiv:2601.14465
(Jánosik et al.) shows the live question is whether `C(n) = Ω(n)`, states it is open,
conjectures it is true, and names the route without executing it:

> "most probably a linear lower bound can be achieved via the random independent set process."

Known state: `n/√(log n) ≲ C(n) ≲ exp(−c(log n)^{1/9})·n²`.

## The result, in one paragraph

The known lower bound `n/√(log n)` is exactly the alteration threshold `√(V/μ)`, where `μ`
is the size-biased mean multiplicity of a squared distance and `μ ≍ log n` in the grid.
Five unrelated-looking methods all stall at that same threshold for the same reason. But
the random greedy process itself, measured to `n = 8192`, is **linear** — it beats the
threshold by the missing factor. So the gap is in the analysis, not in the truth. Round 10
localised it: the two Bennett–Bohman hypotheses the isosceles hypergraph fails are stated
as **pointwise maxima over pairs** and consumed by the proof as **edge-weighted averages**,
and under that weighting the hypergraph satisfies both with polynomial room (`ε ≈ 0.26`).
Round 11 removed the third hypothesis, regularity, at a cost of `√1.470 = 1.21`. Round 12
then showed the remaining obligation does not split: `Δ₂`'s dominant role is identical to
`Γ`'s, and its one extra role — the Azuma step size — is not repairable by truncation,
because every vertex has `Θ(1)` partners at its maximum codegree and the process runs
`Θ(n)` steps in which all `N` vertices must survive.

## Read in this order

| file | what it is |
|---|---|
| `Human_Review/note.html` | the deliverable — self-contained write-up, open in a browser |
| `CAMPAIGN_STATE.md` | canonical state, top candidates, and the DO-NOT-REDO list |
| `docs/final_closeout.md` | the verdict; Chinese version at `docs/final_closeout.zh.md` |
| `docs/round1_findings.md` … `round12_findings.md` | one file per round |
| `checkpoints/checkpoint_latest.md` | resume state, exact next action |
| `ledgers/` | candidate bank, theorem registry, failure ledger |
| `experiments/` | every measurement, sources only |

Also published as a rendered page (private link, owner-controlled):
https://claude.ai/code/artifact/9320efc0-07a2-42d0-a2db-14cfeb3b1d0c

## Status of every claim

| claim | status |
|---|---|
| all-distances-distinct capped at `O(n/(log n)^{1/4})` | proved |
| parity separation; doubling recurrence `C(2n) ≥ 2·C_H(n)` | proved |
| degree-`k` route `< n` for every `k`, and worse than `n/√(log n)` | proved |
| mod-`p` reduction `C(p) ≥ A(p)` | proved |
| B6 is a two-sided obstruction (upper *and* lower bound) | proved |
| irregularity is removable at a cost of `√1.470` | proved, write-up incomplete |
| threshold `√(V/μ)` and its match to the known bound | heuristic + measured |
| `greedy/n →` a positive constant ≈ 0.72–0.84 | measured + model selection |
| `Γ ≍ D/log D`, `Δ₂ ≍ D^{1/2}/√(log D)`, `Γ_edge ≍ D^{0.60}`, `Δ₂_edge ≍ D^{0.24}` | measured |
| truncation of the Azuma step is viable only at `τ ≥ Δ₂max`, i.e. the original hypothesis | measured |
| Obligation R10 splits into an easier `Δ₂` half | **refuted** |
| **`C(n) = Ω(n)`** | **open — not proved, not falsified** |

Twelve rounds, twelve honest zeros on the bound. Judge PASS 0, Grade TYPE2 0.

## What is not here

`lit/` — the arXiv LaTeX sources of the papers being read — is deliberately excluded from
this repository; they are other people's papers. The round 10 and 11 findings cite
**arXiv:1308.3732** (Bennett–Bohman, *The random greedy independent set process*) by line
number in its arXiv source, retrievable with `arxiv.org/e-print/1308.3732`. Compiled
binaries (`*.exe`) are excluded; every experiment is a single self-contained C or Python
file with its build line in the header comment.

## Why it is closed

Round 12 attacked the last route and it did not close. What remains is a single
indivisible obligation:

> an argument tolerating a `Θ(1/n)` fraction of bad `(vertex, partner)` events across
> `Θ(n)` steps — which a pointwise stopping time forbids by construction.

That is a proof of Bennett–Bohman's theorem under averaged rather than pointwise
hypotheses: a research problem in probabilistic combinatorics, not a repair reachable by
any probe, sweep or synthetic hypergraph. The Round 11 checkpoint committed in advance to
stopping if this route failed, and it failed.

**Do not reopen this campaign to run more probes.** `CAMPAIGN_STATE.md` carries the
DO-NOT-REDO list, including several corrections of the campaign's own earlier claims. If
the remaining obligation is ever attacked, the entry points in the Bennett–Bohman source
are lines 720 (the stopping time), 782 and 849 (the two base cases), 1015–1029 (the drift
consumer) and 1172 (the step size).
