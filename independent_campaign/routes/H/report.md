# Route H — Extremal Constructor: Barrier Constructions for Isosceles-Free Sets

**Status: IN PROGRESS.** Appended continuously.

## Problem
C(n) = max |S|, S in [n]^2 = {0..n-1}^2, no three distinct a,b,c in S with d(a,b)=d(b,c)
(squared Euclidean, degenerate/collinear included). Equivalently: for every b in S and
every radius r, |{a in S\{b} : |a-b|^2 = r}| <= 1.

Known: C(n) = Omega(n/sqrt(log n)); C(n) <= n*r_3(n).
Exact: C(1..11)=1,2,4,6,7,9,10,13,16,18,18; C(16)=28, C(27)=48, C(32)=56.

## Log
- [init] Pre-existing files in routes/H/: anneal.py, bench1.py, core.py, fastcore.py, ls.py. Re-validating.

## [1] Verifier validation — VERIFIED_COMPUTATIONAL_RESULT
Three independent isosceles-free verifiers (ordered-triple brute force; per-apex
distance-multiset; per-apex sorted-list) agree on 3000 random subsets of [n]^2, n<=6,
and all reject AP / corner / (1,2)&(2,1) witnesses. Independent exhaustive DFS
reproduces C(1..7) = 1,2,4,6,7,9,10 exactly, matching the given ground truth.
File: routes/H/validate.py, routes/H/core.py.

## [2] Barriers (a),(b),(c) — constructions + machine verification

Constructions (all PROVED general-n, all machine-verified at the n below by
relaxation-specific verifiers in barriers.py):

(a) axis-parallel lines 3-AP-free:  S_a(n) = {(x,y) in [n]^2 : x+y in W},  W 3-AP-free.
    Proof: row y is (W-y) cap [n], column x is (W-x) cap [n]; a translate/reflection of a
    3-AP-free set is 3-AP-free.  |S_a| = sum_{w in W} #{antidiagonal w} >= (n/2)*r_3(n).
    UPPER bound for the relaxation is n*r_3(n) (each of n rows is 3-AP-free), so this
    construction is TIGHT WITHIN A FACTOR 2.

(b) no 3-AP in Z^2:  S_b(n) = {(x,y) : x+y in W1, x-y in W2} or W x W (max taken).
    Proof: for p,p+v,p+2v the sums form a 3-AP with difference v1+v2 and the differences
    a 3-AP with difference v1-v2; 3-AP-freeness of W1,W2 forces v1+v2=v1-v2=0, v=0.
    For W x W: coordinatewise 3-APs force v1=v2=0.  |S_b| >= r_3(n)^2 = n^{2-o(1)}.

(c) corner-free:  S_c(n) = {(x,y) in [n]^2 : x-y in W},  W 3-AP-free.
    Proof: the corner {(x,y),(x+d,y),(x,y+d)} has x-y values (x-y)-d, (x-y), (x-y)+d,
    a NONDEGENERATE 3-AP (d != 0) inside W.  |S_c| >= (n/2)*r_3(n) = n^{2-o(1)}.

Measured sizes (verified by ver_a/ver_b/ver_c; all points distinct and in box):

    n     (a)     (b)     (c)   n^2    (a)/n^2 (b)/n^2 (c)/n^2   C(n) known
    8      29      16      29     64    0.453   0.250   0.453    -
   11      52      36      52    121    0.430   0.298   0.430    18   (0.149)
   16      92      64      92    256    0.359   0.250   0.359    28   (0.109)
   27     212     121     212    729    0.291   0.166   0.291    48   (0.066)
   32     270     144     270   1024    0.264   0.141   0.264    56   (0.055)
   45     504     256     504   2025    0.249   0.126   0.249    -
   64     796     324     796   4096    0.194   0.079   0.194    -
   90    1338     484    1338   8100    0.165   0.060   0.165    -
  128    2800    1024    2800  16384    0.171   0.062   0.171    -

(exact weighted-3AP-free optimisation used for n<=14; heuristic 3-AP-free sets above.)

