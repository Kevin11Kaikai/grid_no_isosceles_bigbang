# Proposal Round 1: Beating C(64)=112 / C(100)=164

## 1. What the notebook's evolved algorithm already does (baseline mechanism)

Read from `data/external/subsets_of_the_grid_with_no_isosceles_triangles.ipynb`, cell 4
(the evolved n=64 program; n=100 program in cell 5 is presumably analogous but was
truncated/empty in the extracted cell — treat as unread, may want to double check).

- **Data structure**: `IsoscelesFreeSet` maintains `points` (set) and, per point, the set of
  squared distances already realized to other members (`forbidden_d2s`). `check_add` /
  `add_point` / `remove_point` are all O(|S|) — this is the same incremental primitive we
  should reuse in any new strategy rather than reinventing it.
- **Phase 1 (symmetric build)**: tries 7 symmetry types (axis offsets at n-1, n-2, n,
  and 4 "mixed half-integer" variants), builds a candidate set of "generators" in one
  quadrant sorted corner-inward, and greedily adds each generator's full symmetry orbit
  (`check_add_group`) if it stays valid. Best symmetry type is kept, then ILS-perturbed by
  removing/re-adding whole generator orbits for the remaining 70% of the time budget.
- **Phase 2 (asymmetric refinement)**: seeded from the better of (phase-1 result, a
  hardcoded previous-best construction loaded via `eval`). Each iteration: remove 8-30% of
  points at random, **re-impose a randomly chosen symmetry type on the survivors** (adds
  mirror partners of whatever remains), then greedily refill using one of four candidate
  orderings chosen probabilistically (local 8-neighborhood expansion 20%, peripheral-only
  40%, perimeter-first-global 30%, uniform random 10%). Accepts if `>=` best size (with 20%
  chance to move to an equal-size plateau).
- **Notably unused**: `scipy.optimize.milp`, `LinearConstraint`, `Bounds` are imported but
  never called anywhere in the shown evolved program. No exact/ILP solve is ever performed;
  every accept/reject decision is either a single greedy incremental check or a symmetry
  projection. This is the main gap we can exploit.

Everything in the notebook's search is: (a) always strictly feasible (fail-closed
incremental checks, never explores infeasible states), (b) driven by *random* destroy
(uniform sampling of points/generators to remove), and (c) repair is *always greedy
single-pass*, never optimal even on a small sub-instance. All three of these are levers we
can pull differently.

## 2. Structural observations on the baselines (OBSERVATIONS, not proven, unverified — Red
Team should check independently; small sample size of n=2 constructions)

Computed directly from `data/baselines/official_raw.py` (SOL_64, 112 pts; SOL_100, 164 pts):

- **Central point-symmetry**: SOL_100 is **100% invariant** under the map
  `(x,y) -> (99-x, 99-y)` (180° rotation about the grid center) — every single point has its
  antipodal partner in the set. SOL_64 is **96.4% invariant** under the analogous
  `(x,y) -> (63-x, 63-y)` map (108/112 points paired, 4 points break the symmetry — almost
  certainly leftover asymmetric-refinement additions on top of a near-perfect symmetric
  core). This strongly suggests the winning construction really is "symmetric core (built by
  Phase 1's generator search) + a handful of asymmetric patches (Phase 2)," exactly as the
  algorithm's two-phase design intends. Implication: any new search should probably also
  special-case central symmetry as a first-class move (add/remove *pairs*), not just as one
  of 7 symmetry types treated uniformly with axis reflections.
- **Large empty center region**: measuring `ring = min(x, y, n-1-x, n-1-y)` (Chebyshev
  distance to nearest edge), SOL_64 has **zero points** with `ring > 11` out of a possible
  max ring of 31 — i.e. a fully empty central square of side `64 - 2*12 = 40` (~39% of the
  grid area). SOL_100 has zero points with `ring > 26` out of max 49 — empty central square
  of side `100 - 2*27 = 46` (~21% of area, less extreme than n=64 but still large). Points
  are heavily concentrated in the outer ~12-17% frame of the grid (ring<=2 alone holds
  66/112 = 59% of SOL_64's points; ring<=4 holds 116/164 = 71% of SOL_100's points).
- **Whole rows/columns are unused**: SOL_64 uses only 31/64 rows and 28/64 columns; SOL_100
  uses 38/100 rows and 36/100 columns. Max points in any single row or column is 8 (n=64) /
  10 (n=100) — well under n, so no row/column is anywhere near "full," but usage is patchy
  rather than uniform, consistent with a generator-orbit construction (only rows/cols
  containing a quadrant generator or its mirrors get populated).
