# CHECKPOINT — Session 7.3, end of Round 11

Timestamp: 2026-08-20
Current FAR round: 11 (complete) · stage: closed · RUN_CONTROL: RUN
(Rounds 9 and 10 archived at `checkpoints/archive/checkpoint_round9.md`, `_round10.md`.)

## WHAT CHANGED

Round 11 did one thing, the one recommended at the end of Round 10 as the cheapest of the
three remaining gaps: **check regularity.** It closes.

This is the first round in eleven that REMOVES an obstacle rather than diagnosing one.
It is also the easy one, and it does nothing for the other two.

## NEW VERIFIED FACTS

### Exact degree profile — `experiments/r11_reg.c`, O(N^2), exact, no sampling

Every edge of `H_n` has a unique apex (two apexes force an equilateral triangle; `Z^2` has
none), so `deg(a) = #{{b,c}: |ab|=|ac|} + sum_{x!=a}(N_x(|xa|^2)-1)`, and both terms come
out of one loop over the apex.

    n        16      24      32      48      64      96      128     160
    Davg/(n^2 ln n)  1.6629  1.6884  1.7025  1.7190  1.7287  1.7400  1.7468  1.7515
    Dmax/Davg        1.4623  1.4703  1.4674  1.4739  1.4733  1.4703  1.4702  1.4686
    Dmax/Dmin        2.256   2.378   2.410   2.503   2.530   2.588   2.617   2.643
    Dmin/Davg        0.648   0.618   0.609   0.589   0.582   0.568   0.562   0.556

`Dmax/Davg = 1.470`, flat over a 10-fold range — confirms Round 6's 1.47 exactly.
Min always at the corner (0,0), max always at the centre. `Dmax/Dmin` still creeping;
whether it is bounded is NOT settled and DOES NOT MATTER — the argument uses only `Dmax`.
`Davg` independently reproduces Round 10's sampled `1.65-1.82 n^2 ln n`.

### Lemma R11 (regularisation) — `PARTIAL_PROOF`

Let `D* = max_v deg(v)`; let `R` be 3-uniform on `[n]^2`, edge-disjoint from `H_n`, with
`deg_R(v) = D* - deg_{H_n}(v)`; set `H' = H_n u R`. Then `H'` is `D*`-regular and every
independent set of `H'` is isosceles-free (it contains no edge of `H_n`), so any lower
bound for `H'` transfers to `C(n)` verbatim. Cost: with `D* = 2.55 n^2 ln n`, `N = n^2`,

    N (log N / D*)^{1/2} = n^2 (2 ln n / 2.55 n^2 ln n)^{1/2} = 0.885 n     still Omega(n)

i.e. exactly `sqrt(Dmax/Davg) = sqrt(1.470) = 1.21`. Downward regularisation is NOT
available: deleting edges of `H_n` admits non-isosceles-free sets.

### R does not break the other hypotheses — `experiments/r11_dummy.c`

Configuration model on the deficiency degrees, independent of the lattice:

    n           24     32     48     64
    |R|/|E|     .470   .467   .474   .473
    D2(R) max   27     31     40     40        D2(R) mean 5.03 5.51 6.30 6.80
    Gamma_R mean 17.4  20.9   27.9   32.4      / ln^2 n = 1.72 1.74 1.86 1.87  (flat)
    vs H_n:     D2 ~ n = 24..64                Gamma ~ n^2/2 = 288..2048

`D2(R)` mean matches `6|R|/N(N-1)` to three decimals and grows like `log N`; max ~6x mean
(Poisson tail over `N^2` pairs). `Gamma_R = Theta(log^2 N)`. Hence
`Delta_2(H') <= Delta_2(H_n) + O(log N)` and `Gamma(H') <= Gamma(H_n) + O(log^2 N)`, both
unchanged to leading order; and the Round 10 edge-weighted statistics can only fall, since
`R` adds 47% more edges each carrying `Gamma = O(log^2 N)`.

