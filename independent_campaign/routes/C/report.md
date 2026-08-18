# Route C — C(n): maximum subsets of the n x n grid with all distances-from-a-point distinct

**Status: LIVE DOCUMENT. Appended continuously; assume termination at any moment.**

## Problem

C(n) = max |S|, S subset of {0,...,n-1}^2, such that there are NO three distinct a,b,c in S with
d(a,b) = d(b,c). Equivalently: for every b in S, the |S|-1 distances from b to S\{b} are pairwise
distinct. Degenerate (collinear) triples count, so b may not be the midpoint of two other points.
All arithmetic uses SQUARED distances (integers); no floating point anywhere.

Combinatorially: S is an independent set in the 3-uniform hypergraph on the n^2 cells whose edges
are {a,b,c} with d(a,b)=d(b,c) for some labelling ("no isosceles triangle, degenerate included").

## Environment

D:/Others/iso6/routes/C/ ; Windows 10; gcc 14.2.0 (MSYS2 UCRT64); Python 3.12.7 + numpy 1.26.4;
20 logical cores. Isolated run: no external retrieval, no sibling-route material consulted.

## Inherited artefacts (pre-existing, from killed earlier runs)

No source code survived, so no method could be recovered; nothing here is inherited as trusted.
Two logs each claimed OPT 20 on the 12x12 board:

- n12.log:          (0,0)(11,11)(10,11)(9,10)(8,10)(1,3)(11,8)(3,11)(11,7)(1,6)(5,10)(10,6)(1,2)(0,8)(0,7)(5,1)(4,11)(0,1)(4,0)(3,0)
- logs/n12_run1.log:(0,0)(0,3)(0,4)(1,0)(1,5)(2,1)(3,1)(6,1)(6,10)(7,0)(7,11)(8,0)(8,11)(10,5)(10,8)(10,9)(11,3)(11,4)(11,10)(11,11)

Treated as UNVERIFIED CLAIMS until re-derived below.

---

## 1. Method A (primary exhaustive solver)

Source: `src/solveA.c` (single-thread) and `src/solveAmt.c` (identical search, OpenMP over root
tasks). Exact integer squared distances throughout.

**Search space.** All subsets of the R x C grid. The DFS picks cells in increasing row-major index
order, so every subset is reached exactly once as an increasing index sequence; nothing is skipped
except by the two prunings below.

**Candidate invariant.** The DFS carries a bitset `cand` with the invariant: *every cell in `cand`
is individually addable to the current partial set S* (S+{u} is still isosceles-free) *and has index
greater than every element of S*. When cell v is added, the exact set of conditions that can newly
fail for a candidate u is:

1. apex b in S: `d(b,u) = d(b,v)`  -> forbid `circle[b][d(b,v)]`
2. apex v:      `d(v,u) = d(v,b)`  -> forbid `circle[v][d(v,b)]`
3. apex u:      `d(u,v) = d(u,b)`  -> forbid `bisect[v][b]` (integer perpendicular bisector)

for every b in S. Nothing else can change, because all other triples lie inside S+{u} which was
already checked, so the filter drops no addable cell (completeness) and keeps no non-addable cell
(soundness). `circle[a][r]` and `bisect[a][b]` are precomputed exact-integer bitmasks; the child
candidate set is three bitwise ANDNOTs per element of S.

**Bound.** Any completion of S is contained in S union cand, so `|S| + popcount(cand)` is a valid
upper bound for the subtree; prune when it is <= best. Inside the candidate loop the residual set
only shrinks, so once the bound fails for one branch it fails for all later ones (`break` is sound).

**Symmetry reduction (optional, root only).** Let T be the lexicographically smallest (as a sorted
index sequence) image of S under the board's symmetry group G (D4 for squares, order 4 for
rectangles). Then
  (i) the minimum-index cell c of T is minimal in its own G-orbit -- otherwise some h with
      idx(h(c)) < idx(c) would give min-idx(hT) < min-idx(T), so hT <_lex T, contradiction;
  (ii) the second-smallest cell d of T satisfies idx(d) <= idx(g(d)) for every g in Stab(c) --
      because gT still has minimum c and contains g(d), so second(gT) <= idx(g(d)), while
      lex-minimality gives idx(d) <= second(gT).
