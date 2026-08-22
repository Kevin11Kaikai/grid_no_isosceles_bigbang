# Checkpoint — Session 8

**Branch:** `session-8-opus5-averaged-stopping`, cut from `session-7.3-far-cascade`.
All new work under `session_8_opus5/`. Nothing outside it modified. Master untouched.
Pre-existing uncommitted work in `long_horizon_run_*` and `ROUND3_TOURNAMENT/` left alone.

**Verdict:** `NEW_INTERMEDIATE_GRID_THEOREM` — see `README.md`.

---

## State

| file | what it holds |
|---|---|
| `THEOREM_CONTRACT.md` | process, filtration, stopping time, the exceptional statistic, quantifiers, bridge to `C(n)` |
| `THEOREM_AND_PROOF.md` | Part I audit of ind.tex at `r=3`; Part II Lemma 1; Part III Theorem 2 + Cor 2.1; Part IV Proposition 3 |
| `ATTACK_LOG.md` | A1 (first candidate refuted), A4 (second candidate, expectation/probability gap), A5 (six rescues, each refuted), A6 (falsification), A7 (what survives) |
| `LITERATURE_NOTES.md` | BB Thm 1.1 verbatim + line map; Jánosik baseline; CMPSY 2026 is an **upper** bound only |
| `CLAIM_REGISTRY.md` | every claim labelled PROVED / CONDITIONAL / EMPIRICAL / FALSIFIED / OPEN |
| `HANDOFF.md` | obligation (Q), plus (H-surv) |
| `experiments/s8_tail.c` | exact `codeg(v,·)` law; checks Lemma 1(a),(c),(d) |
| `experiments/s8_proc.c` | runs the actual process; checks Theorem 2's prediction and (H-surv) |

No `paper/` directory: no complete novel theorem with a grid application survived, so no
paper-shaped material was produced.

## Reproduce

```
cd session_8_opus5/experiments
gcc -O2 -o s8_tail s8_tail.c -lm && ./s8_tail 512 1
gcc -O2 -o s8_proc s8_proc.c -lm && ./s8_proc 256 50 1
```
Runtimes: seconds to ~1 min. `s8_tail 512` is the slowest.

## Key numbers to re-derive if resuming

- `Delta_2(H_n) = n(1+o(1))`, `D(H_n) = Theta(n^2 log n)`, so `D^{1/2}/Delta_2 = Theta(sqrt(log n))`.
- Jump budget for pointwise `d_2`: `g <= sigma sqrt(log n)` with `sigma = o(1)`.
- Union-bound requirement: `g log(g/mu) >= log N = 2 log n`, with `log(g/mu) = Theta(log log n)`.
- Deficit: `sqrt(log n) / log log n`.
- Horizon at which it binds: `t = Theta(1)`, i.e. `m = Theta(n/sqrt(log n))` — the alteration
  threshold. Nothing beyond it is reachable pointwise.

## Exact next action

Attack obligation (Q) of `HANDOFF.md` by route 1 (the line-counting decomposition), using
the primitive-direction census already set up in the proof of Lemma 1(c): at scale `s` there
are `Theta(s)` primitive directions and `Theta(n/s)` lattice points per line, so a fixed
vertex meets `Theta(s)` lines of scale `s` while `Theta(n s)` vertices are reachable at that
scale. The claim to prove is that this `1/n` ratio, summed over scales, bounds the bias of
`v`'s 2-neighbourhood towards the exceptional set.

Do **not** open a new candidate theorem before (Q) is settled — the contract's two-revision
budget is spent.
