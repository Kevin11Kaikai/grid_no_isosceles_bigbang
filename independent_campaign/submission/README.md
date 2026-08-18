# `C(12) = 20` for Erdős Problem 6.59 — computational certificate

**Result.** The largest subset of the `12 × 12` grid containing no (possibly degenerate)
isosceles triangle has exactly **20** points. This closes the previously open bracket
`20 ≤ C(12) ≤ 23`.

**Status.** Exhaustive computation, reproduced end-to-end. This is a data point, not a
theorem, and it has no bearing on the asymptotic bounds
`n/√(log n) ≲ C(n) ≲ e^{-c(log n)^{1/9}} n²`.

---

## 0. Contents

```
README.md                    this certificate
COVER.md                     cover note for the problem-database maintainers
verify_independent.py        definition-only verifier + naive exact solver (§6.1)
code/solveA.c                Method A — bitset branch and bound          (§3)
code/solveB.c                Method B — independent second implementation (§6.2)
logs/calibration_A.log       Method A on n = 1..11                       (§5)
logs/calibration_B.log       Method B on n = 8..11                       (§6.2)
logs/n12_scratch.log         n = 12, symmetry on, from best = 0          (§2, §3)
logs/n12_nosym.log           n = 12, NO symmetry, from best = 20         (§3, decisive)
logs/n12_methodB.log         n = 12, Method B, from best = 20            (§6.2, decisive)
logs/verify_independent.log  output of verify_independent.py             (§6.1)
```

No compiled binaries are shipped. Build from source with the commands in §4; every number
in the tables below is backed by the log file named beside it.

Every table in this document is reproduced by rerunning the commands in §4. Node counts
for searches started from `best = 0` vary by a fraction of a percent between runs, because
threads discover improvements to `best` in different orders and prune differently. The two
decisive `n = 12` runs start from `best = 20`, which pins the pruning and makes their node
counts deterministic.

---

## 1. Definition used

`S ⊆ {0,…,n-1}²` is **admissible** iff there are no three *distinct* points `a, b, c ∈ S`
with `d(a,b) = d(b,c)`, where `d` is the **squared** Euclidean distance.

Degenerate (collinear) triples are included, as in the problem statement: three points in
arithmetic progression on a line have the middle point equidistant from the outer two.
Consequently the trace of `S` on every line is 3-AP-free — this is the source of the
calibration test in §5.

`C(n) = max |S|`. All arithmetic is exact integer arithmetic on squared distances; no
floating point is used anywhere, so no rounding can turn an isosceles triple into a
scalene one.

---

## 2. Lower bound: `C(12) ≥ 20`

Four mutually distinct 20-point admissible sets, each checked against the definition by
`verify_independent.py` (which enumerates all `C(20,3) = 1140` triples and all three apex
choices per triple):

```
A  (0,0) (0,1) (0,7) (0,8) (1,2) (1,3) (1,6) (3,0) (3,11) (4,0) (4,11)
   (5,1) (5,10) (8,10) (9,10) (10,6) (10,11) (11,7) (11,8) (11,11)

B  (0,0) (0,3) (0,4) (1,0) (1,5) (2,1) (3,1) (6,1) (6,10) (7,0) (7,11)
   (8,0) (8,11) (10,5) (10,8) (10,9) (11,3) (11,4) (11,10) (11,11)

C  (0,0) (0,11) (1,0) (1,4) (1,7) (1,11) (2,1) (2,10) (3,1) (3,5)
   (3,6) (3,10) (9,1) (9,10) (10,0) (10,4) (10,7) (10,11) (11,5) (11,6)

D  (0,0) (0,5) (0,6) (1,0) (1,4) (1,7) (1,11) (2,1) (2,10) (3,10)
   (8,1) (9,1) (9,10) (10,0) (10,4) (10,7) (10,11) (11,5) (11,6) (11,11)
```

`D` was produced by the re-run recorded in `logs/n12_scratch.log`.

## 3. Upper bound: no 21-point set exists

Branch and bound over the 3-uniform "isosceles" hypergraph on the 144 cells
(`code/solveA.c`). Subsets are enumerated as strictly increasing sequences of cell
indices. The state carries a candidate bitset `cand` whose invariant is *every cell in
`cand` is individually addable to the current partial set `S`*; on adding `v` the three
families of newly-failing cells are removed by pure bitmask ANDs:

```
for each b in S:
    cand &= ~circle[b][d(b,v)]   # b as apex, legs to v and to the new cell
    cand &= ~circle[v][d(v,b)]   # v as apex, legs to b and to the new cell
    cand &= ~bisector[v][b]      # new cell as apex, equidistant from v and b
```

These are exactly the conditions that can newly fail — every other pair was handled when
the later of its two members was added — so the invariant is maintained and nothing
addable is ever dropped. The only pruning is

```
|S| + popcount(cand) ≤ best   ⟹   abandon
```

which is valid because `cand` is a superset of every legal completion of `S`.

**The decisive run uses no symmetry reduction at all.** It starts from `best = 20`, so it
abandons a branch only when that branch provably cannot reach 21 points. It ran to normal
termination without ever raising `best`. No root cell, no cell pair and no symmetry class
is excluded: the root loop enumerates all ordered index pairs `(v₀,v₁)`, of which
`7750` survive the trivial cutoff `2 + (143 - v₁) ≤ 20` (i.e. `v₁ ≤ 124`); and
`Σ_{v₀=0}^{123} (124 - v₀) = 7750` confirms the count. **Therefore the upper bound does
not depend on the correctness of any symmetry argument.**

