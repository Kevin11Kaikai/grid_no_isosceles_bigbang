# Upper-bound strategy (sidecar)

Lane: `d:\others\iso6-q4f` only. Not an iso6 document. Do not copy into `iso6/`.

## Target

Prove `Q4(n) = O(n^{2-ε})` for some fixed `ε > 0`.
Anything stronger (`O(n^{3/2})`, `O(n)`) is a bonus, not a substitute for honesty.

Success = a checkable proof with a named `ε`.
Partial success = lemmas that stop short of a power saving, labelled as such.
Failure = a Q4-feasible set in the dangerous regime of size `n^{1+c}`.

## Case chart

```
Q4-feasible S
 ├── some |U_*| ≤ n^{1-ε}     →  |S| ≤ n^{2-ε}          [lemma 2, DONE]
 └── all four supports > n^{1-ε}
      └── S ⊆ U_col × U_row
           ├── S = U_col × U_row (full product)
           │     → |S| ≤ 2n-1                          [lemma 1, DONE]
           └── proper subset
                ├── density δ ≤ n^{-ε}
                │     → |S| ≤ n^{2-ε}                  [lemma 2 corollary]
                └── δ > n^{-ε}  (dense partial filling)
                      → lemma 3
                            ├── min(|H|,|J|) ≤ n^{1-ε}          [heavy lines, PROVED]
                            ├── |H|,|J| ≤ n^{7/8}               [core product, PROVED]
                            └── |H| > n^{7/8} and |J| > n^{3/4} [GAP]

```

The campaign target is equivalent to: **lemma 3, or a proof that the dense branch is empty for large n.**

## What is already used, not reproved

From iso6 `docs/Q4_route.md` (read-only):

- `C(n) ≤ Q4(n)`
- full column support ⇒ `|S| ≤ 2n`
- `Q4(n) ≥ r_3(n)` via one row
- constraints 1–2 alone cannot give a power saving (B3)
- summing directions independently caps at `1/log n` (B4) — lemma 3 must not be a harmonic sum

## Status of this attempt

**Closed.** iso6 falsified Q4 (`n^{2-o(1)}`). Sidecar lemmas are correct
and do not give a power saving. The remaining heavy-line core is that
construction. Do not merge into iso6.

- `proofs/lemma_product.md` — DONE
- `proofs/lemma_case_split.md` — DONE
- `proofs/lemma3_caseB.md` — DONE (`√n` form); campaign form in lemma3_campaign
- `proofs/lemma3_caseA.md` — old A1 false; fold geometry
- `proofs/lemma3_campaign.md` — B′ / B″; old triple closed
- `proofs/lemma3_sstar.md` — few heavy `(d,δ)` vertices on `S*`
- `proofs/lemma3_heavy.md` — global heavy lines; `S'` absorbed; core GAP
- `proofs/lemma_dense.md` — dichotomy + dead disjoint-kill


