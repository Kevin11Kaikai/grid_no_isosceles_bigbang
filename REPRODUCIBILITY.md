# Reproducibility

## Environment (as actually used in this session)

- Python 3.12.7
- numpy 1.26.4
- scipy (version providing `scipy.optimize.milp` / HiGHS backend — used by
  `src/search/lns_exact_repair.py`)
- OS: Windows 10 Enterprise 10.0.19045
- No GPU used.
- git 2.47.1.windows.2
- Working directory: `D:\Others\grid_no_isosceles_bigbang` (isolated git repo,
  separate from the unrelated files in `D:\Others`).

Exact package versions were not pinned to a requirements.txt/lockfile in this
session; if reproducing later, run `pip freeze` and compare against the versions
above as a sanity check, since `scipy.optimize.milp`'s HiGHS solver behavior could
in principle vary across versions.

## How to reproduce baseline verification

```bash
cd grid_no_isosceles_bigbang
python -m src.verification.certify results/candidates/n64_k112_baseline_official.json
python -m src.verification.certify results/candidates/n100_k164_baseline_official.json
```

Expected: both print `"status": "DUAL_VERIFIED"`, `verifier_A_pass: true`,
`verifier_B_pass: true`, and the hashes recorded in `artifact_hashes.json`.

Independent verifier can also be run standalone:
```bash
python src/verification_independent/independent_verifier.py data/baselines/baseline_n64_independent.json
python src/verification_independent/independent_verifier.py data/baselines/baseline_n100_independent.json
```

## How to run the unit/fuzz test suite

```bash
python tests/test_oracle_verifier.py
python tests/test_incremental_state.py
python -m pytest tests/test_independent_verifier.py -v
```

## How to run each search method

Greedy multistart (Route A):
```python
from src.search.greedy import greedy_multistart
best, meta = greedy_multistart(n=64, num_starts=50, time_budget_s=60, seed0=0,
                                orders=("random", "boundary_first", "center_first"))
```

LNS with greedy repair (baseline-style, Route D-lite):
```python
from src.search.lns import lns_run
from data.baselines.official_raw import SOL_64
best, meta = lns_run(64, SOL_64, time_budget_s=60, seed=1)
```

LNS with EXACT MILP repair (Route D, the main search route used):
```python
from src.search.lns_exact_repair import lns_exact_run
from data.baselines.official_raw import SOL_100
best, meta = lns_exact_run(100, SOL_100, time_budget_s=420, seed=7, milp_time_limit_s=2.0)
```
Any candidate produced this way that beats the baseline size MUST be passed through
`src/verification/certify.py` before being trusted (the search code itself already
re-checks with the slow oracle before updating `best`, but certify.py is the single
authorized promotion path to `results/certified/`).

## How to verify a candidate end-to-end

```bash
python -m src.verification.certify results/candidates/<file>.json
```
This re-reads the candidate from disk (never trusts an in-memory object), runs both
verifiers, checks structural validity (bounds, duplicates, size-field consistency),
computes a sha256 hash of the canonical (sorted) point set, and — only if
DUAL_VERIFIED — copies the result into `results/certified/`.

## How to regenerate figures

See `src/analysis/` (created as needed) and `figures/`; each figure script is named
after its output file, e.g. a script producing `figures/baseline_n64.png` would be
`src/analysis/plot_baseline_n64.py`. Consult `FINAL_REPORT.md` for which figures were
actually generated in this session (a bounded session may not have produced every
figure listed in the original project brief; this is disclosed there, not silently
omitted).

## How to compile the paper (if generated)

```bash
cd paper
latexmk -pdf main.tex
```
If `latexmk` is unavailable in the environment, `pdflatex main.tex` run twice (for
references) is the fallback, documented in `paper/README_SUBMISSION.md`.