Hence every orbit of optimal sets has a representative satisfying both restrictions, and imposing
them at the root loses no optimum. (The decisive 12x12 upper-bound run below is nevertheless run
with symmetry DISABLED, so the certificate does not depend on this argument at all.)

## 2. Independent verifier

`src/verify.py` -- deliberately naive: for every ordered triple of distinct points (a,b,c) it tests
`d(a,b) != d(b,c)` with exact integer squared distances. It shares no code, no data structures and
no masks with the solver.

Both inherited 12x12 sets check out:
```
n12.log set            size=20  bbox=[0..11]x[0..11]  VALID
logs/n12_run1.log set  size=20  bbox=[0..11]x[0..11]  VALID
```
=> **C(12) >= 20 is certified** (two independent witnesses, verified by the naive checker).

## 3. Re-derivation of C(1..11)  [VERIFIED_COMPUTATIONAL_RESULT]

Method A, complete search from `best = 0`, symmetry reduction on. Exhaustive because the DFS
enumerates every increasing index sequence and only prunes with the valid bound above.

| n  | C(n) found | supplied | agree | search nodes | time (1 thread) |
|----|-----------|----------|-------|--------------|-----------------|
| 1  | 1  | 1  | yes | 0             | 0.00 s |
| 2  | 2  | 2  | yes | 1             | 0.00 s |
| 3  | 4  | 4  | yes | 9             | 0.00 s |
| 4  | 6  | 6  | yes | 86            | 0.00 s |
| 5  | 7  | 7  | yes | 954           | 0.00 s |
| 6  | 9  | 9  | yes | 8 256         | 0.00 s |
| 7  | 10 | 10 | yes | 105 061       | 0.00 s |
| 8  | 13 | 13 | yes | 936 612       | 0.01 s |
| 9  | 16 | 16 | yes | 8 502 693     | 0.11 s |
| 10 | 18 | 18 | yes | 94 970 650    | 1.28 s |
| 11 | 18 | 18 | yes | 1 916 068 651 | 40.30 s |

**NO DISAGREEMENT with the supplied values C(1..11) = 1,2,4,6,7,9,10,13,16,18,18.**

## 4. PRIORITY ZERO — CERTIFICATE FOR C(12) = 20   [VERIFIED_COMPUTATIONAL_RESULT]

### 4.1 Lower bound C(12) >= 20

Three mutually distinct 20-point sets are known (two inherited, one produced from scratch by
Method A). All three pass the independent naive verifier `src/verify.py`. Witness produced by this
run (Method A, from `best=0`):

```
(0,0) (0,11) (1,0) (1,4) (1,7) (1,11) (2,1) (2,10) (3,1) (3,5)
(3,6) (3,10) (9,1) (9,10) (10,0) (10,4) (10,7) (10,11) (11,5) (11,6)
```
`verify.py` -> `size=20 bbox=[0..11]x[0..11] VALID`.

### 4.2 Upper bound: no 21-point set exists

Two complete searches, the decisive one carried out **without any symmetry reduction**:

| run | symmetry | start `best` | result | nodes | wall (20 threads) |
|-----|----------|--------------|--------|-------|-------------------|
| A-scratch | D4 root reduction | 0  | OPT **20** | 27 686 483 095 | 97.2 s |
| A-nosym   | **none**          | 20 | OPT **20** (no improvement found) | 45 922 791 007 | 152.0 s |

`logs/A_n12_scratch.log`, `logs/A_n12_nosym21.log`.

**Why the A-nosym run is exhaustive.** It enumerates every subset of the 144 cells as a strictly
increasing sequence of cell indices; a subset is abandoned only when
`|S| + popcount(cand) <= 20`, i.e. only when *no* completion of S can have 21 or more points
(cand is a superset of every legal extension, by the candidate invariant of section 1). No root
cell, no cell pair and no symmetry class is excluded -- the root loop runs over all
144*143/2 ordered-by-index pairs (7 750 survive the trivial `2 + (N-1-v1) <= 20` cutoff, which
merely says the remaining cells are too few). The run terminated normally having never raised
`best` above 20. Therefore **no 21-point set exists in the 12x12 grid**, and the correctness of the
symmetry argument of section 1 is *not* needed for the upper bound.

### 4.3 Conclusion

