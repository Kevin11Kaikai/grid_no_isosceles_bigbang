# Record Registry — Problem 6.59 (Isosceles-Triangle-Free Grid Subsets)

Literature/priority audit date: **2026-08-11**. Search scope: arXiv (via WebSearch),
the official AlphaEvolve problem repository's git commit history (via GitHub API),
and the source paper itself. This is a single-session, non-exhaustive audit — see
caveats at the bottom.

## Canonical source

- Georgiev, Gómez-Serrano, Tao, Wagner. *Mathematical Exploration and Discovery at
  Scale*. arXiv:2511.02864. Problem 6.59.
- Official repository: github.com/google-deepmind/alphaevolve_repository_of_problems,
  path `experiments/subsets_of_the_grid_with_no_isosceles_triangles/`.
- WebSearch summary of the paper's own account (not independently verified beyond
  what's quoted here): the pre-AlphaEvolve best known construction on the 64×64 grid
  had **110** points; it was conjectured 112 might be achievable but unfound "despite
  many months of attempts" until AlphaEvolve (given a hint about approximate 4-fold
  symmetry and edge-concentration) found the 112-point configuration. The paper also
  states asymptotic bounds n/√(log n) ≲ C(n) ≲ e^(−c·(log n)^(1/9))·n² for a constant
  c > 0 (general n, not specific to n=64/100).

## Registry entries

| n | Construction size | Source | Repo/pub date | Coordinates available | Independently verified (this project) | Comparison with our result | Notes |
|---|---|---|---|---|---|---|---|
| 64 | 112 | AlphaEvolve repo (arXiv:2511.02864, Problem 6.59) | notebook committed 2025-11-05, renamed (content unchanged, same blob sha `c0d665a9...`) 2026-06-22 | Yes — `data/baselines/official_raw.py` `SOL_64` | Yes — DUAL_VERIFIED, see `results/certified/n64_k112_baseline_official.json` | Best construction we found in this project's search budget: **112** (no improvement) | Pre-AlphaEvolve best was reportedly 110 per WebSearch summary of the paper |
| 100 | 164 | AlphaEvolve repo (arXiv:2511.02864, Problem 6.59) | same notebook, same commit history | Yes — `data/baselines/official_raw.py` `SOL_100` | Yes — DUAL_VERIFIED, see `results/certified/n100_k164_baseline_official.json` | Best construction we found in this project's search budget: see `logs/lns_exact_n100_seed7.json` for the search outcome | — |

## Candidate related/adjacent papers checked and ruled out as NOT superseding

1. **Károlyi & Solymosi, "A Salem–Spencer-Type Construction for Large Subsets of
   Integer Grids with No Isosceles *Right* Triangles"**, arXiv:2607.22828 (2026-07-24).
   This is a DIFFERENT, strictly weaker problem: it only forbids isosceles triangles
   that are also right triangles, not all isosceles triangles. A set avoiding all
   isosceles triangles (our problem) automatically avoids isosceles right triangles,
   but not vice versa — so their Ω(n^1.3) bound is for an easier problem and is not
   comparable to / does not supersede C(n) for Problem 6.59. Ruled out.
2. **Jánosik, "Avoiding configurations of small size in the square grid"**,
   arXiv:2601.14465. WebFetch of the abstract found it addresses avoiding
   parallelograms, trapezoids, concyclic sets, rhombuses/kites — not isosceles
   triangles — and no mention of C(64)/C(100)/AlphaEvolve/Problem 6.59. Ruled out
   (different forbidden configuration).
3. **"Geometry-Aware MCTS for Extremal Problems in Combinatorial Geometry"**,
   arXiv:2606.26399. WebFetch of the abstract found it addresses the No-Three-in-Line
   problem and Smallest Complete Set problem — not isosceles-triangle avoidance, no
   mention of our target quantities. Ruled out (different problem).

## Verdict

**We found no source, in the scope searched, reporting a legal construction beating
112 points on the 64×64 grid or 164 points on the 100×100 grid for the exact
Problem 6.59 definition (all isosceles triangles, including degenerate collinear
equidistant triples, forbidden).**

