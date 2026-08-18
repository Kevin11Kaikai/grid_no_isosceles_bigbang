# Cursor sidecars (branch `sidecar-qsq-f2-cursor`)

These directories are **not** part of the BigBang `src/` campaign tree.
They record Cursor/Grok work on Problem 6.59 relaxations, kept isolated from
Claude's `iso6` lane. Nothing here claims `C(n)=O(n^{2-ε})`.

| directory | what it is | status |
|---|---|---|
| `iso6-q4f/` | Q4 falsification then a dead upper-bound attempt | frozen |
| `iso6-joint/` | Joint constraint hunt after Q4; lemma **J1** (rotate-90 / square-corner); J2 not named | frozen |
| `iso6-sq/` | Square-corner relaxation `Q_SQ`; peeling check; elementary upper-bound holes; theorem `F_2(n)=2n-2`; `F_3` lower bound only | live record |

Start at each folder's `LEDGER.md`. Proved two-row theorem: `iso6-sq/proofs/two_row.md`.

Do not treat these as a power-saving proof for `C(n)`.
