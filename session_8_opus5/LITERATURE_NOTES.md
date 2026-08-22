# Literature notes — Session 8

Only sources whose **theorem statements were opened and read** are listed as verified.
Repository paraphrases from earlier branches were not used as authority for anything here.

---

## Verified at theorem level

### Bennett–Bohman, *A note on the random greedy independent set algorithm*
arXiv:1308.3732; Random Structures & Algorithms **49** (2016). LaTeX source read in full
(`lit/ind.tex`, 1675 lines).

**Theorem 1.1 (ind.tex line 254), exact statement.** Let `r >= 3` and `eps > 0` be fixed.
Let `H` be `r`-uniform, `D`-regular on `N` vertices with `D > N^eps`. If
`Delta_l(H) < D^{(r-l)/(r-1) - eps}` for `l = 2,...,r-1`, and `Gamma(H) < D^{1-eps}`, then
random greedy produces an independent set with `|I| = Omega( N (log N / D)^{1/(r-1)} )` with
probability `1 - exp(-N^{Omega(1)})`.

Points established by reading, used throughout this session:

- **`eps` is a fixed constant**, and the proof needs `zeta << delta << eps` (line 745). All
  the "room" in the hypotheses is polynomial, never logarithmic.
- There is a **second density hypothesis**, `N = Omega(D^{1/(r-1)+eps})` (eq. `notdense`,
  line 309), used at lines 810, 875, 956, 1168. `H_n` satisfies it (`D ≍ N log N << N^2`).
- The stopping time (line 720) has four conditions; the two pair-quantified ones are proved
  in §"Crude bounds" (line 757). **At `r = 3` the `dlemma` induction is empty** (`b = r`
  immediately) and `clemma` reduces to the single case `c_{2,2->1}`.
- `C_{2,2->1}` is consumed at exactly lines 1017–1029 (drift of `d_l^-`), 1180 (step size),
  and 1243 (in the separate subgraph-count theorem).
- The error functions satisfy `f_v' > 3 f_2` (line 981), `f_l' > 5 l q^{-1} f_{l+1}`
  (line 995), `f_l' > 2 l C(r-1,l) t^{r-l-1} q^{l-2} f_v` (line 998); at `r = 3` the
  `q^{-1}`/`q` pair cancels and the growth is `f = e^{O(t^2)} = N^{O(zeta^2)}`, which is why
  `zeta^{r-1} << delta` suffices.
- Deviation inequalities: Freedman (line 797) inside the crude bounds; symmetric and
  asymmetric Hoeffding-type (lines 1147, 1152) in the dynamic section. The asymmetric one
  (line 1152) gives `exp(-d^2/(3 m eta N))`, which is **weaker** than Freedman's
  `exp(-d^2/(2(v + Cd)))` by a factor `sqrt(log n)` in our setting.

**On the Freedman direction.** `d^2/(2(v + Cd)) <= d/(2C)` always. `d/(2C)` is therefore a
**ceiling** on the achievable exponent, not a lower bound on it. Session 8 uses it only in
that direction (as a ceiling), and Theorem 2 does not depend on it at all: Theorem 2
lower-bounds the probability of the bad event directly, so it applies whatever inequality is
used.

### Jánosik, et al., *Avoiding configurations of small size in the square grid*
arXiv:2601.14465. Read for the problem statement and the state of the art.

- Best known **lower** bound for the largest isosceles-free subset of `[n]^2`:
  `Omega(n / sqrt(log n))`, by a probabilistic (alteration) argument.
- The linear bound is **conjectured**, and the route is named but not executed:
  *"most probably a linear lower bound can be achieved via the random independent set
  process."* Session 8 is an attempt on exactly that route.

### Croot–Mao–Pohoata–Sheffer–Yip, *A combinatorial large sieve for Sidon sets, distances, and norm forms*
arXiv:2606.17487 (submitted 16 Jun 2026, revised 24 Jun 2026). Abstract and result statement read.

- Gives a new **upper** bound: the largest isosceles-free subset of `[N]^2` has size at most
  `N · exp(-c log N / log log N)`; described as the first progress in over thirty years.
- **It does not touch the lower bound.** The baseline this session must beat is unchanged at
  `Omega(n/sqrt(log n))`.

---

## Consulted, not used as authority

- Bohman–Keevash, *Dynamic concentration of the triangle-free process* — source of the
  "self-correcting" refinement of the differential-equation method. Relevant because it
  removes the `q^{-C}` compounding of tolerances. Session 8's Theorem 2 is proved assuming
  **no** compounding, so self-correction cannot evade it. Statement not opened; not cited for
  anything load-bearing.
- Guo–Warnke, *On the power of random greedy algorithms*, arXiv:2104.07854 — abstract only;
  full text not obtained. Could not confirm or exclude any relaxation of BB's pair
  hypotheses there. **This is the main gap in the novelty check.**
- Warnke, *A gentle introduction to the differential equation method and dynamic
  concentration*, arXiv:2007.01994 — background.
- Rödl–Sárközy–Zhao, *Independence number of hypergraphs under degree conditions* — listed by
  search, not opened.

---

## Novelty assessment

Searched for published work relaxing BB's pair conditions from polynomial (`D^{1/2-eps}`) to
logarithmic slack, and for a negative/barrier result of Theorem 2's shape. Nothing found.

**But this is a negative search result over three queries, not an exhaustive check.** In
particular Guo–Warnke was not read in full. The correct status is:

- Lemma 1: elementary; parts (`max collinear points in a grid`, `r_2(d) = d^{o(1)}`,
  `sum_{d<=X} r_2(d)^2 ≍ X log X`) are classical. `D(H_n) = Theta(n^2 log n)` is very likely
  known or folklore. **No novelty claimed.** The only mildly new framing is that the `log` in
  `D` and the size of `Delta_2` are the same harmonic sum.
- Theorem 2: **novelty PLAUSIBLE, not verified.** It is a barrier specific to `H_n`, of a
  shape (heavy-tailed increment vs. union bound over vertices) that is natural enough that it
  may exist somewhere in the `H`-free-process literature for a different hypergraph.
- Proposition 3: a reduction, not a theorem about `C(n)`. Its components are routine given
  Lemma 1.
