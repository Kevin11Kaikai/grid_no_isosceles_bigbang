# RESEARCH_STATE — long_horizon_run_20260811_183737

**Updated:** 2026-08-14 (Grok 4.6; F081–F087; finite r=2 obstruction vs this S0)

## Incumbent
- n=64 **112** / n=100 **164** — **no legal +1**

## This session (information gain)
- F081–F082: easiest-q min-cover "cap=165" was counting deleted S0 points as addable.
- **True unselected surplus after those covers = 1 (the q only).**
- F084: 205 pairs, max n_unsel=1; random/top-degree pairs open 0.
- **PROVED.md §6:** with Gate1 (16 cells LB=2, rest ≥3) + joint VC=4 on those 16, every 2-deletion from this S0 opens ≤1 unselected cell ⇒ frozen-core r=2 cannot reach 165.
- F085: k-delete sweep, surplus always negative through k=32.
- F086–F087: Hamming on top-degree Rem 24/32 + the leftover Add octet/quartet: all r `INFEASIBLE_SCOPED`.

## Closed basins (do not reopen as primary)
- Previous list (S0-snap, midset≤139, killed Hamming U_ids, rem2, S0+1, avoid-S0, lattice, ring, rowband, F077–F080)
- Easiest-q frozen-core min-cover / cover+1 (F081–F082)
- Top-degree Rem 24/32 Hamming with can_add(F) Add (F086–F087)

## Next
1. n64 unselected-surplus analogue (sandbox; exact-1 qs).
2. Hamming with Add not restricted to can_add(F) — only if a new reason (can_add(F) is already the maximal unselected pool for that F).
3. Non-S0 cores / from-scratch that already hit 137: structured destroy of those, not of S0.
4. Dual-verify before promote.

## Discipline
TIMEOUT ≠ INFEAS; scoped ≠ global; standing order push.
