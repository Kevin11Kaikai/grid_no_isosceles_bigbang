# Session 7.3 — Round 4 findings (campaign reopened under 7.2 §58 REBRANCH)

**Headline: the campaign's first rigorous *recursive* theorem (Tier A1 shape), and its
own kill. Rounds 1–3 showed the probabilistic routes to `C(n) = Omega(n)` all lose one
factor of `log n` to `Sum r_2(d)^2 ≍ X log X`. Round 4 shows the *constructive* route —
self-similar dilation, the highest-priority Tier A1 family, untouched until now — is
blocked by the same arithmetic, and quantifies the loss as a constant factor `1/sqrt 3`
per doubling.**

---

## 4.1 The mechanism: an exact parity separation — `VERIFIED_THEOREM`

Classify `Z^2` by coordinate parity. Elementary and exhaustively checked
(`experiments/r4_verify.py`, 81x81 vectors, 0 violations):

```
    p - q = (even, even)   =>   |p-q|^2 = 0  (mod 4)
    p - q = (odd,  odd )   =>   |p-q|^2 = 2  (mod 8)
```

So in `T = 2S u (2S + (1,1))` every apex sees its **own** class at `0 mod 4` and the
**other** class at `2 mod 8`. Those two families can never collide. The separation is
free, exact, and needs no hypothesis on `S`. This is the "arithmetic type" missing
invariant that §20 asks for, and no earlier round used it.

## 4.2 The doubling theorem — `VERIFIED_THEOREM`

The separation reduces isosceles-freeness of `T` to four conditions, two of which `S`
already supplies. Writing `G(s,s') = |2(s-s') + (1,1)|^2`, define

> **condition (H):** for every `s in S`, both `s' -> G(s,s')` and `s' -> G(s',s)` are
> injective on `S` — i.e. every row *and* every column of the matrix `G` is injective.

Geometrically: each half-integer point `s +- (1/2,1/2)` must lie off every perpendicular
bisector of a pair of `S`.

> **Theorem R4.** If `S c [n]^2` is isosceles-free and satisfies (H), then
> `T = 2S u (2S+(1,1)) c [2n]^2` is isosceles-free and `|T| = 2|S|`. Hence
> **`C(2n) >= 2 C_H(n)`**, where `C_H` is the maximum over (H)-satisfying `S`.

Verified end-to-end for `n = 5..16` by a **naive triple loop that knows nothing about
parity** (`r4_verify.py`): every doubling returned exactly `2|S|` points, isosceles-free,
no exceptions. The derivation is sound.

The offset must be `(+-1,+-1)`: a larger odd offset overflows `[2n]^2`. (Probe 4.1's
"best over odd `(a,b)`" column is therefore not usable for the recurrence — those
witnesses have span up to `41 > 2n`. Recorded so it is not misread later.)

## 4.3 Why it dies: (H) is itself an `r_2`-condition — `VERIFIED_THEOREM` + measurement

The identity (verified, 0 violations)

```
    (2w+1)^2 + (2z+1)^2  =  8( T(w) + T(z) ) + 2 ,     T(w) = w(w+1)/2
```

shows the cross-class distances are sums of two **odd** squares. Their representation
statistics are `r_2`-type — the *same* arithmetic that blocks every probabilistic route.
So (H) does not sidestep the obstruction; it re-imposes it. Concretely, each `s in S`
now carries three injectivity families instead of one (own-class, `G`-row, `G`-column),
and a greedy solving `m^3/D ~ m` predicts

```
    rho(n) = C_H(n)/C(n)  ->  1/sqrt(3) = 0.5774 .
```

**Measured (`r4_cost.py`, offset `(1,1)`, same greedy both sides):**

| `n` | 6 | 8 | 10 | 12 | 14 | 16 | 20 | 24 | 28 | 32 | 40 | 48 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `rho` | .667 | .667 | .643 | .625 | .579 | .591 | .593 | .581 | .618 | .575 | .617 | .607 |

**Exact values (`r4_exact.py`, branch and bound, against known optimal `C(n)`):**

