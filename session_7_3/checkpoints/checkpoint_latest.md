# CHECKPOINT — Session 7.3, end of Round 12 · CAMPAIGN CLOSED

Timestamp: 2026-08-20
Current FAR round: 12 (complete) · stage: CLOSEOUT · RUN_CONTROL: RUN
(Rounds 9, 10, 11 archived under `checkpoints/archive/`.)

**This campaign is closed. Do not reopen it to run more probes.**
Read `docs/final_closeout.md` first, then `CAMPAIGN_STATE.md` for the DO-NOT-REDO list.

## WHAT ROUND 12 DID

Attacked the route Round 11 recommended — the `Δ₂` half of Obligation R10, as the separable
one. It does not separate. Two of my own claims are corrected.

**Correction 1 — `Δ₂` is not "only a step size".** The Round 11 checkpoint asserted that;
it was a guess written without auditing the other uses. Auditing all of them
(`lit/ind.tex` 782, 811, 846, 1018, 1172): the dominant role is line 782, the base case of
`dlemma`'s reverse induction on `b`, which is **structurally identical to `Γ`'s role** at
line 849 — `i = 0` value of a tracked variable, induction diagonal in `A`, consumed at line
1018 by the same edge-weighted sum. Round 10's averaging observation therefore applies to
`Δ₂` verbatim, and yields nothing new.

**Correction 2 — truncation does not repair line 1172.** The step of `Z_ℓ^+(v)` is
`d_{{v,y_i}↑ℓ+1}` with `y_i` drawn **uniformly** from `V(i)` — the codegree at a random
partner, not a maximum. That is what made truncation look available. The criterion forced
by the stopping time (which halts on the first vertex to fail) is

    sum_v P(v ever steps > tau)  ~  i_max * E_v[B_v(tau)]  <<  1,
    B_v(tau) = #{y : codeg(v,y) > tau},   i_max ~ 1.07 n for H_n.

## NEW VERIFIED FACTS — `experiments/r12_tail.c`, n = 32..192, 30-40 apexes, seed 777

`i_max · E_v[B_v(τ)]`, with `τ` in units of `√D`:

    tau/sqrtD    0.80   0.65    0.55   0.50   0.40    0.30    0.20
    n=32            0    7.9     106    175   1575    3528    8669
    n=64            0      0       0      0   2412    8100   1.6e4
    n=128           0      0       0      0    838   2.8e4   4.2e4

**The transition sits exactly at `Δ₂max`** (`Δ₂max/√D` = 0.622, 0.487, 0.422 for
n = 32, 64, 128). There is no intermediate regime.

    n                              32     64     96    128    160
    partners AT the per-vertex max 1.43   2.43   2.10   2.10   1.50
    within 90% of the max          4.2   11.7   28.4   48.3   70.2
    i_max * (partners at max)     49.6    167    226    300    256
      in units of n               1.55   2.62   2.35   2.34   1.60

Each vertex has `Θ(1)` partners *at* its maximum codegree — its mirror images, the same
structured family Rounds 1 and 8 found for `Γ`. Truncating one below the max already costs
`Θ(n)` against a requirement of `≪ 1`. **Truncation is viable only at `τ ≥ Δ₂max`, i.e. the
original hypothesis.**

Without truncation, Freedman's exponent `d/(2C)` with `C = Δ₂max`, against the `log N` a
union bound over the `N` vertices needs:

    n            32     64     96    128    160    192
    d/(2C)      0.804  1.026  1.114  1.184  1.269  1.331
    log N       6.93   8.32   9.13   9.70  10.15  10.52
    short by    8.63   8.10   8.19   8.20   8.00   7.90     <- flat, closes like sqrt(log D)

Symmetric Azuma with `c_i = Δ₂max` for every step is vacuous: `Σc_i² = i_max Δ₂max² ≍ n³`
against `d² ≍ n² log n`, exponent `≍ log n / n → 0`.

## CONSEQUENCE

**Obligation R10 does not split.** Both halves reduce to one thing:

> an argument tolerating a `Θ(1/n)` fraction of bad `(vertex, partner)` events across
> `Θ(n)` steps, which a pointwise stopping time forbids by construction.

That is a different proof of Bennett-Bohman's theorem, not a repair to it. It is a research
problem in probabilistic combinatorics and nothing in this campaign bears on it.

Judge PASS 0 · TYPE2 0. **Twelfth consecutive honest zero on the bound.**

## WHY THE CAMPAIGN IS CLOSING

The Round 11 checkpoint committed to this in advance:

> If it does not close, the campaign has nothing left that changes any line of the ledger,
> and should stop.

It did not close. Closing out per that commitment, not because a budget expired.

## RUNNING PROCESSES

None. No background jobs; `runtime/active_jobs.md` empty.

## FILES CREATED OR MODIFIED

    experiments/r12_tail.c  r12_tail.exe   new — codegree tail, truncation criterion
    docs/round12_findings.md               new
    docs/final_closeout.md                 new (§79)
    Human_Review/note.html                 §7 extended, §8 ledger + closing
    CAMPAIGN_STATE.md                      round 12 block, header marked CAMPAIGN CLOSED
    checkpoints/archive/checkpoint_round11.md   archived
    checkpoints/checkpoint_latest.md       this file

Note republished, same URL and favicon:
https://claude.ai/code/artifact/9320efc0-07a2-42d0-a2db-14cfeb3b1d0c

Mirrored to `Kevin11Kaikai/grid_no_isosceles_bigbang`, branch `session-7.3-far-cascade`,
directory `session_7_3/` (PR #2, deliberately NOT merged to master).

## EXACT NEXT ACTION

**None. Do not reopen for further probes.** If the remaining obligation is ever attacked,
the entry points in `lit/ind.tex` are: 720 (the stopping time), 782 and 849 (the two base
cases), 1015-1029 (the drift consumer), 1172 (the step size).

## DO NOT REDO

Full list in `CAMPAIGN_STATE.md`. New this round:
- Do not attempt to separate the `Δ₂` half of Obligation R10: `Δ₂`'s dominant role is
  identical to `Γ`'s (line 782 vs 849), so averaging gains nothing new there.
- Do not attempt truncation of the line-1172 Azuma step: viable only at `τ ≥ Δ₂max`, which
  is the original hypothesis. Fails by `Θ(n)` at any lower `τ`, because every vertex has
  `Θ(1)` partners at its maximum codegree and the process runs `Θ(n)` steps.
- Do not try symmetric Azuma with the worst-case step: the bound is vacuous.
- Do not write a checkpoint claim about how a proof uses a quantity without auditing every
  occurrence first. The Round 11 "only a step size" claim was wrong and cost a round.
