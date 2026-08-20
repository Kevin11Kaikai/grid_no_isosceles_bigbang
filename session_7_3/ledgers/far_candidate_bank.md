# FAR candidate bank — Session 7.3, Round 1

Mechanism diversity, not count (7.3 rule replacing the 40-60 quota). Every candidate was
CHECKed against the `iso6` barrier cage B1-B8 **before** any development.

---

## FAR-C001 — `C(n) = Omega(n)` via the random greedy independent set process
**Origin** LITERATURE (arXiv:2601.14465 names the route and does not execute it).
**Mechanism family** probabilistic / nibble. **Representation** 3-uniform hypergraph `H_n`.
**Statement** `H_n` satisfies the hypotheses of Bennett-Bohman Thm 1.1, hence
`C(n) = Omega(n)`.
**Direct implication** settles the conjectured linear lower bound; the gap to the known
`n/sqrt(log n)` is exactly `sqrt(log n)`.
**Barrier check** B1-B8 are all *upper*-bound barriers; none applies to a lower-bound
construction. Passes.
**Pre-solve** importance 5 · difficulty 3 · reachability 4 · leverage 5 · novelty risk MEDIUM.
**Probe result** `KILLED (as stated)`. Both hypotheses fail — `Delta_2 = Theta(n)` against
a required `D^{1/2-eps}`, and `Gamma = Omega(n^2)` against a required `D^{1-eps}`. Each
fails by exactly a logarithmic margin. Rigorous witnesses in `docs/round1_findings.md` §2.
**What survives** the failure is informative, not merely negative: the deficits are
`sqrt(log n)` and `log n`, and the obstruction is carried by axis-parallel/diagonal pairs
(measured, `experiments/extremal_pairs.py`). Promoted to FAR-C004.
**Status** `KILLED -> FIX`

---

## FAR-C002 — one point per column
**Origin** INTERNAL (repair attempt for C001: kill the axis-parallel pairs by construction).
**Statement** for every `n` there is `f:[n]->[n]` whose graph is isosceles-free; hence
`C(n) >= n`.
**Why it might be true** found by backtracking for every `n` tried, with node count growing
like `n^4` — polynomially, not exponentially.
**Probe result** `PROGRESS`. Existence verified `n <= 128`. **No proof.** The LLL route to
existence fails by exactly `log n` (`E[#violations] = Theta(n log n)` against `n` points).
**Hardest obligation** existence for all `n`. Genuinely easier than the original? *Unclear* —
this is structurally the Costas-array situation, where existence for all `n` is famously
open. Flagged as a possible fake reduction.
**Status** `PROGRESS / BLOCKED-pending`

---