**C(12) = 20.** VERIFIED_COMPUTATIONAL_RESULT. This confirms the two earlier, uncertified runs, and
sits inside the supplied bracket 20 <= C(12) <= 23 at its lower end.

## 5. Exhaustive enumeration of ALL maximum sets, small n   [VERIFIED_COMPUTATIONAL_RESULT]

`src/solveAdump.exe n n (C(n)-1) --dump C(n) --nosym` enumerates *every* subset of size C(n)
(pruning only on `|S|+|cand| <= C(n)-1`, which can never discard a set of size C(n)).
Saved in `sets/n{8,9,10}_all_max.txt`.

| n  | C(n) | # maximum sets | # orbits under D4 | note |
|----|------|----------------|-------------------|------|
| 8  | 13   | 48  | 6 | all orbits free (48 = 6*8) |
| 9  | 16   | 4   | 1 | **unique up to symmetry**, stabiliser of order 2 |
| 10 | 18   | 8   | 1 | **unique up to symmetry**, trivial stabiliser |

The n=9 optimum (unique, 16 points) is a strikingly rigid object:
```
(0,1)(0,3)(0,4)(0,6) (2,0)(2,7) (3,0)(3,7) (5,0)(5,7) (6,0)(6,7) (8,1)(8,3)(8,4)(8,6)
```
Rows 0 and 8 carry the 4-point Salem-Spencer-type block {1,3,4,6} (a perfect-difference-free
pattern), and the middle is a pair of vertical "walls" in columns 0 and 7 at rows {2,3,5,6}
-- the SAME pattern {2,3,5,6} = {1,3,4,6}+1 . Rows 1,4,7 and columns 2,5 are completely empty.

The n=10 optimum (unique, 18 points):
```
(0,1)(0,2)(0,6)(0,7) (2,2)(2,3)(2,5)(2,6) (5,0)(5,8) (8,0)(8,1)(8,7)(8,8) (9,2)(9,3)(9,5)(9,6)
```
18 points in **5 rows only** (row occupancy 4,4,4,4,2 -- FIVE of the ten rows are empty),
while the columns are spread 3,3,2,2,2,2,2,2 over 8 of 10 columns.


## 6. C on k x n rectangles   [VERIFIED_COMPUTATIONAL_RESULT, exhaustive for every entry listed]

Method A, complete search from `best=0`, D4/Klein symmetry reduction at the root only.
Every listed value is an exhaustive optimum, not a "best found".

### k = 1 : this is exactly r_3(n) (max 3-AP-free subset of {0..n-1})

Two points in a row plus a third midway is an isosceles (degenerate) triple with the middle point
as apex; conversely a 3-AP-free column set has all distances from each point distinct. So
`C(1,n) = r_3(n)` **identically**, and this is a strong external check on the solver:

```
n    : 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17
C(1,n): 1  2  2  3  4  4  4  4  5  5  6  6  7  8  8  8  8
n    :18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34
C(1,n): 8  8  9  9  9  9 10 10 11 11 11 11 12 12 13 13 13
```
This reproduces the classical Salem-Spencer / Erdos-Turan sequence (1,2,2,3,4,4,4,4,5,5,6,6,7,8,
8,8,8,8,8,9,9,9,9,10,10,11,11,11,11,12,12,13,13,13) exactly. **Independent confirmation that the
solver's notion of "isosceles" and its enumeration are right.**

### k = 2

```
n    : 2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
C(2,n): 2  4  4  4  6  6  8  8  8  8 10 10 12 12 12 14 14 16 16
n    :21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38
C(2,n):16 16 16 16 17 18 18 18 20 20 20 20 22 22 22 24 24 24
```

### k = 3

```
n    : 3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
C(3,n): 4  4  6  8  8  8  9 10 10 11 12 12 13 14 16 16 16 16 17 17 18 18 19 19
```

### k = 4

```
n    : 4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
C(4,n): 6  6  8  8  9 10 11 12 12 13 14 15 16 16 17 18 18
```

### k = 5

```
n    : 5  6  7  8  9 10 11 12 13 14 15 16 17 18
C(5,n): 7  8 10 10 12 12 13 14 14 16 16 18 18 20
```

### k = 6

```
n    : 6  7  8  9 10 11 12 13 14 15 16
C(6,n): 9 10 12 12 14 16 16 16 18 18 18
```