| run | symmetry | start `best` | result | root tasks | nodes | wall (20 threads) |
|---|---|---|---|---|---|---|
| from scratch | D4 | 0 | OPT **20** | 2 152 | 27 703 965 030 | 51.0 s |
| **decisive** | **none** | 20 | OPT **20**, no improvement | 7 750 | **45 922 791 007** | 81.8 s |

The decisive run's node count is **deterministic** — with `best` pinned at 20 and never
rising, the pruning decisions do not depend on thread scheduling. It reproduced to the
digit across independent runs on different occasions (45 922 791 007 both times), which is
the strongest single reproducibility signal available here. The scratch run's count does
vary slightly between runs, as expected, because threads discover improvements to `best`
in different orders.

**Concurrency note.** `best` is read without a lock. A stale read can only be *smaller*
than the true value, which weakens pruning and makes the search do more work; it can never
cause a branch to be skipped. Increases to `best` are performed under a critical section.

## 4. Reproduction

```
gcc -O3 -march=native -fopenmp -DNWC=4 code/solveA.c -o solveA
./solveA 12 12 0            # from scratch, symmetry on   -> OPT 20
./solveA 12 12 20 --nosym   # decisive upper bound         -> OPT 20, no improvement
python verify_independent.py
```

Roughly two minutes total on 20 threads. Logs of the runs above are in `logs/`.

## 5. Calibration

The solver was re-run from scratch on every grid whose value was already known, and on a
second family with an independently known answer.

| n | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|----|----|
| `C(n)` computed | 1 | 2 | 4 | 6 | 7 | 9 | 10 | 13 | 16 | 18 | 18 |
| known | 1 | 2 | 4 | 6 | 7 | 9 | 10 | 13 | 16 | 18 | 18 |

**No disagreement.** Note `C(10) = C(11) = 18`, so the sequence is not strictly
increasing — a useful sanity check that the search is not silently over-counting.

Second calibration: on a `1 × n` grid the problem degenerates to "no 3-term AP", so
`C(1,n)` must equal `r_3(n)`. The naive solver reproduces the Salem–Spencer sequence
exactly for `n = 1..30`.

## 6. Independent verification

### 6.1 Definition-only checker

`verify_independent.py` shares no code, no data structure and no algorithm with either C
solver:

- **validity** is decided by enumerating all `C(|S|,3)` triples and all three apex choices,
  comparing squared distances — no bitsets, no incremental filtering;
- **small exact values** are recomputed by a plain recursion with *no* candidate set and
  *no* bound beyond "not enough cells remain", re-testing validity from the definition at
  every extension. It cannot inherit a bug from the fast solvers. It is deliberately
  unoptimised and becomes impractical beyond `n = 7`; that is the honest limit of this
  particular cross-check.

Output: all four witnesses `VALID` and pairwise distinct; naive values agree with
`C(1..7)`; `C(1,n) = r_3(n)` for `n = 1..24` with **0 mismatches**.

### 6.2 Second exhaustive implementation (`code/solveB.c`)

Method B differs from Method A in every part that could hide a shared bug:

- **different cell order** — cells relabelled along anti-diagonals, so the search tree has
  a different shape;
- **different validity oracle** — no precomputed circle/bisector masks; candidates are
  tested straight from the definition via per-point tables of used squared distances;
- **different bound** — in addition to `|S| + |cand|`, a row/column 3-AP capacity bound,
  using a precomputed table of the largest 3-AP-free subset of each column mask;
- **no symmetry reduction at all.**

Agreement on every grid both methods can finish, with visibly different search trees:

| n | Method A | Method B | A nodes | B nodes |
|---|---|---|---|---|
| 8 | 13 | 13 | 941 064 | 1 320 054 |
| 9 | 16 | 16 | 6 860 575 | 9 246 938 |
| 10 | 18 | 18 | 91 424 705 | 106 462 783 |
| 11 | 18 | 18 | 1 920 973 219 | 2 456 884 014 |
| **12** | **20** | **20** | 45 922 791 007 | 32 795 784 946 |

Method B was run at `n = 12` from `best = 20`, with no symmetry reduction, and terminated
normally after 1385 s (20 threads) without finding any 21-point set. Its node count is
*lower* than Method A's despite the weaker propagation, because the row/column 3-AP
capacity bound prunes harder — the two searches are genuinely different, and they agree.

**The upper bound `C(12) ≤ 20` therefore rests on two independent exhaustive
implementations, neither of which uses any symmetry argument.**

## 7. What this does and does not establish

Established: `C(12) = 20`, by exhaustive search, reproduced from scratch, with the upper
bound established **twice, by two implementations sharing no search order, no validity
oracle and no bound**, neither using any symmetry argument, and calibrated against eleven
known values and against `r_3`.

Not established: anything asymptotic. This certificate should not be read as evidence for
or against any conjecture about the growth of `C(n)`.

Residual risk, stated plainly: both exhaustive implementations are branch-and-bound
searches written by the same author in the same sitting, so a *conceptual* error about the
problem — as opposed to a coding error — could in principle affect both. The defence
against that is §1 (the definition, including degenerate triples) together with the `r_3`
calibration of §5, which would fail loudly if degenerate triples were being mishandled.
Anyone re-checking this result should attack Method A's candidate invariant (§3) first.

## 8. Provenance

Produced in an isolated self-directed search campaign on Problem 6.59 that made no
progress on the asymptotic problem; this value is its only surviving contribution. The
campaign's other outputs were checked against the literature and found to be known, in
particular the Gaussian-integer formulation of the isosceles-right-triangle relaxation and
the self-similar digit construction for it, both of which appear in
[arXiv:2607.22828](https://arxiv.org/abs/2607.22828) (Károlyi–Solymosi).
