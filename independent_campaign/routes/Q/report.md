# Route Q — Joint-Direction Mechanism Hunt

**Status: IN PROGRESS** (incremental crash-recovery log; full findings also returned as text)

## Mission
Find a constraint implied by isosceles-freeness that the intersection-of-Behrend
construction S = {(x,y) : x in A, y in B, x+y in W, x-y in Z} (A,B,W,Z shifted
3-AP-free) VIOLATES. Per-direction constraints are barriered; look for constraints
coupling two directions on the same pair of points.

## Log

### 0. Setup
- Working dir D:/Others/iso6/routes/Q/. Report created first per survival rule.

### 1. First adversary builds — a finite-size trap (important)
Coordinate-descent over the four shifts, with the best 3-AP-free base sets I can
generate (best of 40 randomised greedy restarts vs the base-3 digit-avoiding set):

| n   | |T| | |T'| | best |S| |
|-----|-----|------|----------|
| 120 | 26  | 37   | 21 |
| 500 | 57  | 82   | 37 |
| 729 | 70  | 128  | 67 |
| 2187| 132 | 256  | 97 |

At n=2187 the adversary has |S|=97 and is **isosceles-free** (0 triples).
This is NOT evidence for the construction: a *random* set of m points in [n]^2 has
expected isosceles-triple count ~ m^3/#distances ~ m^3 sqrt(log n)/n^2, which is o(1)
unless m >> n^{2/3}. At n=2187, n^{2/3}=167 > 97.
**Finite-n Behrend sets are too sparse for the violation to be visible.**
Consequence: forensics must be run either (a) at small n where greedy 3-AP-free sets
have high density (delta^4 n^2 >> n^{2/3} requires delta >> n^{-1/3}), or (b) on
maximum-size Q4-feasible sets found by direct search, which sit in the same relaxation
and are much denser at finite n.

### 2. Two usable adversaries
(a) **Canonical Behrend-intersection**: too sparse at accessible n (see above).
(b) **Direct Q4-feasible greedy** (`q4_search.py`, incremental exact verifier): sets that
satisfy all four line-kill constraints exactly, found by randomised greedy.

| n | |S| | Q4 violations | isosceles triples |
|---|-----|---------------|-------------------|
| 20 | 32 | 0 | 51 |
| 30 | 52 | 0 | 127 |
| 40 | 69 | 0 | 207 |
| 60 | 107 | 0 | 396 |
| 80 | 149 | 0 | 642 |
| 100 | 189 | 0 | 941 |
| 150 | 286 | 0 | 1710 |
| 200 | 396 | 0 | 2738 |

VERIFIED_COMPUTATIONAL_RESULT: Q4-feasible sets of these sizes exist and are far from
isosceles-free.

### 3. Exact pattern-level forensics (`patterns.py`)
An isosceles triple is fixed by its *pattern* (u,v) = (b-a, c-b) with |u|^2=|v|^2.
For a linear form psi=<.,e> with values U=psi(u), V=psi(v), a 3-AP-free W_e containing
psi(S) is violated iff
  (P1) U=V!=0        <-> u+v parallel to e   [ = exactly the line-kill constraint for e ]
  (P2) U+2V=0, U!=0  [ extra: from 3-AP-freeness, NOT from line-kill ]
  (P3) 2U+V=0, V!=0  [ extra ]
PROVED (elementary). Consequence: **the pure k-direction line-kill relaxation kills exactly
those patterns whose base direction dir(c-a) lies in E.** Everything else is invisible to it.

Census over all patterns with u,v in [-8,8]^2 (2016 patterns):

| E | line-kill survivors | construction survivors |
|---|---|---|
| {(1,0),(0,1)} | 1216 (60.3%) | 1088 (54.0%) |
| Q4 = {(1,0),(0,1),(1,1),(1,-1)} | 704 (34.9%) | 576 (28.6%) |
| all prim. dirs |e|_inf<=2 (8) | 576 | 448 |
| all prim. dirs |e|_inf<=3 (16) | 368 | 272 |
| all prim. dirs |e|_inf<=4 (24) | 336 | 240 |

Smallest pattern surviving Q4: u=(3,2), v=(-2,3) (and its symmetry class) —
legs of squared length **13**, mutually **perpendicular** (u.v=0), base c-a=(1,5),
|c-a|^2=26. So the minimal invisible configuration is an *isosceles right triangle*
with legs (3,2),(-2,3) and base direction (1,5).
Survivor base directions in the box: 84 distinct — the invisible directions genuinely
spread; the top ones are (3,1),(1,3),(2,1),(1,2),(5,1),(1,5),(7,1),(5,3),...

### 4. Forensics on dense Q4-feasible adversaries (`forensics2.py`)
n=100, |S|=189, 941 isosceles triples / n=200, |S|=396, 2738 triples.

