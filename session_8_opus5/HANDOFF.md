# Handoff — the single remaining mathematical obligation

Obligation **(Q2)** carried by the previous pass is **discharged** (Theorem F, §6.2). The
obligation below replaces it.

Resolved along the way, and not to be reopened:

- **(Q2), the `l = 2` neighbourhood average** — closed by Lemma E + Theorem F, using only the
  vertex-count condition (P), Lemma 1(c) and Lemmas D/E. It needs neither (H-surv) nor the
  crude cap.
- **(H-surv)** — shown to be (i) *not dischargeable* by line-averaging, since the line-average
  of `d_2` obeys the identical Theorem 2 barrier (Corollary 6.1), and (ii) *not needed* by the
  positive programme, since it gates only the barrier Theorem 2. Theorem 2 is therefore
  permanently a conditional obstruction theorem.
- **Prop 3(3a), the crude cap** — corrected to unconditional, `K = Theta(sqrt(log n)/log log n)`.
- **Prop 3(3b)'s independence audit** — superseded by Lemma C, a Freedman estimate assuming no
  independence.

---

## The obligation

> **(K1) The dynamic pair codegree of `H_n`.**
>
> `c_{2,2->1}(v,v',i)` is the number of vertices `y` such that `{v,y}` and `{v',y}` are both
> size-2 edges of `H(i)` — i.e. the codegree of the pair `v,v'` in the evolving 2-graph
> `G(i)`. It is the **unique genuinely dynamic pair condition at `r = 3`** (§1.1): the other
> three instances are monotone and hence deterministic. Bennett–Bohman require
> ```
>       c_{2,2->1}(v,v',i)  <=  C_{2,2->1}  =  8 D^{1/2 - eps + 2 lambda}
> ```
> for all pairs and all `i <= T`, and consume it at ind.tex lines 1018 (drift error) and 1180
> (step size).
>
> Show that `H_n` satisfies it with a polylogarithmic rather than polynomial `eps`, i.e.
> ```
>       max_{v,v'}  c_{2,2->1}(v,v', i)   =   O( s_2(t_i) / (log n)^{A} )
> ```
> for a suitable constant `A > 0`, for all `i <= T`, with failure probability `o(N^{-2})`.

## Why it is the right last question, and how it sits

- **Scale.** `G(i)` has `N = n^2` vertices and degrees `d_2 ≈ s_2 = Theta(n sqrt(log n))`, so
  the *typical* pair codegree is `s_2^2/N = Theta(log n)` — a factor `n/polylog` below what is
  required. The obligation is therefore about the **maximum**, not the average, and there is a
  factor `n/polylog` of room.
- **Why it is not automatic.** `y` is a common 2-neighbour of `v` and `v'` exactly when there
  are chosen vertices `z, z'` with `{v,y,z}` and `{v',y,z'}` edges of `H`. By Lemma E(b) a
  single chosen `z` can create `Theta(n)` 2-edges at `v` along one line, and a single `z'` can
  do the same at `v'`; if those two lines coincide, `c_{2,2->1}(v,v')` jumps by `Theta(n)` in
  one step. That is the same coherent-line mechanism as everywhere else in this session, and
  it must be counted, not bounded stepwise.
- **The expected shape of the proof.** Identical to Theorem F: the jump is `Theta(n)` and
  occurs only when the chosen vertex lies on a line common to `v` and `v'`; the hazard of that
  is `Theta((log n)^{-1/2})` per line; and the budget `C_{2,2->1}/n = Theta(sqrt(log n)/polylog)`
  must beat `log N / log log n`. **Note this is `Theta(sqrt(log n))` against
  `log n/log log n` — the Theorem 2 shape.** Whether it clears therefore depends on the
  precise power of `log n` available in `C_{2,2->1}`, and on whether the two lines can in fact
  coincide often. **This may well fail.** It is the last thing that could.

## What closing it would give — and what would still be missing

If (K1) closes, every condition of the substituted stopping time is verified, and the horizon
is set by the tolerance-compounding constant `C` of §5.5 line 6:
```
   sigma = sigma_{3,0} = (log log n)^{-1/2}          (meets every sigma-constraint, K2)
   compounding:  sigma_{3,0} e^{C t^2}/q^2 = o(1)    =>  t = O( sqrt(log log log n) )
   horizon:      m = t N / D^{1/2}                    =  Theta( n sqrt(log log log n)/sqrt(log n) )
```
That constant `C` is a **computation** with BB's error-function system (ind.tex lines 981–998),
not an open question, but it has not been carried out and it fixes the answer. Until both are
done, the proved bound stays `C(n) = Omega(n/sqrt(log n))`.

## What must not be redone

- Do **not** revisit "average `Delta_2` or `Gamma`" (registry S1/S2/S5).
- Do **not** try to rescue the *pointwise* `d_2` condition, by any means (registry B4,
  ATTACK_LOG A5). And do **not** try to rescue it by averaging over a **line**: Corollary 6.1
  shows the line-average obeys the same barrier.
- Do **not** assume independence or negative association of `{e(u)}`; both are false (§5.1).
- Do **not** use Cauchy–Schwarz against the *global* `sum_u e(u)^2`; short by `sqrt(n)` (§5.4).
  Against the *per-line* second moment it works, and that is Theorem F.
- Do **not** attempt a *signed* bound on `sum_{u ∈ P(v,y)} e(u)`. `P(v,y)` is a random subset
  of the bisector line, so cancellation over the line implies nothing about it. The absolute
  value plus the per-line second moment is the correct formulation (§6.0).
- Do **not** infer asymptotics from the finite-`n` tables. In this session a fitting error of
  exactly that kind — `sd_y(A) = Theta(n^3)` rather than the true `Theta(n^2 log^2 n)`, the two
  differing by a factor 4 at `n <= 64` — briefly made the averaged programme look dead. It was
  caught by computing `sd/mean`, which is scale-free and came out flat at 0.22. **Keep using
  scale-free ratios when checking a fit.**
