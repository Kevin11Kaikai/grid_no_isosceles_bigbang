# CAMPAIGN_STATE — Session 7.3

Campaign: Problem 59 of the AlphaEvolve Repository of Problems = §6.39 of arXiv:2511.02864
(the label "6.59" used by the `iso6` archive is a conflation and finds nothing in search).
Workspace `D:\Others\iso7`. Archive imported from `D:\Others\iso6` (read-only).

Session: 7.3 · FAR round: 12 (complete) - CAMPAIGN CLOSED · Stage: CLOSEOUT (docs/final_closeout.md) · NOTE WRITTEN
Last checkpoint: `checkpoints/checkpoint_latest.md`

## PRIMARY OBJECTIVE
A publishable advance on `C(n)`. **Round 1 did not produce one.**

## WHAT ROUND 1 CHANGED
The target moved from the upper bound to the **lower** bound. `iso6` spent itself on
`O(n^{2-eps})`; arXiv:2601.14465 shows the live question is `C(n) = Omega(n)`, explicitly
open, conjectured true, with a route named but not executed. Read `docs/round1_findings.md`.

## FAR FUNNEL, ROUND 1
raw 4 · checked 4 · probed 4 · KILLED 1 (C001 as stated) · PROGRESS 2 · capped 1 ·
COMPLETE claims 0 · judge-pass 0 · TYPE2 0 · TYPE3 0 · deep attack 0

## CURRENT TOP CANDIDATES
1. **FAR-C004** — the shared-`log n` diagnosis, now **widened by Round 4** from
   probabilistic to recursive methods. The only item with paper potential, as a note.
   Tier B. Not a theorem about `C(n)`.
1b. **FAR-C005** — parity doubling `C(2n) >= 2 C_H(n)`. Correct, verified end-to-end,
   the campaign's only recursive theorem — and self-killed: `rho -> ~1/sqrt 3` so it
   iterates to density 0, and `2 C_H` is below known `C(2n)`. See `docs/round4_findings.md`.
2. **FAR-C002** — one point per column. Verified `n <= 128`; existence for all `n` unproved
   and structurally Costas-like, so possibly a fake reduction.
3. — (nothing else earned promotion)

## CURRENT PAPER CANDIDATE
**WRITTEN.** `Human_Review/note.html` — *"The √log n gap is in the analysis, not in the
truth"*. Organised around the `sqrt(V/mu)` threshold, which DERIVES the known bound; five
blocked method families; the measurement that the process is linear; the three BB
hypotheses that fail, each by one logarithm; and the round-9 evidence that `Gamma`
constrains the analysis rather than the process. Closing section is an explicit ledger of
proved vs measured vs open. Still Tier B: no new bound on `C(n)`.

## BEST COUNTEREXAMPLE / OBSTRUCTION
`Gamma(H_n) = Omega(n^2)` from axis-parallel mirror pairs, against a required `D^{1-eps}`.
It is the cleanest single reason the nibble route does not close.

## TOP OPEN OBLIGATIONS
1. Beat the threshold `sqrt(V/mu)` by a factor `sqrt(mu) = sqrt(log n)`. Round 5 shows
   this is THE obligation and that it cannot be evaded by changing the ambient: `mu` and
   the size of the distance-value range are coupled.
2. Prove one-per-column existence for all `n` (would give `C(n) >= n` outright).
3. A nibble/greedy analysis valid at `Delta_2 ~ D^{1/2}/sqrt(log n)`, i.e. on the boundary
   rather than polynomially inside it.

## BUDGET (7.3 rule §78b)
3 rounds under the old 7.3 rule. **Reopened: the user re-issued the 7.2 master prompt, and 7.2 §58 lists budget exhaustion as a REBRANCH trigger, not a stop condition. 9 rounds used. Still an honest zero on the bound. Round 5 produced the sqrt(V/mu) threshold; round 6 produced the campaign's first POSITIVE evidence — the greedy process beats that threshold and is linear.** If no candidate reaches Judge PASS + Grade TYPE2 by round 3, stop and
write an honest zero. Round 1 outcome argues for stopping early rather than late: the
diagnosis is genuine but it is Tier B, and obligation 1 is a hard analytic-number-theory
gain that this campaign has no tool for.