| quantity | n=100 | n=200 |
|---|---|---|
| distinct base directions dir(c-a) | 424 | 1142 |
| triples with base dir in the Q4 set | 0 (0.00%) | 0 (0.00%) |
| base dirs with \|e\|_inf<=3 | 26% | 20% |
| base dirs with \|e\|_inf<=7 | 50% | 41% |
| base dirs with \|e\|_inf<=13 | 67% | 58% |
| median \|c-a\|/n | 0.374 | 0.403 |
| median leg/n | 0.442 | 0.435 |
| legs perpendicular (right isosceles) | 22.6% | 18.4% |
| points that are an apex | 186/189 | 395/396 |
| top-10% of apexes carry | 19.4% | 20.3% |
| violating base pairs | 828 (4.7% of pairs) | 2439 (3.1%) |
| max multiplicity of a base pair | 5 | 4 |

**Answers to the forensic questions.**
- *Which directions?* NOT bounded. 1142 distinct base directions for 2738 triples
  (2.4 triples per direction). Only ~20% of triples have \|e\|_inf <= 3.
  0% lie in the four fixed directions (that is exactly what Q4 removes).
- *Range?* LONG. Median base length 0.40n, median leg 0.44n. This is a global,
  box-scale phenomenon, not a local one.
- *Concentration?* NONE. Essentially every point of S is an apex; the top decile of
  apexes carries ~20% of the triples (uniform would be 10%); no base pair repeats
  more than 4-5 times.
Conclusion: the information Q4 fails to capture is *spread uniformly over apexes,
over pairs, and over Omega(|S|) distinct directions, at box scale.* There is no small
set of extra directions that recovers it; each new direction recovers O(1/k) of it,
which is precisely the B4' harmonic/exponential trade.

## 5. CANDIDATE MECHANISM: the SQUARE-CORNER (rotated-corner) constraint

**Definition.** A *square corner* is a triple {b, b+w, b+w^perp} with w in Z^2\{0},
w^perp=(-w_2,w_1). (Three vertices of a square, right angle at b.)

**(a) Implied by isosceles-freeness. PROVED.** |w| = |w^perp|, so b+w and b+w^perp are
equidistant from b. So every isosceles-free set is square-corner-free.
Note w=(d,0) gives the *classical corner* {b, b+(d,0), b+(0,d)}, so square-corner-freeness
implies corner-freeness; the constraint is the full rotation-orbit of the corners problem.

**(b) It is exactly a two-direction constraint on the same apex**: it couples the direction
w with the direction w^perp at a single point b. This is the shape the brief asked for.

**(c) Minimality.** From the pattern census, the smallest isosceles pattern invisible to Q4
has legs (3,2) and (-2,3) — i.e. w and w^perp with w=(2,3). In general the square corner
for w is *not* killed by the Q4 construction unless w_1w_2=0, w_1=+-w_2, w_1=+-2w_2,
w_2=+-2w_1, w_1=+-3w_2, w_2=+-3w_1.

**(d) PROVED PROPOSITION (square-corner blindness of every finite direction set).**
With apex b, a=b+w, c=b+w^perp, so u=b-a=-w, v=c-b=w^perp, and for a direction e=(e1,e2):
  U=<u,e>=-<w,e>,  V=<v,e>=det(w,e)=w1 e2 - w2 e1.
The three kill conditions become single *linear equations in w*:
  P1: w1(e1+e2)   + w2(e2-e1)   = 0
  P2: w1(-e1+2e2) + w2(-e2-2e1) = 0
  P3: w1(-2e1+e2) + w2(-2e2-e1) = 0
None of these has all coefficients zero for e != 0. Hence **each direction e kills the
square corners of at most 3 lines' worth of w**, so a direction set E of size k kills at
most 3k(2R+1) of the (2R+1)^2-1 vectors w with |w|_inf <= R: a fraction <= 3k/(2R+1).

VERIFIED_COMPUTATIONAL_RESULT (`square_corner.py`), fraction of w in [-R,R]^2 killed:

| E | |E| | R=25 | R=50 | R=100 | R=200 |
|---|-----|------|------|-------|-------|
| Q4 | 4 | 13.85% | 7.14% | 3.62% | 1.82% |
| all prim |e|_inf<=4 | 24 | 23.69% | 12.47% | 6.38% | 3.21% |

Exact 1/R decay, as the proposition predicts.

**Consequence.** In [n]^2 the relevant w have |w|_inf up to n, so a k-direction
line-kill/Behrend-intersection construction leaves a 1 - O(k/n) fraction of all rotation
classes completely unconstrained. Unlike adding directions (each costing a Behrend factor
delta = exp(-C sqrt(log n))), there is **no way to buy the square-corner constraints
one direction at a time**: you would need k = Theta(n) directions, i.e. delta^n.

**(e) VERIFIED_COMPUTATIONAL_RESULT — the barrier constructions really do contain
square corners, in abundance, spread over many rotation classes.**
"Q4-alive" = the square corner is *not* killed by any of the four Q4 directions.