- **Caveat**: we have not checked whether the emptiness of the center is a *necessary*
  feature of any near-optimal solution (e.g. because interior points have many more
  equidistant collinear/near-collinear partners and are therefore intrinsically harder to
  add without conflict) or merely an artifact of this particular search never trying hard
  enough there. This is exactly the kind of claim the Red Team should stress-test — e.g. by
  measuring the true "conflict density" (fraction of other grid points blocked) as a
  function of ring depth on a partially-filled grid, and separately, by seeing whether a
  search that is deliberately biased toward the interior can still find interior-heavy
  legal configurations of comparable local density.

## 3. Three proposed strategies

### Strategy A — Tabu search with informed (not random) removal + swap moves

- **State**: same `IsoscelesFreeSet(n)` object as the baseline (reuse verbatim — it's
  already correct and O(|S|) per op). Add a `tabu_until: dict[point -> iteration]` map.
- **Move set**: single-point swap = remove one point `p in S`, then attempt to add one or
  more points from a *ranked* candidate list (not random/peripheral-biased). Rank
  candidates by a **blocking score**: for each `q` currently rejected by `check_add`,
  precompute (lazily, only after a removal, restricted to `q`'s neighborhood or a sampled
  subset for speed) whether removing `p` is *why* `q` was rejected, by checking if `q`'s
  conflict distance set intersects `forbidden_d2s[p]`. Prefer removing points `p` that
  "free up" the most currently-blocked high-value candidates (e.g. peripheral points, since
  observation above shows periphery is where the density lives).
- **Tabu rule**: once removed, `p` cannot be re-added for `tenure` iterations (tenure ~
  |S|/20, tunable) *unless* re-adding it would set a new best-size record (aspiration
  criterion) — standard tabu search escape hatch.
- **Why it escapes the notebook's local optima**: the notebook's Phase 2 removal is uniform
  random over 8-30% of points every iteration (a big, unfocused kick) and its repair order
  is one of 4 fixed heuristics, never adapting to *which* points were actually removed. Tabu
  search instead makes small, targeted, non-reversible-for-a-while moves guided directly by
  what is/isn't blocking growth right now, which is a qualitatively different search
  trajectory (steepest-descent-with-memory vs. random-restart-flavored ILS).
- **Stopping rule**: hard wall-clock budget, e.g. 3-5 minutes per (n, starting seed) pair;
  stop early if no improvement in last `5 * tenure` iterations (plateaus fast once tabu list
  cycles through a limited feature space — worth confirming empirically rather than
  guessing further).

### Strategy B — Simulated annealing on a relaxed penalty landscape + exact repair

- **State**: a possibly-*infeasible* multiset of points `S'`, plus for scoring, the count of
  isosceles-triple violations `V(S')` (every point-pair-pair coincidence of squared
  distance, both from a common apex AND the degenerate-collinear-midpoint case already
  included in "equal distance from apex" per the problem's own equivalence — no separate
  case needed since it reduces to "for every b, distances to others must be distinct").
- **Energy**: `E(S') = -|S'| + lambda * V(S')`, with `lambda` large enough that any
  size-preserving move that removes a violation always dominates a same-size move that adds
  one (e.g. `lambda = 2n`, so a single violation costs more than any single point is worth).
- **Neighbor moves**: add a uniformly random grid point not in `S'` (may introduce
  violations), or remove a uniformly random point from `S'`. Accept via standard Metropolis
  criterion on `E`, temperature annealed geometrically over the time budget.
- **This is the key point of difference from the notebook**: the notebook's search is
  *fail-closed at every single micro-step* (every add is validated immediately, so it can
  never pass "through" a temporarily-conflicted intermediate state to reach a better basin
  on the other side). SA on the relaxed landscape explicitly allows transient conflicts,
  which is a standard way to escape optima that greedy fail-closed hill-climbing cannot
  reach.
- **Repair / fail-closed guarantee for anything reported**: SA never directly produces a
  candidate for the leaderboard. Periodically (e.g. every 500 SA steps, and always at the
  end), take the current `S'`, and run an **exact max-independent-set repair**: build the
  conflict hypergraph restricted to `S'` (every violated triple is a "at most 2 of these 3"
  constraint) and solve via `scipy.optimize.milp` (already imported by the notebook but
  unused!) for the largest feasible subset of `S'`. Only a `milp`-certified-feasible set is
  ever eligible to become the new incumbent. This guarantees every reported candidate is
  exactly checked, not just "probably fine," which directly serves the Red-Team-audit
  requirement of this pipeline.