## COMPUTE PROFILE
20 logical cores, W0 = 4, ceiling ~10. Windows 10 / PowerShell + Git Bash (the 7.2 prompt's
macOS preflight in §52 does not run here). No heavy job left running.

## WHAT ROUND 10 CHANGED

Read the Bennett-Bohman proof itself (`lit/ind.tex` 690/720/768/849/1017). `Gamma` enters
ONLY as the `i=0` value of the tracked variable `c_{r,r->r-1}(v,v')`, per pair, as the base
case of a per-pair induction; and the ONLY consumer of that induction's output is the drift
of `d_l^-(v)`, where the error term is a SUM over the pairs sharing an edge with `v`, not a
maximum. So the statistic the proof needs is the EDGE-WEIGHTED average of `Gamma` (and of
`Delta_2`), not the max. Measured `n=32..256` (`experiments/r10_edgeg.c`):

    Gamma_edge   ~ D^0.60   vs required D^{1-eps}     -> holds with eps ~ 0.40
    Delta_2_edge ~ D^0.24   vs required D^{1/2-eps}   -> holds with eps ~ 0.26

whereas the maxima fail for EVERY fixed eps (`Gamma_max = Theta(D/log D)`,
`Delta_2 = Theta(D^{1/2}/sqrt(log D))`). The edge measure IS biased toward the bad pairs,
by `~0.27 sqrt(n)` (mirror pairs have long bisectors, so they sit in many edges) -- and
averaging wins anyway. See `docs/round10_findings.md`.

**The obstacle is now relocated, not removed.** These conditions define the STOPPING TIME
(line 720): one bad pair halts the process regardless of the aggregate. Obligation R10 is
to replace (eq:setdegree) and (eq:codegree) by vertex-aggregated conditions and re-derive
lines 1015-1060 / 1147-1185. That needs dynamic concentration for a sum of `~D` correlated
variables -- which BB explicitly decline to establish for these variables (line 695). Union
bound shrinks `N^2` pairs -> `N` vertices. NOT established.

## WHAT ROUND 11 CHANGED

**The regularity gap is CLOSED.** Exact degree profile of `H_n` computed for `n <= 160`
(`experiments/r11_reg.c`, O(N^2), exact integer arithmetic, no sampling): `Dmax/Davg =
1.470` with no trend, min always at the corner, max always at the centre. `Davg = 1.66-1.75
n^2 ln n`, independently reproducing round 10's sampled 1.65-1.82.

Regularise UPWARD to `D* = max_v deg(v)` by adding a 3-uniform `R` with
`deg_R(v) = D* - deg(v)`. `H_n u R` is `D*`-regular, an independent set in it is still
isosceles-free (so the bound transfers verbatim), and the cost is `sqrt(1.470) = 1.21`:
BB's conclusion for `H'` is `0.885 n`, still `Omega(n)`. Downward regularisation is not
available -- deleting edges of `H_n` admits non-isosceles-free sets.

`R` does not break the other hypotheses (`experiments/r11_dummy.c`, configuration model,
n=24..64): `Delta_2(R)` mean matches `6|R|/N(N-1)` to 3 decimals and grows like `log N`,
max ~40; `Gamma_R` mean = `1.8 ln^2 n` (flat across the range), max ~70. Against
`Delta_2(H) ~ n` and `Gamma(H) ~ n^2/2` both are lower order. Edge-weighted stats can only
improve (R adds 47% more edges each carrying `Gamma = O(log^2 N)`).

Status `PARTIAL_PROOF`: exact degree realisation, edge-disjointness and the Chernoff bounds
for `R` are routine and not written. See `docs/round11_findings.md` 11.4.

**GAPS: 3 -> 2. Adding `R` does NOTHING for the remaining two** -- they are maxima over
pairs of a subgraph of `H'`. The easy gap is gone; the hard two are where round 10 left
them.

