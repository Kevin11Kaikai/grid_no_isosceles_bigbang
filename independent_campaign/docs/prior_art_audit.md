# Prior-Art Audit — UNSEALED 2026-08-17

§3 HARD ISOLATION was maintained for the whole discovery phase and is now lifted by user
decision. This document replaces `NOVELTY_UNASSESSED` with an assessed status for every
substantive campaign result. Executed in the order fixed by
`docs/session6_final_closeout.md` §7.

Search was targeted, not exhaustive. Verdicts below are `KNOWN`, `SUPERSEDED`,
`NOT FOUND` (searched, nothing located — *not* a novelty claim), or
`NOVELTY CANDIDATE` (searched specifically, nothing located, and there is positive
indirect evidence it is unstated).

---

## 0. The problem itself — baseline confirmed exactly

Erdős Problem **6.59**, `C_{6.59}(n)` = largest subset of `[n]²` with no (possibly flat)
isosceles triangle. Asked independently by **Wu** and **Ellenberg–Jain**, possibly Erdős.

```
    n/√(log n)  ≲  C(n)  ≲  e^{-c (log n)^{1/9}} · n²
```

Identical to the sealed baseline packet, including the remark that the lower bound may be
improvable to `≳ n`. **The target `C(n) = O(n^{2-ε})` is genuinely open.** No campaign
result contradicts the literature and no published result contradicts a campaign result.

New external data point not in the baseline: best known construction at `n = 64` has size
**110**, found by PatternBoost.

---

## 1. Audit item (i) — the square-corner / `Z[i]` formulation → **KNOWN**

A square corner `{b, b+w, b+i·w}` is exactly a **non-degenerate isosceles right triangle**
(legs `w` and `iw`: equal length, perpendicular). `Q_SQ(n)` is a studied quantity, written
`F(n)` in the literature, and it is studied **over the Gaussian integers**.

| | statement | source |
|---|---|---|
| upper | `F(n) = O(n²/(log n)^{1-ε})` for every `ε>0` | **Bloom (2014)**, cited in arXiv:2601.14465 |
| upper (refined) | `F(n) ≪ n²/(log n)^{1+c}` | arXiv:2607.22828 |
| lower | `F(n) ≫ n^α/(log n)^{140}`, `α = log 281 / log|51+51i| ≈ 1.318` | arXiv:2607.22828, Thm 4.2 |
| corners (axis-parallel IRT) | `n²/(log log n)^C` contains a corner | **Shkredov** |

**Our tensor lemma is their construction mechanism.** Their Theorem 4.2 picks a Gaussian
base `β = 51+51i`, a **carry-free** diamond digit region, and a digit alphabet of size 281
found by AlphaEvolve search, giving exponent `log q / log|β|`. That is precisely the
campaign's `Q_SQ(n) = Ω(n^{log g(q)/log q})` with "no carry analysis needed". **NOT NOVEL.**

**Our `Ω(n^{1.1562})` (from exact `g(11)=16`) is SUPERSEDED** by `Ω(n^{1.318})`. Their
alphabet search was far larger than ours; our exact values remain correct and remain the
only *exhaustively certified* points on that curve, but they do not set the record.

### 1a. The decisive strategic consequence — route SQ is **lossy**

`C(n) ≤ Q_SQ(n)` is proved. Substituting the best known bound on `Q_SQ`:

```
    C(n) = O(n² / (log n)^{1-ε})      via the square-corner relaxation
    C(n) = O(n² e^{-c (log n)^{1/9}})  via the baseline n·r_3(n)
```

and `e^{-c(log n)^{1/9}}` decays faster than **every** power of `log n`. So passing to
`Q_SQ` currently **throws away more than it gains**: the relaxation is strictly lossy at
the present state of knowledge, and it can only ever help if someone proves a *power
saving* for `Q_SQ` — which is itself an open problem whose published progress is merely
logarithmic.

**Verdict on route SQ.** The campaign's barrier analysis was *correct* — `Q_SQ` really is
not capped at `n^{2-o(1)}` (best construction `n^{1.318}`), and the campaign was right that
it is the only mechanism it found escaping the `n^{2-o(1)}` barrier family. But
"unbarriered" is not "promising": SQ is a lateral move to an open problem of comparable
difficulty, not a step toward the target. The closeout's own caveat — *"no difficulty
reduction is claimed for it, so the route is not essentially complete"* — is now
confirmed from outside, and should be strengthened: **route SQ is DEPRIORITIZED, not LIVE.**

---

## 2. Audit item (ii) — B6, the degree-`k` relaxation → **NOT FOUND**

`n^{2-2/(k+1)-o(1)}` for the relaxation "each point, each radius, at most `k` points".
Nothing located. The proof method (alteration against the moment sums
`M_j(R) = Σ_{r≤R} r_2(r)^j`, using `r_2(r) ≤ d(r) = r^{o(1)}`) is entirely standard, so the
statement is likely folklore-adjacent even if unstated. Modest value at best. The
*consequence* — that any argument surviving at degree 2 is capped at `n^{4/3}` — is the
useful part and was not located either.

## 3. Audit item (iii) — `C(12) = 20` → **KNOWN** (verdict reversed 2026-08-18; see F7)

**This section's original verdict was wrong.** It read `NOT FOUND`, on the grounds that no
source printed an exact value of `C(n)` at `n = 12` and that the sealed baseline supplied
`20 ≤ C(12) ≤ 23`.

