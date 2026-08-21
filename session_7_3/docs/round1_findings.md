# Session 7.3 — Round 1 findings

**Headline: no new bound was proved. The round produced a rigorous diagnosis of *why* the
conjectured linear lower bound resists the standard tools, and it is a sharp one: every
standard probabilistic route fails by exactly one logarithmic factor, and all three
failures trace to the same arithmetic sum.**

## 0. What the FIND stage changed about the target

The archived campaign (`iso6`) spent itself entirely on the **upper** bound
`C(n) = O(n^{2-eps})`. The FIND stage found that this was the wrong end of the problem.

From Janosik et al., *Avoiding configurations of small size in the square grid*,
[arXiv:2601.14465](https://arxiv.org/abs/2601.14465) (2026):

> "the best known lower bound on `f_iso(n)` is sublinear due to Charton, Ellenberg,
> Wagner, and Williamson. They remarked that most probably a linear lower bound can be
> achieved via the random independent set process, and conjecture that the answer is
> indeed linear, based on the constructions found by Patternboost."

So the live open question is `C(n) = Omega(n)`, the gap to the known `c*n/sqrt(log n)` is
exactly `sqrt(log n)`, and the experts have **named a route without executing it**. That is
a far better target than the upper bound: explicitly open, believed true, believed
reachable.

Supporting datum: `C(n)/n` over every known exact/best value is strikingly flat —
`20/12=1.67, 22/13=1.69, 28/16=1.75, 56/32=1.75, 112/64=1.75, 164/100=1.64`.

## 1. The hypergraph parameters — `VERIFIED_COMPUTATIONAL_RESULT`

`H_n` = the 3-uniform hypergraph on `V=[n]^2` whose edges are the isosceles triples.
Each edge has a **unique** apex: two apexes would force an equilateral lattice triangle,
which does not exist. Measured exactly (`experiments/degree.py`, `experiments/codeg.py`):

| quantity | measured | form |
|---|---|---|
| `N` | `n^2` | |
| `D` (avg degree) | `Davg/(n^2 log n) = 1.48 -> 1.66` for `n = 3..16`, rising slowly | `Theta(n^2 log n)` |
| `Dmax/Davg` | `1.36 - 1.50`, bounded | near-regular |
| `Delta_2` (max pair-degree) | `~ 1.7 n` | `Theta(n)` |
| `Gamma` (max `(r-1)`-codegree) | `~ 1.9 n^2` | `Omega(n^2)` |

The `log n` in `D` is exactly `Sum_{d<=X} r_2(d)^2 ~ X log X` — the mean number of grid
points sharing a squared distance.

## 2. The obstruction — `VERIFIED_THEOREM` (about the tool, not about the problem)

Bennett-Bohman, *A note on the random greedy independent set algorithm*
([arXiv:1308.3732](https://arxiv.org/abs/1308.3732)), Theorem 1.1, from the LaTeX source:
for `r`-uniform, `D`-regular `H` on `N` vertices with `D > N^eps`, **if**

```
    Delta_l(H) < D^{(r-l)/(r-1) - eps}   for l = 2..r-1     and     Gamma(H) < D^{1-eps}
```

then the random greedy algorithm gives `|I| = Omega(N (log N / D)^{1/(r-1)})`.

Applied to `H_n` (`r=3`, `N=n^2`, `D=Theta(n^2 log n)`) the conclusion would be **exactly**
`Omega(n^2 * (2 log n/(n^2 log n))^{1/2}) = Omega(n)` — the conjectured bound, on the nose.

**Both hypotheses fail, and each fails by exactly a logarithmic margin.**

| hypothesis | required | actual | deficit |
|---|---|---|---|
| `Delta_2 < D^{1/2-eps}` | `n^{1-2eps+o(1)}` | `Theta(n)` | `Delta_2 ~ D^{1/2}/sqrt(log n)` |
| `Gamma < D^{1-eps}` | `n^{2-2eps+o(1)}` | `Omega(n^2)` | `Gamma ~ D/log n` |

Both deficits are rigorous, not merely measured:

- `Delta_2 = Omega(n)`: for `p=(x,c)`, `q=(x,c+2)` the perpendicular bisector is the grid
  line `y = c+1`, giving `n-2` apexes `r` with `{p,q,r}` isosceles.
- `Gamma = Omega(n^2)`: for `p,q` on a common row `y=c`, every vertical mirror pair
  `{(x,y),(x,2c-y)}` is equidistant from **both**, giving `>= n(n-1)/2` shared pairs.

AKPSS / Duke-Lefmann-Rodl do not apply either — they require `Delta_2 = 1` (simple
hypergraphs), and here `Delta_2 = Theta(n)`.

**Which pairs carry the obstruction** (`experiments/extremal_pairs.py`): the `Delta_2`- and
`Gamma`-extremal pairs are precisely the **axis-parallel and diagonal** ones — at `n=12`
the `Gamma`-extremal pairs are exactly the same-row and same-column pairs. So the
obstruction is carried by the grid's **D4 mirror structure**, i.e. by the
*degenerate/collinear* isosceles triples — the very feature that separates this problem
from its continuous cousin (erdosproblems #657).

## 3. The same log factor kills the Local Lemma route — `VERIFIED_THEOREM`

Restrict to one point per column, `f:[n]->[n]` uniform i.i.d. Bad events `A_{i,j,k}`:
apex `i` equidistant from columns `j,k`. Then `P(A_{i,j,k}) = O(d(C)/n^2)` with
`C = (i-k)^2-(i-j)^2`, so `E[#violations] = Theta(n log n)` against only `n` points.
Symmetric LLL needs `e*p*(d+1) <= 1` and gives `Theta(log n) > 1`; the asymmetric form
gives `Sum_{B~A} P(B) = Theta(log n)` and fails identically.

## 4. The unifying statement

> **Every standard probabilistic route to `C(n) = Omega(n)` — alteration, random greedy /
> nibble, and the Local Lemma — falls short by exactly one factor of `log n`, and in all
> three the factor is the same arithmetic sum `Sum_{d<=X} r_2(d)^2 ~ X log X`.**

Alteration *loses* `sqrt(log n)`, giving the known `n/sqrt(log n)`; the nibble would
*recover* it, but its codegree hypotheses fail by `sqrt(log n)` and `log n` respectively.
The problem sits exactly on the boundary of the available technology. This is why the
remark in arXiv:2601.14465 is a remark and not a theorem.

## 5. Evidence for the conjecture — `VERIFIED_CONSTRUCTION`

Isosceles-free sets with **exactly one point per column** — which would give `C(n) >= n`
outright — were found by backtracking for `n = 8,12,...,40,48,56,64,80,96,128`. Node counts `45 360` (`n=40`),
`694 670` (`n=80`), `1 669 785` (`n=96`), `2 843 740` (`n=128`) — growing
**polynomially**, roughly `n^2` to `n^4`, not exponentially, which is the real evidence
that these sets exist for every `n`. The `n=96` witness was re-checked by an independent
naive verifier sharing no logic with the search: 96 points, 96 distinct columns,
428 640 apex-and-pair combinations, **0 violations** (`experiments/verify_onecol.py`).

Note the honest scope: this is **not** a record. `C(96) >= 155` is already implied by the
AlphaEvolve-style constructions (164 points in `[100]^2`). A one-per-column set of size
exactly `n` is worth only its *structure* — it is the shape a clean proof of
`C(n) = Omega(n)` would most plausibly take.

A methodological trap was avoided here: a first, weaker search (greedy with restarts)
reported "not found" at `n=48` and `n=64`; proper backtracking finds both in seconds. Per
campaign rule §69, repeated search failure is not impossibility — and here it was literally
an artefact of the search.

## 6. Also verified: the strip decomposition — `VERIFIED_LEMMA`

`S` in `[k]x[n]` with rows `A_i` is isosceles-free **iff** all three hold
(`experiments/strip_reform.py`, brute-forced over 87 999 subsets, `k<=3`, `n<=6`,
**0 mismatches**):

- **(M)** for `a` in `A_i` and rows `j, j'` with `|i-j| = |i-j'|`: `a` is not the midpoint
  of a pair `(b,b')` in `A_j x A_{j'}`. The case `j'=j` says: **no occupied column is the
  midpoint of a pair inside any single row**.
- **(V)** if `A_i` is nonempty then `A_j` and `A_{2i-j}` are **column-disjoint** for every
  `j != i` — rows equidistant from a nonempty row share no column.
- **(D)** the residual `u^2 != u'^2` collisions, each a divisor equation
  `(s-s')(s+s') = c`, hence `n^{o(1)}` solutions — rigid and sparse.

**(V) explains an observation the archive left unexplained** ("extremal sets at `n=9,10`
leave whole rows empty"): if *every* row is occupied then every two same-parity rows are
column-disjoint, forcing `|S| <= 2n`. An extremal set must therefore empty out rows to
break the row-3-APs. Formally `|S| <= cc(G)*n`, where `G` is the graph on occupied rows
with `j ~ j'` iff same parity and `(j+j')/2` occupied, and `cc` is the clique-cover number.

**This does not yield a new upper bound.** Taking the occupied-row set to be 3-AP-free
makes `G` edgeless and the bound degenerates to `r_3(k)*r_3(n) = n^{2-o(1)}` — i.e. it is
capped by the archive's own barriers B2/B3/B4'. `CHECKED -> capped, not promoted.`

## 7. Status

| item | evidence level | tier |
|---|---|---|
| `D`, `Delta_2`, `Gamma` for `H_n` | `VERIFIED_COMPUTATIONAL_RESULT` + rigorous lower bounds | C |
| Bennett-Bohman inapplicable, with exact deficits | `VERIFIED_THEOREM` | **B** |
| LLL inapplicable, same log factor | `VERIFIED_THEOREM` | **B** |
| "all standard routes miss by one log" | `EMPIRICAL_PATTERN` over three routes | B |
| one-per-column sets exist for `n <= 80` | `VERIFIED_CONSTRUCTION` | C |
| strip decomposition (M)/(V)/(D) | `VERIFIED_LEMMA` | C |
| `C(n) = Omega(n)` | **NOT PROVED** | — |
| `C(n) = O(n^{2-eps})` | **NOT PROVED, not attempted this round** | — |

`NOVELTY_PRELIMINARY` on sections 2-4: searched, nothing located, but these are claims
about the *inapplicability of a tool*, exactly the kind of statement that lives unstated in
the literature. **None of it may be presented as a theorem about `C(n)`.**