## WHAT ROUND 12 CHANGED - AND WHY THE CAMPAIGN IS CLOSING

**The last route is closed.** Round 11 recommended attacking the `Delta_2` half of
Obligation R10 as the separable one. It does not separate, and two of my own claims were
wrong.

CORRECTION 1: `Delta_2` is not "only a step size". Its dominant role (line 782) is the base
case of `dlemma`'s reverse induction on `b` -- structurally IDENTICAL to `Gamma`'s role at
line 849 -- and its consumer at line 1018 is the same edge-weighted sum. So round 10's
averaging observation applies to it verbatim, with no new gain.

CORRECTION 2: its one extra role, the Azuma step size at line 1172, is NOT repairable by
truncation. The step is `d_{{v,y_i} up l+1}` with `y_i` UNIFORMLY chosen, so it is the
codegree at a random partner, which is why truncation looked available. Criterion forced by
the stopping time: `i_max * E_v[B_v(tau)] << 1` with `i_max ~ 1.07 n`. Measured
(`experiments/r12_tail.c`, n=32..160): the transition sits EXACTLY at `Delta_2max`. Each
vertex has 1.4-2.4 partners AT its maximum codegree (its mirror images), so truncating one
below the max already costs `i_max * Theta(1) = Theta(n)`. **Truncation is viable only at
tau >= Delta_2max, i.e. the original hypothesis.**

Without truncation: Freedman exponent `d/(2C)` with `C = Delta_2max` is short of `log N` by
a FLAT factor ~8 across n=32..192 (8.63, 8.10, 8.19, 8.20, 8.00, 7.90), closing only like
`sqrt(log D)`. Symmetric Azuma with `c_i = Delta_2max` is vacuous (`exponent ~ log n / n`).

CONSEQUENCE: Obligation R10 does not split. Both halves need one thing -- an argument
tolerating a `Theta(1/n)` fraction of bad (vertex, partner) events across `Theta(n)` steps,
which a pointwise stopping time forbids by construction. That is a different proof of
Bennett-Bohman's theorem, not a repair to it.

**The round 11 checkpoint committed in advance: "If it does not close, the campaign has
nothing left that changes any line of the ledger, and should stop." It did not close.
CLOSING OUT.** See `docs/round12_findings.md` and `docs/final_closeout.md`.

## NEXT ACTION
Round 7 settled Round 6's open question: `greedy/n -> positive constant ~0.72-0.84`, so the
process really is `Theta(n)`. And it pinned the obstacle exactly:

    BB requires  Gamma   < D^{1-eps}      H_n has  Gamma   ~ D / log D
    BB requires  Delta_2 < D^{1/2-eps}    H_n has  Delta_2 ~ D^{1/2} / sqrt(log D)

Neither fails polynomially; each fails by ONE LOGARITHM. The well-posed target is a
log-strengthening of Bennett-Bohman Thm 1.1, which alone gives `C(n) = Omega(n)`.
Round 8 then showed the ask is much weaker than round 7 stated: BB's `Gamma` condition
fails on only a `Theta(1/n)` fraction of pairs, and the typical pair beats it by 4-5
orders of magnitude. **The note is WRITTEN**: `Human_Review/note.html`, published at
https://claude.ai/code/artifact/9320efc0-07a2-42d0-a2db-14cfeb3b1d0c
Round 9 added direct evidence to its section 7 and it was republished.

## DO NOT REDO
- Do not recompute `C(n)` for `n <= 32` — known by SAT with proved optimality
  (arXiv:2411.00566). See `KNOWN_RESULTS.md`.
- Do not re-derive the `Z[i]`/square-corner relaxation or the tensor lemma — published
  (arXiv:2607.22828), and the relaxation is lossy.
- Do not re-attempt bounded-direction, bounded-apex, bounded-scale or degree-2-robust
  upper-bound arguments — B1-B8.