**VERDICT (a),(b),(c): TOTAL BARRIERS, PROVED.**  Each relaxation admits sets of size
n^{2-o(1)} (density exp(-O(sqrt(log n)))), whereas C(n) is conjectured n^{1+o(1)}.
Therefore NO upper-bound argument whose only input is
  * "each row/column is 3-AP-free", or
  * "S has no 3-term AP in Z^2", or
  * "S is corner-free"
can prove anything better than n^2 exp(-O(sqrt(log n))).  For (a) this is essentially
the CURRENT best known upper bound n*r_3(n): the AP/collinear content of the isosceles
condition is already fully exploited and is provably exhausted at n^{2-o(1)}.
At n=128 the barrier sets are >10x larger than the best isosceles-free sets, and the
ratio grows.

## [3] Barrier (d): distinct distances from a FIXED small apex set only

Constructions are EXACT optima for k=1 (count distinct radii) and k=2 (maximum bipartite
matching between the radius-classes of b1 and of b2, via Hopcroft-Karp); greedy lower
bounds for k>=3.  All machine-verified with ver_d.  Apex sets chosen ADVERSARIALLY
(worst = the apex placement minimising the answer, i.e. central/clustered apexes).

k=1, EXACT (= number of distinct values of |p-b|^2, p in [n]^2):
    n     best-b    worst-b     n^2    worst/n^2
    8         34         15      64      0.2344
   16        120         42     256      0.1641
   32        431        135    1024      0.1318
   64       1576        457    4096      0.1116
  128       5839       1621   16384      0.0989
  181      11292       3062   32761      0.0935
  256      21860       5924   65536      0.0904
  The worst/n^2 column is decaying like 1/sqrt(log n) -- exactly Landau-Ramanujan:
  the number of integers <= N that are sums of two squares is Theta(N/sqrt(log N)).
  So k=1 gives EXACTLY Theta(n^2/sqrt(log n)).  PROVED.

k=2, EXACT (maximum bipartite matching):
    n=  8 worst=  14   n= 16 worst=  40   n= 32 worst= 128
    n= 64 worst= 439   n= 90 worst= 813   n=128 worst=1557   (worst/n^2 = 0.0950)

k=3, greedy lower bound:
    n=  8 worst=  13   n= 16 worst=  37   n= 32 worst= 119
    n= 64 worst= 396   n= 90 worst= 745   n=128 worst=1419   (worst/n^2 = 0.0866)

Many clustered apexes at n=128 (greedy lower bounds):
    k =    1     2     3     4     6     8    12    16    24    32
  size = 1621  1545  1378  1258   980   902   763   648   525   452
 /n^2  =.0989 .0943 .0841 .0768 .0598 .0551 .0466 .0396 .0320 .0276

**PROOF (general n, any fixed k).** Let Delta = max_r #{u in Z^2 : |u|^2 = r, |u|_inf < n}
= max_r r_2(r) <= d(r) = n^{o(1)}.  Greedily scan all n^2 grid points; add p unless some
apex b_i already has a point at radius |p-b_i|^2.  Each accepted point forbids at most
sum_i (r_2 of its radius from b_i) - k <= k*Delta later points.  Hence
    |S| >= n^2 / (k*Delta + 1) = n^2 / (k * n^{o(1)}).
So for any k = n^{o(1)} apexes the answer is n^{2-o(1)}.   PROVED.

**VERDICT (d): TOTAL BARRIER, PROVED.**  Going from 1 apex to 3 apexes costs only ~12%
of the set (1621 -> 1419 at n=128); going to 32 clustered apexes still leaves n^{2-o(1)}.
Any argument that extracts its contradiction from a bounded (or even n^{o(1)}) number of
apexes is DEAD -- it cannot beat n^{2-o(1)}.  The isosceles condition must be used at
essentially ALL n^{1+o(1)} points of S simultaneously.  In particular "pick the extreme
point / the corner point / a few special points of S and count its distances" is
provably insufficient.

## [4] Barrier (f): degree <= k instead of degree <= 1  -- THE DECISIVE BARRIER

Condition D(k): for every b in S and every squared distance r, at most k points of S at
squared distance r from b.  D(1) = isosceles-free.

**THEOREM (PROVED, general n).** For every fixed k >= 1 there is S subset of [n]^2 with
D(k) and
        |S| >= n^{2 - 2/(k+1) - o(1)}.