### Square diagonal (k = n), for reference

```
n   : 1 2 3 4 5 6 7  8  9 10 11 12
C(n): 1 2 4 6 7 9 10 13 16 18 18 20
```

### Where the density is lost  [EMPIRICAL_PATTERN]

Density C(k,n)/(kn) at n = 16:  k=1: 8/16 = .500 ; k=2: 12/32 = .375 ; k=3: 14/48 = .292 ;
k=4: 16/64 = .250 ; k=5: 18/80 = .225 ; k=6: 18/96 = .188 ; and the square C(12)/144 = .139.
Adding a row is worth much less than the previous one: at n=16 the marginal gains are
8, 4, 2, 2, 2, 0 as k goes 1..6. The loss is *not* concentrated in one direction -- it
accumulates as soon as a second dimension exists, then decays roughly like a constant per row.

`C(k,n) - C(k-1,n)` at n=16: 4, 2, 2, 2, 0 for k = 2..6. **EMPIRICAL_PATTERN only** -- these are
tiny n and say nothing about asymptotics.

## 7. Increments, ratios, and a rigorous (but weak) counting upper bound

| n | C(n) | C(n)-C(n-1) | C(n)/n | D(n)=#distinct squared distances in [n]^2 | rigorous bound C(n) <= D(n)+1 |
|---|------|-------------|--------|------------------------------------------|-------------------------------|
| 1 | 1  | -  | 1.0000 | 0   | 1   |
| 2 | 2  | 1  | 1.0000 | 2   | 3   |
| 3 | 4  | 2  | 1.3333 | 5   | 6   |
| 4 | 6  | 2  | 1.5000 | 9   | 10  |
| 5 | 7  | 1  | 1.4000 | 14  | 15  |
| 6 | 9  | 2  | 1.5000 | 19  | 20  |
| 7 | 10 | 1  | 1.4286 | 26  | 27  |
| 8 | 13 | 3  | 1.6250 | 33  | 34  |
| 9 | 16 | 3  | 1.7778 | 41  | 42  |
| 10| 18 | 2  | 1.8000 | 50  | 51  |
| 11| 18 | **0** | 1.6364 | 60  | 61  |
| 12| 20 | 2  | 1.6667 | 70  | 71  |
| 16| 28 | -  | 1.7500 | 119 | 120 |
| 27| 48 | -  | 1.7778 | 314 | 315 |
| 32| 56 | -  | 1.7500 | 430 | 431 |

Ratios where both values are available:
`C(2)/C(1)=2.000, C(4)/C(2)=3.000, C(6)/C(3)=2.250, C(8)/C(4)=2.167, C(10)/C(5)=2.571,
C(12)/C(6)=2.222, C(16)/C(8)=2.154, C(32)/C(16)=2.000.`

**The counting upper bound (proved).** Fix `r`. Because every point of `S` has *pairwise distinct*
distances to the rest of `S`, each point has **at most one** partner at squared distance `r`;
i.e. for every `r`, the "distance-`r` graph" induced on `S` is a **perfect-matching-or-less**
(max degree <= 1). Hence
```
  |S|(|S|-1)/2 = sum_r m_r  <=  D(n) * floor(|S|/2)   =>   C(n) <= D(n) + 1.
```
Since `D(n) ~ K n^2 / sqrt(log n)` (Landau-Ramanujan), this bound is `n^{2-o(1)}` while the data
say `C(n) ~ 1.75 n`. So the counting bound is nowhere near tight -- the binding constraint is
geometric, not a distance-budget. **This is the single most useful structural fact found for an
upper-bound attack: for every r, the distance-r graph on S is a matching, so m_r <= |S|/2, and the
measured multiplicities below show how close to that ceiling the extremal sets actually get.**

`C(11) - C(10) = 0` is the only zero increment in the range: **C(11)=C(10)=18** although the board
grows by 21 cells. EMPIRICAL_PATTERN. `C(n)/n` sits in [1.63, 1.80] for all n >= 8, and equals
exactly 1.75 at n = 16 and n = 32. Small-n data; **this proves nothing about the asymptotics.**

## 8. Structure of extremal 2 x n sets: a PRODUCT law with exactly one exception
   [VERIFIED_COMPUTATIONAL_RESULT for the C values; EMPIRICAL_PATTERN for the law]

