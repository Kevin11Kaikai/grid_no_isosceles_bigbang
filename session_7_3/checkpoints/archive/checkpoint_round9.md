# CHECKPOINT — Session 7.3, end of Round 9

Timestamp: 2026-08-20
Current FAR round: 9 (complete) · stage: closed · THE NOTE IS WRITTEN

## WHAT CHANGED
1. The Tier-B note was written and published (the standing editorial item since round 3).
2. Round 9 tested the question the note ends on, and the answer supports it.

## THE DELIVERABLE
`Human_Review/note.html` -> https://claude.ai/code/artifact/9320efc0-07a2-42d0-a2db-14cfeb3b1d0c
Sections: the problem; the `sqrt(V/mu)` threshold that derives the known bound; five
blocked method families; the measurement that random greedy is linear; the three failing
BB hypotheses; the rarity of the `Gamma` failure; the question; an explicit
proved/measured/open ledger. Republished after round 9 with the new evidence in section 7.

## NEW VERIFIED FACTS (round 9)
1. **`Gamma` isolated does not affect the process.** Matched-control design: same `D`, same
   `Delta_2`, same edge count and codegree structure; only `Gamma` differs. Over 3 seeds,
   treat/control = 1.0000, 0.9951, 1.0094, 1.0236 for `Gamma/D` = 0, .07, .23, .33.
2. **The bad-pair fraction does not matter either.** At fixed budget `P*H = 60`, trading
   `Gamma` (0.30D -> 0.01D) against bad fraction (1/N -> 60/N) leaves `|I|` flat ~7100 and
   ratios within 0.995-1.014.
3. **Rarity is forced:** `Sum_{v'} Gamma(v,v') <= D(Delta_2-1)`, so
   `#{v' : Gamma >= T} <= D*Delta_2/T`; for `H_n` that is `Theta(log n / n)`. Round 8's
   measured `Theta(1/n)` follows from `Delta_2` being small, not from the lattice.
4. `Gamma ~ D/log D` exceeds `D^{1-eps}` only when `D^eps > log D`, i.e. `D ~ 10^20` for
   `eps=0.1`. **The real regime is untestable at any feasible size**; `Gamma = Theta(D)` is
   a proxy, and a harder test than the real one.

## CORRECTION MADE THIS ROUND
The first synthetic design (`r9_synth.c`) was confounded: raising the bad-pair fraction also
raised `Delta_2` to the group size, making the hypergraph less constraining. That is why
`|I|/BB` appeared to RISE 0.594 -> 0.843. It measured `Delta_2`, not `Gamma`. Superseded by
the matched control in `r9_ctrl.c`.

## WHAT ROUND 9 DOES NOT SHOW
BB need `Gamma` small for CONCENTRATION of tracked quantities; this measures only the final
`|I|`, a mean. A robust mean is compatible with unruly fluctuations. And synthetic
hypergraphs mimic `H_n`'s parameters, not its lattice-reflection structure.

## TOP OPEN OBLIGATIONS
1. A Bennett-Bohman variant tolerating `Delta_2 = O(D^{1/2}/sqrt(log D))`, constant-factor
   irregularity, and a `Theta(N^{-1/2})` fraction of pairs with `Gamma = Theta(D/log D)`.
   This is now the only route the campaign has evidence for. Requires reading their proof.
2. FAR-C002 one-per-column existence for all `n` (verified `n <= 128`).

## ACTIVE LOCAL JOBS
None.

## RESOURCE HEALTH
Fine. Single-threaded probes, < 1 GB.

## DEFERRED HEAVY COMPUTE
- `Gamma` maximised over all `~n^4` pairs; `r6_greedy` at `n = 16384`; exact `A(p)` for
  `p >= 13`; FAR-C002 at `n >= 160` with an `n`-scaled cap. None has a claim riding on it.

## FILES MODIFIED
Human_Review/note.html (new, published); docs/round9_findings.md (new);
experiments/r9_synth.c, r9_ctrl.c, r9_frac.c + .exe (new); CAMPAIGN_STATE.md; this file.

## EXACT NEXT ACTION
Open. The note is delivered. The only mathematical route left needs a close reading of
arXiv:1308.3732's proof to see whether `Gamma` enters via a union bound over pairs (in
which case a vanishing bad fraction is tolerable) or via a per-pair concentration
requirement (in which case it is not). `lit/ind.tex` line 849 is the entry point.

## DO NOT REDO
- Synthetic `Gamma` experiments without a matched control: raising `Gamma` by grouping
  raises `Delta_2` too and the result is meaningless.
- Trying to test `Gamma ~ D/log D` vs `D^{1-eps}` numerically — untestable below `D~10^20`.
- MinGW `sizeof(long)==4`; index-based Python patching of C sources; `nohup ... &` inside
  run_in_background; `%Lf` under MinGW printf.