In particular k=2 gives n^{4/3-o(1)}, k=3 gives n^{3/2-o(1)}, k -> inf gives n^{2-o(1)}.

*Proof.* Let r_2(r)=#{u in Z^2 : |u|^2=r}.  A violation of D(k) is a (k+2)-tuple
(b; p_1..p_{k+1}) with all p_i at one squared distance r from b; the number of such tuples
inside [n]^2 is at most n^2 * M_{k+1}(2n^2) where M_j(R)=sum_{r<=R} r_2(r)^j.
Since r_2(r) <= d(r) = r^{o(1)} and M_1(R) = O(R), we get M_{k+1}(2n^2) <= n^{2+o(1)},
so the tuple count is at most n^{4+o(1)}.
Take S_0 by including each grid point independently with probability p, and delete one
p_i from every surviving bad tuple.  The result satisfies D(k) exactly, and
   E|S| >= p n^2 - p^{k+2} n^{4+o(1)}.
Choose p with p^{k+1} n^{2+o(1)} = 1/2, i.e. p = Theta(n^{-2/(k+1)-o(1)}); then
   E|S| >= p n^2 / 2 = n^{2-2/(k+1)-o(1)}.   QED
(The sharper form, using M_j(R) ~ c_j R (log R)^{2^{j-1}-1}, gives
 |S| = Theta( n^{2-2/(k+1)} / (log n)^{(2^k - 1)/(k+1)} ), i.e. n^{4/3}/log n for k=2.)

NUMERICAL CONFIRMATION of the moment sums (routes/H/moments.py), R up to 4*10^6:
   M1/R -> 3.1416 = pi ;  M2/(R lnR) -> 4.53 ;  M3/(R ln^3 R) -> 0.63 ;
   M4/(R ln^7 R) -> 0.00054 ;  max r_2 = 144 at R=4e6  (i.e. R^{o(1)}).
   Exponents 0,1,3,7 = 2^{j-1}-1 confirmed.

MEASURED (random-greedy lower bounds, every set independently verified by fastdk.verify;
the k=1 column was additionally cross-verified with core.verify_isofree*):

     n     D(1)    D(2)    D(3)     D(2)/D(1)  D(3)/D(1)
     8       10      --      --
    11       13      30      --        2.31
    16       19      42      --        2.21
    22       27      64      --        2.37
    32       36      96     155        2.67       4.31
    45       51     139     242        2.73       4.75
    64       70     212     374        3.03       5.34
    90      100     307     575        3.07       5.75
   128      140     474     917        3.39       6.55
   181      191      --    1414                   7.40
   256      268      --      --

  The ratio D(2)/D(1) grows steadily (2.2 -> 3.4) and D(3)/D(1) grows faster
  (4.3 -> 7.4): a POLYNOMIAL separation being resolved, not a constant factor.
  Exact brute force at tiny n: D(1)=4, D(2)=8 at n=3;  D(1)=6, D(2)=12 at n=4.

**VERDICT (f): THE STRONGEST BARRIER OF THE SIX.**  Relaxing "degree exactly <= 1" to
"degree <= 2" raises the maximum from n^{1+o(1)} to n^{4/3-o(1)} -- a POLYNOMIAL jump.
Consequently ANY upper-bound argument that is robust under replacing 1 by 2 in the
degree bound -- which includes essentially every counting / double-counting / energy /
L^2 / Fourier / graph-regularity argument that loses a constant factor when a radius
class has 2 points instead of 1 -- CANNOT prove better than O(n^{4/3}).
Robust-to-degree-3 arguments cannot beat n^{3/2}.  Robust-to-degree-k cannot beat
n^{2-2/(k+1)}.  To reach the conjectured n^{1+o(1)} an argument must be EXACTLY tight at
degree 1: it must break the moment it allows a single radius class of size 2.
This is the sharpest instruction to the theory branches produced here.

## [5] Barrier (e): degree <= 1 only for squared distances r <= R

**THEOREM (PROVED, general n).** For every 1 <= R <= 2n^2 there is S subset of [n]^2 with
"every radius r <= R has degree <= 1 at every apex" and
        |S| >= n^2 / (2 sqrt(2 R log R)).