## FAR-C003 — strip decomposition and the row clique-cover bound
**Origin** INTERNAL_DATA (the archive's unexplained `C(2,25)=17` and "extremal sets leave
whole rows empty").
**Statement** `|S| <= cc(G)*n` where `G` is the graph on occupied rows, `j~j'` iff same
parity and `(j+j')/2` occupied.
**Probe result** `CHECKED -> capped`. Correct and validated (0/87 999 mismatches), and it
does explain the empty rows. But an adversary takes the occupied-row set 3-AP-free, `G`
becomes edgeless, and the bound degenerates to `r_3(k)*r_3(n) = n^{2-o(1)}` — precisely the
archive's B2/B3/B4' cap. Not promoted.
**Status** `CHECKED / DEPRIORITIZED`

---

## FAR-C004 — the shared-logarithm diagnosis
**Origin** SYNTHESIS (of C001, C002, and the known alteration bound).
**Statement** alteration, nibble and LLL each miss `C(n) = Omega(n)` by exactly one factor
of `log n`, and in all three the factor is `Sum_{d<=X} r_2(d)^2 ~ X log X`.
**Why it matters** it converts "most probably achievable" into a precise account of what is
missing, and it says where a proof must gain: any successful argument must beat the mean
distance-multiplicity, not merely apply an off-the-shelf theorem.
**Potential paper role** the honest core of a short note; **not** a theorem about `C(n)`.
**Novelty** `NOVELTY_PRELIMINARY` — searched, nothing located, but statements about a
tool's inapplicability characteristically go unwritten. Must not be oversold.
**Status** `PROGRESS`

---

## Not opened this round
- Upper bound `O(n^{2-eps})` — the whole of `iso6`. B1-B8 cage stands; nothing new to add.
- Exact `C(33)` (first genuinely open value) — `n=13` cost 596 billion nodes; `n=33` is
  astronomically out of reach, and per §31 the table no longer discriminates candidates.
- B6 prior art — searched (`arXiv:2601.14465` discusses no degree-`k` relaxation);
  still `NOT FOUND`, still low value.

---

## FAR-C005 — parity-separated doubling

**Origin:** Round 4 FIND, source B (problem-grounded: arithmetic type of `|p-q|^2`).
**Theorem family:** A1 recursive / A2 decomposition — the highest-priority Tier A family,
untouched by rounds 1-3.
**Representation:** arithmetic (residues of squared distances mod 4 and mod 8).

**Precise statement.** `S c [n]^2` isosceles-free satisfying condition (H) — every row and
column of `G(s,s') = |2(s-s')+(1,1)|^2` injective — gives `T = 2S u (2S+(1,1)) c [2n]^2`
isosceles-free with `|T| = 2|S|`. Hence `C(2n) >= 2 C_H(n)`.

**Why it may be true:** proved, and verified end-to-end by a naive checker for `n=5..16`.
**Why it mattered:** `C_H = C` would have given `C(n) = Omega(n)` by iteration.
**Contrary evidence / kill:** `rho = C_H/C -> ~1/sqrt 3 = 0.577` (exact `n<=7`, greedy to
`n=48`), because (H) is itself an `r_2`-Sidon condition via
`(2w+1)^2+(2z+1)^2 = 8(T(w)+T(z))+2`. Density multiplies by `rho` per doubling -> 0.
Also `2 C_H(n) < C(2n)` at every `n` where both are known.
**Generality:** dilation by `q` preserves the class count only for `q` a power of 2
(`M(q)=q` for `q=2,4,8`; `M(q)<q` for `q=3,5,6,7,9`).

**Pre-solve importance:** 5 · **difficulty:** 3 · **reachability:** 4 · **leverage:** 5
**Local compute:** LIGHT. **Friend-Safe:** YES.
**Potential paper role:** a section of the Tier-B obstruction note — the constructive half.
**Current status:** `KILLED as a route to Omega(n)` / `VERIFIED_THEOREM as a recurrence`.

---

## FAR-C006 — the mod-`p` / finite-field quotient

**Origin:** Round 5 FIND, source A+B (make the campaign's obstruction *vanish* rather than
work around it).
**Theorem family:** A6 representation-driven / A7 finite-to-asymptotic.
**Representation:** arithmetic — `F_{p^2}` with its norm form.

**Precise statement.** `S c [0,p)^2` with all same-apex values `Q(s-s') mod p` distinct is
isosceles-free in `Z^2`; so `C(p) >= A(p)`. Mod `p` the multiplicity function is exactly
flat (`p+1` preimages per nonzero value, `p = 3 mod 4`), removing the `Sum r_2^2 ≍ X log X`
non-uniformity that killed rounds 1-4. Ceiling `A(p) <= p`.

**Why it mattered:** `A(p) = Omega(p)` would have given `C(n) = Omega(n)` along the primes.
**Kill:** `A(p) = Theta(sqrt p)`. `A(p)/sqrt p` is flat at 2.11 -> 2.70 over `p = 11..401`
while `A(p)/p` collapses .636 -> .135. Flattening `mu` collapsed the distance-value range
from `~p^2/sqrt(log p)` to `p-1`; the threshold `sqrt(V/mu)` therefore got *worse*, not
better. No algebraic family (monomial graphs, norm circle, Welch/Costas) comes near.
**Generality:** the trade-off is intrinsic — `mu >= V/(#distinct values)`, so no quotient
of `Z^2` buys uniformity without paying more in range.

**Pre-solve importance:** 5 · **difficulty:** 3 · **reachability:** 4 · **leverage:** 5
**Local compute:** LIGHT. **Friend-Safe:** YES.
**Potential paper role:** section 3 of the obstruction note — the arithmetic-quotient half,
and the source of the unifying `sqrt(V/mu)` formula.
**Current status:** `KILLED as a route to Omega(n)` / reduction itself `VERIFIED_THEOREM`.
