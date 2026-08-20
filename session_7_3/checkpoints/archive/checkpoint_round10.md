# CHECKPOINT — Session 7.3, end of Round 10

Timestamp: 2026-08-20
Current FAR round: 10 (complete) · stage: closed · RUN_CONTROL: RUN
(Round 9 checkpoint archived at `checkpoints/archive/checkpoint_round9.md`.)

## WHAT CHANGED

Round 10 answered the question the Round 9 checkpoint set as the exact next action —
whether `Gamma` enters Bennett-Bohman via a union bound over pairs or via a per-pair
concentration requirement. It is neither, and the answer changes the note's central claim.

Source read: `lit/ind.tex` 690 (definition of `c_{a,a'->k}`), 720 (the stopping time),
768 (`C_{a,a'->k}`), 849 (the induction: "base case following immediately from the
condition on Gamma"), 1015-1029 (the one consumer), 695 and 1172 (limitations).

1. `Gamma(H)` is the maximum over pairs of `c_{r,r->r-1}(v,v',0)` — the `i=0` value of a
   tracked variable, nothing more. It appears at exactly one step of the proof.
2. That induction is DIAGONAL in the pair: each pair's chain is driven only by that pair's
   own variables, so a bad pair's `Gamma` propagates to that pair alone.
3. The only place the chain's output is spent is the drift of `d_l^-(v)`, where the error
   term is a SUM over the pairs sharing an edge with `v`, against a main term
   `~ d_l(v) D^{1/(r-1)}`. The statistic the proof consumes is therefore the EDGE-WEIGHTED
   mean of `Gamma` (and of `Delta_2`), not the maximum.

## NEW VERIFIED FACTS

`experiments/r10_edgeg.c`, `n = 32,48,64,96,128,160,192,256`, 20 apexes (8 for n>=160),
seed 7. Each sampled apex `x` yields `Gamma(x,y)` and `codeg(x,y)` for EVERY `y`.

    Gamma_edge / D          = .0252 .0161 .0120 .0082 .0064 .0054 .0048 .0040   ~ D^-0.396
    Gamma_max  / D          = .1060 .0866 .0734 .0641 .0559 .0515 .0502 .0465
    Delta_2_edge / sqrt(D)  = .227  .174  .147  .115  .097  .085  .077  .067    ~ D^-0.261
    Delta_2_max  / sqrt(D)  = .631  .541  .493  .442  .417  .392  .378  .366
    bias Gamma_edge/Gamma_unif = 1.53 .. 4.93        ( flat against 0.27 sqrt n )

=>  `Gamma_edge ~ D^0.60`   (BB need `< D^{1-eps}`   : holds at eps ~ 0.40)
    `Delta_2_edge ~ D^0.24` (BB need `< D^{1/2-eps}` : holds at eps ~ 0.26)
    Both hold simultaneously at eps ~ 0.26; `D > N^eps` is trivial (`D ~ N log N`).
    The maxima fail for EVERY fixed eps. **The failure is an artefact of the maximum.**

`D` measured at 1.65-1.82 `n^2 ln n` throughout — independently reproduces Round 6's 1.75.

Cross-validation: `r8_gdist.c` (4000 uniform random pairs) and `r10_edgeg.c` (100 apexes x
all 4095 partners), two independently written programs with different algorithms, agree on
the uniform-pair mean of `Gamma` at n=64 to 0.5% — 179.4 vs 178.6.

Risk predicted before running, and survived: the edge measure IS biased toward the
`Gamma`-bad pairs — mirror pairs have long perpendicular bisectors, so they lie in many
edges — and the bias grows like `sqrt(n)`. Averaging wins regardless.

## STATUS CHANGES

- Round 7's "each hypothesis fails by ONE LOGARITHM" is correct but is now known to be the
  wrong comparison. Superseded, not contradicted.
- Route status `BLOCKED`, not `PROGRESS`. No claim about `C(n)` changed.
- Judge PASS 0 · TYPE2 0. Tenth consecutive honest zero on the bound.

## TOP OPEN OBLIGATIONS

1. **Obligation R10.** Replace the pointwise stopping-time conditions (eq:setdegree) and
   (eq:codegree) at line 720 by vertex-aggregated ones and re-derive the drift and Freedman
   estimates at 1015-1060 and 1147-1185. Needs dynamic concentration for a sum of `~D`
   correlated variables, which BB explicitly decline for exactly these variables (line 695:
   "we only need relatively crude upper bounds"). In favour: the union bound shrinks from
   `N^2` pairs to `N` vertices, and there is `eps ~ 0.26` of room instead of none.
2. **Regularity.** `H_n` is not `D`-regular (`Dmax/Davg ~ 1.47`, Round 6). Untouched by
   Round 10 and unexamined by the entire campaign. Likely routine; not verified.
3. Beat the threshold `sqrt(V/mu)` by `sqrt(log n)` (unchanged since Round 5).

## RUNNING PROCESSES

None. No background jobs; `runtime/active_jobs.md` empty. No heavy job left running.

## FILES CREATED OR MODIFIED

    experiments/r10_edgeg.c            new — edge-weighted Gamma / Delta_2 measurement
    experiments/r10_edgeg.exe          /c/msys64/ucrt64/bin/gcc -O2 -o ... -lm
    docs/round10_findings.md           new
    Human_Review/note.html             §5 pointer, §7 rewritten, §8 ledger + closing
    CAMPAIGN_STATE.md                  round 10 block + 4 new DO-NOT-REDO entries
    checkpoints/archive/checkpoint_round9.md   archived
    checkpoints/checkpoint_latest.md   this file

Note republished, same URL and favicon:
https://claude.ai/code/artifact/9320efc0-07a2-42d0-a2db-14cfeb3b1d0c

## EXACT NEXT ACTION

Open. Two candidates, in order of expected value.

(a) **Attempt the separable half of Obligation R10.** The `Delta_2` side may not need
    aggregate concentration at all: at line 1172, `Delta_2` enters as the maximum STEP SIZE
    in the Freedman/Azuma bound for `d_l^+(v)`, not as a drift term. Truncating the
    martingale and bounding separately the probability of ever taking a large step is the
    standard fix for that shape. If it closes, only the `Gamma` side remains.

(b) **Check regularity.** The cheapest of the three gaps and entirely unexamined. Round 6's
    `r6_bb.c` already computes exact degrees; extend it to the full degree profile and test
    whether restricting to a central sub-square, or adding dummy edges, produces a
    `D`-regular hypergraph whose `Gamma` and `Delta_2` are no worse.

## DO NOT REDO

Full list in `CAMPAIGN_STATE.md`. New this round:
- Do not re-derive "fails by one logarithm" and stop there: that compares MAXIMA, and the
  proof consumes AVERAGES. The live obstacle is the stopping time at line 720, not the
  hypergraph's parameters.
- Bash-tool heredocs containing single quotes fail outright; a backslash-n inside a
  heredoc-fed Python string is eaten and becomes a real newline inside C string literals.
  Use Write/Edit for C sources.
- These C sources are CRLF. A multi-line Python `str.replace` keyed on newline silently
  fails to match; read with `newline=''` and key on CRLF, or use Edit.