CAVEAT worth keeping visible: at `n = 64`, `Delta_2(R) = 40` against `Delta_2(H_n) ~ 84`.
The separation is a statement about growth rates, not about accessible `n`.

## NOT DONE (all routine, none deep) — see `docs/round11_findings.md` 11.4

1. Configuration model yields triples with a repeated vertex (0.5-0.6%), discarded here,
   perturbing degrees slightly. Exact degree realisation + switching not written.
2. Edge-disjointness from `H_n` not enforced (`|H_n|/C(N,3) ~ 3.5 ln n/n^2 -> 0`).
3. `Delta_2(R)`, `Gamma_R` bounds are MEASURED, not proved (standard Chernoff/Poisson).

## STATUS CHANGES

    gap                              status
    D-regularity                     CLOSED, cost sqrt(1.470) = 1.21
    Gamma < D^{1-eps}   pointwise    fails; holds edge-weighted at eps ~ 0.40
    Delta_2 < D^{1/2-eps} pointwise  fails; holds edge-weighted at eps ~ 0.26

Judge PASS 0 · TYPE2 0. Eleventh consecutive honest zero on the bound.

## TOP OPEN OBLIGATIONS

1. **Obligation R10** (unchanged, and now the ONLY structural one): replace the pointwise
   stopping-time conditions (eq:setdegree) and (eq:codegree) at `lit/ind.tex` line 720 by
   vertex-aggregated ones and re-derive lines 1015-1060 / 1147-1185. Needs dynamic
   concentration for a sum of `~D` correlated variables, which BB decline for exactly these
   variables (line 695). Union bound shrinks `N^2` pairs -> `N` vertices; `eps ~ 0.26` room.
2. Beat the threshold `sqrt(V/mu)` by `sqrt(log n)` (unchanged since Round 5).

## RUNNING PROCESSES

None. No background jobs; `runtime/active_jobs.md` empty.

## FILES CREATED OR MODIFIED

    experiments/r11_reg.c    r11_reg.exe      new — exact degree profile
    experiments/r11_dummy.c  r11_dummy.exe    new — regularisation cost check
    docs/round11_findings.md                  new
    Human_Review/note.html                    §5 regularity row, new §7.1, §8 ledger, closing
    CAMPAIGN_STATE.md                         round 11 block
    checkpoints/archive/checkpoint_round10.md archived
    checkpoints/checkpoint_latest.md          this file

Note republished, same URL and favicon:
https://claude.ai/code/artifact/9320efc0-07a2-42d0-a2db-14cfeb3b1d0c

## EXACT NEXT ACTION

The remaining route is Obligation R10 and nothing else. It is analysis, not computation:
attempt the `Delta_2` half first, where at `ind.tex` line 1172 `Delta_2` enters as the
maximum STEP SIZE in the Freedman/Azuma bound for `d_l^+(v)` rather than as a drift term.
Truncating the martingale and bounding separately the probability of ever taking a large
step is the standard repair for that shape; if it closes, only the `Gamma` half remains.

Note that this was ranked (a) at the end of Round 10 and deferred in favour of (b). It is
real research-level work with a real chance of not closing, and no further probe, sweep or
synthetic hypergraph will substitute for it. If it does not close, the campaign has nothing
left that changes any line of the ledger, and should stop.

## DO NOT REDO

Full list in `CAMPAIGN_STATE.md`. New this round:
- Do not re-open regularity. `Dmax/Davg = 1.470` exactly, upward regularisation is free up
  to `sqrt(1.470)`, and it does NOT help `Gamma` or `Delta_2` (both are maxima over pairs of
  a subgraph of `H'`).
- Do not compute `Dmax/Dmin` asymptotics: irrelevant, the argument uses only `Dmax`.
- Do not regularise downward: deleting edges of `H_n` admits non-isosceles-free sets.
