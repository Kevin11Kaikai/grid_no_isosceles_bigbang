# Q4 is FALSIFIED as a route to a power saving

`VERIFIED_THEOREM` (for the mechanism class). Novelty: NOVELTY_UNASSESSED.

Result: **`Q4(n) ≥ (1/64)·r_3(n)^4/n^2 = n^{2-o(1)}`.** Hence no upper bound derived from the
four-direction line-kill relaxation alone can prove `C(n) = O(n^{2-ε})`.

This kills the campaign's strongest lead. It was obtained by falsification-first policy, at a
small fraction of the cost of the proof attempt it pre-empted.

---

## Recap of Q4

For `S ⊆ [n]^2` let `U_col, U_row, U_dia, U_ant` be the occupied `x`, `y`, `x-y`, `x+y`
values, `X_y` / `Y_x` / `A_d` / `D_a` the fibres, and `M(A)` the same-parity midpoints of
distinct pairs. Q4 is:

  (1) `M(X_y) ∩ U_col = ∅`  (2) `M(Y_x) ∩ U_row = ∅`
  (3) `M(A_d) ∩ U_ant = ∅`  (4) `M(D_a) ∩ U_dia = ∅`

Q4 is implied by isosceles-freeness (each constraint is an instance of L2b), so
`C(n) ≤ Q4(n)`.

---

## Lemma (Sufficiency)

Let `A, B ⊆ [0,n)` and `W, Z ⊆ Z` be **3-AP-free**. Then

    S = { (x,y) ∈ [n]^2 : x ∈ A, y ∈ B, x+y ∈ W, x-y ∈ Z }

satisfies all four Q4 constraints.

*Proof.* For a set `A`, `M(A) ∩ A = ∅` is exactly 3-AP-freeness (the midpoint of `a` and
`a+2d` is `a+d`). Now `U_col ⊆ A`, and for every row `y` we have `X_y ⊆ A`, hence
`M(X_y) ⊆ M(A)`, so `M(X_y) ∩ U_col ⊆ M(A) ∩ A = ∅`. That is (1); (2) is identical with `B`.
For (3), `U_ant ⊆ W` and `A_d ⊆ W` for every diagonal `d` (the `x+y` values on a diagonal all
have equal parity, so midpoints are integers), giving `M(A_d) ∩ U_ant ⊆ M(W) ∩ W = ∅`.
(4) is identical with `Z`. ∎

Verified computationally: 143 non-empty sets of this form at `n = 9,16,27,40`, checked by an
**independently written** Q4 verifier — **0 violations** (`experiments/q4_barrier_proof.py`).

## Lemma (Averaging)

Fix 3-AP-free `T ⊆ [0,n)` and `T' ⊆ [0,2n)`, `t = |T|`, `t' = |T'|`. For shifts
`(a,b,w,z)` put `A = T+a`, `B = T+b`, `W = T'+w`, `Z = T'+z` — all 3-AP-free. Over the boxes

    a, b ∈ [-(n-1), n-1],   w ∈ [-(2n-1), 2n-2],   z ∈ [-(3n-2), n-1]

(which contain **every** admissible shift), the counting identity

    Σ_{(a,b,w,z)} |S(a,b,w,z)|  =  n^2 · t^2 · t'^2

holds, because each of the `n^2` points `(x,y)` is counted once for each of the `t` shifts
`a = x - τ` (`τ ∈ T`), the `t` shifts `b`, the `t'` shifts `w`, and the `t'` shifts `z`.

The box has `(2n-1)^2 (4n-2)^2 ≤ 64 n^4` elements, so some shift tuple attains

    |S| ≥ n^2 t^2 t'^2 / (64 n^4) = t^2 t'^2 / (64 n^2).

*Verification.* Identity confirmed exactly — per-point count and full brute-force sum over
the entire shift box agree with `n^2 t^2 t'^2` at `n = 5` (10000) and `n = 6` (20736), and the
per-point count matches at `n = 7, 9`. **The ranges matter:** an earlier version clipped the
`z` box and the identity failed by ~8%; `z` must run down to `-(3n-2)`.

## Theorem

Taking `T, T'` to be Behrend sets, `t = r_3(n) ≥ n·exp(-C√(log n))` and `t' = r_3(2n) ≥ t`:

    Q4(n) ≥ r_3(n)^4 / (64 n^2) ≥ (1/64) · n^2 · exp(-4C√(log n)) = n^{2-o(1)}.  ∎

---

## Why this is decisive

Q4 was adopted precisely because it **escaped barrier B3** — the Behrend product `B × B`
satisfies the axis-only constraints but violates the diagonal constraint at every diagonal
pair. That remains true. But it only meant the *specific* B3 construction failed; a
**different** construction, the four-fold intersection above, satisfies all four constraints
at size `n^{2-o(1)}`. Escaping one barrier construction is not escaping the barrier.

**Methodological lesson for the campaign:** "mechanism M defeats the known barrier
construction" is much weaker evidence than it feels, and must never be promoted to
"mechanism M is promising" without an independent attempt to build a *new* barrier
construction adapted to M. Q4 was labelled PROMISING on exactly that insufficient basis.

---

## The sharpened barrier B4′ — a genuinely useful by-product

The argument generalises to *any* finite set of directions. For primitive directions
`e_1,...,e_k` with linear forms `φ_i`, the sufficient condition for all `k` line-kill
constraints is that each `φ_i(S)` lies in a 3-AP-free set `W_i`. Averaging over independent
shifts of the `W_i` gives, with `δ = exp(-C√(log n))` the Behrend density,

    Q_k(n) ≳ n^2 · δ^k = n^2 · exp(-C k √(log n)).

For this to drop below `n^{2-ε}` one needs `C k √(log n) > ε log n`, i.e.

    **k = Ω(√(log n)) directions.**

So: *no relaxation using a bounded number of directions of the line-kill mechanism can ever
give a power saving* — `VERIFIED_THEOREM` for that class. This supersedes the heuristic
barrier B4 with a rigorous statement, and it converts a vague "summing over directions
saturates" into a precise design requirement: **a working mechanism must couple `Ω(√log n)`
directions simultaneously**, and must do so in a way not implied by 3-AP-freeness of each
individual projection.

That last clause is the real content. The barrier construction only ever uses "each
projection lands in a 3-AP-free set". Any mechanism whose consequences are implied by that
statement is dead for all `k`. A live mechanism must use a genuinely *joint* constraint
across directions — something that fails for `S = ∩_i φ_i^{-1}(W_i)` even when every `W_i`
is 3-AP-free.
