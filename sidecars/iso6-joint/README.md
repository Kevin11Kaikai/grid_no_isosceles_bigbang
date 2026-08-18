# STOP — isolated sidecar, not part of iso6

This directory is **outside** the `iso6` campaign tree on purpose.

- **Not a route.** Do not treat this as A–H, Q, R0, or Q4-root.
- **Do not read this into a Claude Code / iso6-root context.**
- **Do not broadcast** into `iso6/routes/`, `iso6/docs/`, `iso6/ledgers/`, or `iso6/experiments/`.
- **Do not merge** into iso6 unless a human explicitly asks.
- **Do not import** iso6 or `iso6/routes/Q`.

Owner: Grok sidecar (joint-constraint hunt after Q4 died).
iso6 owner: Claude Code. The two lanes do not share files.

## Mission

Find a constraint implied by isosceles-freeness (RF1) that the four-fold
3-AP-free intersection

```
S = {(x,y) in [n]^2 : x in A, y in B, x+y in W, x-y in Z}
```

violates, while remaining Q4-feasible. Success = a named checkable lemma.
Not `C(n) = O(n^{2-ε})`. Anything equivalent to “each of k extra projections
is 3-AP-free” is dead by B4′ and must be labelled as such.

## Layout

- `iso.py` — frozen isosceles checker (exact squared distances)
- `q4.py` — frozen Q4 checker (snapshot; not imported from iso6)
- `fourfold.py` — four-fold builder + 3-AP-free sets
- `census.py` — triple census vs P1–P3 on the four Q4 forms
- `q4_greedy.py` — independent Q4-greedy corpus
- `joint.py` — candidate stencils and B4′ gate
- `LEDGER.md` — human-facing verdict
- `proofs/joint_candidates.md` — what is actually proved