- **Stopping rule**: fixed wall-clock budget (e.g. 5 minutes), geometric cooling schedule
  sized to that budget (e.g. `T_k = T_0 * 0.999^k`); independent restarts if it converges
  (E stops improving for a fixed step count) with budget remaining.

### Strategy C — Large Neighborhood Search seeded from the 112/164 baselines, with exact
CP/MILP repair on the destroyed region (not greedy)

- **State**: start from the *exact* SOL_64 / SOL_100 point lists (already verified valid).
  Partition the grid into a small number of regions — both geometric (quadrants, the
  "frame" ring<=k vs. the empty center, individual rows/columns) and random axis-aligned
  boxes of varying size.
- **Destroy**: remove all currently-selected points inside the chosen region (typically
  10-40 points, kept deliberately small so the repair step is tractable exactly).
- **Repair — the actual novelty**: rather than the notebook's greedy single-pass refill,
  enumerate the *candidate* points inside the destroyed region (all empty grid cells there,
  or a filtered subset if the region is large), build the conflict hypergraph between
  candidates and the (fixed) rest of `S`, plus among candidates themselves, and solve the
  resulting **maximum independent set / 0-1 ILP exactly** with `scipy.optimize.milp`
  (binary variable per candidate, one `sum <= 2` constraint per conflicting triple where at
  least 2 of the 3 points are still "free" — triples with 2+ fixed points that already
  conflict are simply infeasible seeds and pruned upfront; triples with exactly 1 free point
  become a hard exclusion of that point). This is a legitimate lazy-constraint-generation
  setup: start with `sum <= 2` triple constraints derived from a first candidate pass,
  solve, check the incumbent for any triple violation missed due to enumeration shortcuts,
  add violated constraints, and re-solve (usually 0-2 extra rounds for regions this small).
  For regions with <=~50 candidates this should solve in well under a second per call given
  `n<=100` grids.
- **Two concrete region choices motivated by Section 2's observations**:
  1. **Frame-restricted LNS**: since ring<=11 (n=64) / ring<=26 (n=100) already holds ~all
     points, run repeated small-window LNS *only inside the populated frame*, sweeping
     across it — this concentrates all compute where the payoff density is empirically
     highest, and each subproblem is small enough for exact solving.
  2. **Center-probe LNS**: deliberately do a handful of LNS rounds that inject candidate
     points from the empty center (ring>11 / ring>26) into an otherwise-fixed frame, to
     directly test the Section-2 "is the empty center necessary or just unexplored" question
     with hard evidence (either it stays empty because exact solving confirms no legal
     center points exist compatibly, or the search discovers some, which would itself be a
     structurally interesting finding).
- **Why this escapes the notebook's optimum**: the notebook never solves any sub-instance
  exactly, so its refill step can strand achievable points on the table simply because of
  greedy insertion order. A same-region exact repair is guaranteed to find the true regional
  optimum given the rest of `S` fixed, which upper-bounds what any greedy variant could do
  there and should be strictly competitive with, and sometimes better than, the baseline's
  refinement phase.
- **Stopping rule**: budget per region size (e.g. cap `milp` calls at 2s wall-clock each,
  skip/fallback to greedy if exceeded), overall LNS loop budget e.g. 5-8 minutes total,
  covering multiple region partitions and both frame-sweep and center-probe variants; keep
  best feasible `|S|` seen, always re-validate with the exact `IsoscelesFreeSet` incremental
  checker before reporting (belt-and-suspenders against any MILP-encoding bug).

## 4. Suggested execution order for the main agent

Given the "minutes to low tens of minutes" budget: Strategy C (LNS+MILP seeded from the
*already-good* baselines) is likely the best time/payoff ratio since it starts from 112/164
rather than from scratch and only needs to find local improvements. Strategy A (tabu) is a
cheap, fast second attempt from the same seeds. Strategy B (SA+relaxed energy) is the most
exploratory/expensive and best used with whatever time budget remains, or run in parallel
in the background. All three should use the identical `IsoscelesFreeSet` validity checker at
the point of reporting so results are trivially cross-checkable by the Red Team regardless
of which internal representation each strategy used mid-search.