Let `g2(n)` = the largest subset `A` of `{0,...,n-1}` that is **3-AP-free** *and* has **no two
consecutive elements** (min gap >= 2). Then `{0,1} x A` is always a valid set, because for an apex
`(0,a)` the distances are `(a-a')^2` and `1+(a-a')^2`; distinctness within each family is exactly
3-AP-freeness, and the only way the two families can collide is `(a-a')^2 = 1 + 0`, i.e. `a'` a
neighbour of `a` -- which the gap-2 condition forbids. So `C(2,n) >= 2 g2(n)`.

Measured (exhaustive C values, brute-force `g2`):

| n | 2..24 | 25 | 26..38 |
|---|-------|----|--------|
| `C(2,n)` vs `2*g2(n)` | **equal for every n** | `C(2,25)=17 > 16 = 2*g2(25)` | **equal for every n** |

```
n     : 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 ...
C(2,n): 2 4 4 4 6 6 8 8  8  8 10 10 12 12 12 14 14 16 16 16 16 16 16 17 18 ...
2*g2(n):2 4 4 4 6 6 8 8  8  8 10 10 12 12 12 14 14 16 16 16 16 16 16 16 18 ...
```
Verified optimal 2x25 witness of size **17** (checked by `verify.py`), the ONLY size in the range
that is odd and the ONLY place the product law fails:
```
(0,0)(0,1)(0,5)(0,7)(0,11)(0,16)(0,18)(0,23)(0,24)
(1,2)(1,5)(1,7)(1,11)(1,13)(1,16)(1,18)(1,22)
```
Note it even uses two *adjacent* cells (0,0),(0,1) in the same row -- impossible in a product.

Sample verified extremal products:
```
2x8 : A={0,2,5,7}                       2x20: A={0,2,5,7,11,13,16,18}
2x30: A={0,2,5,7,11,16,19,23,26,28}     2x36: A={0,2,5,9,11,19,21,24,26,30,32,35}
```
So **for k=2 the extremal configuration is a product `{0,1} x A`**, not a graph of a function and
not a Sidon set. For k=1 it is exactly a Salem-Spencer (3-AP-free) set. For k >= 3 the product
structure breaks (see next section).

## 9. Structure of extremal k x n sets for k >= 3: reflection-symmetric row pairs
   [C values VERIFIED_COMPUTATIONAL_RESULT; the structural law is EMPIRICAL_PATTERN]

Generalised product law (proved): `{0,h} x A` is valid iff `A` is 3-AP-free **and** `A` contains
no pair `a',a''` with `|a-a'|^2 - |a-a''|^2 = h^2` for some `a in A` (difference-of-two-squares
collisions). For `h=1` and `h=2` the only solution of `u^2 - v^2 = h^2` with `v >= 0` is
`(u,v)=(h,0)`, so the extra condition is simply "no two elements at distance `h`".

Exhaustive optima found (all verified by the solver, several spot-checked with `verify.py`):

```
3x17 -> 16 = {0,2} x {0,1,4,5,11,12,15,16}          PURE PRODUCT, only rows 0 and 2 used, h=2
4x16 -> 16   rows 0,1,3 used                        not a product
5x18 -> 20   row0=row4={0,2,15,17}, row1=row3={0,5,8,9,12,17}   (row 2 EMPTY)
6x16 -> 18   row0=row4={0,2,3,9,11}, row1=row3={5,9,14,15}      (rows 2,5 EMPTY)
```
The `5x18` and `6x16` optima are *reflection-symmetric*: the occupied rows are `{0,1,3,4}` and the
set is invariant under `x -> 4-x`, being a union of two "doubled layers"
`{0,4} x B  union  {1,3} x D`. This is the recurring motif: **extremal sets pair up identical rows
at a fixed vertical offset and leave whole rows empty**, rather than spreading points evenly.
EMPIRICAL_PATTERN.

Nothing looks like a graph of a function (row occupancies of 4 are common), nothing is a Sidon set
(the autocorrelation `|S cap (S-v)|` reaches 8 in the unique 10x10 optimum -- a Sidon set would
have max 1), and there is no Behrend/sphere structure visible: the popular squared distances are
the SMALL ones (`r^2 = 1, 2, 5`), not a single large shell.