- Do not conclude "not found" from a greedy search: at `n=48,64` that answer was an
  artefact; backtracking finds witnesses in seconds. Likewise `onecol2.py` reporting "no"
  at `n=160,192,224` was the 3M-node cap, not nonexistence.
- Do not re-attempt dilation / self-similar constructions. Round 4: only powers of 2
  preserve the class count, and even they pay a constant `~1/sqrt 3` per step.
- Do not use a doubling offset larger than `(+-1,+-1)`: it overflows `[2n]^2`.
- Do not re-attempt arithmetic quotients (mod `p`, finite fields, norm circles) to flatten
  `r_2`. Round 5: the quotient collapses the distance-value range faster than it flattens
  the multiplicity, and caps the construction at `~2.7 sqrt(p)`.
- Do not re-test monomial graphs, norm circles, or Welch/Costas maps over `F_p`: all
  measured, none close to isosceles-free.
- Do not re-argue that greedy might be `n/sqrt(log n)`: measured to `n=8192`, excluded.
- Do not re-fit `greedy/n` with a power-of-log model: the theory-derived form
  `gamma^2 = A + B lnln n/ln n + C/ln n` beats it in-sample AND out-of-sample (r7_fit.py).
- Round 6's `n=64` greedy value 71.0 rested on 3 seeds and was HIGH; 20 seeds give 68.00.
- Round 1's `Gamma`-extremal pair (axis-parallel) is not the maximiser: the DIAGONAL pair
  is larger for all `n >= 16`. Mechanism was right, maximiser was not.
- Do not claim only the 4 lattice-reflection directions give `Gamma = Theta(n^2)`: REFUTED,
  `(2,1)` gives `Gamma/n^2 = 0.082` at both n=64 and n=128. The bad set is short-primitive-
  direction pairs; the 4 reflection families are only the extremal ones.
- `H_n` is NOT `D`-regular (`Dmax/Davg ~ 1.47`), which BB Thm 1.1 requires. Do not conflate
  centre degree (`D/(n^2 ln n) ~ 2.57`) with average degree (`~1.75`).
- MinGW/Windows: `sizeof(long) == 4`, not 8. Passing 8 to `qsort` silently scrambles the
  array (symptom: max=0 alongside a nonzero mean). Use `long long`/`sizeof`.
- Do not patch C sources with index-based Python `str.replace`: it corrupted r8_gdist.c and
  burned a 10-minute timeout on gcc error output. Rewrite the file instead.
- Do not quote Round 2's constant `0.78` for the free greedy process: it was measured for
  the ONE-PER-COLUMN restricted process. The free process gives `~1.01-1.11 n`.
- Do not launch background jobs with `nohup ... &` inside a run_in_background call: the
  harness reports exit 0 for the launcher and the redirect file stays empty. Run plainly.
- Do not re-derive that `Gamma`/`Delta_2` fail BB's hypotheses "by one logarithm" and stop
  there: round 10 shows that comparison uses the MAX, and the proof consumes an EDGE-
  WEIGHTED AVERAGE, under which both hold with eps ~ 0.26. The live obstacle is the
  STOPPING TIME (lit/ind.tex line 720), not the hypergraph's parameters.
- Do not use a heredoc containing single quotes in the Bash tool: the wrapper breaks on
  them. And a backslash-n inside a heredoc-fed Python string is eaten -- it produced a
  literal newline inside a C string literal. Use Write/Edit for C sources.
- These C sources and CAMPAIGN_STATE.md are CRLF. A multi-line Python `str.replace` keyed
  on newline silently fails to match. Read with `newline=''` and key on CRLF, or use Edit.
- Do not re-open regularity: `Dmax/Davg = 1.470` exactly (n<=160), upward regularisation
  costs only `sqrt(1.470)`, and it does NOT help `Gamma` or `Delta_2` -- both are maxima
  over pairs of a subgraph of `H'`. Do not regularise downward (admits bad sets). Do not
  chase `Dmax/Dmin` asymptotics: the argument uses only `Dmax`.