This is stated in the conservative form required by this project's integrity rules:
*"We found no larger construction in the sources examined,"* not a claim that no such
construction exists anywhere.

---

# Refresh #2 — 2026-08-14 (full-PDF scope; corrects two Refresh #1 rulings)

Scope this time: WebSearch (4 queries), **full-PDF text extraction** of the two
candidate papers previously judged at abstract level only, OEIS lookup (blocked,
HTTP 403 — still not covered), and a GitHub API re-check of the official notebook.

## Result: no change to the record. 112 / 164 still stand.

**Third-party corroboration (new, and the most valuable finding of this refresh).**
Zhang, Zhuang, Wang & Kaplan, *Geometry-Aware MCTS for Extremal Problems in
Combinatorial Geometry*, arXiv:2606.26399 (2026-06), independently surveys the
best-known bounds for exactly our problem and records, in its Table 1:

> Max No Isosceles Triangle — Lower Bound Ω(n/√log n) (Charton et al., 2024);
> ours ≈ 1.4n (Empirical Fit); **112 for n = 64 and 164 for n = 100
> (Georgiev et al., 2025)**

This is an *external, independent* attestation — by a group with no connection to
this project — that 112 and 164 were still the state of the art as of June 2026.
Previously our "no one has beaten it" statement rested only on our own negative
search; it now has outside support.

They also explicitly concede they did not match it:

> "Highly specialized constructions using recent AI tools find larger sets for
> specific grid sizes (e.g., n ∈ {64,100}) (Georgiev et al., 2025) … We still
> include the performance of our MCTS framework to demonstrate that it remains
> competitive with these more specialized approaches."

**Definition cross-check (independent confirmation of our oracle).** Their §2
formalization matches ours exactly, degenerate case included:

> Max-No-Isosceles: Φ(s) = {∀P ⊆ s with |P| = 3, ¬Isos(P)}, where Isos(P) is true
> if at least two Euclidean distances between points in P are equal, **including
> degenerate cases (i.e., collinear triples where one point is the midpoint of the
> segment)**.

This is the first outside confirmation that the problem statement our verifier
enforces is the intended one.

## Corrections to Refresh #1

Refresh #1 ruled out papers #2 and #3 on the basis of abstract-level reads. The
full-PDF reads show **both rulings were reached for the wrong reason.** The
verdicts survive; the reasoning did not.

- **#3 (arXiv:2606.26399, MCTS).** Refresh #1 said it "addresses the No-Three-in-Line
  problem and Smallest Complete Set problem — not isosceles-triangle avoidance."
  **That is wrong.** Max-No-Isosceles is one of the six problems it studies
  (§2, §4.2, App. A.1.5, App. G.5). The abstract simply never names it, because it
  is one of the problems on which they did *not* set a new record. Correctly ruled
  out as not superseding — but only because their result is *worse*, not because
  the paper is off-topic.
- **#2 (arXiv:2601.14465, Jánosik).** Refresh #1 said it covers "parallelograms,
  trapezoids, concyclic sets, rhombuses/kites — not isosceles triangles." Also
  wrong: it does treat f_iso△(n), defined as "no three of them form the vertices of
  a (possibly flat) isosceles triangle." Correctly ruled out, but as a **survey**
  that proves nothing new here and cites the same Charton–Ellenberg–Wagner–Williamson
  sublinear lower bound — not because it is about a different configuration.

Methodological note: Refresh #1's own mandatory caveat ("checked only at the
abstract level … a full-PDF read might surface an incidental mention missed here")
predicted this failure exactly. The caveat did its job. Abstract-level screening is
hereby recorded as **insufficient** for this problem, precisely because our target
quantity tends to appear in papers that did *not* improve on it and therefore do
not advertise it.

## New comparison data point

| n | Size | Source | Ratio size/n |
|---|---|---|---|
| 64 | 112 | Georgiev et al. 2025 (incumbent) | 1.750 |
| 90 | **124** | arXiv:2606.26399 App. G.5 Fig. 13 (MCTS) | 1.378 |
| 100 | 164 | Georgiev et al. 2025 (incumbent) | 1.640 |