The value was already known. Charton–Ellenberg–Wagner–Williamson, *PatternBoost*
([arXiv:2411.00566](https://arxiv.org/abs/2411.00566), Oct 2024) state that "for `n` up to
`≈ 32`, SAT solvers can find the best constructions **and prove their optimality**", and
plot every computed value; the plotted value at `n = 12` is **20**, and the plotted sequence
agrees with this campaign's at every common point. The audit missed it because it searched
printed numbers and did not read the figure. Full account, and the two rules it produced, in
`ledgers/failure_ledger.md` **F7**.

The campaign's contribution at `n = 12` is therefore an **independent reproduction by a
different method**, not a new value. The computational record below stands as written — it
is what makes the reproduction worth anything.

**Re-verified at root, 2026-08-17 — it is no longer a salvaged subagent report.** Both
decisive searches were rebuilt and re-run in-session: the symmetry-disabled run from
`best = 20` reproduced **45 922 791 007 nodes exactly** (deterministic, since `best` never
rises), and its root task count `7750` matches the closed form `Σ_{v₀=0}^{123}(124-v₀)`.
`C(1..11)` re-derived with no disagreement; `C(1,n) = r_3(n)` reproduced for `n = 1..24` by
a definition-only solver sharing no logic with the fast one; four pairwise-distinct
20-point witnesses all valid. A **second exhaustive implementation** (different cell order,
different validity oracle, different bound, no symmetry) independently establishes the
upper bound at `n = 12` — `32 795 784 946` nodes, 1385 s, no 21-point set — and agrees on
`n = 8..11`. The upper bound therefore rests on two implementations, neither using
symmetry; only a shared *conceptual* error remains unexcluded, guarded by the `r_3` test.

Package: `submission/` (`README.md`, `COVER.md`, `verify_independent.py`, `code/`, `logs/`),
re-labelled as an independent reproduction. With this verdict reversed the campaign has **no**
surviving novel contribution.

## 4. Theorem 4 (Behrend digit-spheres cannot be square-corner-free) → **KNOWN IN SUBSTANCE**

*Initially logged as the campaign's best novelty candidate. A full read of
arXiv:2607.22828 (Károlyi–Solymosi) closed it.*

The paper contains:

> **Remark 2.5.** "No finite set that contains the vertices of a square can be equipped
> with an IRT-peeling order."

and its digit alphabet `C` (the diamond region of eq. 3.3, 281 digits) is **deliberately
not `i`-invariant** — the paper "explicitly uses a non-symmetric region to avoid carries,
breaking any rotational symmetry."

Theorem 4's mathematical core is exactly the content of Remark 2.5: the triple
`(b, i·b, -i·b)` satisfies the defining equation `a + ic = (1+i)b`, so an `i`-invariant
digit set is automatically corner-full. Károlyi–Solymosi state it in the form their method
needs (peeling orders); the campaign states it in the form the Behrend method needs
(sphere conditions). The extra step in Theorem 4 — that a rotation-invariant `Q` satisfies
`Q(i·d) = Q(d)`, so the sphere condition cannot repair it — is **one line**.

A one-line corollary of a stated remark is not an independent contribution. Theorem 4 is
correct, was independently derived, and is not novel. **Downgraded; it is not citable and
must not be presented as a result.**

Residual: Theorem 4 as stated covers *any* `i`-invariant digit box with *any* direct-sum
quadratic form, formally broader than Remark 2.5. That breadth is not a contribution.

## 5. Remaining results — assessed briefly

| result | verdict |
|---|---|
| B4′ (bounded-direction line-kill capped at `n^{2-o(1)}`) | NOT FOUND; not searched deeply |
| Theorem A (`Q_SQ(n) ≤ g(q)` for `q ≥ 2n`) | almost certainly folklore |
| Theorem B (ideal uniformity, `m(p) = g(q)` as one function) | almost certainly folklore; `Z[i]` structure is exactly what arXiv:2607.22828 uses |
| Lemma C (`m(p) ≤ (p+1)/2`, half-orbit form) | trivial bound; mechanism naming is the only content |
| `C(n²) ≥ C(n)²` is FALSE (`C(16)=28 < 36`) | NOT FOUND |
| the `2×n` product law with its single exception `C(2,25)=17` | NOT FOUND |

---

## 6. What the audit changes

1. **Route SQ: LIVE → DEPRIORITIZED.** Not because it was barriered — the barrier analysis
   was right — but because the relaxation is lossy and the sub-problem is independently
   open with only logarithmic progress. §1a.
2. **The campaign's positive lower-bound work is superseded.** The tensor lemma is the
   published construction mechanism and our exponent is below the published one.
3. **One candidate survives: `C(12) = 20`.** Theorem 4, logged as the best mathematical
   candidate when this document was first written, did not survive the full read — it is
   Remark 2.5 of arXiv:2607.22828 in different clothing. `C(12) = 20` is a computational
   data point closing a bracket that the sealed packet listed as open; its natural
   destination is the problem's entry in the Erdős problem database, not a paper.
   It is not progress on `C(n) = O(n^{2-ε})`.
4. **The campaign's negative results held up.** Every barrier, every falsification, and the
   refusal to upgrade SQ past "no difficulty reduction claimed" are all consistent with the
   external record. The discipline was not wasted; the discovery was.
5. **F6 is confirmed.** Blind mode had already begun restating its own results; it was also
   re-deriving published ones. The unsealing was overdue.

**Nothing in this audit constitutes progress toward `C(n) = O(n^{2-ε})`. The problem is
open and the campaign did not move it.**

Sources: [arXiv:2607.22828](https://arxiv.org/abs/2607.22828) ·
[arXiv:2601.14465](https://arxiv.org/abs/2601.14465) ·
[arXiv:2511.02864](https://arxiv.org/abs/2511.02864) ·
[PatternBoost, arXiv:2411.00566](https://arxiv.org/pdf/2411.00566)
