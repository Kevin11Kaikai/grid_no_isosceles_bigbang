# Round 3 — Approach Registry

Per protocol Section 4, two approaches count as different only if their
mathematical **mechanisms** differ. Different vocabulary does not create a
branch. Per Section 5, a route may be marked `FALSIFIED` only on a counterexample
to its central claim, a rigorous impossibility theorem, a contradiction, or
exhaustive elimination of a precisely defined finite class — **never** because it
performed poorly, ran slowly, or looks inelegant. Otherwise: `BLOCKED` or
`DEPRIORITIZED`.

Bar: strictly beat **112** (n=64) or **164** (n=100). Primary target n=100.

## Wave 1 (launched 2026-08-14)

### R1-ALG — explicit algebraic / number-theoretic construction
- **Core mechanism:** build S as the solution set of congruence/algebraic
  conditions rather than by search. The per-pivot condition says every translate
  S − p has pairwise-distinct norms N(v)=vx²+vy²; ask what algebraic structure
  forces that. Behrend/Salem–Spencer lifts, Sidon and Singer difference sets,
  quadratic residues, Gaussian-integer norm rigidity mod p ≡ 3 (mod 4).
- **Why prioritised:** the known Ω(n/√log n) lower bound is Behrend-flavoured,
  i.e. it comes from exactly this family — and asymptotic papers never evaluate
  their constructions concretely at n=64/100.
- **Status:** `EXPLORING`

### R2-SYM — imposed symmetry, orbit-level exact solve
- **Core mechanism:** work over orbits of a group action (C4/D4/C2 about the
  half-integer centre), build the orbit-level conflict structure, solve maximum
  legal orbit-union exactly with CP-SAT under a boundary-weighted objective.
- **Crux assigned:** derive exactly when symmetry *forces* an isosceles triple
  (the centre cannot be in S; and for p ∈ S and an orbit {q,rq,r²q,r³q}, when does
  p see two orbit-mates at equal squared distance). Quantify "approximate 4-fold
  symmetry" instead of using it as a slogan.
- **Status:** `EXPLORING`

### R3-REC — exact small n, then recursive / product lifting
- **Core mechanism:** certify exact C(n) for small n with CP-SAT + dihedral
  symmetry breaking, then hunt composition operators with **proved** legality
  conditions. Scaling k·S is legality-preserving but density-losing; the live
  question is S = k·A + B (Minkowski/base-k digits), where
  N(k(a−a′)+(b−b′)) = k²N(a−a′) + 2k⟨a−a′,b−b′⟩ + N(b−b′) and the k² term
  dominates for large k.
- **Why prioritised:** most likely location in this campaign for a clean theorem.
- **Status:** `EXPLORING`

### R4-SPEC — design in distance-spectrum space
- **Core mechanism:** work backwards from the spectrum. With |S|=k every pivot
  needs k−1 distinct realisable squared distances, giving the rigorous bound
  C(n) ≤ 1 + min over p ∈ S of |R(p)| where R(p)={N(v) : p+v ∈ G_n, v≠0}.
  Then constructive design via permutation/Costas-array and Golomb/B₂ row
  patterns.
- **Dual mandate:** this is the one route licensed to hunt a **proved upper
  bound**. An upper bound is a theorem; failure of search is not one, and the two
  must stay logically separate.
- **Possible explanatory payoff:** if |R(p)| is genuinely larger for corner than
  for central pivots, the boundary-concentration prior is *derived* rather than
  assumed.
- **Status:** `EXPLORING`

## Mechanism-independence check

All four differ at the mechanism level, and all four differ from everything
attempted in this repository to date. Prior work (`failed_ideas.md` F-001…F-010
and the concurrent session's routes) is **entirely search metaheuristics**:
greedy multistart, LNS with greedy / exact-MILP / multi-region repair, tabu,
simulated annealing, CP-SAT lazy-constraint global search, symmetry-guided
multistart, Hamming shells, pattern-grow, orbit-defect. Every Wave 1 route is
explicitly forbidden from drifting into that family.

If two routes converge on the same mechanism, Section 3 requires keeping only
enough agents to develop it and redirecting the rest.

## Adjudication

`ROUND3_TOURNAMENT/judge.py` re-adjudicates every candidate from disk and ignores
all self-reported status fields. See `JUDGE_SELFTEST.md` — the harness was itself
attacked with six adversarial fixtures before being trusted, and two defects in
the harness were found and fixed in that pass.
