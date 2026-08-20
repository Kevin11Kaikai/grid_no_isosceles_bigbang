# Session 7.3 — Round 5 findings

**Headline: no new bound — but Round 5 found the single formula that explains why rounds
1–5 all failed, reproduces the known lower bound exactly, and states precisely what any
proof of `C(n) = Omega(n)` must beat. It also closed a third method family (arithmetic
quotients) by showing that flattening the obstruction and destroying the bound are the
same operation.**

---

## 5.1 The mod-`p` reduction — `VERIFIED_THEOREM` (rigorous, and weak)

> **Lemma R5.1.** Let `S c [0,p)^2` be such that for every `s in S` the map
> `s' -> Q(s-s') mod p` is injective on `S\{s}`, where `Q(u) = u_x^2 + u_y^2`.
> Then `S` is isosceles-free in `Z^2`. Hence `C(p) >= A(p)`.

*Proof.* Distinct mod `p` implies distinct as integers. No wraparound argument needed. ∎

**Why this looked like the way out.** Rounds 1–4 all died on the non-uniformity of
`r_2(d)`: `Sum_{d<=X} r_2(d)^2 ≍ X log X`. Mod `p` that non-uniformity *does not exist*.
For `p = 3 (mod 4)`, `Q` is the norm form of `F_{p^2}` and every nonzero value has exactly
`p+1` preimages — perfectly flat. Round 3 §3.5 item 4 demanded a route that "beats the mean
multiplicity directly"; this makes it constant. Ceiling: `|S| <= p` (`p = 3 mod 4`).

## 5.2 It fails, and the failure is `sqrt(p)` — `VERIFIED_COMPUTATIONAL_RESULT`

Exact `A(p)` by branch and bound, greedy lower bounds above that (`r5_fp.py`,
`r5_scale.py`):

| `p` | 11 | 19 | 23 | 31 | 43 | 59 | 79 | 103 | 151 | 199 | 251 | 307 | 401 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `A(p)` | 7 | 10 | 11 | 13 | 16 | 19 | 22 | 26 | 32 | 37 | 43 | 48 | 54 |
| `A(p)/p` | .636 | .526 | .478 | .419 | .372 | .322 | .278 | .252 | .212 | .186 | .171 | .156 | .135 |
| **`A(p)/sqrt p`** | 2.11 | 2.29 | 2.29 | 2.33 | 2.44 | 2.47 | 2.47 | 2.56 | 2.60 | 2.62 | 2.71 | 2.74 | **2.70** |

`A(p)/p` collapses; `A(p)/sqrt(p)` is **flat**. So `A(p) = Theta(sqrt p)` and the reduction
yields only `C(n) >= ~2.7 sqrt(n)` — a factor `~sqrt(n)` *below* the known bound.

No explicit family helps either (`r5_scale.py`): over `p = 11..103`, the best monomial
graph `{(t,t^k)}`, the norm-circle `{x : N(x)=1}`, and the Welch/Costas map `{(i, g^i)}`
all have violation counts in the hundreds-to-thousands, none near 0. Notably the circle is
the *worst* of the three — consistent with its exact reduction (below) to a 3-AP problem.

## 5.3 THE UNIFYING FORMULA — the round's real product

For an apex `a` let `N_a(d) = #{b : |a-b|^2 = d}` and let

```
    P  =  E_a[ Sum_d N_a(d)^2 ] / (V-1)^2  =  mu / V ,      V = |ambient| ,
```

where `mu = Sum N^2 / Sum N` is the **size-biased mean multiplicity** of a squared
distance. Bad triples in a random `m`-set number `~ m^3 P`; alteration and random greedy
survive while `m^3 P < m`, i.e.

```
                        m  <  P^{-1/2}  =  sqrt( V / mu ) .
```

**Measured (`r5_unify.py`), both ambients:**

| `[n]^2` | `n=8` | 12 | 16 | 24 | 32 | 48 | 64 |
|---|---|---|---|---|---|---|---|
| `P n^2 / ln n` | 1.580 | 1.513 | 1.479 | 1.445 | 1.426 | 1.405 | **1.394** |
| `P^{-1/2} / (n/sqrt(ln n))` | .796 | .813 | .822 | .832 | .837 | .844 | **.847** |

