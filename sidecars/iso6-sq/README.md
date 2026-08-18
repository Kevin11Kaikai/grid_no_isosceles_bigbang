# STOP — isolated sidecar, not part of iso6

This directory is **outside** the `iso6` campaign tree on purpose.

- **Not a route.** Do not treat this as A–H, Q, R0, Q4-root, or J1-root.
- **Do not read this into a Claude Code / iso6-root context.**
- **Do not broadcast** into `iso6/routes/`, `iso6/docs/`, `iso6/ledgers/`, or `iso6/experiments/`.
- **Do not merge** into iso6 unless a human explicitly asks.
- **Do not import** iso6, `iso6/routes/Q`, `iso6-q4f`, or `iso6-joint`.

Owner: Grok sidecar (Q_SQ falsification after J1 / square-corner).
iso6 owner: Claude Code. The two lanes do not share files.

`iso6-joint` is frozen (J1 named). `iso6-q4f` is frozen (Q4 dead). This lane does not continue either.

## Mission

Falsify-first the square-corner relaxation

```
Q_SQ(n) = max |S|  over S subset [n]^2 with no square-corner
```

A square-corner is `{b, b+w, b+R(w)}` with `R = ±90°`, `w ≠ 0`.

Success = a verified superlinear / `n^{1+c}` / `n^{2-o(1)}` square-corner-free
construction, **or** an honest “ammunition failed, not a safety proof”.
Not `C(n) = O(n^{2-ε})`. Do not mark PROMISING from greedy. Do not start
an upper-bound proof in this lane.

## Layout

- `sq.py` — frozen square-corner checker (exact integer arithmetic)
- `iso.py` — tiny isosceles checker (sanity: iso-free ⇒ sq-free)
- `construct.py` — construction battery
- `run_all.py` — negative controls + battery
- `LEDGER.md` — human-facing verdict
- `proofs/qsq_battery.md` — what was actually run
