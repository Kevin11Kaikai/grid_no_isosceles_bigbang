# Proposal Round 2: Beyond Single-Region LNS for C(64)=112 / C(100)=164

Written by the Round 2 Proposer subagent. Scope discipline note (per Round 1's F-004
process-integrity finding): this file, and the one-off analysis scripts referenced
below, were the only things this subagent touched. All analysis scripts were written
and executed from this subagent's own OS temp scratch directory (outside the repo
entirely), reading only the already-DUAL_VERIFIED files
`results/certified/n64_k112_baseline_official.json` and
`results/certified/n100_k164_baseline_official.json` plus importing (never modifying)
`src/search/incremental_state.py`. Nothing was written anywhere in the repo except
this file.

## 1. What Round 1's negative result actually proves and does not prove

Round 1 ran `src/search/lns_exact_repair.py` for 8613 exact regional repairs on n=64
and 25153 on n=100 (33766 total), each an exact 0-1 ILP solve (`scipy.optimize.milp`,
HiGHS) for the true maximum legal refill of one destroyed region given the rest of the
working set fixed, and found zero improving moves anywhere. Read literally, this is a
strong statement but a narrow one. What it proves:

- **For every region the search actually sampled** (random boxes with radius 3 to
  `n//6`; row/column bands of half-width 1-3 spanning the grid; boundary-frame windows
  of depth 1 to `n//8`; all capped at 400 candidate cells via `rng.sample` when
  larger — see `lns_exact_repair.py` lines 217-258), the true regional optimum, given
  everything else fixed, is never better than what's already there. This is a real,
  exact (not heuristic) per-region guarantee, and 33766 samples is a lot of coverage
  of a 4096-cell (n=64) / 10000-cell (n=100) grid.
- It also structurally rules out any improving move reachable by changing a **single
  contiguous region** while holding literally everything else fixed, for the region
  shapes/sizes actually tried.

What it does **not** prove, and this is the operative gap for Round 2:

- **Multi-region coordination.** Every single call to `exact_repair_region` optimizes
  exactly one destroyed region against a fixed remainder that includes every other
  candidate region untouched. This is the LNS analogue of 1-opt in local search: it is
  mathematically incapable of finding an improvement that requires two or more
  *disjoint* regions to change *simultaneously* (e.g. region A alone has no improving
  refill given the current region B, and region B alone has no improving refill given
  the current region A, but changing both together does). Nothing in Round 1 ever ran
  a single ILP over candidates drawn from two or more disjoint regions at once. This is
  exactly the gap the main agent's strategy (2) is meant to close, and it is a
  qualitative gap, not a matter of running the same route longer.
- **The 400-candidate cap silently truncates the largest regions actually attempted.**
  Row/column bands and frame windows can exceed 400 raw cells (e.g. a full row band of
  half-width 3 for n=64 is up to `64*7=448` cells; for n=100 up to `100*7=700`), and
  when they do, `lns_exact_repair.py` randomly subsamples down to 400 before building
  the ILP. So even the single-region claim is, in the largest-region cases, really
  "exact optimum of a random 400-cell subset of the region," not "exact optimum of the
  whole region" — a strictly weaker guarantee than the docstring's framing suggests for
  those specific calls.
- **Reachability from the two known baselines.** Every Round 1 route (LNS+MILP, tabu,
  greedy-LNS) starts from SOL_64 / SOL_100 and only ever explores states reachable by
  destroy-and-repair moves from that specific starting point. A completely different
  113-point (or larger) legal configuration, unrelated in structure to either baseline,
  is entirely outside what this search could ever find or rule out — 33766 is a lot of
  local moves, but it is still a local search around exactly two starting points.