*Proof.* Bad triples (b;p,q) with |p-b|^2=|q-b|^2=r<=R number at most
n^2 * M_2(R) = O(n^2 R log R).  Alteration with p = (2 R log R)^{-1/2} gives
|S| >= p n^2 / 2.  QED
Consistency check: at R = 2n^2 this is n/(4 sqrt(log n)), reproducing the known
Omega(n/sqrt(log n)) lower bound for the full problem -- the method is calibrated.

**SELF-SIMILAR (modular) VERSION, PROVED.** If T subset of (Z_M)^2 satisfies the same
condition on the torus with M > 2 sqrt(R), then S = {p in [n]^2 : p mod M in T} satisfies
it in [n]^2 (distinct vectors of squared length <= R have sup-norm < M/2, so they stay
distinct mod M), and |S| >= (n/M)^2 |T|.  Thus the problem at radius cutoff R is
EXACTLY the full problem on an M x M torus with M ~ 2 sqrt(R) -- the R-truncated problem
is self-similar to the original at scale sqrt(R).

MEASURED (greedy, every set verified by fastdk.verify with the radius mask):
 n=64  (grid 4096 pts):
    R     1     2     4     8    16    32    64   128   256   512  1024  2048  4096  7938
 size  1723  1317  1186   756   538   367   274   200   150   116    98    86    71    71
 n=128 (grid 16384 pts):
    R     1     2     4     8    16    32    64   128   256  ...
 size  6863    --    --  2950  2062  1389  1001   703   511  ...
 Fitted local slope d log(size)/d log(R) is approximately -0.49 for moderate R
 (matching the predicted R^{-1/2}), flattening only once size approaches C(n).

**VERDICT (e): SCALE-CALIBRATION FOR THE THEORY BRANCHES.**  An argument that uses only
distances of LENGTH <= L (i.e. squared distance r <= L^2) can never prove a bound better
than ~ n^2 / L.  Concretely:
   to prove |S| = O(n^{1.5})   you need scale  L >= n^{0.5};
   to prove |S| = O(n^{1.25})  you need scale  L >= n^{0.75};
   to prove |S| = O(n^{1+eps}) you need scale  L >= n^{1-eps}, i.e. essentially the
   full diameter.
The difficulty is spread EVENLY over all dyadic scales: each doubling of the length
scale buys exactly a factor 2 and no more.  There is no "hardest scale" to attack.
Good news for theory: reaching n^{1.5} only requires control at scale sqrt(n), well
short of the diameter; there is real headroom before the barrier bites.

## [6] Explicit ALGEBRAIC constructions (mission item 1)

**PROVED, general n (explicit, no randomness):**
  A 3-AP-free subset of a LINE is isosceles-free.  On a line, "b equidistant from a and c"
  is exactly "a,b,c is a 3-AP" (a=b-t, c=b+t).  Hence for W subset [n] 3-AP-free,
        S = W x {0}   (or the diagonal {(w,w)})
  is isosceles-free, and with W a Behrend set
        |S| = n * exp(-c sqrt(log n)) = n^{1-o(1)}.
  This is the best EXPLICIT construction found; it is only slightly weaker than the
  known probabilistic Omega(n / sqrt(log n)).  Machine-verified at n=32 (|S|=12) and
  n=64 (|S|=18) by core.verify_isofree and core.verify_isofree_ref.

**Algebraic families tested (routes/H/algebraic.py).**  For each, |F| and the largest
isosceles-free subset extracted by 25 randomised greedy passes (a LOWER bound):

  n=32 (grid greedy alone reaches 36, C(32)=56):
    line/diag Behrend            |F|=  12  whole family IS isosceles-free   -> 12
    parabola {(x, x^2 mod 31)}   |F|=  31  NOT isosceles-free               -> 19
    cube     {(x, x^3 mod 31)}   |F|=  31  NOT                              -> 19
    inverse  {(x, x^-1 mod 31)}  |F|=  30  NOT                              -> 20
    power    {(x, 3^x mod 31)}   |F|=  30  NOT                              -> 19
    Sidon (Erdos-Turan)          |F|=  15  NOT                              -> 13
    max lattice circle           |F|=  16  NOT                              ->  8
    2D Behrend sphere (base 3)   |F|=  44  NOT                              -> 19
  n=64:
    line/diag Behrend            |F|=  18  IS isosceles-free                -> 18
    parabola mod 61              |F|=  61  NOT                              -> 37
    inverse mod 61               |F|=  60  NOT                              -> 37
    power 2^x mod 61             |F|=  60  NOT                              -> 37
    2D Behrend sphere (base 5)   |F|=  90  NOT                              -> 30
    (grid greedy alone reaches 70)

