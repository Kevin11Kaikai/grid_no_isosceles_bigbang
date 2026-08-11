# Submission Notes

## Compilation status: NOT COMPILED (no LaTeX toolchain in this session's environment)

`pdflatex`, `latexmk`, and `tectonic` were all checked and are unavailable in this
Windows environment (`where pdflatex`, `where miktex` both returned "not found").
Installing a full LaTeX distribution (MiKTeX/TeX Live) was judged out of scope for
this session (a large, non-trivial software installation) rather than something to
do silently in the background of a research task; a human with a LaTeX environment
should run:

```bash
cd paper
latexmk -pdf main.tex
```

or, without `latexmk`:

```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Content status

`main.tex` and `references.bib` are complete (no `[PLACEHOLDER]` brackets remain;
all sections have real, hedged content reflecting this session's actual results).
Per `PREPRINT_READINESS.md`, this manuscript is assessed as **RESEARCH_REPORT_ONLY**
quality, not submission-ready, primarily because only one search route was run to
completion in this session (see PREPRINT_READINESS.md for the specific upgrade
path). Treat `main.tex` as a well-scoped draft/template, not a final manuscript.

## Figures referenced but not embedded in main.tex

`figures/baseline_n64.png`, `figures/baseline_n100.png`,
`figures/ring_histogram_n64.png`, `figures/ring_histogram_n100.png` were generated
(`src/analysis/plot_baselines.py`) but not yet `\includegraphics`'d into `main.tex`
in this pass — a straightforward addition once compilation is possible to verify
figure placement/sizing visually.

## Authorship

`\author{Anonymous Research Draft}` per project instructions (no institutional
affiliation was specified or should be fabricated).