The MCTS n=90 figure is the only *new* concrete construction size this refresh
surfaced. It is far below the incumbent trend and is not useful as a seed.

## Reinterpretation of our own sealed-tournament numbers (important)

arXiv:2606.26399 reports that a well-engineered, symmetry-aware, 7-CPU-day-per-trial
MCTS search reaches **≈ 1.4n** on this problem from scratch. Evaluated at our two
targets that is 89.6 (n=64) and 140 (n=100).

Our sealed tournament — the S0-free arm, i.e. search that never sees the official
baseline (`TOURNAMENT_SEALED/EXPERIMENTS/wave2_best_n*.json`) — produced **90 (n=64)
and 137 (n=100)**.

Those land essentially *on* the published generic-search frontier. This reframes that
result: 90/137 is not our search underperforming, it is **what independent
from-scratch search of this problem currently achieves, anywhere.** The incumbents sit
at 1.75n and 1.64n, far above that frontier.

Consequence for strategy: the ~27-point gap from 137 to 165 at n=100 is very unlikely
to be closed by more or better *generic* search, however much compute is spent. The
incumbents' margin over the generic frontier came from imposed structure — the
approximate 4-fold symmetry and edge-concentration prior that the source paper reports
was the decisive hint. Tellingly, arXiv:2606.26399's App. C.2 Table 2 shows they applied
**no canonical symmetry pruning at all** for Max-No-Isosceles (unlike Max-N3IL,
Min-Complete and Min-Dom, where they ran one trial per symmetry class) — the one
problem where they used no symmetry prior is the one problem where they fell furthest
behind. That is weak but directionally consistent evidence that the symmetry prior,
not search power, is the operative ingredient.

## Weak heuristic (explicitly NOT evidence)

Fitting the known asymptotic form c·n/√(log n) through the n=64 incumbent predicts
a ratio of 1.750·√(ln 64 / ln 100) = 1.663 at n=100, i.e. ≈ **166** points; the
incumbent there is 164. Anchoring the other way, n=100 predicts 110.4 at n=64 where
the incumbent is 112. Under this crude scaling the n=64 construction is the stronger
of the two and n=100 carries ~2 points of apparent slack.

**This is numerology, not evidence.** The asymptotic constant is meaningless at
n ≈ 100, the √log correction is nowhere near its asymptotic regime, and two data
points cannot fit a one-parameter law with any confidence. It is recorded only
because it points the same direction as our independent structural finding that
n=100 is the softer target, and must never be cited as support for C(100) ≥ 165.

## Official repository re-check

`experiments/subsets_of_the_grid_with_no_isosceles_triangles.ipynb` is at blob sha
`c0d665a986ec…` — **byte-identical to what Refresh #1 recorded**. Commits touching
that path: only `8df7363e` (2025-11-05, initial) and `8887f654` (2026-06-22, rename).
The 2026-07-01 / 2026-07-02 repo-wide commits did not touch it. No improved
construction has been published there.

## Refresh #2 verdict

**No source found, in the scope searched, reporting a legal construction beating
112 (n=64) or 164 (n=100).** The record has now been checked twice, the second time
including a paper that independently confirms both numbers. Further un-targeted
literature searching is judged low-yield and is not recommended.

Still not covered (unchanged gaps): OEIS (403-blocked this session), MathSciNet,
Google Scholar citation graph, non-English sources, puzzle/competition archives.

## Caveats (mandatory disclosure)

- This audit used WebSearch (a small number of queries) and WebFetch of two candidate
  papers' abstract pages (not full PDFs) plus one GitHub API commit-history check. It
  is **not** an exhaustive literature review (no systematic search of MathSciNet,
  Google Scholar citation graphs, OEIS, competitive-programming/puzzle-hunt archives,
  or non-English sources).
- The Jánosik and MCTS papers were checked only at the abstract level via WebFetch's
  summarization; a full-PDF read might surface an incidental mention missed here.
- Any claim of "novelty" or "no known larger construction" in this project's other
  documents should be read subject to these scope limits, per the project's own
  Level 4 discipline (apparently new / to the best of our literature search).
