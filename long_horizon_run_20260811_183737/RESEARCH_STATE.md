# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-12 (Gate2 Main close + Agent B Wave2 closure)  
**Remote:** `origin/master` (sync after Gate2 commit)  
**Phase:** Gate2 **PASS/CLOSED**; Wave3 ranking authorized. LH-4 enlarged orbit work remains live (separate from Wave2 B freeze).

## Incumbent

- n=64 **112** / n=100 **164** — no promotion; **no legal +1** from Wave2 A/B/C

## Wave2 closure (authoritative)

| Agent | Verdict | Headline |
|---|---|---|
| A | PASS | n100 r=2 + halos `INFEASIBLE_SCOPED`; n64 r=1 scoped INFEAS; multi-region no +1 |
| B | PASS (COMPLETE) | No candidates; Type0 longs **TIMEOUT** size=0; many other axes scoped INFEAS |
| C | PASS | Best V=3 @165 / V=2 @113; no V=0 |
| Red Team | A/B/C PASS | Gate2 closed |
| Gate2 | **PASS / CLOSED** | `scratch/wave2/gate2_decision.md`; `WAVE3_READY` |

**Discipline:** TIMEOUT ≠ INFEASIBLE; scoped INFEAS ≠ global UB; C plateau ≠ impossibility.

## Live lead (LH-4, post-Wave2)

Enlarged defect orbits (`max_extra=220`, `max_defect=220`, `halo=14`) remain the open TIMEOUT track — distinct from Wave2 B frozen universes:

| Run | Status | Notes |
|---|---|---|
| Type0 20min s301 | TIMEOUT | 1921 rounds / 32186 cuts |
| Type1 20min s302 | TIMEOUT | 114 rounds / 19919 cuts |
| Type0 **45min** s401 | check / continue | see `EXPERIMENTS/LH4_orbit_enlarged/` |

## Critical process finding (unchanged)

All Wave2 `n100_V3` elites = **S0 ∪ {q}** (Hamming remove=0). Soft |S|=165 never left that basin.

## Next 3 actions (Gate2 obstruction-driven)

1. Wave3: fund open TIMEOUT Type0 enlargements and/or certificate-driven Hamming Rem/Add outside killed Wave2 U_ids.
2. Do **not** grind C soft S0+1 seeds; require remove≥2 or nonlocal free vars.
3. Main Wave3 ranking memo → top 1–2 routes; hold FunSearch.

## Standing order

Push after meaningful events; continue; no Hard Stop for polish.