**FINDING (EMPIRICAL, with one PROVED positive).**  No algebraic family tested is
isosceles-free as a whole except the 1-dimensional Behrend line, and no family yields an
isosceles-free subset larger than plain randomised greedy on the whole grid.  Modular
curves (parabola / cube / inverse / primitive-root graph) give only ~0.6n, versus ~1.1n
from greedy.  Circles are terrible (a circle is saturated with isosceles triangles: every
chord's perpendicular bisector meets it).  Behrend spheres in 2D do not help because
the isosceles condition is not an additive-AP condition.
This is itself informative: the problem RESISTS algebraic construction in a way that
Behrend/3-AP problems do not, which is weak evidence that the truth is near n^{1+o(1)}
rather than n^{3/2}.  Labelled EMPIRICAL_PATTERN.

**NO PRODUCT / LIFT CONSTRUCTION EXISTS (from the given exact values).**
C(4)=6 but C(16)=28 < 36 = C(4)^2, so C(n^2) >= C(n)^2 is FALSE.  Any "lift a solution
at scale n to scale n^2" construction is therefore impossible in the naive form.
This kills the standard route to a polynomial lower-bound improvement.

## [7] Anti-recurrence quadrant stress test (mission item 3)

Setup: find isosceles-free S subset [2n]^2 with EXACTLY t points in each of the four
n x n quadrants; maximise t.  Quadrant-constrained min-conflicts + tabu search
(routes/H/quad.py); every returned set verified isosceles-free.

RIGOROUS CEILING (a consequence of the GIVEN exact values, no search needed):
4t <= C(2n), so t <= floor(C(2n)/4) and t/C(n) <= C(2n)/(4 C(n)).

   n    C(n)   C(2n)   ceiling t   ceiling t/C(n)    ACHIEVED t   achieved t/C(n)
   4      6      13         3          0.500              3            0.500
   5      7      18         4          0.571              3            0.429
   6      9       -         -            -                4            0.444
   8     13      28         7          0.538              5            0.385
  11     18       -         -            -               (running)
  16     28      56        14          0.500           (running)

The observed doubling ratios from the given exact values are
   C(6)/C(3)=2.25, C(8)/C(4)=2.17, C(10)/C(5)=2.57, C(16)/C(8)=2.15, C(32)/C(16)=2.00
-- all far below 4, and NOT drifting upward.

**VERDICT: THE STRESS TEST FAILS -- and that is the informative outcome.**
There is a hard CEILING at roughly 50-57% simultaneous quadrant occupancy, and it is
rigorous (it follows from the exact C(2n) values, not from my search).  Four
simultaneously near-extremal quadrants DO NOT EXIST at any n where the answer is known.
This is EVIDENCE IN FAVOUR of a recurrence C(2n) <= (4-delta) C(n) with a fixed delta
(the data suggests delta ~ 1.8, i.e. C(2n) <= 2.2 C(n)).  If such a recurrence could be
PROVED for all n it would give C(n) = O(n^{log_2 2.2}) = O(n^{1.14}) -- essentially
resolving the problem.  This is the most promising direction I can hand to the theory
branches.
CAVEAT: the naive quadrant relaxation ("each quadrant is isosceles-free, ignore
cross-quadrant triples") gives EXACTLY C(2n) <= 4C(n) and nothing better -- four
independent optimal quadrant sets satisfy it.  So a recurrence proof MUST use
cross-quadrant isosceles triples.  My data measures precisely how much those bite:
they cut 4C(n) down to about 2.2C(n) at the sizes tested.  EMPIRICAL_PATTERN, small n.