| `n` | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|
| `C(n)` | 4 | 6 | 7 | 9 | 10 |
| `C_H(n)` exact | 2 | 4 | 5 | 6 | 8 |
| `rho` exact | .500 | .667 | .714 | .667 | .800 |

Exact and greedy agree that **`rho` is bounded away from 1**, at roughly the predicted
`1/sqrt 3`. Since each doubling multiplies density by `rho`, iterating gives density
`rho^k -> 0`. **The construction cannot reach `Omega(n)`.** It is also weak as a
construction: `2 C_H(4) = 8 < C(8) = 13`, `2 C_H(5) = 10 < C(10) = 18`.

## 4.4 Parity is the *only* dilation — `VERIFIED_COMPUTATIONAL_RESULT`

Generalise: dilate by `q`, take classes `V c Z_q^2`, set `T = u_{v in V} (qS + v) c [qn]^2`.
Density is preserved only if `|V| >= q`. Two classes are separable exactly when the value
sets `Val(w) = {|qu+w|^2 : u in Z^2}` are disjoint. Computed exactly
(`r4_dilation2.py`, `Val` tested to `3x10^5`):

| `q` | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|
| `M(q)` | **2** | 2 | **4** | 4 | 4 | 5 | **8** | 6 |
| `M(q)/q` | 1.00 | .67 | 1.00 | .80 | .67 | .71 | 1.00 | .67 |

`M(q) = q` exactly on the **powers of 2** and is strictly smaller for every other
`q <= 9`. So parity doubling and its iterates are the unique dilations whose class count
even keeps up with the grid — and 4.3 shows that even they lose a constant factor once
the cross-class condition is paid. (Probe 4.4 first used only the guaranteed invariant
`|qu+w|^2 = |w|^2 (mod q)`; that is sound but not sharp — it misses the `mod 8` separation
at `q=2` — so the table above is the corrected one.)

## 4.5 What Round 4 adds to the campaign's diagnosis

Rounds 1–3 established: *every standard probabilistic route loses exactly one `log n`,
traceable to `Sum_{d<=X} r_2(d)^2 ≍ X log X`.* Round 3 closed the bounded-degree escape.
Round 4 closes the remaining natural family:

> **The self-similar constructive route is blocked by the same arithmetic. The only
> density-preserving dilation of `Z^2` is by a power of 2, and the cross-class condition
> it creates is again a Sidon condition for a sum of two squares — so the doubling pays a
> constant factor `~1/sqrt 3` and iterates to density zero.**

This is a real widening: the obstruction is no longer "probabilistic tools are too weak"
but "the representation function `r_2` blocks the probabilistic *and* the recursive
routes alike." That is the strongest single sentence the campaign has produced and it
materially improves the Tier-B note.

## 4.6 Status after Round 4

| item | evidence | tier |
|---|---|---|
| parity separation `0 mod 4` vs `2 mod 8` | `VERIFIED_THEOREM` | B |
| doubling theorem `C(2n) >= 2 C_H(n)` | `VERIFIED_THEOREM` | **B** |
| `(2w+1)^2+(2z+1)^2 = 8(T(w)+T(z))+2`, so (H) is `r_2`-type | `VERIFIED_THEOREM` | B |
| `rho -> ~1/sqrt 3`, so doubling iterates to density 0 | exact `n<=7` + greedy `n<=48` | B |
| `M(q) = q` only on powers of 2 | `VERIFIED_COMPUTATIONAL_RESULT` (`Val` to `3e5`) | C |
| `C(n) = Omega(n)` | **NOT PROVED** | — |

**Judge PASS 0 / TYPE2 0.** Theorem R4 is correct and is the campaign's only recursive
theorem, but the Paper-Killer Referee objection (§52) is fatal and I state it rather than
hide it: *`2 C_H(n)` is below known values of `C(2n)` at every `n` where both are known,
so the theorem advances no bound.* Tier B, as a component of the obstruction note.

`NOVELTY_PRELIMINARY`. Nothing here is a new bound on `C(n)`.