| set | n | \|S\| | square corners | Q4-alive | alive per point | distinct alive w-directions |
|---|---|---|---|---|---|---|
| B x B (barrier B3) | 81 | 256 | 3840 | 1360 | 5.3 | 168 |
| B x B (barrier B3) | 243 | 1024 | 31744 | 16000 | 15.6 | 988 |
| greedy Q4-feasible | 100 | 189 | 213 | 200 | 1.06 | 187 |
| greedy Q4-feasible | 200 | 396 | 505 | 491 | 1.24 | 448 |

Cross-check between two independently written enumerators: `iso_triples` reports exactly
505 right-isosceles triples at n=200 and `count_square_corners` reports 505. Agreement.
Second cross-check: the shift-averaged count of *classical* corners (w=(d,0)) over the
whole shift box is exactly **0** (`avg_supersat.py`) — as it must be, since Q4's diagonal
direction kills them — while the same count for square corners is strictly positive.

**(f) Averaged supersaturation (heuristic, but with an exact finite-n instrument).**
`avg_supersat.py` computes exactly
  sum_shifts #configs = sum_w V(w) prod_i c_i(phi_i(w), phi_i(w^perp)),
  c_i(P,Q) = #{tau in T_i : tau+P in T_i, tau+Q in T_i},   sum_shifts |S| = n^2 t^2 t'^2.
Results: n=40 rho=2.45e-3 (72/6240 w-classes alive), n=60 rho=1.54e-3 (42/14160).
Heuristically rho ~ n^2 delta^8 for k=4 (in general n^2 delta^{2k}), which tends to
infinity for Behrend density delta=exp(-c sqrt(log n)) but is <1 for the polynomially
sparse 3-AP-free sets available at accessible n (delta ~ n^{-0.37} gives rho ~ n^{-0.96}).
**So the finite-n rho values neither confirm nor refute the asymptotic claim** — recorded
honestly as such. The direct B x B counts above are the load-bearing evidence.

### 6. EXPLICIT CERTIFICATE (mission step 1, done properly) — `certificate.py`
Seeding the greedy 3-AP-free construction with the required elements produces, at n=200:

  A, B  3-AP-free subsets of [0,200)   (|A|=31, |B|=31)
  W     3-AP-free subset of [0,399)    (|W|=46)
  Z     3-AP-free subset of [-199,200) (|Z|=46)
  S = {(x,y) in [200]^2 : x in A, y in B, x+y in W, x-y in Z}, |S| = 16
  S = [(7,175),(19,52),(19,112),(19,113),(19,147),(19,148),(63,68),(63,118),
       (66,66),(66,148),(68,69),(116,45),(155,6),(155,169),(187,139),(187,153)]

VERIFIED_COMPUTATIONAL_RESULT (independent verifiers in `qlib.py`):
 * A,B,W,Z each 3-AP-free — yes.
 * Q4 line-kill violations: rows 0, cols 0, diagonals 0, antidiagonals 0. **All four
   line-kill constraints hold.**
 * S is NOT isosceles-free. It has exactly **one** isosceles triple:
   apex (66,66), legs to (63,68) and (68,69), squared leg length 13.
   That triple is exactly the square corner b=(66,66), w=(2,3), w^perp=(-3,2).

So the smallest possible counterexample is realised: a genuine member of the barrier
family whose *only* failure is a single square corner. This is the cleanest possible
statement that the square-corner constraint is the first thing the barrier misses.
Saved as `certificate_n200.npz`.

### 7. How much of the difficulty does the square-corner constraint capture?
Randomised-greedy maxima (EMPIRICAL — heuristic lower bounds only, never a status change):

| n | iso-free | square-corner-free | classical-corner-free | sq/iso | sq/n |
|---|---------|--------------------|-----------------------|--------|------|
| 20 | 24 | 39 | 110 | 1.63 | 1.95 |
| 30 | 34 | 67 | 212 | 1.97 | 2.23 |
| 40 | 45 | 87 | 329 | 1.93 | 2.18 |
| 60 | 65 | 140 | 627 | 2.15 | 2.33 |
| 80 | 89 | 195 | - | 2.19 | 2.44 |
| 120 | 131 | 296 | - | 2.26 | 2.47 |
| 160 | 171 | 410 | - | 2.40 | 2.56 |
| 240 | - | 652 | - | - | 2.72 |
| 320 | - | 888 | - | - | 2.78 |

Greedy corner-free grows like n^1.59 (true answer n^{2-o(1)}); greedy iso-free like n^0.95
(true answer n^{1-o(1)}); greedy **square-corner-free stays at ~2.5n and creeps up only
sub-logarithmically**. So at the greedy level the square-corner constraint already costs
almost everything that full isosceles-freeness costs, and costs vastly more than classical
corner-freeness. EMPIRICAL_PATTERN, not evidence of a theorem.

Exact maxima (`exact_small.py`, exhaustive branch and bound; C(n) values independently
reproduce the sealed 4,6,7,9):

| n | C(n) | Q_SQ(n) |
|---|------|---------|
| 3 | 4 | 4 |
| 4 | 6 | 6 |
| 5 | 7 | 9 |
| 6 | 9 | 11 |