- **Section 3 below adds new, sharper evidence on exactly why local search from these
  two points in particular has found nothing**, which changes the interpretation of
  the 33766-repair figure from "we got unlucky with 33766 tries" to "the two baselines
  sit at an unusually deep and narrow local optimum even under 1- and 2-point removal,
  which is consistent with (but does not prove) that reaching 113/165 from here requires
  either many simultaneous coordinated changes, or a fundamentally different
  construction not locally reachable from either baseline at all."

## 2. Design recommendations for the four Round 2 strategies

### (1) Simulated annealing with periodic exact repair

- **State and violation counting.** Reuse `IncrementalIsoscelesFreeSet`
  (`src/search/incremental_state.py`) as the base, but extend `forbidden_d2s[q]` from
  "one point per distance" to a **multiset** (distance -> list of realizing points), so
  a temporarily-infeasible working set can be represented and its violations counted
  in O(1) amortized per add/remove. Define `V(S') = sum over q in S' of sum over
  distances d with multiplicity m_d>=2 of (m_d - 1)` — i.e. total "excess" repeated
  distances across all pivots. This is cheap to maintain incrementally (each add/remove
  touches O(|S'|) distance-multiset entries, same asymptotic cost as the existing
  legal-only version) and is exactly the quantity that periodic exact repair will drive
  to zero.
- **Energy and lambda.** `E(S') = -|S'| + lambda * V(S')`. Round 1's own proposal
  suggested a fixed `lambda = 2n`; this undersells the actual worst case — a single
  point addition can in principle create violations at up to `O(|S'|)` distinct
  pivots simultaneously (if the new point happens to coincide with many existing
  pivots' already-used distances at once), so `lambda` should be set at least
  `>= |S'|_max + 1` (current working size, dynamically, not `2n`), i.e. large enough
  that even the worst-case single-move violation delta can never outweigh any
  size-preserving gain. Because the periodic exact repair is what actually recovers
  a legal candidate, `lambda` does not need to guarantee infeasibility is *impossible*
  mid-search, only that the random walk is systematically biased toward low-`V`
  basins so repair has good material to work with.
- **Move set.** Point-level, not region-level (this is the qualitative difference from
  Round 1's LNS): (a) add a uniformly random empty cell, (b) remove a uniformly random
  occupied point, (c) a **targeted swap**: remove point `p`, then immediately attempt
  to add the specific point `q` that `can_add`'s witness dict says was blocked *because
  of* `p` (this is a one-line lookup already available from the witness structure
  `can_add` returns — `witness["point_2"]` or `witness["point_1"]` depending on which
  branch fired). Given Section 3's finding that single-point removal opens literally
  zero new legal cells for 110/112 (n=64) and 164/164 (n=100) baseline points, the
  targeted-swap move is unlikely to pay off directly from the pure baseline start —
  its value is in later stages, once SA has already perturbed the state away from the
  baseline into genuinely different (if currently infeasible) territory.
- **Cooling schedule.** Given hours (not minutes) are now available: run 6-10
  independent SA chains per grid (different seeds), each budgeted 15-30 minutes,
  geometric cooling `T_k = T0 * (T_min/T0)^(k/K)` with `T0` calibrated so a
  single-new-violation move (`delta E ~= +lambda`) has roughly 30-50% acceptance
  probability at the start, and `T_min` small enough that late-stage moves are
  essentially only accepted if they reduce `V` or preserve size. Add reheating: if
  `V(S')` after a repair cycle has not produced an improvement in the last 8-10 repair
  cycles, reheat to 40-60% of `T0` and continue rather than terminating the chain —
  cheap given the compute budget, and standard practice for avoiding a single
  monotonic cooldown getting stuck early.
- **Repair frequency and mechanism.** Trigger repair adaptively whenever `V(S')`
  first exceeds a threshold (e.g. 8-15), not on a fixed step count — this bounds the
  size of each repair ILP dynamically rather than letting violations pile up
  unpredictably. The repair itself should be a **direct generalization of
  `exact_repair_region`**, not a new implementation: partition the current `S'` into
  `F` (points touching zero violations, permanently kept) and `T` (the small "touched"
  set actually involved in some violation, typically tens of points), then solve one
  0-1 ILP with a variable per point in `T` (keep/drop) **plus** a variable per empty
  cell adjacent to `T`'s footprint (candidate add), using literally the same
  fixed-pivot / candidate-pivot constraint-construction code path as
  `exact_repair_region` (`lns_exact_repair.py` lines 104-154) with `fixed_points = F`
  and `region_candidates = T ∪ (nearby empty cells)`. This reuses already-tested,
  already-correct constraint-generation logic instead of writing a second MILP
  encoding from scratch, which directly reduces the risk of a second Red-Team-flagged
  encoding bug.
- **Why this can reach states Round 1 could not.** The notebook's own search (Phase 1/2)
  and every Round 1 route are fail-closed at every micro-step: no accepted intermediate
  state is ever allowed to be illegal, even transiently. SA on the relaxed `V`-penalized
  landscape is the only Round 1/2 route that can pass *through* a temporarily-invalid
  configuration to reach a strictly-larger legal basin on the other side — a standard,
  well-understood escape mechanism that none of Round 1's three routes (LNS+MILP, tabu,
  greedy-LNS) had access to, since all three only ever add points that are individually
  legal at the moment of insertion.

### (2) Multi-region / larger-window exact ILP repair

- **The direct fix for the Section-1 gap.** Generalize `exact_repair_region` to accept
  a **list** of disjoint destroy regions in one call: build `fixed = current - union(all
  removed regions)`, `candidates = union(all region_candidates)`, and run the existing
  constraint-construction logic unchanged over the combined candidate pool — the
  constraint code already treats candidates as one flat list keyed by `idx[p]`, so this
  is a small, low-risk change (loosen the caller's region-selection loop, not the
  ILP-building internals).
- **Concrete region-count/size recommendations, ordered by tractability risk:**
  1. **Two disjoint regions, ~100-200 candidates each (m~200-400 total)** — directly
     comparable in size to what Round 1 already solved routinely in low seconds; try
     this FIRST since it is the cheapest genuinely-new experiment and the most direct
     answer to "can two regions jointly find what neither can alone." Use a generous
     per-call time limit (10-30s) since this is the highest-priority new case.
  2. **Symmetric-pair regions**: destroy region `R` and its central-symmetric image
     `R' = refl(R)` (reflection map used in H-001) simultaneously, but do **not** force
     the solver to keep the fill symmetric — let it choose freely. This is a clean,
     targeted stress test of whether H-001's near-total central symmetry is load-bearing
     (an asymmetric joint fill of `R ∪ R'` beating the symmetric baseline would be
     direct evidence it is not) or just structurally convenient (if the solver, given
     total freedom, still reconstructs a symmetric-looking fill, that's suggestive
     evidence in the other direction).
  3. **3-4 disjoint regions, m up to 800-1200** — accept per-call MILP time limits of
     60-120s; explicitly log solver status (`optimal` vs `time-limit-incumbent`) since
     only `optimal` calls carry the same "we exhaustively checked this exact
     subproblem" guarantee Round 1's headline figure relies on — a time-limited
     incumbent is still a legitimate feasibility check but not an exhaustiveness
     proof for that subproblem, and conflating the two would weaken the honesty of
     any resulting negative-result claim.
  4. **Untruncated full-row-and-column-cross regions** — note that Round 1's 400-cell
     cap means even its *single*-region runs never fully solved the largest
     row/column/frame regions it nominally sampled (see Section 1). Lifting the cap
     for these specific region kinds (row+column cross around a chosen center, up to
     ~700-850 cells for n=64 before the old cap) is itself new territory worth trying
     before investing in true multi-region compute.
- **Tractability ceiling — calibrate, don't guess.** Before committing a large compute
  budget to any specific `m`, run a short calibration sweep: 10 calls each at
  `m in {200, 400, 800, 1200, 1600}`, log wall-clock-to-optimal, and pick the largest
  `m` that still reliably reaches `optimal` status within the intended per-call budget.
  HiGHS's MIP performance on this constraint structure (dense candidate-pivot triple
  constraints) has not been characterized at `m>400` in this project yet — Round 1's
  own 400-cap was itself somewhat arbitrary (chosen for the single-region case), not a
  measured tractability limit.

### (3) Symmetry-guided search

- **Orbit-space parametrization.** Under the central-symmetry map used in H-001
  (`(x,y) -> (n-1-x, n-1-y)`, which has no fixed points for even `n`, so every orbit is
  a true pair), partition the grid into `n^2/2` orbit-pairs `{p, refl(p)}`. Define the
  search variable as **one bit per orbit**: 1 means both `p` and `refl(p)` are selected,
  0 means neither. This exactly halves the decision-variable count and *by
  construction* guarantees every candidate is centrally symmetric — a genuinely
  different representation from anything Round 1 used (Round 1's routes all operated
  in raw point space and only happened to preserve symmetry when it happened to).
- **Implementation**: a thin `add_orbit(p)` / `remove_orbit(p)` wrapper around
  `IncrementalIsoscelesFreeSet`: `add_orbit` must check both `p` and `refl(p)` together
  before committing (checking `p` alone can spuriously succeed even though `refl(p)`
  then fails, including the case where `p` and `refl(p)` conflict *with each other*
  at exactly the symmetric distance) — commit only if both succeed, else roll back
  cleanly. Run the same LNS/tabu/SA machinery entirely in orbit-space on top of this
  wrapper: since moves are atomic pairs, the effective search space and the per-move
  validity-check cost are both roughly halved relative to point-space, so for equal
  wall-clock budget an orbit-space search gets roughly 2x the effective move count.
- **A specific, cheap, high-value first experiment (recommended to run before anything
  else in this strategy):** exhaustively scan all currently-occupied orbits (54 for
  n=64, 82 for n=100 — see Section 3, already computed and verified) removing each one
  at a time and checking whether **any** replacement orbit (not just the removed one
  itself) becomes addable. This is the orbit-space analogue of a single-point swap scan,
  costs only tens of `IncrementalIsoscelesFreeSet`-based checks per orbit (cheap), and
  either produces an immediate actionable frontier or a clean, orbit-specific negative
  data point to add to `failed_ideas.md`. **This subagent already ran this exact
  experiment as part of Section 3's structural analysis — see H-006b below: the result
  was a clean 0/54 and 0/82 (only the trivially-self-reconstructable orbit is ever
  addable), so this specific "first experiment" is already done and already negative.**
  The main agent should treat single-orbit removal as ruled out and move directly to
  multi-orbit removal (2-3 orbits at once) as the actual starting granularity for this
  strategy, informed by that result rather than re-discovering it.
- **A meaningful symmetry-breaking test.** Run two matched-budget conditions: (A)
  orbit-space-only search (as above), (B) an otherwise-identical algorithm (same move
  budget, same acceptance rule) but operating in raw point-space with no symmetry
  constraint. A genuinely informative outcome requires watching for two different
  signals, not just final size: (i) does (A) *converge faster* to a given size than
  (B), evidence the symmetric representation is a genuinely more efficient
  parametrization of this problem's near-optimal region, not just a coincidence of how
  the official notebook happened to search; (ii) does (B) ever find a size *strictly
  larger* than (A)'s ceiling — a direct, immediately actionable improvement if so. If
  both plateau at exactly 112/164 despite (B) having access to a strictly larger state
  space and being a different algorithm from both (A) and the official notebook, that
  is meaningfully stronger evidence for a real symmetric ceiling than either the
  official notebook's or Round 1's own single-algorithm results could provide alone,
  since it would be a case of two independent search algorithms and two different
  representations converging on the same number.

### (4) CP-SAT-based lazy-constraint / hypergraph global search

- **Model.** One Boolean variable `x_p` per grid cell (4096 for n=64, 10000 for n=100
  — trivial variable counts for CP-SAT). Objective: maximize `sum(x_p)`. No isosceles
  constraints are added upfront; the full naive constraint set is far too large to
  enumerate eagerly for n=100 (before distance-collision filtering, `O(n^4)` candidate
  (pivot, pair) triples), which is exactly why lazy addition is the right approach here.
- **Do not start from zero cuts.** `logs/*.json` (`lns_exact_n100_seed7.json`,
  `tabu_n64_seed3.json`, `tabu_n100_seed11.json`, `lns_greedy_n64_multiseed.json`,
  `center_probe_n64.json`) were checked directly by this subagent — none of them
  persist raw violated-triple witness lists, only aggregate iteration/size counters, so
  there is no ready-made cut file to import verbatim. There is, however, real reusable
  structure available at near-zero extra cost:
  1. **Re-derive cuts from `exact_repair_region`'s own constraint construction.** Every
     one of Round 1's 33766 MILP calls already built a full local constraint model
     (`constraints_rows` in `lns_exact_repair.py`, lines 104-154) before solving it and
     then discarding it. Re-running a modest batch of these same region-repair calls
     (a few hundred is enough) with one addition — persist `constraints_rows` instead
     of only using it for that one MILP — and translating each `x_p + x_a + x_b <= 2`
     row into a CP-SAT linear cut over the same grid points gives tens of thousands of
     already-correct, already-validated cuts before the lazy loop even starts.
  2. **Seed from the two DUAL_VERIFIED baselines' own pivot structure directly**,
     independent of any regional search. For every occupied pivot `q` in the current
     112/164-point baseline and every other grid cell `r` (not just other occupied
     cells), compute `d^2(q,r)` and group by distance; every group of size >= 3 across
     the **whole grid** (not sampled, not regional) yields a valid `sum(group) <= 2`
     cut. This is `O(n^2 * |S|)` — for n=100, `10000 * 164 = 1.64M` distance
     evaluations, trivial — and gives a large, exact, global (not regionally-sampled)
     cut set anchored directly on the already-certified baselines before any lazy
     iteration begins.
  3. **Genuinely lazy loop for the residual.** After seeding with (1)+(2), solve with a
     time limit, rescan the incumbent's own selected points for any remaining violated
     triple (`O(k^2)` over the incumbent's own `k <= n` selected points — trivial), add
     any found in bulk (thousands at once, not one at a time, to amortize solver
     restart overhead via `AddLinearConstraint(sum(...) <= 2)` calls batched per
     round), and repeat until either zero violations remain (a genuine CP-SAT-proof
     legal incumbent under the accumulated cuts) or a wall-clock/round budget is hit.
  - **Toward a partial impossibility proof, not just another heuristic.** If a
    full lazy-cut CP-SAT run converges to `OPTIMAL` status with objective `<=` the
    current baseline size, that is a genuine machine-checked upper bound for that
    exact model, not another negative heuristic search result — this is the
    substantive difference in kind between this strategy and (1)-(3), and is worth
    prioritizing partly *because* a negative result here is qualitatively stronger
    evidence than any of the other three strategies could produce. Even short of full
    convergence, log `solver.ResponseStats()` / the best objective bound after every
    lazy round — a shrinking upper bound over hours, even without reaching proven
    optimality, is a legitimate and reportable partial result ("no legal set larger
    than X was found by a machine-checked model with Y validated cuts in Z hours,
    though completeness of the cut set was not established").
  - **Mandatory encoding self-check, do this FIRST, before trusting any output:**
    verify that CP-SAT, seeded with the cuts from (1)+(2), still accepts the known
    112/164-point baseline itself as feasible (warm-start/hint it in directly). If the
    known-legal baseline is ever rejected as infeasible under the emitted cuts, that is
    an encoding bug in the cut-generation code, not evidence about the problem — this
    is the CP-SAT-route analogue of Round 1's Red Team Attack 6 (MILP-encoding
    correctness vs. brute force on synthetic instances) and should be treated with the
    same mandatory, non-optional status.
  - **Practical CP-SAT settings** for an hours-scale budget: `num_search_workers` in
    the 8-16 range (CP-SAT's parallel portfolio benefits substantially from wall-clock
    at this scale); persist the `CpSolver`/model between lazy rounds and warm-start
    each round's search with the previous round's incumbent rather than discarding it.

## 3. New structural hypotheses (computed directly from the certified baselines)

All figures below were computed fresh by this subagent from
`results/certified/n64_k112_baseline_official.json` and
`...n100_k164_baseline_official.json`, using the project's own
`IncrementalIsoscelesFreeSet` for anything correctness-sensitive (see the honest
process note at the end of this section).

**H-005 (new): zero currently-empty cell anywhere in either grid — not just the
center — is directly addable, and the average conflict count strictly increases
toward the interior.** Scanning every one of the 3984 empty cells (n=64) / 9836 empty
cells (n=100) and counting exact conflicts (apex-type + pivot-type) against the full
baseline: **0/3984 and 0/9836 are addable with zero conflicts.** The average conflict
count per empty cell rises from ~14 near the boundary (ring 0-2) to ~27 (n=64) / ~42
(n=100) at the deepest interior ring, in a roughly monotonic trend with a few noisy
bumps (full ring-by-ring table available by rerunning the analysis; e.g. n=64: ring 0
avg 13.74 conflicts -> ring 31 (deepest, 4 cells) avg 27.0; n=100: ring 0 avg 15.43 ->
ring 49 (deepest, 4 cells) avg 42.0). This sharpens H-002: the empty center is not
merely *unpopulated*, it is *measurably harder-blocked* than the periphery by this
direct count, which is real evidence (though still not proof) that H-002's center
emptiness reflects genuine structural difficulty rather than pure search artifact —
exactly the kind of quantitative angle H-002's own "Caveat" paragraph in
`hypotheses.md` asked for.

**H-006 (new): both baselines sit at an exactly-flat single-point-removal local
optimum.** For n=64, only 2 of 112 points free even one replacement empty cell when
removed individually ((56,61) and (56,2), each freeing exactly 1 cell — not enough for
a net gain since removing one point and adding one back is size-neutral at best); the
other 110/112 points free literally zero empty cells if removed alone. For n=100,
**0 of 164 points** free any empty cell at all when removed individually. This is
sharper and more specific than the aggregate "33766 MILP repairs found nothing" figure:
it is direct evidence that simple swap-based local search (tabu with informed removal,
greedy-repair LNS — both tried in Round 1 as F-002/F-004) was very unlikely to succeed
from these exact starting points regardless of how it was tuned, since there is
essentially no single-point-removal gradient to follow at all.

**H-006b (new, orbit-space extension of H-006, symmetry-guided-search-relevant):**
the same flatness holds under symmetric *orbit*-pair removal. Scanning all 54
(n=64) / 82 (n=100) currently-occupied central-symmetric orbit pairs, removing each
pair and checking (via `IncrementalIsoscelesFreeSet`, both points checked jointly, not
independently) whether **any** orbit — not just the one just removed — becomes legally
addable: **54/54 and 82/82 orbit removals open exactly one addable orbit, and in every
single case that orbit is the trivially-self-reconstructable one just removed.** Zero
orbit removals open any *alternative* replacement orbit. This directly answers the
"cheap first experiment" this subagent recommends in Section 2's Strategy (3): it is
already negative, so the main agent should start symmetry-guided search at 2-3
simultaneous orbit removals, not 1.

*(Process-integrity note, in the spirit of this project's discipline of disclosing
errors rather than hiding them: this subagent's first attempt at the orbit-removal
scan had a real bug — a list-comprehension `[p for p in pts if refl(p) in S and p <
refl(p)]` was mistakenly treated as a list of `(p, q)` pairs and unpacked with `for
(p, q) in symmetric_pts`, which actually unpacked each single point's own `(x, y)`
integer coordinates instead of two point-tuples. This produced a nonsensical but
non-crashing result (uniformly "opens 2" for every orbit) that was caught by this
subagent, not by an external check, via a sanity re-derivation using the project's own
`IncrementalIsoscelesFreeSet` before being reported here. The number actually reported
above (H-006b) is from the corrected script. Flagging this transparently since a wrong
number silently reported as a "new hypothesis" would be exactly the kind of error this
project's Red Team process exists to catch.)*

**H-007 (new): row/column occupancy counts cluster into a small number of discrete
values, not a smooth distribution — a fingerprint of the generator-orbit
construction.** n=64 row-occupancy histogram (count of used rows by how many points
they hold): `{2 points: 10 rows, 3: 2, 4: 8, 6: 4, 7: 2, 8: 2}` (28 rows used total).
n=100: `{2: 12, 4: 12, 6: 6, 8: 2, 10: 4}` (36 rows used total). Both are visibly
quantized into a handful of repeated values rather than graded — consistent with the
notebook's own generator-and-orbit construction (a small number of underlying
"generator" rows populate several mirrored/translated rows identically under the
symmetry group), and suggesting that a per-construction row/column occupancy
*signature* (the multiset of row-counts and column-counts) could be a cheap,
low-dimensional invariant worth checking on any future candidate construction —
a construction with a smooth, non-quantized row-occupancy histogram would itself be
a signal that it was NOT built by the same generator-orbit mechanism as the official
notebook, which is either irrelevant or interesting depending on whether it also beats
112/164.

**H-008 (new, on the 4 symmetry-breaking points in SOL_64): they are "second-shell"
points, not edge points, and none of their would-be mirror partners are occupied by
anything else.** The 4 points breaking central symmetry are `(1,2)`, `(1,61)`,
`(59,26)`, `(59,37)`, at ring depths `[4, 1, 4, 1]` (not ring 0 — i.e. not on the
literal outer edge). Checking each one's exact reflected partner: `refl(59,26)=(4,37)`,
`refl(1,2)=(62,61)`, `refl(59,37)=(4,26)`, `refl(1,61)=(62,2)` — **none of these four
reflected coordinates are occupied by any other point in SOL_64.** This means the
4-point asymmetry is not "point A displaced B's rightful symmetric slot" (which would
show up as some other occupied point sitting exactly at one of these four reflected
coordinates); it looks more like 4 genuinely standalone Phase-2 patch additions layered
on top of a perfectly symmetric 108-point (54-orbit) core, exactly as
`scratch/proposer/proposal_round1.md`'s original interpretation guessed but did not
directly verify. This is a small, useful confirmation for Strategy (3): the "symmetric
core + asymmetric patch" model is not just plausible from the aggregate 96.4%
statistic, it holds up point-by-point.

## 4. Recommended priority ordering and honest assessment

Given genuinely large compute is now available (hours, not minutes), recommended order:

1. **CP-SAT lazy-constraint search (Strategy 4) — start first, run longest.** This is
   the only strategy of the four that can produce a qualitatively different kind of
   result: either a genuinely new construction (if the model finds one), or real
   progress toward a machine-checked partial impossibility bound (if it doesn't) —
   which is strictly more valuable than "yet another heuristic route found nothing" at
   this point, given Round 1 already produced three heuristic negative results and
   Section 1 above already explains structurally why the simplest heuristic moves
   (single-point swap, single-orbit swap) are flat. Start the mandatory baseline-
   feasibility self-check (Section 2.4) immediately, since everything downstream
   depends on the cut encoding being correct.
2. **Multi-region exact ILP repair (Strategy 2), region-pair experiments first.**
   Second priority because it is the most direct structural answer to Section 1's
   identified gap (Round 1 never tried simultaneous disjoint-region changes at all),
   it reuses well-tested code with low implementation risk, and — per Section 3's
   H-006 finding that even 1-point and 1-orbit removal never opens any frontier — it
   is quite plausible that a genuine improvement, if one exists near either baseline
   at all, requires exactly this kind of coordinated multi-region move. This is
   simultaneously the strategy most likely to find an actual improvement (if the
   near-baseline neighborhood has any slack left at all) and cheap to run for hours
   given the calibration-then-scale approach in Section 2.
3. **Simulated annealing with periodic exact repair (Strategy 1).** Third priority:
   genuinely different search dynamics (transient infeasibility) that neither Round 1
   nor Strategy 2 can replicate, but slower to cover the same amount of state space
   per unit compute than exact multi-region ILP, and its main payoff — escaping deep,
   narrow local optima — is exactly the situation Section 3 shows these two baselines
   are in, so it is a reasonable, well-motivated use of remaining hours rather than a
   long shot, just not the top pick given CP-SAT and multi-region ILP are both more
   direct routes to the two things this round should actually try to produce (a new
   construction, or a machine-checked bound).
4. **Symmetry-guided search (Strategy 3).** Fourth priority, not because it is weak,
   but because Section 3 already answered its cheapest first experiment (single-orbit
   removal — negative, H-006b) as part of writing this proposal, so its next useful
   increment (2-3 simultaneous orbit removals, and the matched symmetric-vs-asymmetric
   comparison) is a smaller, more specific piece of remaining work than the other three
   strategies, well suited to running as a background/parallel track alongside
   whichever of (1)-(3) the main agent runs first, rather than needing dedicated
   priority.

**Honest assessment of which is most likely to find an actual improvement vs. produce
another (still valuable) negative result:**

- **Most likely to find a real improvement, if one exists near the current baselines
  at all: Strategy 2 (multi-region ILP)**, precisely because Section 1's gap analysis
  and Section 3's H-006/H-006b findings together identify a specific, previously-untried
  class of move (coordinated 2+ region changes) that is the most plausible remaining
  place slack could exist, given single- and even orbit-paired removal are provably
  flat. If Strategy 2 with genuinely large region counts/sizes also finds nothing, that
  would be a considerably stronger negative result than Round 1's, since it would rule
  out the specific gap Round 1 left open.
- **Most likely to produce a rigorous, reportable negative result (a real partial
  impossibility bound) rather than a discovery: Strategy 4 (CP-SAT).** Given how
  aggressively local Round 1 and Section 3's findings show these baselines to be, an
  actual construction beating 112/164 — if it exists — plausibly looks nothing like
  either baseline, which is exactly the kind of thing a global lazy-constraint model
  can in principle discover that no local-move strategy (1, 2, or 3) can, but it is
  also the strategy most likely to instead spend its hours tightening a proven upper
  bound without reaching full convergence — which is still genuinely valuable and
  qualitatively different from a fourth heuristic-search negative result, and should be
  reported as such either way.
- **Most likely to reconfirm existing structure without moving the needle much:
  Strategy 3 (symmetry-guided).** Given H-006b already shows the flat-local-optimum
  property extends cleanly into orbit-space, the marginal information from fully
  building out Strategy 3 is probably confirmatory (a cleaner, more efficient
  re-derivation of "112/164 is a strong local optimum, symmetric or not") rather than
  discovery-oriented — still worth running, since a clean confirmatory result from a
  second independent representation is real evidence (see Section 2's discussion of
  why two independently-converging algorithms is stronger evidence than one), just not
  where this subagent would bet on finding 113 or 165.
