# 1b. KNOWN RESULTS — read before any FIND stage. Rediscovering any of this is not a result.

Problem: `C(n) = max |S|`, `S ⊆ [n]²`, no three distinct points with `d(a,b) = d(b,c)`
(squared Euclidean; **degenerate/collinear triples are forbidden too**).
Correct name: **Problem 59** of the AlphaEvolve Repository of Problems = **§6.39** of
arXiv:2511.02864. ("6.59" is a conflation of the two and finds nothing in any search.)
The continuous cousin is erdosproblems.com **#657**.

## Exact values — KNOWN, with proved optimality, for all n ≲ 32
Charton–Ellenberg–Wagner–Williamson, *PatternBoost*, arXiv:2411.00566 (Oct 2024): SAT
solvers find the optima **and prove optimality** for n up to ≈32, and the paper plots every
computed value.
```
C(1..13) = 1,2,4,6,7,9,10,13,16,18,18,20,22     (13 independently recomputed here)
C(16)=28  C(21)=36  C(23)=40  C(25)=44  C(27)=48  C(32)=56
```
=> Any exact C(n) with n ≤ 32 is a REPRODUCTION. First open exact value: **n = 33**.

## Constructions
112 in [64]², 164 in [100]² — AlphaEvolve, arXiv:2511.02864 §6.39. (110 in [64]² by
PatternBoost.) Beating these is Tier C evidence, not a theorem.

## Asymptotics — the actual target
```
n/sqrt(log n)  ≲  C(n)  ≲  exp(-c (log n)^{1/9}) · n²
```
Upper mechanism: every line meets S in a 3-AP-free set, so `C(n) ≤ n·r_3(n)`, plus
Kelley–Meka / Bloom–Sisask. **`C(n) = O(n^{1.99})` is OPEN.** Asked by Wu and by
Ellenberg–Jain. Lower bound possibly improvable to ≳ n.

## Dead — do not re-derive (D:\Others\iso6\)
- **Z[i] / square-corner relaxation `Q_SQ` = isosceles-right-triangle-free** — KNOWN, it is
  `F(n)` in the literature. Bloom (2014): `F(n)=O(n²/(log n)^{1-ε})`. Károlyi–Solymosi
  arXiv:2607.22828: `F(n) ≪ n²/(log n)^{1+c}` and `F(n) ≫ n^{1.318}/(log n)^{140}`.
  The campaign's tensor lemma **is** their construction mechanism. And the relaxation is
  **lossy**: `n²/(log n)^{1+c}` is weaker than the baseline `n² e^{-c(log n)^{1/9}}`.
- **Behrend-digit-spheres are never square-corner-free** = Remark 2.5 of arXiv:2607.22828.
- Barriers proved for their method classes (`iso6/docs/barriers.md`, `verified_results.md`):

| | mechanism class capped | cap |
|---|---|---|
| B1 | distance-multiplicity / shell counting (Landau–Ramanujan) | `n²/√log n` |
| B2 | 3-AP-freeness on all lines (Behrend product) | `n^{2-o(1)}` |
| B3 | axis line-kill, full strength | `n^{2-o(1)}` |
| B4′ | bounded-direction line-kill; `k` directions leave `1-O(k/R)` of rotation classes free | `n^{2-o(1)}` |
| B5 | scale iteration with sub-constant scale ratio | polylog only |
| **B6** | **degree-`k` relaxation (≤k per radius per apex): admits `n^{2-2/(k+1)-o(1)}`** | **degree-2-robust ⇒ `n^{4/3}`** |
| B7 | using only distances ≤ L; truncation at R ≡ full problem on an `M×M` torus, `M~2√R` | `n²/L` |
| B8 | distinctness at only `k = n^{o(1)}` apexes | `n²/k·n^{o(1)}` |

**B6 is the sharpest filter: check every candidate argument against it BEFORE developing it.**
A proof of `n^{1+o(1)}` must be exactly tight at degree 1.
**B4′ design requirement:** a live mechanism must be violated by `S = ∩_i φ_i^{-1}(W_i)`
with every `W_i` 3-AP-free. If its consequences follow from "every projection is 3-AP-free",
it is dead.

## Falsified in-campaign (`iso6/ledgers/failure_ledger.md`)
F1 Q4 four-direction relaxation (`≥ n^{2-o(1)}`) · F2 boundary induction · F3 hand-derived
incremental filters · F4 small-scale tower ratios uninformative · F5 finite-margin
(1+i)-tower recurrence · F6 blind mode self-collision · **F7 `C(12)=20` already known**.

## The two F7 rules — MANDATORY
1. **FIGURES ARE DATA.** A claim "we computed the values for n ≤ N" is prior art for every
   n ≤ N whether or not any number is typeset. Open the figure (`arxiv.org/e-print/<id>`).
2. **INTERROGATE SUPPLIED NUMBERS.** A baseline handing you exact values at n=32 has already
   answered your question at n=12. No network access needed for that refutation.

## Structural facts established (correct, mostly folklore-or-unsearched)
- `C(1,n) = r_3(n)` exactly (Salem–Spencer, A003002) — the calibration test for degeneracy.
- `C(n²) ≥ C(n)²` is **FALSE**: `C(16)=28 < 36 = C(4)²`. No naive product/lift exists.
- Extremal sets at n=9,10 are unique up to D4, leave whole rows empty. No algebraic family
  (modular parabola/cube/inverse, Sidon, primitive-root, lattice circles, 2-D Behrend) is
  isosceles-free; none beats greedy. Weak evidence the truth is near `n^{1+o(1)}`.
- `C(2,25) = 17` is an exception to an otherwise-clean 2×n product law.
