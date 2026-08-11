# Preprint Readiness

## Verdict: RESEARCH_REPORT_ONLY

**Rationale:** This project's substantive result is a reproduction (with genuine
independent dual-verification) of a previously published construction, plus a
methodologically real but ultimately negative search result (no improvement found),
plus a real multi-agent adversarial-audit process. Per the project's own gating
rule ("do not claim READY just because a PDF was successfully generated" — and here
not even that: no PDF was generated at all, see below), none of the four conditions
for producing a full arXiv-style manuscript push are unambiguously met at
publication quality:

- No dual-certified NEW lower bound was produced (Section 6/10 of FINAL_REPORT.md).
- No new structural CONSTRUCTION was produced (only structural OBSERVATIONS on the
  existing baselines, explicitly unproven, sample size 2).
- The search METHOD (LNS + exact MILP regional repair) is real and reasonably
  documented, but was only run for one round in one session — a full paper's
  "Search Methodology" section would benefit from more seeds, more routes actually
  executed (not just proposed), and ideally a second independent search route's
  results to compare against, none of which happened here.
- The negative result IS reasonably systematic (33766 exact regional repairs across
  two grid sizes) but is a single route, single-round result — a stronger
  methodological paper would report at least 2-3 genuinely different search
  strategies' outcomes (as Proposer round 1 itself recommended and as the project's
  own brief calls for "at least 3 formal rounds unless a clear stop condition is
  hit" — no clear stop condition specific to the OVERALL project was hit; only the
  single LNS+MILP route reached its own natural stopping point).

A `paper/main.tex` skeleton with a hedged, accurate abstract WAS drafted (see
`paper/main.tex`) as a template for a future, more complete write-up, but it
contains explicit `[PLACEHOLDER]` sections that would need real content (more
search routes' results, a completed Related Work read of the two ruled-out
adjacent papers' full text rather than abstracts only, etc.) before it should be
considered submission-quality. **No PDF was compiled** — no LaTeX distribution
(`pdflatex`/`latexmk`/`tectonic`) was available in this session's environment; see
`paper/README_SUBMISSION.md` for exact compile instructions for whoever has such a
toolchain available.

## What would upgrade this to READY_WITH_REVISIONS

1. At least one more genuinely different search route actually executed to
   completion (Proposer Strategy A: tabu with informed removal, or Strategy B: SA
   with periodic exact repair) with its own negative-or-positive result reported.
2. A full-text (not abstract-only) check of the two literature papers ruled out in
   `record_registry.md`, and ideally 1-2 additional independent literature queries
   with different phrasing/sources (e.g. OEIS, a directed search of citations TO
   arXiv:2511.02864 rather than just keyword search).
3. Either a compiled, proofread PDF (once a LaTeX toolchain is available) with all
   placeholder sections filled in, or an explicit decision to publish as a
   Markdown/HTML technical report instead of a LaTeX preprint.

## What would upgrade this to EXTERNAL_PRIORITY_CHECK_REQUIRED

Only if a future round's search DOES find a legal construction exceeding 112 (n=64)
or 165 (n=100) points AND it passes DUAL_VERIFIED certification AND a fresh Red Team
pass finds no defect specific to that candidate. That did not happen in this
session.
