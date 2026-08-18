# STOP — isolated sidecar, not part of iso6

This directory is **outside** the `iso6` campaign tree on purpose.

- **Not a route.** Do not treat this as A–H, R0, or Q4-root.
- **Do not read this into a Claude Code / iso6-root context.**
- **Do not broadcast** anything here into `iso6/routes/A`–`H`, `iso6/docs/`, `iso6/ledgers/`, or `iso6/experiments/`.
- **Do not merge** into iso6 unless a human explicitly asks.

Owner: Grok sidecar (Q4 falsification only).
iso6 owner: Claude Code. The two lanes do not share files.

## What this lane does

Continue open question 1 from iso6 `docs/Q4_route.md`, without editing that file:

> Does there exist an algebraic construction of Q4-feasible sets of size
> `n^{2-o(1)}`, or even `n^{1+c}`?

This lane's construction battery did **not** find the four-fold Behrend
intersection that iso6 used to falsify Q4. Failure to find a construction
here was not a proof that Q4 is safe. The route is now dead in iso6;
this sidecar stops. Do not merge.

## Protocol after Claude Code quota resets

- Grok stays in `iso6-q4f` only.
- Claude Code stays in `iso6` (`docs/`, `proofs/`, `ledgers/`, `experiments/`, `routes/`).
- A superlinear Q4-feasible construction is recorded **only** in `LEDGER.md` here. It is not written into `iso6/docs/Q4_route.md`. Tell the human; they decide whether to hand it to Claude.
- Failure to find a construction is **not** a proof that Q4 is safe. Do not claim that.

## Kill / fail lines (this ledger only)

- **Q4 dies:** some construction, on a stretch of `n`, gives `|S| >= n^{1.1}` (or a clear `n^{1+c}`) and `verify()` passes.
- **Ammunition fails:** that family repairs down to `O(n)` or `n^{1+o(1)}`. Failure of a family is not a safety proof.
- **Gap:** exact `Q4(n)` for small `n` sits clearly above the greedy `~1.8n` pattern.

## Layout

- `q4.py` — frozen Q4 checker (copied from an iso6 snapshot; not imported, not kept in sync)
- `exact.py` — small-`n` exact / timed search
- `construct.py` — algebraic construction battery
- `LEDGER.md` — results for this lane
- `out/` — raw tables and point sets