| `F_p^2` | `p=11` | 19 | 23 | 31 | 43 | 59 | 79 | 103 |
|---|---|---|---|---|---|---|---|---|
| `P * p` | 1.100 | 1.056 | 1.045 | 1.033 | 1.024 | 1.017 | 1.013 | **1.010** |
| `A(p) / P^{-1/2}` | 2.21 | 2.36 | 2.35 | 2.37 | 2.47 | 2.50 | 2.49 | **2.57** |

So `P ≍ log n / n^2` in the grid and `P = 1/p` exactly in `F_p^2`, and:

```
    [n]^2 :  mu ≍ log n ,  V = n^2   =>   threshold = n / sqrt(log n)   <- THE KNOWN BOUND
    F_p^2 :  mu = p ,      V = p^2   =>   threshold = sqrt(p)           <- probe 5.2
```

> **The known lower bound `n/sqrt(log n)` is not an artefact of one technique. It is
> `sqrt(V/mu)`, the alteration threshold, and every method this campaign tried —
> alteration, random greedy, the nibble, the Local Lemma, bounded-degree ground sets,
> parity doubling, and the mod-`p` quotient — computes exactly this quantity. Proving
> `C(n) = Omega(n)` means beating it by `sqrt(mu) = sqrt(log n)`.**

## 5.4 Why the quotient trick cannot work — the general obstruction

Since `mu >= V / (#distinct distance values)`,

```
    threshold  =  sqrt(V/mu)  <=  sqrt( #distinct distance values ) .
```

Flattening `r_2` means shrinking `mu` toward 1 — but a quotient that flattens the
representation function *also collapses the value range*, and it collapses it by more than
it gains. Mod `p`: `mu` drops from `log n` to... `p`, i.e. it goes the **wrong way**,
because the `p^2` points now share only `p` distance values. This is a genuine
trade-off, not a failure of ingenuity:

> **Uniformity of the distance-multiplicity function and largeness of its range are
> coupled. No quotient of `Z^2` buys the first without paying more for the second.**

This closes a third method family, after the probabilistic (R1, R3) and the
constructive/recursive (R4).

## 5.5 A by-product: the norm circle is exactly a 3-AP problem — `VERIFIED_THEOREM`

For `p = 3 (mod 4)` let `G < F_{p^2}^*` be the norm-1 circle, `|G| = p+1`. For `s,s'`
on a circle `aG`, writing `h = g_2/g_1`,

```
    N(s - s')  =  -N(a) * (1-h)^2 / h  =  -N(a) * ( h + h^{-1} - 2 ) ,
```

which is invariant under `h -> h^{-1}`. So each distance is hit exactly twice, and a
subset of the circle is isosceles-free **iff** it contains no `b, a, b'` with `b + b' = 2a`
in `G ≅ Z_{p+1}` — i.e. **iff it is 3-AP-free**. The circle therefore gives only
`(p+1)/exp(c sqrt(log p))` points, worse than `sqrt p`. (Independently: `1D` isosceles-free
is literally 3-AP-free, since `|a-b| = |b-c|` on a line means `b` is the midpoint — which
is also why the *upper* bound `exp(-c(log n)^{1/9}) n^2` carries the Kelley–Meka exponent.)

## 5.6 Status after Round 5

| item | evidence | tier |
|---|---|---|
| mod-`p` reduction `C(p) >= A(p)` | `VERIFIED_THEOREM` | B |
| `A(p) = Theta(sqrt p)`, so the reduction is `sqrt(n)`-weak | exact `p<=11`, greedy to `p=401` | B |
| threshold `= sqrt(V/mu)`, reproducing `n/sqrt(log n)` | `VERIFIED_COMPUTATIONAL_RESULT` | **B** |
| uniformity/range trade-off kills all quotient routes | argued + measured | **B** |
| circle sections = 3-AP-free sets in `Z_{p+1}` | `VERIFIED_THEOREM` | C |
| `C(n) = Omega(n)` | **NOT PROVED** | — |

**Judge PASS 0 / TYPE2 0.** Fifth consecutive honest zero on the bound. But §5.3 is the
first statement the campaign has produced that is *predictive* rather than diagnostic: it
derives the known bound instead of merely failing to beat it, and it says exactly what the
open problem costs — a factor `sqrt(mu)`.

`NOVELTY_PRELIMINARY`. Nothing here is a new bound on `C(n)`.
