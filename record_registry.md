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
